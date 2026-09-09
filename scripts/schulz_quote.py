#!/usr/bin/env python3
"""Publish Dr. Schulz's full endorsement. Approved 9 September 2026.

The wall has carried a one-line first-person statement since 7 August, with the
fuller wording staged in an HTML comment marked PENDING SCHULZ APPROVAL. That
was deliberate: the long version was drafted for him to approve or rewrite, and
publishing it before he confirmed would have been a fabricated testimonial. He
approved it, so the staged text becomes the published text and the comment goes.

Wording is his approved text verbatim, with the possessive corrected in
"Shafaat's capstone" (the staged draft read "Shafaat capstone"). Multi-paragraph
quotation convention: an opening quote mark on each paragraph, a closing mark
only on the last.
"""
import sys, pathlib

p = pathlib.Path("index.html")
h = p.read_text(encoding="utf-8")

# 1. the staged comment goes ------------------------------------------------
start = h.find("<!-- PENDING SCHULZ APPROVAL.")
if start < 0:
    sys.exit("abort: the pending-approval comment is not there")
end = h.find("-->", start)
if end < 0:
    sys.exit("abort: unterminated comment")
h = h[:start] + h[end + 3:]
if "PENDING SCHULZ APPROVAL" in h:
    sys.exit("abort: a second pending comment survived")

# 2. the short line becomes the approved quotation ---------------------------
OLD = ('<p class="q">&ldquo;I chaired the Season&nbsp;1 capstone, '
       'and I support HSREP.&rdquo;</p>')
NEW = (
 '<p class="q">&ldquo;I chaired Shafaat\'s capstone, so I have followed this '
 'from the start, and it has grown into a serious, well-documented platform. '
 'He is careful about what the evidence can and cannot show, which is what '
 'makes the advocacy worth trusting.</p>\n'
 '<p class="q">&ldquo;He also would not stop at the argument. The Prevention '
 'Adoption Initiative takes the hardest part of prevention, turning a '
 'recommended screening into a completed one, and treats it as something to '
 'design and test responsibly, with sustainability in mind.</p>\n'
 '<p class="q">&ldquo;It is that pairing, credible advocacy and a real plan to '
 'act on it, that makes me glad to support the work and to encourage the right '
 'partner to take a serious look.&rdquo;</p>'
)
if h.count(OLD) != 1:
    sys.exit(f"abort: the short Schulz line appears {h.count(OLD)}x")
h = h.replace(OLD, NEW, 1)

# 3. a rule so the follow-on paragraphs do not each draw the card's hairline --
STYLE_ID = 'hs-endo-quote'
if STYLE_ID in h:
    sys.exit("abort: the endorsement style block is already present")
CSS = ('<style id="hs-endo-quote">\n'
       '/* .endo .q carries the card\'s top hairline. In a multi-paragraph\n'
       '   quotation only the first paragraph should. Cards align to the top so\n'
       '   the two short ones are not stretched to match the long one. */\n'
       '.endos{align-items:start}\n'
       '.endo .q + .q{border-top:0;padding-top:0;margin-top:9px}\n'
       '</style></head>')
if h.count("</head>") != 1:
    sys.exit("abort: expected exactly one </head>")
h = h.replace("</head>", CSS, 1)

for needle, want in (
    ("Shafaat's capstone", 1),
    ("I chaired the Season&nbsp;1 capstone", 0),
    ('<p class="q">', 5),      # roundtable question, reader prompt, three Schulz paragraphs
    ("&rdquo;", 4),            # unchanged: the long quote closes once, as the short line did
    ('<div class="who">Dr. Jeffrey Schulz</div>', 1),
    ('<span class="cnt">1<small>on record</small></span>', 1),
    ('<style id="hs-endo-quote">', 1),
):
    got = h.count(needle)
    if got != want:
        sys.exit(f"abort: {needle!r} appears {got}x, expected {want}")

p.write_text(h, encoding="utf-8")
print("index.html: Dr. Schulz's approved endorsement published")
