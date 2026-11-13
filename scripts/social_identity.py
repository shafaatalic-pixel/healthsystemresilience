#!/usr/bin/env python3
"""Idempotent (13 Nov 2026): Follow HSREP adds Instagram + YouTube; sameAs for HSREP and founder; article author @id."""
import re, glob
IG='<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill-rule="evenodd" d="M7 3h10a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V7a4 4 0 0 1 4-4zm0 2a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm5 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8zm0 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm5.2-3.6a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2z"/></svg>'
YT='<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.7 15.1V8.9l5.8 3.1z"/></svg>'
ADD=('<a class="ig" href="https://www.instagram.com/hsraep/" target="_blank" rel="noopener" aria-label="HSREP on Instagram" title="HSREP on Instagram">'+IG+'</a>'
     '<a class="yt" href="https://www.youtube.com/playlist?list=PLc1RrZJwukkg" target="_blank" rel="noopener" aria-label="HSREP films on YouTube" title="HSREP films on YouTube">'+YT+'</a>')
CSS='footer .folw a.ig:hover,footer .folw a.ig:focus-visible{background:#C13584;border-color:#C13584}footer .folw a.yt:hover,footer .folw a.yt:focus-visible{background:#CC0000;border-color:#CC0000}'
ORG_OLD='"sameAs": ["https://www.linkedin.com/company/hsrep-org/", "https://www.facebook.com/HSREP.org"]'
ORG_NEW='"sameAs": ["https://www.linkedin.com/company/hsrep-org/", "https://www.facebook.com/HSREP.org", "https://www.instagram.com/hsraep/"]'
FOUNDER=('"sameAs": ["https://shafaatalichoyon.com/#person", "https://shafaatalichoyon.com", "https://www.linkedin.com/in/sacgrowthspecialist/", '
 '"https://www.youtube.com/@ShafaatAliChoyon", "https://www.instagram.com/shafaat.ali.choyon", "https://www.tiktok.com/@shafaat.ali.choyon", '
 '"https://www.facebook.com/Shafaat.Ali.Choyon", "https://www.facebook.com/sacgrowthspecialist", "https://www.wikidata.org/wiki/Q140372377"]')
changed=[]
for p in sorted(set(glob.glob('*.html')+glob.glob('*/*.html')+glob.glob('*/*/*.html'))):
    if p.startswith(('_archive','node_modules','first-draft')): continue
    s=open(p,encoding='utf-8').read(); o=s
    if 'class="fl-row"' in s and 'a class="ig"' not in s:
        s=re.sub(r'(<div class="fl-row">.*?aria-label="HSREP on Facebook".*?</a>)', lambda m: m.group(1)+ADD, s, count=1, flags=re.S)
    if 'a.ig:hover' not in s and 'a.li:focus-visible{background:#0A66C2;border-color:#0A66C2}' in s:
        s=s.replace('a.li:focus-visible{background:#0A66C2;border-color:#0A66C2}','a.li:focus-visible{background:#0A66C2;border-color:#0A66C2}'+CSS,1)
    s=s.replace(ORG_OLD,ORG_NEW)
    s=s.replace('"sameAs": ["https://www.linkedin.com/in/sacgrowthspecialist/", "https://shafaatalichoyon.com", "https://shafaatalichoyon.com/#person"]',FOUNDER)
    s=s.replace('"sameAs": ["https://shafaatalichoyon.com/#person", "https://www.linkedin.com/in/sacgrowthspecialist/"]',FOUNDER)
    s=s.replace('"author": {"@type": "Person", "name": "Md Shafaat Ali Choyon"','"author": {"@id": "https://shafaatalichoyon.com/#person", "@type": "Person", "name": "Md Shafaat Ali Choyon"')
    if s!=o: open(p,'w',encoding='utf-8').write(s); changed.append(p)
print(len(changed),'changed'); print(changed)
