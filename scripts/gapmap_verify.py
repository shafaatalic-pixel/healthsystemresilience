#!/usr/bin/env python3
"""Verify every published Prevention Gap Map figure against HRSA's own numbers.

Ground truth is data/source/hrsa-h80-<year>-michigan.json, written by scripts/gapmap_extract.py
straight from HRSA's file. Nothing here is checked against another part of the map: each count is
recomputed from HRSA's rows and compared with what visitors see.

Checks
  1. data/gapmap-<year>.json: every center (rate, counts, setting, city, suppression), every center's
     clinic-site count, the number of site dots per center, and the Michigan and site totals.
  2. Page copy (scripts/gapmap_main.html and the built gap-map.html), the tour captions, llms.txt and
     the page description: every stated figure must equal the figure recomputed from the source.
     Any "<number> sites" phrase must be a number the source supports.
  3. Narration: each tour caption must be the caption its clip was recorded from
     (assets/gapmap-vo/recorded.json), so audio and text cannot drift apart.

Exit status 1 on any failure. scripts/gapmap_build.py runs this and refuses to write the page if it
fails; the pre-commit hook and the CI workflow run it too.

    python3 scripts/gapmap_verify.py            (from the website root)
"""
import html
import json
import math
import os
import re
import sys
from datetime import datetime

TARGET_X10 = 728          # 72.8% target, in tenths of a percent
WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def text_of(s):
    s = re.sub(r'<script\b.*?</script>|<style\b.*?</style>', ' ', s, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def expected(src):
    C = src['centers']
    N, D = src['totals']['num'], src['totals']['den']
    pub = [c for c in C if c['rate_published']]
    gap = lambda r: TARGET_X10 / 10 - r
    rate_of = lambda cs: 100 * sum(c['num'] for c in cs) / sum(c['den'] for c in cs)
    rural = [c for c in pub if c['setting'] == 'Rural']
    urban = [c for c in pub if c['setting'] == 'Urban']
    need = max(0, -(-(TARGET_X10 * D - 1000 * N) // 1000))
    e = {
        'year': src['source']['reporting_year'], 'nc': len(C), 'npub': len(pub), 'nsup': len(C) - len(pub),
        'num': N, 'den': D, 'r1': '%.1f' % (100 * N / D), 'gap1': '%.1f' % (TARGET_X10 / 10 - 100 * N / D),
        'notup': D - N, 'need': need, 'need_round': int(round(need, -2)),
        'need60': max(0, -(-(600 * D - 1000 * N) // 1000)),
        'met': sum(1 for c in pub if c['rate'] >= TARGET_X10 / 10),
        'b1': sum(1 for c in pub if 0 < gap(c['rate']) <= 10),
        'b2': sum(1 for c in pub if 10 < gap(c['rate']) <= 25),
        'b3': sum(1 for c in pub if gap(c['rate']) > 25),
        'rural': '%.1f' % rate_of(rural), 'urban': '%.1f' % rate_of(urban), 'nr': len(rural), 'nu': len(urban),
        'perm': src['totals']['active_permanent'], 'seas': src['totals']['active_seasonal'],
        'mob': src['totals']['active_mobile_van'], 'nozip': src['totals']['permanent_without_zip'],
        'refreshed': datetime.strptime(src['source']['refreshed'].split()[0], '%m/%d/%Y'),
    }
    e['nsup_word'] = WORDS[e['nsup']] if e['nsup'] < len(WORDS) else str(e['nsup'])
    return e


def check_data(src, G, fail):
    e = expected(src)
    m = G['meta']
    for key, want in (('year', e['year']), ('mi_num', e['num']), ('mi_den', e['den']), ('ncenters', e['nc']),
                      ('sites_permanent', e['perm']), ('sites_seasonal', e['seas']), ('sites_mobile', e['mob']),
                      ('refreshed', e['refreshed'].strftime('%Y-%m-%d'))):
        if m.get(key) != want:
            fail('data meta.%s is %r, HRSA says %r' % (key, m.get(key), want))
    S = {c['k']: c for c in src['centers']}
    if sorted(S) != sorted(c.get('k') for c in G['centers']):
        fail('data centers do not match HRSA Michigan awardees (by BHCMISID)')
        return
    dots = [0] * len(G['centers'])
    for s in G['sites']:
        dots[s[0]] += 1
        if not (0 <= s[1] <= G['W'] and 0 <= s[2] <= G['H']):
            fail('site dot off the map: %r' % (s,))
    for i, c in enumerate(G['centers']):
        h = S[c['k']]
        who = c['name']
        if c['setting'] != h['setting']:
            fail('%s: setting %s, HRSA %s' % (who, c['setting'], h['setting']))
        if c['city'].lower() != h['city'].lower():
            fail('%s: city %s, HRSA %s' % (who, c['city'], h['city']))
        if h['rate_published']:
            for f in ('rate', 'num', 'den'):
                if c[f] != h[f]:
                    fail('%s: %s %r, HRSA %r' % (who, f, c[f], h[f]))
        elif any(c[f] is not None for f in ('rate', 'num', 'den')):
            fail('%s: HRSA did not publish a rate, but the data shows numbers' % who)
        if c['nsites'] != h['sites']['active_permanent']:
            fail('%s: %d clinic sites shown, HRSA lists %d active permanent sites'
                 % (who, c['nsites'], h['sites']['active_permanent']))
        if dots[i] != c['nsites']:
            fail('%s: %d dots on the map but %d clinic sites stated' % (who, dots[i], c['nsites']))
    if len(G['sites']) != e['perm']:
        fail('map has %d site dots, HRSA lists %d active permanent sites' % (len(G['sites']), e['perm']))


def phrases_page(e):
    rf = e['refreshed'].strftime('%B %-d, %Y') if os.name != 'nt' else e['refreshed'].strftime('%B %d, %Y')
    return [
        'Michigan %s%%' % e['r1'], 'Gap to target %s points' % e['gap1'], 'At or above target %d of %d' % (e['met'], e['npub']),
        '%d of %d centers have a published rate. The %s without one' % (e['npub'], e['nc'], e['nsup_word']),
        '%s eligible adults not up to date. Reaching 72.8%% means about %s more' % (format(e['notup'], ','), format(e['need_round'], ',')),
        '%s%% vs %s%%' % (e['rural'], e['urban']),
        'across %d rural and %d urban centers with a published rate' % (e['nr'], e['nu']),
        '%d of %d centers are more than 25 points below' % (e['b3'], e['npub']),
        'stays at %s' % format(e['den'], ','), 'from %s%% to 72.8%%' % e['r1'],
        'refreshed by HRSA on %s' % rf, 'Data year %d' % e['year'],
        "all %d centers' published totals (%s of %s)" % (e['nc'], format(e['num'], ','), format(e['den'], ',')),
        "All %d permanent clinic sites that Michigan's %d health centers reported as active on December 31, %d"
        % (e['perm'], e['nc'], e['year']),
        "For %d sites HRSA's file has no ZIP code" % e['nozip'],
        'Seasonal sites (%d) and mobile vans (%d) are not shown' % (e['seas'], e['mob']),
    ]


def phrases_raw(e):
    return ['id="gm-mi-rate">%s<' % e['r1'], 'id="gm-hero-need">%s<' % format(e['need'], ','),
            'id="gm-goal-n">%s<' % format(e['need'], ',')]


def phrases_tour(e):
    return [
        "Michigan's %d federally funded health centers, %s%% of adults aged 46 to 75 were up to date on colorectal cancer screening in %d"
        % (e['nc'], e['r1'], e['year']),
        'All %d against one line' % e['npub'],
        'Rural centers reached %s%%, urban centers %s%%, and %d centers are more than 25 points below' % (e['rural'], e['urban'], e['b3']),
        'Reaching 72.8%% means %s more adults screened. Even a goal of 60%% would mean %s more'
        % (format(e['need'], ','), format(e['need60'], ',')),
        "HRSA's public %d file" % e['year'],
    ]


def phrases_llms(e):
    return ["Michigan's %d federally funded health centers in %d" % (e['nc'], e['year']),
            'Michigan: %s of %s eligible adults screened (%s%%); about %s more would reach the target. %s centers have no published rate'
            % (format(e['num'], ','), format(e['den'], ','), e['r1'], format(e['need_round'], ','), e['nsup_word'].capitalize())]


def check_text(label, s, phrases, fail, e=None):
    for p in phrases:
        if p not in s:
            fail('%s: expected "%s"' % (label, p))
    if e is not None:
        ok = {e['perm'], e['nozip']}
        for m in re.finditer(r'\b(\d[\d,]*) (?:permanent |active )?(?:clinic )?sites\b', s):
            n = int(m.group(1).replace(',', ''))
            if n not in ok:
                fail('%s: "%s" is not a site count HRSA supports (%s)' % (label, m.group(0), sorted(ok)))


def tour_steps(js):
    return re.findall(r"title:'([^']*)',\s*line:(\"[^\"]*\"|'[^']*')", js)


def run(root='.', built=None, llms=None):
    errs = []
    fail = errs.append
    G = json.load(open(os.path.join(root, 'data/gapmap-2025.json'), encoding='utf-8'))
    sp = os.path.join(root, 'data/source/hrsa-h80-%d-michigan.json' % G['meta']['year'])
    if not os.path.exists(sp):
        return ['missing %s: run scripts/gapmap_extract.py on HRSA\'s file first' % sp]
    src = json.load(open(sp, encoding='utf-8'))
    e = expected(src)
    check_data(src, G, fail)

    main = open(os.path.join(root, 'scripts/gapmap_main.html'), encoding='utf-8').read()
    check_text('gapmap_main.html', text_of(main), phrases_page(e), fail, e)
    check_text('gapmap_main.html (markup)', main, phrases_raw(e), fail)
    if built is None and os.path.exists(os.path.join(root, 'gap-map.html')):
        built = open(os.path.join(root, 'gap-map.html'), encoding='utf-8').read()
    if built is not None:
        check_text('gap-map.html', text_of(built), phrases_page(e), fail, e)
        check_text('gap-map.html (markup)', built, phrases_raw(e), fail)
        d = re.search(r'<meta name="description" content="([^"]*)"', built)
        want = 'all %d federally funded health centers in Michigan, from HRSA\'s %d data' % (e['nc'], e['year'])
        if not d or want not in html.unescape(d.group(1)):
            fail('gap-map.html: meta description should say "%s"' % want)

    js = open(os.path.join(root, 'assets/gapmap-tour-1.js'), encoding='utf-8').read()
    steps = tour_steps(js)
    caps = ' '.join(t + '. ' + norm(json.loads(l) if l.startswith('"') else l[1:-1]) for t, l in steps)
    check_text('tour captions', caps, phrases_tour(e), fail, e)
    rec = json.load(open(os.path.join(root, 'assets/gapmap-vo/recorded.json'), encoding='utf-8'))['steps']
    if len(rec) != len(steps):
        fail('tour has %d steps but %d recorded clips' % (len(steps), len(rec)))
    for (title, l), r in zip(steps, rec):
        cap = json.loads(l) if l.startswith('"') else l[1:-1]
        if norm(cap) != norm(r['caption']) or title != r['title']:
            fail('tour step "%s": caption changed since %s was recorded; re-record it and update recorded.json'
                 % (title, r['file']))
        if not os.path.exists(os.path.join(root, 'assets/gapmap-vo', r['file'])):
            fail('missing narration clip ' + r['file'])

    if llms is None and os.path.exists(os.path.join(root, 'llms.txt')):
        llms = open(os.path.join(root, 'llms.txt'), encoding='utf-8').read()
    if llms is not None:
        line = next((x for x in llms.splitlines() if 'gap-map.html' in x), '')
        check_text('llms.txt', line, phrases_llms(e), fail, e)
    return errs


if __name__ == '__main__':
    errs = run()
    if errs:
        print('Gap Map verification FAILED (%d):' % len(errs))
        for x in errs:
            print('  - ' + x)
        sys.exit(1)
    print('Gap Map verified against HRSA: all figures, site counts, captions and narration match.')
