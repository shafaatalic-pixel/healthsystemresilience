#!/usr/bin/env python3
"""Build the 'Ask the record' index: every In Brief sentence on every published
piece, with the piece it came from and its DOI. Writes data/record.json and, if
index-next.html carries RECORD markers, embeds the same JSON there so the box
works without a fetch. Run after any article changes (the site-numbers workflow
calls it)."""
import glob, html, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def text(s): return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s))).strip()
dois = json.load(open(f'{ROOT}/data/dois.json'))
cards = open(f'{ROOT}/articles.html', encoding='utf-8').read()
meta = {}
for c in re.findall(r'<a class="fcard".*?</a>', cards, flags=re.S):
    slug = re.search(r'href="articles/([^/]+)/', c).group(1)
    meta[slug] = dict(
        type=re.search(r'data-type="([^"]+)"', c).group(1),
        country=re.search(r'data-country="([^"]+)"', c).group(1),
        thumb=re.search(r'src="([^"]+)"', c).group(1),
        read=text(re.search(r'class="rdtime"[^>]*>(.*?)<', c).group(1)) if 'rdtime' in c else '',
        title=text(re.search(r'<h[23][^>]*>(.*?)</h[23]>', c, flags=re.S).group(1)),
        dek=text(re.search(r'class="m">(.*?)</(?:div|p)>', c, flags=re.S).group(1)).split(' · ')[0],
        outlet=' · '.join(text(re.search(r'class="m">(.*?)</(?:div|p)>', c, flags=re.S).group(1)).split(' · ')[1:]),
    )
out = []
for p in sorted(glob.glob(f'{ROOT}/articles/*/*.html')):
    slug = p.split('/')[-2]
    if slug not in meta: continue
    a = open(p, encoding='utf-8').read()
    m = re.search(r'class="inbrief".*?<ul>(.*?)</ul>', a, flags=re.S)
    bullets = [text(b) for b in re.findall(r'<li>(.*?)</li>', m.group(1), flags=re.S)] if m else []
    k = re.search(r'class="kicker"[^>]*>(.*?)<', a)
    d = meta[slug]
    out.append(dict(slug=slug, url=f'articles/{slug}/{slug}.html', doi=dois.get(slug, ''),
                    kicker=text(k.group(1)) if k else '', **d, brief=bullets))
json.dump(out, open(f'{ROOT}/data/record.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
blob = json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
for page in ['index-next.html', 'index.html']:
    fp = f'{ROOT}/{page}'
    if not os.path.exists(fp): continue
    s = open(fp, encoding='utf-8').read()
    if '<!--RECORD:START-->' not in s: continue
    s2 = re.sub(r'<!--RECORD:START-->.*?<!--RECORD:END-->',
                lambda _: f'<!--RECORD:START--><script id="record-data" type="application/json">{blob}</script><!--RECORD:END-->', s, flags=re.S)
    if s2 != s: open(fp, 'w', encoding='utf-8').write(s2); print('embedded in', page)
# the library front on the home page: one card per piece, newest season first, special report first
def card(x):
    ct = 'sr' if x['type'] == 'Special report' else ''
    ib = html.escape(x['brief'][0]) if x['brief'] else html.escape(x['dek'])
    doi = f'<span class="doi">DOI {html.escape(x["doi"])}</span>' if x['doi'] else ''
    return (f'<a class="hn-card" data-country="{html.escape(x["country"])}" data-type="{html.escape(x["type"])}" href="{x["url"]}">'
            f'<div class="th"><img src="{x["thumb"]}" width="680" height="680" alt="" loading="lazy" decoding="async"></div>'
            f'<div class="b"><div class="mr"><span class="ct {ct}">{html.escape(x["type"])}</span><span>{html.escape(x["read"])}</span><span>{html.escape(x["outlet"].replace(" · ", " · "))}</span></div>'
            f'<h3>{html.escape(x["title"])}</h3><p class="ib">{ib}</p>'
            f'<div class="ft">{doi}<span class="go">Read &rarr;</span></div></div></a>')
order = sorted(out, key=lambda x: (x['type'] != 'Special report', x['type'] == 'Foundations', x['title']))
cards_html = '\n'.join(card(x) for x in order)
for page in ['index-next.html', 'index.html']:
    fp = f'{ROOT}/{page}'
    if not os.path.exists(fp): continue
    s = open(fp, encoding='utf-8').read()
    if '<!--LIBRARY:START-->' not in s: continue
    s2 = re.sub(r'<!--LIBRARY:START-->.*?<!--LIBRARY:END-->', lambda _: '<!--LIBRARY:START-->\n' + cards_html + '\n<!--LIBRARY:END-->', s, flags=re.S)
    if s2 != s: open(fp, 'w', encoding='utf-8').write(s2); print('library rendered in', page)
print(f'{len(out)} pieces, {sum(len(x["brief"]) for x in out)} sentences')
