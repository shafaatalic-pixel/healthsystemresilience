#!/usr/bin/env python3
"""Build gap-map.html, the Prevention Gap Map page.

The page shell (head styles, header, footer, page scripts) is taken from
dashboard-demo.html so the Gap Map always matches the initiative pages. The
page body lives in scripts/gapmap_main.html, its styles in
assets/css/gapmap-1.css, its script in assets/gapmap-1.js and its numbers in
data/gapmap-2025.json (HRSA UDS H80-2025, Table 6B; see the Methods section).

Also adds the "Gap Map" tab to the Prevention Adoption Initiative band on the
other initiative pages, and the page to sitemap.xml and llms.txt.
Safe to run more than once.

Run from the website root:  python3 scripts/gapmap_build.py
"""
import json
import re

TODAY = '2026-11-05'
URL = 'https://hsraep.org/gap-map.html'
TITLE = 'Prevention Gap Map: Michigan colorectal screening | HSREP'
DESC = ("Colorectal cancer screening at all 39 federally funded health centers in Michigan, "
        "from HRSA's 2025 data, against the 72.8% Healthy People 2030 target.")
OG_TITLE = 'Prevention Gap Map: where Michigan can close the colorectal screening gap'
OG_DESC = ("Find a health center, compare it with others, and see what reaching the 72.8% target would take. "
           "Public HRSA data, updated each year.")

BAND_ITEMS = [('Overview', '/initiative.html'), ('The Completion Worklist', '/dashboard-demo.html'),
              ('Gap Map', '/gap-map.html'), ('Future roadmap', '/initiative-next.html')]


def band(cur, cls='hs-band'):
    links = ''.join(f'<a href="{h}"{" aria-current=" + chr(34) + "page" + chr(34) if h == cur else ""}>{t}</a>'
                    for t, h in BAND_ITEMS)
    return (f'<nav id="secnav" class="{cls}" aria-label="Prevention Adoption Initiative">'
            f'<div class="sn-label">Prevention Adoption Initiative</div>{links}</nav>')


BAND_RE = re.compile(r'<nav id="secnav" class="(hs-band[^"]*)" aria-label="Prevention Adoption Initiative">.*?</nav>', re.S)


def jsonld():
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "@id": URL + "#webpage", "url": URL, "name": TITLE, "description": DESC,
             "isPartOf": {"@type": "WebSite", "name": "HSREP", "url": "https://hsraep.org/"},
             "about": {"@id": URL + "#dataset"}, "dateModified": TODAY, "inLanguage": "en"},
            {"@type": "Dataset", "@id": URL + "#dataset",
             "name": "Prevention Gap Map: colorectal cancer screening at Michigan health centers, 2025",
             "description": ("Colorectal cancer screening rates (adults 46 to 75) for the 39 HRSA-funded health centers "
                             "in Michigan, with each center's distance from the Healthy People 2030 target of 72.8%."),
             "creator": {"@type": "Organization", "name": "HSREP", "url": "https://hsraep.org/"},
             "isBasedOn": "https://data.hrsa.gov/data/download",
             "temporalCoverage": "2025", "spatialCoverage": "Michigan, United States",
             "distribution": {"@type": "DataDownload", "encodingFormat": "application/json",
                              "contentUrl": "https://hsraep.org/data/gapmap-2025.json"},
             "license": "https://creativecommons.org/licenses/by/4.0/", "dateModified": TODAY}
        ]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


def build():
    s = open('dashboard-demo.html', encoding='utf-8').read()
    main = open('scripts/gapmap_main.html', encoding='utf-8').read()

    def sub1(pat, rep, s, flags=0):
        new, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
        if n != 1:
            raise SystemExit('pattern not found: ' + pat)
        return new

    s = sub1(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, re.S)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_DESC}">', s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">', s)
    s = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{OG_TITLE}">', s, count=1)
    s = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{OG_DESC}">', s, count=1)
    # the worklist page's structured data describes the worklist; replace it with the map's
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', '', s, flags=re.S)
    s = s.replace('</head>', jsonld() + '<link rel="stylesheet" href="/assets/css/gapmap-1.css?v=20261105a"></head>', 1)
    s = BAND_RE.sub(lambda m: band('/gap-map.html', m.group(1)), s, count=1)
    s = sub1(r'<main\b.*?</main>\s*(?:<div id="gm-tip"[^>]*></div>)?', main.strip(), s, re.S)
    if 'gapmap-1.js' not in s:
        s = s.replace('</body>', '<script src="/assets/gapmap-1.js?v=20261105a" defer></script></body>', 1)
    for t in ('</head>', '<body', '</body>', '</html>'):
        assert t in s, t
    open('gap-map.html', 'w', encoding='utf-8').write(s)
    print('wrote gap-map.html', len(s))


def bands():
    for f in ('initiative.html', 'initiative-next.html', 'dashboard-demo.html', 'worklist-quick.html'):
        s = open(f, encoding='utf-8').read()
        m = BAND_RE.search(s)
        if not m:
            print('no band in', f)
            continue
        cur = re.search(r'<a href="([^"]+)" aria-current="page">', m.group(0))
        new = band(cur.group(1) if cur else '', m.group(1))
        if new != m.group(0):
            s = s[:m.start()] + new + s[m.end():]
            open(f, 'w', encoding='utf-8').write(s)
            print('band updated:', f)


def sitemap():
    s = open('sitemap.xml', encoding='utf-8').read()
    if URL in s:
        return
    entry = (f'  <url>\n    <loc>{URL}</loc>\n    <lastmod>{TODAY}</lastmod>\n'
             '    <changefreq>yearly</changefreq>\n    <priority>0.8</priority>\n  </url>\n')
    s = s.replace('</urlset>', entry + '</urlset>', 1)
    open('sitemap.xml', 'w', encoding='utf-8').write(s)
    print('sitemap: added')


def llms():
    s = open('llms.txt', encoding='utf-8').read()
    if URL in s:
        return
    line = (f"- [Prevention Gap Map]({URL}): Colorectal cancer screening at each of Michigan's 39 federally funded "
            "health centers in 2025 (HRSA Uniform Data System, adults 46 to 75), shown against the Healthy People 2030 "
            "target of 72.8%. Michigan: 91,450 of 187,620 eligible adults screened (48.7%); about 45,100 more would reach "
            "the target. Four centers have no published rate and nothing is estimated for them. A screening rate does not "
            "show whether a positive stool test led to a colonoscopy. Not a ranking. Updated each year.\n")
    anchor = '- [Is your clinic a fit for the pilot?]'
    s = s.replace(anchor, line + anchor, 1) if anchor in s else s + '\n' + line
    open('llms.txt', 'w', encoding='utf-8').write(s)
    print('llms.txt: added')


if __name__ == '__main__':
    build()
    bands()
    sitemap()
    llms()
