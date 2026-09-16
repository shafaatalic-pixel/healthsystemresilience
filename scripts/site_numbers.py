#!/usr/bin/env python3
"""Counts that must never drift: computed from the pieces, written into the pages.

"The six outlet chapters" sat on the rights page after Season 1 had grown to
eight. A number typed into prose is a promise to remember it later, and nobody
does. So any count that changes when a piece is published lives here instead,
and the pages carry a marker where the number goes:

    the <!--N:outlet_word-->eight<!--/N--> pieces first published by an outlet

The text between the markers is replaced with the computed value; the markers
are HTML comments, so nothing shows in the rendered page.

  python3 scripts/site_numbers.py            # rewrite every marker
  python3 scripts/site_numbers.py --check    # exit 1 if any marker is stale
  python3 scripts/site_numbers.py --list     # print the available keys

--check runs in CI, so the failure arrives as a red tick on the commit rather
than as a partner noticing it on the rights page.
"""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from citation_meta import article_meta, ROOT  # noqa: E402

CHECK = "--check" in sys.argv
LIST = "--list" in sys.argv
WORDS = ("zero one two three four five six seven eight nine ten eleven twelve "
         "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty").split()
PAGES = ["*.html", "advocacy/*.html", "initiative/*.html", "articles/*/*.html"]
MARK = re.compile(r"(<!--N:([A-Za-z0-9_]+)-->)(.*?)(<!--/N-->)", re.S)


def word(n):
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def facts():
    """Every count the site is allowed to state, derived from the pieces."""
    outlets, own, names = 0, 0, set()
    for path in sorted(glob.glob(os.path.join(ROOT, "articles", "*", "*.html"))):
        if path.endswith("index.html"):
            continue
        m, _ = article_meta(path)
        if not m:
            continue
        if m["outlet"]:
            outlets += 1
            names.add(m["outlet"])
        else:
            own += 1
    total = outlets + own
    dois = json.load(open(os.path.join(ROOT, "data", "dois.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(ROOT, "data", "dois.json")) else {}

    # Editorial types, as the library page itself classifies each card.
    kinds = {}
    lib = os.path.join(ROOT, "articles.html")
    if os.path.exists(lib):
        for k in re.findall(r'data-type="([^"]+)"', open(lib, encoding="utf-8").read()):
            kinds[k] = kinds.get(k, 0) + 1

    outlet_list = sorted(names)
    joined = (" and ".join(outlet_list) if len(outlet_list) < 3
              else ", ".join(outlet_list[:-1]) + " and " + outlet_list[-1])
    f = {
        "total_pieces": str(total), "total_word": word(total),
        "outlet_pieces": str(outlets), "outlet_word": word(outlets),
        "own_pieces": str(own), "own_word": word(own),
        "doi_count": str(len(dois)), "doi_word": word(len(dois)),
        "outlets": joined,
    }
    for k, n in kinds.items():
        key = re.sub(r"[^a-z0-9]+", "_", k.lower()).strip("_")
        f["type_%s" % key] = str(n)
        f["type_%s_word" % key] = word(n)
    return f


def main():
    f = facts()
    if LIST:
        for k in sorted(f):
            print("  %-22s %s" % (k, f[k]))
        return 0
    stale, seen, unknown = [], 0, set()
    for pat in PAGES:
        for path in sorted(glob.glob(os.path.join(ROOT, pat))):
            s = open(path, encoding="utf-8").read()
            if "<!--N:" not in s:
                continue
            out, changed = [], False
            pos = 0
            for mo in MARK.finditer(s):
                key, cur = mo.group(2), mo.group(3)
                seen += 1
                if key not in f:
                    unknown.add(key)
                    continue
                if cur != f[key]:
                    changed = True
                    stale.append((os.path.relpath(path, ROOT), key, cur, f[key]))
                    out.append(s[pos:mo.start()] + mo.group(1) + f[key] + mo.group(4))
                    pos = mo.end()
            if changed and not CHECK:
                open(path, "w", encoding="utf-8").write("".join(out) + s[pos:])
    for k in sorted(unknown):
        print("  unknown key in a page: %s (see --list)" % k)
    if CHECK:
        for p, k, cur, want in stale:
            print("  stale: %s  %s  says %r, should be %r" % (p, k, cur, want))
        print("%d marker(s) checked, %d stale" % (seen, len(stale)))
        return 1 if (stale or unknown) else 0
    for p, k, cur, want in stale:
        print("  %s  %s: %r -> %r" % (p, k, cur, want))
    print("%d marker(s) checked, %d updated" % (seen, len(stale)))
    return 1 if unknown else 0


if __name__ == "__main__":
    sys.exit(main())
