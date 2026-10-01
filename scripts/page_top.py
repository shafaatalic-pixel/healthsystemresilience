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


# pages whose main action is not the roundtable get their own header button
CTA = {'initiative.html': ('Host the pilot', '#host')}


def header(here, cta=('Join Roundtable', '/roundtable.html')):
    nav = ''.join(
        f'<a class="here" aria-current="page" href="{h}">{t}</a>' if t == here else f'<a href="{h}">{t}</a>'
        for t, h in NAV)
    return ('<header class="site hs-top"><div class="hs-top-in"><div class="hs-top-row">'
            '<a class="hs-top-logo" href="/index.html" aria-label="HSREP home"><img src="/assets/logo-da7e214a.svg" '
            'width="2700" height="940" alt="HSREP, Health System Resilience &amp; Economic Protection"></a>'
            f'<nav class="hs-top-nav" aria-label="Main">{nav}</nav>'
            f'<a class="hs-srch" href="/search.html" aria-label="Search HSREP">{SEARCH_SVG}<span>Search</span></a>'
            f'<a class="hs-top-cta" href="{cta[1]}">{cta[0]}</a>'
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


# Pages with too few sections for the automatic band get a written one.
# Articles and films share a "Season 1 library" band, the way the initiative
# pages share theirs. (label, links, anchors to add: [(old, new)])
LIB = 'Season 1 library'
STATIC = {
    'articles.html': (LIB, [('Articles', '/articles.html', 'page'), ('Short films', '/films.html#short-films', ''),
                            ('Explainers', '/films.html#explainers', '')], []),
    'films.html': (LIB, [('Articles', '/articles.html', ''), ('Short films', '#short-films', ''),
                         ('Explainers', '#explainers', '')], []),
    'identity.html': ('On this page', [('The mark', '#identity', ''), ('Three principles', '#principles', ''),
                                       ('Colour and type', '#colour-and-type', '')],
                      [('<div class="pgrid rv">', '<div class="pgrid rv" id="principles">'),
                       ('<div class="specs rv">', '<div class="specs rv" id="colour-and-type">')]),
}
SPY = ('<script id="band-spy">(function(){var n=document.getElementById("secnav");if(!n||!("IntersectionObserver" in window))return;'
       'var m={};[].slice.call(n.querySelectorAll(\'a[href^="#"]\')).forEach(function(a){var t=document.getElementById(a.getAttribute("href").slice(1));if(t)m[t.id]=a;});'
       'var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){Object.keys(m).forEach(function(k){m[k].classList.toggle("active",k===e.target.id);});}});},{rootMargin:"-20% 0px -70% 0px"});'
       'Object.keys(m).forEach(function(k){io.observe(document.getElementById(k));});})();</script>')


def static_band(name, s):
    if name not in STATIC:
        return s
    label, links, ids = STATIC[name]
    html = ''.join(f'<a href="{h}"{" aria-current=" + chr(34) + "page" + chr(34) if c else ""}>{t}</a>'
                   for t, h, c in links)
    s = re.sub(r'<nav id="secnav" class="hs-band"[^>]*>[\s\S]*?</nav>',
               f'<nav id="secnav" class="hs-band" aria-label="{label}"><div class="sn-label">{label}</div>{html}</nav>',
               s, count=1)
    for old, new in ids:
        if new not in s:
            s = s.replace(old, new, 1)
    if 'id="band-spy"' not in s:
        s = s.replace('</body>', SPY + '</body>', 1)
    return s


def run(path):
    name = path.split('/')[-1]
    s = open(path, encoding='utf-8').read()
    o = s
    if name in SKIP and name != 'dashboard-demo.html':
        return False

    if name != 'dashboard-demo.html':
        here = 'Articles' if path.startswith('articles/') else HERE.get(name)
        s = re.sub(r'<header\b[\s\S]*?</header>', lambda m: header(here, CTA.get(name, ('Join Roundtable', '/roundtable.html'))), s, count=1)

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

    s = static_band(name, s)

    if s != o:
        open(path, 'w', encoding='utf-8').write(s)
        return True
    return False


if __name__ == '__main__':
    for p in sorted(glob.glob('*.html') + glob.glob('articles/*/*.html')):
        print(('changed ' if run(p) else 'same    ') + p)
