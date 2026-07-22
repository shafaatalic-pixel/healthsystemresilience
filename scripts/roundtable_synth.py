#!/usr/bin/env python3
"""
HSREP Roundtable — auto-draft synthesis (Tier 1, static-site friendly).

Runs in GitHub Actions on a schedule. When a roundtable's response window has
closed, it pulls the responses from Tally, drafts a synthesis with the Claude API,
and writes it into roundtables/<id>.json as a DRAFT (approved:false, status:"drafted").

Nothing publishes automatically. The GitHub Action opens a Pull Request with the
draft; a human reviews it and — to publish — sets "approved": true and merges.
The live roundtable page reads the JSON and only renders the synthesis when approved.

Honesty rules baked in:
  - Only responses that consented to publication are used.
  - "Yes but keep me anonymous" responses are anonymized (no name/affiliation).
  - "No — keep it private" responses are excluded entirely.
  - Contributors listed are real and consented only; nothing is fabricated.

Environment (set as GitHub Actions secrets):
  TALLY_API_KEY       - Tally API key (Settings → API; needs a plan with API access)
  ANTHROPIC_API_KEY   - Claude API key from console.anthropic.com
  ANTHROPIC_MODEL     - (optional) a current model id, e.g. from docs.anthropic.com/en/docs/about-claude/models
"""
import os, sys, json, datetime, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, "roundtables", "rt-01.json")
TALLY_KEY = os.environ.get("TALLY_API_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")  # set to a current model id

# --- field labels as they appear in the Tally form (edit if you rename fields) ---
F_NAME        = "Full name"
F_AFFIL       = "Role or affiliation"
F_ENGAGE      = "How would you like to engage?"
F_TOPIC       = "Which article, season, or topic is this about?"
F_MESSAGE     = "Your message or response"
F_CONSENT     = "May we publish your response with your name and affiliation?"
CONSENT_YES   = "Yes"
CONSENT_ANON  = "Yes but keep me anonymous"
CONSENT_NO    = "No — keep it private"


def load_cfg():
    with open(CFG_PATH) as f:
        return json.load(f)


def save_cfg(cfg):
    cfg["updated"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with open(CFG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")


def http_json(url, headers, data=None):
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def tally_submissions(form_id):
    """Fetch completed submissions for a Tally form. Returns a list of {label: value} dicts."""
    url = f"https://api.tally.so/forms/{form_id}/submissions?filter=completed&limit=1000"
    raw = http_json(url, {"Authorization": f"Bearer {TALLY_KEY}"})
    subs = raw.get("submissions") or raw.get("data") or []
    out = []
    for s in subs:
        answers = s.get("responses") or s.get("answers") or []
        d = {}
        for a in answers:
            label = a.get("label") or a.get("title") or a.get("key") or ""
            val = a.get("value")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            d[label.strip()] = (val or "").strip() if isinstance(val, str) else val
        out.append(d)
    return out


def find(d, key):
    """Match a field by exact label, then by case-insensitive substring."""
    if key in d:
        return d[key]
    for k, v in d.items():
        if key.lower() in (k or "").lower():
            return v
    return ""


def collect_responses(subs, roundtable_label):
    """Keep roundtable responses that consented; anonymize where asked; drop private ones."""
    kept = []
    for d in subs:
        engage = str(find(d, F_ENGAGE) or "")
        # only include roundtable + argument responses (they're what a synthesis is about)
        if roundtable_label.lower() not in engage.lower() and "respond" not in engage.lower():
            continue
        consent = str(find(d, F_CONSENT) or "")
        if CONSENT_NO.split(" —")[0].lower() in consent.lower() or "no" == consent.strip().lower():
            continue  # private
        msg = str(find(d, F_MESSAGE) or "").strip()
        if not msg:
            continue
        anon = "anonym" in consent.lower()
        kept.append({
            "name": "" if anon else str(find(d, F_NAME) or "").strip(),
            "affiliation": "" if anon else str(find(d, F_AFFIL) or "").strip(),
            "topic": str(find(d, F_TOPIC) or "").strip(),
            "message": msg,
            "anonymous": anon,
        })
    return kept


def claude_synthesis(question, responses):
    """Draft a Chatham-House-style synthesis. Returns markdown."""
    lines = []
    for i, r in enumerate(responses, 1):
        who = "Anonymous contributor" if r["anonymous"] else (
            f'{r["name"]}' + (f', {r["affiliation"]}' if r["affiliation"] else ""))
        lines.append(f'[{i}] {who}: {r["message"]}')
    corpus = "\n\n".join(lines)

    prompt = f"""You are the moderator of an independent health-policy platform's roundtable. Write a calm, analytical synthesis of the responses below, in the restrained broadsheet voice of a policy institute (never marketing, never hype).

The guiding question was: "{question}"

Write in Markdown, ~350-500 words, with:
- A one-paragraph through-line: what the responses collectively suggest.
- The main points of agreement.
- The genuine disagreements or tensions (do not smooth them over).
- One short "What this means for practice" paragraph.
Attribute specific points to contributors by name where they are named; refer to anonymous contributors as "one contributor" without inventing identities. Do not invent quotes, names, affiliations, statistics, or points that are not in the responses. If the responses are thin, say so plainly rather than padding.

RESPONSES:
{corpus}
"""
    body = {
        "model": MODEL,
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = json.dumps(body).encode()
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    resp = http_json("https://api.anthropic.com/v1/messages", headers, data)
    return "".join(block.get("text", "") for block in resp.get("content", []))


def main():
    cfg = load_cfg()
    today = datetime.date.today().isoformat()

    # keep the status field honest for the front-end even before close
    if today < cfg["open"]:
        cfg["status"] = "scheduled"; save_cfg(cfg); print("Not open yet."); return
    if today <= cfg["close"]:
        cfg["status"] = "open"; save_cfg(cfg); print("Window open — nothing to synthesize."); return
    if cfg.get("status") in ("drafted", "published") and cfg.get("synthesis_md"):
        print("Synthesis already drafted/published — skipping."); return

    if not (TALLY_KEY and ANTHROPIC_KEY):
        print("Missing TALLY_API_KEY or ANTHROPIC_API_KEY — cannot draft.", file=sys.stderr)
        cfg["status"] = "closed"; save_cfg(cfg); sys.exit(0)

    subs = tally_submissions(cfg["tally_form_id"])
    responses = collect_responses(subs, cfg.get("roundtable_engagement_label", "roundtable"))
    cfg["response_count"] = len(responses)

    if not responses:
        cfg["status"] = "closed"; save_cfg(cfg)
        print("Closed, but no consented responses to synthesize."); return

    md = claude_synthesis(cfg["question"], responses).strip()
    cfg["synthesis_md"] = md
    cfg["contributors"] = [
        {"name": r["name"], "affiliation": r["affiliation"]}
        for r in responses if not r["anonymous"] and r["name"]
    ]
    cfg["status"] = "drafted"
    cfg["approved"] = False  # human approval required to publish
    save_cfg(cfg)
    print(f"Draft synthesis written from {len(responses)} responses. Awaiting approval (set approved:true and merge).")


if __name__ == "__main__":
    main()
