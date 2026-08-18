"""在 build_list.py 数据基础上生成单文件 HTML 看板。"""
import json, os, re, glob, hashlib
from build_list import ROWS, EXCLUDED, LINKS

LAYER_LABEL = {
    'L1': 'L1 运行时 AI 原生',
    'L2': 'L2 运行时 AI 增强',
    'L3': 'L3 生产管线 AI 重度',
}
CONF_LABEL = {'A': '已核实', 'B': '较可靠', 'C': '待核实'}

SHOT_DIR = 'screenshots'


def shot_key(game):
    return re.sub(r'[^\w一-鿿]+', '_', game)[:40]


def shots_for(game):
    """返回 screenshots/ 下该游戏的画面文件名，最多 2 张。"""
    key = shot_key(game)
    files = sorted(glob.glob(os.path.join(SHOT_DIR, key + '_*.*')))
    return [os.path.basename(f) for f in files[:2]]


def game_anchor(game):
    """生成稳定且安全的卡片锚点。"""
    digest = hashlib.md5(game.encode('utf-8')).hexdigest()[:10]
    return f'game-{digest}'


def link_label(url):
    """从 URL 推断显示名。"""
    if 'steampowered.com' in url:
        return 'Steam'
    if 'taptap.cn' in url or 'taptap.com' in url:
        return 'TapTap'
    if 'itch.io' in url:
        return 'itch.io'
    if 'wegamedb' in url:
        return 'WeGame'
    if 'afdian' in url:
        return '爱发电'
    if any(d in url for d in ('donews', 'hstong', '163.com', 'qq.com', 'toutiao', 'sohu', 'sina')):
        return '报道'
    return '官网'

CITY_GROUP = {}
for r in ROWS:
    c = r['city'].split('（')[0].split('/')[0].strip()
    if '待核实' in c:
        c = '待核实'
    CITY_GROUP[c] = CITY_GROUP.get(c, 0) + 1

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TapTap AI 游戏拜访追踪清单</title>
<style>
:root{
  --bg:#faf9f7; --card:#fff; --line:#e5e3dd; --line2:#d3d1c7;
  --tx:#2c2c2a; --tx2:#5f5e5a; --tx3:#888780;
  --l1:#185fa5; --l1bg:#e6f1fb; --l2:#854f0b; --l2bg:#faeeda;
  --a:#0f6e56; --abg:#e1f5ee; --b:#185fa5; --bbg:#e6f1fb; --c:#5f5e5a; --cbg:#f1efe8;
  --red:#a32d2d; --redbg:#fcebeb;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);
  font:400 14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:32px 24px 64px}
.game-nav{position:fixed;top:28px;left:max(16px,calc(50% - 790px));width:150px;
  max-height:calc(100vh - 56px);display:flex;flex-direction:column;background:var(--card);
  border:1px solid var(--line);border-radius:12px;padding:12px;z-index:20}
.nav-title{font-size:13px;font-weight:500;margin-bottom:8px}
.nav-search{width:100%;border:1px solid var(--line);border-radius:7px;padding:6px 8px;
  font:inherit;font-size:12px;color:var(--tx);background:#fff;margin-bottom:8px;outline:none}
.nav-search:focus{border-color:var(--line2)}
.nav-list{overflow:auto;display:flex;flex-direction:column;gap:2px;padding-right:2px}
.nav-list a{display:block;padding:5px 7px;border-radius:6px;font-size:12px;line-height:1.35;
  color:var(--tx2);text-decoration:none;word-break:break-word}
.nav-list a:hover{background:var(--cbg);color:var(--tx)}
.nav-list a.active{background:var(--l1bg);color:var(--l1);font-weight:500}
.nav-list a.nav-hidden{display:none}
.nav-count{font-size:11px;color:var(--tx3);margin-top:7px;padding-top:7px;border-top:1px solid var(--line)}
.nav-toggle{display:none;position:fixed;left:14px;bottom:16px;z-index:30;background:var(--tx);
  color:#fff;border-color:var(--tx);border-radius:18px;padding:7px 13px}
@media(max-width:1580px){
  .game-nav{left:14px;top:14px;transform:translateX(-180px);transition:transform .18s ease;
    max-height:calc(100vh - 28px)}
  .game-nav.open{transform:translateX(0)}
  .nav-toggle{display:block}
}
h1{font-size:22px;font-weight:500;margin:0 0 6px}
.sub{color:var(--tx2);font-size:13px;margin-bottom:24px}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}
.m{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.m .lb{font-size:12px;color:var(--tx2);margin-bottom:6px}
.m .vl{font-size:24px;font-weight:500;line-height:1.1}
.m .hint{font-size:11px;color:var(--tx3);margin-top:4px}
.note{background:#fff;border:1px solid var(--line);border-left:3px solid var(--l2);
  border-radius:8px;padding:12px 16px;font-size:13px;color:var(--tx2);margin:18px 0 22px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:18px}
button{font:inherit;font-size:13px;padding:6px 14px;border:1px solid var(--line2);
  background:#fff;color:var(--tx2);border-radius:16px;cursor:pointer}
button.on{background:var(--tx);color:#fff;border-color:var(--tx)}
.sp{width:1px;height:20px;background:var(--line2);margin:0 4px}
.cnt{font-size:12px;color:var(--tx3);margin-left:auto}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:18px 20px;margin-bottom:12px}
.card.hid{display:none}
.hd{display:flex;flex-wrap:wrap;gap:10px;align-items:baseline;margin-bottom:4px}
.nm{font-size:16px;font-weight:500}
.tag{font-size:11px;padding:2px 9px;border-radius:10px;white-space:nowrap}
.t-L1{background:var(--l1bg);color:var(--l1)} .t-L2{background:var(--l2bg);color:var(--l2)}
.t-A{background:var(--abg);color:var(--a)} .t-B{background:var(--bbg);color:var(--b)}
.t-C{background:var(--cbg);color:var(--c)}
.lk{display:inline-flex;gap:6px;flex-wrap:wrap}
.shots{display:flex;gap:10px;margin:10px 0 4px}
.shots img{height:130px;width:auto;border-radius:8px;border:0.5px solid var(--line);
  object-fit:cover;cursor:zoom-in;background:#f0eeea}
.shots img:hover{opacity:.9}
.lbbox{display:none;position:fixed;inset:0;background:rgba(0,0,0,.82);z-index:99;
  align-items:center;justify-content:center;cursor:zoom-out}
.lbbox.on{display:flex}
.lbbox img{max-width:92vw;max-height:90vh;border-radius:8px}
.lk a{font-size:12px;padding:2px 10px;border:0.5px solid var(--line2);border-radius:10px;
  color:var(--l1);background:#fff}
.lk a:hover{background:var(--l1bg);text-decoration:none}
.co{font-size:13px;color:var(--tx2);margin-bottom:12px}
.co b{font-weight:500;color:var(--tx)}
.gr{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:0 22px}
.f{padding:7px 0;border-top:1px solid #f0eeea;min-width:0}
.f .k{font-size:11px;color:var(--tx3);margin-bottom:2px}
.f .v{font-size:13px;color:var(--tx);word-wrap:break-word}
.f.full{grid-column:1/-1}
.vv{background:#f7f6f3;border-radius:8px;padding:10px 12px;margin-top:10px;
  font-size:13px;color:var(--tx2)}
.vv-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:5px}
.vv-head b{color:var(--tx);font-weight:500}
.vv-hint{font-size:11px;color:var(--tx3)}
.vv-edit{min-height:22px;padding:3px 5px;margin:0 -5px;border-radius:5px;outline:none;
  color:var(--tx2);white-space:pre-wrap}
.vv-edit:hover{background:#fff}
.vv-edit:focus{background:#fff;box-shadow:0 0 0 1px var(--line2);color:var(--tx)}
.vv-edit[data-saved="1"]:after{content:" 已保存";font-size:11px;color:var(--a)}
.edit-tools{display:flex;justify-content:flex-end;gap:6px;margin-top:6px}
.edit-tools button{padding:2px 9px;font-size:11px;border-radius:10px}
a{color:var(--l1);text-decoration:none} a:hover{text-decoration:underline}
h2{font-size:15px;font-weight:500;margin:34px 0 12px}
.ex{background:var(--redbg);border:1px solid #f7c1c1;border-radius:10px;
  padding:12px 16px;margin-bottom:10px;font-size:13px}
.ex .g{font-weight:500;color:var(--red)}
.ex .r{color:var(--tx2);margin-top:4px}
.foot{margin-top:34px;padding-top:16px;border-top:1px solid var(--line);
  font-size:12px;color:var(--tx3);line-height:1.8}
</style>
</head>
<body>
<aside class="game-nav" id="gameNav" aria-label="游戏快捷跳转">
  <div class="nav-title">游戏列表</div>
  <input class="nav-search" id="navSearch" type="search" placeholder="搜索游戏" autocomplete="off">
  <div class="nav-list" id="navList">__NAV__</div>
  <div class="nav-count" id="navCount">共 __N__ 款</div>
</aside>
<button class="nav-toggle" id="navToggle" type="button">游戏目录</button>
<div class="wrap">
<h1>TapTap AI 游戏拜访追踪清单</h1>
<div class="sub">已排除 TapTap Maker（TapTap 制造）产出 · 数据核准于 2026-08-17</div>

<div class="metrics">
  <div class="m"><div class="lb">收录目标</div><div class="vl">__N__</div><div class="hint">款游戏 / 团队</div></div>
  <div class="m"><div class="lb">已核实主体</div><div class="vl">__NA__</div><div class="hint">公司+机制均可查</div></div>
  <div class="m"><div class="lb">L1 运行时原生</div><div class="vl">__NL1__</div><div class="hint">AI 即玩法本体</div></div>
  <div class="m"><div class="lb">可实地拜访</div><div class="vl">__NCITY__</div><div class="hint">已定位国内城市</div></div>
  <div class="m"><div class="lb">明确排除</div><div class="vl">__NEX__</div><div class="hint">含 Maker 全量</div></div>
</div>

<div class="bar">
  <button class="on" data-f="all">全部</button>
  <button data-f="A">已核实</button>
  <button data-f="B">较可靠</button>
  <button data-f="C">待核实</button>
  <div class="sp"></div>
  <button data-f="L1">L1 原生</button>
  <button data-f="L2">L2 增强</button>
  <div class="sp"></div>
  <button data-f="pc">PC</button>
  <button data-f="mobile">手游</button>
  <div class="sp"></div>
  <button data-f="visitable">可拜访</button>
  <span class="cnt" id="cnt"></span>
</div>

<div id="list">__CARDS__</div>

<h2>明确排除项</h2>
__EXCLUDED__

<div class="foot">
字段设计针对实地拜访场景：公司主体与所在城市用于安排行程，核心团队背景用于判断对话层级，
融资情况用于判断合作阶段，AI 机制描述用于准备技术问题，AI 成本披露是极少数团队会公开的稀缺信息，
展会出没记录是低成本接触的机会窗口。<br>
「拜访价值」默认内容仅供参考，可直接在网页中编辑，修改结果保存在当前浏览器本地。<br>
CSV 版本另含「拜访状态 / 接触人 / 拜访日期 / 跟进备注」四个空列，可直接作为跟进表使用。
</div>
</div>
<script>
var btns=document.querySelectorAll('button[data-f]'),cards=document.querySelectorAll('.card');
function apply(f){
  var n=0;
  cards.forEach(function(c){
    var ok = f==='all' ? true
      : f==='visitable' ? c.dataset.visitable==='1'
      : f==='pc' ? c.dataset.pc==='1'
      : f==='mobile' ? c.dataset.mobile==='1'
      : (c.dataset.conf===f || c.dataset.layer===f);
    c.classList.toggle('hid',!ok); if(ok)n++;
  });
  document.getElementById('cnt').textContent='显示 '+n+' / '+cards.length+' 项';
}
btns.forEach(function(b){b.onclick=function(){
  btns.forEach(function(x){x.classList.remove('on')});
  b.classList.add('on'); apply(b.dataset.f);
}});
apply('all');
var box=document.createElement('div');box.className='lbbox';
box.innerHTML='<img>';
box.onclick=function(){box.classList.remove('on')};
document.body.appendChild(box);
function lb(src){box.querySelector('img').src=src;box.classList.add('on')}
var visitKey='taptap-ai-visit-values-v1';
function readVisits(){try{return JSON.parse(localStorage.getItem(visitKey)||'{}')}catch(e){return {}}}
function writeVisits(data){try{localStorage.setItem(visitKey,JSON.stringify(data))}catch(e){}}
var visitData=readVisits();
document.querySelectorAll('.vv-edit').forEach(function(el){
  var game=el.dataset.game;
  if(Object.prototype.hasOwnProperty.call(visitData,game))el.textContent=visitData[game];
  el.addEventListener('input',function(){
    visitData[game]=el.textContent.trim();writeVisits(visitData);
    el.dataset.saved='1';clearTimeout(el._st);el._st=setTimeout(function(){el.dataset.saved='0'},900);
  });
  el.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();el.blur()}});
});
function resetVisit(btn){
  var el=btn.closest('.vv').querySelector('.vv-edit'),game=el.dataset.game;
  el.textContent=el.dataset.default;delete visitData[game];writeVisits(visitData);
  el.dataset.saved='1';setTimeout(function(){el.dataset.saved='0'},900);
}
var nav=document.getElementById('gameNav'),navList=document.getElementById('navList');
document.getElementById('navToggle').onclick=function(){nav.classList.toggle('open')};
document.getElementById('navSearch').addEventListener('input',function(){
  var q=this.value.trim().toLowerCase(),n=0;
  navList.querySelectorAll('a').forEach(function(a){
    var show=!q||a.textContent.toLowerCase().indexOf(q)>=0;
    a.classList.toggle('nav-hidden',!show);if(show)n++;
  });
  document.getElementById('navCount').textContent='显示 '+n+' / '+navList.querySelectorAll('a').length+' 款';
});
navList.querySelectorAll('a').forEach(function(a){a.onclick=function(){
  navList.querySelectorAll('a').forEach(function(x){x.classList.remove('active')});
  a.classList.add('active');if(innerWidth<=1580)nav.classList.remove('open');
}});
var observer=new IntersectionObserver(function(entries){
  entries.forEach(function(e){if(e.isIntersecting){
    navList.querySelectorAll('a').forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id)});
  }});
},{rootMargin:'-15% 0px -75% 0px'});
cards.forEach(function(c){observer.observe(c)});
</script>
</body>
</html>"""


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def card(r):
    visitable = '0' if ('待核实' in r['city'] or '非国内' in r['city']) else '1'
    plat = r.get('platform', '待核实')
    # 平台筛选标记：pc 端（含 PC/Steam）与手游端可同时为真
    is_pc = '1' if ('PC' in plat or 'Steam' in plat) else '0'
    is_mobile = '1' if ('手游' in plat or 'android' in plat or 'iOS' in plat) else '0'
    # 链接渲染：优先 LINKS 映射（含 Steam/官网等），无映射但有 app_id 时给 TapTap 页
    raw_links = LINKS.get(r['game'], [])
    if not raw_links and r['app_id']:
        raw_links = [f'https://www.taptap.cn/app/{r["app_id"]}']
    links_html = ''.join(
        f'<a href="{esc(u)}" target="_blank">{link_label(u)} ↗</a>'
        for u in raw_links
    )
    fields = [
        ('平台', plat),
        ('核心团队背景', r['founder']), ('团队规模', r['team_size']),
        ('融资情况', r['funding']), ('当前阶段与数据', r['stage']),
        ('发行渠道', r['channel']), ('联系方式', r['contact']),
        ('展会出没', r['expo']), ('其他产品 / 工具链', r['other_product']),
    ]
    fs = ''.join(
        f'<div class="f"><div class="k">{k}</div><div class="v">{esc(v)}</div></div>'
        for k, v in fields if v and v != '—'
    )
    fs += (f'<div class="f full"><div class="k">AI 机制</div>'
           f'<div class="v">{esc(r["ai_mech"])}</div></div>')
    if r['ai_cost'] and r['ai_cost'] != '未公开':
        fs += (f'<div class="f full"><div class="k">AI 成本披露</div>'
               f'<div class="v">{esc(r["ai_cost"])}</div></div>')
    fs += (f'<div class="f full"><div class="k">证据来源</div>'
           f'<div class="v">{esc(r["src"])}</div></div>')
    anchor = game_anchor(r['game'])
    shot_files = shots_for(r['game'])
    shots_html = ''
    if shot_files:
        imgs = ''.join(
            f'<img src="{SHOT_DIR}/{esc(fn)}" loading="lazy" alt="{esc(r["game"])} 画面" '
            f'onclick="lb(this.src)">'
            for fn in shot_files
        )
        shots_html = f'<div class="shots">{imgs}</div>'
    return f"""<div class="card" id="{anchor}" data-conf="{r['conf']}" data-layer="{r['layer']}" data-visitable="{visitable}" data-pc="{is_pc}" data-mobile="{is_mobile}">
<div class="hd"><span class="nm">{esc(r['game'])}</span>
<span class="tag t-{r['layer']}">{LAYER_LABEL.get(r['layer'], r['layer'])}</span>
<span class="tag t-{r['conf']}">{CONF_LABEL[r['conf']]}</span>
<span class="lk">{links_html}</span></div>
<div class="co"><b>{esc(r['company'])}</b> · {esc(r['city'])} · {esc(plat)}</div>
{shots_html}
<div class="gr">{fs}</div>
<div class="vv">
  <div class="vv-head"><b>拜访价值</b><span class="vv-hint">默认内容仅供参考，可直接点击编辑</span></div>
  <div class="vv-edit" contenteditable="true" spellcheck="false" data-game="{esc(r['game'])}" data-default="{esc(r['visit_value'])}">{esc(r['visit_value'])}</div>
  <div class="edit-tools"><button type="button" onclick="resetVisit(this)">恢复默认</button></div>
</div>
</div>"""


if __name__ == '__main__':
    conf_order = {'A': 0, 'B': 1, 'C': 2}
    layer_order = {'L1': 0, 'L2': 1, 'L3': 2}
    rows = sorted(ROWS, key=lambda x: (conf_order.get(x['conf'], 9),
                                       layer_order.get(x['layer'], 9), x['game']))
    cards = '\n'.join(card(r) for r in rows)
    nav_items = '\n'.join(
        f'<a href="#{game_anchor(r["game"])}" title="{esc(r["game"])}">{esc(r["game"])}</a>'
        for r in rows
    )
    ex = '\n'.join(
        f'<div class="ex"><div class="g">{esc(e["game"])}'
        + (f'（{esc(e["company"])}）' if e['company'] else '')
        + f'</div><div class="r">{esc(e["reason"])}</div></div>'
        for e in EXCLUDED
    )
    nvisit = sum(1 for r in ROWS if '待核实' not in r['city'] and '非国内' not in r['city'])
    html = (HTML.replace('__CARDS__', cards).replace('__NAV__', nav_items).replace('__EXCLUDED__', ex)
            .replace('__N__', str(len(ROWS)))
            .replace('__NA__', str(sum(1 for r in ROWS if r['conf'] == 'A')))
            .replace('__NL1__', str(sum(1 for r in ROWS if r['layer'] == 'L1')))
            .replace('__NCITY__', str(nvisit))
            .replace('__NEX__', '4000+'))
    with open('taptap_ai_games_dashboard.html', 'w', encoding='utf-8') as fp:
        fp.write(html)
    print('HTML written. rows=', len(ROWS), 'visitable=', nvisit)
