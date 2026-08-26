#!/usr/bin/env python3
"""
HSREP Roundtable — live participation count sync.

Runs on a schedule while a roundtable window is open. For every roundtables/rt-*.json
it reads the Tally submission count for that form and writes it back as
`response_count`, with a `count_synced` timestamp. It does NOT touch the synthesis,
status, or approval fields — the synthesis automation (roundtable_synth.py) owns
those once the window has closed.

This is what lets the private Roundtable Console show a near-live participation
number without ever exposing an API key: the key lives only in GitHub Actions
secrets; the browser only reads the resulting JSON.

Environment (GitHub Actions secret):
  TALLY_API_KEY  - Tally API key (Settings -> API; needs a Tally plan with API access)
"""
import os, sys, glob, json, datetime, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT_DIR = os.path.join(ROOT, "roundtables")
TALLY_KEY = os.environ.get("TALLY_API_KEY", "")


def http_json(url, headers):
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def tally_count(form_id):
    """Return the number of completed submissions for a Tally form."""
    url = f"https://api.tally.so/forms/{form_id}/submissions?filter=completed&limit=1000"
    raw = http_json(url, {"Authorization": f"Bearer {TALLY_KEY}"})
    for k in ("totalNumberOfSubmissionsPerFilter", "totalNumberOfSubmissions", "total"):
        if isinstance(raw.get(k), int):
            return raw[k]
    subs = raw.get("submissions") or raw.get("data") or []
    return len(subs)


def main():
    if not TALLY_KEY:
        print("No TALLY_API_KEY set - skipping count sync.", file=sys.stderr)
        return
    today = datetime.date.today().isoformat()
    now = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    changed = 0
    for path in sorted(glob.glob(os.path.join(RT_DIR, "rt-*.json"))):
        try:
            with open(path) as f:
                cfg = json.load(f)
        except Exception as e:
            print(f"skip {os.path.basename(path)}: {e}", file=sys.stderr); continue
        form_id = cfg.get("tally_form_id")
        if not form_id:
            continue
        # only sync while scheduled/open; leave closed rounds to the synthesis job
        if cfg.get("close") and today > cfg["close"]:
            continue
        if cfg.get("status") in ("drafted", "published"):
            continue
        try:
            n = tally_count(form_id)
        except urllib.error.HTTPError as e:
            print(f"{os.path.basename(path)}: Tally HTTP {e.code}", file=sys.stderr); continue
        except Exception as e:
            print(f"{os.path.basename(path)}: {e}", file=sys.stderr); continue
        if cfg.get("response_count") == n and cfg.get("count_synced"):
            print(f"{os.path.basename(path)}: unchanged ({n})"); continue
        cfg["response_count"] = n
        cfg["count_synced"] = now
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False); f.write("\n")
        changed += 1
        print(f"{os.path.basename(path)}: {n} submissions")
    print(f"Done. {changed} file(s) updated.")


if __name__ == "__main__":
    main()
