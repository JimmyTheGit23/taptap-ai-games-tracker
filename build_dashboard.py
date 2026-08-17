"""在 build_list.py 数据基础上生成单文件 HTML 看板。"""
import json
from build_list import ROWS, EXCLUDED

LAYER_LABEL = {
    'L1': 'L1 运行时 AI 原生',
    'L2': 'L2 运行时 AI 增强',
    'L3': 'L3 生产管线 AI 重度',
}
CONF_LABEL = {'A': '已核实', 'B': '较可靠', 'C': '待核实'}

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
.co{font-size:13px;color:var(--tx2);margin-bottom:12px}
.co b{font-weight:500;color:var(--tx)}
.gr{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:0 22px}
.f{padding:7px 0;border-top:1px solid #f0eeea;min-width:0}
.f .k{font-size:11px;color:var(--tx3);margin-bottom:2px}
.f .v{font-size:13px;color:var(--tx);word-wrap:break-word}
.f.full{grid-column:1/-1}
.vv{background:#f7f6f3;border-radius:8px;padding:10px 12px;margin-top:10px;
  font-size:13px;color:var(--tx2)}
.vv b{color:var(--tx);font-weight:500}
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

<div class="note">
<b>口径说明。</b>TapTap 官方 AI 标签下仅 3 款游戏，且平台元数据不可作为判定依据 ——
实测 5 款已知 AI 游戏，标签召回率仅 <b>40%</b>、简介关键词召回率 <b>80%</b>。
典型反例是《历史模拟器：崇祯》：国内首款 AI 原生历史策略游戏，但 TapTap 标签只有「策略」，
简介全文不含 AI 与大模型字样（用「世界推演模型」表述）。
因此本清单以第三方深度报道、券商研报、展会名录交叉召回，平台数据仅用于核准评分与厂商。
置信度 A 表示公司主体与 AI 机制均有公开可查证据；C 表示仅有单一媒体提及、主体待补齐。
L3（生产管线 AI 重度）未做全量收录 —— 开发者普遍不主动披露美术与配音的 AI 使用比例，强行推断会把猜测写成结论。
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
    link = (f'<a href="https://www.taptap.cn/app/{r["app_id"]}" target="_blank">'
            f'TapTap 页面 →</a>') if r['app_id'] else ''
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
    return f"""<div class="card" data-conf="{r['conf']}" data-layer="{r['layer']}" data-visitable="{visitable}" data-pc="{is_pc}" data-mobile="{is_mobile}">
<div class="hd"><span class="nm">{esc(r['game'])}</span>
<span class="tag t-{r['layer']}">{LAYER_LABEL.get(r['layer'], r['layer'])}</span>
<span class="tag t-{r['conf']}">{CONF_LABEL[r['conf']]}</span>{link}</div>
<div class="co"><b>{esc(r['company'])}</b> · {esc(r['city'])} · {esc(plat)}</div>
<div class="gr">{fs}</div>
<div class="vv"><b>拜访价值 </b>{esc(r['visit_value'])}</div>
</div>"""


if __name__ == '__main__':
    conf_order = {'A': 0, 'B': 1, 'C': 2}
    layer_order = {'L1': 0, 'L2': 1, 'L3': 2}
    rows = sorted(ROWS, key=lambda x: (conf_order.get(x['conf'], 9),
                                       layer_order.get(x['layer'], 9), x['game']))
    cards = '\n'.join(card(r) for r in rows)
    ex = '\n'.join(
        f'<div class="ex"><div class="g">{esc(e["game"])}'
        + (f'（{esc(e["company"])}）' if e['company'] else '')
        + f'</div><div class="r">{esc(e["reason"])}</div></div>'
        for e in EXCLUDED
    )
    nvisit = sum(1 for r in ROWS if '待核实' not in r['city'] and '非国内' not in r['city'])
    html = (HTML.replace('__CARDS__', cards).replace('__EXCLUDED__', ex)
            .replace('__N__', str(len(ROWS)))
            .replace('__NA__', str(sum(1 for r in ROWS if r['conf'] == 'A')))
            .replace('__NL1__', str(sum(1 for r in ROWS if r['layer'] == 'L1')))
            .replace('__NCITY__', str(nvisit))
            .replace('__NEX__', '4000+'))
    with open('taptap_ai_games_dashboard.html', 'w', encoding='utf-8') as fp:
        fp.write(html)
    print('HTML written. rows=', len(ROWS), 'visitable=', nvisit)
