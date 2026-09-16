#!/usr/bin/env python3
"""Mint a DOI for each article by depositing a record on Zenodo, then write
data/dois.json and refresh the citation meta tags.

Needs a Zenodo personal access token with the deposit:write and deposit:actions
scopes, exported by the person who owns the account (never pasted here):

  export ZENODO_TOKEN=...            # from zenodo.org -> Applications -> Personal access tokens
  export ORCID=0000-0000-0000-0000   # optional, attached to the author record
  python3 scripts/zenodo_deposit.py --dry-run          # show every record, deposit nothing
  python3 scripts/zenodo_deposit.py --sandbox          # rehearse on sandbox.zenodo.org (separate token)
  python3 scripts/zenodo_deposit.py                    # mint for real
  python3 scripts/zenodo_deposit.py --only when-the-ground-shakes

Rights rule, deliberately conservative: only the Special Report (HSREP's own,
cleared for full reproduction) is deposited with its PDF, under CC BY 4.0.
Pieces first published by The Daily Star or The Eastern Echo are deposited as
metadata-only records that point to the HSREP page and to the outlet, so the
DOI is real and citable without redistributing another publisher's text.
Records already listed in data/dois.json are skipped, so the script is safe to
re-run.
"""
import json, os, re, subprocess, sys, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from citation_meta import article_meta, ROOT  # noqa: E402

DRY = "--dry-run" in sys.argv
SANDBOX = "--sandbox" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
BASE = "https://sandbox.zenodo.org/api" if SANDBOX else "https://zenodo.org/api"
TOKEN = os.environ.get("ZENODO_TOKEN", "")
ORCID = os.environ.get("ORCID", "").strip()
DOIS = os.path.join(ROOT, "data", "dois.json")
SUBJECTS = ["health system resilience", "economic protection", "public health", "health policy"]
COUNTRY = {"The Daily Star": "Bangladesh", "The Eastern Echo": "United States", "": "Bangladesh"}

def api(method, path, data=None, raw=None, ctype="application/json"):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    body = None
    if data is not None:
        body = json.dumps(data).encode(); req.add_header("Content-Type", ctype)
    elif raw is not None:
        body = raw; req.add_header("Content-Type", "application/octet-stream")
    try:
        with urllib.request.urlopen(req, body, timeout=120) as r:
            t = r.read().decode()
            return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        sys.exit("%s %s -> HTTP %s\n%s" % (method, path, e.code, e.read().decode()[:1500]))

def record_for(m):
    with_file = not m["outlet"]  # HSREP's own piece: deposit the PDF
    creator = {"person_or_org": {"type": "personal", "given_name": "Md Shafaat Ali", "family_name": "Choyon"},
               "affiliations": [{"name": "HSREP, Health System Resilience & Economic Protection"}]}
    if ORCID:
        creator["person_or_org"]["identifiers"] = [{"scheme": "orcid", "identifier": ORCID}]
    desc = "<p>%s</p>" % m["desc"]
    if m["outlet"]:
        desc += ("<p>First published by %s on %s. The HSREP page holds the argument as an advocacy package: "
                 "summary, sources, media and the professional discussion under it. This record identifies that "
                 "package; the publisher's version of record is at the outlet link below.</p>") % (m["outlet"], m["date"])
    else:
        desc += "<p>An HSREP Special Report, cleared for full reproduction with attribution.</p>"
    related = [{"identifier": m["url"], "scheme": "url", "relation_type": {"id": "isidenticalto"},
                "resource_type": {"id": "publication-article"}}]
    if m["outlet_url"]:
        related.append({"identifier": m["outlet_url"], "scheme": "url", "relation_type": {"id": "ispublishedin"},
                        "resource_type": {"id": "publication-article"}})
    meta = {
        "resource_type": {"id": "publication-article"},
        "title": m["title"],
        "creators": [creator],
        "publication_date": m["date"],
        "publisher": m["outlet"] or "HSREP",
        "description": desc,
        "languages": [{"id": "eng"}],
        "subjects": [{"subject": s} for s in SUBJECTS + [COUNTRY.get(m["outlet"], "")] if s],
        "related_identifiers": related,
        "version": "1.0",
    }
    if with_file:
        meta["rights"] = [{"id": "cc-by-4.0"}]
    return {"access": {"record": "public", "files": "public"}, "files": {"enabled": with_file}, "metadata": meta}, with_file

dois = json.load(open(DOIS)) if os.path.exists(DOIS) else {}
if not DRY and not TOKEN:
    sys.exit("ZENODO_TOKEN is not set. Export it in this shell first (see the docstring).")

import glob
for path in sorted(glob.glob(os.path.join(ROOT, "articles", "*", "*.html"))):
    if path.endswith("index.html"): continue
    m, _ = article_meta(path)
    if not m or (ONLY and m["slug"] != ONLY): continue
    if m["slug"] in dois:
        print("skip  ", m["slug"], "already", dois[m["slug"]]); continue
    rec, with_file = record_for(m)
    pdf_local = os.path.join(os.path.dirname(path), os.path.basename(m["pdf"]))
    print(("DRY   " if DRY else "mint  ") + m["slug"], "| file" if with_file else "| metadata-only", "|", m["outlet"] or "HSREP")
    if DRY:
        print(json.dumps(rec["metadata"], indent=1, ensure_ascii=False)[:900], "\n"); continue
    draft = api("POST", "/records", rec)
    rid = draft["id"]
    if with_file:
        key = os.path.basename(pdf_local)
        api("POST", "/records/%s/draft/files" % rid, [{"key": key}])
        api("PUT", "/records/%s/draft/files/%s/content" % (rid, key), raw=open(pdf_local, "rb").read())
        api("POST", "/records/%s/draft/files/%s/commit" % (rid, key))
    pub = api("POST", "/records/%s/draft/actions/publish" % rid)
    doi = pub.get("pids", {}).get("doi", {}).get("identifier") or pub.get("doi")
    if not doi:
        sys.exit("published %s but no DOI in the response: %s" % (rid, json.dumps(pub)[:600]))
    dois[m["slug"]] = doi
    os.makedirs(os.path.dirname(DOIS), exist_ok=True)
    json.dump(dois, open(DOIS, "w"), indent=2); print("      ", doi, "->", pub.get("links", {}).get("self_html", ""))

if not DRY:
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "citation_meta.py")], check=True)
    print("done. commit data/dois.json and the article pages, push, purge.")
