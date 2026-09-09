#!/usr/bin/env python3
"""
Quantise a rendered social card down to the size the rest of the set sits at.

    python3 scripts/og/optimize.py assets/social/og/og-roundtable.png

Playwright writes full-colour PNGs of roughly 900KB. These cards are flat navy
with a handful of accent colours, so a 256-colour palette is visually identical
and lands around 310KB — in line with the other cards, and small enough that
Facebook and LinkedIn fetch it without complaint.

Needs Pillow:  pip3 install --user Pillow
"""
import os
import sys

from PIL import Image

if len(sys.argv) < 2:
    raise SystemExit("usage: optimize.py <card.png> [colours, default 256]")

path = sys.argv[1]
colours = int(sys.argv[2]) if len(sys.argv) > 2 else 256

before = os.path.getsize(path)
im = Image.open(path).convert("RGB")
im.quantize(colors=colours, method=Image.MEDIANCUT,
            dither=Image.FLOYDSTEINBERG).save(path, optimize=True)
after = os.path.getsize(path)

print("%s  %d KB -> %d KB  (%d colours)"
      % (path, before // 1024, after // 1024, colours))
