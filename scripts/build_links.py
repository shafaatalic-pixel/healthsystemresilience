#!/usr/bin/env python3
"""Build /links/index.html: HSREP's link-in-bio page for @hsraep (Instagram) and the HSREP Facebook Page.

Facebook does not make links in Page comments or captions clickable, and Instagram never does, so
each HSREP post says "All links: hsraep.org/links" and this page carries every link for that post.
Header, footer, fonts and scripts are taken from pilot-fit.html so the page matches the site.
Each card appears at its post time (11:00 AM Michigan). Append new posts to POSTS in date order.

Usage: python3 scripts/build_links.py [site_root]
"""
import datetime, html, os, re, sys
from zoneinfo import ZoneInfo

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = ZoneInfo("America/Detroit")
E = lambda s: html.escape(str(s), quote=True)
ART = "/articles/{0}/{0}.html"

# (date, key, title, [(button, detail, url, utm_content)], optional "HH:MM")
POSTS = [
    # Already on the HSREP Facebook Page (theme Reel, 21 Oct 2026; also going to @hsraep)
    # The Oct 20 to 21 link posts (What HSREP is, pilot assistant, Ask HSREP) have clickable preview cards; only the theme Reel needs a card.
    ("2026-10-21", "theme", "HSREP has a theme", [
        ("The mark and the theme", "The Humanist Crest and the theme, chapter by chapter", "/identity.html", "identity"),
        ("Start here", "The platform, its thesis and what it publishes", "/", "home"),
        ("How it was built", "The HSREP case, with the numbers", "https://shafaatalichoyon.com/case/hsrep/", "case")], "16:18"),
    # Reels, from the Reel Posting Pack (scheduled 30 Oct 2026; HSREP 2 on Meta from Nov 5)
    ("2026-11-03", "hsrep1", "What HSREP is", [
        ("Start here", "The platform, its thesis and what it publishes", "/", "home"),
        ("The Season 1 record", "57,274 impressions at $0 ad spend, every figure sourced", "/season-1.html", "season"),
        ("The prevention initiative", "Our first applied work, in development", "/initiative.html", "initiative"),
        ("Ask HSREP", "Answers from HSREP's published record", "/?ask=1", "ask")]),
    ("2026-11-06", "hsrep5", "From a recommended test to a finished one", [
        ("The initiative", "A weekly routine for the follow-through gap", "/initiative.html", "initiative"),
        ("", "Eight questions, two minutes, nothing stored", "/pilot-fit.html", "fit"),
        ("Ask about the pilot", "For health-center teams", "/initiative.html?ask=1&as=clinic", "ask")]),
    ("2026-11-10", "hsrep4", "What hosting the pilot asks of your staff", [
        ("What a host commits", "Hours, roles, data and the month-3 decision", "/initiative.html#host", "initiative"),
        ("", "Eight questions, two minutes, nothing stored", "/pilot-fit.html", "fit"),
        ("Ask about the pilot", "For health-center teams", "/initiative.html?ask=1&as=clinic", "ask")]),
    ("2026-11-17", "hsrep6", "Execution is the intervention", [
        ("The routine", "Find. Rank. Act. Close.", "/initiative.html#how", "initiative"),
        ("Where it goes next", "The other completion gaps it fits", "/initiative-next.html", "next"),
        ("Ask about the pilot", "For health-center teams", "/initiative.html?ask=1&as=clinic", "ask")]),
    ("2026-11-24", "hsrep7", "One routine, the measures you already pay for", [
        ("Where it goes next", "Health plans and the measures they reward", "/initiative-next.html", "next"),
        ("The initiative", "The first pilot: colorectal, one Michigan health center", "/initiative.html", "initiative"),
        ("Ask about the pilot", "For health-plan quality leads", "/initiative.html?ask=1&as=plan", "ask")]),
    ("2026-12-01", "hsrep2", "When illness becomes a bill", [
        ("The article", "When illness becomes a bill: the medical debt crisis", ART.format("when-illness-becomes-a-bill-medical-debt"), "article"),
        ("Start here", "The platform, its thesis and what it publishes", "/", "home"),
        ("Ask HSREP", "Answers from HSREP's published record", "/?ask=1", "ask")]),
    ("2026-12-15", "hsrep3", "Bangladesh: the family pays first", [
        ("HSREP Bangladesh", "Where new health money should go first", "https://hsrep.bd/", "bd"),
        ("The article", "Public health investment must be a top priority", ART.format("increasing-public-health-investment"), "article"),
        ("Ask HSREP", "Answers from HSREP's published record", "/?ask=1", "ask")]),
]

# Evergreen links. Older posts (Jul 22 to Aug 18) are not mapped one by one (Shafaat, 31 Oct): that content returns as new Reels.
# posts and the platform posts. One entry per destination, titled with the post's own opening line so a
# reader coming from an old post recognises it. Links in those captions are not clickable on Facebook.
LIBRARY = [
    ("All nine Season 1 articles", "/articles.html"),
    ("The Prevention Adoption Initiative", "/initiative.html"),
    ("The Season 1 record", "/season-1.html"),
]

CSS = """<style id="lk-css">
.lk-hero{padding:34px 0 8px}
.lk-hero h1{font-family:var(--font-display);font-weight:700;font-size:clamp(30px,6vw,40px)}
.lk-hero .lead{color:var(--mut);max-width:34em;margin:6px 0 0}
.lk-list{list-style:none;margin:22px 0 0;padding:0;display:flex;flex-direction:column;gap:12px}
.lk{border:1px solid var(--line);border-radius:16px;background:#fff;padding:16px}
.lk.hit{border-color:var(--coral);box-shadow:0 0 0 4px rgba(188,58,38,.12)}
.lk .m{font:600 11px/1 var(--font-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--coral);margin:0 0 6px}
.lk h2{font-family:var(--font-display);font-size:20px;line-height:1.25;margin:0 0 12px;color:var(--navy)}
.lk .bt{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.lk .bt a{display:flex;flex-direction:column;gap:2px;border:1px solid var(--line);border-radius:12px;padding:10px 12px;text-decoration:none;color:var(--ink);background:var(--paper);min-width:0}
.lk .bt a:hover{border-color:var(--coral)}
.lk .bt a b{font:700 14.5px/1.25 var(--font-body);color:var(--navy)}
.lk .bt a span{font-size:12.5px;line-height:1.35;color:var(--mut)}
.lk .bt a:last-child:nth-child(odd){grid-column:1/-1}
.lk .bt a:first-child{border-color:var(--navy);background:var(--ground)}
.lk .bt a.k-ask b::before{content:"\\2726  ";color:var(--coral)}
.lk-lib{margin-top:34px}
.lk-lib h2.lt{font-family:var(--font-display);font-size:24px;color:var(--navy);margin:0 0 4px}
.lk-lib .ls{color:var(--mut);margin:0 0 14px;font-size:14.5px}
.lk-ev{display:flex;flex-wrap:wrap;gap:8px}
.lk-ev a{border:1px solid var(--line);border-radius:999px;padding:9px 14px;text-decoration:none;font:600 14px/1.2 var(--font-body);color:var(--navy);background:#fff}
.lk-ev a:hover{border-color:var(--coral);color:var(--coral)}
.lk-lib details{border:1px solid var(--line);border-radius:14px;background:#fff;margin:0 0 10px}
.lk-lib summary{cursor:pointer;padding:13px 16px;font:700 15px/1.3 var(--font-body);color:var(--navy)}
.lk-lib ul{list-style:none;margin:0;padding:0 8px 8px}
.lk-lib li a{display:block;padding:10px 10px;border-top:1px solid var(--line);text-decoration:none;color:var(--ink)}
.lk-lib li a i{display:block;font-style:normal;font-size:13px;color:var(--mut);line-height:1.35}
.lk-lib li a b{display:block;font:600 14.5px/1.35 var(--font-body);color:var(--navy)}
.lk-lib li a:hover b{color:var(--coral)}
.lk-none{color:var(--mut);border:1px dashed var(--line);border-radius:14px;padding:16px;text-align:center}
@media(max-width:380px){.lk .bt{grid-template-columns:1fr}}
</style>"""


# Posts not yet scheduled stay off the page until they are (HSREP 3: Shafaat's decision pending, 31 Oct 2026).
HOLD = set()  # hsrep3 released 31 Oct (scheduled Dec 15)


def at_ms(d, hhmm="11:00"):
    h, m = map(int, hhmm.split(":"))
    return int(datetime.datetime.combine(datetime.date.fromisoformat(d), datetime.time(h, m), tzinfo=TZ).timestamp() * 1000)


def card(p):
    d, k, title, links = p[:4]
    when = datetime.date.fromisoformat(d).strftime("%b %-d, %Y")
    bt = []
    for lab, det, url, c in links:
        ext = url.startswith("http")
        sep = "&" if "?" in url.split("#")[0] else "?"
        base, _, frag = url.partition("#")
        href = f"{base}{sep}utm_source=SRC&utm_medium=social&utm_campaign={d}-reel-{k}&utm_content={c}" + (f"#{frag}" if frag else "")
        tgt = ' target="_blank" rel="noopener"' if ext else ""
        bt.append(f'<a class="k-{c}" href="{E(href)}" data-to="{c}"{tgt}><b>{E(lab)}</b><span>{E(det)}</span></a>')
    return (f'<li class="lk" id="{k}" data-at="{at_ms(d, p[4] if len(p) > 4 else "11:00")}" data-k="{k}" hidden>'
            f'<p class="m">{when}</p><h2>{E(title)}</h2><div class="bt">{"".join(bt)}</div></li>')


def library():
    out = ['<section class="lk-lib" id="earlier"><h2 class="lt">Everything else</h2><div class="lk-ev">']
    for title, url in LIBRARY:
        href = f"{url}?utm_source=SRC&utm_medium=social&utm_campaign=links-evergreen&utm_content=library"
        out.append(f'<a href="{E(href)}" data-to="library">{E(title)}</a>')
    return "".join(out) + "</div></section>"

def main():
    src = open(os.path.join(ROOT, "pilot-fit.html"), encoding="utf-8").read()
    head, rest = src.split("</head>", 1)
    head = re.sub(r"<title>.*?</title>", "<title>Every link from our posts - HSREP</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="The link from HSREP on Instagram and Facebook: every post, with each of its links one tap away.">', head)
    head = head.replace('href="https://hsraep.org/pilot-fit.html"', 'href="https://hsraep.org/links/"')
    head = re.sub(r'<style id="pf-css">.*?</style>', "", head, flags=re.S) + CSS
    body_open = rest[:rest.index("<main>")]
    foot = rest[rest.index("</main>"):]
    foot = re.sub(r'<script id="pf-js">.*?</script>', "", foot, flags=re.S)
    main_html = ('<main><div class="wrap"><section class="lk-hero"><p class="eyebrow">From Instagram and Facebook</p>'
                 '<h1>Every link from our posts.</h1>'
                 '<p class="lead">Newest first. Each post has its sources, the initiative and the assistant, one tap each.</p></section>'
                 '<ol class="lk-list" id="lk">\n' + "\n".join(card(p) for p in sorted((p for p in POSTS if p[1] not in HOLD), key=lambda p: (p[0], p[4] if len(p) > 4 else "11:00"), reverse=True)) + '\n</ol>'
                 '<p class="lk-none" id="lk-none" hidden>Nothing posted yet. <a href="/">Start here</a>.</p>' + library() + '</div>')
    js = """<script id="lk-js">(function(){var now=Date.now(),src='hsrep-links';
try{var s=new URLSearchParams(location.search).get('utm_source');if(s&&/^[a-z0-9_-]{2,20}$/.test(s))src=s;}catch(e){}
var cs=[].slice.call(document.querySelectorAll('#lk .lk')),n=0;[].forEach.call(document.querySelectorAll('#earlier a'),function(a){a.href=a.getAttribute('href').replace('utm_source=SRC','utm_source='+src);});
cs.forEach(function(c){var on=now>=+c.dataset.at;c.hidden=!on;if(on)n++;[].forEach.call(c.querySelectorAll('a'),function(a){a.href=a.getAttribute('href').replace('utm_source=SRC','utm_source='+src);});});
document.getElementById('lk-none').hidden=n>0;
function tr(e,p){try{if(window.hsTrack)hsTrack(e,p);else if(window.gtag)gtag('event',e,p);}catch(_){}}
var h=(location.hash||'').slice(1);var c=h&&document.getElementById(h);if(c&&!c.hidden){c.classList.add('hit');c.scrollIntoView({block:'center'});}
document.getElementById('lk').addEventListener('click',function(e){var a=e.target.closest('a');if(a)tr('links_open',{post:a.closest('.lk').dataset.k,to:a.dataset.to,src:src});});document.getElementById('earlier').addEventListener('click',function(e){var a=e.target.closest('a');if(a)tr('links_open',{post:'earlier',to:a.pathname,src:src});});})();</script>"""
    out = head + "</head>" + body_open + main_html + foot.replace("</body>", js + "</body>", 1)
    os.makedirs(os.path.join(ROOT, "links"), exist_ok=True)
    open(os.path.join(ROOT, "links", "index.html"), "w", encoding="utf-8").write(out)
    print("links/index.html:", len(POSTS), "posts")


if __name__ == "__main__":
    main()
