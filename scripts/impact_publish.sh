#!/usr/bin/env bash
# Refresh the Impact page from the Analytics Command Center and publish it.
#
#     bash scripts/impact_publish.sh
#
# One command for the whole manual chain: read the dashboard, render the figures
# into the pages, commit only if a number moved, push, and purge the edge cache.
# The purge is the step that is easy to forget and the one that decides whether
# anyone sees the change for the next hour.
#
# This is the interim path. It runs on your machine, after the Command Center has
# refreshed, and it needs no API credentials because the dashboard already holds
# the access. Once the five GitHub secrets exist, .github/workflows/impact.yml
# does all of this nightly and this script becomes the manual fallback.
#
# Optional, and only if you want the purge done for you rather than in the
# dashboard:  export CF_PURGE_TOKEN=...  and  export CF_ZONE_ID=...

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

DASH="${HSREP_DASHBOARD:-$HOME/Documents/Claude/Artifacts/analytics-command-center/index.html}"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

if [ ! -f scripts/impact_build.py ]; then
  echo "Run this from inside the site repository." >&2; exit 1
fi
if [ ! -f "$DASH" ]; then
  echo "The Analytics Command Center is not at:" >&2
  echo "  $DASH" >&2
  echo "Pass its path with HSREP_DASHBOARD=... or open the artifact once to create it." >&2
  exit 1
fi

# The Command Center writes this file when it refreshes. If it is older than a
# day the figures about to be published are yesterday's, which is worth knowing
# before they are committed rather than after.
# python3 rather than stat: BSD stat -f and GNU stat -f mean different things,
# and the GNU one succeeds with text that breaks the arithmetic below.
MTIME="$(python3 -c 'import os,sys;print(int(os.path.getmtime(sys.argv[1])))' "$DASH" 2>/dev/null || echo "")"
if [ -n "$MTIME" ]; then
  AGE_HOURS=$(( ( $(date +%s) - MTIME ) / 3600 ))
else
  AGE_HOURS=0
fi
say "Dashboard last written ${AGE_HOURS}h ago"
if [ "$AGE_HOURS" -gt 26 ]; then
  printf 'That is more than a day old. Refresh the Command Center first? [y/N] '
  read -r ans
  case "$ans" in [Yy]*) ;; *) echo "Stopping. Nothing changed."; exit 0 ;; esac
fi

# Only three files are committed, and only the parts of them this script wrote.
# If any of the three already had uncommitted edits, they would be swept into the
# commit silently, which is how an unrelated half-finished change gets published.
DIRTY="$(git status --porcelain -- data/impact.json impact.html index.html)"
if [ -n "$DIRTY" ]; then
  say "These files already had uncommitted changes"
  echo "$DIRTY"
  printf '\nThey will be committed along with the refreshed figures. Continue? [y/N] '
  read -r ok
  case "$ok" in [Yy]*) ;; *) echo "Stopping. Nothing changed."; exit 0 ;; esac
fi

say "Reading the dashboard"
python3 scripts/impact_build.py "$DASH" || exit 1

say "Rendering the figures into the pages"
python3 scripts/impact_render.py . || exit 1

rm -f .git/HEAD.lock .git/index.lock .git/refs/heads/main.lock 2>/dev/null

git add data/impact.json impact.html index.html 2>/dev/null
if git diff --cached --quiet; then
  say "No figure moved. Nothing committed, nothing purged."
  exit 0
fi

say "What changed"
git diff --cached --stat
python3 - <<'PY'
import json, subprocess
try:
    old = json.loads(subprocess.check_output(["git", "show", "HEAD:data/impact.json"]))
    new = json.load(open("data/impact.json"))
except Exception:
    raise SystemExit(0)


def flat(o, p=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flat(v, p + "." + str(k)))
    elif isinstance(o, list):
        out[p[1:]] = str(o)[:60]
    else:
        out[p[1:]] = o
    return out


a, b = flat(old), flat(new)
rows = [(k, a.get(k), b.get(k)) for k in sorted(set(a) | set(b))
        if a.get(k) != b.get(k) and k not in ("updated", "window.to", "source")]
if rows:
    print("\nFigures:")
    for k, x, y in rows:
        print("  %-34s %s -> %s" % (k, x, y))
PY

printf '\nCommit and push? [Y/n] '
read -r go
case "$go" in [Nn]*) echo "Left staged. Nothing pushed."; exit 0 ;; esac

git commit -q -m "Impact: figures refreshed $(date +%Y-%m-%d)

Read from the Analytics Command Center by scripts/impact_build.py and written
into the pages by scripts/impact_render.py. Published with
scripts/impact_publish.sh.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" || exit 1
# hsrep-bot commits to main from GitHub Actions every night, so main here is
# often behind. Rebase before pushing or the push is rejected.
git pull --rebase -q origin main || { echo "Rebase failed. Nothing was pushed." >&2; exit 1; }
git push -q origin main || { echo "Push failed. Nothing was purged." >&2; exit 1; }
say "Pushed"

if [ -n "${CF_PURGE_TOKEN:-}" ] && [ -n "${CF_ZONE_ID:-}" ]; then
  say "Waiting 90s for GitHub Pages to build"
  sleep 90
  say "Purging the edge cache"
  curl -sS -X POST \
    "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/purge_cache" \
    -H "Authorization: Bearer ${CF_PURGE_TOKEN}" \
    -H "Content-Type: application/json" \
    --data '{"files":["https://hsraep.org/impact.html","https://hsraep.org/"]}' \
    -o /tmp/hsrep_purge.json
  python3 -c "import json;d=json.load(open('/tmp/hsrep_purge.json'));print('  purged' if d.get('success') else '  PURGE FAILED: %s'%d.get('errors'))"
else
  say "Now purge the cache, or readers keep the old page for up to an hour"
  echo "  Cloudflare -> hsraep.org -> Caching -> Configuration -> Custom Purge -> URL"
  echo "  https://hsraep.org/impact.html"
  echo "  https://hsraep.org/"
  echo
  echo "  To have this script do it: export CF_PURGE_TOKEN=... and CF_ZONE_ID=..."
fi
