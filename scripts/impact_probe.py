#!/usr/bin/env python3
"""
Ask GA4 the same question four ways, so a disagreement can be measured instead
of guessed at.

    GA4_SA_JSON="$(cat ...)" GA4_PROPERTY_ID=546797423 python3 scripts/impact_probe.py

Written on 9 September 2026 because scripts/impact_fetch.py returned reader
figures roughly a third of the Analytics Command Center's - 71 past thirty
seconds against 140 - across every bucket and every outbound domain at once.
A uniform factor like that is a metric or a bucketing difference, not a real
change, and the reader figure is the number this page is built on.

Prints every metric side by side and keeps GA4's "(not set)" rows, which the
fetcher drops. Read-only; writes nothing.
"""
import json
import os
import sys

LAUNCH = "2026-07-22"
METRICS = ["eventCount", "activeUsers", "totalUsers", "sessions"]


def session():
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    info = json.loads(os.environ["GA4_SA_JSON"])
    return AuthorizedSession(service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/analytics.readonly"]))


def report(s, prop, dims, event=None, limit=50):
    body = {"dateRanges": [{"startDate": LAUNCH, "endDate": "today"}],
            "dimensions": [{"name": d} for d in dims],
            "metrics": [{"name": m} for m in METRICS],
            "limit": limit, "keepEmptyRows": False}
    if event:
        body["dimensionFilter"] = {"filter": {
            "fieldName": "eventName",
            "stringFilter": {"matchType": "EXACT", "value": event}}}
    r = s.post("https://analyticsdata.googleapis.com/v1beta/properties/%s:runReport" % prop,
               json=body, timeout=60)
    if r.status_code != 200:
        print("   ! %s: %s" % (r.status_code, r.text[:200]))
        return []
    return [([v["value"] for v in row.get("dimensionValues", [])],
             [v["value"] for v in row.get("metricValues", [])])
            for row in r.json().get("rows", [])]


def table(title, rows, note=""):
    print("\n== %s" % title)
    if note:
        print("   %s" % note)
    print("   %-28s %10s %10s %10s %10s" % ("value", *METRICS))
    for dims, mets in rows:
        print("   %-28s %10s %10s %10s %10s" % ((" / ".join(dims) or "(empty)"), *mets))


def main():
    prop = os.environ.get("GA4_PROPERTY_ID", "").strip()
    if not prop or not os.environ.get("GA4_SA_JSON"):
        raise SystemExit("Set GA4_SA_JSON and GA4_PROPERTY_ID.")
    s = session()

    table("engaged_time, split by the seconds parameter",
          report(s, prop, ["customEvent:seconds"], "engaged_time"),
          "the fetcher reads activeUsers here and reported 71 / 27 / 12 / 9")
    table("engaged_time, no split", report(s, prop, [], "engaged_time"))

    table("scroll_depth, split by the percent parameter",
          report(s, prop, ["customEvent:percent"], "scroll_depth"),
          "the fetcher reads activeUsers at percent=100 and reported 33")

    table("outbound_click, split by link_domain",
          report(s, prop, ["customEvent:link_domain"], "outbound_click"),
          "the fetcher reads eventCount and drops (not set)")
    table("outbound_click, no split", report(s, prop, [], "outbound_click"))

    table("every event, for scale", report(s, prop, ["eventName"], None, limit=40))

    print("\nWhat to look for:")
    print("  * if a metric column matches the dashboard's 140 / 70 / 37 / 26,")
    print("    that column is the one the fetcher should be reading;")
    print("  * if a large (not set) row appears under link_domain, the domains")
    print("    are being dropped rather than missing.")


main()
