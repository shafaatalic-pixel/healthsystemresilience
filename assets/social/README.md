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
1080 x 1080 px, 1x. These are the section cards used in the 28-link promotion
sequence. Full-resolution 2x masters are kept outside the repo; these are the
web-weight copies.

Copy on every card is drawn from the page it fronts. No claim appears here that
is not already published on hsraep.org. In particular: 57,274 is a **sum of
platform impressions**, not a count of unique people, and the Prevention
Adoption Initiative is described as proposed / in development.
