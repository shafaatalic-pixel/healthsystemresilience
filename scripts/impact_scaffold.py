#!/usr/bin/env python3
"""
One-off: create impact.html and wire it into the site.

    python3 scripts/impact_scaffold.py .

The page shell (head, header, footer, scripts, CLS reserve) is copied from
methodology.html so it cannot drift from the rest of the site, and only <main>
is replaced. The prose lives here; every number is written between markers by
scripts/impact_render.py, so the page is complete at first paint and nothing
shifts.

Idempotent.
"""
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
DONOR = "methodology.html"
PAGE = "impact.html"

DESC = ("How far HSREP's arguments travelled, who actually read them, and what was "
        "learned. Readership, retrieval, participation and the record of what did "
        "not work.")

CSS = """<style id="hs-impact">
/* Impact. Every figure is written into the markup by scripts/impact_render.py,
   so nothing here is fetched or measured in the browser and the page cannot
   shift after first paint.

   The shell this page is copied from carries an older token vocabulary
   (--card, --line, --navy2) rather than the one the newer pages use, so seven
   tokens were resolving to nothing and the borders, radii and tinted panels
   silently disappeared. Bridge them here rather than editing the shared
   stylesheet, which other pages depend on. */
:root{--white:#fff;--hairline:var(--line,#DCE3EA);--panel:var(--paper,#F6F7F9);
  --coral-wash:#FDEEEA;--r-md:10px;--r-lg:14px;--sh-xs:0 1px 2px rgba(28,46,74,.06)}
.imp-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin:26px 0 22px}
.imp-t{background:var(--white);border:1px solid var(--hairline);border-radius:var(--r-lg);padding:18px 20px;box-shadow:var(--sh-xs)}
.imp-t b{display:block;font-family:var(--font-display);font-size:34px;line-height:1;color:var(--navy);font-variant-numeric:tabular-nums;font-weight:700}
.imp-t span{display:block;margin-top:8px;font-size:13.5px;line-height:1.4;color:var(--muted)}
.imp-t.is-quiet b{color:var(--muted)}
.imp-note{background:var(--coral-wash);border-left:3px solid var(--coral);border-radius:0 var(--r-md) var(--r-md) 0;
  padding:17px 20px;margin:4px 0 22px;max-width:76ch}
.imp-note p{margin:0;font-size:15.5px;line-height:1.6;color:var(--ink)}
.imp-note p+p{margin-top:10px}
.imp-bars{margin:22px 0;max-width:62ch}
.imp-bar{display:grid;grid-template-columns:150px 1fr 58px;align-items:center;gap:12px;margin-bottom:9px;font-size:14.5px}
.imp-bar i{display:block;height:9px;border-radius:5px;background:var(--navy);min-width:3px}
.imp-bar.alt i{background:var(--coral)}
.imp-bar.quiet i{background:var(--hairline)}
.imp-bar b{font-family:var(--font-mono);font-size:13px;color:var(--muted);text-align:right;font-weight:500}
.imp-tab{width:100%;border-collapse:collapse;margin:22px 0;font-size:14.5px;max-width:70ch}
.imp-tab th{font-family:var(--font-mono);letter-spacing:.05em}
.imp-tab td{padding:9px 12px 9px 0;border-bottom:1px solid var(--hairline);vertical-align:top}
.imp-tab td.n{font-family:var(--font-mono);font-variant-numeric:tabular-nums;white-space:nowrap;color:var(--navy)}
.imp-tab tbody tr.hi td{background:var(--coral-wash)}\n.imp-tab tbody tr.hi td:first-child{box-shadow:inset 3px 0 0 var(--coral)}
.imp-tab td small{color:var(--muted)}
.imp-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:8px 26px;margin:20px 0;max-width:72ch;
  font-size:14.5px}
.imp-list div{display:flex;justify-content:space-between;gap:14px;padding:7px 0;border-bottom:1px solid var(--hairline)}
.imp-list b{font-family:var(--font-mono);font-weight:500;color:var(--navy);font-variant-numeric:tabular-nums}
.imp-updated{font-family:var(--font-mono);font-size:11.5px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.imp-later{background:var(--panel);border:1px dashed var(--hairline);border-radius:var(--r-lg);padding:20px 22px;
  margin-top:12px;max-width:76ch}
.imp-later p{margin:0 0 8px;font-size:15px;color:var(--muted)}
.imp-later ul{margin:0;padding-left:19px;color:var(--muted);font-size:14.5px;line-height:1.7}
@media(max-width:640px){
  .imp-bar{grid-template-columns:112px 1fr 50px;font-size:13.5px}
  .imp-t b{font-size:29px}
}
</style></head>"""

MAIN = """<main id="main">

<section><div class="wrap">
<div class="kicker" id="the-record">The record</div>
<h1>What the record shows.</h1>
<p class="lede">This page is the platform's own account of itself: how far the arguments travelled, who actually read them, what people did next, and what did not work. It is kept as advocacy intelligence rather than as a scoreboard, which means the uncomfortable figures are here too.</p>
<p class="imp-updated"><!--IMPACT:UPDATED:START--><!--IMPACT:UPDATED:END--></p>
</div></section>

<section><div class="wrap">
<h2 class="sec" id="who-reads">Who reads it</h2>
<p>Analytics packages count visitors. Most of those visitors are neither people nor readers, so the figure HSREP publishes is the one that survives contact with that fact: how many stayed long enough to have read something.</p>
<!--IMPACT:READERS:START--><!--IMPACT:READERS:END-->
</div></section>

<section><div class="wrap">
<h2 class="sec" id="how-they-arrived">How they arrived</h2>
<p>Where the visits came from since launch. The ordering is worth holding onto, because it does not match the ordering of impressions: the platform that showed the argument to the most people is not the platform that brought the most of them here.</p>
<!--IMPACT:ARRIVAL:START--><!--IMPACT:ARRIVAL:END-->
</div></section>

<section><div class="wrap">
<h2 class="sec" id="read-by-machines">Read by machines</h2>
<p>The least expected finding on this page, and the one with the clearest implication for anyone publishing health evidence now. HSREP is read far more by AI systems than by search engines, and some of those fetches were triggered by a person asking an assistant a question.</p>
<!--IMPACT:MACHINES:START--><!--IMPACT:MACHINES:END-->
</div></section>

<section><div class="wrap">
<h2 class="sec" id="what-people-did">What people did</h2>
<p>Every recorded action since launch, published in full rather than filtered to the flattering ones. The distribution is the useful part: it shows which argument the audience is actually standing next to.</p>
<!--IMPACT:ACTIONS:START--><!--IMPACT:ACTIONS:END-->
</div></section>

<section><div class="wrap">
<h2 class="sec" id="what-did-not-work">What did not work</h2>
<p>An impact page that only reports what succeeded is a brochure. This is the section that makes the rest of the page worth believing.</p>
<!--IMPACT:PARTICIPATION:START--><!--IMPACT:PARTICIPATION:END-->
</div></section>

<section><div class="wrap">
<h2 class="sec" id="season-impact">Season impact</h2>
<p>Each season's campaign data lives on its own hub, where it sits beside the arguments it belongs to. The headline figures are here; the full record, the eleven findings and the per-piece breakdown are one click away.</p>
<!--IMPACT:SEASON1:START--><!--IMPACT:SEASON1:END-->
</div></section>

<section><div class="wrap">
<h2 class="sec" id="methods">Method, and what it cannot tell you</h2>
<p>Site figures come from Google Analytics 4 and Cloudflare on hsraep.org, refreshed from the same dashboard that produces them, so the site and the dashboard cannot disagree. Season 1 campaign figures come from platform-native analytics and are reconciled and documented separately.</p>
<p><a class="btn ghost" href="methodology.html">How 57,274 is counted &rarr;</a></p>
<p>What these numbers cannot tell you. Visitor counts include automated traffic that no filter removes completely, so the datacentre deduction above is a floor and not a ceiling. Engagement time is measured by the browser and stops when a tab is backgrounded. Search Console and Analytics count different things over different windows and are never added together. Audience composition comes from samples in the hundreds and describes who was reached, never a population. Nothing on this page is an experiment: it is one practitioner's observational record, useful for generating hypotheses and not for settling them.</p>
<div class="imp-later">
<p>Reserved, and rendered only once there is something to report:</p>
<ul>
<li>responses on the record, by question</li>
<li>published roundtable syntheses</li>
<li>registrations and participants by affiliation</li>
<li>presentation requests and partnership enquiries</li>
<li>downloads by asset</li>
<li>Season 2 campaign data</li>
</ul>
</div>
</div></section>

</main>"""


SECNAV = ('<nav class="mth-secnav" aria-label="On this page">'
          '<span class="sn-lab">On this page</span>'
          '<a href="#who-reads">Who reads it</a>'
          '<a href="#how-they-arrived">How they arrived</a>'
          '<a href="#read-by-machines">Read by machines</a>'
          '<a href="#what-people-did">What people did</a>'
          '<a href="#what-did-not-work">What did not work</a>'
          '<a href="#season-impact">Season impact</a>'
          '<a href="#methods">Method</a></nav>')


def swap_head(s):
    """Point the shell's identity at this page instead of the donor's."""
    subs = [
        (r'<title>.*?</title>', '<title>Impact, what the record shows - HSREP</title>', 1),
        (r'(<meta name="description" content=")[^"]*(">)', r'\1%s\2' % DESC, 1),
        (r'(<meta property="og:title" content=")[^"]*(">)',
         r'\1Impact, what the record shows\2', 1),
        (r'(<meta name="twitter:title" content=")[^"]*(">)',
         r'\1Impact, what the record shows\2', 1),
        (r'(<meta property="og:description" content=")[^"]*(">)', r'\1%s\2' % DESC, 1),
        (r'(<meta name="twitter:description" content=")[^"]*(">)', r'\1%s\2' % DESC, 1),
        (r'(<meta property="og:url" content="https://hsraep\.org/)[^"]*(">)',
         r'\1impact.html\2', 1),
        (r'(<link rel="canonical" href="https://hsraep\.org/)[^"]*(">)',
         r'\1impact.html\2', 1),
        (r'(og/og-)[a-z0-9-]+(\.png)', r'\1impact\2', 0),
        (r'hsraep\.org/methodology\.html', 'hsraep.org/impact.html', 0),
        (r'"name": "[^"]*- HSREP"', '"name": "Impact, what the record shows - HSREP"', 1),
        (r'("position": 2, "name": ")[^"]*(")', r'\1Impact\2', 1),
    ]
    for pat, rep, count in subs:
        s = re.sub(pat, rep, s, count=count, flags=re.S)
    return s


def build():
    donor = open(os.path.join(ROOT, DONOR), encoding="utf-8").read()
    a = donor.index("<main")
    b = donor.index("</main>") + len("</main>")
    page = donor[:a] + MAIN + donor[b:]
    page = swap_head(page)
    if 'id="hs-impact"' not in page:
        page = page.replace("</head>", CSS, 1)
    # the donor's section bar lists the donor's sections; swap in this page's
    page = re.sub(r'<nav class="mth-secnav".*?</nav>', SECNAV, page, count=1, flags=re.S)
    # and the donor marks its own nav item as current
    hdr = re.search(r"<header[^>]*>.*?</header>", page, re.S)
    if hdr:
        h = re.sub(r'\s*class="here"', '', hdr.group(0))
        h = h.replace('<a href="impact.html">Impact</a>',
                      '<a class="here" href="impact.html">Impact</a>', 1)
        page = page[:hdr.start()] + h + page[hdr.end():]
    dest = os.path.join(ROOT, PAGE)
    old = open(dest, encoding="utf-8").read() if os.path.exists(dest) else None
    if old is not None:
        # keep whatever the renderer has already written between the markers
        for name in ("UPDATED", "READERS", "ARRIVAL", "MACHINES", "ACTIONS",
                     "PARTICIPATION", "SEASON1"):
            m = re.search(r"<!--IMPACT:%s:START-->(.*?)<!--IMPACT:%s:END-->" % (name, name),
                          old, re.S)
            if m and m.group(1):
                page = page.replace(
                    "<!--IMPACT:%s:START--><!--IMPACT:%s:END-->" % (name, name),
                    "<!--IMPACT:%s:START-->%s<!--IMPACT:%s:END-->" % (name, m.group(1), name))
    if page != old:
        open(dest, "w", encoding="utf-8").write(page)
        print("  wrote:", PAGE)
    else:
        print("  already current:", PAGE)


ONE = re.compile(r'<a[^>]*href="[^"]*impact\.html"[^>]*>Impact</a>')
RUN = re.compile(r'(?:<a[^>]*href="[^"]*impact\.html"[^>]*>Impact</a>\s*){2,}')
ART = re.compile(r'<a[^>]*href="([^"]*?)articles\.html"[^>]*>Articles</a>')


def wire():
    """Impact joins the primary nav, the footer, the sitemap and llms.txt.

    Insertion is scoped: the nav link goes inside <header>, the footer link inside
    the Platform column, and the relative prefix is taken from the Articles link on
    the same page, because article and transcript pages link as ../../articles.html
    or /articles.html. An earlier version matched the first Initiative link
    anywhere in the document, which put a second copy in the nav on every run;
    RUN collapses any such duplicates left behind."""
    n = 0
    for dp, dn, fn in os.walk(ROOT):
        if any(x in dp for x in ("/.git", "node_modules", "_archive", "/scripts")):
            continue
        for f in fn:
            if not f.endswith(".html"):
                continue
            path = os.path.join(dp, f)
            s = o = open(path, encoding="utf-8").read()

            s = RUN.sub(lambda m: ONE.search(m.group(0)).group(0), s)   # repair

            hdr = re.search(r"<header[^>]*>.*?</header>", s, re.S)
            if hdr and not ONE.search(hdr.group(0)):
                art = ART.search(hdr.group(0))
                if art:
                    link = '<a href="%simpact.html">Impact</a>' % art.group(1)
                    fixed = hdr.group(0).replace(art.group(0), art.group(0) + link, 1)
                    s = s[:hdr.start()] + fixed + s[hdr.end():]

            i = s.find("<h2>Platform</h2>")
            if i >= 0:
                j = s.find("</div>", i)
                col = s[i:j]
                if not ONE.search(col):
                    m = re.search(r'<a href="([^"]*?)initiative\.html">Initiative</a>', col)
                    if m:
                        fixed = col.replace(
                            m.group(0),
                            '<a href="%simpact.html">Impact</a>' % m.group(1) + m.group(0), 1)
                        s = s[:i] + fixed + s[j:]

            if s != o:
                open(path, "w", encoding="utf-8").write(s)
                n += 1
    print("  nav/footer updated on %d pages" % n)

    sm = os.path.join(ROOT, "sitemap.xml")
    s = open(sm, encoding="utf-8").read()
    if "impact.html" in s:
        print("  sitemap.xml: already listed")
    else:
        # the file's own indentation varies, so anchor on the <loc> and rebuild
        # the surrounding <url> block from what is already there
        m = re.search(r"[ \t]*<url>\s*<loc>https://hsraep\.org/methodology\.html</loc>", s)
        if not m:
            m = re.search(r"[ \t]*<url>\s*<loc>https://hsraep\.org/season-1\.html</loc>", s)
        if not m:
            raise SystemExit("ABORT: could not find an anchor <url> block in sitemap.xml")
        entry = ("  <url><loc>https://hsraep.org/impact.html</loc>"
                 "<changefreq>daily</changefreq><priority>0.8</priority></url>\n")
        s = s[:m.start()] + entry + s[m.start():]
        open(sm, "w", encoding="utf-8").write(s)
        assert "impact.html" in open(sm, encoding="utf-8").read()
        print("  sitemap.xml: impact.html added")

    lt = os.path.join(ROOT, "llms.txt")
    s = open(lt, encoding="utf-8").read()
    if "impact.html" not in s:
        s = s.rstrip() + (
            "\n\n## Impact\n"
            "https://hsraep.org/impact.html\n"
            "The platform's own record: readership (published as engaged readers, not raw "
            "visitor counts, with datacentre traffic deducted and named), how visitors "
            "arrive, AI-crawler retrieval against search, every recorded action, and the "
            "record of what did not work.\n")
        open(lt, "w", encoding="utf-8").write(s)
        print("  llms.txt: Impact section added")
    else:
        print("  llms.txt: already listed")


build()
wire()
print("done")
