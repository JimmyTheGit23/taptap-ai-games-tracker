"""抓取 TapTap 详情页，核准评分/厂商/标签/预约数等动态字段。"""
import json, sys, time
from taptap_probe import get, nuxt_payload, deref

APP_IDS = {
    59622: '异常',
    746715: '群星低语-Whispers from the Star',
    156070: '假如我是人工智能If I am AI',
    771203: 'AIFriends',
    773812: '乌托',
}


def fetch(app_id):
    t = get(f'https://www.taptap.cn/app/{app_id}')
    p = nuxt_payload(t)
    if not p:
        return None
    for o in p:
        if isinstance(o, dict) and 'identifier' in o and 'title' in o and 'id' in o:
            f = deref(p, o)
            devs = f.get('developers') or []
            stat = f.get('stat') or {}
            rating = (stat.get('rating') or {}) if isinstance(stat, dict) else {}
            tags = [x.get('value') for x in (f.get('tags') or []) if isinstance(x, dict)]
            desc = f.get('description')
            if isinstance(desc, dict):
                desc = desc.get('text') or desc.get('detail') or ''
            return dict(
                app_id=app_id,
                title=f.get('title'),
                score=rating.get('score'),
                developer=devs[0].get('name') if devs and isinstance(devs[0], dict) else None,
                tags=tags,
                reserve_count=stat.get('reserve_count') if isinstance(stat, dict) else None,
                fans_count=stat.get('fans_count') if isinstance(stat, dict) else None,
                desc_len=len(desc) if isinstance(desc, str) else 0,
                desc_head=(desc[:200] if isinstance(desc, str) else ''),
            )
    return None


if __name__ == '__main__':
    out = []
    for aid, nm in APP_IDS.items():
        try:
            r = fetch(aid)
            out.append(r)
            print(f"[{aid}] {r['title']} | score={r['score']} | dev={r['developer']} | "
                  f"tags={r['tags']} | reserve={r['reserve_count']} | fans={r['fans_count']}")
        except Exception as e:
            print(f"[{aid}] {nm} ERR {e!r}")
        time.sleep(1)
    with open('taptap_live.json', 'w', encoding='utf-8') as fp:
        json.dump([x for x in out if x], fp, ensure_ascii=False, indent=1)
    print('saved taptap_live.json')
