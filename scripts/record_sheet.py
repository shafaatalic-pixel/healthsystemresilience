#!/usr/bin/env python3
"""One-page HSREP record sheet: the file deposited with each article's DOI.

Zenodo does not accept metadata-only records ("A record must always have as
minimum one file associated with it" - support.zenodo.org), so every deposit
needs a file. For pieces first published by an outlet we deposit HSREP's own
record sheet rather than the publisher's text: title, byline, where it first
appeared, the In Brief summary already published on the HSREP page, both links,
the citation and the rights note. It does not reproduce the article.

  python3 scripts/record_sheet.py                    # build every sheet
  python3 scripts/record_sheet.py --only <slug>
  python3 scripts/record_sheet.py --only <slug> --doi 10.5281/zenodo.123

Rendered with headless Chrome, one Letter page, using the site's own fonts.
"""
import glob, html as H, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from citation_meta import article_meta, ROOT  # noqa: E402
import people  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = os.path.join(ROOT, "build", "record-sheets")
MONTHS = ("January February March April May June July August September "
          "October November December").split()


def pretty(d):
    try:
        y, m, dd = (d.split("T")[0].split("-") + ["1", "1"])[:3]
        return "%d %s %s" % (int(dd), MONTHS[int(m) - 1], y)
    except Exception:
        return d


def apa_date(d):
    try:
        y, m, dd = (d.split("T")[0].split("-") + ["1", "1"])[:3]
        return "%s, %s %d" % (y, MONTHS[int(m) - 1], int(dd))
    except Exception:
        return d


initials = people.initials  # kept for importers


def inbrief(s):
    """The In Brief bullets and reading time already published on the page."""
    m = re.search(r'class="inbrief".*?<ul>(.*?)</ul>', s, re.S)
    items = []
    if m:
        for li in re.findall(r"<li>(.*?)</li>", m.group(1), re.S):
            t = re.sub(r"<(?!/?(?:b|strong|i|em)\b)[^>]*>", "", li)
            items.append(re.sub(r"\s+", " ", t).strip())
    r = re.search(r'class="ib-read">([^<]+)<', s)
    return items, (r.group(1).strip() if r else "")


def kicker(s):
    m = re.search(r'class="kicker"[^>]*>(.*?)</div>', s, re.S)
    return H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()) if m else ""


def deck(s):
    m = re.search(r'class="(?:deck|standfirst|sub)"[^>]*>(.*?)</', s, re.S)
    return H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()) if m else ""


def by_html(names):
    """Name in bold, credentials plain, role in grey — one line per byline."""
    out = []
    for n in names:
        p = people.person(n)
        s = "<b>%s</b>" % H.escape(p["name"])
        if p["credentials"]:
            s += ", " + H.escape(p["credentials"])
        if p["role"]:
            s += ' <span>&middot; %s</span>' % H.escape(p["role"])
        out.append(s)
    return " &nbsp; ".join(out)


def sheet_html(m, items, read, doi, kick=""):
    a = ROOT + "/assets"
    names = m["authors"] or ["Md Shafaat Ali Choyon"]
    cite = "%s (%s). %s. %s." % (people.reference_names(names), apa_date(m["date"]), m["title"],
                                 m["outlet"] or people.HSREP)
    if doi:
        cite += " https://doi.org/%s" % doi
    first = ("%s, %s" % (m["outlet"], pretty(m["date"]))) if m["outlet"] else \
            ("HSREP, %s" % pretty(m["date"]))
    bullets = "".join("<li>%s</li>" % x for x in items)
    rows = [("First published", H.escape(first))]
    if m["outlet_url"]:
        rows.append(("Publisher's version", '<a href="%s">%s</a>' % (m["outlet_url"], H.escape(m["outlet_url"]))))
    rows.append(("HSREP page", '<a href="%s">%s</a>' % (m["url"], H.escape(m["url"]))))
    if read:
        rows.append(("Length", H.escape(read)))
    meta = "".join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows)
    return """<!doctype html><html lang="en"><meta charset="utf-8"><title>%(title)s</title>
<style>
@font-face{font-family:Spectral;src:url('%(a)s/fonts/spectral-600-38929e98.woff2')format('woff2');font-weight:600}
@font-face{font-family:Spectral;src:url('%(a)s/fonts/spectral-400-b68564de.woff2')format('woff2');font-weight:400}
@font-face{font-family:Spectral;src:url('%(a)s/fonts/spectral-400i-839c9455.woff2')format('woff2');font-weight:400;font-style:italic}
@font-face{font-family:Inter;src:url('%(a)s/fonts/inter-var-1dc044f4.woff2')format('woff2');font-weight:100 900}
@font-face{font-family:Plex;src:url('%(a)s/fonts/ibm-plex-mono-500-3a2668b9.woff2')format('woff2');font-weight:500}
@page{size:Letter;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:8.5in;height:11in}
body{font-family:Inter,system-ui,sans-serif;color:#1C2E4A;font-size:10.5pt;line-height:1.5;
 padding:0.72in 0.82in 0.62in;-webkit-print-color-adjust:exact;print-color-adjust:exact;position:relative}
a{color:#1C2E4A;text-decoration:none;border-bottom:.5pt solid #C6D2DE}
.top{display:flex;align-items:center;gap:9px;padding-bottom:9px;border-bottom:1.6pt solid #1C2E4A}
.top img{width:26px;height:26px}
.wm{font-family:Spectral,Georgia,serif;font-weight:600;font-size:13pt;letter-spacing:.01em}
.wm small{display:block;font-family:Inter,sans-serif;font-weight:450;font-size:6.6pt;letter-spacing:.09em;
 text-transform:uppercase;color:#5F6B78;margin-top:1px}
.kind{margin-left:auto;font-family:Plex,monospace;font-size:7pt;letter-spacing:.14em;text-transform:uppercase;color:#C43C25}
.kick{font-family:Plex,monospace;font-size:7pt;letter-spacing:.13em;text-transform:uppercase;color:#5F6B78;margin-top:26px}
h1{font-family:Spectral,Georgia,serif;font-weight:600;font-size:21pt;line-height:1.16;margin:7px 0 0;letter-spacing:-.005em}
.deck{font-family:Spectral,Georgia,serif;font-style:italic;font-size:11.5pt;color:#46566B;margin-top:9px;max-width:6.2in}
.by{margin-top:14px;padding-top:9px;border-top:.6pt solid #DCE3EA;font-size:9.5pt}
.by b{font-weight:600}.by span{color:#5F6B78}
h2{font-family:Plex,monospace;font-size:7pt;letter-spacing:.15em;text-transform:uppercase;color:#C43C25;
 font-weight:500;margin:22px 0 8px}
ul{list-style:none}
li{position:relative;padding-left:15px;margin-bottom:6px;font-size:10pt;line-height:1.45}
li:before{content:"";position:absolute;left:0;top:.52em;width:5px;height:5px;background:#F26D5A;border-radius:50%%}
li b{font-weight:600}
table{width:100%%;border-collapse:collapse;font-size:9pt}
th{text-align:left;font-family:Plex,monospace;font-size:7pt;letter-spacing:.09em;text-transform:uppercase;
 color:#5F6B78;font-weight:500;width:1.55in;padding:4.5px 0;vertical-align:top}
td{padding:4.5px 0;vertical-align:top;overflow-wrap:anywhere;word-break:normal;font-size:8.6pt}
tr+tr th,tr+tr td{border-top:.5pt solid #EDF1F5}
.cite{margin-top:8px;background:#F4F7FA;border-left:2.2pt solid #1C2E4A;padding:11px 13px;
 font-size:9pt;line-height:1.5}
.cite .lbl{font-family:Plex,monospace;font-size:6.8pt;letter-spacing:.13em;text-transform:uppercase;
 color:#5F6B78;display:block;margin-bottom:4px}
.note{margin-top:16px;font-size:8.2pt;line-height:1.5;color:#5F6B78;max-width:6.1in}
.foot{position:absolute;left:.82in;right:.82in;bottom:.5in;display:flex;gap:12px;
 border-top:.6pt solid #DCE3EA;padding-top:7px;font-family:Plex,monospace;font-size:7pt;
 letter-spacing:.06em;color:#5F6B78}
.foot .r{margin-left:auto}
.doi{color:#1C2E4A}
</style>
<div class="top"><img src="%(a)s/crest.png" alt=""><div class="wm">HSREP<small>Health System Resilience &amp; Economic Protection</small></div><div class="kind">Record sheet</div></div>
%(kick)s<h1>%(title)s</h1>
%(deck)s
<div class="by">%(by)s</div>
<h2>In brief</h2>
<ul>%(bullets)s</ul>
<h2>The record</h2>
<table>%(meta)s</table>
<div class="cite"><span class="lbl">Cite as</span>%(cite)s</div>
<p class="note">%(note)s</p>
<div class="foot"><div>%(doiline)s</div><div class="r">hsraep.org</div></div>
</html>""" % dict(
        a="file://" + a.replace(" ", "%20"),
        kick=('<div class="kick">%s</div>' % H.escape(kick)) if kick else "",
        title=H.escape(m["title"]),
        deck=('<p class="deck">%s</p>' % H.escape(m["desc"])) if m["desc"] else "",
        by=by_html(names), bullets=bullets, meta=meta, cite=H.escape(cite),
        note=("This record sheet is HSREP's own summary of the piece, published under CC BY 4.0. "
              "It does not reproduce the article. The version of record is the publisher's, at the link above."
              if m["outlet"] else
              "Published by HSREP under CC BY 4.0. The full text is deposited with this record."),
        doiline=('DOI <span class="doi">%s</span>' % H.escape(doi)) if doi else "HSREP record sheet",
    )


def build(slug=None, doi="", quiet=False):
    os.makedirs(OUT, exist_ok=True)
    made = []
    for path in sorted(glob.glob(os.path.join(ROOT, "articles", "*", "*.html"))):
        if path.endswith("index.html"):
            continue
        m, s = article_meta(path)
        if not m or (slug and m["slug"] != slug):
            continue
        items, read = inbrief(s)
        if not m["desc"]:
            m["desc"] = deck(s)
        if not items:
            print("  no In Brief bullets on", m["slug"], "- sheet would be thin"); continue
        tmp = os.path.join(ROOT, ".sheet-%s.html" % m["slug"])
        pdf = os.path.join(OUT, "%s--record.pdf" % m["slug"])
        open(tmp, "w", encoding="utf-8").write(sheet_html(m, items, read, doi, kicker(s)))
        r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                            "--virtual-time-budget=3000", "--print-to-pdf=" + pdf,
                            "file://" + tmp.replace(" ", "%20")],
                           capture_output=True, text=True)
        os.remove(tmp)
        if not os.path.exists(pdf):
            sys.exit("chrome failed for %s\n%s" % (m["slug"], r.stderr[-800:]))
        made.append(pdf)
        if not quiet:
            print("  sheet %-44s %6d bytes" % (m["slug"], os.path.getsize(pdf)))
    return made


if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    doi = sys.argv[sys.argv.index("--doi") + 1] if "--doi" in sys.argv else ""
    build(only, doi)
    print("written to", OUT)
