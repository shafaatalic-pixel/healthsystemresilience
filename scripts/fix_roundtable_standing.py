#!/usr/bin/env python3
"""
HSREP — Roundtable No. 01: from an expired window to a standing open question.

Context (8 Sep 2026). The Aug 11-25 window closed with no responses. The site was
still claiming "Closed - synthesis published" on the home page and "open through
August 25" in the participate section, because both state machines inferred state
from dates and assumed closed meant published.

This makes state explicit rather than inferred, and converts No. 01 into a
standing question with no closing date, with an honest record of the first window.

Run from the website root:  python3 scripts/fix_roundtable_standing.py .
Idempotent: running twice changes nothing.
"""
import json, os, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
changed = []


def edit(rel, pairs, required=True):
    """Apply (old, new, expected_count) replacements with an exact-count assertion."""
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        if required:
            raise SystemExit("missing file: " + rel)
        print("  skip (absent): " + rel)
        return
    s = orig = open(path, encoding="utf-8").read()
    for pair in pairs:
        old, new = pair[0], pair[1]
        n = pair[2] if len(pair) > 2 else 1
        if new in s:
            continue                      # already applied
        found = s.count(old)
        if found != n:
            raise SystemExit(
                "ABORT %s: expected %d occurrence(s), found %d of:\n  %r" % (rel, n, found, old[:120]))
        s = s.replace(old, new)
    if s != orig:
        open(path, "w", encoding="utf-8").write(s)
        changed.append(rel)
        print("  edited: " + rel)
    else:
        print("  already current: " + rel)


# ---------------------------------------------------------------- 1. the data
RT = {
    "id": "rt-01",
    "title": "Roundtable № 01",
    "question": "Does the platform decide who hears the argument?",
    # `state` is authoritative for what the public pages show.
    # scheduled | open | open-standing | closed-pending | published
    "state": "open-standing",
    "open": "2026-08-11",
    "close": None,
    "first_window": {"open": "2026-08-11", "close": "2026-08-25", "response_count": 0},
    "tally_form_id": "VLBbYM",
    "roundtable_engagement_label": "Join a roundtable discussion",
    # `status` stays owned by the synthesis pipeline: scheduled | open | closed | drafted | published
    "status": "open",
    "approved": False,
    "synthesis_md": "",
    "contributors": [],
    "response_count": 0,
    "count_synced": False,
    "updated": "2026-09-08",
}
rt_path = os.path.join(ROOT, "roundtables", "rt-01.json")
with open(rt_path, "w", encoding="utf-8") as f:
    json.dump(RT, f, indent=2, ensure_ascii=False)
    f.write("\n")
changed.append("roundtables/rt-01.json")
print("  written: roundtables/rt-01.json")


# ---------------------------------------------------------------- 2. home page
OLD_SM1 = """<script>(function(){var p=document.getElementById('rt-pill');if(!p)return;
var n=new Date(),o=new Date(p.dataset.open+'T00:00:00'),c=new Date(p.dataset.close+'T23:59:59');
var a1=document.getElementById('rt-cta1'),AR=' <span class="ar">→</span>';
function d(t){return Math.max(0,Math.ceil((t-n)/864e5));}
if(n<o){p.innerHTML='<i></i>Opens in '+d(o)+' days';if(a1)a1.innerHTML='See the question'+AR;}
else if(n<=c){p.innerHTML='<i></i>Open · closes in '+d(c)+' days';if(a1)a1.innerHTML='Take part'+AR;}
else{p.innerHTML='<i></i>Closed · synthesis published';if(a1)a1.innerHTML='Read the record'+AR;}})();</script>"""

NEW_SM1 = """<script>(function(){var p=document.getElementById('rt-pill');if(!p)return;
var a1=document.getElementById('rt-cta1'),AR=' <span class="ar">→</span>',n=new Date();
function d(t){return Math.max(0,Math.ceil((t-n)/864e5));}
/* state is explicit in the markup (mirrored from roundtables/rt-01.json) so it can
   never be inferred wrongly — a closed window is not the same thing as a published
   synthesis. Dates are only a fallback for older markup. */
var st=p.dataset.state||'';
if(!st){var o=new Date(p.dataset.open+'T00:00:00'),c=new Date(p.dataset.close+'T23:59:59');
 st=n<o?'scheduled':(n<=c?'open':'closed-pending');}
if(st==='scheduled'){p.innerHTML='<i></i>Opens in '+d(new Date(p.dataset.open+'T00:00:00'))+' days';if(a1)a1.innerHTML='See the question'+AR;}
else if(st==='open'){p.innerHTML='<i></i>Open · closes in '+d(new Date(p.dataset.close+'T23:59:59'))+' days';if(a1)a1.innerHTML='Add your response'+AR;}
else if(st==='open-standing'){p.innerHTML='<i></i>Open · no closing date';if(a1)a1.innerHTML='Add your response'+AR;}
else if(st==='published'){p.innerHTML='<i></i>Published record';if(a1)a1.innerHTML='Read the synthesis'+AR;}
else{p.innerHTML='<i></i>Closed · synthesis in preparation';if(a1)a1.innerHTML='Read the record'+AR;}})();</script>"""

OLD_SM2 = """<script>(function(){var p=document.getElementById('rt-pill'),a2=document.getElementById('rt-cta2');if(!p||!a2)return;
var n=new Date(),o=new Date(p.dataset.open+'T00:00:00'),c=new Date(p.dataset.close+'T23:59:59'),AR=' <span class="ar">→</span>';
if(n<o)a2.innerHTML='Register your interest'+AR;
else if(n<=c)a2.innerHTML='Respond now'+AR;
else{a2.href='roundtable.html#synthesis';a2.removeAttribute('target');a2.innerHTML='Read the synthesis'+AR;}})();</script>"""

NEW_SM2 = """<script>(function(){var p=document.getElementById('rt-pill'),a2=document.getElementById('rt-cta2');if(!p||!a2)return;
var n=new Date(),AR=' <span class="ar">→</span>',st=p.dataset.state||'';
if(!st){var o=new Date(p.dataset.open+'T00:00:00'),c=new Date(p.dataset.close+'T23:59:59');
 st=n<o?'scheduled':(n<=c?'open':'closed-pending');}
if(st==='scheduled')a2.innerHTML='Register your interest'+AR;
else if(st==='open'||st==='open-standing')a2.innerHTML='Add your response'+AR;
else if(st==='published'){a2.href='roundtable.html#synthesis';a2.removeAttribute('target');a2.innerHTML='Read the synthesis'+AR;}
else{a2.href='roundtable.html#synthesis';a2.removeAttribute('target');a2.innerHTML='Read the record'+AR;}})();</script>"""

edit("index.html", [
    # the pill carries the state, and its no-JS text already matches what the script writes
    ('<span class="pill" id="rt-pill" data-open="2026-08-11" data-close="2026-08-25"><i></i>Opens Aug 11 · 14 days</span>',
     '<span class="pill" id="rt-pill" data-state="open-standing" data-open="2026-08-11" data-close=""><i></i>Open · no closing date</span>', 1),
    ('<a class="btn accent" id="rt-cta1" href="roundtable.html">Take part <span class="ar">→</span></a>',
     '<a class="btn accent" id="rt-cta1" href="roundtable.html">Add your response <span class="ar">→</span></a>', 1),
    (OLD_SM1, NEW_SM1, 1),
    (OLD_SM2, NEW_SM2, 1),
    # a standing question has no window, so the steps stop referring to one
    ('<b>Moderated exchange</b><span class="d">Selected responses receive replies and follow-ups over the window.</span>',
     '<b>Moderated exchange</b><span class="d">Selected responses receive replies and follow-ups.</span>', 1),
    ('<b>Published synthesis</b><span class="d">Conclusions and disagreements published with named contributors, a citable record.</span>',
     '<b>Published synthesis</b><span class="d">Once enough responses are in, conclusions and disagreements are published with named contributors, a citable record.</span>', 1),
    # participate section: the hardcoded campaign window is what could never expire
    ('<div class="lead">The current priority is Roundtable № 01. Partnership and newsletter options remain available without competing for attention.</div>',
     '<div class="lead">Roundtable № 01 is open, with no closing date. Partnership and newsletter options remain available without competing for attention.</div>', 1),
    ('<div class="n">CURRENT CAMPAIGN · OPEN THROUGH AUGUST 25</div>',
     '<div class="n">OPEN NOW · NO CLOSING DATE</div>', 1),
])


# --------------------------------------------------------- 3. roundtable page
PILL_OPEN = ('<span style="display:inline-flex;align-items:center;gap:9px;font-family:var(--font-mono);'
             'font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#267A69;border:1px solid #267A69;'
             'border-radius:999px;padding:7px 15px"><span style="width:8px;height:8px;border-radius:50%;'
             'background:#267A69"></span>Open · no closing date</span>')
RNG_OPEN = (' <span style="font-family:var(--font-mono);font-size:12px;color:var(--muted);letter-spacing:.03em;'
            'white-space:nowrap">Opened 11 August 2026</span>')

OLD_PILL_CLOSED = ('<span style="display:inline-flex;align-items:center;gap:9px;font-family:var(--font-mono);'
                   'font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#65717E;border:1px solid #65717E;'
                   'border-radius:999px;padding:7px 15px"><span style="width:8px;height:8px;border-radius:50%;'
                   'background:#65717E"></span>Closed · synthesis in preparation</span>'
                   ' <span style="font-family:var(--font-mono);font-size:12px;color:var(--muted);letter-spacing:.03em;'
                   'white-space:nowrap">Aug 11, Aug 25, 2026 &middot; 14-day window</span>')

RECORD_HTML = (
    '<p class="big">The first response window ran from 11 to 25 August 2026 and closed without any responses. '
    'There is nothing to synthesise yet, so nothing is published here.</p>'
    '<p>The reason is worth stating, because it is the more useful finding. The question was opened cold: '
    'announced to a general audience rather than put to named professionals first, and given a deadline before '
    'anyone had a reason to meet it. The next question will be put to a first group by hand before it opens to everyone.</p>'
    '<p>The question itself has not expired, so the window has been removed rather than the question. It stays open '
    'with no closing date. When enough responses are on the record, a moderated synthesis will be published here, '
    'naming the contributors who consented to be named.</p>')

OLD_RENDER = """  function renderDates(open,close,now){
    var MO=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var rng=' <span style="font-family:var(--font-mono);font-size:12px;color:var(--muted);letter-spacing:.03em;white-space:nowrap">'+MO[open.getMonth()]+' '+open.getDate()+', '+MO[close.getMonth()]+' '+close.getDate()+', '+close.getFullYear()+' &middot; 14-day window</span>';
    if(now<open){"""

NEW_RENDER = """  function renderStanding(){
    box.innerHTML=pill('Open \\u00b7 no closing date','#267A69')+' <span style="font-family:var(--font-mono);font-size:12px;color:var(--muted);letter-spacing:.03em;white-space:nowrap">Opened 11 August 2026</span>';
    cta.innerHTML='<a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">Add your response &rarr;</a> <a class="btn ghost on-dark" href="#synthesis">What the record holds &rarr;</a>';
    synth.innerHTML=RECORD_SO_FAR;
  }
  function renderDates(open,close,now){
    var MO=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var rng=' <span style="font-family:var(--font-mono);font-size:12px;color:var(--muted);letter-spacing:.03em;white-space:nowrap">'+MO[open.getMonth()]+' '+open.getDate()+', '+MO[close.getMonth()]+' '+close.getDate()+', '+close.getFullYear()+' &middot; 14-day window</span>';
    if(now<open){"""

OLD_DISPATCH = """  const now=new Date();
  fetch('roundtables/rt-01.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(cfg=>{
    if(cfg&&cfg.approved&&cfg.synthesis_md){ renderPublished(cfg); return; }
    const o=(cfg&&cfg.open)||box.dataset.open, c=(cfg&&cfg.close)||box.dataset.close;
    renderDates(new Date(o+'T00:00:00'),new Date(c+'T23:59:59'),now);
  }).catch(()=>{
    renderDates(new Date(box.dataset.open+'T00:00:00'),new Date(box.dataset.close+'T23:59:59'),now);
  });"""

NEW_DISPATCH = """  const now=new Date();
  function paint(cfg){
    if(cfg&&cfg.approved&&cfg.synthesis_md){ renderPublished(cfg); return; }
    /* state is authoritative; dates are only a fallback. A closed window is not a
       published synthesis, and a question with no close date never expires. */
    const st=(cfg&&cfg.state)||box.dataset.state||'';
    if(st==='open-standing'){ renderStanding(); return; }
    const o=(cfg&&cfg.open)||box.dataset.open, c=(cfg&&cfg.close)||box.dataset.close;
    if(!c){ renderStanding(); return; }
    renderDates(new Date(o+'T00:00:00'),new Date(c+'T23:59:59'),now);
  }
  fetch('roundtables/rt-01.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(paint).catch(()=>paint(null));"""

edit("roundtable.html", [
    # --- head
    ('<meta name="description" content="HSREP Roundtable № 01, a structured, time-boxed professional discussion on how platform choice shapes who receives health evidence.',
     '<meta name="description" content="HSREP Roundtable № 01, an open, on-the-record professional discussion of how platform choice shapes who receives health evidence.', 1),
    # --- hero: state attribute + honest pill, matching what the script writes
    ('<div id="rtstatus" data-open="2026-08-11" data-close="2026-08-25" style="margin:14px 0 6px">' + OLD_PILL_CLOSED,
     '<div id="rtstatus" data-state="open-standing" data-open="2026-08-11" data-close="" style="margin:14px 0 6px">' + PILL_OPEN + RNG_OPEN, 1),
    ('<span><span style="color:#8ea1b8">When</span> &nbsp;<b style="color:#fff">August 11-25, 2026</b> · 14-day window</span>',
     '<span><span style="color:#8ea1b8">When</span> &nbsp;<b style="color:#fff">Open now</b> · no closing date</span>', 1),
    ('<div id="rtcta" class="cta"><a class="btn ghost on-dark" href="#synthesis">Read the record &rarr;</a> <a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">Join the next roundtable &rarr;</a></div>',
     '<div id="rtcta" class="cta"><a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">Add your response &rarr;</a> <a class="btn ghost on-dark" href="#synthesis">What the record holds &rarr;</a></div>', 1),
    # --- how it works: no window any more
    ('<div class="rd rv"><div class="rk">Window · 14 days</div><div><b>Respond</b>',
     '<div class="rd rv"><div class="rk">Any time</div><div><b>Respond</b>', 1),
    ('<div class="rd rv"><div class="rk">On close</div><div><b>Synthesis</b><p>When the window ends, responses are reviewed and a single published synthesis names consented contributors and the through-line.</p></div></div>',
     '<div class="rd rv"><div class="rk">When there is enough</div><div><b>Synthesis</b><p>Once the question has drawn enough responses, they are reviewed and a single published synthesis names consented contributors and the through-line.</p></div></div>', 1),
    # --- section 03: the honest record
    ('<div id="rtsynth" class="rich rv" style="max-width:76ch"><p class="big">The response window has closed. The moderated synthesis, naming consented contributors and the through-line, is in preparation and will be posted here.</p></div>',
     '<div id="rtsynth" class="rich rv" style="max-width:76ch">' + RECORD_HTML + '</div>', 1),
    ('<p class="srcnote rv">Contributors and responses are published only when real, consented, and attributable, never estimated. Until the window closes and responses are reviewed, this record stays empty by design.</p>',
     '<p class="srcnote rv">Contributors and responses are published only when they are real, consented and attributable. Nothing here is estimated, and nothing is filled in to look fuller than it is.</p>', 1),
    # --- the render script
    (OLD_RENDER, NEW_RENDER, 1),
    (OLD_DISPATCH, NEW_DISPATCH, 1),
    ("  const days=(d,now)=>Math.max(0,Math.ceil((d-now)/86400000));",
     "  const days=(d,now)=>Math.max(0,Math.ceil((d-now)/86400000));\n  const RECORD_SO_FAR=" + json.dumps(RECORD_HTML) + ";", 1),
    # --- stage rail: handle a question with no closing date
    ("""  var open=new Date(st.getAttribute('data-open')+'T00:00:00');
  var close=new Date(st.getAttribute('data-close')+'T23:59:59');
  var now=new Date();
  var d=function(t){return Math.max(0,Math.ceil((t-now)/86400000));};
  var rds=road.querySelectorAll('.rd');
  if(!rds.length) return;
  var cur,live;
  if(now<open){cur=0;live='Opens in '+d(open)+' days';}
  else if(now<=close){cur=0;live='Closes in '+d(close)+' days';}
  else {cur=1;live='Window closed';}""",
     """  var open=new Date(st.getAttribute('data-open')+'T00:00:00');
  var closeAttr=st.getAttribute('data-close');
  var close=closeAttr?new Date(closeAttr+'T23:59:59'):null;
  var stateAttr=st.getAttribute('data-state')||'';
  var now=new Date();
  var d=function(t){return Math.max(0,Math.ceil((t-now)/86400000));};
  var rds=road.querySelectorAll('.rd');
  if(!rds.length) return;
  var cur,live;
  if(stateAttr==='open-standing'||!close){cur=0;live='Open now';}
  else if(now<open){cur=0;live='Opens in '+d(open)+' days';}
  else if(now<=close){cur=0;live='Closes in '+d(close)+' days';}
  else {cur=1;live='Window closed';}""", 1),
    # --- FAQ, in the page and in the structured data
    ("The asynchronous format runs about fourteen days and is tied to a specific finding. Roundtable No. 1 runs August 11-25, 2026, anchored to Season 1's finding that the platform, not the content, drove who saw an argument.",
     "Roundtable No. 1 is open with no closing date. Its first response window ran 11-25 August 2026 and closed without responses, so the window was removed rather than the question. It stays anchored to Season 1's finding that the platform, not the content, drove who saw an argument.", 2),
])


# ------------------------------------------------- 4. shared announcement bar
edit("assets/analytics.js", [
    (""" function campaignState(cfg) {
 var now = new Date();
 var open = new Date((cfg.open || "2026-08-11") + "T00:00:00");
 var close = new Date((cfg.close || "2026-08-25") + "T23:59:59");
 if (now >= open && now <= close) return "roundtable";
 if (now > close) return "season2";
 return "upcoming";
 }""",
     """ function campaignState(cfg) {
 /* an explicit state in rt-01.json wins over anything inferred from dates */
 if (cfg.state === "open" || cfg.state === "open-standing") return "roundtable";
 if (cfg.state === "scheduled") return "upcoming";
 if (cfg.state === "closed-pending" || cfg.state === "published") return "season2";
 var now = new Date();
 var open = new Date((cfg.open || "2026-08-11") + "T00:00:00");
 var close = new Date((cfg.close || "2026-08-25") + "T23:59:59");
 if (now >= open && now <= close) return "roundtable";
 if (now > close) return "season2";
 return "upcoming";
 }""", 1),
    (""" if (state === "roundtable") {
 mainHref = "https://tally.so/r/VLBbYM"; kicker = "Roundtable № 01";
 desktop = "Open through " + fmtDate(closeD, true) + ".";
 mobile = "Open through " + fmtDate(closeD) + "."; action = "Respond now →"; actionMobile = action;
 }""",
     """ if (state === "roundtable") {
 mainHref = "https://tally.so/r/VLBbYM"; kicker = "Roundtable № 01";
 if (cfg.state === "open-standing" || !cfg.close) {
 desktop = "Open now, no closing date."; mobile = "Open now.";
 } else {
 desktop = "Open through " + fmtDate(closeD, true) + "."; mobile = "Open through " + fmtDate(closeD) + ".";
 }
 action = "Add your response →"; actionMobile = "Respond →";
 }""", 1),
    # the pre-fetch fallback now matches reality, so the bar renders once and never re-renders
    (' var fallback = { open: "2026-08-11", close: "2026-08-25" };',
     ' var fallback = { state: "open-standing", open: "2026-08-11", close: null };', 1),
])


# --------------------------------------------------------- 5. private console
edit("roundtable-console.html", [
    ("""  if(cfg.approved && cfg.synthesis_md) return {key:'pub',cls:'b-pub',label:'Published · live on site',phase:'published',open:open,close:close};""",
     """  if(cfg.approved && cfg.synthesis_md) return {key:'pub',cls:'b-pub',label:'Published · live on site',phase:'published',open:open,close:close};
  if(cfg.state==='open-standing')      return {key:'open',cls:'b-open',label:'Open · no closing date',phase:'standing',open:open,close:null};""", 1),
    ("""  h+='<div class="metric"><div class="k">Window</div><div class="v" style="font-size:1rem;padding-top:8px"><span class="win">'+fmt(s.open)+' → '+fmt(s.close)+'</span></div></div>';""",
     """  h+='<div class="metric"><div class="k">Window</div><div class="v" style="font-size:1rem;padding-top:8px"><span class="win">'+fmt(s.open)+' → '+(s.close?fmt(s.close):'no closing date')+'</span></div></div>';""", 1),
    ("""  }else if(s.phase==='open'){""",
     """  }else if(s.phase==='standing'){
    h+='<p class="empty">This question is open with no closing date. Use “Check participation” for the live count, then draft the synthesis when there is enough on the record to be worth synthesising.'+esc(upd)+'</p>';
  }else if(s.phase==='open'){""", 1),
], required=False)


# ------------------------------------------------------- 6. the two automations
edit("scripts/roundtable_synth.py", [
    ('    if today <= cfg["close"]:',
     '    if not cfg.get("close") or today <= cfg["close"]:'),
], required=False)
# note: the count-sync script already tolerates a null close ("if cfg.get('close') and ...")


# ------------------------------- 7. teach the CLS pass to read the real state
edit("scripts/cls_pagefix.py", [
    (r'''            h2 = re.sub(r'<a class="(btn accent|cta|hs-hcta)"[^>]*>Participate</a>', sub_cta, h)''',
     r'''            h2 = re.sub(r'<a class="(btn accent|cta|hs-hcta)"[^>]*>(?:Participate|Season 2 updates|Join Roundtable|Roundtable record|Add your response|Request presentation)</a>', sub_cta, h)'''),
    ("""today = datetime.date.today()
open_d, close_d = datetime.date(2026, 8, 11), datetime.date(2026, 8, 25)   # rt-01 dates (fallback in analytics.js)
state = 'roundtable' if open_d <= today <= close_d else ('season2' if today > close_d else 'upcoming')""",
     """today = datetime.date.today()

def campaign_state():
    \"\"\"Mirror analytics.js campaignState() so the baked header CTA matches what the
    script would set, and nothing is relabelled after first paint.\"\"\"
    cfg = {}
    try:
        import json as _json
        with open(os.path.join(root, 'roundtables', 'rt-01.json'), encoding='utf-8') as f:
            cfg = _json.load(f)
    except Exception:
        pass
    st = cfg.get('state')
    if st in ('open', 'open-standing'): return 'roundtable'
    if st == 'scheduled':               return 'upcoming'
    if st in ('closed-pending', 'published'): return 'season2'
    o = cfg.get('open') or '2026-08-11'
    c = cfg.get('close') or '2026-08-25'
    open_d = datetime.date(*[int(x) for x in o.split('-')])
    close_d = datetime.date(*[int(x) for x in c.split('-')])
    return 'roundtable' if open_d <= today <= close_d else ('season2' if today > close_d else 'upcoming')

state = campaign_state()"""),
], required=False)


print("\n%d file(s) changed:" % len(changed))
for c in changed:
    print("  " + c)
print("\nNext: re-run  python3 scripts/cls_pagefix.py .  so every page's baked header CTA")
print("matches the new campaign state (it now reads roundtables/rt-01.json).")
