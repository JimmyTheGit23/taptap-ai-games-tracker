import urllib.request, gzip, re, json, urllib.parse, time

UA = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}


def get(u, retry=2):
    for k in range(retry + 1):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30)
            d = r.read()
            if r.headers.get('Content-Encoding') == 'gzip':
                d = gzip.decompress(d)
            return d.decode('utf-8', 'ignore')
        except Exception as e:
            if k == retry:
                raise
            time.sleep(1.5)


def nuxt_payload(t):
    i = t.find('[["Reactive"')
    if i < 0:
        return None
    dep = 0
    for j in range(i, len(t)):
        if t[j] == '[':
            dep += 1
        elif t[j] == ']':
            dep -= 1
            if dep == 0:
                return json.loads(t[i:j + 1])
    return None


def deref(p, node, depth=0, maxd=6):
    """Nuxt flat payload: ints are indices into p."""
    if depth > maxd:
        return None
    if isinstance(node, int):
        if 0 <= node < len(p):
            return deref(p, p[node], depth + 1, maxd)
        return node
    if isinstance(node, str) or isinstance(node, bool) or node is None or isinstance(node, float):
        return node
    if isinstance(node, list):
        return [deref(p, x, depth + 1, maxd) for x in node]
    if isinstance(node, dict):
        return {k: deref(p, v, depth + 1, maxd) for k, v in node.items()}
    return node


def fetch_platforms(app_id):
    """取支持平台列表，如 ['android','ios'] / ['pc']。

    platform_info.supported_platforms 是三层嵌套引用，deref 默认深度取不到，
    这里在原始 payload 上手动逐层解引用。
    """
    t = get(f'https://www.taptap.cn/app/{app_id}')
    p = nuxt_payload(t)
    if not p:
        return []
    for o in p:
        if isinstance(o, dict) and 'platform_info' in o:
            pi = p[o['platform_info']]
            sp = pi.get('supported_platforms')
            arr = p[sp] if isinstance(sp, int) else sp
            keys = []
            if isinstance(arr, list):
                for el in arr:
                    node = p[el] if isinstance(el, int) else el
                    if isinstance(node, dict):
                        k = node.get('key')
                        val = p[k] if isinstance(k, int) else k
                        if isinstance(val, str):
                            keys.append(val)
            return keys
    return []


PLATFORM_LABEL = {
    frozenset(['pc']): 'PC',
    frozenset(['android']): '手游(安卓)',
    frozenset(['ios']): '手游(iOS)',
    frozenset(['android', 'ios']): '手游(双端)',
}


def platform_label(keys):
    ks = frozenset(keys)
    if ks in PLATFORM_LABEL:
        return PLATFORM_LABEL[ks]
    parts = [('手游' if 'android' in ks or 'ios' in ks else ''),
             ('PC' if 'pc' in ks else '')]
    return '+'.join(x for x in parts if x) or '未标注'


if __name__ == '__main__':
    t = get('https://www.taptap.cn/app/746715')
    p = nuxt_payload(t)
    for o in p:
        if isinstance(o, dict) and 'identifier' in o and 'title' in o and 'id' in o:
            full = deref(p, o)
            print(json.dumps(full, ensure_ascii=False, indent=1)[:4000])
            break
