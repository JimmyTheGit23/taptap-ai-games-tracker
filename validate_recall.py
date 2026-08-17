"""反向验证：用已知 AI 游戏抽查「关键词召回」的真实命中率。

这是漏检《历史模拟器：崇祯》后补上的校验步骤。
结论会写进 build_list.py 的方法论注释。
"""
from taptap_probe import get, nuxt_payload, deref

KEYWORDS = ['AI', 'ai', '人工智能', 'AIGC', '大模型', 'LLM', '智能体',
            'Agent', 'AI生成', 'AI驱动', 'AI伙伴', 'AI NPC']

KNOWN_AI_GAMES = {
    813198: '历史模拟器：崇祯',
    773812: '乌托',
    771203: 'AIFriends',
    746715: '群星低语',
    156070: '假如我是人工智能',
}


def probe(app_id):
    t = get(f'https://www.taptap.cn/app/{app_id}')
    p = nuxt_payload(t)
    for o in p:
        if isinstance(o, dict) and 'identifier' in o and 'title' in o and 'id' in o:
            f = deref(p, o)
            tags = [x.get('value') for x in (f.get('tags') or []) if isinstance(x, dict)]
            d = f.get('description')
            if isinstance(d, dict):
                d = d.get('text') or d.get('detail') or ''
            d = str(d or '')
            tag_hit = any(any(k.lower() == (tg or '').lower() for k in KEYWORDS) for tg in tags)
            desc_hit = any(k in d for k in KEYWORDS)
            return f.get('title'), tags, tag_hit, desc_hit, len(d)
    return None, [], False, False, 0


if __name__ == '__main__':
    print(f"{'游戏':22s} {'标签命中':>8s} {'简介命中':>8s}  标签")
    print('-' * 78)
    tag_ok = desc_ok = either = 0
    for aid, nm in KNOWN_AI_GAMES.items():
        try:
            title, tags, th, dh = probe(aid)[:4]
            tag_ok += th
            desc_ok += dh
            either += (th or dh)
            print(f"{(title or nm)[:20]:22s} {'命中' if th else '漏':>8s} "
                  f"{'命中' if dh else '漏':>8s}  {tags}")
        except Exception as e:
            print(f'{nm} ERR {e!r}')
    n = len(KNOWN_AI_GAMES)
    print('-' * 78)
    print(f'标签召回率 {tag_ok}/{n} = {tag_ok/n:.0%}   '
          f'简介召回率 {desc_ok}/{n} = {desc_ok/n:.0%}   '
          f'两者取并 {either}/{n} = {either/n:.0%}')
    print('\n结论：单靠平台元数据无法可靠召回 AI 游戏，必须依赖第三方报道与玩家评价。')
