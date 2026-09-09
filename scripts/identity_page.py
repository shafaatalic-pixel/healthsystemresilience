#!/usr/bin/env python3
"""
Give the crest its own page, and take it off a home page that was not showing it.

    python3 scripts/identity_page.py .

Found on 9 September: commit 61cbe56 (18 August) added a bare `hidden` attribute
to <section id="identity"> and <section id="mission-vision"> on index.html, and
nothing was ever written to remove it. Both have been display:none on the live
home page for three weeks. The campaign band in the same commit is toggled by a
script; these two were not, and were never meant to carry the attribute.

So this is a restoration rather than a relocation:

  * identity.html takes the whole crest story, visible, with room to be longer
    than a homepage section can be.
  * index.html loses both sections, and the hero gains one line naming what the
    coral point is and linking to the full story. The exposition would argue
    against itself in the hero — its own opening line is "Most platforms open
    with a logo. Ours opens with a promise" — so the idea is promoted and the
    telling is not.
  * mission-vision is not moved: about.html#mission-vision already carries it.

Idempotent.
"""
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

DESC = ("The HSREP mark, read one element at a time: an open arch, a rising "
        "foundation, three figures who are deliberately unalike, and a single "
        "coral point. A promise about how health protection should be built.")

IDLINE = ('<p class="idline">The coral point in our mark is the person the whole structure '
          'exists to protect, and it is the accent on every action you can take here. '
          '<a href="identity.html">Read the crest &rarr;</a></p>')

IDLINE_CSS = """<style id="hs-idline">
/* One line in the hero, not the whole crest story. The full telling opens with
   "Most platforms open with a logo. Ours opens with a promise", which only works
   where it now lives — on its own page, a click away. */
.hero .idline{margin:18px 0 22px;font-size:14.5px;line-height:1.55;color:#b9c7d8;max-width:56ch}
.hero .idline a{color:#fff;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.35);
  padding-bottom:1px;white-space:nowrap}
.hero .idline a:hover,.hero .idline a:focus-visible{color:var(--coral);border-bottom-color:var(--coral)}
@media(max-width:720px){.hero .idline{font-size:14px}}
</style></head>"""

OPENER = """<section class="band" id="the-mark" style="background:var(--paper)"><div class="wrap">
<div class="shead rv"><div class="eyebrow">Identity</div><div class="top"><h1 class="sec" style="margin:0">Most platforms open with a logo.</h1><div class="lead">HSREP opens with a promise. The mark is not decoration and it is not a monogram: it is the argument drawn, and it is where the platform's one warm colour comes from. Read it one element at a time.</div></div></div>
</div></section>
"""


def cut(s, start_marker, end_marker):
    a = s.index(start_marker)
    b = s.index(end_marker, a + 1)
    return s[a:b], a, b


def swap_head(page):
    subs = [
        (r"<title>.*?</title>", "<title>The mark, and what it carries - HSREP</title>", 1),
        (r'(<meta name="description" content=")[^"]*(">)', r"\1%s\2" % DESC, 1),
        (r'(<meta property="og:title" content=")[^"]*(">)',
         r"\1The mark, and what it carries\2", 1),
        (r'(<meta name="twitter:title" content=")[^"]*(">)',
         r"\1The mark, and what it carries\2", 1),
        (r'(<meta property="og:description" content=")[^"]*(">)', r"\1%s\2" % DESC, 1),
        (r'(<meta name="twitter:description" content=")[^"]*(">)', r"\1%s\2" % DESC, 1),
        (r'(<meta property="og:url" content="https://hsraep\.org/)[^"]*(">)',
         r"\1identity.html\2", 1),
        (r'(<link rel="canonical" href="https://hsraep\.org/)[^"]*(">)',
         r"\1identity.html\2", 1),
        (r"(og/og-)[a-z0-9-]+(\.png)", r"\1identity\2", 0),
        (r'"name": "[^"]*- HSREP"', '"name": "The mark, and what it carries - HSREP"', 1),
    ]
    for pat, rep, count in subs:
        page = re.sub(pat, rep, page, count=count, flags=re.S)
    # The home page's structured data describes the home page. Drop the nodes that
    # do not apply here rather than leaving a FAQPage on a page with no FAQ.
    import json

    def prune(m):
        try:
            doc = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        drop = {"FAQPage", "ItemList", "WebPage", "BreadcrumbList", "CollectionPage"}
        if isinstance(doc.get("@graph"), list):
            doc["@graph"] = [x for x in doc["@graph"]
                             if not (isinstance(x, dict) and x.get("@type") in drop)]
        elif doc.get("@type") in drop:
            return ""
        return ('<script type="application/ld+json">'
                + json.dumps(doc, ensure_ascii=False) + "</script>")

    page = re.sub(r'<script type="application/ld\+json">(.*?)</script>', prune, page, flags=re.S)
    return page


def main():
    ip = os.path.join(ROOT, "index.html")
    s = open(ip, encoding="utf-8").read()
    dest0 = os.path.join(ROOT, "identity.html")

    if '<section class="band idstory js-off" id="identity"' not in s:
        # already moved on an earlier run; the links below are still worth checking
        if not os.path.exists(dest0):
            raise SystemExit("ABORT: index.html has no identity section and identity.html "
                             "does not exist. Restore one of them before re-running.")
        print("  already moved: identity is on identity.html, not index.html")
        links()
        return

    ident, ia, ib = cut(s, '<section class="band idstory js-off" id="identity"',
                        '<section class="mvband" id="mission-vision"')
    mv, ma, mb = cut(s, '<section class="mvband" id="mission-vision"', '<section id="faq"')

    # ---- identity.html -----------------------------------------------------
    a = s.index("<main")
    b = s.index("</main>") + len("</main>")
    body = ident.replace(' id="identity" hidden>', ' id="identity">', 1)
    # it is no longer section eight of anything, and h2 is the wrong level for a
    # page whose whole subject this is
    body = body.replace('<span class="snum">&#167;&nbsp;08</span> \u00b7 Identity', 'Identity', 1)
    body = body.replace('<span class="snum">§&nbsp;08</span> · Identity', 'Identity', 1)
    body = body.replace('<h2 class="sec">', '<h1 class="sec">', 1).replace(
        '</h2>', '</h1>', 1)
    page = s[:a] + '<main id="main" tabindex="-1">\n' + body + "\n</main>" + s[b:]
    page = swap_head(page)
    hdr = re.search(r"<header[^>]*>.*?</header>", page, re.S)
    if hdr:
        h = re.sub(r'\s*class="here"', "", hdr.group(0))
        page = page[:hdr.start()] + h + page[hdr.end():]
    if 'id="hs-idline"' in page:
        page = re.sub(r'<style id="hs-idline">.*?</style>', "", page, flags=re.S)
    dest = os.path.join(ROOT, "identity.html")
    old = open(dest, encoding="utf-8").read() if os.path.exists(dest) else None
    if page != old:
        open(dest, "w", encoding="utf-8").write(page)
        print("  wrote: identity.html")
    else:
        print("  already current: identity.html")

    # ---- index.html --------------------------------------------------------
    out = s[:ia] + s[mb:]
    if IDLINE not in out:
        anchor = '<div class="cta"><a class="btn accent" href="season-1.html">'
        if anchor not in out:
            raise SystemExit("ABORT: hero CTA not found, cannot place the identity line")
        out = out.replace(anchor, IDLINE + "\n" + anchor, 1)
    if 'id="hs-idline"' not in out:
        out = out.replace("</head>", IDLINE_CSS, 1)
    if out != s:
        open(ip, "w", encoding="utf-8").write(out)
        print("  index.html: identity and mission-vision removed, hero line added")
    else:
        print("  already current: index.html")

    links()


def links():
    """Footer link, sitemap and llms.txt. Safe to run on its own."""
    n = 0
    for dp, dn, fn in os.walk(ROOT):
        if any(x in dp for x in ("/.git", "node_modules", "_archive", "/scripts")):
            continue
        for f in fn:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            t = o = open(p, encoding="utf-8").read()
            i = t.find("<h2>Platform</h2>")
            if i >= 0:
                j = t.find("</div>", i)
                col = t[i:j]
                if ">The mark</a>" not in col:
                    m = re.search(r'<a href="([^"]*?)initiative\.html">Initiative</a>', col)
                    if m:
                        fixed = col.replace(
                            m.group(0),
                            m.group(0) + '<a href="%sidentity.html">The mark</a>' % m.group(1), 1)
                        t = t[:i] + fixed + t[j:]
            if t != o:
                open(p, "w", encoding="utf-8").write(t)
                n += 1
    print("  footer link added on %d pages" % n)

    sm = os.path.join(ROOT, "sitemap.xml")
    t = open(sm, encoding="utf-8").read()
    if "identity.html" in t:
        print("  sitemap.xml: already listed")
    else:
        m = re.search(r"[ \t]*<url>\s*<loc>https://hsraep\.org/about\.html</loc>", t)
        if not m:
            m = re.search(r"[ \t]*<url>\s*<loc>https://hsraep\.org/impact\.html</loc>", t)
        if not m:
            raise SystemExit("ABORT: no anchor <url> block in sitemap.xml")
        t = (t[:m.start()] + "  <url><loc>https://hsraep.org/identity.html</loc>"
             "<changefreq>yearly</changefreq><priority>0.5</priority></url>\n" + t[m.start():])
        open(sm, "w", encoding="utf-8").write(t)
        assert "identity.html" in open(sm, encoding="utf-8").read()
        print("  sitemap.xml: identity.html added")

    lt = os.path.join(ROOT, "llms.txt")
    t = open(lt, encoding="utf-8").read()
    if "identity.html" not in t:
        open(lt, "w", encoding="utf-8").write(
            t.rstrip() + "\n\n## The mark\nhttps://hsraep.org/identity.html\n"
            "The HSREP crest read one element at a time: an open arch, a rising foundation, "
            "three deliberately unalike figures, and one coral point, which is the person the "
            "structure exists to protect and the accent on every action on the site.\n")
        print("  llms.txt: The mark added")
    else:
        print("  llms.txt: already listed")


main()
print("done")
