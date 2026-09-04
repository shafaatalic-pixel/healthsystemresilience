#!/usr/bin/env python3
"""Build the two Prevention Adoption Initiative briefs (US, Bangladesh) as HTML, then PDF.
Single template, two data sets. Fonts are embedded from @fontsource packages so the PDF
matches the HSREP brand (Spectral / Inter / IBM Plex Mono) wherever it is printed."""
import os, json, base64, subprocess, html as H
ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "fonts", "node_modules", "@fontsource")

def font_face(family, pkg, weight, style="normal"):
    fn = f"{pkg}-latin-{weight}-{style}.woff2"
    p = os.path.join(F, pkg, "files", fn)
    b64 = base64.b64encode(open(p, "rb").read()).decode()
    return f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2');}}"

FONTS = "\n".join([
    font_face("Inter", "inter", 400), font_face("Inter", "inter", 500), font_face("Inter", "inter", 600), font_face("Inter", "inter", 700),
    font_face("Spectral", "spectral", 600), font_face("Spectral", "spectral", 700),
    font_face("IBM Plex Mono", "ibm-plex-mono", 400), font_face("IBM Plex Mono", "ibm-plex-mono", 500),
])

CSS = """
:root{--navy:#1C2E4A;--coral:#F26D5A;--ink:#28333F;--muted:#65717E;--hair:#DCE3EA;--paper:#F7F9FB;--tint:#F2F5F8}
*{box-sizing:border-box}
@page{size:letter;margin:0}
html,body{margin:0;padding:0;background:#fff}
body{font-family:'Inter',sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:8.5in;height:11in;background:var(--paper);display:flex;flex-direction:column;overflow:hidden}
.top{background:var(--navy);color:#fff;border-bottom:3px solid var(--coral);padding:0 .42in;height:.5in;display:flex;align-items:center;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.16em;text-transform:uppercase}
.top .r{color:#C9D3DF}
.body{padding:.2in .42in 0;flex:1;display:flex;flex-direction:column}
h1{font-family:'Spectral',serif;font-weight:700;font-size:23px;color:var(--navy);margin:8px 0 5px;letter-spacing:-.01em;line-height:1.15}
.sub{font-size:10.2px;color:var(--muted);line-height:1.45;margin:0 0 12px;max-width:7.2in}
.pitch{background:#fff;border:1px solid var(--hair);border-left:4px solid var(--coral);border-radius:6px;padding:10px 16px 6px}
.pitch .ph{display:flex;justify-content:space-between;align-items:center;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--navy);font-weight:500;padding-bottom:6px;border-bottom:1px solid var(--hair)}
.pitch .ph .st{color:var(--coral);font-size:9px;font-weight:400}
.pitch .row{display:grid;grid-template-columns:105px 1fr;gap:10px;padding:6px 0;border-bottom:1px solid #EEF1F4;font-size:9.6px;line-height:1.42}
.pitch .row:last-child{border-bottom:0}
.pitch .k{font-family:'IBM Plex Mono',monospace;font-size:8.6px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding-top:1px}
.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:9.4px;letter-spacing:.18em;text-transform:uppercase;color:var(--coral);margin:11px 0 5px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}
.stat{background:var(--tint);border-radius:6px;padding:9px 13px}
.stat .n{font-family:'IBM Plex Mono',monospace;font-size:14.5px;font-weight:500;color:var(--navy);margin-bottom:3px}
.stat .t{font-size:8.4px;color:var(--muted);line-height:1.4}
.card{background:#fff;border:1px solid var(--hair);border-radius:6px;padding:10px 13px}
.card .e{font-family:'IBM Plex Mono',monospace;font-size:8.4px;letter-spacing:.14em;text-transform:uppercase;color:var(--coral);margin-bottom:5px}
.card h3{font-family:'Spectral',serif;font-weight:600;font-size:13px;color:var(--navy);margin:0 0 4px;line-height:1.2}
.card p{margin:0;font-size:8.8px;line-height:1.42}
.band{background:var(--navy);color:#fff;border-radius:6px;padding:11px 16px 9px;margin-top:1px}
.band .cols{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.band .lab{font-family:'IBM Plex Mono',monospace;font-size:8.2px;letter-spacing:.14em;text-transform:uppercase;color:#C9D3DF;margin-bottom:5px}
.band .lab.rm{color:var(--coral)}
.band ul{list-style:none;margin:0;padding:0}
.band li{font-size:9.3px;line-height:1.35;padding:2px 0 2px 12px;position:relative}
.band li:before{content:'';position:absolute;left:0;top:7px;width:5px;height:5px;border-radius:50%;background:var(--coral)}
.band li small{color:#C9D3DF;font-size:8.3px}
.band .loop{border-top:1px solid rgba(255,255,255,.22);margin-top:8px;padding-top:7px;font-family:'IBM Plex Mono',monospace;font-size:8.2px;color:#DCE3EA;line-height:1.45}
h2{font-family:'Spectral',serif;font-weight:700;font-size:14px;color:var(--navy);margin:0 0 4px}
.demo p{margin:0;font-size:9.4px;line-height:1.45}
.foot{margin-top:auto;padding:9px 0 0;border-top:1px solid var(--hair)}
.foot .cols{display:grid;grid-template-columns:1.05fr 1fr;gap:22px;font-size:8.2px;line-height:1.45}
.foot .cols .l b{color:var(--navy)}
.foot .cols .r{color:var(--muted)}
.foot .src{font-family:'IBM Plex Mono',monospace;font-size:7.2px;color:var(--muted);margin:7px 0 .28in;line-height:1.45}
"""

PILLARS = """
<div class="eyebrow">The pilot loop — three core pillars, and a three-pillar roadmap</div>
<div class="band">
  <div class="cols">
    <div><div class="lab">Core · what the first site runs</div>
      <ul><li>Service redesign &amp; friction reduction</li>
          <li>Interoperable data infrastructure <small>— one nightly de-identified 19-column file for the pilot</small></li>
          <li>Implementation enablement <small>— training so the site runs and sustains it</small></li></ul></div>
    <div><div class="lab rm">Roadmap · after a validated pilot, not in the first pilot</div>
      <ul><li>Predictive AI, explainable</li>
          <li>Agentic &amp; conversational outreach</li>
          <li>Algorithmic equity &amp; governance</li></ul></div>
  </div>
  <div class="loop">Identify → Rank by transparent rules (days overdue, days since a positive test, prior no-shows) → Reduce friction → Communicate (literacy-tailored) → Escalate (community-health-worker outreach) → Measure, incl. diagnostic follow-up after a positive result. No patient messaging is automated in the first pilot.</div>
</div>
"""

def page(d):
    rows = "".join(f'<div class="row"><div class="k">{k}</div><div>{v}</div></div>' for k, v in d["pitch"])
    stats = "".join(f'<div class="stat"><div class="n">{n}</div><div class="t">{t}</div></div>' for n, t in d["stats"])
    cards = "".join(f'<div class="card"><div class="e">{e}</div><h3>{h}</h3><p>{p}</p></div>' for e, h, p in d["cards"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{H.escape(d['title'])}</title>
<style>{FONTS}{CSS}</style></head><body><div class="page">
<div class="top"><span>Prevention Adoption Initiative · {d['country']} · Proposed</span><span class="r">HSREP · hsraep.org/initiative</span></div>
<div class="body">
<h1>{d['h1']}</h1><p class="sub">{d['sub']}</p>
<div class="pitch"><div class="ph"><span>The pitch in 30 seconds</span><span class="st">Proposed · In development</span></div>{rows}</div>
<div class="eyebrow">The problem — adoption, not science</div><div class="grid3">{stats}</div>
<div class="eyebrow">Which one are you? — different partners, different value, same engine</div><div class="grid3">{cards}</div>
{PILLARS}
<div class="eyebrow">The demonstration</div><div class="demo"><h2>{d['demo_h']}</h2><p>{d['demo_p']}</p></div>
<div class="foot"><div class="cols">
<div class="l"><b>Md Shafaat Ali Choyon</b> — Founder, HSREP · MBA, MCIM, MPH, CHES®<br>hsraep.org/initiative · Book 30 min: calendly.com/shafaat-alic/30min<br>LinkedIn: /in/sacgrowthspecialist</div>
<div class="r">An HSREP initiative in development. All designs are illustrative and future-tense; no patient data has been collected. The first pilot runs on transparent rules and existing staff; AI components are a roadmap item. Operational materials will be reviewed by counsel before any launch.</div>
</div><div class="src">SOURCES — {d['sources']}</div></div>
</div></div></body></html>"""

US = dict(
  title="Prevention Adoption Initiative — United States brief", country="United States",
  h1="Recommended, reimbursed — and still not completed.",
  sub="A partnership brief on closing the gap between the preventive care that is recommended and the preventive care that actually gets finished — in the safety-net settings where the gap is widest.",
  pitch=[
    ("Problem", "U.S. colorectal-cancer screening sits at <b>63.5% against a 72.8% target</b> — and 44.89% in Federally Qualified Health Centers (CY2025 UDS; Michigan 48.74%). The services work; <b>completion</b> is what fails."),
    ("Solution", "A proposed <b>disease-agnostic completion engine</b>: it finds who is overdue, removes friction, and drives follow-through, run weekly on a fidelity dashboard. A predictive, explainable model is on the roadmap — not in the first pilot."),
    ("Evidence", "Every lever is already recommended by the Community Preventive Services Task Force (mailed FIT +16.1pp, reminders +15.3pp, navigation +13.6pp). Honest caveat: real-world gains depend on <b>implementation fidelity</b> — STOP CRC averaged ~3.4pp — which this design exists to protect."),
    ("Cost", "<b>~$90</b> per additional person screened (Pignone et al., JGIM 2021 benchmark)."),
    ("The ask", "One clinic to run a pre-registered <b>12-month pilot</b>; partners to scale it. Step one is a 30-minute conversation."),
  ],
  stats=[
    ("~8%", "of U.S. adults 35+ receive all 15 high-priority preventive services (Borsky, <i>Health Affairs</i> 2018)."),
    ("63.5% → 72.8%", "CRC screening vs. the Healthy People 2030 target — barely off baseline (2023)."),
    ("44.89%", "CRC screening in Federally Qualified Health Centers, CY2025 UDS (Michigan 48.74%) — the gap concentrates here."),
  ],
  cards=[
    ("Health centers / FQHCs", "Improve a measure you already report", "Host the pilot — raise a UDS/HEDIS measure you already report, inside your existing staffing, with the fidelity discipline that makes outreach reliably land."),
    ("Funders / partners", "Fund a cost-effective, scalable model", "A disease-agnostic engine at ~$90 per additional person screened, with an equity-stratified design and a path from one site to a network."),
    ("Researchers", "Co-design a publishable pilot", "A pre-registered stepped-wedge / RE-AIM evaluation with a protocol-first publication — rigor built in, co-authorship on the table. Principal investigator: to be confirmed."),
  ],
  demo_h="A proposed 12-month colorectal-cancer completion pilot.",
  demo_p="One Southeast Michigan FQHC below the UDS benchmark, with an outreach function and a quality-improvement sponsor. The site keeps its workflow and its data; HSREP is implementation lead (training, fidelity dashboard, weekly measurement, coordination); an academic partner owns the evaluation independently. Evaluated with RE-AIM against the site's own baseline, pre-registering a benchmarked target above the ~3.4-point STOP CRC average, with a comparison clinic where feasible, a named post-grant sustainability path, and guaranteed diagnostic follow-up. First readout after one full screening cycle (about month six); results published whichever way they go. Disease-agnostic by design — the same loop extends to cervical and breast screening, hypertension, and immunizations.",
  sources="Borsky et al., Health Affairs 2018 · Healthy People 2030 C-07 (2023 baseline) · HRSA Uniform Data System CY2025, national and Michigan, accessed Aug 2026 · CDC Community Guide (median effects) · Coronado et al., STOP CRC, JAMA Internal Medicine 2018 · Pignone et al., JGIM 2021 (mailed-FIT cost).",
)

BD = dict(
  title="Prevention Adoption Initiative — Bangladesh brief", country="Bangladesh",
  h1="The screening exists. Completion is what's missing.",
  sub="A partnership brief on closing the gap between preventive care that is offered and preventive care that is actually completed — across Bangladesh's community-clinic screening system.",
  pitch=[
    ("Problem", "Bangladesh's national screening programme has reach and a registry — yet its own evaluation found that only <b>40.4% of VIA-positive women attended for colposcopy</b> (January 2018 – May 2023; Nessa et al., 2025). That is a completion-and-fidelity gap, not a science gap."),
    ("Solution", "A proposed <b>disease-agnostic completion engine</b>: it finds who is overdue, removes friction, and drives follow-through, run weekly on a fidelity dashboard. A predictive, explainable model is on the roadmap — not in the first pilot."),
    ("The model", "<b>Embed, don't build</b> — the engine plugs into existing clinics and the national registry. In Bangladesh, friction reduction means the barriers that actually stop completion: transparent bundled pricing, literacy-tailored urgency communication, and one-visit / home-collection logistics."),
    ("Evidence", "Each mechanism carries quantified effect sizes from the CDC Community Guide; the programme's own evaluation identifies the uptake and follow-up gaps the loop is designed to close."),
    ("The ask", "A first <b>private-network partner</b> to run the loop commercially — then a donor-supported public-programme pilot in a few upazilas to prove it at national scale. Step one is a 30-minute conversation."),
  ],
  stats=[
    ("69%", "of health spending is out-of-pocket (WHO, 2025) — one hospitalization can push a household into poverty."),
    ("&lt;1% of GDP", "public health spending (World Bank, 2021) — prevention is under-resourced."),
    ("40.4%", "of VIA-positive women attended for colposcopy in the national programme's own evaluation (2018–2023) — most positives never complete follow-up."),
  ],
  cards=[
    ("Private healthcare", "Finish the tests you already start", "You already run entry-test campaigns; the leak is conversion — price shock, urgency that never lands, second-visit logistics. The loop attacks all three. Coverage alone doesn't complete care; a designed loop does."),
    ("Government", "Strengthen a programme that exists", "DGHS NCDC, the national cervical &amp; breast screening leadership, and the Community Clinic Health Support Trust — piloted in a few upazilas, closing gaps the programme's own evaluation identifies."),
    ("Research &amp; NGO", "Reach, rigor, and credibility", "icddr,b, BSMMU, BRAC, Marie Stopes — publishable, scalable evidence that opens donor funding. Ethics via BMRC or BSMMU; evaluation partner to be confirmed."),
  ],
  demo_h="Embed the completion loop into a programme that already exists.",
  demo_p="Rather than build something new, the engine embeds into the existing network of roughly 14,000 community clinics and the national electronic registry — piloted in a few upazilas, aligned to the national NCD and screening strategy — to close the uptake and follow-up gaps the programme's own evaluation identifies. Data stays within the programme's registry and DGHS control; HSREP is implementation lead; an independent academic partner evaluates. Disease-agnostic by design: the same loop applies to cervical and breast screening, hypertension, and immunizations.",
  sources="WHO Global Health Expenditure (2025) · World Bank health-financing indicators (2021) · Nessa et al., BMC Global and Public Health 2025;3:34 (colposcopy attendance among VIA-positive women, 2018–2023) · DGHS NCDC / NCCBCST national screening programme · e-HIS/DHIS2 evaluations, BMC Public Health &amp; PLOS Glob. Public Health (2025) · CDC Community Guide (mechanism effect sizes).",
)

for name, d in (("us", US), ("bd", BD)):
    open(os.path.join(ROOT, f"brief_{name}.html"), "w", encoding="utf-8").write(page(d))
print("html written")
