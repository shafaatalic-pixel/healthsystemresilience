#!/usr/bin/env python3
"""
Cut the home page to about half its length, and put what leaves on the page that
owns the subject.

    python3 scripts/home_cut.py .

Per HSREP_Impact_Page_and_Home_Cut_Plan.md, part 2. Four moves:

  * The FAQ, 605 words and 27% of the page, drops from ten questions to three.
    Four go to about.html, two to initiative.html, one is dropped because
    about.html already answers it. The structured data travels with them, so no
    answer-engine value is lost — the questions simply get answered on the page
    whose whole subject is the answer.
  * #focus moves to the Season 1 hub, where the next-season brief belongs.
  * The founder block becomes two sentences and a link.
  * An Impact snapshot arrives, rendered from data/impact.json like every other
    figure on the site.

Then the section numbers are rewritten in document order, because three of them
have just left.

Idempotent. Run scripts/impact_render.py afterwards to fill the snapshot.
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
IX = os.path.join(ROOT, "index.html")

FAQ_RE = re.compile(r'<details class="faqi"><summary>(.*?)<span class="fx"></span></summary>'
                    r'<div class="faqa">(.*?)</div></details>', re.S)

# 0-based, against the ten questions as they stand on the home page
KEEP = {0, 2, 7}                 # what HSREP is, what the thesis means, how to engage
TO_ABOUT = [1, 3, 4, 9]          # who is behind it, what Season 1 was, what it found, how counted
TO_INITIATIVE = [5]              # the initiative; the gap is already answered there
DROP = {6, 8}                    # initiative.html already answers the gap question,
                                 # about.html the affiliation one

SNAPSHOT = """<!-- § IMPACT SNAPSHOT -->
<section id="impact-snapshot"><div class="wrap">
<div class="shead rv"><div class="eyebrow"><span class="snum">&#167;&nbsp;03</span> &middot; Impact</div>
<div class="top"><h2 class="sec">Is anyone actually reading this?</h2><div class="lead">The first question a professional asks about a platform they have not heard of. HSREP publishes the answer, including the parts that are not flattering.</div></div></div>
<!--IMPACT:HOME:START--><!--IMPACT:HOME:END-->
</div></section>
"""

SNAPSHOT_CSS = """<style id="hs-snapshot">
/* Four figures and a link. Written into the markup by scripts/impact_render.py,
   so the home page stays correct at first paint. */
#impact-snapshot .snap{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:14px;margin:8px 0 20px}
#impact-snapshot .snap div{background:var(--white);border:1px solid var(--hairline);border-radius:var(--r-lg);padding:17px 19px;box-shadow:var(--sh-xs)}
#impact-snapshot .snap b{display:block;font-family:var(--font-display);font-weight:700;font-size:31px;line-height:1;color:var(--navy);font-variant-numeric:tabular-nums}
#impact-snapshot .snap span{display:block;margin-top:7px;font-size:13.5px;line-height:1.4;color:var(--muted)}
#impact-snapshot .snapnote{font-size:14.5px;color:var(--muted);max-width:70ch;margin:0 0 16px}
@media(max-width:640px){#impact-snapshot .snap b{font-size:27px}}
</style></head>"""

FOUNDER = """<p>Founder of HSREP. A growth, marketing and public-health strategist with sixteen years turning complex systems into measurable results, grounded in public health. HSREP grew out of a Master of Public Health capstone at Eastern Michigan University and now publishes independently. <a href="about.html#founder-principal">Background, standards and disclosures &rarr;</a></p>"""

FAQ_TAIL = ('<p class="faqmore" style="margin:20px 0 0;font-size:15px;color:var(--muted)">'
            'More questions, including how HSREP is funded, how sources and corrections are '
            'handled, and who it is written for. <a href="about.html#faq">The full set '
            '&rarr;</a></p>')


def section(s, sid):
    a = s.rfind("<section", 0, s.index('id="%s"' % sid))
    b = s.index("</section>", a) + len("</section>")
    return s[a:b], a, b


def faq_jsonld(s):
    """The FAQPage node, wherever it sits — standalone or inside an @graph."""
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        if d.get("@type") == "FAQPage":
            return m, d, None
        for i, node in enumerate(d.get("@graph", []) or []):
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                return m, d, i
    return None, None, None


def put_jsonld(s, m, doc):
    return (s[:m.start()] + '<script type="application/ld+json">'
            + json.dumps(doc, ensure_ascii=False) + "</script>" + s[m.end():])


def entities(doc, idx):
    return (doc["@graph"][idx] if idx is not None else doc)["mainEntity"]


def append_to(page_name, blocks, ents):
    """Add questions and their structured data to a page that already has both."""
    p = os.path.join(ROOT, page_name)
    s = open(p, encoding="utf-8").read()
    m, doc, idx = faq_jsonld(s)
    if m is None:
        raise SystemExit("ABORT: no FAQPage structured data on " + page_name)
    have = {e["name"] for e in entities(doc, idx)}
    fresh_e = [e for e in ents if e["name"] not in have]
    fresh_b = [b for b, e in zip(blocks, ents) if e["name"] not in have]
    if not fresh_b:
        print("  already current:", page_name)
        return
    close = s.rfind("</details>") + len("</details>")
    s = s[:close] + "".join(fresh_b) + s[close:]
    m, doc, idx = faq_jsonld(s)          # positions moved
    entities(doc, idx).extend(fresh_e)
    s = put_jsonld(s, m, doc)
    open(p, "w", encoding="utf-8").write(s)
    print("  %s: +%d questions" % (page_name, len(fresh_b)))


def main():
    s = open(IX, encoding="utf-8").read()

    # ---------- 1. the FAQ ------------------------------------------------
    faq_block, fa, fb = section(s, "faq")
    blocks = ["<details class=\"faqi\"><summary>%s<span class=\"fx\"></span></summary>"
              "<div class=\"faqa\">%s</div></details>" % (m.group(1), m.group(2))
              for m in FAQ_RE.finditer(faq_block)]
    m, doc, idx = faq_jsonld(s)
    ents = entities(doc, idx) if m is not None else []

    if len(blocks) == 10 and len(ents) == 10:
        append_to("about.html", [blocks[i] for i in TO_ABOUT], [ents[i] for i in TO_ABOUT])
        append_to("initiative.html", [blocks[i] for i in TO_INITIATIVE],
                  [ents[i] for i in TO_INITIATIVE])
        kept_b = [blocks[i] for i in sorted(KEEP)]
        kept_e = [ents[i] for i in sorted(KEEP)]
        new_faq = FAQ_RE.sub("", faq_block, count=0)
        new_faq = new_faq.replace('<div class="faqlist rv">',
                                  '<div class="faqlist rv">' + "".join(kept_b), 1)
        if 'class="faqmore"' not in new_faq:
            new_faq = new_faq.replace("</div></div></section>", FAQ_TAIL + "</div></div></section>", 1)
        s = s[:fa] + new_faq + s[fb:]
        m, doc, idx = faq_jsonld(s)
        if idx is not None:
            doc["@graph"][idx]["mainEntity"] = kept_e
        else:
            doc["mainEntity"] = kept_e
        s = put_jsonld(s, m, doc)
        print("  index.html: FAQ 10 -> 3")
    else:
        print("  already current: FAQ (%d visible, %d in structured data)"
              % (len(blocks), len(ents)))

    # ---------- 2. #focus to the season hub --------------------------------
    if 'id="focus"' in s:
        blk, a, b = section(s, "focus")
        s = s[:a] + s[b:]
        sp = os.path.join(ROOT, "season-1.html")
        t = open(sp, encoding="utf-8").read()
        if 'id="focus"' not in t:
            moved = re.sub(r'<span class="snum">[^<]*</span>\s*&middot;\s*', "", blk)
            moved = re.sub(r'<span class="snum">[^<]*</span>\s*·\s*', "", moved)
            t = t.replace("</main>", moved + "\n</main>", 1)
            open(sp, "w", encoding="utf-8").write(t)
            print("  season-1.html: areas of focus moved in")
        print("  index.html: #focus removed")
    else:
        print("  already current: #focus")

    # ---------- 3. the founder block ---------------------------------------
    if "Background, standards and disclosures" not in s:
        blk, a, b = section(s, "about")
        new = re.sub(r"<p>Founder of HSREP\..*?</p>", FOUNDER, blk, count=1, flags=re.S)
        s = s[:a] + new + s[b:]
        print("  index.html: founder block trimmed")
    else:
        print("  already current: founder block")

    # ---------- 4. the impact snapshot -------------------------------------
    if "<!--IMPACT:HOME:START-->" not in s:
        blk, a, b = section(s, "findings")
        s = s[:b] + "\n\n" + SNAPSHOT + s[b:]
        print("  index.html: impact snapshot added")
    else:
        print("  already current: impact snapshot")
    if 'id="hs-snapshot"' not in s:
        s = s.replace("</head>", SNAPSHOT_CSS, 1)

    # ---------- 5. renumber -------------------------------------------------
    n = [0]

    def bump(mo):
        n[0] += 1
        return '<span class="snum">&#167;&nbsp;%02d</span>' % n[0]

    s = re.sub(r'<span class="snum">(?:&#167;|§)&nbsp;\d+</span>', bump, s)
    print("  index.html: %d section numbers rewritten" % n[0])

    open(IX, "w", encoding="utf-8").write(s)


main()
print("done")
