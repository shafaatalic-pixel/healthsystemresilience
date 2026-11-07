#!/usr/bin/env python3
"""journey-1107: tie the site into one pitch path.

Run from the website/ folder:  python3 scripts/journey1107/apply.py
  worklist/index.html   deep links #prog-<programme>, #draft-<code>, #tour-<id>-<n>; Present bar script
  initiative.html       routine panels: demo examples (codes, not names), why each step matters,
                        a preview and a link into the demo; Gap Map callout under 01 The gap
  dashboard-demo.html   each programme opens the demo on that programme
  gap-map.html          follow-up CTA opens the sample case; gapmap-1.js version bump
  assets/gapmap-1.js    a center below target shows "Closing the gap" with the demo and the readout
  assets/search-index.json  the routine examples, as on the page
  assets/present.js     five-stop Present path (?present on any page); loaded on four pages
Needs assets/worklist/wl-step-{find,rank,act,close}.webp. Idempotent (marker journey-1107).
"""
import sys, json, pathlib, shutil
MARK = 'journey-1107'
here = pathlib.Path(__file__).resolve().parent
root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent
WL_JS = (here / 'wl_block.js').read_text(encoding='utf-8')
PRESENT_TAG = '<script src="/assets/present.js?v=20261107a" defer></script>'

def sub_once(s, old, new, what):
    n = s.count(old)
    if n != 1: sys.exit(f'{what}: expected 1 match, found {n}')
    return s.replace(old, new)

def add_present(s, what):
    if PRESENT_TAG in s: return s
    i = s.rindex('</body>'); return s[:i] + PRESENT_TAG + '\n' + s[i:]

# assets/present.js
shutil.copyfile(here / 'present.js', root / 'assets' / 'present.js'); print('present.js: copied')

# worklist
p = root / 'worklist' / 'index.html'; s = p.read_text(encoding='utf-8')
if MARK in s: print('worklist: already applied')
else:
    s = sub_once(s, '\n// Deep links from the website: #tour-overview', WL_JS + '\n// Deep links from the website: #tour-overview', 'worklist js anchor')
    s = add_present(s, 'worklist'); p.write_text(s, encoding='utf-8'); print('worklist: patched')

# initiative.html
PANELS = {
 'find': dict(hidden=True,
  what='Everyone overdue for a stool test, and every positive test still waiting for a colonoscopy, pulled from the nightly file.',
  who='HSREP (me), from your nightly file.',
  why='Reminder and recall only reach people who are on the list. Provider reminder and recall raised colorectal screening by a median 15.3 points in published studies.',
  ex='This week: 14 people overdue for a stool test and 9 positive tests still waiting for a colonoscopy, 2 of them already past the 180-day window. Invented panel of 30.',
  href='/worklist/#followup', go='See the list in the demo', w=960, h=400,
  alt='The demo follow-up list: 2 past the 180-day window, 8 open, 1 scheduled, 2 done within 180 days.'),
 'rank': dict(hidden=False,
  what='Three transparent rules, shown beside every case: days overdue, days since a positive test, prior no-shows. No predictive model in the first pilot.',
  who='The rules, in the worklist. Anyone on staff can see why a case is where it is.',
  why='Staff time is short. The rules put the people closest to losing the 180-day window first, which is the step COF-E counts from 2027.',
  ex='P-1407 &middot; 210 days since a positive test &middot; 0 missed visits &rarr; first. P-1000 &middot; 194 days &middot; 2 missed visits &rarr; second. Codes only, never names.',
  href='/worklist/#case-P-1407', go='Open P-1407 in the demo', w=960, h=371,
  alt='The first four rows of the ranked list: P-1407 at 210 days, then P-1000 at 194 days with 2 missed visits.'),
 'act': dict(hidden=True,
  what='Match the action to the barrier: a mailed kit, a reminder in the patient&rsquo;s language, help booking, or a community health worker.',
  who='Your outreach staff, with scripts I write and test with them.',
  why='Patient navigation raised screening by a median 13.6 points, and removing structural barriers such as mailing the kit by 16.1. The routine matches the help to the barrier instead of sending everyone the same reminder.',
  ex='P-1407 &middot; Arabic &middot; language barrier &rarr; book an interpreter. The message is drafted in Arabic from signed-off wording, and a named person checks and approves it before anything is sent.',
  href='/worklist/#draft-P-1407', go='See the message and the checks', w=760, h=580,
  alt='Case P-1407: next step, check and approve the message; help to offer, book an interpreter.'),
 'close': dict(hidden=True,
  what='Record the completed test or colonoscopy and the days it took, then check whether follow-up differs between language groups.',
  who='Your staff record it. I review the week with your quality-improvement lead.',
  why='A step counts only when it shows in the record. Counting it the way COF-E will, and by language, shows whether the routine is working and for whom.',
  ex='Colonoscopy within 180 days, by language, counting only people whose window has closed: English 1 of 2 &middot; Arabic 0 of 1 &middot; Spanish 0 of 1.',
  href='/worklist/#equity', go='See the fairness check', w=960, h=215,
  alt='Follow-up within 180 days by language: English 1 of 2, Arabic 0 of 1, Spanish 0 of 1.'),
}
def panel(k, d):
    return (f'<div role="tabpanel" id="pan-{k}" aria-labelledby="tab-{k}"' + (' hidden' if d['hidden'] else '') + '>'
      f'<div class="ex"><span class="mono k">What happens</span><p>{d["what"]}</p><p class="who"><span class="mono k">Who</span>{d["who"]}</p>'
      f'<p class="why"><span class="mono k">Why it makes a difference</span>{d["why"]}</p></div>'
      f'<div class="sample"><span class="mono k">In the demo &middot; invented people</span><p>{d["ex"]}</p>'
      f'<a class="pai-shot" href="{d["href"]}"><img src="assets/worklist/wl-step-{k}.webp" width="{d["w"]}" height="{d["h"]}" loading="lazy" decoding="async" alt="{d["alt"]}"><span class="go">{d["go"]} &rarr;</span></a></div></div>')
INIT_CSS = ('<style id="journey-1107">'
 '.pai-loop .why{margin-top:14px}.pai-loop .why .k{display:block;margin-bottom:2px}'
 '.pai-shot{display:block;margin-top:12px;border:1px solid var(--pai-line);border-radius:8px;overflow:hidden;background:#fff;text-decoration:none;transition:border-color .2s}'
 '.pai-shot:hover,.pai-shot:focus-visible{border-color:var(--coral)}'
 '.pai-shot img{display:block;width:100%;height:auto;max-height:240px;object-fit:cover;object-position:top left}'
 '.pai-shot .go{display:block;padding:9px 12px;font-weight:600;font-size:14.5px;color:var(--pai-coral-text)}'
 '.pai-gapmap{display:flex;flex-direction:column;gap:4px;margin:18px 0 0;padding:16px 20px;border:1px solid var(--pai-line);border-left:3px solid var(--coral);border-radius:0 10px 10px 0;background:#fff;text-decoration:none;color:inherit}'
 '.pai-gapmap:hover,.pai-gapmap:focus-visible{border-color:var(--coral)}'
 '.pai-gapmap .mono{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--pai-coral-text)}'
 '.pai-gapmap b{font-family:var(--font-display);font-size:1.15rem;line-height:1.35;color:var(--heading)}'
 '.pai-gapmap span:last-child{font-size:14.5px;color:var(--ink)}'
 '</style>')
GAPMAP_CALLOUT = ('<a class="pai-gapmap" href="/gap-map.html"><span class="mono">The Prevention Gap Map &middot; Michigan, 2025</span>'
 '<b>34 of the 35 Michigan health centers with a published rate are below the 72.8% target.</b>'
 '<span>Find a center, see its distance from the target and what closing the gap would take &rarr;</span></a>\n')
CAVEAT = ('<p class="pai-small">The effects quoted under each step are median results from the Community Preventive Services Task Force, measured in other settings. '
 'They are not the pilot&rsquo;s expected results and are not added together. Details in <a href="#evidence">Evidence and questions</a>.</p>\n')
p = root / 'initiative.html'; s = p.read_text(encoding='utf-8')
if MARK in s: print('initiative: already applied')
else:
    a = s.index('<div role="tabpanel" id="pan-find"'); b = s.index('\n</div>\n<div class="pai-pillars">', a)
    s = s[:a] + '\n'.join(panel(k, PANELS[k]) for k in ['find', 'rank', 'act', 'close']) + s[b:]
    s = sub_once(s, '<div class="pai-pillars">', CAVEAT + '<div class="pai-pillars">', 'initiative pillars')
    s = sub_once(s, '<div class="pai-why"><b>Why follow-through, not a new method</b>', GAPMAP_CALLOUT + '<div class="pai-why"><b>Why follow-through, not a new method</b>', 'initiative gap callout')
    s = sub_once(s, '</head>', INIT_CSS + '\n</head>', 'initiative head')
    s = add_present(s, 'initiative'); p.write_text(s, encoding='utf-8'); print('initiative: patched')

# search index: the routine examples as on the page
p = root / 'assets' / 'search-index.json'; s = p.read_text(encoding='utf-8')
REPL = [
 ('Example from the synthetic worklist', 'In the demo · invented people'),
 ('This week: 12 overdue for a stool test, 4 positive tests without a finished colonoscopy. Synthetic panel of 30.', PANELS['find']['ex'].replace('&middot;', '·').replace('&rarr;', '→')),
 ('Samuel T. · 194 days since a positive test · 1 prior no-show → first in the follow-up queue.', 'P-1407 · 210 days since a positive test · 0 missed visits → first. P-1000 · 194 days · 2 missed visits → second. Codes only, never names.'),
 ('Samuel T. · transport barrier → navigation, plus a ride to the colonoscopy.', 'P-1407 · Arabic · language barrier → book an interpreter. The message is drafted in Arabic from signed-off wording, and a named person checks and approves it before anything is sent.'),
 ('Follow-up by language: English 3 of 4 · Spanish 1 of 3 · Other 1 of 2.', 'Colonoscopy within 180 days, by language, counting only people whose window has closed: English 1 of 2 · Arabic 0 of 1 · Spanish 0 of 1.'),
 ('shown beside every name', 'shown beside every case'),
]
if 'P-1407 · Arabic' in s or 'P-1407 \\u00b7 Arabic' in s: print('search index: already applied')
else:
    n = 0
    for old, new in REPL:
        for o, nw in ((old, new), (json.dumps(old)[1:-1], json.dumps(new)[1:-1])):
            if o in s: s = s.replace(o, nw); n += 1; break
    p.write_text(s, encoding='utf-8'); print(f'search index: {n} of {len(REPL)} replaced')

# dashboard-demo.html: programmes open the demo
p = root / 'dashboard-demo.html'; s = p.read_text(encoding='utf-8')
LI = [
 ('<li>Colorectal: positive stool test to colonoscopy</li>', '<li><a href="/worklist/#prog-us-crc">Colorectal: positive stool test to colonoscopy</a></li>'),
 ('<li>Cervical: abnormal Pap or HPV to colposcopy</li>', '<li><a href="/worklist/#prog-us-cerv">Cervical: abnormal Pap or HPV to colposcopy</a></li>'),
 ('<li>Breast: abnormal mammogram to diagnostic follow-up</li>', '<li><a href="/worklist/#prog-us-breast">Breast: abnormal mammogram to diagnostic follow-up</a></li>'),
 ('<li>Blood pressure: high reading to recheck</li>', '<li><a href="/worklist/#prog-us-bp">Blood pressure: high reading to recheck</a></li>'),
 ('<li>Hepatitis C: reactive antibody to confirmatory test</li>', '<li><a href="/worklist/#prog-us-hcv">Hepatitis C: reactive antibody to confirmatory test</a></li>'),
 ('<li>Diabetes: A1c test, yearly eye exam, yearly kidney test</li>', '<li>Diabetes: <a href="/worklist/#prog-us-a1c">A1c test</a>, <a href="/worklist/#prog-us-dm-eye">yearly eye exam</a>, <a href="/worklist/#prog-us-dm-kidney">yearly kidney test</a></li>'),
 ('<li>Lung: yearly low-dose CT</li>', '<li><a href="/worklist/#prog-us-lung">Lung: yearly low-dose CT</a></li>'),
 ('<li>Prediabetes: referral to a prevention program</li>', '<li><a href="/worklist/#prog-us-dpp">Prediabetes: referral to a prevention program</a></li>'),
 ('<li>Childhood vaccines: next dose due</li>', '<li><a href="/worklist/#prog-us-vax">Childhood vaccines: next dose due</a></li>'),
 ('<li>Cervical: VIA-positive to colposcopy</li>', '<li><a href="/worklist/#prog-bd-cerv">Cervical: VIA-positive to colposcopy</a></li>'),
 ('<li>Hypertension: raised reading to confirming visit</li>', '<li><a href="/worklist/#prog-bd-htn">Hypertension: raised reading to confirming visit</a></li>'),
 ('<li>Hypertension: 90-day check after starting treatment</li>', '<li><a href="/worklist/#prog-bd-htn-control">Hypertension: 90-day check after starting treatment</a></li>'),
 ('<li>Diabetes: raised glucose to confirming test</li>', '<li><a href="/worklist/#prog-bd-dm">Diabetes: raised glucose to confirming test</a></li>'),
 ('<li>Diabetes: HbA1c 90 days after starting treatment</li>', '<li><a href="/worklist/#prog-bd-dm-a1c">Diabetes: HbA1c 90 days after starting treatment</a></li>'),
 ('<li>Diabetes: yearly eye check, yearly kidney check</li>', '<li>Diabetes: <a href="/worklist/#prog-bd-dm-eye">yearly eye check</a>, <a href="/worklist/#prog-bd-dm-kidney">yearly kidney check</a></li>'),
 ('<li>Kidney: abnormal result to confirming test</li>', '<li><a href="/worklist/#prog-bd-ckd">Kidney: abnormal result to confirming test</a></li>'),
 ('<li>Factory anaemia: repeat haemoglobin after iron</li>', '<li><a href="/worklist/#prog-bd-anaemia">Factory anaemia: repeat haemoglobin after iron</a></li>'),
]
if MARK in s: print('dashboard: already applied')
else:
    for old, new in LI: s = sub_once(s, old, new, 'dashboard ' + old[4:30])
    s = sub_once(s, '<p class="lede">Each programme has its own deadline, wording and measure. A host clinic starts with one.</p>',
        '<p class="lede">Each programme has its own deadline, wording and measure. A host clinic starts with one. Each name below opens that programme in the demo; the Bangladesh ones open in Bangla.</p>', 'dashboard programmes lede')
    s = sub_once(s, '.cw-sub{font-size:17px;margin:22px 0 0}', '.cw-sub{font-size:17px;margin:22px 0 0}\n/* journey-1107 */\n.cw-two li a{color:inherit;text-decoration:underline;text-decoration-color:rgba(184,64,44,.45);text-underline-offset:3px}\n.cw-two li a:hover{color:#B8402C}', 'dashboard css')
    s = add_present(s, 'dashboard'); p.write_text(s, encoding='utf-8'); print('dashboard: patched')

# gap map
p = root / 'assets' / 'gapmap-1.js'; s = p.read_text(encoding='utf-8')
FIX = ("/* journey-1107 */if(c.pub&&c.need>0)h+='<div class=\"gm-fix\"><span class=\"mono\">Closing the gap</span><p>Screening is step one. The Completion Worklist works the weekly list of people who are due, and of positive tests still waiting for a colonoscopy, most urgent first.</p>"
       "<a href=\"/worklist/#case-P-1407\">See one case in the demo &rarr;</a><a href=\"#next\">Ask for a free follow-up readout &rarr;</a></div>';\n ")
if MARK in s: print('gapmap js: already applied')
else:
    s = sub_once(s, " h+='<div class=\"gm-btns\">", " " + FIX + "h+='<div class=\"gm-btns\">", 'gapmap select')
    p.write_text(s, encoding='utf-8'); print('gapmap js: patched')
p = root / 'gap-map.html'; s = p.read_text(encoding='utf-8')
GM_CSS = ('<style id="journey-1107">.gm-fix{margin:14px 0 0;padding:12px 14px;border-left:3px solid var(--coral);background:var(--panel,#F2F5F8);border-radius:0 8px 8px 0;display:flex;flex-direction:column;gap:6px}'
 '.gm-fix .mono{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--pai-coral-text)}.gm-fix p{margin:0;font-size:14px;line-height:1.5}'
 '.gm-fix a{font-weight:600;font-size:14px;color:var(--pai-coral-text);text-decoration:none}.gm-fix a:hover{text-decoration:underline}</style>')
if MARK in s: print('gap-map: already applied')
else:
    s = sub_once(s, '<a href="/dashboard-demo.html"><b>Close the follow-up step &rarr;</b>', '<a href="/worklist/#case-P-1407"><b>Close the follow-up step &rarr;</b>', 'gap-map next cta')
    s = sub_once(s, '/assets/gapmap-1.js?v=20261106b', '/assets/gapmap-1.js?v=20261107j', 'gap-map js version')
    s = sub_once(s, '</head>', GM_CSS + '\n</head>', 'gap-map head')
    s = add_present(s, 'gap-map'); p.write_text(s, encoding='utf-8'); print('gap-map: patched')
