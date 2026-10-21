#!/usr/bin/env python3
"""Deposit a dated version of the Prevention Adoption Initiative page on Zenodo.

The page changes often. An exhibit, a grant application or a citation needs a frozen,
dated copy with its own DOI, so each deposit is one PDF printed from the page with every
tab and question expanded (initiative.html?print=1), under a concept DOI that stays the
same across versions. Later versions are new versions of the same record.

  export ZENODO_TOKEN=...      # zenodo.org -> Applications -> Personal access tokens (deposit:write, deposit:actions)
  export ORCID=0009-0009-1646-5201
  python3 scripts/zenodo_deposit_page.py --dry-run
  python3 scripts/zenodo_deposit_page.py --pdf assets/HSREP_Prevention_Adoption_Initiative_Page_2026-10-21.pdf --version 2026-10-21

Writes data/dois_pages.json ({"initiative": {"concept": ..., "versions": {"2026-10-21": doi}}}).
A second run with a new --version creates a new version of the existing record.
"""
import json, os, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import people  # noqa: E402

DRY = "--dry-run" in sys.argv
SANDBOX = "--sandbox" in sys.argv
BASE = "https://sandbox.zenodo.org/api" if SANDBOX else "https://zenodo.org/api"
TOKEN = os.environ.get("ZENODO_TOKEN", "")
ORCID = os.environ.get("ORCID", "").strip()
PDF = sys.argv[sys.argv.index("--pdf") + 1] if "--pdf" in sys.argv else "assets/HSREP_Prevention_Adoption_Initiative_Page_2026-10-21.pdf"
VERSION = sys.argv[sys.argv.index("--version") + 1] if "--version" in sys.argv else "2026-10-21"
OUT = os.path.join(ROOT, "data", "dois_pages.json")
COMMUNITY = "hsrep"

def api(method, path, data=None, raw=None, soft=False):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.inveniordm.v1+json")
    body = None
    if data is not None:
        body = json.dumps(data).encode(); req.add_header("Content-Type", "application/json")
    elif raw is not None:
        body = raw; req.add_header("Content-Type", "application/octet-stream")
    try:
        with urllib.request.urlopen(req, body, timeout=180) as r:
            t = r.read().decode(); return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        if soft: return {"_error": e.code, "_body": e.read().decode()[:300]}
        sys.exit("%s %s -> HTTP %s\n%s" % (method, path, e.code, e.read().decode()[:1500]))

def metadata():
    creators = people.creators(["Md Shafaat Ali Choyon"], fallback_orcid=ORCID)
    desc = ("<p>The Prevention Adoption Initiative is an HSREP initiative in development: a proposed twelve-month pilot, "
            "the Colorectal Cancer Screening Completion Pilot, at one Southeast Michigan health center, with a decision at month "
            "three, run by the clinic's own staff on a weekly routine and judged by an independent academic evaluator once one is "
            "confirmed. This record is a dated, frozen copy of the public page hsraep.org/initiative.html as it stood on %s, "
            "printed with every tab and question expanded. It states the problem (the Prevention Adoption Gap), the routine, the "
            "terms for a host clinic, an evaluator and a funder, the evidence and its limits, the founder's track record, and the "
            "status: no host site or academic partner is confirmed and nothing is deployed.</p>"
            "<p>Later versions of the page are deposited as new versions of this record. The live page may differ from this copy.</p>"
            "<p>A proposal and design document, not a peer-reviewed article and not a report of results.</p>") % VERSION
    return {
        "access": {"record": "public", "files": "public"}, "files": {"enabled": True},
        "metadata": {
            "resource_type": {"id": "publication-report"},
            "title": "Prevention Adoption Initiative: Colorectal Cancer Screening Completion Pilot, proposal and design (page version %s)" % VERSION,
            "creators": creators,
            "publication_date": VERSION,
            "publisher": "HSREP",
            "description": desc,
            "languages": [{"id": "eng"}],
            "subjects": [{"subject": s} for s in ["preventive care", "colorectal cancer screening", "federally qualified health centers",
                                                   "implementation", "health system resilience", "public health", "United States"]],
            "related_identifiers": [{"identifier": "https://hsraep.org/initiative.html", "scheme": "url",
                                     "relation_type": {"id": "isidenticalto"}, "resource_type": {"id": "publication-report"}}],
            "version": VERSION,
            "rights": [{"id": "cc-by-4.0"}],
        },
    }

if __name__ == "__main__":
    pdf = os.path.join(ROOT, PDF) if not os.path.isabs(PDF) else PDF
    if not os.path.exists(pdf): sys.exit("no such PDF: " + pdf)
    rec = metadata()
    saved = json.load(open(OUT)) if os.path.exists(OUT) else {}
    page = saved.get("initiative", {"concept": "", "versions": {}})
    if VERSION in page["versions"]:
        sys.exit("version %s already deposited: %s" % (VERSION, page["versions"][VERSION]))
    if DRY:
        print("DRY  ", os.path.basename(pdf), os.path.getsize(pdf), "bytes"); print(json.dumps(rec["metadata"], indent=1, ensure_ascii=False)); sys.exit(0)
    if not TOKEN: sys.exit("ZENODO_TOKEN is not set.")
    if page["concept"]:
        # new version of the existing record
        prev = page["versions"][sorted(page["versions"])[-1]]
        rid_prev = prev.rsplit(".", 1)[-1]
        draft = api("POST", "/records/%s/versions" % rid_prev)
        rid = draft["id"]
        api("PUT", "/records/%s/draft" % rid, rec)
    else:
        draft = api("POST", "/records", rec); rid = draft["id"]
    key = os.path.basename(pdf)
    api("POST", "/records/%s/draft/files" % rid, [{"key": key}])
    api("PUT", "/records/%s/draft/files/%s/content" % (rid, key), raw=open(pdf, "rb").read())
    api("POST", "/records/%s/draft/files/%s/commit" % (rid, key))
    pub = api("POST", "/records/%s/draft/actions/publish" % rid)
    doi = pub.get("pids", {}).get("doi", {}).get("identifier") or pub.get("doi")
    concept = (pub.get("parent") or {}).get("pids", {}).get("doi", {}).get("identifier") or pub.get("conceptdoi") or page["concept"]
    if not doi: sys.exit("published %s but no DOI: %s" % (rid, json.dumps(pub)[:600]))
    page["concept"] = concept; page["versions"][VERSION] = doi
    saved["initiative"] = page
    os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(saved, open(OUT, "w"), indent=2)
    print(doi, "concept", concept, "->", pub.get("links", {}).get("self_html", ""))
    r = api("POST", "/records/%s/communities" % rid, {"communities": [{"id": COMMUNITY}]}, soft=True)
    print("community:", "submitted" if not r.get("_error") else "not submitted (%s)" % r["_error"])
    print("Now put the DOI on the page: the version line in initiative.html, then commit, push, purge.")
