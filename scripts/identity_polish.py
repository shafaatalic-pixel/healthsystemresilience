#!/usr/bin/env python3
"""
Give the crest page the dark stage it was always designed for, and a close.

    python3 scripts/identity_polish.py .

The identity band was written for a dark background and lost it when the section
moved off the home page onto its own. The evidence is in the stylesheet, which
groups it with the other dark surfaces:

    .hero,.dark,.mvband,.navy,.idstory,.toast,footer{--coral:#F26D5A}
    .hero,.dark,.mvband,.idstory,.toast,footer{--muted:#AEB9C7}

and styles its chapter rules as rgba(255,255,255,.12) with #cdd9e6 body text.
On its own page it inherited .band{background:var(--panel)}, so a component drawn
for navy has been rendering pale-on-pale. This restores the stage, enlarges the
crest, lights it from behind, and adds the section the page was missing: what the
mark actually commits the platform to, with the colours and letterforms that
carry it.

Idempotent. No change to the beat player's markup or JavaScript.
"""
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
P = os.path.join(ROOT, "identity.html")

CSS = '''<style id="hs-crest">
/* ---- the stage. #identity, not .idstory: section.band is 0,1,1
   and would otherwise keep painting this pale -------------------------------------------------------- */
#identity{background:
  radial-gradient(120% 80% at 50% -10%,rgba(242,109,90,.13),transparent 62%),
  linear-gradient(180deg,#0E1E33 0%,#16293F 48%,#0D1B2E 100%);
  color:#D7E2EF;padding-top:clamp(3rem,6vw,5.5rem)}
#identity .eyebrow{color:var(--coral)}
#identity h1.sec,#identity h2.sec{color:#fff}
#identity .lead{color:#B7C4D4;max-width:62ch}
#identity .shead{margin-bottom:clamp(30px,4vw,52px)}

/* a slow drift behind the crest, so the stage is never quite still */
#identity::after{content:"";position:absolute;left:50%;top:34%;width:min(780px,90vw);
  aspect-ratio:1;transform:translate(-50%,-50%);pointer-events:none;z-index:0;
  background:radial-gradient(closest-side,rgba(120,170,255,.10),transparent 70%);
  animation:idglow 14s ease-in-out infinite alternate}
@keyframes idglow{from{opacity:.55;transform:translate(-50%,-50%) scale(.92)}
                  to{opacity:1;transform:translate(-52%,-48%) scale(1.06)}}
#identity .wrap{position:relative;z-index:1}

/* ---- the crest, unboxed and lit --------------------------------------- */
#identity .crestwrap{background:transparent;border:0;box-shadow:none;padding:0;
  display:flex;flex-direction:column;justify-content:center}
/* The mark keeps its own navy, so on a navy stage it needs something to sit
   on. A light disc rather than an inverted crest: this page exists to show the
   real mark, not a version of it. */
#identity .crestwrap::before{inset:auto;left:50%;top:calc(50% - 26px);
  transform:translate(-50%,-50%);width:min(720px,124%);aspect-ratio:1;
  border-radius:50%;z-index:0;
  background:radial-gradient(closest-side,#FFFFFF 0%,#FFFFFF 34%,#EFF4FA 52%,
    rgba(228,237,247,.42) 68%,rgba(228,237,247,.12) 78%,rgba(228,237,247,0) 88%)}
#identity .creststage{position:relative;z-index:1}
#identity .creststage{max-width:min(392px,70%);
  filter:drop-shadow(0 26px 60px rgba(0,0,0,.45))}
#identity .crestcap{color:#8FA1B8;margin-top:22px}
#identity .crestcap b{color:#fff}

/* the highlighted element lifts out of the stage rather than just brightening */
#identity .creststage .cp{transition:opacity .55s var(--ease),filter .45s var(--ease),
  transform .55s var(--ease)}
.js-anim #identity .creststage .cp.hi,#identity .creststage .cp.hi{
  filter:drop-shadow(0 0 18px rgba(255,255,255,.28))}

/* ---- the chapters ------------------------------------------------------ */
#identity .beatbox .lbl{margin-bottom:20px}
#identity .beat .bt{color:#D3DFEC;font-size:1.02rem;line-height:1.68}
#identity .beat .bt b{color:#fff}
#identity .beat.big .bt,#identity .beats .beat .bt{max-width:54ch}
#identity .musicbtn{color:#8FA1B8;border-color:rgba(255,255,255,.22)}
#identity .musicbtn:hover{border-color:var(--coral);color:var(--coral)}
#identity .dots button{background:rgba(255,255,255,.22)}
#identity .dots button:hover{background:rgba(255,255,255,.45)}
#identity .dots button[aria-current="true"],#identity .dots button.on{background:var(--coral)}

/* ---- the close: what the mark commits us to ---------------------------- */
.idsys{background:var(--paper)}
.pgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(16px,2.2vw,26px);
  margin:6px 0 clamp(38px,5vw,62px)}
.pcard{position:relative;background:var(--white);border:1px solid var(--hairline);
  border-radius:var(--r-lg);padding:26px 24px 24px;box-shadow:var(--sh-xs);
  transition:transform .35s var(--ease),box-shadow .35s var(--ease)}
.pcard:hover{transform:translateY(-3px);box-shadow:var(--sh-md)}
.pcard .pn{font-family:var(--font-mono);font-size:11px;letter-spacing:.14em;
  color:var(--coral)}
.pcard h3{font-family:var(--font-display);font-size:1.28rem;line-height:1.25;
  margin:12px 0 10px;color:var(--navy)}
.pcard p{font-size:.95rem;line-height:1.62;color:var(--ink);margin:0}
.pcard::after{content:"";position:absolute;left:24px;right:24px;bottom:0;height:2px;
  background:var(--coral);transform:scaleX(0);transform-origin:0 50%;
  transition:transform .4s var(--ease)}
.pcard:hover::after{transform:scaleX(1)}

.specs{display:grid;grid-template-columns:1.15fr 1fr;gap:clamp(22px,3vw,44px);
  align-items:start}
.slbl{font-family:var(--font-mono);font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);margin-bottom:16px}
.swatches{display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,1fr));gap:12px}
.sw span{display:block;height:56px;border-radius:var(--r-md);background:var(--c);
  border:1px solid rgba(28,46,74,.08)}
.sw b{display:block;font-size:.82rem;margin-top:9px;color:var(--navy);font-weight:600}
.sw i{display:block;font-family:var(--font-mono);font-size:10.5px;color:var(--muted);
  font-style:normal;letter-spacing:.04em}
.tspec > div{padding:14px 0;border-top:1px solid var(--hairline)}
.tspec > div:first-child{border-top:0;padding-top:0}
.tspec p{margin:0 0 4px;color:var(--navy);line-height:1.1}
.tspec .td{font-family:var(--font-display);font-size:2rem}
.tspec .tb{font-family:var(--font-body);font-size:1.7rem;font-weight:600}
.tspec .tm{font-family:var(--font-mono);font-size:1.35rem;letter-spacing:-.01em}
.tspec small{font-size:.86rem;color:var(--muted)}

@media(max-width:860px){
  .pgrid{grid-template-columns:1fr}
  .specs{grid-template-columns:1fr}
  #identity .creststage{max-width:min(340px,72%)}
}
@media(prefers-reduced-motion:reduce){
  #identity::after{animation:none}
  .pcard,.pcard::after{transition:none}
}
</style></head>'''

SECTION = '''
<section class="band idsys" id="the-system"><div class="wrap">
<div class="shead rv"><div class="eyebrow">The system</div>
<div class="top"><h2 class="sec">What the mark commits us to.</h2>
<div class="lead">Three principles, and the short list of colours and letterforms that
carry them across everything HSREP publishes.</div></div></div>

<div class="pgrid rv">
<div class="pcard"><span class="pn">01</span><h3>Human in purpose</h3>
<p>The coral point sits above the structure because the person is the reason the
structure exists. Every figure on this site is checked against whether it describes
a person or only a request.</p></div>
<div class="pcard"><span class="pn">02</span><h3>Systemic in method</h3>
<p>The arch is drawn as infrastructure, not as a shield. Arguments are sourced,
methods are published, and a number that falls is published beside the one that
rose.</p></div>
<div class="pcard"><span class="pn">03</span><h3>Protective in outcome</h3>
<p>The foundation rises into the central figure because protection and the person
are one form. Work that never reaches a clinic is a hobby; the initiative exists
to close that gap.</p></div>
</div>

<div class="specs rv">
<div class="spec"><div class="slbl">Colour</div>
<div class="swatches">
<div class="sw" style="--c:#0F2036"><span></span><b>Navy deep</b><i>#0F2036</i></div>
<div class="sw" style="--c:#1C2E4A"><span></span><b>Navy</b><i>#1C2E4A</i></div>
<div class="sw" style="--c:#F26D5A"><span></span><b>Coral</b><i>#F26D5A</i></div>
<div class="sw" style="--c:#267A69"><span></span><b>Green</b><i>#267A69</i></div>
<div class="sw" style="--c:#F2F5F8"><span></span><b>Panel</b><i>#F2F5F8</i></div>
</div>
<p style="margin:18px 0 0;font-size:.92rem;line-height:1.6;color:var(--muted);max-width:52ch">
One warm colour against one institutional one. Coral is never decoration: it marks
the person, and it marks every action a reader can take.</p>
</div>
<div class="spec"><div class="slbl">Letterforms</div>
<div class="tspec">
<div><p class="td">Spectral</p><small>Display &mdash; arguments, headings, the things
meant to be read slowly.</small></div>
<div><p class="tb">Inter</p><small>Body &mdash; everything read at length.</small></div>
<div><p class="tm">IBM Plex Mono</p><small>Labels &mdash; figures, sources, windows,
and anything a machine produced.</small></div>
</div>
</div>
</div>

<p style="margin:clamp(30px,4vw,46px) 0 0">
<a class="btn ghost" href="media.html">Media &amp; brand kit <span class="ar">&rarr;</span></a></p>
</div></section>
'''


def main():
    s = open(P, encoding="utf-8").read()
    before = s

    if 'id="hs-crest"' not in s:
        s = s.replace("</head>", CSS, 1)
        print("  stage styles added")
    else:
        print("  already current: styles")

    if 'id="the-system"' not in s:
        i = s.index("</main>")
        s = s[:i] + SECTION + s[i:]
        print("  the system section added")
    else:
        print("  already current: the system")

    # the section bar on this page, if it has one, should carry the new anchor
    if 'class="mth-secnav"' in s and 'href="#the-system"' not in s:
        s = re.sub(r'(<span class="sn-lab">On this page</span>)',
                   r'\1<a href="#the-system">The system</a>', s, count=1)

    if s.count("<h1") != 1:
        raise SystemExit("ABORT: expected one <h1>, found %d" % s.count("<h1"))
    for tag in ('<div class="beats"', 'id="dots"', 'class="creststage"'):
        if s.count(tag) != 1:
            raise SystemExit("ABORT: the player's %s appears %d times"
                             % (tag, s.count(tag)))

    if s != before:
        open(P, "w", encoding="utf-8").write(s)
        print("  wrote: identity.html")
    else:
        print("  no change")


main()
print("done")
