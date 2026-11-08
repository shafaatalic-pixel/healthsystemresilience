#!/usr/bin/env python3
"""voice-1108: two narrated tours in an AI version of the founder's voice (ElevenLabs, 8 Nov 2026).

Run from the website/ folder:  python3 scripts/voice1108/apply.py
  tour.html                     new page: 10 stops across the Gap Map, the initiative and the worklist demo
  assets/tour-vo/               10 clips + recorded.json (captions as recorded)
  assets/worklist-vo/           12 clips + recorded.json
  worklist/index.html           a seventh tour, "Hear how it works" (#tour-voice), featured next to the overview
  dashboard-demo.html           the narrated tour card and a hero link
  initiative.html               hero link to /tour.html
  gap-map.html                  "06 The next step" links to /tour.html
Idempotent: a file that already carries the marker is left alone. The clips live in assets/*-vo/ (from HSR/vo-staging/);
if scripts/voice1108/vo/ exists they are copied from there first.
"""
import sys, pathlib, shutil
MARK = 'voice-1108'
here = pathlib.Path(__file__).resolve().parent
root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here.parent.parent

def sub_once(s, old, new, what):
    n = s.count(old)
    if n != 1: sys.exit(f'{what}: expected 1 match, found {n}')
    return s.replace(old, new)

for name, n in (('tour', 10), ('worklist', 12)):
    d = root / 'assets' / f'{name}-vo'; d.mkdir(parents=True, exist_ok=True)
    for k in range(1, n + 1):
        src, dst = here / 'vo' / name / f'step-{k:02d}.mp3', d / f'step-{k:02d}.mp3'
        if src.exists(): shutil.copyfile(src, dst)
        elif not dst.exists(): sys.exit(f'missing clip {dst}')
    shutil.copyfile(here / f'{name}-recorded.json', d / 'recorded.json')
print('clips: in place')

t = (here / 'tour.html').read_text(encoding='utf-8')
(root / 'tour.html').write_text(t.replace('<meta name="robots"', f'<!-- {MARK} -->\n<meta name="robots"', 1), encoding='utf-8'); print('tour.html: written')

p = root / 'worklist' / 'index.html'; s = p.read_text(encoding='utf-8')
if MARK in s: print('worklist: already applied')
else:
    js = (here / 'wl_voice.js').read_text(encoding='utf-8')
    s = sub_once(s, '\n// Deep links from the website: #tour-overview', js + '\n// Deep links from the website: #tour-overview', 'worklist js anchor')
    p.write_text(s, encoding='utf-8'); print('worklist: patched')

p = root / 'dashboard-demo.html'; s = p.read_text(encoding='utf-8')
if MARK in s: print('dashboard: already applied')
else:
    s = sub_once(s, '<a class="btn pai-secondary" href="https://calendly.com/shafaat-alic/30min">Book 30 minutes</a></div>',
        '<a class="btn pai-secondary" href="https://calendly.com/shafaat-alic/30min">Book 30 minutes</a></div>\n<p class="cw-voicelink"><a href="/worklist/#tour-voice">&#9654; Hear how it works, narrated in about four minutes</a> · <a href="/tour.html">or the whole idea in two and a half</a></p>', 'dashboard hero')
    s = sub_once(s, '</div>\n<h3 class="cw-sub">Or explore by task</h3>',
        '</div>\n<a class="cw-tour cw-voice" href="/worklist/#tour-voice"><span class="cw-role">Narrated · AI version of the founder&rsquo;s voice</span><b>Hear how it works</b><span>How the list works, what it changes from the usual approach, and where HSREP comes in. The demo moves as you listen.</span><span class="cw-meta">Colorectal · English · 12 steps · about 4 minutes</span><span class="go">Listen &rarr;</span></a>\n<h3 class="cw-sub">Or explore by task</h3>', 'dashboard voice card')
    anchor = '.cw-sub{font-size:17px;margin:22px 0 0}'
    s = sub_once(s, anchor, anchor + '\n/* voice-1108 */\n.cw-voice{margin-top:12px;border-left:4px solid #1C2E4A}\n.cw-voicelink{margin:-4px 0 14px;font-size:15px}\n.cw-voicelink a{color:#B8402C;text-decoration:none;border-bottom:1px solid rgba(184,64,44,.4)}\n.cw-voicelink a:hover{border-bottom-color:#B8402C}', 'dashboard css')
    p.write_text(s, encoding='utf-8'); print('dashboard: patched')

p = root / 'initiative.html'; s = p.read_text(encoding='utf-8')
if MARK in s: print('initiative: already applied')
else:
    s = sub_once(s, '<a class="btn pai-secondary" href="#ask-band" data-ask-open>Ask me a question first <span class="ar">&rarr;</span></a></div>',
        '<a class="btn pai-secondary" href="#ask-band" data-ask-open>Ask me a question first <span class="ar">&rarr;</span></a></div>\n<p class="pai-tourlink"><!-- voice-1108 --><a href="/tour.html">&#9654; The two-and-a-half-minute tour, narrated</a> <span>from the Gap Map to the routine and the demo, in an AI version of my voice</span></p>', 'initiative hero')
    s = sub_once(s, '.srcnote.corr{border-top:1px solid rgba(242,109,90,.45)}</style>',
        '.srcnote.corr{border-top:1px solid rgba(242,109,90,.45)}\n.pai-tourlink{margin:2px 0 6px;font-size:15px}.pai-tourlink a{font-weight:600;color:var(--coral-text,#B8402C);text-decoration:none;border-bottom:1px solid rgba(184,64,44,.4)}.pai-tourlink a:hover{border-bottom-color:currentColor}.pai-tourlink span{color:var(--muted,#5B6474)}</style>', 'initiative css')
    p.write_text(s, encoding='utf-8'); print('initiative: patched')

p = root / 'gap-map.html'; s = p.read_text(encoding='utf-8')
if MARK in s: print('gap-map: already applied')
else:
    s = sub_once(s, 'Get one page back. No patient data.</a>\n</div>',
        'Get one page back. No patient data.</a>\n<a href="/tour.html"><!-- voice-1108 --><b>Hear the whole idea in 2&frac12; minutes &rarr;</b>A narrated tour from this map to the follow-up routine and the demo, in an AI version of the founder&rsquo;s voice.</a>\n</div>', 'gap-map next cta')
    p.write_text(s, encoding='utf-8'); print('gap-map: patched')
