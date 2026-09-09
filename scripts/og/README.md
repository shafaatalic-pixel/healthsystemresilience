# Social cards

The OpenGraph images at `assets/social/og/*.png` are what Facebook, LinkedIn and
X show when someone shares a page. They are 2400×1260 (1200×630 at 2×).

Each card here is a plain HTML file rendered by a headless browser, so editing one
is editing text and CSS rather than reopening a design tool.

## Editing a card

```bash
node scripts/og/render.mjs og-roundtable
python3 scripts/og/optimize.py assets/social/og/og-roundtable.png
```

Then commit both the `.html` and the `.png`.

## Two rules learned the hard way

**No dates in the artwork.** The roundtable card carried "AUG 11–25" and one
question. The window closed, the question was reframed, and for a fortnight every
share advertised a campaign that no longer existed. State — "open now, no closing
date" — is safe. A date is a promise the image cannot keep.

**Re-scrape after deploying.** Facebook caches link previews indefinitely. After a
card changes, push the page URL through
[the Facebook sharing debugger](https://developers.facebook.com/tools/debug) and
[LinkedIn's Post Inspector](https://www.linkedin.com/post-inspector/) or both will
keep serving the old image, sometimes for months.

## Requirements

- Playwright: `npm i -D playwright`, or set `PW_CHROMIUM` to a Chromium binary you
  already have.
- Pillow for the optimise step: `pip3 install --user Pillow`.
- Network access when rendering: the fonts come from Google Fonts, the same
  families the site uses.
