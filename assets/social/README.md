# HSREP — social & link-preview assets

Committed so that (a) every major page has its own Open Graph link preview
instead of sharing one generic site card, and (b) the campaign creatives have
stable, citable URLs for emails, partner decks and press.

## /og — link-preview cards
1200 x 630 CSS, rendered at 2x = **2400 x 1260 px**. This matches the
`og:image:width` / `og:image:height` values already declared site-wide.
Wired into the `og:image` and `twitter:image` tags of the pages they front:

| file | page |
|---|---|
| og-season-1.png   | /season-1.html |
| og-articles.png   | /articles.html |
| og-methodology.png| /methodology.html |
| og-initiative.png | /initiative.html and /initiative/prevention-adoption-initiative.html |
| og-roundtable.png | /roundtable.html |
| og-about.png      | /about.html |
| og-media.png      | /media.html |
| og-films.png      | /films.html |

`/og-image.png` (repo root) stays the homepage card and the fallback.

## /cards — square campaign creatives
Nineteen files, **2160 x 2160 px**, about 0.9 MB each and 16.7 MB in total.
These are the full-resolution masters, not web-weight copies, and no page on the
site loads them. They are sized for native upload to Facebook, LinkedIn and
Instagram, which recompress on their own terms and reward the larger source.

They are committed so the posting kit, partner decks, emails and press can cite
a stable URL: `https://hsraep.org/assets/social/cards/<file>.png`. Each card
fronts one entry in the posting kit, and the kit lists which card belongs to
which post.

Re-compressed losslessly on 4 August 2026 with oxipng, level 6, safe chunks
stripped. That took the folder from 30.7 MB to 16.7 MB. Filenames, dimensions
and URLs are unchanged, and every file was checked pixel for pixel against its
original before the change was kept.

Copy on every card is drawn from the page it fronts. No claim appears here that
is not already published on hsraep.org. In particular: 57,274 is a **sum of
platform impressions**, not a count of unique people, and the Prevention
Adoption Initiative is described as proposed / in development.
