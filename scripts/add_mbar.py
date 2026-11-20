"""Add the phone/tablet section strip (nav.hs-mbar) under the top header on every page with the main nav.
Idempotent: pages that already have the strip are skipped. Run from the website folder."""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ITEMS = [('/prevention.html', 'Prevention guides', 'lead'), ('/season-1.html', 'Season 1', ''),
         ('/articles.html', 'Articles', ''), ('/initiative.html', 'Initiative', ''),
         ('/impact.html', 'Impact', ''), ('/about.html', 'About', '')]
VER = '20261120a'


def bar(here):
    out = []
    for h, t, c in ITEMS:
        attrs = (f' class="{c}"' if c else '') + f' href="{h}"' + (' aria-current="page"' if h == here else '')
        out.append(f'<a{attrs}>{t}</a>')
    return '<nav class="hs-mbar" aria-label="Sections">' + ''.join(out) + '</nav>'


changed, skipped = [], []
for p in sorted(ROOT.rglob('*.html')):
    rel = p.relative_to(ROOT).as_posix()
    if '_mockups' in rel:
        continue
    s = p.read_text(encoding='utf-8')
    if 'hs-top-nav' not in s:
        continue
    s2 = re.sub(r'top-1\.css\?v=[0-9a-z]+', f'top-1.css?v={VER}', s)
    if 'class="hs-mbar"' not in s2:
        i = s2.index('hs-top-nav')
        j = s2.index('</header>', i) + len('</header>')
        nav = s2[s2.rfind('<nav', 0, i):s2.index('</nav>', i)]
        m = re.search(r'class="here"[^>]*href="([^"]+)"', nav)
        here = m.group(1) if m else ''
        s2 = s2[:j] + bar(here) + s2[j:]
    if s2 != s:
        p.write_text(s2, encoding='utf-8')
        changed.append(rel)
    else:
        skipped.append(rel)

print('changed', len(changed), 'skipped', len(skipped))
if skipped:
    print('skipped:', ', '.join(skipped))
