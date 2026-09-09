#!/usr/bin/env python3
"""
One-off: open three questions instead of one.

Roundtable № 01's original wording — "Does the platform decide who hears the
argument?" — asked professionals to report on a mechanism they would only have
noticed if they had posted professionally and then read the analytics. Most of the
audience has neither, so the honest response was silence. That is a better
explanation of the empty first window than the cold open alone.

This reframes № 01 so it can be answered from someone's own working day, and opens
two more questions anchored to the initiative and to the medical-debt chapter, so a
quality lead and a social worker each have a way in that a communications question
never gave them.

Idempotent. Run from the website root: python3 scripts/questions_setup.py .
"""
import json, os, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
TODAY = "2026-09-09"


def edit(rel, pairs):
    """pairs are (old, new), (old, new, sentinel_str) or (old, new, expected_count)."""
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        raise SystemExit("missing: " + rel)
    s = o = open(p, encoding="utf-8").read()
    for pair in pairs:
        old, new = pair[0], pair[1]
        # a third element is either a sentinel string proving the edit is applied,
        # or an integer count when the same text legitimately appears more than once
        extra = pair[2] if len(pair) > 2 else None
        sentinel = extra if isinstance(extra, str) else new
        want = extra if isinstance(extra, int) else 1
        if sentinel in s:
            continue
        c = s.count(old)
        if c != want:
            raise SystemExit("ABORT %s: expected %d, found %d of %r" % (rel, want, c, old[:110]))
        s = s.replace(old, new)
    if s != o:
        open(p, "w", encoding="utf-8").write(s)
        print("  edited:", rel)
    else:
        print("  already current:", rel)


def write_q(cfg):
    path = os.path.join(ROOT, "roundtables", cfg["id"] + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("  written: roundtables/%s.json" % cfg["id"])


BASE = {
    "state": "open-standing",
    "close": None,
    "tally_form_id": "VLBbYM",
    "roundtable_engagement_label": "Join a roundtable discussion",
    "status": "open",
    "approved": False,
    "synthesis_md": "",
    "contributors": [],
    "response_count": 0,
    "count_synced": False,
    "updated": TODAY,
}

Q1 = dict(BASE, **{
    "id": "rt-01",
    "title": "Roundtable № 01",
    "featured": True,
    "question": "When a health message has to reach a particular group, what actually works?",
    "for_whom": "Health educators, community health workers, communications leads, clinicians and "
                "programme officers — anyone who has tried to get information to a specific group.",
    "anchor": "Anchored to Season 1: the same piece, published the same day in the same words, routed to "
              "opposite audiences on Facebook and LinkedIn.",
    # routes a submission to this question when the form's topic field mentions any of these
    "tally_match": ["№ 01", "no. 01", "reaching", "message", "audience", "platform"],
    "open": "2026-08-11",
    "first_window": {"open": "2026-08-11", "close": "2026-08-25", "response_count": 0},
    "reframed": {
        "date": TODAY,
        "from": "Does the platform decide who hears the argument?",
        "why": "The original wording asked professionals to report on platform analytics most of them have "
               "no reason to have seen.",
    },
})

Q2 = dict(BASE, **{
    "id": "rt-02",
    "title": "Roundtable № 02",
    "featured": False,
    "question": "Where does preventive care break down between recommended and completed in your setting?",
    "for_whom": "FQHC leadership and quality staff, care coordinators, community health workers, clinicians "
                "and programme managers.",
    "anchor": "Anchored to the Prevention Adoption Gap: colorectal screening reaches 44.89% at the average "
              "FQHC nationally and 48.74% in Michigan (CY2025 UDS), and 63.5% of U.S. adults against a "
              "Healthy People 2030 target of 72.8%.",
    "tally_match": ["№ 02", "no. 02", "prevention", "preventive", "screening", "completion"],
    "open": TODAY,
})

Q3 = dict(BASE, **{
    "id": "rt-03",
    "title": "Roundtable № 03",
    "featured": False,
    "question": "What does the cost of care do to the people you serve that never shows up in the record?",
    "for_whom": "Clinicians, social workers, financial counsellors, health educators and public health "
                "practitioners who see the consequences before the data does.",
    "anchor": "Anchored to Season 1, Chapter 2: 41% of U.S. adults carry medical or dental debt, and 64% of "
              "those with debt delayed or skipped care they needed (KFF, 2022).",
    "tally_match": ["№ 03", "no. 03", "cost of care", "medical debt", "debt", "affordability"],
    "open": TODAY,
})

for q in (Q1, Q2, Q3):
    write_q(q)


# --------------------------------------------------------------------- CSS
QCSS = """<style id="hs-questions">
/* Open questions — three ways in, generated by scripts/roundtable_responses.py */
.qopen{padding:var(--sec-y) 0;border-top:1px solid var(--hairline)}
.qgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;align-items:stretch}
.qcard{display:flex;flex-direction:column;gap:9px;background:var(--white);border:1px solid var(--hairline);
  border-radius:var(--r-lg);padding:20px;scroll-margin-top:calc(var(--hdr,92px) + 56px)}
.qcard.is-featured{border-color:var(--coral);box-shadow:0 0 0 1px var(--coral)}
.qcard .qk{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.qcard .qn{font-family:var(--font-mono);font-size:11px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted)}
.qcard .qtag{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;
  color:var(--coral);border:1px solid var(--coral);border-radius:999px;padding:3px 8px}
.qcard h3{margin:0;font-family:var(--font-display);font-size:19px;font-weight:600;line-height:1.24;color:var(--navy)}
.qcard .qwho{margin:0;font-size:13.5px;line-height:1.5;color:var(--muted)}
.qcard .qanchor{margin:0;font-size:12.5px;line-height:1.55;color:var(--muted);padding-left:11px;
  border-left:2px solid var(--hairline)}
.qcard .qfoot{margin-top:auto;padding-top:14px;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.qcard .qcount{font-family:var(--font-mono);font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.qcard .qfoot .btn{margin-left:auto;padding:10px 16px;font-size:13px}
/* the record, grouped by question */
.wall-group{margin-bottom:30px}
.wall-group .wg-h{margin-bottom:14px;padding-bottom:11px;border-bottom:1px solid var(--hairline)}
.wall-group .wg-n{display:block;font-family:var(--font-mono);font-size:10.5px;letter-spacing:.13em;
  text-transform:uppercase;color:var(--coral);margin-bottom:5px}
.wall-group .wg-h h3{margin:0;font-family:var(--font-display);font-size:19px;font-weight:600;color:var(--navy);line-height:1.25}
.wall-quiet{margin:0 0 22px;font-size:13.5px;color:var(--muted)}
@media(max-width:900px){.qgrid{grid-template-columns:1fr}
  .qcard .qfoot .btn{margin-left:0;width:100%;justify-content:center}}
</style></head>"""


# ------------------------------------------------------------ roundtable.html
edit("roundtable.html", [
    ("</head>", QCSS),
    # the marker the generator fills, between the hero and § 00
    ("</div></section>\n<section id=\"the-case\">",
     "</div></section>\n<!--QUESTIONS:START--><!--QUESTIONS:END-->\n<section id=\"the-case\">",
     "<!--QUESTIONS:START-->"),
    # hero: the reframed question
    ("<h1>Does the platform decide who hears the argument?</h1>\n"
     '<p class="dek">Season 1 found that <b style="color:var(--coral)">platform, not content, drove who saw a '
     'health argument</b>: the same piece routed to opposite audiences on Facebook and LinkedIn. This roundtable '
     'puts that finding to professionals.</p>',
     "<h1>When a health message has to reach a particular group, what actually works?</h1>\n"
     '<p class="dek">Season 1 found that <b style="color:var(--coral)">platform, not content, drove who saw a '
     'health argument</b>: the same piece routed to opposite audiences on Facebook and LinkedIn. This question '
     'asks what you have found that works, from your own setting rather than from anyone&rsquo;s analytics.</p>'),
    # § 00 closing line
    ("If a platform quietly sorts who hears public-health evidence, <b>what is the professional responsibility</b>: "
     "publish everywhere and accept the sorting, or plan for it? That is what the questions below ask.",
     "If where you publish quietly sorts who hears public-health evidence, <b>what is the professional "
     "responsibility</b>: publish well and accept the sorting, or design for it? That is what the prompts below ask."),
    # § 01 heading: "questions" now means the three open roundtables, so these become prompts
    ('<div class="top"><h2 class="sec">Three questions. Your name on the record.</h2></div>',
     '<div class="top"><h2 class="sec">Three prompts. Your name on the record.</h2></div>'),
    # the two positions, rewritten so neither requires analytics to hold
    ('<div class="rt2h">Publish everywhere, accept the sorting</div><p>Total reach is the point. Put the evidence '
     'on every platform, keep the message identical, and let each audience find it. Tailoring per channel risks '
     'bending the evidence to fit the medium, and a larger raw audience is still a larger audience.</p>',
     '<div class="rt2h">Publish it well, and let it find people</div><p>Get the evidence right, put it where you '
     'can, and trust the people who need it to find it. Tailoring for each channel risks bending the message to '
     'fit the medium, and a larger audience is still a larger audience.</p>'),
    ('<div class="rt2h">Plan for the routing, target the channel</div><p>If the platform decides who hears you, '
     'publishing blindly is a coin flip. Match the channel to the audience the evidence is meant to reach, a '
     'policy argument belongs where policymakers already are, and treat distribution as part of the professional '
     'responsibility, not an afterthought.</p>',
     '<div class="rt2h">Design for how it travels</div><p>If where you publish decides who hears you, publishing '
     'blindly is a coin flip. Match the channel to the people the evidence is meant to reach, a policy argument '
     'belongs where policymakers already are, and treat distribution as part of the work rather than an '
     'afterthought.</p>'),
    ('<p class="rt2note">Most professionals hold some of both. The three questions below ask which way your own '
     'experience pulls you.</p>',
     '<p class="rt2note">Most professionals hold some of both. The three prompts below ask which way your own '
     'experience pulls you. Answer any one of them.</p>'),
    # the prompts themselves: answerable from a working day, not from a dashboard
    ('<div class="c2"><span class="cn">Q1</span><div><b>Does it match your experience?</b> <span>In your setting, '
     'does platform choice change <em>who</em> actually receives health evidence, and have you seen it?</span></div></div>',
     '<div class="c2"><span class="cn">Q1</span><div><b>What have you actually done?</b> <span>Think of one time '
     'you needed information to reach a specific group. What did you do, and did it land?</span></div></div>'),
    ('<div class="c2"><span class="cn">Q2</span><div><b>What would you do differently?</b> <span>If platform '
     'routing is real, how should a practitioner or institution disseminate evidence to reach the intended '
     'audience?</span></div></div>',
     '<div class="c2"><span class="cn">Q2</span><div><b>What have you stopped doing?</b> <span>What did you try '
     'that looked reasonable and did not reach the people it was for?</span></div></div>'),
    ('<div class="c2"><span class="cn">Q3</span><div><b>Where is the risk?</b> <span>What&rsquo;s the danger of '
     'optimizing for platform reach, and how do we avoid distorting the evidence to fit the channel?</span></div></div>',
     '<div class="c2"><span class="cn">Q3</span><div><b>Where is the risk?</b> <span>If we design around how a '
     'channel behaves, what do we risk bending: the message, the evidence, or who gets left out?</span></div></div>'),
    # FAQ answer, in the page and in the structured data
    ("Roundtable No. 1 is open with no closing date. Its first response window ran 11-25 August 2026 and closed "
     "without responses, so the window was removed rather than the question. It stays anchored to Season 1's "
     "finding that the platform, not the content, drove who saw an argument.",
     "Three questions are open at once, each with no closing date, so you can answer the one your own work speaks "
     "to. Roundtable No. 1's first window ran 11-25 August 2026 and closed without responses; its question was "
     "reframed on 9 September 2026 because the original wording asked for platform analytics most professionals "
     "have no reason to have seen.", 2),
])

# ------------------------------------------------------------------ index.html
edit("index.html", [
    ('<div class="lead">One focused question per argument. Named contributors. A published synthesis.</div>',
     '<div class="lead">Three open questions, each answerable from your own work. Named contributors. A published '
     'synthesis.</div>'),
    ('<p class="q">&ldquo;Does the platform decide who hears the argument?&rdquo;</p>',
     '<p class="q">&ldquo;When a health message has to reach a particular group, what actually works?&rdquo;</p>'),
    ('<div class="anc">Anchored to Season 1&rsquo;s finding that <i>platform, not content, drove who saw a health '
     'argument</i></div>',
     '<div class="anc">Anchored to Season 1&rsquo;s finding that <i>platform, not content, drove who saw a health '
     'argument</i> &middot; two further questions are open on preventive-care completion and the cost of care</div>'),
])

# --- index.html: the campaign band under the hero -------------------------
# It was date-gated and has been hidden since 25 August, still carrying the old
# question. Make it state-driven like every other roundtable surface, and let it
# show again now the questions are standing open.
edit("index.html", [
    ('id="roundtable-campaign" data-open="2026-08-11" data-close="2026-08-25" '
     'aria-labelledby="roundtable-campaign-title" hidden>',
     'id="roundtable-campaign" data-state="open-standing" data-open="2026-08-11" data-close="" '
     'aria-labelledby="roundtable-campaign-title">'),
    ('<div class="eyebrow">Current campaign · Open through August 25</div>'
     '<h2 id="roundtable-campaign-title">Does the platform decide who hears the argument?</h2>'
     '<p>Five minutes. Named professional contributions. Moderated exchange. Published synthesis.</p>',
     '<div class="eyebrow">Open now · three questions · no closing date</div>'
     '<h2 id="roundtable-campaign-title">When a health message has to reach a particular group, '
     'what actually works?</h2>'
     '<p>Three questions are open. Answer the one your own work speaks to: five minutes, under your name, '
     'moderated, and published.</p>'),
    ('<a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">'
     'Join Roundtable № 01 <span class="ar">→</span></a>',
     '<a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">'
     'Add your response <span class="ar">→</span></a>'),
    ("<script>(function(){var p=document.getElementById('roundtable-campaign');if(!p)return;"
     "var n=new Date(),o=new Date(p.dataset.open+'T00:00:00'),c=new Date(p.dataset.close+'T23:59:59');"
     "if(n>=o&&n<=c)p.hidden=false;})();</script>",
     "<script>(function(){var p=document.getElementById('roundtable-campaign');if(!p)return;"
     "/* state is authoritative and already baked into the markup, so this settles "
     "nothing on the current path and cannot shift the page. */"
     "var st=p.dataset.state||'';"
     "if(st==='open'||st==='open-standing'){p.hidden=false;return;}"
     "if(st){p.hidden=true;return;}"
     "var n=new Date(),o=new Date(p.dataset.open+'T00:00:00'),c=new Date(p.dataset.close+'T23:59:59');"
     "if(n>=o&&n<=c)p.hidden=false;})();</script>"),
])

print("done")
