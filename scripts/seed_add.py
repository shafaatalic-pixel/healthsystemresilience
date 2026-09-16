#!/usr/bin/env python3
"""
Put an emailed or invited response on the record in one step.

  python3 scripts/seed_add.py --q rt-02 --name "Jane Doe, MPH" \
      --aff "Quality lead, Example Health Center, Detroit" \
      --text "Three sentences pasted from the email." --date 2026-09-17

  --anon        publish without name and affiliation (they are not written to disk)
  --pending     add as pending instead of published (review first)
  --no-render   append only; skip the site render

Consent rule: run this only for a response whose author wrote, in the email,
that it may be published (named or anonymously). The seed file keeps the
attribution you pass and nothing else about the sender.
"""
import argparse, datetime, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESP = os.path.join(ROOT, "roundtables", "responses")

ap = argparse.ArgumentParser()
ap.add_argument("--q", required=True, help="question id, e.g. rt-02")
ap.add_argument("--name", default="")
ap.add_argument("--aff", default="")
ap.add_argument("--text", required=True)
ap.add_argument("--date", default=datetime.date.today().isoformat())
ap.add_argument("--anon", action="store_true")
ap.add_argument("--pending", action="store_true")
ap.add_argument("--no-render", action="store_true")
a = ap.parse_args()

if not os.path.exists(os.path.join(ROOT, "roundtables", a.q + ".json")):
    sys.exit("no such question: %s" % a.q)
if not a.anon and not a.name:
    sys.exit("give --name (and --aff) or pass --anon")

path = os.path.join(RESP, a.q + ".seed.json")
entries = []
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        entries = json.load(f)

entry = {
    "name": "" if a.anon else a.name.strip(),
    "affiliation": "" if a.anon else a.aff.strip(),
    "text": a.text.strip(),
    "received": a.date,
    "attribution": "anonymous" if a.anon else "named",
    "status": "pending" if a.pending else "published",
}
entries.append(entry)
os.makedirs(RESP, exist_ok=True)
with open(path, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("added to %s (%d entries)" % (os.path.relpath(path, ROOT), len(entries)))

if not a.no_render:
    r = subprocess.run([sys.executable, os.path.join(HERE, "roundtable_responses.py")], cwd=ROOT)
    sys.exit(r.returncode)
