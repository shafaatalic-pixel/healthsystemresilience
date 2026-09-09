#!/usr/bin/env python3
"""Second pass on the home page: the roundtable card, and depth in the hero.

Three things this fixes.

1. `<div class="rtcount">3 questions open</div>` was written into the roundtable
   card with no CSS rule anywhere. It rendered at browser-default 16px with
   default block margins and broke the card's alignment. It is now a small
   coral chip in the card's own type scale.

2. The roundtable card sat in plain white while the card directly below it in
   Participate — same page, same ask — had the coral top rule and warm ground.
   The card carrying the actual question now gets the same treatment.

3. The hero's motion was all in the first two seconds and then the field went
   flat. It now has an atmospheric ground, a light that travels down the
   protection chain, a rule that draws under the coral word, and the coral point
   of the mark breathing. Everything additive and absolutely positioned or
   painted into an existing box, so nothing moves: CLS stays 0.

Idempotent. Aborts rather than writing twice.
"""
import sys, pathlib

p = pathlib.Path("index.html")
h = p.read_text(encoding="utf-8")

STYLE_ID = 'hs-home3'
if STYLE_ID in h:
    sys.exit(f"abort: <style id=\"{STYLE_ID}\"> already present")

if h.count("</head>") != 1:
    sys.exit("abort: expected exactly one </head>")
if h.count('<div class="rtcount">') != 1:
    sys.exit("abort: expected exactly one .rtcount div")
if h.count('<div class="rtcard rv">') != 1:
    sys.exit("abort: expected exactly one .rtcard")

CSS = """<style id="hs-home3">
/* ---- 1. the count line -------------------------------------------------
   This div was in the markup with no rule behind it: default 16px Inter,
   default block margins, sitting outside the card's 24px gutter. */
.rtcard .rtcount{display:inline-flex;align-items:center;gap:7px;
  margin:16px 24px 0;padding:5px 12px;border-radius:999px;
  font-family:var(--font-mono);font-size:11px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--coral);
  background:rgba(242,109,90,.10);border:1px solid rgba(242,109,90,.28)}
.rtcard .rtcount::before{content:"";width:6px;height:6px;border-radius:50%;
  background:var(--coral);flex:none}

/* ---- 2. the card that carries the question -----------------------------
   Matched to .priority-main in Participate. Same ask, same treatment.
   ::before needs z-index because .h paints its own panel background. */
.rtcard{position:relative;border-color:#E7B4A8;
  background-image:linear-gradient(155deg,rgba(242,109,90,0) 38%,rgba(242,109,90,.075) 100%)}
.rtcard::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;z-index:2;
  background:linear-gradient(90deg,var(--coral),#f59277)}
.rtcard:hover{box-shadow:0 18px 44px rgba(242,109,90,.18)}
.rtcard .h{background:rgba(255,255,255,.55);border-bottom-color:#F1D3CA}

/* ---- 3. depth in the hero ---------------------------------------------- */
/* Two soft blooms so the navy reads as a field with a light in it rather
   than a flat fill. Behind everything, pointer-events off. */
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(58% 52% at 20% 26%,rgba(96,138,198,.20),rgba(96,138,198,0) 72%),
    radial-gradient(46% 46% at 82% 78%,rgba(242,109,90,.13),rgba(242,109,90,0) 72%)}
.hero .wrap{position:relative;z-index:1}
.hero .crest{opacity:.07}

/* The coral word gets its rule drawn under it once the words have landed. */
.hero h1 .wr[style*="coral"]{position:relative}
.hero h1 .wr[style*="coral"]::after{content:"";position:absolute;left:0;right:0;
  bottom:.02em;height:3px;border-radius:2px;
  background:linear-gradient(90deg,var(--coral),rgba(242,109,90,.22));
  transform:scaleX(0);transform-origin:left center;
  animation:hlDraw .95s var(--ease) 1.05s forwards}
@keyframes hlDraw{to{transform:scaleX(1)}}

/* The point of life keeps breathing after it arrives. */
@keyframes cptBreathe{0%,100%{box-shadow:0 0 0 0 rgba(242,109,90,.42)}
  50%{box-shadow:0 0 0 10px rgba(242,109,90,0)}}
.brandmark .cpt{animation:cptin .5s var(--ease) 1.05s forwards,
  cptBreathe 3.8s var(--ease) 2.2s infinite}

/* The chain card lifts off the navy, and a light travels down the chain
   once, slowly, the way the argument runs down it. */
.chain{background:linear-gradient(160deg,rgba(255,255,255,.085),rgba(255,255,255,.028));
  border-color:rgba(255,255,255,.18);box-shadow:0 26px 64px rgba(6,16,30,.34)}
.chain .line::after{content:"";position:absolute;left:-1px;top:0;width:3px;height:100%;
  border-radius:2px;
  background:linear-gradient(180deg,rgba(242,109,90,0) 0%,rgba(255,196,181,.95) 7%,
    rgba(242,109,90,0) 15%,rgba(242,109,90,0) 100%);
  background-size:100% 300%;background-repeat:no-repeat;
  animation:chFlow 6.4s linear 2.9s infinite}
@keyframes chFlow{0%{background-position:0 -105%}100%{background-position:0 205%}}

@media(max-width:760px){
  .hero::before{background:radial-gradient(70% 40% at 30% 22%,rgba(96,138,198,.18),rgba(96,138,198,0) 74%)}
}
@media(prefers-reduced-motion:reduce){
  .hero h1 .wr[style*="coral"]::after{animation:none;transform:none}
  .brandmark .cpt{animation:none;box-shadow:none}
  .chain .line::after{animation:none;display:none}
}
</style></head>"""

h = h.replace("</head>", CSS, 1)

for needle, want in (
    ('<style id="hs-home3">', 1),
    ("</head>", 1),
    (".rtcard .rtcount{", 1),
    (".hero::before{", 2),   # base rule plus the narrow-width override
    ('<div class="rtcount">', 1),
    ("@keyframes chFlow", 1),
):
    got = h.count(needle)
    if got != want:
        sys.exit(f"abort: {needle!r} appears {got}x, expected {want}")

p.write_text(h, encoding="utf-8")
print("index.html: hs-home3 inserted")
