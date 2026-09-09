#!/usr/bin/env python3
"""
Corrections advised by the 9 September analytics read.

Three things, all sourced to a measured number rather than a hunch:

1. The response form moves onto the page. Eleven outbound clicks to tally.so
   since launch, zero submissions. Every "answer" control now points at an
   on-page #respond section holding the form in a fixed-height frame, so the
   off-domain hop is gone and nothing shifts after first paint.

2. Roundtable No. 02 becomes the featured question. The Initiative page drew
   189 section views and 20 CTA clicks since launch; the Roundtable drew 18 and
   6. No. 02 is the question that belongs to the Prevention Adoption Gap, so it
   is the one the audience is already standing next to.

3. The Initiative page carries the ask. That is where the attention is.

Also clears the last stale share strings, which still advertised the closed
11-25 August window and the old question.

Idempotent. Run from the website root: python3 scripts/fix_response_path.py .
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

Q2 = "Where does preventive care break down between recommended and completed in your setting?"


def edit(rel, pairs):
    """pairs are (old, new), (old, new, sentinel_str) or (old, new, expected_count).
    A str third element proves the edit is already applied when `new` itself is
    rewritten later by the generator; an int asserts how many times `old` occurs."""
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        raise SystemExit("missing: " + rel)
    s = o = open(p, encoding="utf-8").read()
    for pair in pairs:
        old, new = pair[0], pair[1]
        third = pair[2] if len(pair) > 2 else None
        sentinel = third if isinstance(third, str) else new
        want = third if isinstance(third, int) else 1
        if sentinel in s:
            continue
        c = s.count(old)
        if c != want:
            raise SystemExit("ABORT %s: found %d of %r (wanted %d)" % (rel, c, old[:110], want))
        s = s.replace(old, new)
    if s != o:
        open(p, "w", encoding="utf-8").write(s)
        print("  edited:", rel)
    else:
        print("  already current:", rel)


def set_featured(fid, value):
    p = os.path.join(ROOT, "roundtables", fid + ".json")
    cfg = json.load(open(p, encoding="utf-8"))
    if cfg.get("featured") == value:
        print("  already current:", fid, "featured =", value)
        return
    cfg["featured"] = value
    json.dump(cfg, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("  set %s featured = %s" % (fid, value))


# --------------------------------------------------------------------------
# 1. Featured question: No. 01 -> No. 02
# --------------------------------------------------------------------------
set_featured("rt-01", False)
set_featured("rt-02", True)

# --------------------------------------------------------------------------
# 2. roundtable.html — the on-page form, and the hero that leads to it
# --------------------------------------------------------------------------
RESPOND_CSS = """<style id="hs-respond">
/* The response form, embedded rather than linked. Eleven people clicked
   through to tally.so since launch and none came back with a submission, so
   the off-domain hop is the thing being removed here. The frame is a fixed
   height at each breakpoint: the iframe never resizes itself, so this section
   cannot shift the page after first paint. */
#respond{padding:var(--sec-y) 0;background:var(--panel)}
.respond-frame{margin-top:26px;background:var(--white);border:1px solid var(--hairline);
  border-radius:var(--r-lg);box-shadow:var(--sh-xs);overflow:hidden;height:820px}
.respond-frame iframe{display:block;width:100%;height:820px;border:0}
.respond-alt{margin:14px 0 0;font-size:14px;color:var(--muted)}
.respond-alt a{color:var(--muted);border-bottom:1px dotted var(--hairline);text-decoration:none}
.respond-alt a:hover,.respond-alt a:focus-visible{color:var(--coral);border-bottom-color:var(--coral)}
.respond-which{display:inline-block;font-family:var(--font-mono);font-size:12px;letter-spacing:.04em;
  color:var(--navy);background:var(--coral-wash);border-radius:999px;padding:3px 9px}
@media(max-width:720px){.respond-frame,.respond-frame iframe{height:960px}}
</style></head>"""

RESPOND_SECTION = """<!--QUESTIONS:END-->
<section id="respond"><div class="wrap">
<div class="shead rv"><div class="eyebrow">Add your response</div><div class="top"><h2 class="sec">Answer here. About five minutes.</h2><div class="lead">The form asks which question you are answering. Write <span class="respond-which">№ 01</span> <span class="respond-which">№ 02</span> or <span class="respond-which">№ 03</span> in that field and your response is filed against that question. Every response is read before anything appears on the record, and nothing is published without your consent.</div></div></div>
<div class="respond-frame rv"><iframe src="https://tally.so/embed/VLBbYM?alignLeft=1&amp;transparentBackground=1" title="HSREP Roundtable response form" loading="lazy" width="100%" height="820" frameborder="0" marginheight="0" marginwidth="0"></iframe></div>
<p class="respond-alt">If the form will not load, <a href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">open it in a new tab</a> or write to <a href="mailto:contact@hsraep.org">contact@hsraep.org</a>.</p>
</div></section>"""

SHARE_TEXT = ("Three%20questions%20are%20open%20at%20HSREP%20Roundtables%20%E2%80%94%20"
              "answer%20the%20one%20your%20own%20work%20speaks%20to.")
OLD_SHARE = ("Join%20HSREP%20Roundtable%20No.1%20%E2%80%94%20does%20the%20platform%20decide%20"
             "who%20hears%20a%20health%20argument%3F%20Open%20Aug%2011%E2%80%9325%2C%202026")

edit("roundtable.html", [
    # hero
    ("<h1>When a health message has to reach a particular group, what actually works?</h1>",
     "<h1>%s</h1>" % Q2),
    ('<p class="dek">Season 1 found that <b style="color:var(--coral)">platform, not content, drove who '
     'saw a health argument</b>: the same piece routed to opposite audiences on Facebook and LinkedIn. '
     'This question asks what you have found that works, from your own setting rather than from anyone&rsquo;s '
     'analytics.</p>',
     '<p class="dek">Colorectal screening reaches <b style="color:var(--coral)">44.89% at the average '
     'federally qualified health centre</b> and 48.74% in Michigan. The services exist and are paid for. '
     'This question asks where, in your own setting, the distance between recommended and completed '
     'actually opens up. Two further questions are open beside it.</p>'),
    # the section that now holds the form
    ("<!--QUESTIONS:END-->", RESPOND_SECTION, '<section id="respond">'),
    ("</head>", RESPOND_CSS),
    # stale share strings, still advertising the closed August window
    (OLD_SHARE, SHARE_TEXT, 2),
])

# every "answer" control on the page now lands on the form instead of leaving
p = os.path.join(ROOT, "roundtable.html")
s = o = open(p, encoding="utf-8").read()
OUT = 'href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener"'
KEEP = '<a ' + OUT + '>open it in a new tab</a>'
# the fallback inside #respond is the one link that must still leave the site
s = s.replace(KEEP, "@@KEEP@@")
n = s.count(OUT)
s = s.replace(OUT, 'href="#respond"').replace("@@KEEP@@", KEEP)
if s != o:
    open(p, "w", encoding="utf-8").write(s)
    print("  roundtable.html: %d outbound response links now point at #respond" % n)
else:
    print("  already current: roundtable.html response links")

# --------------------------------------------------------------------------
# 3. index.html — the card and the campaign band lead with No. 02
# --------------------------------------------------------------------------
edit("index.html", [
    ('<p class="q">&ldquo;When a health message has to reach a particular group, what actually works?&rdquo;</p>',
     '<p class="q">&ldquo;%s&rdquo;</p>' % Q2),
    ('<div class="anc">Anchored to Season 1&rsquo;s finding that <i>platform, not content, drove who saw a '
     'health argument</i> &middot; two further questions are open on preventive-care completion and the cost '
     'of care</div>',
     '<div class="anc">Anchored to the Prevention Adoption Gap: <i>44.89% colorectal screening at the average '
     'FQHC, 48.74% in Michigan</i> &middot; two further questions are open on health messaging and the cost '
     'of care</div>'),
    ('<span class="no">Roundtable <b>№ 01</b></span>', '<span class="no">Roundtable <b>№ 02</b></span>'),
    ('<h3>Join Roundtable № 01</h3>', '<h3>Join Roundtable № 02</h3>'),
    ('<div class="rt-campaign-mark" aria-hidden="true"><span>№</span><strong>01</strong></div>',
     '<div class="rt-campaign-mark" aria-hidden="true"><span>№</span><strong>02</strong></div>'),
    ('<h2 id="roundtable-campaign-title">When a health message has to reach a particular group, what actually '
     'works?</h2>',
     '<h2 id="roundtable-campaign-title">%s</h2>' % Q2),
    ('<a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">Add your response '
     '<span class="ar">→</span></a>',
     '<a class="btn accent" href="roundtable.html#respond">Add your response <span class="ar">→</span></a>'),
    ('<a class="btn accent" id="rt-cta2" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">'
     'Add your response <span class="ar">→</span></a>',
     '<a class="btn accent" id="rt-cta2" href="roundtable.html#respond">Add your response '
     '<span class="ar">→</span></a>'),
])

# --------------------------------------------------------------------------
# 4. initiative.html — the ask, where the attention actually is
# --------------------------------------------------------------------------
INIT_CSS = """<style id="hs-initrt">
/* The Initiative page drew 189 section views and 20 CTA clicks since launch
   against the Roundtable page's 18 and 6. The open question about preventive-care
   completion belongs to this argument, so the ask sits here too. */
#rt-ask{padding:var(--sec-y) 0;background:var(--panel)}
.rtask{background:var(--white);border:1px solid var(--hairline);border-left:3px solid var(--coral);
  border-radius:var(--r-lg);box-shadow:var(--sh-xs);padding:30px 32px;max-width:80ch}
.rtask .k{font-family:var(--font-mono);font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;
  color:var(--muted);margin-bottom:10px}
.rtask h2{font-family:var(--font-display);font-size:clamp(21px,2.4vw,27px);line-height:1.28;
  color:var(--heading);margin:0 0 12px;font-weight:600}
.rtask p{margin:0 0 16px;font-size:15.5px;line-height:1.62;color:var(--ink)}
.rtask .rf{margin-top:20px}
@media(max-width:720px){.rtask{padding:24px 22px}}
</style></head>"""

INIT_SECTION = """<section id="rt-ask"><div class="wrap">
<div class="rtask rv">
<div class="k">Open question № 02 &middot; no closing date</div>
<h2>Where does preventive care break down between recommended and completed in your setting?</h2>
<p>The Prevention Adoption Gap is the argument on this page. The open question is the same argument put back to the people who watch it happen: colorectal screening reaches 44.89% at the average federally qualified health centre and 48.74% in Michigan, and the reasons are not in the published figures.</p>
<p>Answer from your own setting. Five minutes, under your name and affiliation, read before anything is published, and nothing published without your consent.</p>
<div class="rf"><a class="btn accent" href="roundtable.html#respond">Add your response <span class="ar">&rarr;</span></a> <a class="btn ghost" href="roundtable.html">See all three questions <span class="ar">&rarr;</span></a></div>
</div>
</div></section>
<section id="faq">"""

edit("initiative.html", [
    ("</head>", INIT_CSS),
    ('<section id="faq">', INIT_SECTION, '<section id="rt-ask">'),
])

# --------------------------------------------------------------------------
# 5. The generator writes the same links, so it has to agree
# --------------------------------------------------------------------------
edit("scripts/roundtable_responses.py", [
    # cards: answer on the page, do not leave it
    ("""        bits.append('<a class="btn accent" href="%s" target="_blank" rel="noopener">Answer this &rarr;</a></div>'
                    % esc(q_form_url(q)))""",
     """        bits.append('<a class="btn accent" href="#respond">Answer this &rarr;</a></div>')"""),
    # the empty state's call to action, same reasoning
    ("""                '<p class="wall-cta"><a class="btn accent" href="%s" target="_blank" rel="noopener">'
                'Be the first on the record &rarr;</a></p></div>' % esc(q_form_url(questions[0])))""",
     """                '<p class="wall-cta"><a class="btn accent" href="#respond">'
                'Be the first on the record &rarr;</a></p></div>')"""),
    # the featured question leads the grid, whichever one it is
    ("""    featured = next((q for q in questions if q.get("featured")), questions[0])""",
     """    featured = next((q for q in questions if q.get("featured")), questions[0])
    # the featured question leads the grid and the record, whichever one it is
    questions.sort(key=lambda q: (not q.get("featured"), q["id"]))"""),
])

print("done")
