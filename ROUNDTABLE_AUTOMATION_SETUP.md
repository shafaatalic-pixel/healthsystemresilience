# HSREP Roundtable — auto-synthesis setup (Tier 1)

This wires the roundtable so that **after a discussion window closes, a synthesis is
drafted automatically** from your Tally responses — but **nothing publishes until you
approve it.** The draft arrives as a GitHub pull request you read, edit, and merge.

```
Tally responses  ->  GitHub Action (daily)  ->  Claude drafts synthesis
                                                       |
                                                       v
                                       Pull request opened for YOU
                                                       |
                                         you edit + set approved:true + merge
                                                       v
                                  Live roundtable page shows the record
```

Private responses are never used. "Anonymous" responses appear without a name. Only
responses that consented to publication are synthesized or listed as contributors.

---

## Files this adds to the site repo

```
.github/workflows/roundtable-synthesis.yml   the scheduled job + PR opener
scripts/roundtable_synth.py                  pulls Tally, drafts with Claude, writes a DRAFT
roundtables/rt-01.json                        the roundtable's config + (once drafted) its synthesis
```

The live page (`roundtable.html`) already reads `roundtables/rt-01.json` on load and
shows the synthesis only when `"approved": true`.

---

## One-time setup

### 1. Two API keys, stored as GitHub secrets
In the site repo: **Settings -> Secrets and variables -> Actions -> New repository secret.**

| Secret name | Where to get it |
|---|---|
| `TALLY_API_KEY` | Tally -> **Settings -> API** (requires a Tally plan that includes API access) |
| `ANTHROPIC_API_KEY` | console.anthropic.com -> **API Keys** |

Optional: add a repository **variable** (not secret) named `ANTHROPIC_MODEL` set to a
current model id from docs.anthropic.com/en/docs/about-claude/models. If you skip it,
the script uses a sensible default.

> Note on Tally: the free tier does **not** include API access. If you'd rather not
> upgrade, you can skip the automation entirely and paste responses in by hand — the
> page works either way (see "Manual fallback" below).

### 2. Confirm the Tally field labels match
`scripts/roundtable_synth.py` matches responses by field label. If you renamed any form
fields, update the constants at the top of that file (`F_NAME`, `F_AFFIL`, `F_ENGAGE`,
`F_MESSAGE`, `F_CONSENT`). It matches on a case-insensitive substring, so small wording
changes are fine.

### 3. Turn on GitHub Actions + Pages
- **Settings -> Pages** -> Source: *Deploy from a branch* (or GitHub Actions), custom
  domain `hsraep.org`. The repo already contains a `CNAME` file with that domain.
- **Settings -> Actions -> General** -> allow "Read and write permissions" and
  "Allow GitHub Actions to create and approve pull requests" (needed so the job can open
  the review PR).

---

## Scheduling a roundtable

Edit `roundtables/rt-01.json` (or copy it to `rt-02.json` for the next one):

```json
{
  "question": "Does the platform decide who hears the argument?",
  "open":  "2026-08-01",
  "close": "2026-08-15",
  "tally_form_id": "VLBbYM",
  "status": "scheduled",
  "approved": false
}
```

The page shows "Opens in N days" before `open`, "Open · closes in N days" during the
window, and "Closed · synthesis in preparation" after — all automatically from these
dates. No code change needed to schedule; just edit the two dates.

---

## What happens on close (automatically)

The Action runs once a day. It does nothing until `close` has passed. On the first run
after close it:
1. Pulls completed submissions from Tally.
2. Drops non-consenting responses; anonymizes the ones that asked to stay anonymous.
3. Asks Claude to draft a restrained, Chatham-House-style synthesis (agreements, real
   disagreements, "what this means for practice") — with an explicit instruction to
   invent nothing.
4. Writes the draft into `rt-01.json` as `status:"drafted"`, `approved:false`.
5. Opens a pull request titled **"Roundtable synthesis ready for review."**

## What you do (the approval gate)

1. Open the pull request. Read the `synthesis_md` field in the diff.
2. Edit it however you like — it's a draft, not a verdict.
3. Set `"approved": true` in `rt-01.json`.
4. Merge. The live page now renders the synthesis and the named, consented contributors.

Until you merge with `approved:true`, the public page shows only "synthesis in
preparation." You are always the last editor of the record.

---

## Manual fallback (no Tally API / no automation)

You never need the automation to publish a record. To post one by hand, edit
`roundtables/rt-01.json` directly:

```json
{
  "approved": true,
  "status": "published",
  "response_count": 6,
  "synthesis_md": "## The through-line\n\nContributors broadly agreed that ...",
  "contributors": [
    {"name": "Dr. A. Example", "affiliation": "School of Public Health"}
  ]
}
```

Commit it. The page renders it exactly the same way. The automation is a convenience,
not a dependency.

---

## Cost & privacy notes
- The Action runs daily but does real work (a Claude call) only once per closed
  roundtable — effectively pennies.
- No response data is stored anywhere except your own repo, and only consented
  responses ever leave Tally.
- Nothing is ever published without a human merge.
