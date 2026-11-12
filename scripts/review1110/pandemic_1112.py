#!/usr/bin/env python3
"""pandemic-1112: the 3.6 million were COVID-related patients (Shafaat, 12 Nov 2026), not "people reached".
Fixes the initiative line and amends corrections entry -6 (visible + JSON-LD). Idempotent. Run from website/."""
import pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent.parent
def rep(f, old, new):
    p = root / f; s = p.read_text(encoding='utf-8')
    if new in s and old not in s: print(f'= {f} (already)'); return
    if s.count(old) != 1: sys.exit(f'{f}: expected 1, found {s.count(old)}: {old[:60]}')
    p.write_text(s.replace(old, new), encoding='utf-8'); print(f'+ {f}')
rep('initiative.html',
    'During COVID, Praava&rsquo;s doctor hotline, nationwide home sample collection and six-hour traveler testing reached about 3.6 million people, about 2% of Bangladesh&rsquo;s population, by my record of that work.',
    'During COVID, Praava served about 3.6 million COVID-related patients, about 2% of Bangladesh&rsquo;s population, through nationwide home sample collection, six-hour traveler testing and a doctor hotline, by my record of that work.')
rep('corrections.html',
    '<p>The page said Praava &ldquo;served&rdquo; about 3.6 million people, about 2% of Bangladesh, and about 8% of Dhaka. The figure counts people reached by its pandemic services (a doctor hotline, home sample collection and traveler testing), not patients treated. The line now says reached, names the services, drops the Dhaka share and says the figure comes from the founder&rsquo;s record of that work.</p>',
    '<p>The page said Praava &ldquo;served&rdquo; about 3.6 million people, about 2% of Bangladesh, and about 8% of Dhaka. The line now says the 3.6 million were COVID-related patients, names the services (home sample collection, traveler testing and a doctor hotline), drops the Dhaka share and says the figure comes from the founder&rsquo;s record of that work. Amended 12 Nov 2026: the first version of this entry, and of the page line, said the figure counted people reached rather than patients. The founder confirmed they were COVID-related patients, and both now say so.</p>')
rep('corrections.html',
    '"description":"The 3.6 million figure counts people reached by Praava\'s pandemic services, not patients. The line now says reached, names the services and drops the Dhaka share."}',
    '"description":"The 3.6 million figure is COVID-related patients served by Praava. The line now says so, names the services and drops the Dhaka share. Amended 12 Nov 2026: the first version said people reached rather than patients."}')
print('done: pandemic-1112')
