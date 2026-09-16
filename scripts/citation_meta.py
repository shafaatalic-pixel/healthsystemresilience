#!/usr/bin/env python3
"""Citation metadata for every article page: Google Scholar (citation_*) and
Dublin Core (DC.*) meta tags, generated from the page's own Article JSON-LD,
its canonical link and its PDF. Idempotent: writes between <!--CITE:START-->
and <!--CITE:END--> in <head>, replacing any earlier block.

DOIs: if data/dois.json maps a slug to a DOI, citation_doi and DC.identifier
carry it and the Article JSON-LD gets an "identifier" (also "sameAs").

  python3 scripts/citation_meta.py            # rewrite all article pages
  python3 scripts/citation_meta.py --check    # print what would be written
"""
import glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOIS = os.path.join(ROOT, "data", "dois.json")
OUTLETS = {"thedailystar.net": "The Daily Star", "easternecho.com": "The Eastern Echo"}
CHECK = "--check" in sys.argv

def esc(s): return html.escape(s, quote=True)

def article_meta(path):
    s = open(path, encoding="utf-8").read()
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    art = None
    for x in ld:
        try:
            j = json.loads(x)
        except Exception:
            continue
        if isinstance(j, dict) and j.get("@type") == "Article":
            art = j; break
    if not art:
        return None, s
    canon = re.search(r'rel="canonical" href="([^"]+)"', s)
    pdf = re.search(r'href="([^"]+\.pdf)"', s)
    ext = re.findall(r'href="(https?://(?:www\.)?(thedailystar\.net|easternecho\.com)[^"]*)"', s)
    outlet_url, outlet = (ext[0][0], OUTLETS[ext[0][1]]) if ext else ("", "")
    slug = os.path.basename(os.path.dirname(path))
    d = art.get("datePublished", "")
    author = art.get("author", {})
    authors = [a.get("name") for a in (author if isinstance(author, list) else [author]) if a.get("name")]
    base = canon.group(1).rsplit("/", 1)[0] + "/" if canon else ""
    pdf_url = (pdf.group(1) if pdf and pdf.group(1).startswith("http") else base + pdf.group(1)) if pdf else ""
    return dict(slug=slug, title=art.get("headline", ""), desc=art.get("description", ""),
                date=d, authors=authors, url=canon.group(1) if canon else "", pdf=pdf_url,
                outlet=outlet, outlet_url=outlet_url, modified=art.get("dateModified", "")), s

def tags(m, doi):
    t = []
    add = lambda n, v: v and t.append('<meta name="%s" content="%s">' % (n, esc(v)))
    add("citation_title", m["title"])
    for a in m["authors"]: add("citation_author", a)
    add("citation_publication_date", m["date"].replace("-", "/"))
    add("citation_online_date", m["date"].replace("-", "/"))
    add("citation_journal_title", m["outlet"] or "HSREP")
    add("citation_publisher", "HSREP, Health System Resilience & Economic Protection")
    add("citation_language", "en")
    add("citation_abstract_html_url", m["url"])
    add("citation_fulltext_html_url", m["url"])
    add("citation_pdf_url", m["pdf"])
    add("citation_doi", doi)
    add("DC.title", m["title"])
    for a in m["authors"]: add("DC.creator", a)
    add("DC.date", m["date"])
    add("DC.description", m["desc"])
    add("DC.publisher", "HSREP")
    add("DC.identifier", ("https://doi.org/" + doi) if doi else m["url"])
    add("DC.type", "Text")
    add("DC.format", "text/html")
    add("DC.language", "en")
    add("DC.rights", "https://hsraep.org/terms.html")
    if m["outlet_url"]: add("DC.relation", m["outlet_url"])
    return "<!--CITE:START-->" + "".join(t) + "<!--CITE:END-->"

def inject_ld_identifier(s, doi):
    """Add identifier/sameAs for the DOI to the Article JSON-LD, once."""
    def rep(mo):
        raw = mo.group(1)
        try: j = json.loads(raw)
        except Exception: return mo.group(0)
        if not (isinstance(j, dict) and j.get("@type") == "Article"): return mo.group(0)
        j["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI", "value": doi}
        same = set(j.get("sameAs", []) if isinstance(j.get("sameAs"), list) else ([j["sameAs"]] if j.get("sameAs") else []))
        same.add("https://doi.org/" + doi); j["sameAs"] = sorted(same)
        return '<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False) + '</script>'
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', rep, s, count=1, flags=re.S)

def main():
  dois = json.load(open(DOIS)) if os.path.exists(DOIS) else {}
  n = 0
  for path in sorted(glob.glob(os.path.join(ROOT, "articles", "*", "*.html"))):
      if path.endswith("index.html"): continue
      m, s = article_meta(path)
      if not m: continue
      doi = dois.get(m["slug"], "")
      block = tags(m, doi)
      if "<!--CITE:START-->" in s:
          new = re.sub(r"<!--CITE:START-->.*?<!--CITE:END-->", lambda _: block, s, flags=re.S)
      else:
          new = re.sub(r'(<link rel="canonical" href="[^"]+">)', lambda mo: mo.group(1) + block, s, count=1)
      if doi: new = inject_ld_identifier(new, doi)
      if CHECK:
          print(m["slug"], "|", m["outlet"] or "HSREP", "|", m["date"], "| doi:", doi or "-"); continue
      if new != s:
          open(path, "w", encoding="utf-8").write(new); n += 1
  if not CHECK: print("citation meta written to %d page(s)" % n)

if __name__ == "__main__":
    main()
