#!/usr/bin/env python3
"""
Two considered changes to the home hero. Not a redesign.

    python3 scripts/home_polish.py .

The hero was already the strongest thing on the site: the ring draws itself, the
crest fades up inside it, the coral point arrives last, the headline assembles
word by word, and the protection chain draws its line and pulses each step in
turn. Adding more motion there would be noise, so this does not.

What it changes:

  * The crest watermark, sitting at 5% opacity behind the hero, was the one
    completely static element in a large flat field of navy. It now drifts,
    slowly enough that nobody will catch it moving.
  * The line inviting a reader to the crest page was plain grey body text with a
    small underlined link, immediately below a headline that assembles itself.
    Now that the crest page is a showpiece, its doorway is marked as one: a
    coral rule, brighter type, and a link that separates from the sentence.

Both respect prefers-reduced-motion. Idempotent.
"""
import os
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
P = os.path.join(ROOT, "index.html")

CSS = '''<style id="hs-hero2">
/* The watermark drifts. 26 seconds a cycle, 3% of opacity and 18px of travel:
   the field stops being flat without anyone catching it in the act. */
.hero .crest{animation:heroDrift 26s var(--ease) infinite alternate;will-change:transform}
@keyframes heroDrift{
  from{transform:translate(0,0) scale(1);opacity:.045}
  to{transform:translate(-20px,-14px) scale(1.06);opacity:.075}}

/* The doorway to the crest page, marked as one. */
.hero .idline{position:relative;margin:24px 0 6px;padding:2px 0 2px 20px;
  border-left:2px solid rgba(242,109,90,.6);color:#C8D5E4;font-size:15px;
  line-height:1.62;max-width:56ch}
.hero .idline a{display:inline-block;margin-top:8px;color:#fff;font-weight:600;
  border-bottom:1px solid rgba(255,255,255,.28);padding-bottom:2px;
  transition:color .25s var(--ease),border-color .25s var(--ease),
             letter-spacing .25s var(--ease)}
.hero .idline a:hover,.hero .idline a:focus-visible{color:var(--coral);
  border-bottom-color:var(--coral);letter-spacing:.012em}

@media(prefers-reduced-motion:reduce){
  .hero .crest{animation:none;opacity:.05}
  .hero .idline a{transition:none}
}
</style></head>'''


def main():
    s = open(P, encoding="utf-8").read()
    if 'id="hs-hero2"' in s:
        print("  already current")
        return
    if 'class="idline"' not in s or 'class="crest"' not in s:
        raise SystemExit("ABORT: the hero is not shaped the way this expects")
    open(P, "w", encoding="utf-8").write(s.replace("</head>", CSS, 1))
    print("  hero polish added")


main()
print("done")
