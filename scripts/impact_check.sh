#!/usr/bin/env bash
# Run the fetcher's diff test without putting any credential into a command line.
#
#     bash scripts/impact_check.sh
#
# It asks for the four values, holds them only for the length of one command, and
# stores nothing. Nothing reaches your shell history, no file is written, and the
# Cloudflare token is not echoed as you paste it.
#
# The diff prints every field where the API path disagrees with what
# scripts/impact_build.py produced from the Command Center. It writes nothing.

set -u
cd "$(dirname "$0")/.." || exit 1

if [ ! -f scripts/impact_fetch.py ]; then
  echo "Run this from inside the site repository." >&2
  exit 1
fi

echo
echo "Four values. Paste each and press return."
echo "Tip: for the key file you can drag it from Finder into this window."
echo

printf 'Path to the service-account JSON key: '
read -r KEYPATH
KEYPATH="${KEYPATH%\"}"; KEYPATH="${KEYPATH#\"}"          # drag-and-drop quoting
KEYPATH="${KEYPATH%\'}"; KEYPATH="${KEYPATH#\'}"
KEYPATH="${KEYPATH/#\~/$HOME}"                            # ~ is not expanded by read
if [ ! -f "$KEYPATH" ]; then
  echo "No file at: $KEYPATH" >&2
  exit 1
fi
if ! python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get('client_email') else 1)" "$KEYPATH" 2>/dev/null; then
  echo "That file does not look like a service-account key (no client_email)." >&2
  exit 1
fi
echo "  key belongs to: $(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['client_email'])" "$KEYPATH")"
echo "  that address must be a Viewer on the GA4 property and a user on Search Console."
echo

printf 'GA4 numeric property id (not G-XXXXXXX): '
read -r PROPID
case "$PROPID" in
  ''|*[!0-9]*) echo "That is not a number. Admin -> Property settings -> Property ID." >&2; exit 1 ;;
esac

printf 'Cloudflare analytics token (input hidden): '
read -rs CFTOKEN; echo
if [ -z "$CFTOKEN" ]; then echo "No token given." >&2; exit 1; fi

printf 'Cloudflare zone id for hsraep.org: '
read -r CFZONE
if [ -z "$CFZONE" ]; then echo "No zone id given." >&2; exit 1; fi

echo
echo "Fetching. Nothing will be written."
echo

GA4_SA_JSON="$(cat "$KEYPATH")" \
GA4_PROPERTY_ID="$PROPID" \
CF_ANALYTICS_TOKEN="$CFTOKEN" \
CF_ZONE_ID="$CFZONE" \
python3 scripts/impact_fetch.py --diff 2>&1 | grep -v "FutureWarning\|NotOpenSSLWarning\|warnings.warn\|eol_message"

echo
echo "Nothing was stored. Close this window and the values are gone."
