#!/usr/bin/env python3
"""Extract the Michigan source facts for the Prevention Gap Map from HRSA's UDS awardee file.

Reads HRSA's H80-<year>.xlsx (https://data.hrsa.gov/data/download) with the standard library only
and writes data/source/hrsa-h80-<year>-michigan.json: every Michigan awardee's colorectal screening
numbers exactly as HRSA publishes them, and every active site HRSA lists for them, counted by type.

This file is the ground truth that scripts/gapmap_verify.py checks the published map against.
Counts are taken from HRSA's rows directly, never from anything the map pipeline produced.

Run from the website root:
    python3 scripts/gapmap_extract.py ~/Downloads/H80-2025.xlsx
"""
import hashlib
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
PNS = '{http://schemas.openxmlformats.org/package/2006/relationships}'
STATE = 'MI'


def col_index(ref):
    letters = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


class Book:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        wb = ET.fromstring(self.z.read('xl/workbook.xml'))
        rels = ET.fromstring(self.z.read('xl/_rels/workbook.xml.rels'))
        target = {r.get('Id'): r.get('Target') for r in rels.iter(PNS + 'Relationship')}
        self.sheets = {}
        for s in wb.iter(NS + 'sheet'):
            t = target[s.get(RNS + 'id')].lstrip('/')
            self.sheets[s.get('name')] = t if t.startswith('xl/') else 'xl/' + t
        self.strings = []
        if 'xl/sharedStrings.xml' in self.z.namelist():
            with self.z.open('xl/sharedStrings.xml') as f:
                for ev, el in ET.iterparse(f):
                    if el.tag == NS + 'si':
                        self.strings.append(''.join(t.text or '' for t in el.iter(NS + 't')))
                        el.clear()

    def rows(self, name):
        with self.z.open(self.sheets[name]) as f:
            for ev, el in ET.iterparse(f):
                if el.tag != NS + 'row':
                    continue
                row = {}
                for c in el.iter(NS + 'c'):
                    t, v = c.get('t'), c.find(NS + 'v')
                    if t == 's' and v is not None:
                        val = self.strings[int(v.text)]
                    elif t == 'inlineStr':
                        val = ''.join(x.text or '' for x in c.iter(NS + 't'))
                    else:
                        val = v.text if v is not None else ''
                    row[col_index(c.get('r'))] = val
                el.clear()
                if row:
                    yield [row.get(i, '') for i in range(max(row) + 1)]

    def table(self, name):
        it = self.rows(name)
        head = [h.strip() for h in next(it)]
        for r in it:
            r = r + [''] * (len(head) - len(r))
            yield dict(zip(head, (x.strip() if isinstance(x, str) else x for x in r)))


def num(v):
    v = (v or '').replace(',', '').strip()
    if v in ('', '--', '-'):
        return None
    f = float(v)
    return int(f) if f == int(f) else f


def main(path):
    year = re.search(r'H80-(\d{4})', os.path.basename(path))
    if not year:
        raise SystemExit('expected a file named like H80-2025.xlsx')
    year = int(year.group(1))
    b = Book(path)

    cover = next(b.table('Coversheet'))
    refreshed = cover.get('DateOfLastReportRefresh', '').strip()
    if str(cover.get('ReportingYear', '')).strip() != str(year):
        raise SystemExit('Coversheet reporting year %r does not match the file name' % cover.get('ReportingYear'))
    if not refreshed:
        raise SystemExit('Coversheet: DateOfLastReportRefresh not found')

    info = [r for r in b.table('HealthCenterInfo') if r['HealthCenterState'] == STATE]
    ids = {r['BHCMISID'] for r in info}
    t6 = {r['BHCMISID']: r for r in b.table('Table6BClinicalmeasures') if r['BHCMISID'] in ids}
    P = '%ofAdultswithAppropriateScreeningforColorectalCancer'
    N = '#ofAdultswithAppropriateScreeningforColorectalCancer'
    D = 'TotalofAdults46-75ScreeningforColorectalCancer'

    sites = {k: {'active_permanent': 0, 'active_seasonal': 0, 'active_mobile_van': 0, 'active_other': 0,
                 'permanent_without_zip': 0, 'inactive': 0} for k in ids}
    for r in b.table('HealthCenterSiteInfo'):
        k = r['BHCMISID']
        if k not in ids:
            continue
        s = sites[k]
        if r['SiteStatus'].lower() != 'active':
            s['inactive'] += 1
            continue
        lt = r['LocationType'].lower()
        if lt == 'permanent':
            s['active_permanent'] += 1
            if not re.match(r'^\d{5}', r['SiteZIPCode'] or ''):
                s['permanent_without_zip'] += 1
        elif lt == 'seasonal':
            s['active_seasonal'] += 1
        elif lt == 'mobile van':
            s['active_mobile_van'] += 1
        else:
            s['active_other'] += 1

    centers = []
    for r in info:
        m = t6.get(r['BHCMISID'])
        if m is None:
            raise SystemExit('no Table 6B row for ' + r['HealthCenterName'])
        centers.append({'k': r['BHCMISID'], 'hrsa_name': r['HealthCenterName'], 'city': r['HealthCenterCity'],
                        'setting': r['UrbanRuralFlag'], 'rate_published': m[P] not in ('', '--'),
                        'rate': num(m[P]), 'num': num(m[N]), 'den': num(m[D]), 'sites': sites[r['BHCMISID']]})

    tot = lambda key: sum(c['sites'][key] for c in centers)
    out = {
        'source': {'file': os.path.basename(path), 'sha256': hashlib.sha256(open(path, 'rb').read()).hexdigest(),
                   'url': 'https://data.hrsa.gov/data/download', 'refreshed': refreshed,
                   'reporting_year': year, 'extracted': date.today().isoformat(), 'state': STATE},
        'totals': {'centers': len(centers), 'rates_published': sum(c['rate_published'] for c in centers),
                   'num': sum(c['num'] or 0 for c in centers), 'den': sum(c['den'] or 0 for c in centers),
                   'active_permanent': tot('active_permanent'), 'active_seasonal': tot('active_seasonal'),
                   'active_mobile_van': tot('active_mobile_van'), 'active_other': tot('active_other'),
                   'permanent_without_zip': tot('permanent_without_zip')},
        'centers': centers}
    os.makedirs('data/source', exist_ok=True)
    dest = 'data/source/hrsa-h80-%d-michigan.json' % year
    json.dump(out, open(dest, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('wrote', dest, json.dumps(out['totals']))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(os.path.expanduser(sys.argv[1]))
