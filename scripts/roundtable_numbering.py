#!/usr/bin/env python3
"""Stop inviting people into a numbered roundtable, and give methodology.html
the site's width.

Three questions are open at once with no closing date. Numbering them is useful
on roundtable.html, where the three cards sit side by side and the number says
which question you are reading. It is not useful in a call to action, where
"Join Roundtable No. 1" reads as an invitation to the window that closed on
25 August, and where the Season 1 hub said 01 while the home page said 02.

So: the number stays on the card that quotes a specific question (section 03 on
the home page still says "Roundtable No. 2" above that question, which is
accurate). Every generic invitation loses the number.

The Season 1 hub also pointed at index.html#roundtable rather than at
roundtable.html, so the button took a reader to a summary of the thing instead
of to the thing.

methodology.html gets the same width treatment as impact.html: .wrap to 1180px
so the header and footer match every other page, with the prose that had no cap
of its own held at 72ch so the measure does not run to 130 characters.
"""
import sys, pathlib

# ------------------------------------------------------------- season-1.html
p = pathlib.Path("season-1.html")
h = p.read_text(encoding="utf-8")
old = ('<a class="btn ghost" href="index.html#roundtable">'
       'Join Roundtable &#8470;&nbsp;01 <span class="ar">&rarr;</span></a>')
new = ('<a class="btn ghost" href="roundtable.html">'
       'Three questions open <span class="ar">&rarr;</span></a>')
if h.count(old) != 1:
    sys.exit(f"abort: season-1 CTA appears {h.count(old)}x")
h = h.replace(old, new, 1)
if "Join Roundtable &#8470;&nbsp;01" in h:
    sys.exit("abort: a numbered Season 1 invitation survived")
p.write_text(h, encoding="utf-8")
print("season-1.html: numbered invitation replaced, and it points at roundtable.html now")

# ----------------------------------------------------------------- index.html
p = pathlib.Path("index.html")
h = p.read_text(encoding="utf-8")
old = "<h3>Join Roundtable № 02</h3>"
new = "<h3>Join the roundtable</h3>"
if h.count(old) != 1:
    sys.exit(f"abort: index CTA heading appears {h.count(old)}x")
h = h.replace(old, new, 1)
# the section 03 card keeps its number: it labels the question quoted beneath it
if h.count("Roundtable <b>№ 02</b>") != 1:
    sys.exit("abort: the section 03 card label changed unexpectedly")
p.write_text(h, encoding="utf-8")
print("index.html: the Participate invitation no longer names a number")

# ----------------------------------------------------------- methodology.html
p = pathlib.Path("methodology.html")
h = p.read_text(encoding="utf-8")
old = ".wrap{max-width:960px;margin:0 auto;padding:0 22px}"
new = ("  /* the site's --maxw, written out because this page carries no external\n"
       "     stylesheet. The header and footer use .wrap, so 960px here put the\n"
       "     navigation on two lines while every other page kept one. Prose that\n"
       "     had no cap of its own is held at 72ch so the measure stays readable\n"
       "     in the wider column. */\n"
       "  .wrap{max-width:1180px;margin:0 auto;padding:0 24px}\n"
       "  main p,main li,main h3{max-width:72ch}")
if h.count(old) != 1:
    sys.exit(f"abort: methodology .wrap rule appears {h.count(old)}x")
h = h.replace(old, new, 1)
for needle, want in (("max-width:1180px", 1), ("main p,main li,main h3{max-width:72ch}", 1)):
    if h.count(needle) != want:
        sys.exit(f"abort: {needle!r} appears {h.count(needle)}x")
p.write_text(h, encoding="utf-8")
print("methodology.html: .wrap widened to 1180px, prose capped at 72ch")
