#!/usr/bin/env python3
"""Rebuild assets/search-index.json from the published pages.

Run from the website root after any content change inside <main>:
    python3 scripts/mkindex.py
Chrome changes (header, footer, nav) never need a rebuild; the corpus is
scoped to <main> with scripts, styles, forms, media and navigation removed.

Document fields (read by search.html): u url, t title, k kind, kl kind label,
w weight (lower sorts first on ties), s section label, d meta description,
h headings joined by " · ", b body text, p date (JSON-LD dateModified, or
datePublished for articles) or "".
"""
import json, os, re, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "search-index.json")

# Out of the corpus: error page, the results page itself, and unlisted pages.
SKIP = {"404.html", "search.html", "roundtable-console.html"}

# path prefix or file -> (kind, label, weight, section)
KINDS = [
    ("articles/", ("article", "Article", 0, "Season 1 article")),
    ("transcripts/", ("transcript", "Transcript", 3, "Film transcript")),
    ("index.html", ("platform", "Platform", 4, "Home")),
    ("about.html", ("platform", "Platform", 4, "About")),
    ("articles.html", ("platform", "Platform", 4, "Article library")),
    ("media.html", ("platform", "Platform", 4, "Media and brand kit")),
    ("identity.html", ("platform", "Platform", 4, "Identity")),
    ("roundtable.html", ("platform", "Platform", 4, "Roundtable")),
    ("season-1.html", ("season", "Season", 1, "Season 1")),
    ("initiative.html", ("initiative", "Initiative", 1, "Prevention Adoption Initiative")),
    ("initiative-next.html", ("initiative", "Initiative", 1, "Initiative roadmap")),
    ("dashboard-demo.html", ("initiative", "Initiative", 1, "Dashboard demonstration")),
    ("impact.html", ("evidence", "Evidence", 2, "Impact")),
    ("methodology.html", ("evidence", "Evidence", 2, "Methodology")),
    ("corrections.html", ("evidence", "Evidence", 2, "Corrections log")),
    ("films.html", ("film", "Films", 2, "Films and explainers")),
    ("privacy.html", ("policy", "Policy", 5, "Privacy")),
    ("terms.html", ("policy", "Policy", 5, "Terms")),
    ("accessibility.html", ("policy", "Policy", 5, "Accessibility")),
]

STRIP_BLOCKS = ["script", "style", "noscript", "svg", "template", "header", "footer",
                "form", "video", "audio", "iframe", "canvas", "nav"]


def strip_blocks(s):
    for tag in STRIP_BLOCKS:
        s = re.sub(r"<%s\b[^>]*>[\s\S]*?</%s>" % (tag, tag), " ", s, flags=re.I)
    s = re.sub(r"<!--[\s\S]*?-->", " ", s)
    s = re.sub(r'<[^>]+class="[^"]*\bbreadcrumb[^"]*"[^>]*>[\s\S]*?</(ol|ul|div|nav)>', " ", s, flags=re.I)
    return s


def text(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def kind_for(rel):
    for key, v in KINDS:
        if rel == key or (key.endswith("/") and rel.startswith(key)):
            return v
    return ("platform", "Platform", 4, "Page")


def meta(s, name):
    m = re.search(r'<meta\s+(?:name|property)="%s"\s+content="([^"]*)"' % re.escape(name), s, re.I)
    if not m:
        m = re.search(r'<meta\s+content="([^"]*)"\s+(?:name|property)="%s"' % re.escape(name), s, re.I)
    return html.unescape(m.group(1)).strip() if m else ""


def jsonld_date(s, keys):
    for k in keys:
        m = re.search(r'"%s"\s*:\s*"(\d{4}-\d{2}-\d{2})' % k, s)
        if m:
            return m.group(1)
    return ""


def doc(path, rel):
    s = open(path, encoding="utf-8").read()
    if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', s, re.I) and rel != "dashboard-demo.html":
        return None
    k, kl, w, sec = kind_for(rel)
    t = text(re.search(r"<title>([\s\S]*?)</title>", s, re.I).group(1)) if re.search(r"<title>", s, re.I) else rel
    t = re.sub(r"\s*[—|·\-]\s*HSREP.*$", "", t).strip() or t
    t = re.sub(r"^Transcript:\s*", "", t)
    d = meta(s, "description")
    body = strip_blocks(s)
    m = re.search(r"<main\b[^>]*>([\s\S]*?)</main>", body, re.I)
    main = m.group(1) if m else re.sub(r"[\s\S]*?<body[^>]*>", "", body)
    heads = [text(h) for h in re.findall(r"<h[1-3]\b[^>]*>([\s\S]*?)</h[1-3]>", main, re.I)]
    heads = [h for h in heads if h]
    p = jsonld_date(s, ["datePublished"] if k == "article" else ["dateModified"])
    return {"u": "/" + rel, "t": t, "k": k, "kl": kl, "w": w, "s": sec, "d": d,
            "h": " · ".join(heads), "b": text(main), "p": p}


def main():
    docs = []
    for sub in ("", "articles", "transcripts"):
        base = os.path.join(ROOT, sub) if sub else ROOT
        for dp, dns, fns in os.walk(base):
            if sub == "" and dp != ROOT:
                continue
            dns[:] = [x for x in dns if not x.startswith((".", "_"))]
            for fn in sorted(fns):
                if not fn.endswith(".html"):
                    continue
                rel = os.path.relpath(os.path.join(dp, fn), ROOT).replace(os.sep, "/")
                if rel in SKIP or rel.startswith("first-draft/"):
                    continue
                d = doc(os.path.join(dp, fn), rel)
                if d:
                    docs.append(d)
    docs.sort(key=lambda x: x["u"])
    out = {"v": 1, "n": len(docs), "docs": docs}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=True, separators=(",", ": "))
    print("%d documents -> %s" % (len(docs), os.path.relpath(OUT, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
