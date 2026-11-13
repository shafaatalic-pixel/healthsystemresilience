#!/usr/bin/env python3
"""Open data files for hsraep.org/data.html: built from the sources, checked against the sources.

Writes five CSV files into data/:
  gapmap-<year>-michigan-centers.csv   one row per Michigan health center, from HRSA's own rows
                                       (data/source/hrsa-h80-<year>-michigan.json); display names
                                       come from data/gapmap-<year>.json
  season1-posts-facebook.csv           post-level rows from assets/HSR_Season1_Master_Dataset.xlsx
  season1-posts-linkedin.csv
  season1-posts-instagram.csv
  season1-platform-totals.csv          the three dashboard totals and their sum, read from the workbook

Nothing is typed in by hand. --check rebuilds every file in memory and compares it with the file on
disk, then checks every figure stated on data.html and in the llms.txt line for data.html against
the same sources. Exit status 1 on any difference. scripts/gapmap_verify.py calls the Gap Map part,
so the pre-commit hook and CI refuse a commit that would publish a file that differs from HRSA.

    python3 scripts/open_data.py            write the files (from the website root)
    python3 scripts/open_data.py --check    verify, write nothing
"""
import csv
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from gapmap_extract import Book          # noqa: E402  (standard-library xlsx reader)
import gapmap_verify as GV               # noqa: E402

XLSX = 'assets/HSR_Season1_Master_Dataset.xlsx'
TABS = (('facebook', '04. Posts - Facebook', 'fb_views', 'Season 1 Dashboard Lock'),
        ('linkedin', '05. Posts - LinkedIn', 'impressions', 'Season 1 Dashboard Lock'),
        ('instagram', '06. Posts - Instagram', 'ig_native_calc', 'IG NATIVE TOTAL'))
GAP_COLS = ['bhcmis_id', 'hrsa_name', 'health_center', 'city', 'setting', 'rate_published',
            'adults_46_75_screened', 'adults_46_75_eligible', 'screening_rate_pct',
            'points_below_target_72_8', 'permanent_clinic_sites']


def _csv(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def _n(v):
    """A workbook cell as int, float or '' ; text stays text."""
    if v is None or v == '':
        return ''
    try:
        f = float(v)
    except (TypeError, ValueError):
        return v
    return int(f) if f == int(f) else f


def _slug(h):
    return re.sub(r'[^a-z0-9]+', '_', re.sub(r'[^\x00-\x7f]', '', str(h)).strip().lower()).strip('_')


def _plain(s):
    """Notes are published in plain ASCII: the workbook's emoji markers and long dash are removed."""
    s = str(s).replace(' — ', ': ')
    return re.sub(r'[^\x00-\x7f]+ ?', '', s).strip()


# ---------------------------------------------------------------- Gap Map
def gap_rows(src, G):
    names = {c['k']: (c['name'], c['city']) for c in G['centers']}
    order = [c['k'] for c in G['centers']]
    S = {c['k']: c for c in src['centers']}
    if sorted(order) != sorted(S):
        raise SystemExit('gapmap data and HRSA source list different centers')
    rows = []
    for k in order:
        c = S[k]
        pub = c['rate_published']
        rows.append([k, c['hrsa_name'], names[k][0], names[k][1], c['setting'], 'yes' if pub else 'no',
                     c['num'] if pub else '', c['den'] if pub else '', c['rate'] if pub else '',
                     ('%.1f' % (GV.gap_tenths(c['rate']) / 10)) if pub else '',
                     c['sites']['active_permanent']])
    if len(rows) != len(src['centers']):
        raise SystemExit('row count changed: %d in, %d out' % (len(src['centers']), len(rows)))
    return rows


def gap_csv(src, G):
    return _csv(GAP_COLS, gap_rows(src, G))


def check_gap_csv(src, G, path):
    """Each published row against HRSA's row. Returns a list of problems."""
    errs = []
    if not os.path.exists(path):
        return ['missing %s: run scripts/open_data.py' % path]
    got = open(path, encoding='utf-8', newline='').read()
    rows = list(csv.DictReader(io.StringIO(got)))
    S = {c['k']: c for c in src['centers']}
    if len(rows) != len(S):
        errs.append('centers CSV has %d rows, HRSA lists %d Michigan awardees' % (len(rows), len(S)))
    for r in rows:
        c = S.get(r['bhcmis_id'])
        if c is None:
            errs.append('centers CSV: %s is not a Michigan awardee in HRSA\'s file' % r['bhcmis_id'])
            continue
        who = r['health_center']
        if c['rate_published']:
            for col, f in (('adults_46_75_screened', 'num'), ('adults_46_75_eligible', 'den'), ('screening_rate_pct', 'rate')):
                if r[col] != str(c[f]):
                    errs.append('centers CSV, %s: %s is %s, HRSA %s' % (who, col, r[col], c[f]))
            want = '%.1f' % (GV.gap_tenths(c['rate']) / 10)
            if r['points_below_target_72_8'] != want:
                errs.append('centers CSV, %s: points below target %s, should be %s' % (who, r['points_below_target_72_8'], want))
        elif any(r[col] for col in ('adults_46_75_screened', 'adults_46_75_eligible', 'screening_rate_pct', 'points_below_target_72_8')):
            errs.append('centers CSV, %s: HRSA did not publish a rate, but the file shows numbers' % who)
        if r['rate_published'] != ('yes' if c['rate_published'] else 'no'):
            errs.append('centers CSV, %s: rate_published is wrong' % who)
        if r['permanent_clinic_sites'] != str(c['sites']['active_permanent']):
            errs.append('centers CSV, %s: %s sites, HRSA %d' % (who, r['permanent_clinic_sites'], c['sites']['active_permanent']))
        if r['hrsa_name'] != c['hrsa_name'] or r['setting'] != c['setting'] or r['city'].lower() != c['city'].lower():
            errs.append('centers CSV, %s: name, city or setting differs from HRSA' % who)
    if got != gap_csv(src, G):
        errs.append('centers CSV on disk is not what scripts/open_data.py builds from HRSA\'s rows')
    return errs


# ---------------------------------------------------------------- Season 1
def season(root):
    """Returns ({name: csv text}, facts). Raises SystemExit if the workbook does not add up."""
    b = Book(os.path.join(root, XLSX))
    out, facts = {}, {}
    for plat, tab, primary, lock in TABS:
        data = [r for r in b.rows(tab)]
        hi = next(i for i, r in enumerate(data) if 'Unit' in r)
        cols = [i for i, h in enumerate(data[hi]) if h != '']
        names = [_slug(data[hi][i]) for i in cols]
        ni, pi = names.index('notes'), names.index(primary)
        rows, post_sum, dash = [], None, None
        for r in data[hi + 1:]:
            r = r + [''] * (max(cols) + 1 - len(r))
            unit = str(r[cols[0]])
            if not unit:
                continue
            if unit.upper().startswith('POST SUM'):
                post_sum = _n(r[cols[pi]])
                continue
            if unit.upper().startswith(lock.upper()):
                vals = [_n(x) for x in r[1:] if x != '']
                dash = next(v for v in vals if isinstance(v, (int, float)))
                continue
            rec = [_n(r[i]) for i in cols]
            if isinstance(rec[2], str) and re.match(r'^\d{1,2}/\d{1,2}$', rec[2]):
                mo, da = map(int, rec[2].split('/'))
                rec[2] = '2026-%02d-%02d' % (mo, da)
            for j in range(3, len(rec)):                 # words found in a number column go to notes
                if j != ni and isinstance(rec[j], str) and rec[j] != '':
                    rec[ni] = (str(rec[ni]) + ' ' + rec[j]).strip()
                    rec[j] = ''
            rec[ni] = _plain(rec[ni])
            rows.append(rec)
        total = sum(x[pi] for x in rows if isinstance(x[pi], (int, float)))
        if post_sum is None or dash is None:
            raise SystemExit('%s: could not find the POST SUM or dashboard row in the workbook' % tab)
        if total != post_sum:
            raise SystemExit('%s: post rows add to %s, the workbook says %s' % (tab, total, post_sum))
        out['season1-posts-%s.csv' % plat] = _csv(names, rows)
        facts[plat] = {'rows': len(rows), 'post_sum': total, 'dash': dash}
    fb, li, ig = (facts[p]['dash'] for p in ('facebook', 'linkedin', 'instagram'))
    facts['total'] = fb + li + ig
    out['season1-platform-totals.csv'] = _csv(
        ['platform', 'metric', 'season1_total', 'source'],
        [['Facebook', 'Views', fb, 'Meta Professional Dashboard (dashboard-authoritative)'],
         ['LinkedIn', 'Impressions', li, 'LinkedIn Analytics (dashboard-authoritative)'],
         ['Instagram', 'Native views (total views minus cross-post referral views)', ig, 'Instagram post insights, calculated post by post'],
         ['All three', 'Organic views and impressions', facts['total'], 'Sum of the three rows above; Feb 21 to Apr 12, 2026; $0 ad spend']])
    return out, facts


# ---------------------------------------------------------------- the page
def page_phrases(e, f):
    c = lambda n: format(n, ',')
    day = e['refreshed'].strftime('%d %B %Y').lstrip('0')
    return [
        '%d health centers %d with a published rate' % (e['nc'], e['npub']),
        '%s patients screened of %s eligible patients' % (c(e['num']), c(e['den'])),
        '%s%% Michigan rate' % e['r1'],
        'One row per health center (%d rows)' % e['nc'],
        'the %d permanent clinic sites' % e['perm'],
        'reporting year %d (H80-%d.xlsx, refreshed %s)' % (e['year'], e['year'], day),
        'the rate for %s centers' % e['nsup_word'],
        'so the %d published rows do not add up' % e['npub'],
        '%s Facebook views + %s LinkedIn impressions + %s Instagram native views = %s views and impressions'
        % (c(f['facebook']['dash']), c(f['linkedin']['dash']), c(f['instagram']['dash']), c(f['total'])),
        '%d Facebook posts' % f['facebook']['rows'], '%d LinkedIn posts' % f['linkedin']['rows'],
        '%d Instagram posts' % f['instagram']['rows'],
        'The post rows add to %s Facebook views and %s LinkedIn impressions' % (c(f['facebook']['post_sum']), c(f['linkedin']['post_sum'])),
        '(%s and %s)' % (c(f['facebook']['dash']), c(f['linkedin']['dash'])),
        'add to %s' % c(f['total']),
    ]


def page_raw(e, f):
    c = lambda n: format(n, ',')
    return ['%s of %s eligible patients screened (%s%%)' % (c(e['num']), c(e['den']), e['r1']),
            '%d HRSA-funded health centers' % e['nc'],
            '%s Facebook views, %s LinkedIn impressions and %s Instagram native views, %s in total'
            % (c(f['facebook']['dash']), c(f['linkedin']['dash']), c(f['instagram']['dash']), c(f['total']))]


def llms_phrases(e, f):
    return ["all %d of Michigan's federally funded health centers" % e['nc'], format(f['total'], ',')]


def check(root=ROOT):
    errs = []
    G = json.load(open(os.path.join(root, 'data/gapmap-2025.json'), encoding='utf-8'))
    year = G['meta']['year']
    src = json.load(open(os.path.join(root, 'data/source/hrsa-h80-%d-michigan.json' % year), encoding='utf-8'))
    e = GV.expected(src)
    errs += check_gap_csv(src, G, os.path.join(root, 'data/gapmap-%d-michigan-centers.csv' % year))
    files, f = season(root)
    for name, want in files.items():
        p = os.path.join(root, 'data', name)
        if not os.path.exists(p):
            errs.append('missing data/%s: run scripts/open_data.py' % name)
        elif open(p, encoding='utf-8', newline='').read() != want:
            errs.append('data/%s is not what scripts/open_data.py builds from the Season 1 workbook' % name)
    dp = os.path.join(root, 'data.html')
    if os.path.exists(dp):
        s = open(dp, encoding='utf-8').read()
        GV.check_text('data.html', GV.text_of(s), page_phrases(e, f), errs.append, e)
        GV.check_text('data.html (markup)', s, page_raw(e, f), errs.append)
    lp = os.path.join(root, 'llms.txt')
    if os.path.exists(lp):
        line = next((x for x in open(lp, encoding='utf-8').read().splitlines() if '/data.html' in x), None)
        if line is not None:
            GV.check_text('llms.txt (data.html line)', line, llms_phrases(e, f), errs.append, e)
    return errs


def build(root=ROOT):
    G = json.load(open(os.path.join(root, 'data/gapmap-2025.json'), encoding='utf-8'))
    year = G['meta']['year']
    src = json.load(open(os.path.join(root, 'data/source/hrsa-h80-%d-michigan.json' % year), encoding='utf-8'))
    files, f = season(root)
    files['gapmap-%d-michigan-centers.csv' % year] = gap_csv(src, G)
    for name, text in sorted(files.items()):
        with open(os.path.join(root, 'data', name), 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
        print('wrote data/%s (%d rows)' % (name, text.count('\n') - 1))


if __name__ == '__main__':
    if '--check' in sys.argv:
        problems = check()
        if problems:
            print('Open data verification FAILED (%d):' % len(problems))
            for x in problems:
                print('  - ' + x)
            sys.exit(1)
        print('Open data verified: every CSV matches its source, and data.html matches the CSVs.')
    else:
        build()
