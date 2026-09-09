#!/usr/bin/env python3
"""
Give impact.html its own opening, and stop it claiming methodology's structured data.

    python3 scripts/impact_page_identity.py .

impact.html was scaffolded from methodology.html. The scaffold replaced <main>,
but methodology's hero band sits *outside* main, so the live Impact page opened
with "Season 1 - Impact Methodology & Reconciliation / How we count 57,274." and
then, immediately below, a second <h1> reading "What the record shows."

Three things carried over the same way and are fixed here:

  * the hero band, which now carries the Impact page's own eyebrow, heading and
    lede, with the duplicate opening block removed from <main>;
  * the WebPage node, which still named and described the methodology page, and
    a breadcrumb whose last crumb read "Methodology";
  * a Dataset node describing the Season 1 campaign dataset, and an FAQPage node
    with seven questions, none of which appear anywhere on this page. Structured
    data has to describe what is on the page, so both are removed. Neither is
    lost: methodology.html still carries them, and it is where they are true.

Idempotent.
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
P = os.path.join(ROOT, "impact.html")

HERO = ('<div class="hero"><div class="wrap">\n'
        ' <div class="ey">The record</div>\n'
        ' <h1>What the record shows.</h1>\n'
        " <p>The platform's own account of itself: how far the arguments travelled, "
        "who actually read them, what people did next, and what did not work. It is "
        "kept as advocacy intelligence rather than as a scoreboard, which means the "
        "uncomfortable figures are here too.</p>\n"
        "</div></div>")

NAME = "Impact, what the record shows - HSREP"
DESC = ("Readership, retrieval, participation and the record of what did not work, "
        "for the HSREP advocacy platform.")


def main():
    s = open(P, encoding="utf-8").read()
    before = s

    # ---- 1. the hero -------------------------------------------------------
    m = re.search(r'<div class="hero"><div class="wrap">.*?</div></div>', s, re.S)
    if m is None:
        raise SystemExit("ABORT: no hero band found on impact.html")
    if "How we count" in m.group(0):
        s = s[:m.start()] + HERO + s[m.end():]
        print("  hero replaced")
    else:
        print("  already current: hero")

    # ---- 2. the duplicate opening block in <main> --------------------------
    dup = re.search(r'<section><div class="wrap">\s*<div class="kicker" id="the-record">'
                    r'.*?(<p class="imp-updated">.*?</p>)\s*</div></section>', s, re.S)
    if dup:
        s = (s[:dup.start()] + '<section><div class="wrap">\n' + dup.group(1)
             + "\n</div></section>" + s[dup.end():])
        print("  duplicate opening block removed from <main>")
    else:
        print("  already current: <main> opening")

    if s.count("<h1") != 1:
        raise SystemExit("ABORT: expected exactly one <h1>, found %d" % s.count("<h1"))

    # ---- 3. the structured data --------------------------------------------
    jm = re.search(r'<script type="application/ld\+json">(\{.*?"@graph".*?\})</script>', s, re.S)
    if jm is None:
        raise SystemExit("ABORT: no @graph structured data on impact.html")
    doc = json.loads(jm.group(1))
    g = doc["@graph"]
    changed = False

    keep = [nd for nd in g if nd.get("@type") not in ("Dataset", "FAQPage")]
    if len(keep) != len(g):
        print("  removed %d node(s) describing content this page does not have"
              % (len(g) - len(keep)))
        g = keep
        changed = True

    for nd in g:
        if nd.get("@type") == "WebPage" and nd.get("name") != NAME:
            nd["name"] = NAME
            nd["description"] = DESC
            changed = True
            print("  WebPage node renamed")
        if nd.get("@type") == "BreadcrumbList":
            last = nd["itemListElement"][-1]
            if last.get("name") != "Impact":
                last["name"] = "Impact"
                changed = True
                print("  breadcrumb corrected")

    if changed:
        doc["@graph"] = g
        s = (s[:jm.start()] + '<script type="application/ld+json">'
             + json.dumps(doc, ensure_ascii=False) + "</script>" + s[jm.end():])
    else:
        print("  already current: structured data")

    for mk in ("UPDATED", "READERS", "ARRIVAL", "MACHINES", "ACTIONS",
               "PARTICIPATION", "SEASON1"):
        for edge in ("START", "END"):
            tag = "<!--IMPACT:%s:%s-->" % (mk, edge)
            if s.count(tag) != 1:
                raise SystemExit("ABORT: %s appears %d times" % (tag, s.count(tag)))

    if s != before:
        open(P, "w", encoding="utf-8").write(s)
        print("  wrote: impact.html")
    else:
        print("  no change")


main()
print("done")
