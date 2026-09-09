#!/usr/bin/env python3
"""
HSREP Roundtable — the response wall.

Turns roundtable submissions into a visible, citable record. Before this, a
response went into Tally and vanished until a synthesis existed; the first window
closed with nothing on the page and no way for a contributor to see their own
words. This makes each consented response appear on the record with its own
permalink, while keeping the moderation gate.

WHAT IT DOES
  1. Ingests submissions from Tally (API), from a Tally CSV export, and from a
     hand-written seed file for people invited directly.
  2. Applies the same consent rules as the synthesis engine: "No" is never stored,
     "anonymous" is stripped of name and affiliation before it touches disk.
  3. Merges into roundtables/responses/rt-01.json, assigning stable ids and never
     overwriting a moderator's edits to entries that already exist.
  4. Renders the wall as STATIC HTML into roundtable.html (and a count into
     index.html) between markers, so the page needs no fetch, works with JS off,
     and shifts nothing after first paint.

NOTHING PUBLISHES AUTOMATICALLY. New entries land as "status": "pending". The
GitHub Action opens a pull request; reviewing that PR is the moderation step.
To publish an entry, change its "status" to "published" (or "declined" to refuse
it), re-run with --render-only, and merge.

USAGE
  python3 scripts/roundtable_responses.py                    # Tally API (needs TALLY_API_KEY) + seed, then render
  python3 scripts/roundtable_responses.py --csv export.csv   # ingest a Tally CSV export (works on the free tier)
  python3 scripts/roundtable_responses.py --render-only      # regenerate the HTML from the JSON, after moderating

ENVIRONMENT
  TALLY_API_KEY - optional. Without it the API step is skipped and the CSV / seed
                  paths still work, so this is usable on Tally's free tier today.
"""
import argparse, csv, datetime, hashlib, html, json, os, re, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, "roundtables", "rt-01.json")
RESP_DIR = os.path.join(ROOT, "roundtables", "responses")
RESP_PATH = os.path.join(RESP_DIR, "rt-01.json")
SEED_PATH = os.path.join(RESP_DIR, "rt-01.seed.json")
RT_HTML = os.path.join(ROOT, "roundtable.html")
INDEX_HTML = os.path.join(ROOT, "index.html")
TALLY_KEY = os.environ.get("TALLY_API_KEY", "")

# Field labels exactly as they appear in the Tally form. Kept identical to
# scripts/roundtable_synth.py so the wall and the synthesis never disagree.
F_NAME    = "Full name"
F_AFFIL   = "Role or affiliation"
F_ENGAGE  = "How would you like to engage?"
F_MESSAGE = "Your message or response"
F_CONSENT = "May we publish your response with your name and affiliation?"

MARK = {
    "wall":  ("<!--WALL:START-->", "<!--WALL:END-->"),
    "count": ("<!--RTCOUNT:START-->", "<!--RTCOUNT:END-->"),
}


# ----------------------------------------------------------------- utilities
def esc(s):
    return html.escape(str(s or ""), quote=True)


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def find(d, key):
    """Match a Tally field by exact label, then case-insensitive substring."""
    if key in d:
        return d[key]
    for k, v in d.items():
        if key.lower() in (k or "").lower():
            return v
    return ""


def key_for(name, affiliation, text):
    """Stable dedup key. Deliberately excludes status/notes so moderation is preserved."""
    raw = "|".join([(name or "").strip().lower(), (affiliation or "").strip().lower(),
                    re.sub(r"\s+", " ", (text or "")).strip().lower()])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------- ingest
def classify(consent):
    """-> 'named' | 'anonymous' | None (None means: never store this)."""
    c = str(consent or "").strip().lower()
    if not c:
        return None                      # no answer recorded: treat as no consent
    if "anonym" in c:
        return "anonymous"
    if c.startswith("no") or "keep it private" in c:
        return None
    if c.startswith("yes"):
        return "named"
    return None                          # anything unrecognised is not consent


def normalise(d, roundtable_label):
    """One Tally submission -> a wall entry, or None if it should not be stored."""
    engage = str(find(d, F_ENGAGE) or "")
    if roundtable_label.lower() not in engage.lower() and "respond" not in engage.lower():
        return "skip"                    # not a roundtable response at all
    text = str(find(d, F_MESSAGE) or "").strip()
    if not text:
        return "skip"
    attribution = classify(find(d, F_CONSENT))
    if attribution is None:
        return "withheld"                # counted, never written to disk
    name = "" if attribution == "anonymous" else str(find(d, F_NAME) or "").strip()
    affil = "" if attribution == "anonymous" else str(find(d, F_AFFIL) or "").strip()
    return {
        "key": key_for(name, affil, text),
        "received": datetime.date.today().isoformat(),
        "attribution": attribution,
        "name": name,
        "affiliation": affil,
        "text": text,
        "status": "pending",
        "seeded": False,
        "note": "",
    }


def from_tally(form_id):
    url = f"https://api.tally.so/forms/{form_id}/submissions?filter=completed&limit=1000"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TALLY_KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = json.loads(r.read().decode())
    out = []
    for s in raw.get("submissions") or raw.get("data") or []:
        d = {}
        for a in s.get("responses") or s.get("answers") or []:
            label = (a.get("label") or a.get("title") or a.get("key") or "").strip()
            val = a.get("value")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            d[label] = val.strip() if isinstance(val, str) else val
        out.append(d)
    return out


def from_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [dict(row) for row in csv.DictReader(f)]


# ------------------------------------------------------------------- render
def fmt_date(iso):
    try:
        d = datetime.date.fromisoformat(iso)
    except Exception:
        return iso
    return "%d %s %d" % (d.day, ["January", "February", "March", "April", "May", "June", "July",
                                 "August", "September", "October", "November", "December"][d.month - 1], d.year)


FIRST_WINDOW_NOTE = (
    "<p>The first response window ran from 11 to 25 August 2026 and closed without any responses. "
    "The question was opened cold: announced to a general audience rather than put to named professionals "
    "first, and given a deadline before anyone had a reason to meet it. The window has been removed rather "
    "than the question.</p>")

EMPTY_STATE = (
    '<p class="big">Nothing is on the record yet. This page shows responses as they are cleared, '
    'so it is empty because no one has written, not because nothing is being shown.</p>'
    + FIRST_WINDOW_NOTE +
    '<p>The question stays open with no closing date. When enough responses are on the record, a moderated '
    'synthesis will be published above, naming the contributors who consented to be named.</p>'
    '<p class="wall-cta"><a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">'
    'Be the first on the record &rarr;</a></p>')


def render_wall(data):
    pub = [r for r in data["responses"] if r.get("status") == "published"]
    pub.sort(key=lambda r: (r.get("received", ""), r.get("id", "")), reverse=True)
    c = data["counts"]

    if not pub:
        return '<div class="wall-empty rich rv" style="max-width:76ch">' + EMPTY_STATE + "</div>"

    bits = ['<div class="wall-counts rv">']
    bits.append('<span class="wc"><b>%d</b> on the record</span>' % c.get("published", 0))
    if c.get("pending"):
        bits.append('<span class="wc"><b>%d</b> in review</span>' % c["pending"])
    if c.get("withheld"):
        bits.append('<span class="wc wc-q"><b>%d</b> withheld at the contributor&rsquo;s request</span>'
                    % c["withheld"])
    bits.append("</div>")

    bits.append('<div class="wall rv">')
    for r in pub:
        anon = r.get("attribution") == "anonymous"
        who = "Anonymous contributor" if anon else esc(r.get("name") or "Contributor")
        rid = esc(r.get("id"))
        bits.append('<article class="resp" id="%s">' % rid)
        bits.append('<div class="resp-h"><span class="resp-n">%s</span>' % who)
        if not anon and r.get("affiliation"):
            bits.append('<span class="resp-a">%s</span>' % esc(r["affiliation"]))
        bits.append('<span class="resp-d">%s</span></div>' % esc(fmt_date(r.get("received", ""))))
        for para in [p for p in re.split(r"\n\s*\n", r.get("text", "").strip()) if p.strip()]:
            bits.append("<p>%s</p>" % esc(para.strip()).replace("\n", "<br>"))
        bits.append('<div class="resp-f">')
        if r.get("seeded"):
            bits.append('<span class="resp-chip">Invited before the question opened</span>')
        if r.get("note"):
            bits.append('<span class="resp-chip">%s</span>' % esc(r["note"]))
        bits.append('<a class="resp-link" href="#%s">hsraep.org/roundtable.html#%s</a>' % (rid, rid))
        bits.append("</div></article>")
    bits.append("</div>")
    bits.append('<div class="wall-foot rich rv" style="max-width:76ch">' + FIRST_WINDOW_NOTE + "</div>")
    bits.append('<p class="wall-cta rv"><a class="btn accent" href="https://tally.so/r/VLBbYM" '
                'target="_blank" rel="noopener">Add your response &rarr;</a></p>')
    return "".join(bits)


def render_count(data):
    n = data["counts"].get("published", 0)
    if not n:
        return ""
    return '<div class="rtcount">%d response%s on the record</div>' % (n, "" if n == 1 else "s")


def splice(path, kind, payload):
    a, b = MARK[kind]
    s = open(path, encoding="utf-8").read()
    i, j = s.find(a), s.find(b)
    if i < 0 or j < 0:
        print("  ! markers %s missing in %s — skipped" % (kind, os.path.basename(path)), file=sys.stderr)
        return False
    new = s[: i + len(a)] + payload + s[j:]
    if new == s:
        print("  unchanged: %s (%s)" % (os.path.basename(path), kind))
        return False
    open(path, "w", encoding="utf-8").write(new)
    print("  rendered:  %s (%s)" % (os.path.basename(path), kind))
    return True


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="a Tally CSV export to ingest")
    ap.add_argument("--render-only", action="store_true", help="skip ingestion, just regenerate the HTML")
    args = ap.parse_args()

    cfg = load_json(CFG_PATH, {})
    data = load_json(RESP_PATH, {
        "question_id": cfg.get("id", "rt-01"),
        "question": cfg.get("question", ""),
        "updated": "",
        "counts": {"received": 0, "published": 0, "pending": 0, "declined": 0, "withheld": 0},
        "responses": [],
    })
    data["question"] = cfg.get("question", data.get("question", ""))
    existing = {r["key"]: r for r in data["responses"] if r.get("key")}
    label = cfg.get("roundtable_engagement_label", "roundtable")

    if not args.render_only:
        raw = []
        if args.csv:
            raw = from_csv(args.csv)
            print("  read %d row(s) from %s" % (len(raw), os.path.basename(args.csv)))
        elif TALLY_KEY and cfg.get("tally_form_id"):
            try:
                raw = from_tally(cfg["tally_form_id"])
                print("  fetched %d submission(s) from Tally" % len(raw))
            except urllib.error.HTTPError as e:
                print("  Tally HTTP %s — leaving the record as it is" % e.code, file=sys.stderr)
            except Exception as e:
                print("  Tally unreachable (%s) — leaving the record as it is" % e, file=sys.stderr)
        else:
            print("  no TALLY_API_KEY and no --csv: ingestion skipped (seed file and rendering still run)")

        withheld = added = 0
        for row in raw:
            r = normalise(row, label)
            if r == "skip":
                continue
            if r == "withheld":
                withheld += 1
                continue
            if r["key"] in existing:
                continue                       # already known; moderator edits are preserved
            data["responses"].append(r)
            existing[r["key"]] = r
            added += 1
        if raw:
            data["counts"]["withheld"] = withheld
        print("  %d new response(s), %d withheld at the contributor's request" % (added, withheld))

        # hand-written invitations: people asked directly, who consented in writing
        seeds = load_json(SEED_PATH, [])
        seeded = 0
        for s in seeds:
            k = key_for(s.get("name", ""), s.get("affiliation", ""), s.get("text", ""))
            if k in existing:
                continue
            entry = {
                "key": k,
                "received": s.get("received") or datetime.date.today().isoformat(),
                "attribution": s.get("attribution", "named"),
                "name": s.get("name", ""),
                "affiliation": s.get("affiliation", ""),
                "text": s.get("text", ""),
                "status": s.get("status", "pending"),
                "seeded": True,
                "note": s.get("note", ""),
            }
            if entry["attribution"] == "anonymous":
                entry["name"] = entry["affiliation"] = ""
            data["responses"].append(entry)
            existing[k] = entry
            seeded += 1
        if seeded:
            print("  %d seeded response(s) added from rt-01.seed.json" % seeded)

    # stable ids, assigned once and never reused, so a permalink never moves
    highest = 0
    for r in data["responses"]:
        m = re.match(r"r-(\d+)$", r.get("id") or "")
        if m:
            highest = max(highest, int(m.group(1)))
    for r in data["responses"]:
        if not r.get("id"):
            highest += 1
            r["id"] = "r-%03d" % highest

    st = [r.get("status") for r in data["responses"]]
    data["counts"].update({
        "published": st.count("published"),
        "pending": st.count("pending"),
        "declined": st.count("declined"),
        "received": len(data["responses"]) + data["counts"].get("withheld", 0),
    })
    data["updated"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    save_json(RESP_PATH, data)
    print("  saved: roundtables/responses/rt-01.json  (%d published, %d pending, %d withheld)"
          % (data["counts"]["published"], data["counts"]["pending"], data["counts"]["withheld"]))

    splice(RT_HTML, "wall", render_wall(data))
    splice(INDEX_HTML, "count", render_count(data))

    if data["counts"]["pending"]:
        print("\n  %d response(s) awaiting your decision. In roundtables/responses/rt-01.json set each"
              % data["counts"]["pending"])
        print("  \"status\" to \"published\" or \"declined\", then re-run with --render-only and merge.")


if __name__ == "__main__":
    main()
