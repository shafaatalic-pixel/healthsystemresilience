#!/usr/bin/env python3
"""dhaka-1112: the Dhaka share (about 8%) is accurate (Shafaat, 12 Nov 2026).
hsraep.org corrections entry -6 says it was left out for length, not doubted; hsrep.bd founder line gains the pandemic figure with the Dhaka share. Idempotent. Run from website/."""
import pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent.parent
bd = root.parent / 'hsrep-bd'
def rep(p, old, new, n=1):
    s = p.read_text(encoding='utf-8')
    if new in s and old not in s: print(f'= {p.name} (already)'); return
    if s.count(old) != n: sys.exit(f'{p}: expected {n}, found {s.count(old)}: {old[:70]}')
    p.write_text(s.replace(old, new), encoding='utf-8'); print(f'+ {p.name}')
c = root / 'corrections.html'
rep(c, 'names the services (home sample collection, traveler testing and a doctor hotline), drops the Dhaka share and says the figure comes from',
       'names the services (home sample collection, traveler testing and a doctor hotline), keeps the line to one figure (the Dhaka share, about 8%, is accurate and was left out for length) and says the figure comes from')
rep(c, 'The line now says so, names the services and drops the Dhaka share. Amended 12 Nov 2026',
       'The line now says so, names the services and keeps to one figure; the Dhaka share (about 8%) is accurate and was left out for length. Amended 12 Nov 2026')
old_bd = 'launched Ghore Lab, a home sample-collection service, during COVID. I sold'
new_bd = 'launched Ghore Lab, a home sample-collection service, during COVID, when Praava served about 3.6 million COVID-related patients, about 2% of Bangladesh&rsquo;s population and about 8% of Dhaka&rsquo;s, by my record of that work. I sold'
for f in (bd / 'index.html', bd / 'scripts' / 'build.py'):
    rep(f, old_bd, new_bd)
print('done: dhaka-1112')
