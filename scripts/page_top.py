#!/usr/bin/env python3
"""One page top for every HSREP page.

Replaces each page's first <header> with the canonical header, links
assets/css/top-1.css last in <head>, and turns every section sub-nav into the
same "On this page" band (#secnav.hs-band). Safe to run more than once.

Run from the website root:  python3 scripts/page_top.py
"""
import glob
import re

SEARCH_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M10.5 3a7.5 7.5 0 1 0 '
              '4.6 13.4l4.2 4.2 1.4-1.4-4.2-4.2A7.5 7.5 0 0 0 10.5 3zm0 2a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11z"/></svg>')
MENU_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 7h16M4 12h16M4 17h16"/></svg>')
NAV = [('Home', '/index.html'), ('Evidence', '/season-1.html'), ('Articles', '/articles.html'),
       ('Impact', '/impact.html'), ('Initiative', '/initiative.html'), ('About', '/about.html')]

# which top-nav item is "here" on each page
HERE = {
    'index.html': 'Home',
    'season-1.html': 'Evidence', 'methodology.html': 'Evidence',
    'articles.html': 'Articles', 'films.html': 'Articles',
    'impact.html': 'Impact',
    'initiative.html': 'Initiative', 'initiative-next.html': 'Initiative',
    'about.html': 'About', 'media.html': 'About', 'identity.html': 'About',
}
SKIP = {'roundtable-console.html', 'dashboard-demo.html'}  # private console; demo keeps its app header
LINK = '<link rel="stylesheet" href="/assets/css/top-1.css">'


def header(here):
    nav = ''.join(
        f'<a class="here" aria-current="page" href="{h}">{t}</a>' if t == here else f'<a href="{h}">{t}</a>'
        for t, h in NAV)
    return ('<header class="site hs-top"><div class="hs-top-in"><div class="hs-top-row">'
            '<a class="hs-top-logo" href="/index.html" aria-label="HSREP home"><img src="/assets/logo-da7e214a.svg" '
            'width="2700" height="940" alt="HSREP, Health System Resilience &amp; Economic Protection"></a>'
            f'<nav class="hs-top-nav" aria-label="Main">{nav}</nav>'
            f'<a class="hs-srch" href="/search.html" aria-label="Search HSREP">{SEARCH_SVG}<span>Search</span></a>'
            '<a class="hs-top-cta" href="/roundtable.html">Join Roundtable</a>'
            '<button id="hmenu-btn" type="button" aria-label="Menu" aria-expanded="false" '
            f'aria-controls="hmenu-panel">{MENU_SVG}<span>Menu</span></button>'
            '</div></div></header>')


def pai_band(cur):
    items = [('Overview', 'initiative.html'), ('Explore the demo', 'dashboard-demo.html'),
             ('Future roadmap', 'initiative-next.html')]
    cur_attr = ' aria-current="page"'
    links = ''.join(f'<a href="/{h}"{cur_attr if h == cur else ""}>{t}</a>' for t, h in items)
    cls = 'hs-band static' if cur == 'dashboard-demo.html' else 'hs-band'
    return (f'<nav id="secnav" class="{cls}" aria-label="Prevention Adoption Initiative">'
            f'<div class="sn-label">Prevention Adoption Initiative</div>{links}</nav>')


def run(path):
    name = path.split('/')[-1]
    s = open(path, encoding='utf-8').read()
    o = s
    if name in SKIP and name != 'dashboard-demo.html':
        return False

    if name != 'dashboard-demo.html':
        here = 'Articles' if path.startswith('articles/') else HERE.get(name)
        s = re.sub(r'<header\b[\s\S]*?</header>', lambda m: header(here), s, count=1)

    if LINK not in s:
        s = s.replace('</head>', LINK + '</head>', 1)

    # bands
    s = s.replace('<nav id="secnav">', '<nav id="secnav" class="hs-band">')
    s = s.replace('<nav class="mth-secnav" aria-label="On this page"><span class="sn-lab">',
                  '<nav id="secnav" class="mth-secnav hs-band" aria-label="On this page"><span class="sn-lab sn-label">')
    if name in ('initiative.html', 'initiative-next.html', 'dashboard-demo.html'):
        m = re.search(r'\n?<nav class="pai-sub"[\s\S]*?</nav>\n?', s)
        if m:
            s = s[:m.start()] + '\n' + s[m.end():]
            if name == 'dashboard-demo.html':
                # directly under the app header
                s = re.sub(r'(<header class="d"[\s\S]*?</header>)', lambda mm: mm.group(1) + pai_band(name), s, count=1)
            else:
                s = s.replace('</header>', '</header>' + pai_band(name), 1)

    # home-style band builder: no "Top", no "The mark", no extra CTA
    s = s.replace("||s.id==='top'", "&&s.id!=='mark'")
    s = s.replace("var cta=document.createElement('a');cta.className='sn-cta';cta.href='#participate';"
                  "cta.textContent='Participate \\u2192';nav.appendChild(cta);", '')

    if s != o:
        open(path, 'w', encoding='utf-8').write(s)
        return True
    return False


if __name__ == '__main__':
    for p in sorted(glob.glob('*.html') + glob.glob('articles/*/*.html')):
        print(('changed ' if run(p) else 'same    ') + p)
