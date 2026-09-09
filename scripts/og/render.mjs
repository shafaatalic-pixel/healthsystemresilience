/**
 * Render an HSREP social card to PNG.
 *
 *   node scripts/og/render.mjs og-roundtable
 *
 * Renders scripts/og/<name>.html at 1200x630 CSS pixels, twice over, and writes
 * assets/social/og/<name>.png at 2400x1260 — the size the rest of the card set
 * uses. The page is loaded from disk, so the HSREP logo resolves through its
 * relative path and the fonts come from Google Fonts over the network.
 *
 * The PNG lands as full-colour and is about 900KB. Run optimize.py after this
 * to quantise it to the ~310KB the other cards sit at:
 *
 *   python3 scripts/og/optimize.py assets/social/og/og-roundtable.png
 *
 * Needs Playwright. Either `npm i -D playwright` (which brings its own browser),
 * or set PW_CHROMIUM to a Chromium binary you already have:
 *
 *   PW_CHROMIUM=/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
 *     node scripts/og/render.mjs og-roundtable
 */
import { createRequire } from "module";
import { fileURLToPath, pathToFileURL } from "url";
import path from "path";
import fs from "fs";

const require = createRequire(import.meta.url);
const here = path.dirname(fileURLToPath(import.meta.url));
const siteRoot = path.resolve(here, "..", "..");

const name = process.argv[2] || "og-roundtable";
const src = path.join(here, name + ".html");
const out = path.join(siteRoot, "assets", "social", "og", name + ".png");

if (!fs.existsSync(src)) {
  console.error("no such card: " + src);
  process.exit(1);
}

let chromium;
try {
  ({ chromium } = require("playwright"));
} catch (e) {
  ({ chromium } = require("playwright-core"));
}

const launch = {};
if (process.env.PW_CHROMIUM) launch.executablePath = process.env.PW_CHROMIUM;

const browser = await chromium.launch(launch);
const page = await browser.newPage({
  viewport: { width: 1200, height: 630 },
  deviceScaleFactor: 2,
});
await page.goto(pathToFileURL(src).href, { waitUntil: "networkidle" });
// give the webfonts a beat to paint, or the card renders in the fallback stack
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(600);
await page.screenshot({ path: out });
await browser.close();

const kb = Math.round(fs.statSync(out).size / 1024);
console.log("wrote " + path.relative(siteRoot, out) + "  (" + kb + " KB, 2400x1260)");
console.log("now run: python3 scripts/og/optimize.py " + path.relative(siteRoot, out));
