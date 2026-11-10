#!/usr/bin/env python3
"""review-1110: fixes from the 10 Nov 2026 platform review (items 1, 2, 4, 5, 6, 7, 8) and a worklist band on the initiative page.

Run from the website/ folder:  python3 scripts/review1110/apply.py [website_root] [hsrep_bd_root]
Idempotent: each replacement is skipped when its new text is already in place.
  1  Praava 34% removed (initiative.html, hsrep.bd) + corrections entry
  2  Scroll reveal: threshold .12 -> 0 on every page; tour frame forces reveals
  4  Pandemic line: "reached", names the services, drops the Dhaka share, says where the figure comes from
  5  "17 years" lines say "in health care since 2021" (bylines, JSON-LD, llms.txt, About, Media)
  6  One pilot story across initiative, dashboard-demo and worklist
  7  Status phrasings: no channel, funder, site or running pilot implied
  8  "Book 30 minutes" near the top of the initiative, Gap Map and tour; two-counts ask on initiative and tour; one label
  +  Worklist band under the initiative hero
"""
import sys, pathlib, re

here = pathlib.Path(__file__).resolve().parent
root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent
bd = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else root.parent / 'hsrep-bd'
CAL = 'https://calendly.com/shafaat-alic/30min'
MAIL2 = 'mailto:contact@hsraep.org?subject=Free%20follow-up%20readout'
log = []
cache = {}

def get(p):
    if p not in cache: cache[p] = p.read_text(encoding='utf-8')
    return cache[p]

def rep(p, old, new, n=1, what=''):
    s = get(p); c = s.count(old)
    if (old in new and new in s) or (c == 0 and ((new and new in s) or not new)):
        log.append(f'  = {p.name}: {what or old[:50]} (already)'); return
    if c != n: sys.exit(f'{p}: {what or old[:70]!r}: expected {n}, found {c}')
    cache[p] = s.replace(old, new); log.append(f'  + {p.name}: {what or old[:50]} x{n}')

W = lambda f: root / f

# ---------- 1. Praava 34% ----------
ini = W('initiative.html')
rep(ini, '<div><div class="n">34%</div><h3>Screening volume inside a real delivery system</h3><p>At Praava Health in Bangladesh, as Head of Marketing &amp; Corporate Sales, I redesigned the diagnostic packages and launched Ghore Lab, a home sample-collection service, during COVID. Laboratory screening utilization rose 34% from 2021 to 2022. That was volume and follow-through, not screening completion; the pilot measures completion.</p></div>',
    '<div><div class="n">Home</div><h3>Lab tests brought to people&rsquo;s homes</h3><p>At Praava Health in Bangladesh, as Head of Marketing &amp; Corporate Sales, I redesigned the diagnostic packages and launched Ghore Lab, a home sample-collection service, during COVID. That work was about access and follow-through for tests, not screening completion; the pilot measures completion.</p></div>', what='34% tile')
# 1 + 4: why-me paragraph
rep(ini, 'I led the diagnostic-package redesign and the Ghore Lab launch behind the 34% above. During the pandemic, Praava served about 2% of Bangladesh&rsquo;s population, about 3.6 million people, and about 8% of Dhaka&rsquo;s.',
    'I led the diagnostic-package redesign and the Ghore Lab launch. During COVID, Praava&rsquo;s doctor hotline, nationwide home sample collection and six-hour traveler testing reached about 3.6 million people, about 2% of Bangladesh&rsquo;s population, by my record of that work.', what='why-me 34% + pandemic line')
rep(ini, 'launched Ghore Lab, a home sample-collection service; laboratory screening utilization rose 34% from 2021 to 2022, which was volume and follow-through, not screening completion.',
    'launched Ghore Lab, a home sample-collection service, during COVID.', n=2, what='FAQ 34% (visible + JSON-LD)')
for f in (bd / 'scripts' / 'build.py', bd / 'index.html'):
    rep(f, 'during COVID; laboratory screening utilization rose 34% from 2021 to 2022. I sold', 'during COVID. I sold', what='hsrep.bd 34%')

cor = W('corrections.html')
entry = ('<div class="rd" id="prevention-adoption-initiative-5"><div class="rk"><span class="rl">Corrected</span><time datetime="2026-11-10">10 Nov 2026</time></div><div><b><a href="/initiative.html">Prevention Adoption Initiative</a> and <a href="https://hsrep.bd">HSREP Bangladesh</a> &middot; Praava 34% figure removed</b><p>The 12 October correction relabelled the Praava track-record figure as laboratory revenue. The 23 October version of the initiative page brought back the earlier wording, laboratory screening utilization up 34%, and the Bangladesh edition carried it too. Until the employment record settles which measure the 34% describes, the figure is off both sites. The archived 23 October PDF still carries the earlier wording.</p></div></div>\n'
         '<div class="rd" id="prevention-adoption-initiative-6"><div class="rk"><span class="rl">Clarified</span><time datetime="2026-11-10">10 Nov 2026</time></div><div><b><a href="/initiative.html#why-me">Prevention Adoption Initiative</a> &middot; Pandemic figure reworded</b><p>The page said Praava &ldquo;served&rdquo; about 3.6 million people, about 2% of Bangladesh, and about 8% of Dhaka. The figure counts people reached by its pandemic services (a doctor hotline, home sample collection and traveler testing), not patients treated. The line now says reached, names the services, drops the Dhaka share and says the figure comes from the founder&rsquo;s record of that work.</p></div></div>\n')
rep(cor, '</div>\n<h2>Found something that does not hold</h2>', entry + '</div>\n<h2>Found something that does not hold</h2>', what='corrections entries')
s = get(cor)
m = re.search(r'(#roundtable-01-2","description":"(?:[^"\\]|\\.)*")\}\]', s)
li = (',{"@type":"ListItem","position":16,"name":"Prevention Adoption Initiative, Praava 34% figure removed","url":"https://hsraep.org/corrections.html#prevention-adoption-initiative-5","description":"The 23 October page brought back the earlier utilization wording for the Praava 34% figure, as did the Bangladesh edition. The figure is off both sites until the employment record settles which measure it describes."}'
      ',{"@type":"ListItem","position":17,"name":"Prevention Adoption Initiative, pandemic figure reworded","url":"https://hsraep.org/corrections.html#prevention-adoption-initiative-6","description":"The 3.6 million figure counts people reached by Praava\'s pandemic services, not patients. The line now says reached, names the services and drops the Dhaka share."}')
if '#prevention-adoption-initiative-5"' not in s:
    s = s[:m.end(1)] + '}' + li + ']' + s[m.end():]
    s = s.replace('"numberOfItems":15', '"numberOfItems":17', 1)
    cache[cor] = s; log.append('  + corrections.html: JSON-LD list items')

# ---------- 2. scroll reveal ----------
for f in ['dashboard-demo.html','initiative.html','roundtable.html','index.html','articles.html','about.html','media.html','identity.html','initiative-next.html','films.html','gap-map.html','season-1.html']:
    p = W(f); s = get(p); c = s.count('threshold:.12')
    if c: cache[p] = s.replace('threshold:.12', 'threshold:0'); log.append(f'  + {f}: threshold 0 x{c}')
tour = W('tour.html')
rep(tour, "'.vt-hl{outline:3px solid #F26D5A!important;",
    "'html.pai-motion .rv,html.pai-motion .rvs,html.pai-motion .rvs>*{opacity:1!important;transform:none!important}'+\n    '.vt-hl{outline:3px solid #F26D5A!important;", what='tour frame reveal override')

# ---------- 5. 17 years ----------
for p in sorted(root.glob('articles/*/*.html')):
    s = get(p); old = 'Growth, marketing and public-health strategist, 17 years turning complex systems into measurable results. Founder of HSREP.'
    if old in s: rep(p, old, 'Growth and marketing strategist for 17 years, in health care since 2021. Founder of HSREP.', what='byline')
for f in ('index.html', 'identity.html'):
    rep(W(f), '"description": "Growth, marketing and public-health strategist with 17 years turning complex systems into measurable results."',
        '"description": "Growth and marketing strategist with 17 years turning complex systems into measurable results, in health care since 2021 and trained in public health (MPH, CHES®)."', what='JSON-LD founder')
rep(W('llms.txt'), 'growth, marketing and public-health strategist (MBA, MCIM, MPH, CHES®), 17 years turning complex systems into measurable results.',
    'growth and marketing strategist (MBA, MCIM, MPH, CHES®), 17 years turning complex systems into measurable results, in health care since 2021.', what='llms founder')
for f in ('about.html', 'media.html'):
    rep(W(f), 'A growth, marketing and public-health strategist with 17 years turning', 'A growth and marketing strategist with 17 years turning', what='bio')

# ---------- 6. one pilot story ----------
rep(ini, 'It supports the routine; the calls and kits are done by people. Thirty invented patients:',
    'It supports the routine; the calls and kits are done by people. The demo shows more than a first pilot would use, such as message drafting; in the pilot nothing goes out without a named person approving it. Thirty invented patients:', what='demo card scope')
s = get(ini)
c = s.count('with a comparison clinic where one is available.')
if 'a comparison group chosen at random inside the clinic' not in s:
    if c != 2: sys.exit(f'initiative evaluation sentence: expected 2, found {c}')
    s = s.replace('with a comparison clinic where one is available.', 'with a comparison clinic where one is available. If the site&rsquo;s committee approves, a comparison group chosen at random inside the clinic gives a stronger reading; the worklist demo shows how that would be reported.', 1)
    s = s.replace('with a comparison clinic where one is available.', "with a comparison clinic where one is available. If the site's committee approves, a comparison group chosen at random inside the clinic gives a stronger reading; the worklist demo shows how that would be reported.", 1)
    cache[ini] = s; log.append('  + initiative.html: random comparison option x2')
dd = W('dashboard-demo.html')
rep(dd, '<dd>A browser tool built on coded lists: no names, record numbers or full dates. A list stays in the browser it was opened in.</dd></div>',
    '<dd>A browser tool built on coded lists: no names, record numbers or full dates. In this demo a list stays in the browser it was opened in; in a pilot the coded file stays on the clinic&rsquo;s own secure storage.</dd></div>\n<div><dt>In a first pilot</dt><dd>The weekly list, the scripts and the record of what got done. Your staff make the calls and mail the kits, nothing goes out without a named person approving it, and the evaluation compares your clinic with its own trend. The demo shows more than a first pilot would use.</dd></div>', what='demo glance scope')
rep(dd, '<h2 id="progh">Colorectal first. Nineteen more ready.</h2>', '<h2 id="progh">Colorectal first. Nineteen more set up in the demo.</h2>', what='nineteen heading')
rep(dd, '<p class="lede">Each programme has its own deadline, wording and measure. A host clinic starts with one.',
    '<p class="lede">Each programme has its own deadline, wording and measure. Only colorectal is specified for a first pilot, and a host clinic starts with one.', what='programmes lede')
rep(dd, '<li><b>Run it for 12 weeks</b><span>The clinic edition on your own accounts, a comparison group if your committee approves, and a report at the end.</span></li>',
    '<li><b>Months 1 to 3: the feasibility phase</b><span>The routine on your own accounts, with a comparison group if your committee approves. At month three you decide whether to continue to month twelve.</span></li>', what='12 weeks step')
rep(dd, '<p>No list is kept by HSREP. A list stays in the browser it is opened in. Messages',
    '<p>No list is kept by HSREP. In the demo a list stays in the browser it is opened in; in a pilot the coded nightly file stays on your own secure storage. Messages', what='data FAQ')
wl = W('worklist/index.html')
rep(wl, '"Run it for 12 weeks": "12 সপ্তাহ চালান"', '"Months 1 to 3: the feasibility phase": "মাস ১ থেকে ৩: সম্ভাব্যতা যাচাইয়ের পর্ব"', what='bn step title')
rep(wl, '"The clinic edition on your own accounts, with a comparison group if your committee approves, and a report at the end.": "আপনার নিজের অ্যাকাউন্টে ক্লিনিক সংস্করণ, আপনার কমিটি অনুমোদন করলে একটি তুলনার দলসহ, আর শেষে একটি প্রতিবেদন।"',
    '"The routine on your own accounts, with a comparison group if your committee approves. At month three you decide whether to continue to month twelve.": "আপনার নিজের অ্যাকাউন্টে এই রুটিন, আপনার কমিটি অনুমোদন করলে একটি তুলনার দলসহ। তৃতীয় মাসে আপনি ঠিক করবেন বারো মাস পর্যন্ত চালাবেন কি না।"', what='bn step text')
rep(wl, "['Run it for 12 weeks', 'The clinic edition on your own accounts, with a comparison group if your committee approves, and a report at the end.']",
    "['Months 1 to 3: the feasibility phase', 'The routine on your own accounts, with a comparison group if your committee approves. At month three you decide whether to continue to month twelve.']", what='step in pubNext')

# ---------- 7. status phrasings ----------
rep(ini, ' I would reach that clinic through the Michigan Primary Care Association and EMU faculty.', '', what='MPCA/EMU sentence')
rep(ini, '<p>Who this fits: a Medicaid plan&rsquo;s quality-incentive dollars, a Michigan health foundation, or an MDHHS subaward under CRCCP.</p>',
    '<p>Who this could fit, none approached yet: a Medicaid plan&rsquo;s quality-incentive dollars, a Michigan health foundation, or an MDHHS subaward under CRCCP.</p>', what='funder fit')
rep(ini, 'The proposed first site is a safety-net setting in Southeast Michigan, chosen because that is where',
    'No site is chosen yet. The pilot is designed for a safety-net setting in Southeast Michigan, because that is where', n=2, what='first site FAQ')
for f in (W('pilot-fit.html'), W('scripts/pilot_fit.py')):
    if not f.exists(): continue
    q = (lambda t: t.replace('’', '\\u2019')) if f.suffix == '.py' else (lambda t: t)
    rep(f, q('The first pilot is in Michigan, where its founder is based and the funding routes (a Medicaid plan’s quality-incentive dollars, a Michigan health foundation, an MDHHS subaward) sit.'),
        q('The first pilot is proposed for Michigan, where its founder is based and where the possible funding routes (a Medicaid plan’s quality-incentive dollars, a Michigan health foundation, an MDHHS subaward) sit. None has been approached yet.'), what='pilot-fit Michigan')
    rep(f, 'The evaluator measures the starting point before month one', 'An evaluator, once confirmed, would measure the starting point before month one', what='pilot-fit evaluator')
rep(W('initiative-next.html'), 'The first pilot already reports completion by language and payer group every week', 'The first pilot would report completion by language and payer group every week', what='already reports')

# ---------- 8. Book 30 minutes, two counts, one label ----------
rep(ini, '<div class="pai-cta"><a class="btn pai-primary" href="#host">Discuss hosting the pilot <span class="ar">&rarr;</span></a><a class="btn pai-secondary" href="dashboard-demo.html">See the Completion Worklist <span class="ar">&rarr;</span></a><a class="btn pai-secondary" href="#ask-band" data-ask-open>Ask me a question first <span class="ar">&rarr;</span></a></div>',
    f'<div class="pai-cta"><a class="btn pai-primary" href="{CAL}">Book 30 minutes <span class="ar">&rarr;</span></a><a class="btn pai-secondary" href="{MAIL2}">Send two counts <span class="ar">&rarr;</span></a><a class="btn pai-secondary" href="#ask-band" data-ask-open>Ask me a question first <span class="ar">&rarr;</span></a></div>\n'
    '<p class="pai-twocounts"><b>Not ready for a call?</b> Send two counts from the last 12 months: positive stool tests in patients aged 45 to 75, and how many of them had a colonoscopy within 180 days. I send back a one-page readout of your follow-up gap. Just the two numbers, no patient data.</p>', what='hero CTAs')
rep(ini, '<p class="pai-tourlink"><!-- voice-1108 --><a href="/tour.html">&#9654; The two-and-a-half-minute tour, narrated</a> <span>from the Gap Map to the routine and the demo, in an AI version of my voice</span></p>',
    '<p class="pai-tourlink"><!-- voice-1108 --><a href="/tour.html">&#9654; The two-and-a-half-minute tour</a> <span>the whole idea</span> &middot; <a href="/worklist/#tour-voice">&#9654; How the worklist runs, 4 min</a> <span>both narrated in an AI version of my voice</span></p>', what='hero tour links')
rep(ini, '.pai-tourlink span{color:var(--muted,#5B6474)}</style>',
    '.pai-tourlink span{color:var(--muted,#5B6474)}\n.pai-twocounts{margin:2px 0 8px;font-size:14.5px;line-height:1.55;color:var(--muted,#5B6474);max-width:62ch}.pai-twocounts b{color:var(--heading,#1C2E4A)}</style>', what='two-counts css')
band = '''<section class="pai-wlband" id="see-it" aria-labelledby="wlbandh"><style>
.pai-wlband{background:#F3F6FA;border-top:1px solid #DCE3EC;border-bottom:1px solid #DCE3EC}
.pai-wlband .wrap{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:28px;align-items:center;padding-block:30px}
.pai-wlband .wl-shot{display:block;border-radius:12px;overflow:hidden;border:1px solid #DCE3EC;box-shadow:0 10px 26px rgba(15,32,54,.12);background:#fff}
.pai-wlband .wl-shot img{display:block;width:100%;height:auto}
.pai-wlband .wl-k{display:block;font:500 12px/1.3 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:#B8402C;margin-bottom:8px}
.pai-wlband h2{font-family:Spectral,Georgia,serif;font-size:clamp(1.35rem,2.5vw,1.8rem);line-height:1.2;margin:0 0 10px;color:#1C2E4A}
.pai-wlband p{margin:0 0 16px;color:#33445C;line-height:1.6;max-width:60ch}
.pai-wlband .wb{display:flex;flex-wrap:wrap;gap:10px}
.pai-wlband small{display:block;margin-top:12px;color:#5B6474;font-size:12.5px;line-height:1.5;max-width:62ch}
@media(max-width:820px){.pai-wlband .wrap{grid-template-columns:minmax(0,1fr);gap:18px}.pai-wlband .wb .btn{flex:1 1 100%;justify-content:center}}
</style><div class="wrap">
<a class="wl-shot" href="/worklist/#case-P-1407"><img src="assets/worklist/wl-step-rank.webp" width="960" height="371" loading="lazy" decoding="async" alt="The Completion Worklist demo: the first rows of the ranked list, each with a patient code, days since the positive test, missed visits and the reason for its place."></a>
<div><span class="wl-k">The Completion Worklist &middot; a demo with invented patients</span>
<h2 id="wlbandh">See the weekly routine before you read about it.</h2>
<p>This is the list your outreach staff would work from each week: who is overdue, why that person is first, what help fits their barrier, and what got finished. Everyone in it is invented, and nothing leaves your browser.</p>
<div class="wb"><a class="btn pai-primary" href="/worklist/#tour-voice">&#9654; Hear how it works, 4 min</a><a class="btn pai-secondary" href="/worklist/#case-P-1407">Open the first case</a><a class="btn pai-secondary" href="dashboard-demo.html">What the demo covers</a></div>
<small>Narrated by an AI version of my voice. The demo shows more than a first pilot would use. In the pilot your staff make the calls and mail the kits, and nothing goes out without a named person approving it.</small>
</div></div></section>
'''
rep(ini, '</div></section>\n\n<section class="pai-askband" id="ask-band"', '</div></section>\n\n' + band + '\n<section class="pai-askband" id="ask-band"', what='worklist band')
for old, new in (('>Discuss hosting the pilot</a>', '>Book 30 minutes about hosting</a>'), ('>Talk about the evaluation</a>', '>Book 30 minutes about the evaluation</a>'),
                 ('>Talk about funding</a>', '>Book 30 minutes about funding</a>'), ('>Book 30 min <span class="ar">', '>Book 30 minutes <span class="ar">'),
                 ('Prefer a person? <a href="https://calendly.com/shafaat-alic/30min">30 minutes with me</a>', 'Prefer a person? <a href="https://calendly.com/shafaat-alic/30min">Book 30 minutes</a>')):
    rep(ini, old, new, what='label ' + new[1:30])
gm = W('gap-map.html')
rep(gm, '<a class="btn pai-secondary" href="#next">Get a free follow-up readout</a></div>',
    f'<a class="btn pai-secondary" href="#next">Get a free follow-up readout</a><a class="btn pai-secondary" href="{CAL}">Book 30 minutes</a></div>', what='gap-map hero book')
rep(gm, '<button type="button" data-gmtour="voice">hear it in the founder\'s voice</button>', '<button type="button" data-gmtour="voice">hear it in an AI version of the founder\'s voice</button>', what='gap-map AI label')
rep(tour, '<a class="vt-open" id="vtOpen" href="/gap-map.html" target="_blank" rel="noopener">Open this page in a new tab &#8599;</a>',
    f'<a class="vt-open" id="vtOpen" href="/gap-map.html" target="_blank" rel="noopener">Open this page in a new tab &#8599;</a>\n<a class="vt-open vt-book" href="{CAL}" data-ev="book_cap">Run a health center? Book 30 minutes &#8599;</a>', what='tour caption book')
rep(tour, '<p>Or keep exploring on your own. The demo stays open, with every screen working and nothing sent.</p>',
    f'<p>Not ready for a call? <a href="{MAIL2}" data-ev="twocounts" style="color:#fff">Send two counts</a>: positive stool tests, and how many had a colonoscopy within 180 days. You get a one-page readout back, and no patient data is needed.</p>', what='tour end two counts')
n = 0
for p in sorted(root.rglob('*.html')):
    if any(x in p.parts for x in ('build', '_archive', 'node_modules')): continue
    s = get(p); c = s.count('>Book a 30-min call</a>')
    if c: cache[p] = s.replace('>Book a 30-min call</a>', '>Book 30 minutes</a>'); n += c
log.append(f'  + footers: "Book a 30-min call" -> "Book 30 minutes" x{n}')

for p, s in cache.items():
    if s != p.read_text(encoding='utf-8'): p.write_text(s, encoding='utf-8')
print('\n'.join(log))
print('done: review-1110')
