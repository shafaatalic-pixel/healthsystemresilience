#!/usr/bin/env python3
"""The lineage: one dated thread from a published argument to a proposed
pilot, placed on five pages. Each page marks its own step.

Run from the website root:  python3 scripts/lineage.py
Safe to run more than once: the block sits between LINEAGE markers and is
replaced in full each time, so edit STEPS or PAGES here, never the HTML.
"""
import re

CSS = '<link rel="stylesheet" href="/assets/css/lineage-1.css?v=20261002e">'
START, END = '<!--LINEAGE:START-->', '<!--LINEAGE:END-->'

# Chronological. (verb, title, href, meta)
STEPS = [
    ('Argued', 'When we ignore public health prevention, we pay the price',
     '/articles/when-we-ignore-prevention-we-pay/when-we-ignore-prevention-we-pay.html',
     '<b>The Eastern Echo</b> &middot; 14 Nov 2025'),
    ('Measured', 'Season 1: <!--N:total_word-->nine<!--/N--> pieces, two countries', '/season-1.html',
     '<b>57,274 impressions</b>, $0 paid &middot; 21 Feb &ndash; 12 Apr 2026'),
    ('Proposed', 'Prevention Adoption Initiative', '/initiative.html',
     'Published July 2026 with a working <a href="/dashboard-demo.html">worklist demo</a> &middot; <b>in development</b>, nothing deployed'),
    ('Put to peers', 'Roundtable &#8470; 02: where does preventive care break down?',
     '/roundtable.html#rt-02', 'Open since 9 Sep 2026 &middot; moderated, on the record'),
    ('Next', 'Colorectal Cancer Screening Completion Pilot', '/initiative.html#host',
     '<b>One host clinic sought</b> &middot; 12 months &middot; no HSREP fee for the first 3 months'),
    ('Then', 'The same routine, five other completion gaps', '/initiative-next.html#other-gaps',
     'Roadmap, <b>not scheduled</b> &middot; blood pressure, diabetic eye exam, kidney test, two follow-ups'),
]

FOOT = ('Every step is dated and links to the record. The initiative is proposed, not running: '
        'an HSREP initiative in development.')
HOW = '<a href="/about.html#how-hsrep-works">How HSREP works &rarr;</a>'

# page -> (kicker, heading, lead, here-step (1-based, or 0), wrapper, anchor-regex, insert-before?)
PAGES = {
    'index.html': (
        'The thread', 'From a published argument to a proposed pilot.',
        'HSREP argues in public, measures how the argument travels, proposes something that can be '
        'tested, and puts it back to the people who do the work. One thread, dated at every step.',
        0, 'band', r'<section class="rt-campaign-panel"', True),
    'articles/when-we-ignore-prevention-we-pay/when-we-ignore-prevention-we-pay.html': (
        'What this argument became', 'This piece is the first step of a thread that runs to a proposed pilot.',
        None, 1, 'article', r'<div class="engage" id="engage">', True),
    'season-1.html': (
        'What Season 1 led to', 'The argument did not stop at publication.',
        'The prevention argument, measured here, became a proposed pilot and an open question to practitioners.',
        2, 'band', r'<section class="band" id="the-argument-in-seven-parts">', True),
    'initiative.html': (
        'Where this came from', 'A pilot proposed from a published, measured argument.',
        'This page is the third step of a thread that began with an article. Each step is public and dated.',
        3, 'band', r'\n<div class="wrap">\n<section class="pai-role" id="host"', True),
    'roundtable.html': (
        'Where this question sits', 'Roundtable &#8470; 02 puts a published argument back to practitioners.',
        'The question is the fourth step of a thread from a published argument to a proposed pilot.',
        4, 'band', r'<section id="respond">', True),
}

SPY = ('<script id="thr-js">(function(){var h=document.documentElement;h.classList.add("thr-js");'
       'var els=[].slice.call(document.querySelectorAll(".thr"));if(!("IntersectionObserver" in window)){els.forEach(function(e){e.classList.add("in");});return;}'
       'var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target);}});},{rootMargin:"0px 0px -12% 0px"});'
       'els.forEach(function(e){io.observe(e);});})();</script>')


def block(kicker, heading, lead, here, wrapper):
    items = []
    for i, (v, t, h, m) in enumerate(STEPS, 1):
        cls = 'here' if i == here else ('then' if i == len(STEPS) else ('next' if i == len(STEPS) - 1 else 'done'))
        this = ' <span class="thr-this">this page</span>' if i == here else ''
        items.append(f'<li class="{cls}"><div class="thr-v">{v}{this}</div>'
                     f'<h3 class="thr-t"><a href="{h}">{t}</a></h3><p class="thr-m">{m}</p></li>')
    lead_html = f'<p class="thr-lead">{lead}</p>' if lead else ''
    inner = (f'<div class="thr-in"><div class="thr-k">{kicker}</div><h2 class="thr-h">{heading}</h2>{lead_html}'
             f'<ol>{"".join(items)}</ol><div class="thr-f"><span>{FOOT}</span>{HOW}</div></div>')
    if wrapper == 'band':
        top = ' thr-top' if here in (0, 3) else ''
        return (f'{START}<section class="thr-band{top}" aria-label="The thread from argument to pilot">'
                f'<div class="wrap"><div class="thr">{inner}</div></div></section>{END}')
    return f'{START}<div class="thr thr-article" aria-label="The thread from argument to pilot">{inner}</div>{END}'


def run(path):
    kicker, heading, lead, here, wrapper, anchor, before = PAGES[path]
    s = open(path, encoding='utf-8').read()
    o = s
    s = re.sub(re.escape(START) + r'[\s\S]*?' + re.escape(END) + r'\n?', '', s)
    html = block(kicker, heading, lead, here, wrapper)
    m = re.search(anchor, s)
    if not m:
        raise SystemExit(f'{path}: anchor not found')
    pos = m.start() if before else m.end()
    s = s[:pos] + html + '\n' + s[pos:]
    if CSS not in s:
        s = re.sub(r'<link rel="stylesheet" href="/assets/css/lineage-1\.css[^>]*>', '', s)
        s = s.replace('</head>', CSS + '</head>', 1)
    if 'id="thr-js"' not in s:
        s = s.replace('</body>', SPY + '</body>', 1)
    if s != o:
        open(path, 'w', encoding='utf-8').write(s)
        return True
    return False


if __name__ == '__main__':
    for p in PAGES:
        print(('changed ' if run(p) else 'same    ') + p)
