#!/usr/bin/env python3
"""The visible "Cite this piece" block on every article page that has a DOI.

The citation_meta tags are for machines; this is the line a reader can copy.
Written between <!--CITEBLOCK:START--> and <!--CITEBLOCK:END--> as the first
child of .pkg, so it sits directly under the article and above Engage.
Idempotent: re-running replaces the block. Slugs with no DOI are skipped.

  python3 scripts/cite_block.py
  python3 scripts/cite_block.py --check
"""
import glob, html as H, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from citation_meta import article_meta, ROOT  # noqa: E402
from record_sheet import apa_date  # noqa: E402
import people  # noqa: E402

DOIS = os.path.join(ROOT, "data", "dois.json")
CHECK = "--check" in sys.argv
CSS = (
    ".citebox{margin:0 0 20px;background:#fff;border:1px solid var(--line,#DCE3EA);"
    "border-radius:14px;padding:22px 26px}"
    ".citebox .ck{font-family:'IBM Plex Mono','IBM Plex Mono Fallback',monospace;font-size:11px;"
    "letter-spacing:.16em;text-transform:uppercase;color:var(--coral,#C43C25);margin-bottom:10px}"
    ".citebox p{margin:0;font-size:15px;line-height:1.62}"
    ".citebox p a{color:inherit;text-decoration:underline;text-underline-offset:2px}"
    ".citebox .clic{margin-top:9px;font-size:13px;line-height:1.55;color:#5F6B78}"
    ".citerow{display:flex;flex-wrap:wrap;gap:9px;margin-top:15px}"
    ".citerow a,.citerow button{font:500 12px/1 'IBM Plex Mono','IBM Plex Mono Fallback',monospace;"
    "letter-spacing:.07em;text-transform:uppercase;color:#1C2E4A;background:#F4F7FA;"
    "border:1px solid var(--line,#DCE3EA);border-radius:999px;padding:9px 14px;cursor:pointer;"
    "text-decoration:none;transition:background .15s,color .15s,border-color .15s}"
    ".citerow a:hover,.citerow button:hover{background:#1C2E4A;color:#fff;border-color:#1C2E4A}"
    "@media(max-width:600px){.citebox{padding:20px}.citebox p{font-size:14px}}"
)
JS = ("var t=this.closest('.citebox').querySelector('.cref').innerText;"
      "var b=this;navigator.clipboard.writeText(t).then(function(){"
      "b.textContent='Copied';setTimeout(function(){b.textContent='Copy citation'},1800)})")


def block(m, doi):
    rid = doi.rsplit(".", 1)[-1]
    venue = m["outlet"] or "HSREP, Health System Resilience &amp; Economic Protection"
    url = "https://doi.org/" + doi
    names = people.reference_names(m["authors"] or ["Md Shafaat Ali Choyon"])
    cite = ('%s (%s). %s. <i>%s</i>. <a href="%s">%s</a>' %
            (H.escape(names), apa_date(m["date"]), H.escape(m["title"]), venue, url, url))
    # HSREP's own pieces carry an open licence; outlet pieces do not (their
    # publisher holds those rights), so the line only appears where it is true.
    lic = ("" if m["outlet"] else
           '<p class="clic">Licence: <a href="https://creativecommons.org/licenses/by/4.0/" '
           'target="_blank" rel="noopener license">CC BY 4.0</a> &mdash; copy, translate, adapt and '
           'reuse it, including commercially, with attribution and a note of any changes.</p>')
    return ("<!--CITEBLOCK:START--><style id=\"hs-cite\">%s</style>"
            "<div class=\"citebox\"><div class=\"ck\">Cite this piece</div>"
            "<p class=\"cref\">%s</p>%s<div class=\"citerow\">"
            "<button type=\"button\" onclick=\"%s\">Copy citation</button>"
            "<a href=\"%s\" target=\"_blank\" rel=\"noopener\">View the DOI record &#8599;</a>"
            "<a href=\"https://zenodo.org/records/%s/export/bibtex\" target=\"_blank\" rel=\"noopener\">BibTeX</a>"
            "<a href=\"https://zenodo.org/records/%s/export/csl\" target=\"_blank\" rel=\"noopener\">RIS / CSL</a>"
            "</div></div><!--CITEBLOCK:END-->") % (CSS, cite, lic, JS, url, rid, rid)


def main():
    dois = json.load(open(DOIS)) if os.path.exists(DOIS) else {}
    n = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "articles", "*", "*.html"))):
        if path.endswith("index.html"):
            continue
        m, s = article_meta(path)
        if not m:
            continue
        doi = dois.get(m["slug"])
        if not doi:
            print("  no DOI for", m["slug"]); continue
        s = re.sub(r"<!--CITEBLOCK:START-->.*?<!--CITEBLOCK:END-->", "", s, flags=re.S)
        anchor = '<div class="pkg">'
        if anchor not in s:
            print("  no .pkg container in", m["slug"]); continue
        out = s.replace(anchor, anchor + block(m, doi), 1)
        if CHECK:
            print("  would write", m["slug"], doi); continue
        open(path, "w", encoding="utf-8").write(out)
        n += 1
    print("cite block written to %d page(s)" % n)


if __name__ == "__main__":
    main()
