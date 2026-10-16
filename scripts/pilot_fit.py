#!/usr/bin/env python3
"""Build pilot-fit.html, the host-clinic fit check for the Prevention Adoption
Initiative, from the accessibility.html page shell.

Run from the website root after editing QUESTIONS or the result copy:
    python3 scripts/pilot_fit.py
Then python3 scripts/mkindex.py.

Every criterion and every "what closes it" line is taken from initiative.html.
Nothing is stored or sent: the check runs in the visitor's browser only.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(ROOT, 'accessibility.html')
OUT = os.path.join(ROOT, 'pilot-fit.html')

CAL = 'https://calendly.com/shafaat-alic/30min'

# Each question: key, short label (used in the result), prompt, options.
# Option: (text, score 0..2, gap note or None). stop=True marks a hard stop.
QUESTIONS = [
    dict(key='where', label='Location', q='Where is your clinic?',
         opts=[('Southeast Michigan', 2, None),
               ('Elsewhere in Michigan', 1, 'The pilot is written for one Southeast Michigan health center, where the weekly on-site hours are possible. A clinic elsewhere in Michigan is worth a conversation; the on-site day would need rethinking.'),
               ('Outside Michigan', 0, 'The first pilot is in Michigan, where its founder is based and the funding routes (a Medicaid plan\u2019s quality-incentive dollars, a Michigan health foundation, an MDHHS subaward) sit. A later site elsewhere would need its own partners.', True)]),
    dict(key='setting', label='Setting', q='What kind of setting is it?',
         opts=[('Federally qualified health center, or look-alike', 2, None),
               ('Another community or safety-net clinic', 2, None),
               ('Hospital-owned primary care', 1, 'The pilot is designed for a health center that reports the UDS colorectal screening measure. Hospital-owned primary care can work if it reports a comparable measure and can produce the nightly file.'),
               ('Private practice or other', 0, 'The pilot is designed for a health center serving people who are most likely to stall between a positive stool test and a colonoscopy. A private practice is not where it starts.', True)]),
    dict(key='rate', label='Screening rate', q='Your colorectal screening rate, on the UDS measure (ages 45 to 75)?',
         opts=[('Below 45%', 2, None),
               ('45% to 55%', 2, None),
               ('Above 55%', 1, 'The pilot suits a center below the national health-center benchmark (44.89% in CY2025 UDS). Above 55% the room to move is smaller, though follow-up after a positive test may still be the gap.'),
               ('I do not know', 1, 'Your UDS report carries it. The evaluator measures the starting point before month one, so the exact figure is not needed to start the conversation.')]),
    dict(key='kits', label='Mailed kits', q='Do you mail stool-test kits to patients today?',
         opts=[('Yes, as a routine', 2, None),
               ('Sometimes, or as a past project', 1, 'The pilot builds on kit outreach your staff already do. If it is occasional, the setup months would make it weekly before the routine starts.'),
               ('No', 0, 'The pilot assumes kits, postage and texts are already part of your outreach. Starting mailed outreach from nothing is a bigger change than the pilot is sized for.')]),
    dict(key='outreach', label='Outreach staff', q='Do you have staff who already call, remind and navigate patients?',
         opts=[('Yes, dedicated outreach or navigation staff', 2, None),
               ('Yes, as part of other roles', 1, 'The routine runs on your existing staff’s time, sized with you at the start. If outreach is a part of other jobs, the first three months show whether the hours are there.'),
               ('No', 0, 'The pilot does not bring staff or hire them. Without someone to make the calls and mail the kits, the weekly list has no one to work it.')]),
    dict(key='qi', label='QI lead', q='Is there a quality-improvement lead who could give 30 minutes a week?',
         opts=[('Yes', 2, None),
               ('Probably, if asked', 1, 'The weekly 30 minutes with the QI lead is how the routine gets fixed when a script does not land. It is the one meeting the pilot asks for.'),
               ('No', 0, 'The pilot asks for one named QI lead and a weekly 30-minute meeting. Without it, there is no one on your side to decide at month three.')]),
    dict(key='it', label='Nightly file', q='Could your IT lead produce a nightly coded export from your EHR? Nineteen columns, no names, record numbers or dates; the key stays with your IT lead.',
         opts=[('Yes, we already produce similar extracts', 2, None),
               ('Probably, with some help', 1, 'The 19 columns are mapped once with your IT lead before month one; the data spec is on the initiative page. Most modern EHRs can schedule it.'),
               ('No, or I am not sure', 0, 'The weekly list is built from that nightly file. Without it there is no list. Your IT lead can judge from the data spec in a short look.')]),
    dict(key='loi', label='Commitment', q='Could leadership sign a written agreement before month one, covering the scope, a feasibility rate for months 1 to 3 that your clinic pays, and a decision at month three to continue or stop?',
         opts=[('Yes', 2, None),
               ('It would need a board or CEO decision', 1, 'The agreement sets the scope and the two rates before month one, and the money can come from your own budget, quality-incentive dollars or a grant your clinic holds. A 30-minute conversation is usually what leadership wants first.'),
               ('No', 0, 'Without a written agreement before month one the pilot cannot start.')]),
]

BANDS = [
    # (min score, key, title, body)
    (14, 'ready', 'Ready to talk',
     'Your clinic matches what the pilot asks for. The next step is a 30-minute conversation, then your IT lead looks at the data spec and you name a quality-improvement lead.'),
    (10, 'gaps', 'A fit, with gaps to close',
     'Most of what the pilot needs is in place. The items below are the ones to settle before the agreement; none of them is unusual, and a 30-minute conversation is where they are usually resolved.'),
    (6, 'notyet', 'Not yet',
     'Some of what the pilot runs on is missing. The items below are what would have to be in place first. The open roundtable question is a good way to stay in the conversation meanwhile.'),
    (0, 'no', 'Not this pilot',
     'The first pilot is sized for one Michigan health center with outreach already running. That is not your setting, and a different pilot would be the honest answer. The roundtable is open to anyone who works in or around care.'),
]

MAX = sum(max(o[1] for o in q['opts']) for q in QUESTIONS)

CSS = '''
.pf-intro{max-width:62ch}
.pf-note{font-size:13.5px;color:var(--mut);margin:0 0 26px}
.pf-q{border:0;margin:0;padding:22px 0 8px;min-width:0;border-top:1px solid var(--line)}
.pf-q legend{padding:0;float:left;width:100%}
#pf-result{scroll-margin-top:calc(var(--hdr,92px) + 18px)}
.pf-q:first-of-type{border-top:0;padding-top:4px}

.pf-q .n{font:700 11px/1 "Inter",'Inter Fallback',sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);margin:0 0 8px}
.pf-q .t{font-size:17px;font-weight:700;color:var(--navy);margin:0 0 12px;line-height:1.35}
.pf-opts{display:grid;gap:8px;margin:0;padding:0;list-style:none}
.pf-opts label{display:flex;gap:12px;align-items:flex-start;padding:11px 14px;border:1px solid var(--line);border-radius:10px;background:#fff;cursor:pointer;font-size:15px;line-height:1.4}
.pf-opts label:hover{border-color:#B7C3D0}
.pf-opts input{margin:4px 0 0;flex:0 0 auto;accent-color:var(--coral)}
.pf-opts label:has(input:checked){border-color:var(--navy);background:var(--ground)}
.pf-opts label:has(input:focus-visible){outline:3px solid #BC3A26;outline-offset:2px}
.pf-actions{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:26px 0 8px}
.pf-btn{display:inline-block;font:700 15px/1 "Inter",'Inter Fallback',sans-serif;padding:13px 22px;border-radius:999px;border:0;background:var(--coral);color:#fff;text-decoration:none!important;cursor:pointer}
.pf-btn[disabled]{opacity:.45;cursor:not-allowed}
.pf-btn.ghost{background:transparent;color:var(--navy);border:1px solid var(--line)}
.pf-left{font-size:13.5px;color:var(--mut)}
#pf-result{display:none;margin-top:8px}
#pf-result.on{display:block}
.pf-band{border-radius:14px;padding:22px 24px;margin:0 0 22px;border:1px solid var(--line);background:var(--ground)}
.pf-band .k{font:700 11px/1 "Inter",'Inter Fallback',sans-serif;letter-spacing:.14em;text-transform:uppercase;margin:0 0 8px;color:var(--mut)}
.pf-band h2{margin:0 0 8px;font-size:26px}
.pf-band p{margin:0;font-size:16px}
.pf-band.ready{border-color:#9CC9B5;background:#EDF7F1}.pf-band.ready .k{color:#267A69}
.pf-band.gaps{border-color:#E9CFA0;background:#FBF4E6}.pf-band.gaps .k{color:#8A5A12}
.pf-band.notyet{border-color:#E5B8AE;background:#FBEFEC}.pf-band.notyet .k{color:#BC3A26}
.pf-band.no{border-color:var(--line);background:#F3F6F9}
.pf-crit{list-style:none;padding:0;margin:0 0 22px;display:grid;gap:6px}
.pf-crit li{display:grid;grid-template-columns:22px 150px 1fr;gap:10px;align-items:baseline;padding:9px 0;border-bottom:1px solid var(--line);font-size:14.5px}
.pf-crit li i{display:inline-block;width:12px;height:12px;border-radius:50%;background:#CBD4DE;position:relative;top:1px}
.pf-crit li.y i{background:#2E8B6E}.pf-crit li.m i{background:#D9A441}.pf-crit li.n i{background:#BC3A26}
.pf-crit li b{color:var(--navy);font-weight:600}
.pf-crit li span{color:var(--ink)}
.pf-gaps h3{font-size:16px;color:var(--navy);margin:22px 0 8px}
.pf-gaps ul{padding-left:0;list-style:none;margin:0 0 20px}
.pf-gaps li{padding:10px 0;border-bottom:1px solid var(--line);font-size:15px}
.pf-gaps li b{display:block;color:var(--navy);margin-bottom:2px}
.pf-cta{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:22px 0 6px}
.pf-small{font-size:13px;color:var(--mut);margin:14px 0 0}
@media(max-width:600px){.pf-crit li{grid-template-columns:18px 1fr;grid-template-rows:auto auto}.pf-crit li span{grid-column:2}}
'''

JS_TMPL = r'''
(function(){
var Q=__Q__, BANDS=__B__, MAX=__MAX__, CAL=__CAL__;
var form=document.getElementById('pf-form'), out=document.getElementById('pf-result'), btn=document.getElementById('pf-go'), left=document.getElementById('pf-left');
function answered(){return Q.filter(function(q){return form.querySelector('input[name="'+q.key+'"]:checked');}).length;}
function update(){var n=answered();btn.disabled=n<Q.length;left.textContent=n<Q.length?(Q.length-n)+' of '+Q.length+' to answer':'All answered';}
form.addEventListener('change',update);update();
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
btn.addEventListener('click',function(){
  var score=0,stop=false,rows=[],gaps=[];
  Q.forEach(function(q){
    var v=form.querySelector('input[name="'+q.key+'"]:checked');var o=q.opts[+v.value];
    score+=o[1]; if(o[3]) stop=true;
    rows.push({label:q.label,text:o[0],cls:o[1]===2?'y':(o[1]===1?'m':'n')});
    if(o[2]) gaps.push({label:q.label,text:o[0],note:o[2]});
  });
  var band=BANDS[BANDS.length-1];
  if(!stop){for(var i=0;i<BANDS.length;i++){if(score>=BANDS[i][0]){band=BANDS[i];break;}}}
  var met=rows.filter(function(r){return r.cls==='y';}).length;
  var h='<div class="pf-band '+band[1]+'"><p class="k">Your result · '+met+' of '+Q.length+' criteria fully met</p><h2>'+esc(band[2])+'</h2><p>'+esc(band[3])+'</p></div>';
  h+='<ul class="pf-crit">'+rows.map(function(r){return '<li class="'+r.cls+'"><i aria-hidden="true"></i><b>'+esc(r.label)+'</b><span>'+esc(r.text)+'</span></li>';}).join('')+'</ul>';
  if(gaps.length){h+='<div class="pf-gaps"><h3>What would close each gap</h3><ul>'+gaps.map(function(g){return '<li><b>'+esc(g.label)+': '+esc(g.text)+'</b>'+esc(g.note)+'</li>';}).join('')+'</ul></div>';}
  var cta;
  if(band[1]==='ready'||band[1]==='gaps'){cta='<a class="pf-btn" href="'+CAL+'" target="_blank" rel="noopener">Discuss hosting the pilot: 30 minutes</a><a class="pf-btn ghost" href="/initiative.html#host">Read the full terms</a>';}
  else{cta='<a class="pf-btn" href="/roundtable.html">Answer the open roundtable question</a><a class="pf-btn ghost" href="/initiative.html">Read about the pilot</a>';}
  h+='<div class="pf-cta">'+cta+'<button type="button" class="pf-btn ghost" id="pf-copy">Copy this result</button></div>';
  h+='<p class="pf-small">Nothing you answered has been stored or sent. The result lives only on this screen until you copy it.</p>';
  out.innerHTML=h;out.classList.add('on');
  var plain='Prevention Adoption Initiative, host clinic fit check\n'+band[2]+' ('+met+' of '+Q.length+' criteria fully met)\n\n'+rows.map(function(r){return '- '+r.label+': '+r.text;}).join('\n')+(gaps.length?'\n\nWhat would close each gap:\n'+gaps.map(function(g){return '- '+g.label+': '+g.note;}).join('\n'):'')+'\n\nFull terms: https://hsraep.org/initiative.html#host\nFit check: https://hsraep.org/pilot-fit.html';
  document.getElementById('pf-copy').addEventListener('click',function(){var b=this;function ok(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy this result';},1800);}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(plain).then(ok,function(){window.prompt('Copy this result',plain);});}else{window.prompt('Copy this result',plain);}});
  out.scrollIntoView({behavior:'smooth',block:'start'});
  try{if(window.hsTrack)window.hsTrack('pilot_fit_result',{band:band[1],met:met});}catch(e){}
});
})();
'''


def build():
    shell = open(SHELL, encoding='utf-8').read()
    # head
    s = shell
    s = s.replace('<title>Accessibility Statement - HSREP</title>', '<title>Is your clinic a fit for the pilot? - HSREP</title>', 1)
    s = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="Eight questions, two minutes. See whether your health center matches what the Colorectal Cancer Screening Completion Pilot asks of a host, and what would close any gap. Nothing is stored or sent.">', s, 1)
    s = s.replace('<link rel="canonical" href="https://hsraep.org/accessibility.html">', '<link rel="canonical" href="https://hsraep.org/pilot-fit.html">', 1)
    s = s.replace('</head>', '<style id="pf-css">' + CSS + '</style></head>', 1)
    # The fit check is an initiative page: the founder assistant, not Ask HSREP (16 Oct 2026).
    s = re.sub(r'<button class="hs-ask" type="button" data-askhs-open aria-haspopup="dialog" aria-expanded="false" aria-label="Ask HSREP" title="[^"]*">',
               '<button class="hs-ask" type="button" data-ask-open aria-haspopup="dialog" aria-label="Ask Shafaat about the pilot" title="Ask Shafaat about the pilot">', s, 1)
    s = s.replace('<span>Ask HSREP</span></button>', '<span>Ask Shafaat</span></button>', 1)
    s = re.sub(r'<script src="/assets/ask-hsrep\.js\?v=[0-9a-z]+" defer></script>', '<script src="/assets/assistant.js?v=20261016f" defer></script>', s, 1)
    # main
    qs = []
    for i, q in enumerate(QUESTIONS, 1):
        opts = ''.join('<li><label><input type="radio" name="%s" value="%d"><span>%s</span></label></li>' % (q['key'], j, o[0]) for j, o in enumerate(q['opts']))
        qs.append('<fieldset class="pf-q"><legend class="n">Question %d of %d</legend><p class="t">%s</p><ul class="pf-opts">%s</ul></fieldset>' % (i, len(QUESTIONS), q['q'], opts))
    main = ('<main><div class="wrap"><p class="eyebrow">Prevention Adoption Initiative</p><h1>Is your clinic a fit for the pilot?</h1>'
            '<p class="updated">Eight questions · about two minutes · nothing is stored or sent</p>'
            '<p class="lead pf-intro">The <a href="/initiative.html">Colorectal Cancer Screening Completion Pilot</a> asks a host health center for specific things: outreach staff who already mail kits and make calls, a quality-improvement lead, a nightly coded file, and a written agreement before month one. This check puts your clinic against that list and tells you what would close any gap. It is an HSREP initiative in development; no site, partner or funding exists yet.</p>'
            '<p class="pf-note">Answers stay in your browser. There is no account, no email, and no one at HSREP sees them unless you copy the result and send it.</p>'
            '<form id="pf-form" onsubmit="return false">' + ''.join(qs) +
            '<div class="pf-actions"><button type="button" class="pf-btn" id="pf-go" disabled>See the result</button><span class="pf-left" id="pf-left"></span></div></form>'
            '<div id="pf-result" aria-live="polite"></div>'
            '<div class="box">The criteria come from the pilot’s own terms: <a href="/initiative.html#host">what a host clinic would commit and get</a>. The result is a reading of fit, not an offer; the pilot starts with a 30-minute conversation either way.</div>'
            '</div></main>')
    s = re.sub(r'<main>[\s\S]*?</main>', lambda m: main, s, 1)
    # script before </body>: Q as [opts as [text,score,note,stop]]
    qjs = [dict(key=q['key'], label=q['label'], opts=[[o[0], o[1], o[2], bool(len(o) > 3 and o[3])] for o in q['opts']]) for q in QUESTIONS]
    js = (JS_TMPL.replace('__Q__', json.dumps(qjs, ensure_ascii=False))
          .replace('__B__', json.dumps(BANDS, ensure_ascii=False))
          .replace('__MAX__', str(MAX)).replace('__CAL__', json.dumps(CAL)))
    s = s.replace('</body>', '<script id="pf-js">' + js + '</script></body>', 1)
    # JSON-LD: swap the page name if the shell carries one
    s = s.replace('"name": "Accessibility Statement"', '"name": "Is your clinic a fit for the pilot?"')
    open(OUT, 'w', encoding='utf-8').write(s)
    print('wrote', os.path.relpath(OUT, ROOT), 'max score', MAX)


if __name__ == '__main__':
    build()
