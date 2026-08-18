"""为清单游戏下载 1-2 张画面截图到 screenshots/。

来源优先级：TapTap 详情页 screenshots 字段（有 app_id）
          → Steam 商店页（LINKS 里有 steampowered 链接）
          → itch.io 页面（雾岛新闻社）
无源条目不下载，在看板标注「暂无画面」。
"""
import json, os, re, time, html as H
import urllib.request, gzip
from taptap_probe import get, nuxt_payload, deref
from build_list import ROWS, LINKS

OUT = 'screenshots'
os.makedirs(OUT, exist_ok=True)

UA_STEAM = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36',
    'Cookie': 'birthtime=568022401; mature_content=1',
}


def download(url, path):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = r.read()
    with open(path, 'wb') as fp:
        fp.write(d)
    return len(d)


def taptap_shots(app_id, n=2):
    t = get(f'https://www.taptap.cn/app/{app_id}')
    p = nuxt_payload(t)
    for o in p:
        if isinstance(o, dict) and 'identifier' in o and 'title' in o and 'id' in o:
            f = deref(p, o)
            break
    out = []
    for s in (f.get('screenshots') or [])[:n]:
        if isinstance(s, dict) and s.get('url'):
            out.append(s['url'])
    return out


def steam_shots(appid, n=2):
    req = urllib.request.Request(
        f'https://store.steampowered.com/app/{appid}/', headers=UA_STEAM)
    r = urllib.request.urlopen(req, timeout=30)
    d = r.read()
    if r.headers.get('Content-Encoding') == 'gzip':
        d = gzip.decompress(d)
    h = d.decode('utf-8', 'ignore')
    i = h.find('&quot;screenshots&quot;')
    if i < 0:
        return []
    seg = H.unescape(h[i:i + 12000])
    full = re.findall(r'"(?:full|fullsize)":"([^"]+)"', seg)
    urls = [u.replace('\\/', '/') for u in full]
    return list(dict.fromkeys(urls))[:n]


def itch_shots(url, n=2):
    t = get(url)
    imgs = re.findall(r'https://img\.itch\.zone/[^"\'\\ ]+\.(?:png|jpg|jpeg)', t)
    return list(dict.fromkeys(imgs))[:n]


def steam_appid_from_links(game):
    for u in LINKS.get(game, []):
        m = re.search(r'steampowered\.com/app/(\d+)', u)
        if m:
            return m.group(1)
    return None


def itch_from_links(game):
    for u in LINKS.get(game, []):
        if 'itch.io' in u:
            return u
    return None


def main():
    manifest = {}
    for r in ROWS:
        game = r['game']
        key = re.sub(r'[^\w一-鿿]+', '_', game)[:40]
        urls, src = [], None
        try:
            if r.get('app_id'):
                urls, src = taptap_shots(r['app_id']), 'taptap'
            if not urls:
                sid = steam_appid_from_links(game)
                if sid:
                    urls, src = steam_shots(sid), 'steam'
            if not urls:
                iu = itch_from_links(game)
                if iu:
                    urls, src = itch_shots(iu), 'itch'
        except Exception as e:
            print(f'  [ERR] {game}: {e!r}')
            urls = []
        files = []
        for k, u in enumerate(urls, 1):
            ext = '.png' if '.png' in u else '.jpg'
            fn = f'{key}_{k}{ext}'
            try:
                sz = download(u, os.path.join(OUT, fn))
                files.append(fn)
                print(f'  [ok] {game} #{k} ({src}, {sz//1024}KB)')
            except Exception as e:
                print(f'  [fail] {game} #{k}: {e!r}')
            time.sleep(0.4)
        manifest[game] = files
        time.sleep(0.6)
    with open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8') as fp:
        json.dump(manifest, fp, ensure_ascii=False, indent=1)
    have = sum(1 for v in manifest.values() if v)
    print(f'\n完成：{have}/{len(manifest)} 款有画面')


if __name__ == '__main__':
    main()
