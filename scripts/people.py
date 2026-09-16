#!/usr/bin/env python3
"""Who wrote what: a byline to an ORCID, credentials, role and affiliation.

Season 1 was one author, so the scripts hardcoded him. Season 2 brings partner
contributors, and a contributor's DOI has to carry the contributor's own ORCID,
not HSREP's. Every script that names an author reads data/authors.json through
here instead.

An unknown byline still works: the name is split into given and family names
and the piece is deposited without an ORCID. That is a degraded record, not a
wrong one, so add the person to data/authors.json before their piece goes out.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, "data", "authors.json")
HSREP = "HSREP, Health System Resilience & Economic Protection"


def load():
    return json.load(open(FILE, encoding="utf-8")) if os.path.exists(FILE) else {}


def person(name):
    a = load().get(name, {})
    parts = [p for p in name.split() if p]
    return {
        "name": name,
        "given": a.get("given") or " ".join(parts[:-1]),
        "family": a.get("family") or (parts[-1] if parts else name),
        "orcid": a.get("orcid", ""),
        "credentials": a.get("credentials", ""),
        "role": a.get("role", ""),
        "affiliation": a.get("affiliation", HSREP),
    }


def initials(name):
    """Choyon, M. S. A. — the reference-list form."""
    p = person(name)
    g = [x[0] + "." for x in p["given"].split() if x]
    return "%s, %s" % (p["family"], " ".join(g)) if g else p["family"]


def reference_names(names):
    """One name, or two joined with &, or APA's comma list ending in &."""
    ii = [initials(n) for n in names if n]
    if not ii:
        return ""
    if len(ii) == 1:
        return ii[0]
    return ", ".join(ii[:-1]) + " & " + ii[-1]


def byline(names):
    """Md Shafaat Ali Choyon, MBA, MCIM, MPH, CHES® — the reading form."""
    out = []
    for n in names:
        p = person(n)
        out.append(p["name"] + (", " + p["credentials"] if p["credentials"] else ""))
    return " and ".join(out)


def creators(names, fallback_orcid=""):
    """The creators block for a Zenodo deposit."""
    out = []
    for i, n in enumerate(names):
        p = person(n)
        c = {"person_or_org": {"type": "personal", "given_name": p["given"], "family_name": p["family"]},
             "affiliations": [{"name": p["affiliation"]}]}
        orcid = p["orcid"] or (fallback_orcid if i == 0 else "")
        if orcid:
            c["person_or_org"]["identifiers"] = [{"scheme": "orcid", "identifier": orcid}]
        out.append(c)
    return out


if __name__ == "__main__":
    import sys
    for n in (sys.argv[1:] or sorted(load())):
        print(json.dumps(person(n), ensure_ascii=False))
