#!/usr/bin/env python3
"""Participate leads with the partnership ask; the roundtable steps back.

The roundtable already owns the header button, the standing campaign banner and
the whole of section 03 directly above. Section 04 was making the same ask a
fourth time in its largest slot, while "Could you host or evaluate the pilot?"
— the only ask on the page with no other home, and the one the pilot cannot
start without — sat in a small secondary card.

The grid places cards by class, not by document order, so the swap is a class
swap plus the reveal delays, the button weights, and an icon for the card that
now leads. Nothing moves in the flow: no layout change, CLS unaffected.

Also widens impact.html to the site's 1180px. It was built from a standalone
template that set .wrap to 960px, and because the header and footer use .wrap
too, the Impact page's navigation wrapped onto two lines while every other page
sat on one.
"""
import sys, pathlib

# ---------------------------------------------------------------- index.html
p = pathlib.Path("index.html")
h = p.read_text(encoding="utf-8")

ICON = ('<div class="picon"><svg viewBox="0 0 24 24">'
        '<path d="M9.5 4h5a1 1 0 0 1 1 1v1.2h-7V5a1 1 0 0 1 1-1z"/>'
        '<path d="M15.5 6.2H18a1 1 0 0 1 1 1V19a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7.2a1 1 0 0 1 1-1h2.5"/>'
        '<path d="M9 13.2l2 2 4-4"/></svg></div>')

SUBS = [
    # the roundtable card steps back to secondary
    ('<div class="path rv priority-main" id="discuss"><div class="picon"><svg viewBox="0 0 24 24">'
     '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>'
     '</svg></div>',
     '<div class="path rv priority-secondary" id="discuss" style="transition-delay:.08s">'),

    # its button is no longer the section's primary action
    ('<a class="btn accent" id="rt-cta2" href="roundtable.html#respond">',
     '<a class="btn ghost" id="rt-cta2" href="roundtable.html#respond">'),

    # the partnership card takes the lead, with an icon of its own
    ('<div class="path rv priority-secondary" id="partner" style="transition-delay:.08s">'
     '<div class="n">PARTNERSHIP · CONSIDERED ASK</div>',
     '<div class="path rv priority-main" id="partner">' + ICON +
     '<div class="n">PARTNERSHIP · CONSIDERED ASK</div>'),

    ('<a class="btn ghost" href="https://calendly.com/shafaat-alic/30min" target="_blank" rel="noopener">Request the presentation',
     '<a class="btn accent" href="https://calendly.com/shafaat-alic/30min" target="_blank" rel="noopener">Request the presentation'),

    # the section lead read roundtable-first
    ('<div class="lead">Three roundtable questions are open, none with a closing date. '
     'Partnership and newsletter options remain available without competing for attention.</div>',
     '<div class="lead">The pilot needs a host site and an independent evaluator before it '
     'can run. The three roundtable questions stay open above, and the newsletter is there '
     'if now is not the time.</div>'),
]

for old, new in SUBS:
    n = h.count(old)
    if n != 1:
        sys.exit(f"abort: {n} matches for {old[:70]!r}")
    h = h.replace(old, new, 1)

for needle, want in (
    ('id="partner"', 1), ('id="discuss"', 1),
    ('class="path rv priority-main" id="partner"', 1),
    ('class="path rv priority-secondary" id="discuss"', 1),
    ('priority-main', 7),          # 1 markup + 5 CSS rules + 1 in a comment
    ('priority-secondary', 2),     # 1 markup + 1 CSS rule
    ('priority-fallback', 2),
    ('class="picon"', 1),          # the icon moves to the partnership card
    ('rt-cta2', 2),                # the anchor and the script that relabels it
):
    got = h.count(needle)
    if got != want:
        sys.exit(f"abort: {needle!r} appears {got}x, expected {want}")

p.write_text(h, encoding="utf-8")
print("index.html: partnership now leads Participate")

# --------------------------------------------------------------- impact.html
q = pathlib.Path("impact.html")
t = q.read_text(encoding="utf-8")
old = ".wrap{max-width:960px;margin:0 auto;padding:0 22px}"
new = ("  /* the site's --maxw. This page carries no external stylesheet, so the\n"
       "     value is written out. 960px here also squeezed the header, which\n"
       "     uses .wrap, and pushed the nav onto two lines. */\n"
       "  .wrap{max-width:1180px;margin:0 auto;padding:0 24px}")
if t.count(old) != 1:
    sys.exit(f"abort: {t.count(old)} matches for the impact .wrap rule")
t = t.replace(old, new, 1)
if t.count("max-width:1180px") != 1:
    sys.exit("abort: 1180 count")
q.write_text(t, encoding="utf-8")
print("impact.html: .wrap widened to 1180px")
