#!/usr/bin/env python3
"""uiux-1107: picks 1-4 of the 7 Nov 2026 UI/UX review of the Completion Worklist demo.

Run from the website/ folder:  python3 scripts/uiux1107/apply.py
  worklist/index.html   start card with the sample case, tours grouped by task, setup in a drawer,
                        tour box beside the screen, #case-<code> deep link, Ask HSREP in the demo bar
  dashboard-demo.html   sample case and tours grouped by task in #tours, hero button, rail label
  assets/analytics.js   no roundtable campaign bar on /worklist/ or the quick demo
Idempotent: a file that already carries the marker is left alone.
"""
import sys, pathlib
MARK = 'uiux-1107'
here = pathlib.Path(__file__).resolve().parent
root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent
JS = (here / 'block.js').read_text(encoding='utf-8')
CSS = (here / 'block.css').read_text(encoding='utf-8')
DASH_TOURS = (here / 'dash_tours.html').read_text(encoding='utf-8').rstrip('\n')
DASH_CSS = (here / 'dash.css').read_text(encoding='utf-8')

def sub_once(s, old, new, what):
    n = s.count(old)
    if n != 1: sys.exit(f'{what}: expected 1 match, found {n}')
    return s.replace(old, new)

p = root / 'worklist' / 'index.html'; s = p.read_text(encoding='utf-8')
if MARK in s: print('worklist: already applied')
else:
    i = s.index('/* Layout: a working tool.'); j = s.index('</style>', i)
    s = s[:j] + CSS + s[j:]
    s = sub_once(s, '\n// Deep links from the website: #tour-overview', JS + '\n// Deep links from the website: #tour-overview', 'worklist js anchor')
    s = sub_once(s, '/assets/analytics.js?v=20261015b', '/assets/analytics.js?v=20261107a', 'worklist analytics version')
    p.write_text(s, encoding='utf-8'); print('worklist: patched')

p = root / 'dashboard-demo.html'; s = p.read_text(encoding='utf-8')
if MARK in s: print('dashboard: already applied')
else:
    a = s.index('<section class="pai-card" id="tours"'); b = s.index('</section>', a) + len('</section>')
    s = s[:a] + DASH_TOURS + s[b:]
    anchor = '.cw-tour .go{margin-top:auto;font-weight:600;color:#B8402C}'
    s = sub_once(s, anchor, anchor + DASH_CSS, 'dashboard css anchor')
    s = sub_once(s, '<a class="btn pai-secondary" href="/worklist/">Open the demo</a>', '<a class="btn pai-secondary" href="/worklist/#case-P-1407">Try a sample case</a>', 'dashboard hero button')
    s = sub_once(s, '<a href="#tours">Guided tours</a>', '<a href="#tours">Try it</a>', 'dashboard rail')
    p.write_text(s, encoding='utf-8'); print('dashboard: patched')

p = root / 'assets' / 'analytics.js'; s = p.read_text(encoding='utf-8')
old = 'if (/\\/(index|initiative|initiative-next|dashboard-demo|pilot-fit)\\.html$/.test(location.pathname) || location.pathname === "/") { barHidden(); return; }'
new = '/* uiux-1107: nor inside the demo tools. */\n if (/\\/(index|initiative|initiative-next|dashboard-demo|pilot-fit|worklist-quick)\\.html$/.test(location.pathname) || /^\\/worklist\\/(index\\.html)?$/.test(location.pathname) || location.pathname === "/") { barHidden(); return; }'
if MARK in s: print('analytics: already applied')
else:
    s = sub_once(s, old, new, 'analytics campaign rule'); p.write_text(s, encoding='utf-8'); print('analytics: patched')
