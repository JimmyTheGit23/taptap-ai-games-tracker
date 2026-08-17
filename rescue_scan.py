"""补救扫描闭环验证：榜单候选 → 评论区特征词扫描 → 验证能否捞出「商店页不声明」的 AI 游戏。

目的：回答「还有多少遗漏、如何补救」。不是跑全量，是验证方法有效并量化漏检规模。
"""
import json, time
from taptap_probe import get, nuxt_payload, deref

# ===== 升级版词表 =====
# 商业特征词：AI 原生游戏绕不开 token 成本，评论区必然出现
BIZ = ['token', 'Token', '积分', '自备API', '自定义API', '接API', 'BYOK', '充值词元', '按量']
# 机制特征词
MECH = ['推演', '世界模型', '生成剧情', 'AI队友', 'AI假人', 'AI伙伴', 'AI驱动',
        '大模型', '智能体', 'Agent', '无限剧情', '开放叙事', 'AI生成', 'AI对话']
# 模型名：评论区玩家会直接点名
MODEL = ['千问', 'DeepSeek', '豆包', 'Gemini', '混元', '文心', 'Kimi', 'GLM',
         'CODEX', 'Codex', 'Qwen', '通义']

BOARDS = ['download', 'played', 'new']  # reserve 只有10条且偏预约期


def board_apps(board):
    """抓一个榜单，返回 [{id,title,tags}]。

    注意：id 必须解成标量。Nuxt payload 里 id 偶尔是引用，deref 失败时会拿到
    dict，导致 set 去重报 unhashable。这里强制转 int 标量，取不到就跳过。
    """
    t = get(f'https://www.taptap.cn/top/{board}')
    p = nuxt_payload(t)
    out = []
    seen = set()
    for o in p:
        if isinstance(o, dict) and 'identifier' in o and 'title' in o and 'id' in o:
            f = deref(p, o)
            aid = f.get('id')
            if isinstance(aid, dict):
                aid = aid.get('id') or aid.get('value')
            if not isinstance(aid, int) or aid in seen:
                continue
            seen.add(aid)
            tags = [x.get('value') for x in (f.get('tags') or []) if isinstance(x, dict)]
            out.append(dict(id=aid, title=f.get('title'), tags=tags))
    return out


def comment_score(app_id):
    """扫评论区正文（剔除全站页脚），返回 (AI命中数, 总命中, 正文)。

    关键修正：TapTap 全站页脚含「TapSight 智能问答助手算法」备案文案，
    其中 'AI'/'算法' 等词会让每个页面都虚高 ~100 分。必须先剔除页脚再统计。
    页脚起点是「营业执照」开始的备案段，正文在 topic 列表区。
    """
    import re
    try:
        t = get(f'https://www.taptap.cn/app/{app_id}/topic')
    except Exception:
        return 0, 0, ''
    body = t[t.find('<body'):]
    # 剔除页脚：备案信息段
    foot_i = body.find('营业执照')
    if foot_i > 0:
        # 保留 body 开头到页脚之间 + 页脚之后可能还有内容，这里只取备案段之前的正文主体
        body = body[:foot_i] + body[body.find('下载手机 APP', foot_i):]
    txt = re.sub(r'<[^>]+>', ' ', body)
    txt = re.sub(r'\s+', ' ', txt)
    # 再剔除残留的备案长尾
    txt = re.sub(r'TapSight.{0,40}号', ' ', txt)
    txt = re.sub(r'网信算备\d+号', ' ', txt)
    ai_n = len(re.findall(r'AI|人工智能', txt))
    biz_n = sum(txt.count(k) for k in BIZ)
    mech_n = sum(txt.count(k) for k in MECH)
    model_n = sum(txt.count(k) for k in MODEL)
    total = ai_n + biz_n + mech_n + model_n
    return ai_n, total, txt


if __name__ == '__main__':
    # 收集榜单去重后的候选
    pool = {}
    for b in BOARDS:
        try:
            for a in board_apps(b):
                pool.setdefault(a['id'], a)
            print(f'[board {b}] ok, 累计 {len(pool)} 款')
        except Exception as e:
            print(f'[board {b}] ERR {e!r}')
        time.sleep(0.8)

    print(f'\n=== 候选池 {len(pool)} 款，开始评论区扫描（仅扫前若干做方法验证）===\n')
    # 方法验证：全部扫，但控制节奏
    results = []
    for i, (aid, a) in enumerate(pool.items()):
        ai_n, total, _ = comment_score(aid)
        results.append(dict(id=aid, title=a['title'], tags=a['tags'],
                            ai_n=ai_n, total=total))
        if (i + 1) % 20 == 0:
            print(f'  已扫 {i+1}/{len(pool)}')
        time.sleep(0.5)

    # 信号强度排序：商业词+机制词是强信号（商店页不一定有 AI 标签）
    results.sort(key=lambda x: -x['total'])
    with open('rescue_scan.json', 'w', encoding='utf-8') as fp:
        json.dump(results, fp, ensure_ascii=False, indent=1)

    print('\n=== 评论区信号 Top 15（数值=AI+商业+机制+模型词命中总数）===')
    for r in results[:15]:
        print(f"  {r['total']:4d}  AI:{r['ai_n']:3d}  {r['title'][:24]:26s} {r['tags']}")
    print('\nsaved rescue_scan.json')
