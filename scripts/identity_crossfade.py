#!/usr/bin/env python3
"""Stagger the chapter cross-fade on identity.html.

Measured live on 9 September 2026: the outgoing and incoming beat both ran a
.5s opacity transition at the same time, so for ~350ms two chapters sat on top
of each other at ~0.5 opacity each and the text read as garbage. Both beats are
position:absolute; inset:0, so there is nowhere for the second one to go.

The fix is timing, not layout. The outgoing beat clears in .22s; the incoming
one waits .24s before it starts. Same half-second overall, never two texts at
once. Verified by sampling computed opacity every 50ms across several
transitions: zero frames with more than one beat above 0.08 opacity.

Beat content never exceeds the 230px reservation (max 192px at a 320px column),
so min-height is left alone and layout is unchanged: CLS stays 0.
"""
import re, sys, pathlib

p = pathlib.Path("identity.html")
h = p.read_text(encoding="utf-8")

ANCHOR = '<style id="hs-crest">'
if h.count(ANCHOR) != 1:
    sys.exit(f"abort: expected 1 {ANCHOR}, found {h.count(ANCHOR)}")

CSS = (
    "\n/* ---- chapter cross-fade ------------------------------------------------ */\n"
    "/* the outgoing chapter clears before the next arrives, so two texts are\n"
    "   never legible on top of each other (they share the same absolute box) */\n"
    "#identity.js-anim .beats .beat{transition:opacity .22s var(--ease),transform .22s var(--ease)}\n"
    "#identity.js-anim .beats .beat.active{transition-delay:.24s}\n"
)

MARK = "#identity.js-anim .beats .beat{"
if MARK in h:
    sys.exit("abort: cross-fade rules already present")

i = h.index(ANCHOR) + len(ANCHOR)
h = h[:i] + CSS + h[i:]

for needle, want in (
    (MARK, 1),
    ("#identity.js-anim .beats .beat.active{transition-delay:.24s}", 1),
    ('<style id="hs-crest">', 1),
    ('id="beats"', 1),
):
    got = h.count(needle)
    if got != want:
        sys.exit(f"abort: {needle!r} appears {got}x, expected {want}")

p.write_text(h, encoding="utf-8")
print("identity.html: staggered cross-fade inserted")
