#!/usr/bin/env python3
"""
Build data/impact.json from the Analytics Command Center.

    python3 scripts/impact_build.py [path/to/analytics-command-center/index.html]

The dashboard already refreshes nightly and already holds the GA access, so this
reads its data blocks rather than opening a second path to Google Analytics. One
credential path, one set of numbers, no chance of the site and the dashboard
disagreeing.

If the path is omitted it falls back to $HSREP_DASHBOARD, then to the usual
location on this machine.

What this deliberately does NOT emit
------------------------------------
Only computed aggregates. No per-visitor rows, no city list beyond the datacentre
names that are excluded (which are published precisely because they are excluded),
nothing that could identify a reader.

The four rules, enforced here rather than left to whoever writes the page:

1. `ga_users` is carried only inside `raw`, next to the deduction, and the page
   template never prints it alone.
2. Impressions are impressions. Never "reach", never "people".
3. Every figure carries its window.
4. A figure that falls is published anyway.
"""
import json
import os
import re
import sys

# Hyperscale locations. A "user" here is a machine in a server farm, not a reader.
# Conservative on purpose: only places that are unambiguously datacentre regions.
DATACENTRE = {
    "ashburn",          # AWS us-east-1
    "council bluffs",   # Google us-central1
    "boardman",         # AWS us-west-2
    "the dalles",       # Google
    "moncks corner",    # Google
    "quincy",           # Microsoft
    "des moines",       # Microsoft
    "papillion",        # Google
    "cheyenne",         # Microsoft / Google
    "mount pleasant",   # Microsoft
}

DEFAULT = os.path.expanduser(
    "~/Documents/Claude/Artifacts/analytics-command-center/index.html")


def block(src, name):
    start, end = "/*<<%s_START>>*/" % name, "/*<<%s_END>>*/" % name
    if start not in src or end not in src:
        raise SystemExit(
            "That file does not carry the %s block, so it is not the Analytics\n"
            "Command Center. Pass the artifact's index.html, or set HSREP_DASHBOARD." % name)
    a = src.index(start) + len(start)
    b = src.index(end)
    m = re.search(r"=\s*(\{.*\})\s*;?\s*$", src[a:b].strip(), re.S)
    if not m:
        raise SystemExit("could not parse the %s block" % name)
    return json.loads(m.group(1))


def cityname(c):
    return (c.get("c") if isinstance(c, dict) else c[0]) or ""


def cityusers(c):
    return (c.get("u") if isinstance(c, dict) else c[1]) or 0


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("HSREP_DASHBOARD", DEFAULT)
    if not os.path.exists(path):
        raise SystemExit(
            "dashboard not found: %s\n"
            "pass its path, or set HSREP_DASHBOARD" % path)

    src = open(path, encoding="utf-8", errors="replace").read()
    H = block(src, "AUTO_DATA_HSREP")

    launch = H.get("win", {}).get("launch", {})
    ga = launch.get("ga", {})
    x2 = H.get("x2", {})
    eng = (x2.get("engsec") or {}).get("launch", {})
    scroll = (x2.get("scrollpct") or {}).get("launch", {})

    # --- readers, the figure the site publishes ---------------------------
    readers = {
        "s30": eng.get("30", 0),
        "s60": eng.get("60", 0),
        "s120": eng.get("120", 0),
        "s240": eng.get("240", 0),
        "bottom": scroll.get("100", 0),
    }

    # --- the deduction, published beside the raw figure -------------------
    excluded, named = 0, []
    for c in launch.get("cities", []):
        if cityname(c).strip().lower() in DATACENTRE:
            excluded += cityusers(c)
            named.append(cityname(c))
    raw = {
        "ga_users": ga.get("users", 0),
        "sessions": ga.get("sess", 0),
        "pageviews": ga.get("pv", 0),
        "engagement_rate": ga.get("engRate", 0),
        "avg_engaged_seconds": ga.get("avgEngSec", 0),
        "excluded_datacentre": excluded,
        "excluded_cities": named,
        "excluded_is_floor": True,   # only the top cities are reported to us
    }

    # --- how they arrived --------------------------------------------------
    ch = {c.get("n", ""): c.get("s", 0) for c in launch.get("channels", [])}
    src_rows = {s.get("n", ""): s.get("s", 0) for s in launch.get("sources", [])}
    def host(*keys):
        return sum(v for k, v in src_rows.items() if any(k.startswith(x) for x in keys))
    arrival = {
        "direct": ch.get("Direct", 0),
        "social": ch.get("Organic Social", 0),
        "search": ch.get("Organic Search", 0),
        "referral": ch.get("Referral", 0),
        "facebook": host("facebook.com", "m.facebook.com", "lm.facebook.com"),
        "linkedin": host("linkedin.com", "lm.linkedin.com"),
    }

    # --- read by machines --------------------------------------------------
    bots = H.get("bots", {}) or {}
    prompted = sum(n for name, n, *_ in (bots.get("ai") or [])
                   if name in ("ChatGPT-User", "Claude-User"))
    seo = H.get("seo", {}) or {}
    machines = {
        "window_days": bots.get("days", 7),
        "ai_fetches": bots.get("aiTotal", 0),
        "user_prompted": prompted,
        "agents": [[a[0], a[1]] for a in (bots.get("ai") or [])],
        "search_crawlers": bots.get("searchTotal", 0),
        "all_bot_requests": bots.get("total", 0),
        "human_visits": (H.get("cf") or {}).get("visits", 0),
        "google_clicks": seo.get("clicks", 0),
        "google_impressions": seo.get("impressions", 0),
        "google_position": seo.get("position", 0),
        "pages_indexed": seo.get("indexed", 0),
    }

    # --- what people did ---------------------------------------------------
    ev = launch.get("ev", {}) or {}
    out = {d[0]: d[1] for d in (x2.get("outboundStd") or [])}
    # cta_click counts every click; the labelled breakdown is smaller, because
    # some controls fire the event without a label. Publish both rather than
    # letting the sum of the list masquerade as the total.
    actions = {
        "cta": launch.get("cta", {}) or {},
        "cta_total": ev.get("cta_click", 0),
        "cta_labelled": sum((launch.get("cta") or {}).values()),
        "downloads": ev.get("file_download", 0),
        "film_plays": ev.get("film_play", 0),
        "shares": ev.get("share_click", 0),
        "outbound": out,
    }
    pages = launch.get("segments", {}) or {}

    # --- what did not work -------------------------------------------------
    participation = {
        "form_clicks": out.get("tally.so", 0),
        "responses": 0,          # the wall is the source once it has entries
        "first_window": {"from": "2026-08-11", "to": "2026-08-25", "responses": 0},
    }

    # --- season 1, locked facts, restated here so the page has one source ---
    season1 = {
        "impressions_sum": 57274,
        "by_platform": {"facebook_views": 36997,
                        "linkedin_impressions": 13054,
                        "instagram_native_views": 7223},
        "pieces": 9, "countries": 2, "paid": 0,
        "reconciliation": "above 94% against full-campaign dashboard locks",
        "note": "A sum of platform impressions. Not reach, not people.",
    }

    doc = {
        "updated": H.get("updated"),
        "source": "Analytics Command Center (GA4 G-7NQTBY7GPK + Cloudflare)",
        "window": {"from": H.get("launchDate", "2026-07-22"),
                   "to": (H.get("updated") or "")[:10]},
        "readers": readers,
        "raw": raw,
        "arrival": arrival,
        "machines": machines,
        "actions": actions,
        "pages": pages,
        "participation": participation,
        "season1": season1,
    }

    dest = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "data", "impact.json")
    if "-o" in sys.argv:
        dest = sys.argv[sys.argv.index("-o") + 1]
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("wrote %s" % dest)
    print("  window        %s to %s" % (doc["window"]["from"], doc["window"]["to"]))
    print("  readers       %d past 30s, %d past 4min, %d to the bottom"
          % (readers["s30"], readers["s240"], readers["bottom"]))
    print("  deduction     %d of %d GA users in %s"
          % (excluded, raw["ga_users"], ", ".join(named) or "no datacentre cities in the top list"))
    print("  machines      %d AI fetches in %d days, %d user-prompted, %d Google clicks"
          % (machines["ai_fetches"], machines["window_days"],
             machines["user_prompted"], machines["google_clicks"]))
    print("  actions       %d CTA clicks (%d labelled), %d downloads, %d film plays"
          % (actions["cta_total"], actions["cta_labelled"],
             actions["downloads"], actions["film_plays"]))


if __name__ == "__main__":
    main()
