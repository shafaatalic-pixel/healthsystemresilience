#!/usr/bin/env python3
"""
One-off: prepare the pages for the response wall.

Adds the render markers, the wall's CSS, and stops the standing-state script from
overwriting the generated wall. After this, scripts/roundtable_responses.py owns
everything between the markers.

Idempotent. Run from the website root: python3 scripts/wall_setup.py .
"""
import os, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")


def edit(rel, pairs):
    """pairs are (old, new) or (old, new, sentinel). The sentinel is what proves the
    edit is already applied, for replacements whose output is later rewritten by the
    generator (the wall markers) and so cannot be matched literally."""
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        raise SystemExit("missing: " + rel)
    s = o = open(p, encoding="utf-8").read()
    for pair in pairs:
        old, new = pair[0], pair[1]
        sentinel = pair[2] if len(pair) > 2 else new
        if sentinel in s:
            continue
        c = s.count(old)
        if c != 1:
            raise SystemExit("ABORT %s: found %d of %r" % (rel, c, old[:110]))
        s = s.replace(old, new)
    if s != o:
        open(p, "w", encoding="utf-8").write(s)
        print("  edited:", rel)
    else:
        print("  already current:", rel)


WALL_CSS = """<style id="hs-wall">
/* Response wall — the record of who answered, rendered statically by
   scripts/roundtable_responses.py so nothing shifts after first paint. */
#rtsynth:empty{display:none}
.wall-counts{display:flex;flex-wrap:wrap;gap:10px 26px;align-items:baseline;margin:0 0 22px;
  font-family:var(--font-mono);font-size:11.5px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.wall-counts b{font-size:17px;font-weight:600;color:var(--navy);margin-right:5px;font-variant-numeric:tabular-nums}
.wall-counts .wc-q b{color:var(--muted)}
.wall{display:flex;flex-direction:column;gap:12px;margin-bottom:26px}
.wall .resp{background:var(--white);border:1px solid var(--hairline);border-radius:var(--r-lg);
  padding:18px 20px;scroll-margin-top:calc(var(--hdr,92px) + 56px)}
.wall .resp:target{border-color:var(--coral);box-shadow:0 0 0 1px var(--coral)}
.wall .resp-h{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px;margin-bottom:9px}
.wall .resp-n{font-family:var(--font-body);font-size:15px;font-weight:700;color:var(--navy)}
.wall .resp-a{font-size:13.5px;color:var(--muted)}
.wall .resp-d{margin-left:auto;font-family:var(--font-mono);font-size:11.5px;color:var(--muted);white-space:nowrap}
.wall .resp p{margin:0 0 10px;font-size:15.5px;line-height:1.62;color:var(--ink);max-width:70ch}
.wall .resp p:last-of-type{margin-bottom:0}
.wall .resp-f{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-top:13px;
  padding-top:11px;border-top:1px solid var(--hairline)}
.wall .resp-chip{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;
  color:var(--muted);border:1px solid var(--hairline);border-radius:999px;padding:4px 10px}
.wall .resp-link{margin-left:auto;font-family:var(--font-mono);font-size:11.5px;color:var(--muted);
  text-decoration:none;border-bottom:1px dotted var(--hairline)}
.wall .resp-link:hover,.wall .resp-link:focus-visible{color:var(--coral);border-bottom-color:var(--coral)}
.wall-foot{margin-bottom:20px;color:var(--muted)}
.wall-foot p{font-size:14px}
.wall-cta{margin:0 0 4px}
@media(max-width:720px){
  .wall .resp{padding:16px}
  .wall .resp-d{margin-left:0;flex-basis:100%}
  .wall .resp-link{margin-left:0;flex-basis:100%;word-break:break-all}
}
/* the roundtable card's live count on the home page */
.rtcount{margin-top:10px;font-family:var(--font-mono);font-size:11.5px;letter-spacing:.05em;
  text-transform:uppercase;color:var(--green)}
</style></head>"""

# --- roundtable.html -------------------------------------------------------
OLD_SEC3 = ('<div id="rtsynth" class="rich rv" style="max-width:76ch"><p class="big">The first response window '
            'ran from 11 to 25 August 2026 and closed without any responses. There is nothing to synthesise yet, '
            'so nothing is published here.</p><p>The reason is worth stating, because it is the more useful '
            'finding. The question was opened cold: announced to a general audience rather than put to named '
            'professionals first, and given a deadline before anyone had a reason to meet it. The next question '
            'will be put to a first group by hand before it opens to everyone.</p><p>The question itself has not '
            'expired, so the window has been removed rather than the question. It stays open with no closing '
            'date. When enough responses are on the record, a moderated synthesis will be published here, naming '
            'the contributors who consented to be named.</p></div>')

NEW_SEC3 = ('<div id="rtsynth" class="rich rv" style="max-width:76ch"></div>\n'
            '<!--WALL:START--><!--WALL:END-->')

# renderStanding() must not write into #rtsynth any more: that element now holds the
# synthesis only, and the wall below it is static HTML owned by the generator.
OLD_STANDING = """    cta.innerHTML='<a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">Add your response &rarr;</a> <a class="btn ghost on-dark" href="#synthesis">What the record holds &rarr;</a>';
    synth.innerHTML=RECORD_SO_FAR;
  }"""
NEW_STANDING = """    cta.innerHTML='<a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">Add your response &rarr;</a> <a class="btn ghost on-dark" href="#synthesis">What the record holds &rarr;</a>';
    /* #rtsynth holds the synthesis only. The response wall beneath it is static
       HTML written by scripts/roundtable_responses.py — never overwrite it here. */
  }"""

def drop_dead_const(rel):
    """RECORD_SO_FAR existed only for renderStanding(); the wall replaces it."""
    p = os.path.join(ROOT, rel)
    src = open(p, encoding="utf-8").read()
    i = src.find('\n  const RECORD_SO_FAR=')
    if i < 0:
        print("  already current:", rel, "(no dead constant)")
        return
    j = src.index("\n", i + 1)          # the constant occupies exactly one line
    open(p, "w", encoding="utf-8").write(src[:i] + src[j:])
    print("  removed dead RECORD_SO_FAR from", rel)


edit("roundtable.html", [
    ("</head>", WALL_CSS),
    (OLD_SEC3, NEW_SEC3, "<!--WALL:START-->"),
    (OLD_STANDING, NEW_STANDING),
])
drop_dead_const("roundtable.html")

# --- index.html ------------------------------------------------------------
edit("index.html", [
    ('<div class="rm"><span><b>\u2713</b> Real name &amp; affiliation</span>',
     '<!--RTCOUNT:START--><!--RTCOUNT:END--><div class="rm"><span><b>\u2713</b> Real name &amp; affiliation</span>', '<!--RTCOUNT:START-->'),
])
# --- roundtable-console.html ----------------------------------------------
# The console is where moderation actually happens, so it needs to show what is
# waiting. It reads the same responses file the public wall is generated from.
edit("roundtable-console.html", [
    ("""  var rc=(typeof cfg.response_count==='number')?cfg.response_count:0;""",
     """  var rc=(typeof cfg.response_count==='number')?cfg.response_count:0;
  var wc=(cfg._wall&&cfg._wall.counts)||null;"""),
    ("""  h+='<div class="metric"><div class="k">Responses</div><div class="v">'+rc+' <small>'+srcLbl+'</small></div></div>';""",
     """  /* the wall's own counts supersede the Tally sync figure; showing both invites
     a contradiction on the one page whose job is to be unambiguous */
  if(!wc)h+='<div class="metric"><div class="k">Responses</div><div class="v">'+rc+' <small>'+srcLbl+'</small></div></div>';"""),
    ("""  h+='<div class="metric"><div class="k">Window</div>""",
     """  if(wc){
    h+='<div class="metric"><div class="k">On the record</div><div class="v">'+(wc.published||0)+' <small>published</small></div></div>';
    if(wc.pending)h+='<div class="metric"><div class="k">Awaiting you</div><div class="v">'+wc.pending+' <small>to moderate</small></div></div>';
    if(wc.withheld)h+='<div class="metric"><div class="k">Withheld</div><div class="v">'+wc.withheld+' <small>not consented</small></div></div>';
  }
  h+='<div class="metric"><div class="k">Window</div>"""),
    ("""  // synthesis panel
  h+='<div class="synth"><div class="sh">Synthesis</div>';""",
     """  if(wc&&wc.pending){
    h+='<div class="howto"><b>'+wc.pending+' response'+(wc.pending===1?'':'s')+' awaiting moderation.</b> '
      +'Open <code>roundtables/responses/'+esc(cfg.id)+'.json</code>, set each pending entry\\'s '
      +'<code>"status"</code> to <code>"published"</code> or <code>"declined"</code>, run '
      +'<code>python3 scripts/roundtable_responses.py --render-only</code>, then commit. '
      +'Nothing shows on the public page until you do.</div>';
  }

  // synthesis panel
  h+='<div class="synth"><div class="sh">Synthesis</div>';"""),
    ("""        if(cfg){ if(!cfg.id)cfg.id=id; html+=card(cfg); found++; i++; next(); }
        else { done(); }""",
     """        if(!cfg){ done(); return; }
        if(!cfg.id)cfg.id=id;
        /* the wall's counts live beside the config, in responses/<id>.json */
        fetch('/roundtables/responses/'+id+'.json?ts='+Date.now(),{cache:'no-store'})
          .then(function(r){return r.ok?r.json():null;})
          .catch(function(){return null;})
          .then(function(w){ cfg._wall=w; html+=card(cfg); found++; i++; next(); });"""),
])
print("done")
