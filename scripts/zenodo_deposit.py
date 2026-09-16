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

Rights rule, deliberately conservative. Zenodo does not accept metadata-only
records ("A record must always have as minimum one file associated with it" -
support.zenodo.org/help/en-gb/1-upload-deposit/36), so every deposit carries a
file. The Special Report, HSREP's own and cleared for full reproduction, is
deposited with its full-text PDF. Pieces first published by The Daily Star or
The Eastern Echo are deposited with an HSREP record sheet instead: one page of
HSREP's own summary, both links and the citation, which does not reproduce the
publisher's text. Both under CC BY 4.0, which covers what is deposited, not the
publisher's version of record. Each DOI is reserved before the sheet is built,
so the sheet prints its own DOI.
Records already listed in data/dois.json are skipped, so the script is safe to
re-run.
"""
import json, os, re, subprocess, sys, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from citation_meta import article_meta, ROOT  # noqa: E402
import record_sheet, people  # noqa: E402

COMMUNITY = "hsrep"  # zenodo.org/communities/hsrep

DRY = "--dry-run" in sys.argv
SANDBOX = "--sandbox" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
BASE = "https://sandbox.zenodo.org/api" if SANDBOX else "https://zenodo.org/api"
TOKEN = os.environ.get("ZENODO_TOKEN", "")
ORCID = os.environ.get("ORCID", "").strip()
DOIS = os.path.join(ROOT, "data", "dois.json")
SUBJECTS = ["health system resilience", "economic protection", "public health", "health policy"]
COUNTRY = {"The Daily Star": "Bangladesh", "The Eastern Echo": "United States", "": "Bangladesh"}

def api(method, path, data=None, raw=None, ctype="application/json", soft=False):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.inveniordm.v1+json")
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
        if soft:
            return {"_error": e.code, "_body": e.read().decode()[:300]}
        sys.exit("%s %s -> HTTP %s\n%s" % (method, path, e.code, e.read().decode()[:1500]))

def community_submit(rid):
    """Put the published record in the HSREP community.

    Submitting creates an inclusion request; accepting it needs the account that
    owns the community. If the token cannot accept, the request is left open and
    waits at zenodo.org/me/requests, so nothing is lost either way.
    """
    r = api("POST", "/records/%s/communities" % rid, {"communities": [{"id": COMMUNITY}]}, soft=True)
    if r.get("_error"):
        print("       community: not submitted (%s) — add it at zenodo.org/communities/%s" % (r["_error"], COMMUNITY))
        return
    ids = [(p.get("request") or {}).get("id") for p in (r.get("processed") or []) if isinstance(p, dict)]
    for q in [x for x in ids if x]:
        a = api("POST", "/requests/%s/actions/accept" % q, {}, soft=True)
        if a.get("_error"):
            print("       community: request open, accept it at zenodo.org/me/requests")
        else:
            print("       community: accepted into %s" % COMMUNITY)

def record_for(m):
    with_file = not m["outlet"]  # HSREP's own piece: deposit the PDF
    names = m["authors"] or ["Md Shafaat Ali Choyon"]
    creators = people.creators(names, fallback_orcid=ORCID)
    missing = [n for n in names if not people.person(n)["orcid"]] if not ORCID else []
    if missing:
        print("      warning: no ORCID on file for %s — add them to data/authors.json" % ", ".join(missing))
    desc = "<p>%s</p>" % m["desc"]
    if m["outlet"]:
        desc += ("<p>First published by %s on %s. The HSREP page holds the argument as an advocacy package: "
                 "summary, sources, media and the professional discussion under it. This record identifies that "
                 "package; the publisher's version of record is at the outlet link below. The file deposited here "
                 "is HSREP's one-page record sheet, not the article: title, byline, where it first appeared, the "
                 "published summary, both links and the citation.</p>"
                 "<p>Published commentary, not a peer-reviewed article.</p>") % (m["outlet"], m["date"])
    else:
        desc += "<p>An HSREP Special Report, cleared for full reproduction with attribution.</p>"
    rel_type = {"id": "publication-report" if not m["outlet"] else "publication-other"}
    related = [{"identifier": m["url"], "scheme": "url", "relation_type": {"id": "isidenticalto"},
                "resource_type": rel_type}]
    if m["outlet_url"]:
        related.append({"identifier": m["outlet_url"], "scheme": "url", "relation_type": {"id": "ispublishedin"},
                        "resource_type": rel_type})
    meta = {
        # Not "publication-article": Zenodo renders that as "Journal article",
        # and none of this is peer reviewed. Outlet commentary is Other; HSREP's
        # own long-form is Report.
        "resource_type": {"id": "publication-report" if with_file else "publication-other"},
        "title": m["title"],
        "creators": creators,
        "publication_date": m["date"],
        "publisher": m["outlet"] or "HSREP",
        "description": desc,
        "languages": [{"id": "eng"}],
        "subjects": [{"subject": s} for s in SUBJECTS + [COUNTRY.get(m["outlet"], "")] if s],
        "related_identifiers": related,
        "version": "1.0",
    }
    meta["rights"] = [{"id": "cc-by-4.0"}]
    return {"access": {"record": "public", "files": "public"}, "files": {"enabled": True}, "metadata": meta}, with_file

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
    print(("DRY   " if DRY else "mint  ") + m["slug"], "| full text" if with_file else "| record sheet", "|", m["outlet"] or "HSREP")
    if DRY:
        print(json.dumps(rec["metadata"], indent=1, ensure_ascii=False)[:900], "\n"); continue
    draft = api("POST", "/records", rec)
    rid = draft["id"]
    # Zenodo has no metadata-only records, so every deposit carries a file. The
    # DOI is reserved first so the record sheet can print its own DOI.
    reserved = api("POST", "/records/%s/draft/pids/doi" % rid)
    doi_pre = reserved.get("pids", {}).get("doi", {}).get("identifier", "")
    if with_file:
        upload = pdf_local                       # HSREP's own piece: the full text
    else:
        record_sheet.build(m["slug"], doi_pre, quiet=True)
        upload = os.path.join(record_sheet.OUT, "%s--record.pdf" % m["slug"])
    key = os.path.basename(upload)
    api("POST", "/records/%s/draft/files" % rid, [{"key": key}])
    api("PUT", "/records/%s/draft/files/%s/content" % (rid, key), raw=open(upload, "rb").read())
    api("POST", "/records/%s/draft/files/%s/commit" % (rid, key))
    pub = api("POST", "/records/%s/draft/actions/publish" % rid)
    doi = pub.get("pids", {}).get("doi", {}).get("identifier") or pub.get("doi")
    if not doi:
        sys.exit("published %s but no DOI in the response: %s" % (rid, json.dumps(pub)[:600]))
    dois[m["slug"]] = doi
    os.makedirs(os.path.dirname(DOIS), exist_ok=True)
    json.dump(dois, open(DOIS, "w"), indent=2); print("      ", doi, "->", pub.get("links", {}).get("self_html", ""))
    community_submit(rid)

if not DRY:
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "citation_meta.py")], check=True)
    print("done. commit data/dois.json and the article pages, push, purge.")
