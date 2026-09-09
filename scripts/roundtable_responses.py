#!/usr/bin/env python3
"""
HSREP Roundtables — open questions and the response wall.

Turns roundtable submissions into a visible, citable record, across however many
questions are open. Before this, a response went into Tally and vanished until a
synthesis existed; the first window closed with nothing on the page and no way for
a contributor to see their own words.

WHAT IT DOES
  1. Discovers every roundtables/rt-*.json. Each is one open question.
  2. Ingests submissions once from Tally (API), a Tally CSV export, or a per-question
     seed file, and routes each one to a question by `tally_match` (a list of
     substrings looked for in the form's topic field). Unrouted responses go to the
     featured question.
  3. Applies the same consent rules as the synthesis engine: "No" is never stored,
     "anonymous" is stripped of name and affiliation before it touches disk.
  4. Merges into roundtables/responses/<id>.json, assigning stable ids and never
     overwriting a moderator's edits to entries that already exist.
  5. Renders, as STATIC HTML between markers, the open-questions cards and the record
     grouped by question, so the pages need no fetch, work with JS off, and shift
     nothing after first paint.

NOTHING PUBLISHES AUTOMATICALLY. New entries land as "status": "pending". The GitHub
Action opens a pull request; reviewing that PR is the moderation step. To publish an
entry, change its "status" to "published" (or "declined"), re-run with --render-only,
and merge.

USAGE
  python3 scripts/roundtable_responses.py                    # Tally API (needs TALLY_API_KEY) + seeds, then render
  python3 scripts/roundtable_responses.py --csv export.csv   # ingest a Tally CSV export (works on the free tier)
  python3 scripts/roundtable_responses.py --render-only      # regenerate the HTML from the JSON, after moderating
"""
import argparse, csv, datetime, glob, hashlib, html, json, os, re, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT_DIR = os.path.join(ROOT, "roundtables")
RESP_DIR = os.path.join(RT_DIR, "responses")
RT_HTML = os.path.join(ROOT, "roundtable.html")
INDEX_HTML = os.path.join(ROOT, "index.html")
TALLY_KEY = os.environ.get("TALLY_API_KEY", "")

# Field labels exactly as they appear in the Tally form. Identical to
# scripts/roundtable_synth.py so the wall and the synthesis never disagree.
F_NAME    = "Full name"
F_AFFIL   = "Role or affiliation"
F_ENGAGE  = "How would you like to engage?"
F_TOPIC   = "Which article, season, or topic is this about?"
F_MESSAGE = "Your message or response"
F_CONSENT = "May we publish your response with your name and affiliation?"

MARK = {
    "questions": ("<!--QUESTIONS:START-->", "<!--QUESTIONS:END-->"),
    "wall":      ("<!--WALL:START-->", "<!--WALL:END-->"),
    "count":     ("<!--RTCOUNT:START-->", "<!--RTCOUNT:END-->"),
}
TALLY = "https://tally.so/r/"


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
    if key in d:
        return d[key]
    for k, v in d.items():
        if key.lower() in (k or "").lower():
            return v
    return ""


def key_for(name, affiliation, text):
    """Stable dedup key. Excludes status and notes so moderation is never overwritten."""
    raw = "|".join([(name or "").strip().lower(), (affiliation or "").strip().lower(),
                    re.sub(r"\s+", " ", (text or "")).strip().lower()])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def fmt_date(iso):
    try:
        d = datetime.date.fromisoformat(iso)
    except Exception:
        return iso
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return "%d %s %d" % (d.day, months[d.month - 1], d.year)


# ------------------------------------------------------------------- ingest
def classify(consent):
    """-> 'named' | 'anonymous' | None (None means: never store this)."""
    c = str(consent or "").strip().lower()
    if not c:
        return None
    if "anonym" in c:
        return "anonymous"
    if c.startswith("no") or "keep it private" in c:
        return None
    if c.startswith("yes"):
        return "named"
    return None


def route(d, questions, featured):
    """Which question is this submission answering?"""
    hay = " ".join([str(find(d, F_TOPIC) or ""), str(find(d, F_ENGAGE) or "")]).lower()
    for q in questions:
        for m in q.get("tally_match") or []:
            if m.lower() in hay:
                return q
    return featured


def normalise(d):
    """One Tally submission -> a wall entry, 'skip', or 'withheld'."""
    engage = str(find(d, F_ENGAGE) or "")
    if engage and "roundtable" not in engage.lower() and "respond" not in engage.lower():
        return "skip"
    text = str(find(d, F_MESSAGE) or "").strip()
    if not text:
        return "skip"
    attribution = classify(find(d, F_CONSENT))
    if attribution is None:
        return "withheld"
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
def q_form_url(q):
    return q.get("tally_url") or (TALLY + q.get("tally_form_id", ""))


def render_questions(questions):
    """The open-questions cards. Every question is one way in; the featured one leads."""
    bits = ['<section class="qopen"><div class="wrap">',
            '<div class="shead rv"><div class="eyebrow">Open questions</div>',
            '<div class="top"><h2 class="sec">Three ways in. Answer the one you can answer from your own work.</h2>',
            '<div class="lead">Each question is anchored to published evidence and open with no closing date. '
            'None of them asks you to have data you would have to go and find.</div></div></div>',
            '<div class="qgrid rv">']
    for q in questions:
        c = q["_resp"]["counts"]
        n = c.get("published", 0)
        bits.append('<article class="qcard%s" id="%s">' % (" is-featured" if q.get("featured") else "", esc(q["id"])))
        bits.append('<div class="qk"><span class="qn">%s</span>%s</div>'
                    % (esc(q.get("title", q["id"])),
                       '<span class="qtag">Featured</span>' if q.get("featured") else ""))
        bits.append('<h3>%s</h3>' % esc(q.get("question", "")))
        if q.get("for_whom"):
            bits.append('<p class="qwho">%s</p>' % esc(q["for_whom"]))
        if q.get("anchor"):
            bits.append('<p class="qanchor">%s</p>' % q["anchor"])   # trusted, authored copy
        bits.append('<div class="qfoot"><span class="qcount">%s</span>'
                    % ("%d on the record" % n if n else "No responses yet"))
        bits.append('<a class="btn accent" href="#respond">Answer this &rarr;</a></div>')
        bits.append("</article>")
    bits.append("</div></div></section>")
    return "".join(bits)


def render_wall(questions):
    """The record, grouped by question. One empty state, not one per question."""
    total_pub = sum(q["_resp"]["counts"].get("published", 0) for q in questions)
    total_pend = sum(q["_resp"]["counts"].get("pending", 0) for q in questions)
    total_with = sum(q["_resp"]["counts"].get("withheld", 0) for q in questions)

    first_window = (
        '<p>Roundtable № 01 first ran as a fourteen-day window from 11 to 25 August 2026 and closed without '
        'responses. Its question was reframed on 9 September: the original wording asked professionals to report '
        'on platform analytics most of them have no reason to have seen. The windows have been removed rather '
        'than the questions.</p>')

    if not total_pub:
        return ('<div class="wall-empty rich rv" style="max-width:76ch">'
                '<p class="big">Nothing is on the record yet. This page shows responses as they are cleared, so it '
                'is empty because no one has written, not because nothing is being shown.</p>'
                + first_window +
                '<p>All three questions stay open with no closing date. When a question has drawn enough responses, '
                'a moderated synthesis is published above it, naming the contributors who consented to be named.</p>'
                '<p class="wall-cta"><a class="btn accent" href="#respond">'
                'Be the first on the record &rarr;</a></p></div>')

    bits = ['<div class="wall-counts rv">',
            '<span class="wc"><b>%d</b> on the record</span>' % total_pub]
    if total_pend:
        bits.append('<span class="wc"><b>%d</b> in review</span>' % total_pend)
    if total_with:
        bits.append('<span class="wc wc-q"><b>%d</b> withheld at the contributor&rsquo;s request</span>' % total_with)
    bits.append("</div>")

    for q in questions:
        pub = [r for r in q["_resp"]["responses"] if r.get("status") == "published"]
        if not pub:
            continue
        pub.sort(key=lambda r: (r.get("received", ""), r.get("id", "")), reverse=True)
        bits.append('<div class="wall-group rv">')
        bits.append('<div class="wg-h"><span class="wg-n">%s</span><h3>%s</h3></div>'
                    % (esc(q.get("title", q["id"])), esc(q.get("question", ""))))
        bits.append('<div class="wall">')
        for r in pub:
            anon = r.get("attribution") == "anonymous"
            who = "Anonymous contributor" if anon else esc(r.get("name") or "Contributor")
            aid = "%s-%s" % (esc(q["id"]), esc(r.get("id")))
            bits.append('<article class="resp" id="%s">' % aid)
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
            bits.append('<a class="resp-link" href="#%s">hsraep.org/roundtable.html#%s</a>' % (aid, aid))
            bits.append("</div></article>")
        bits.append("</div></div>")

    quiet = [q for q in questions if not q["_resp"]["counts"].get("published", 0)]
    if quiet:
        bits.append('<p class="wall-quiet rv">%s open and still without responses: %s.</p>'
                    % ("A question is" if len(quiet) == 1 else "Questions are",
                       ", ".join(esc(q.get("title", q["id"])) for q in quiet)))
    bits.append('<div class="wall-foot rich rv" style="max-width:76ch">' + first_window + "</div>")
    bits.append('<p class="wall-cta rv"><a class="btn accent" href="%s" target="_blank" rel="noopener">'
                'Add your response &rarr;</a></p>' % esc(q_form_url(questions[0])))
    return "".join(bits)


def render_count(questions):
    n = sum(q["_resp"]["counts"].get("published", 0) for q in questions)
    open_q = len(questions)
    parts = ["%d questions open" % open_q] if open_q > 1 else []
    if n:
        parts.append("%d response%s on the record" % (n, "" if n == 1 else "s"))
    if not parts:
        return ""
    return '<div class="rtcount">%s</div>' % esc(" · ".join(parts))


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

    questions = []
    for path in sorted(glob.glob(os.path.join(RT_DIR, "rt-*.json"))):
        cfg = load_json(path, None)
        if not cfg:
            continue
        cfg["_path"] = path
        cfg["_resp_path"] = os.path.join(RESP_DIR, os.path.basename(path))
        cfg["_resp"] = load_json(cfg["_resp_path"], {
            "question_id": cfg.get("id"), "question": cfg.get("question", ""), "updated": "",
            "counts": {"received": 0, "published": 0, "pending": 0, "declined": 0, "withheld": 0},
            "responses": [],
        })
        cfg["_resp"]["question"] = cfg.get("question", "")
        questions.append(cfg)

    if not questions:
        raise SystemExit("no roundtables/rt-*.json found")
    featured = next((q for q in questions if q.get("featured")), questions[0])
    # the featured question leads the grid and the record, whichever one it is
    questions.sort(key=lambda q: (not q.get("featured"), q["id"]))
    print("  %d question(s); featured: %s" % (len(questions), featured.get("title", featured["id"])))

    # every key already known, across all questions, so a routing change never duplicates
    seen = {r["key"] for q in questions for r in q["_resp"]["responses"] if r.get("key")}

    if not args.render_only:
        raw = []
        if args.csv:
            raw = from_csv(args.csv)
            print("  read %d row(s) from %s" % (len(raw), os.path.basename(args.csv)))
        elif TALLY_KEY and featured.get("tally_form_id"):
            forms = []
            for q in questions:
                fid = q.get("tally_form_id")
                if fid and fid not in forms:
                    forms.append(fid)
            for fid in forms:
                try:
                    got = from_tally(fid)
                    raw.extend(got)
                    print("  fetched %d submission(s) from Tally form %s" % (len(got), fid))
                except urllib.error.HTTPError as e:
                    print("  Tally HTTP %s on form %s — leaving the record as it is" % (e.code, fid), file=sys.stderr)
                except Exception as e:
                    print("  Tally unreachable (%s) — leaving the record as it is" % e, file=sys.stderr)
        else:
            print("  no TALLY_API_KEY and no --csv: ingestion skipped (seeds and rendering still run)")

        withheld = {q["id"]: 0 for q in questions}
        added = 0
        for row in raw:
            r = normalise(row)
            if r == "skip":
                continue
            q = route(row, questions, featured)
            if r == "withheld":
                withheld[q["id"]] += 1
                continue
            if r["key"] in seen:
                continue
            q["_resp"]["responses"].append(r)
            seen.add(r["key"])
            added += 1
        if raw:
            for q in questions:
                q["_resp"]["counts"]["withheld"] = withheld[q["id"]]
        print("  %d new response(s), %d withheld at the contributor's request" % (added, sum(withheld.values())))

        # hand-written invitations: people asked directly, who consented in writing
        for q in questions:
            seeds = load_json(os.path.join(RESP_DIR, q["id"] + ".seed.json"), [])
            n = 0
            for s in seeds:
                k = key_for(s.get("name", ""), s.get("affiliation", ""), s.get("text", ""))
                if k in seen:
                    continue
                e = {
                    "key": k,
                    "received": s.get("received") or datetime.date.today().isoformat(),
                    "attribution": s.get("attribution", "named"),
                    "name": s.get("name", ""), "affiliation": s.get("affiliation", ""),
                    "text": s.get("text", ""), "status": s.get("status", "pending"),
                    "seeded": True, "note": s.get("note", ""),
                }
                if e["attribution"] == "anonymous":
                    e["name"] = e["affiliation"] = ""
                q["_resp"]["responses"].append(e)
                seen.add(k)
                n += 1
            if n:
                print("  %d seeded response(s) added to %s" % (n, q["id"]))

    for q in questions:
        data = q["_resp"]
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
            "published": st.count("published"), "pending": st.count("pending"),
            "declined": st.count("declined"),
            "received": len(data["responses"]) + data["counts"].get("withheld", 0),
        })
        data["updated"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        save_json(q["_resp_path"], {k: v for k, v in data.items()})
        print("  saved: roundtables/responses/%s.json  (%d published, %d pending, %d withheld)"
              % (q["id"], data["counts"]["published"], data["counts"]["pending"], data["counts"]["withheld"]))

    splice(RT_HTML, "questions", render_questions(questions))
    splice(RT_HTML, "wall", render_wall(questions))
    splice(INDEX_HTML, "count", render_count(questions))

    pending = sum(q["_resp"]["counts"]["pending"] for q in questions)
    if pending:
        print("\n  %d response(s) awaiting your decision. In roundtables/responses/rt-NN.json set each" % pending)
        print("  \"status\" to \"published\" or \"declined\", then re-run with --render-only and merge.")


if __name__ == "__main__":
    main()
