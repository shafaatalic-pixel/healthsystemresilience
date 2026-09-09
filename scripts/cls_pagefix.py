#!/usr/bin/env python3
"""HSREP CLS fix: reserve the campaign-bar slot in every page's <head> and set the
header CTA to the label analytics.js would apply, so the deferred script no longer
moves anything after first paint. Idempotent. Usage: pagefix.py <site root>"""
import os, re, sys, datetime
root = sys.argv[1]
RESERVE_CSS = ('<style id="hs-reserve">body{padding-top:45px}html.hs-bar-on body,html.hs-nobar body{padding-top:0}'
               'body:has(>.hs-campaign){padding-top:0}</style>')
# The dismissal is per-campaign: analytics.js stores the campaign's state string and
# only stays hidden while the stored value still equals the current state. The
# pre-paint guard has to make the same comparison, or a reader who dismissed the
# previous campaign gets hs-nobar before paint and then the new bar inserted after
# it, which is a 45px shift. Bake the current state into the guard.
GUARD_RE = re.compile(r'<script>try\{if\(sessionStorage\.getItem\("hsrep-campaign-dismissed-v2"\)'
                      r'[^<]*?\)document\.documentElement\.classList\.add\("hs-nobar"\)\}catch\(e\)\{\}</script>')

def guard(state):
    return ('<script>try{if(sessionStorage.getItem("hsrep-campaign-dismissed-v2")==="%s")'
            'document.documentElement.classList.add("hs-nobar")}catch(e){}</script>' % state)
FONT_FALLBACK_CSS = '@font-face{font-family:"Inter Fallback";font-weight:400;font-style:normal;src:local("Arial"),local("ArialMT");size-adjust:107.62%;ascent-override:90.01%;descent-override:22.41%;line-gap-override:0.00%}@font-face{font-family:"Inter Fallback";font-weight:500;font-style:normal;src:local("Arial"),local("ArialMT");size-adjust:108.75%;ascent-override:89.08%;descent-override:22.18%;line-gap-override:0.00%}@font-face{font-family:"Inter Fallback";font-weight:600;font-style:normal;src:local("Arial Bold"),local("Arial-BoldMT");size-adjust:101.46%;ascent-override:95.48%;descent-override:23.77%;line-gap-override:0.00%}@font-face{font-family:"Inter Fallback";font-weight:700;font-style:normal;src:local("Arial Bold"),local("Arial-BoldMT");size-adjust:102.49%;ascent-override:94.52%;descent-override:23.54%;line-gap-override:0.00%}@font-face{font-family:"Inter Fallback";font-weight:800;font-style:normal;src:local("Arial Bold"),local("Arial-BoldMT");size-adjust:103.75%;ascent-override:93.38%;descent-override:23.25%;line-gap-override:0.00%}@font-face{font-family:"Spectral Fallback";font-weight:400;font-style:normal;src:local("Times New Roman"),local("TimesNewRomanPSMT");size-adjust:109.71%;ascent-override:96.52%;descent-override:42.20%;line-gap-override:0.00%}@font-face{font-family:"Spectral Fallback";font-weight:400;font-style:italic;src:local("Times New Roman Italic"),local("TimesNewRomanPS-ItalicMT");size-adjust:100.60%;ascent-override:105.27%;descent-override:46.02%;line-gap-override:0.00%}@font-face{font-family:"Spectral Fallback";font-weight:600;font-style:normal;src:local("Times New Roman Bold"),local("TimesNewRomanPS-BoldMT");size-adjust:106.03%;ascent-override:99.88%;descent-override:43.67%;line-gap-override:0.00%}@font-face{font-family:"Spectral Fallback";font-weight:700;font-style:normal;src:local("Times New Roman Bold"),local("TimesNewRomanPS-BoldMT");size-adjust:107.64%;ascent-override:98.38%;descent-override:43.01%;line-gap-override:0.00%}@font-face{font-family:"IBM Plex Mono Fallback";font-weight:500;font-style:normal;src:local("Courier New"),local("CourierNewPSMT");size-adjust:99.98%;ascent-override:102.52%;descent-override:27.50%;line-gap-override:0.00%}@font-face{font-family:"IBM Plex Mono Fallback";font-weight:600;font-style:normal;src:local("Courier New Bold"),local("CourierNewPS-BoldMT");size-adjust:99.98%;ascent-override:102.52%;descent-override:27.50%;line-gap-override:0.00%}@font-face{font-family:"IBM Plex Mono Fallback";font-weight:700;font-style:normal;src:local("Courier New Bold"),local("CourierNewPS-BoldMT");size-adjust:99.98%;ascent-override:102.52%;descent-override:27.50%;line-gap-override:0.00%}' + ':root{--font-body:"Inter","Inter Fallback",system-ui,sans-serif;--font-display:"Spectral","Spectral Fallback",Georgia,serif;--font-mono:"IBM Plex Mono","IBM Plex Mono Fallback",monospace}'
SKIP = {'roundtable-console.html'}   # private console: no site header, no campaign bar
today = datetime.date.today()

def campaign_state():
    """Mirror analytics.js campaignState() so the baked header CTA matches what the
    script would set, and nothing is relabelled after first paint."""
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

state = campaign_state()

def group(rel):
    p = '/' + rel.replace(os.sep, '/')
    if '/articles/' in p: return 'article'
    if 'initiative' in p: return 'initiative'
    if 'roundtable' in p: return 'roundtable'
    return 'other'

def cta_for(g):
    if g == 'article':    return ('#engage', 'Add your response', False)
    if g == 'initiative': return ('#host', 'Request presentation', False)
    if g == 'roundtable': return ('/roundtable.html', 'Join Roundtable' if state == 'roundtable' else 'Roundtable record', False)
    if state == 'roundtable': return ('/roundtable.html', 'Join Roundtable', False)
    return ('https://buttondown.com/shafaat', 'Season 2 updates', True)

changed = []
for dp, dn, fn in os.walk(root):
    if '/.git' in dp or 'node_modules' in dp or '_archive' in dp: continue
    for f in fn:
        if not f.endswith('.html') or f in SKIP: continue
        path = os.path.join(dp, f); rel = os.path.relpath(path, root)
        s = open(path, encoding='utf-8').read(); o = s
        if 'analytics.js' not in s or '<header' not in s: continue
        # 1. reserve the bar slot (once)
        if 'id="hs-reserve"' not in s:
            s = s.replace('</head>', RESERVE_CSS + guard(state) + '</head>', 1)
        else:
            # keep the guard in step with the current campaign state
            s = GUARD_RE.sub(guard(state), s, 1)
        # 2. static header CTA = what analytics.js sets for this page group
        href, label, ext = cta_for(group(rel))
        attrs = ' target="_blank" rel="noopener"' if ext else ''
        def sub_cta(m):
            tag = m.group(0)
            cls = m.group(1)
            tag = re.sub(r'\shref="[^"]*"', ' href="%s"' % href, tag, 1)
            tag = re.sub(r'\s(target|rel)="[^"]*"', '', tag)
            tag = re.sub(r'>[^<]*</a>$', attrs + '>' + label + '</a>', tag)
            return tag
        # header CTA patterns: <a class="btn accent" ...>Participate</a> inside header.site .row,
        # <a class="cta" ...>Participate</a>, <a class="hs-hcta" ...>Participate</a>
        hdr = re.search(r'<header[^>]*class="[^"]*site[^"]*"[^>]*>.*?</header>', s, re.S)
        if hdr:
            h = hdr.group(0)
            h2 = re.sub(r'<a class="(btn accent|cta|hs-hcta)"[^>]*>(?:Participate|Season 2 updates|Join Roundtable|Roundtable record|Add your response|Request presentation)</a>', sub_cta, h)
            s = s[:hdr.start()] + h2 + s[hdr.end():]
        # 3. static nav label analytics.js applies ("Season 1" -> "Evidence") inside the header nav / mobile panel
        if hdr:
            hdr = re.search(r'<header[^>]*class="[^"]*site[^"]*"[^>]*>.*?</header>', s, re.S); h = hdr.group(0)
            h2 = re.sub(r'(<a[^>]*href="[^"]*season-1\.html"[^>]*>)Season 1(</a>)', r'\1Evidence\2', h)
            s = s[:hdr.start()] + h2 + s[hdr.end():]
        # 3b. the mobile menu button is created by an inline script at the end of <body>; on mobile it
        #     reflows the header row after first paint. Put it in the markup and let the script reuse it.
        MENU_BTN = '<button id="hs-menu-static" type="button" aria-label="Menu" aria-expanded="false" aria-controls="hmenu-panel"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 7h16M4 12h16M4 17h16"/></svg><span>Menu</span></button>'.replace('hs-menu-static', 'hmenu-btn')
        OLD_JS = "var btn=document.createElement('button');btn.id='hmenu-btn';btn.type='button';btn.setAttribute('aria-label','Menu');btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-controls','hmenu-panel');\n   btn.innerHTML='<svg viewBox=\"0 0 24 24\"><path d=\"M4 7h16M4 12h16M4 17h16\"/></svg><span>Menu</span>';\n   var panel=document.createElement('div');panel.id='hmenu-panel';panel.innerHTML=src.innerHTML;\n   var row=hdr.querySelector('.row')||hdr;row.appendChild(btn);document.body.appendChild(panel);"
        NEW_JS = "var btn=document.getElementById('hmenu-btn');\n   if(!btn){btn=document.createElement('button');btn.id='hmenu-btn';btn.type='button';btn.setAttribute('aria-label','Menu');btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-controls','hmenu-panel');\n   btn.innerHTML='<svg viewBox=\"0 0 24 24\"><path d=\"M4 7h16M4 12h16M4 17h16\"/></svg><span>Menu</span>';\n   (hdr.querySelector('.row,.hs-hrow')||hdr).appendChild(btn);}\n   var panel=document.createElement('div');panel.id='hmenu-panel';panel.innerHTML=src.innerHTML;\n   document.body.appendChild(panel);"
        if OLD_JS in s:
            s = s.replace(OLD_JS, NEW_JS, 1)
        # second, minified variant of the same script (transcripts, legal pages, search, 404)
        OLD_JS2 = 'var btn=document.createElement("button");btn.id="hmenu-btn";btn.type="button";btn.setAttribute("aria-label","Menu");btn.setAttribute("aria-expanded","false");btn.setAttribute("aria-controls","hmenu-panel");btn.innerHTML=\'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 7h16M4 12h16M4 17h16"/></svg><span>Menu</span>\';var panel=document.createElement("div");panel.id="hmenu-panel";panel.innerHTML=src.innerHTML;(hdr.querySelector(".row")||hdr).appendChild(btn);document.body.appendChild(panel);'
        NEW_JS2 = 'var btn=document.getElementById("hmenu-btn");if(!btn){btn=document.createElement("button");btn.id="hmenu-btn";btn.type="button";btn.setAttribute("aria-label","Menu");btn.setAttribute("aria-expanded","false");btn.setAttribute("aria-controls","hmenu-panel");btn.innerHTML=\'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 7h16M4 12h16M4 17h16"/></svg><span>Menu</span>\';(hdr.querySelector(".row")||hdr).appendChild(btn);}var panel=document.createElement("div");panel.id="hmenu-panel";panel.innerHTML=src.innerHTML;document.body.appendChild(panel);'
        if OLD_JS2 in s:
            s = s.replace(OLD_JS2, NEW_JS2, 1)
        if '<button id="hmenu-btn"' not in s and (NEW_JS in s or NEW_JS2 in s):
            hdr = re.search(r'<header[^>]*class="[^"]*site[^"]*"[^>]*>.*?</header>', s, re.S); h = hdr.group(0)
            m = re.search(r'<a class="(?:btn accent|cta|hs-hcta)"[^>]*>[^<]*</a>', h)
            if m:
                h2 = h[:m.end()] + MENU_BTN + h[m.end():]
                s = s[:hdr.start()] + h2 + s[hdr.end():]
        # 3c. article header: nav collapses at the same width the menu button appears, and the header CTA
        #     may wrap on phones instead of overflowing the viewport
        if group(rel) == 'article' and 'id="hs-arthdr-fit"' not in s:
            s = s.replace('</head>', '<style id="hs-arthdr-fit">@media(max-width:940px){.hs-sitehdr .hs-hnav{display:none}}@media(max-width:820px){.hs-sitehdr .hs-hcta{white-space:normal;flex:0 1 auto;min-width:0;text-align:center;line-height:1.15;padding:9px 14px}.hs-sitehdr .hs-hlogo,.hs-sitehdr .hs-srch,.hs-sitehdr #hmenu-btn{flex:0 0 auto}}@media(max-width:400px){.hs-sitehdr .hs-hcta{font-size:13px;padding:8px 12px}}</style></head>', 1)
        # 3d. roundtable page: the status pill, CTA row and synthesis note are written by an inline script
        #     after a fetch; ship the closed-window markup statically so the script's write is a no-op
        if f == 'roundtable.html':
            PILL = lambda txt, color: '<span style="display:inline-flex;align-items:center;gap:9px;font-family:var(--font-mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:%s;border:1px solid %s;border-radius:999px;padding:7px 15px"><span style="width:8px;height:8px;border-radius:50%%;background:%s"></span>%s</span>' % (color, color, color, txt)
            RNG = ' <span style="font-family:var(--font-mono);font-size:12px;color:var(--muted);letter-spacing:.03em;white-space:nowrap">Aug 11, Aug 25, 2026 &middot; 14-day window</span>'
            s = re.sub(r'(<div id="rtstatus"[^>]*>)\s*(?=</div>)', lambda m: m.group(1) + PILL('Closed · synthesis in preparation', '#65717E') + RNG, s, 1)
            s = re.sub(r'(<div id="rtcta"[^>]*>)\s*(?=</div>)', lambda m: m.group(1) + '<a class="btn ghost on-dark" href="#synthesis">Read the record &rarr;</a> <a class="btn accent" href="https://tally.so/r/VLBbYM" target="_blank" rel="noopener">Join the next roundtable &rarr;</a>', s, 1)
            s = re.sub(r'(<div id="rtsynth"[^>]*>)\s*(?=</div>)', lambda m: m.group(1) + '<p class="big">The response window has closed. The moderated synthesis, naming consented contributors and the through-line, is in preparation and will be posted here.</p>', s, 1)
        # 3e. "On this page" bar (#secnav): an inline script at the end of <body> moves it to just after
        #     the header, pushing the page down by its height. Place it there in the markup with a fixed height.
        if "hdr.insertAdjacentElement('afterend',nav)" in s and 'id="hs-secnav-fit"' not in s:
            nm = re.search(r'\s*<nav id="secnav">.*?</nav>', s, re.S)
            he = re.search(r'</header>', s)
            if nm and he and nm.start() > he.end():
                nav = nm.group(0).strip()
                s = s[:nm.start()] + s[nm.end():]
                he = re.search(r'</header>', s)
                s = s[:he.end()] + nav + s[he.end():]
                s = s.replace('</head>', '<style id="hs-secnav-fit">#secnav{height:42px}@media(max-width:640px){#secnav{height:39.5px}}</style></head>', 1)
        # pages whose section bar ends up hidden by that script (fewer than two links): hide it from
        # first paint instead of showing an empty 42px bar that disappears. Verified with a headless
        # render on 2026-09-08; re-check if a page's section structure changes.
        SECNAV_HIDDEN = {'articles.html', 'films.html',
            'articles/health-policy-shapes-michigan-tomorrow/health-policy-shapes-michigan-tomorrow.html',
            'articles/increasing-public-health-investment/increasing-public-health-investment.html',
            'articles/mixed-messages-real-costs/mixed-messages-real-costs.html',
            'articles/private-healthcare-health-literacy/private-healthcare-health-literacy.html',
            'articles/public-health-reform-for-economic-growth/public-health-reform-for-economic-growth.html',
            'articles/running-on-empty-workforce-crisis/running-on-empty-workforce-crisis.html',
            'articles/when-illness-becomes-a-bill-medical-debt/when-illness-becomes-a-bill-medical-debt.html',
            'articles/when-we-ignore-prevention-we-pay/when-we-ignore-prevention-we-pay.html'}
        s = s.replace('<style id="hs-secnav-fit">#secnav{display:none!important}</style>', '<style id="hs-secnav-fit">html #secnav{display:none!important}</style>', 1)
        if rel.replace(os.sep, '/') in SECNAV_HIDDEN:
            s = s.replace('<style id="hs-secnav-fit">#secnav{height:42px}@media(max-width:640px){#secnav{height:39.5px}}</style>',
                          '<style id="hs-secnav-fit">html #secnav{display:none!important}</style>', 1)
        # 4. move every <style> that sits inside <body> up into <head>: CSS parsed after first paint
        #    re-lays out the header (mobile logo/search/CTA sizes), which is a measured layout shift
        bpos = s.find('<body')
        if bpos > 0:
            late = [m for m in re.finditer(r'\s*<style[^>]*>.*?</style>', s, re.S) if m.start() > bpos]
            if late:
                blocks = ''.join(m.group(0).strip() for m in late)
                for m in reversed(late): s = s[:m.start()] + s[m.end():]
                hend = s.find('</head>')
                s = s[:hend] + '\n' + blocks + '\n' + s[hend:]
        # 5. web-font swap: metric-matched local fallbacks (size-adjust / ascent / descent overrides) so the
        #    Arial / Times / Courier text drawn before Inter, Spectral and IBM Plex Mono arrive occupies the
        #    same lines; the swap then repaints without moving anything
        if 'id="hs-font-fallback"' not in s:
            s = s.replace('</head>', '<style id="hs-font-fallback">' + FONT_FALLBACK_CSS + '</style></head>', 1)
        def add_fallback(css):
            return re.sub(r'(["\']?)(Inter|Spectral|IBM Plex Mono)\1(\s*,)(?!\s*["\']?\2 Fallback)', lambda m: m.group(1)+m.group(2)+m.group(1)+",'"+m.group(2)+" Fallback'"+m.group(3), css)
        s = re.sub(r'(<style(?![^>]*id="hs-font-fallback")[^>]*>)(.*?)(</style>)', lambda m: m.group(1)+add_fallback(m.group(2))+m.group(3), s, flags=re.S)
        s = re.sub(r'style="([^"]*)"', lambda m: 'style="'+add_fallback(m.group(1))+'"', s)
        if s != o:
            open(path, 'w', encoding='utf-8').write(s); changed.append(rel)
print('state:', state); print('\n'.join(changed)); print(len(changed), 'pages changed')
