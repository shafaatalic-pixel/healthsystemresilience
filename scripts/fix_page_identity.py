#!/usr/bin/env python3
"""
The roundtable page still called itself Roundtable No. 01 — in the title, the
description, the social cards, the eyebrow, the breadcrumb and the site-wide
announcement bar — while its hero now carries question No. 02. The social cards
were the worst of it: they advertised "who actually receives health evidence?",
a question that no longer leads the page.

The page is a hub of three open questions, so it is named as one. The individual
numbers stay where they belong: on the question cards, in the record's account of
the first window, and in the FAQ.

Idempotent. Run from the website root: python3 scripts/fix_page_identity.py .
"""
import os
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

# One string, written both into the static markup and by renderStanding(), so the
# pre-paint and post-paint text are byte-identical and nothing reflows.
OPEN_LINE = "Three questions &middot; none with a closing date"


def edit(rel, pairs):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        raise SystemExit("missing: " + rel)
    s = o = open(p, encoding="utf-8").read()
    for pair in pairs:
        old, new = pair[0], pair[1]
        third = pair[2] if len(pair) > 2 else None
        sentinel = third if isinstance(third, str) else new
        want = third if isinstance(third, int) else 1
        if sentinel in s:
            continue
        c = s.count(old)
        if c != want:
            raise SystemExit("ABORT %s: found %d of %r (wanted %d)" % (rel, c, old[:110], want))
        s = s.replace(old, new)
    if s != o:
        open(p, "w", encoding="utf-8").write(s)
        print("  edited:", rel)
    else:
        print("  already current:", rel)


DESC = ("Three open HSREP Roundtable questions, answered on the record by named professionals: "
        "where preventive care breaks down between recommended and completed, what makes a health "
        "message land, and what the cost of care does that never reaches the record.")
SOCIAL_DESC = ("Three questions open with no closing date, each answerable from your own work. "
               "Responses are read before publication, appear under the contributor's name, and "
               "enter a citable synthesis.")

edit("roundtable.html", [
    # --- head: identity and social cards -----------------------------------
    ("<title>Roundtable &#8470; 01 - HSREP</title>",
     "<title>Roundtables, three open questions - HSREP</title>"),
    ('<meta name="description" content="HSREP Roundtable № 01, an open, on-the-record professional '
     'discussion of how platform choice shapes who receives health evidence.">',
     '<meta name="description" content="%s">' % DESC),
    ('<meta property="og:title" content="Roundtable № 01, who actually receives health evidence?">',
     '<meta property="og:title" content="HSREP Roundtables, three open questions">'),
    ('<meta name="twitter:title" content="Roundtable № 01, who actually receives health evidence?">',
     '<meta name="twitter:title" content="HSREP Roundtables, three open questions">'),
    # --- structured data ---------------------------------------------------
    ('"name": "Roundtable No. 01 - HSREP"', '"name": "Roundtables, three open questions - HSREP"'),
    ('"position": 2, "name": "Roundtable No. 01", "item"',
     '"position": 2, "name": "Roundtables", "item"'),
    ('"inLanguage": "en", "dateModified": "2026-08-04"',
     '"inLanguage": "en", "dateModified": "2026-09-09"'),
    # --- the hero ----------------------------------------------------------
    ('<div class="eyebrow on-dark"><span class="dot"></span>HSREP Roundtable &#8470; 01</div>',
     '<div class="eyebrow on-dark"><span class="dot"></span>HSREP Roundtables &middot; three open questions</div>'),
    # the opened-date line, in the markup and in the script that rewrites it
    ('>Opened 11 August 2026</span></div>', '>' + OPEN_LINE + '</span></div>'),
    (">Opened 11 August 2026</span>';", '>' + OPEN_LINE + "</span>';"),
    # the scheduled branch is dormant but should not name one question either
    ("synth.innerHTML='<p class=\"big\">Roundtable &#8470; 01 opens '+open.toDateString().slice(4)+'. "
     "The synthesis will publish here once the 14-day window closes.</p>';",
     "synth.innerHTML='<p class=\"big\">The next roundtable question opens '+open.toDateString().slice(4)+'. "
     "The synthesis will publish here once the window closes.</p>';"),
])

# The two social descriptions still describe the old question, so replace the whole
# attribute rather than matching its wording.
import re

p = os.path.join(ROOT, "roundtable.html")
s = o = open(p, encoding="utf-8").read()
for key, attr in (("og:description", "property"), ("twitter:description", "name")):
    s = re.sub(r'(<meta %s="%s" content=")[^"]*(">)' % (attr, key),
               lambda m: m.group(1) + SOCIAL_DESC + m.group(2), s, count=1)
if s != o:
    open(p, "w", encoding="utf-8").write(s)
    print("  edited: roundtable.html (social descriptions)")
else:
    print("  already current: roundtable.html (social descriptions)")

# --- the share landing page ------------------------------------------------
edit("go/discuss.html", [
    ("<title>Join HSREP Roundtable № 01, add your professional response</title>",
     "<title>Join an HSREP Roundtable, add your professional response</title>"),
    ('<meta property="og:title" content="Join HSREP Roundtable № 01, add your professional response">',
     '<meta property="og:title" content="Join an HSREP Roundtable, add your professional response">'),
    ('<meta name="twitter:title" content="Join HSREP Roundtable № 01, add your professional response">',
     '<meta name="twitter:title" content="Join an HSREP Roundtable, add your professional response">'),
])

# --- the site-wide announcement bar ----------------------------------------
edit("assets/analytics.js", [
    ('kicker = "Roundtable № 01";', 'kicker = "HSREP Roundtables";', 2),
    ('desktop = "Open now, no closing date.";',
     'desktop = "Three questions open, no closing date.";'),
])

print("done")
