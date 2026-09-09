#!/usr/bin/env bash
# Provision the Google side of the Impact pipeline: a project, two APIs, a
# service account, and its key.
#
#     bash scripts/setup_google_access.sh
#
# You authenticate in your own browser; nothing here handles a password. The key
# is written to ~/Downloads and its contents are never printed. Re-running is
# safe: every step checks whether it has already been done.
#
# The two access grants at the end are console-only and cannot be scripted,
# because they are grants on properties this project does not own. They are also
# the step that fails silently if skipped: the key stays valid and the queries
# come back empty.

set -uo pipefail

PROJECT_PREFIX="hsrep-analytics"
SA_NAME="hsrep-impact-reader"
KEY_OUT="$HOME/Downloads/hsrep-impact-key.json"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
die() { printf '\n\033[31m%s\033[0m\n' "$*" >&2; exit 1; }

command -v gcloud >/dev/null 2>&1 || die \
"gcloud is not installed.

Either install it:
    brew install --cask google-cloud-sdk

or tell Claude and take the console path instead, which is all clicking and
needs nothing installed."

say "1/6  Who are you signed in as?"
ACCOUNT="$(gcloud config get-value account 2>/dev/null)"
if [ -z "$ACCOUNT" ] || [ "$ACCOUNT" = "(unset)" ]; then
  echo "  Not signed in. A browser window will open."
  gcloud auth login || die "Sign-in did not complete."
  ACCOUNT="$(gcloud config get-value account 2>/dev/null)"
fi
echo "  $ACCOUNT"
echo "  This must be the Google account that owns the GA4 property and Search Console."
printf '  Is that the right account? [y/N] '
read -r ok
case "$ok" in [Yy]*) ;; *) echo "Run: gcloud auth login   and pick the right account."; exit 0 ;; esac

say "2/6  The project"
PROJECT="$(gcloud projects list --filter="projectId:${PROJECT_PREFIX}*" \
           --format='value(projectId)' 2>/dev/null | head -1)"
if [ -z "$PROJECT" ]; then
  PROJECT="${PROJECT_PREFIX}-$(date +%s | tail -c 6)"
  echo "  Creating $PROJECT"
  gcloud projects create "$PROJECT" --name="HSREP Analytics" \
    || die "Could not create the project. If your account is in an organisation
that restricts project creation, make one by hand at console.cloud.google.com
and re-run this script."
else
  echo "  Reusing $PROJECT"
fi
gcloud config set project "$PROJECT" >/dev/null 2>&1

say "3/6  Enabling the two APIs (this takes ~30 seconds)"
for api in analyticsdata.googleapis.com searchconsole.googleapis.com; do
  printf '  %s ... ' "$api"
  if gcloud services enable "$api" --project="$PROJECT" >/dev/null 2>&1; then
    echo "on"
  else
    echo "FAILED"
    die "Could not enable $api. Enable it by hand under APIs & Services -> Library."
  fi
done

say "4/6  The service account"
SA_EMAIL="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT" >/dev/null 2>&1; then
  echo "  Already exists"
else
  gcloud iam service-accounts create "$SA_NAME" --project="$PROJECT" \
    --display-name="HSREP Impact reader" \
    --description="Read-only GA4 and Search Console access for hsraep.org/impact.html" \
    || die "Could not create the service account."
fi
echo "  $SA_EMAIL"

say "5/6  The key"
if [ -f "$KEY_OUT" ]; then
  echo "  A key file already exists at $KEY_OUT"
  printf '  Create a second one? The old one keeps working. [y/N] '
  read -r mk
  case "$mk" in [Yy]*) KEY_OUT="${KEY_OUT%.json}-$(date +%H%M).json" ;; *) echo "  Keeping the existing key." ;; esac
fi
if [ ! -f "$KEY_OUT" ]; then
  gcloud iam service-accounts keys create "$KEY_OUT" \
    --iam-account="$SA_EMAIL" --project="$PROJECT" >/dev/null 2>&1 \
    || die "Could not create a key. Some organisations disable service-account keys;
if yours does, create one under IAM -> Service Accounts -> Keys, or ask Claude
for the workload-identity route."
  chmod 600 "$KEY_OUT"
fi
echo "  $KEY_OUT"

say "6/6  Two grants you have to make by hand"
cat <<TXT

  Copy this address:

      $SA_EMAIL

  a) Google Analytics -> Admin -> Property access management -> +
     Add that address with the role  Viewer.
     While you are there: Admin -> Property settings -> Property ID.
     It is a plain number. Write it down; you need it in a moment.

  b) Search Console (hsraep.org) -> Settings -> Users and permissions -> Add user
     Add the same address. Full or Restricted, either works.

  Neither can be scripted, and neither reports an error if skipped. The key
  stays valid and every query comes back empty, which is the most confusing
  failure this pipeline has.

  When both are done, run:

      bash scripts/impact_check.sh

TXT
