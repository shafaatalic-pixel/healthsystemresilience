#!/usr/bin/env python3
"""
Put the consolidated picture at the top of the Impact page, and a clock on it.

    python3 scripts/impact_page_v2.py .
    python3 scripts/impact_render.py .

Three additions, all rendered into the markup by impact_render.py so the page is
correct at first paint and nothing moves after it:

  * a refresh line that counts down to the next nightly run when the last one
    succeeded, and says how old the figures are when it did not;
  * the drop-off, one window and one site, from counted visitors to responses;
  * machines against people over the same seven days, beneath it.

Idempotent.
"""
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
P = os.path.join(ROOT, "impact.html")

SECTION = '''
<section id="the-drop-off"><div class="wrap">
<h2 class="sec" id="drop-off">The drop-off</h2>
<p>Everything below happens in one window, on one site, since launch on 22 July. That
is the only way the gap between any two lines means anything.</p>
<!--IMPACT:DROPOFF:START--><!--IMPACT:DROPOFF:END-->
<h3 class="imp-sub">Machines against people, the last seven days</h3>
<!--IMPACT:SPLIT:START--><!--IMPACT:SPLIT:END-->
</div></section>
'''

CSS = '''<style id="hs-impact2">
/* The refresh line. Fixed height, tabular figures and a reserved width on the
   countdown, so the script that advances the minutes cannot move anything. */
.imp-clock{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin:0;
  font-size:13.5px;line-height:1.5;color:var(--muted)}
.imp-clock b{font-weight:600;color:var(--ink,#1C2E4A)}
.imp-clock .dt{flex:none;width:7px;height:7px;border-radius:50%;background:#2E7D5B;
  transform:translateY(-1px)}
.imp-clock .cd{display:inline-block;min-width:15ch;font-variant-numeric:tabular-nums}
.imp-clock.is-stale .dt{background:var(--coral,#E2603F)}
.imp-clock.is-manual .dt{background:var(--muted,#6B7A8F)}
.imp-clock.is-stale b{color:var(--coral,#E2603F)}

/* One approved sentence, chosen by the numbers. Set apart from the prose it
   leads, because it is the part that changes. */
.imp-say{margin:2px 0 20px;max-width:64ch;font-family:var(--font-display);
  font-size:19.5px;line-height:1.5;color:var(--navy,#1C2E4A)}
@media(max-width:640px){.imp-say{font-size:18px}}

.imp-sub{font-family:var(--font-mono);font-size:12px;letter-spacing:.05em;
  text-transform:uppercase;color:var(--muted);margin:34px 0 12px}

/* The drop-off. Linear widths on purpose: the collapse is the finding, and a
   log axis would flatter it. */
.fn{list-style:none;margin:6px 0 0;padding:0}
.fn li{display:grid;grid-template-columns:minmax(150px,1.15fr) minmax(90px,2fr) 62px 52px;
  gap:14px;align-items:center;padding:9px 0;border-bottom:1px solid var(--line,#DCE3EA)}
.fn li:last-child{border-bottom:0}
.fn .fk{font-size:14.5px;line-height:1.3;color:var(--ink,#1C2E4A)}
.fn .fk i{display:block;font-style:normal;font-size:12px;color:var(--muted);margin-top:2px}
.fn .ft{display:block;height:12px;background:var(--paper,#F6F7F9);border-radius:3px;
  overflow:hidden}
.fn .ft em{display:block;height:100%;background:var(--navy,#1C2E4A);border-radius:3px}
.fn b{font-family:var(--font-display);font-size:20px;line-height:1;text-align:right;
  color:var(--navy,#1C2E4A);font-variant-numeric:tabular-nums}
.fn u{text-decoration:none;font-family:var(--font-mono);font-size:11.5px;text-align:right;
  color:var(--muted);font-variant-numeric:tabular-nums}
.fn li.end .ft em{background:var(--coral,#E2603F)}
.fn li.end b,.fn li.end .fk{color:var(--coral,#E2603F)}
.fnnote{margin:16px 0 0;max-width:72ch;font-size:14.5px;line-height:1.6;color:var(--muted)}
@media(max-width:680px){
  .fn li{grid-template-columns:1fr 58px 46px;gap:10px}
  .fn .ft{grid-column:1/-1;order:3}
  .fn b{font-size:18px}
}

/* Machines against people. Deliberately linear. */
.sp{margin:6px 0 0}
.sp-r{display:grid;grid-template-columns:minmax(150px,1fr) minmax(90px,2.2fr) 68px;gap:14px;
  align-items:center;padding:8px 0}
.sp-k{font-size:14.5px;color:var(--ink,#1C2E4A)}
.sp-t{display:block;height:12px;background:var(--paper,#F6F7F9);border-radius:3px;overflow:hidden}
.sp-t i{display:block;height:100%;border-radius:3px}
.sp-t i.navy{background:var(--navy,#1C2E4A)}
.sp-t i.coral{background:var(--coral,#E2603F)}
.sp b{font-family:var(--font-mono);font-size:13.5px;text-align:right;color:var(--navy,#1C2E4A);
  font-variant-numeric:tabular-nums}
@media(max-width:680px){.sp-r{grid-template-columns:1fr 66px}.sp-t{grid-column:1/-1;order:3}}
</style></head>'''

SCRIPT = '''<script>
/* Advances the minutes on the refresh line. The line is already correct in the
   markup, so this only keeps it correct while the tab stays open; with scripting
   off the page still says when it was last refreshed. */
(function () {
  var el = document.querySelector(".imp-clock"); if (!el) return;
  var cd = el.querySelector(".cd"); if (!cd) return;
  function tick() {
    var next = new Date(el.getAttribute("data-next") || "");
    if (isNaN(next)) return;
    var mins = Math.floor((next - new Date()) / 60000);
    if (mins < 0) { cd.textContent = "A refresh is due."; return; }
    cd.textContent = "Next refresh in " + Math.floor(mins / 60) + "h " +
      String(mins % 60).padStart(2, "0") + "m.";
  }
  tick(); setInterval(tick, 60000);
})();
</script></body>'''


def main():
    s = open(P, encoding="utf-8").read()
    before = s

    # ---- the clock, beside the dateline ------------------------------------
    if "<!--IMPACT:CLOCK:START-->" not in s:
        m = re.search(r'(<p class="imp-updated">.*?</p>)', s, re.S)
        if not m:
            raise SystemExit("ABORT: the dateline is not where it was")
        s = (s[:m.end()] + "\n<!--IMPACT:CLOCK:START--><!--IMPACT:CLOCK:END-->"
             + s[m.end():])
        print("  clock marker added")
    else:
        print("  already current: clock")

    # ---- the drop-off section, first thing in <main> after the dateline -----
    if 'id="the-drop-off"' not in s:
        anchor = s.index("</section>", s.index('class="imp-updated"')) + len("</section>")
        s = s[:anchor] + "\n" + SECTION + s[anchor:]
        print("  drop-off section added")
    else:
        print("  already current: drop-off section")

    # ---- section bar -------------------------------------------------------
    if 'href="#drop-off"' not in s:
        m = re.search(r'(<span class="sn-lab">On this page</span>)', s)
        if not m:
            raise SystemExit("ABORT: section bar not found")
        s = s[:m.end()] + '<a href="#drop-off">The drop-off</a>' + s[m.end():]
        print("  section bar: The drop-off added")
    else:
        print("  already current: section bar")

    if 'id="hs-impact2"' not in s:
        s = s.replace("</head>", CSS, 1)
        print("  styles added")
    if 'querySelector(".imp-clock")' not in s:
        s = s.replace("</body>", SCRIPT, 1)
        print("  countdown script added")

    for name in ("CLOCK", "DROPOFF", "SPLIT"):
        for edge in ("START", "END"):
            tag = "<!--IMPACT:%s:%s-->" % (name, edge)
            if s.count(tag) != 1:
                raise SystemExit("ABORT: %s appears %d times" % (tag, s.count(tag)))
    for anchor in re.findall(r'<nav class="mth-secnav".*?</nav>', s, re.S)[0:1]:
        for href in re.findall(r'href="#([a-z0-9-]+)"', anchor):
            if 'id="%s"' % href not in s:
                raise SystemExit("ABORT: section bar points at missing #%s" % href)

    if s != before:
        open(P, "w", encoding="utf-8").write(s)
        print("  wrote: impact.html")
    else:
        print("  no change")


main()
print("done")
