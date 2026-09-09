#!/usr/bin/env python3
"""
Fetch the Impact page's figures from GA4, Cloudflare and Search Console.

    python3 scripts/impact_fetch.py --diff        # fetch, compare, write nothing
    python3 scripts/impact_fetch.py               # fetch and write data/impact.json

This is the automated path. `scripts/impact_build.py` reads the same figures out
of the Analytics Command Center on the Mac and is deliberately kept: running both
and diffing them is how a silently wrong API query gets caught. They should agree.

Credentials come from the environment and are never written anywhere:

    GA4_SA_JSON         Google service-account key, the whole JSON
    GA4_PROPERTY_ID     numeric property id (not G-XXXXXXX)
    CF_ANALYTICS_TOKEN  Cloudflare token, Zone Analytics: Read
    CF_ZONE_ID          zone id for hsraep.org
    GSC_SITE            Search Console property (default sc-domain:hsraep.org)

Each source is independent. If one fails the others still write, the previous
value for the missing block is carried forward, and data/impact_status.json
records which source did not answer. A page that goes quiet about a failure is
the one thing this page must never do.

What this deliberately does NOT emit: only computed aggregates. No per-visitor
rows, and no city list beyond the datacentre names published *because* they are
excluded.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "impact.json")
STATUS = os.path.join(ROOT, "data", "impact_status.json")
LAUNCH = "2026-07-22"

# Hyperscale locations. A "user" here is a machine in a server farm, not a reader.
# Kept byte-identical to scripts/impact_build.py: the two paths must agree.
DATACENTRE = {
    "ashburn", "council bluffs", "boardman", "the dalles", "moncks corner",
    "quincy", "des moines", "papillion", "cheyenne", "mount pleasant",
}

GA_SCOPES = ["https://www.googleapis.com/auth/analytics.readonly",
             "https://www.googleapis.com/auth/webmasters.readonly"]


def today():
    return dt.date.today().isoformat()


# ---------------------------------------------------------------- google auth
def google_session():
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    raw = os.environ.get("GA4_SA_JSON", "").strip()
    if not raw:
        raise RuntimeError("GA4_SA_JSON is not set")
    info = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(info, scopes=GA_SCOPES)
    return AuthorizedSession(creds)


# ------------------------------------------------------------------- GA4
def ga_report(sess, prop, dims, mets, dim_filter=None, limit=100):
    body = {
        "dateRanges": [{"startDate": LAUNCH, "endDate": "today"}],
        "dimensions": [{"name": d} for d in dims],
        "metrics": [{"name": m} for m in mets],
        "limit": limit,
        "keepEmptyRows": False,
    }
    if dim_filter:
        body["dimensionFilter"] = {"filter": {
            "fieldName": "eventName",
            "stringFilter": {"matchType": "EXACT", "value": dim_filter}}}
    r = sess.post(
        "https://analyticsdata.googleapis.com/v1beta/properties/%s:runReport" % prop,
        json=body, timeout=60)
    if r.status_code != 200:
        raise RuntimeError("GA4 %s: %s" % (r.status_code, r.text[:300]))
    d = r.json()
    rows = []
    for row in d.get("rows", []):
        rows.append(([v.get("value") for v in row.get("dimensionValues", [])],
                     [v.get("value") for v in row.get("metricValues", [])]))
    return rows


def as_int(x):
    try:
        return int(float(x))
    except Exception:
        return 0


def pairs(rows):
    """[[dim], [metric]] -> {dim: int(metric)}"""
    return {(d[0] or ""): as_int(m[0]) for d, m in rows}


# Custom dimensions have to be registered in GA4 Admin before the Data API will
# accept them, and an unregistered one is a hard 400 that aborts the whole
# report sequence. Registered today: cta, seconds, link_domain, page_group,
# percent, film, section. Anything optional goes through here so that a
# dimension someone un-registers costs one figure rather than the whole page.
DEGRADED = []


def optional(label, fn, default=None):
    try:
        return fn()
    except Exception as e:
        DEGRADED.append("%s (%s)" % (label, str(e)[:90]))
        return {} if default is None else default


def fetch_ga4():
    prop = os.environ.get("GA4_PROPERTY_ID", "").strip()
    if not prop:
        raise RuntimeError("GA4_PROPERTY_ID is not set")
    s = google_session()

    tot = ga_report(s, prop, [], ["activeUsers", "sessions", "screenPageViews",
                                  "engagementRate", "userEngagementDuration"], limit=1)
    t = tot[0][1] if tot else ["0"] * 5
    users, sess_n, pv = as_int(t[0]), as_int(t[1]), as_int(t[2])
    eng_rate = round(float(t[3] or 0) * 100)
    avg_eng = round(float(t[4] or 0) / users) if users else 0

    cities = pairs(ga_report(s, prop, ["city"], ["activeUsers"], limit=50))
    excluded, named = 0, []
    for name, n in cities.items():
        if name.strip().lower() in DATACENTRE:
            excluded += n
            named.append(name)

    channels = pairs(ga_report(s, prop, ["sessionDefaultChannelGroup"], ["sessions"]))
    sources = pairs(ga_report(s, prop, ["sessionSource"], ["sessions"], limit=100))

    def host(*keys):
        return sum(v for k, v in sources.items()
                   if any(k.startswith(x) for x in keys))

    events = pairs(ga_report(s, prop, ["eventName"], ["eventCount"], limit=100))

    # activeUsers, not eventCount, and this matters more than it looks.
    #
    # engaged_time fires once per page, so a reader who opens two pages and
    # stays thirty seconds on each fires the event twice. Measured 9 September
    # 2026: the seconds=30 bucket is 142 events but 71 people. The Analytics
    # Command Center had been reading eventCount and publishing it as "140
    # people read past thirty seconds", which was an event count wearing a
    # person's name. The page now publishes people. Do not change this back
    # without reading scripts/impact_probe.py and the correction note.
    secs = optional("engaged_time buckets", lambda: pairs(ga_report(
        s, prop, ["customEvent:seconds"], ["activeUsers"],
        dim_filter="engaged_time", limit=20)))
    pct = optional("scroll_depth buckets", lambda: pairs(ga_report(
        s, prop, ["customEvent:percent"], ["activeUsers"],
        dim_filter="scroll_depth", limit=20)))

    def bucket(d, key):
        v = d.get(str(key))
        return v if v is not None else None

    readers = {k: v for k, v in (
        ("s30", bucket(secs, 30)), ("s60", bucket(secs, 60)),
        ("s120", bucket(secs, 120)), ("s240", bucket(secs, 240)),
        ("bottom", bucket(pct, 100))) if v is not None}

    def real(d):
        """Drop GA4's "(not set)" bucket, which is not a label."""
        return {k: v for k, v in d.items() if k and k != "(not set)"}

    cta = real(optional("cta labels", lambda: pairs(ga_report(
        s, prop, ["customEvent:cta"], ["eventCount"],
        dim_filter="cta_click", limit=50))))

    # The same events counted as people. The drop-off is only honest if every
    # step is the same unit, and "clicked something" is a claim about people.
    people = optional("people per event", lambda: {
        d[0]: as_int(m[0]) for d, m in ga_report(
            s, prop, ["eventName"], ["activeUsers"], limit=100)})
    form_people = optional("people who reached the form", lambda: sum(
        as_int(m[0]) for d, m in ga_report(
            s, prop, ["customEvent:link_domain"], ["activeUsers"],
            dim_filter="outbound_click", limit=200)
        if d[0] == "tally.so"))

    groups = real(optional("page groups", lambda: pairs(ga_report(
        s, prop, ["customEvent:page_group"], ["eventCount"],
        dim_filter="section_view", limit=50))))

    # link_domain, not link_url: GA4 registers the domain, which is the only
    # part this page publishes anyway.
    outbound = {}
    for host_, n_ in real(optional("outbound domains", lambda: pairs(ga_report(
            s, prop, ["customEvent:link_domain"], ["eventCount"],
            dim_filter="outbound_click", limit=200)))).items():
        h = host_.lower().replace("www.", "")
        outbound[h] = outbound.get(h, 0) + n_

    return {
        "readers": readers,
        "raw": {"ga_users": users, "sessions": sess_n, "pageviews": pv,
                "engagement_rate": eng_rate, "avg_engaged_seconds": avg_eng,
                "excluded_datacentre": excluded, "excluded_cities": sorted(named),
                "excluded_is_floor": True},
        "arrival": {"direct": channels.get("Direct", 0),
                    "social": channels.get("Organic Social", 0),
                    "search": channels.get("Organic Search", 0),
                    "referral": channels.get("Referral", 0),
                    "facebook": host("facebook.com", "m.facebook.com", "lm.facebook.com"),
                    "linkedin": host("linkedin.com", "lm.linkedin.com")},
        "actions": {"cta": cta,
                    "cta_total": events.get("cta_click", 0),
                    "cta_people": people.get("cta_click", 0) if people else 0,
                    "cta_labelled": sum(cta.values()),
                    "downloads": events.get("file_download", 0),
                    "film_plays": events.get("film_play", 0),
                    "shares": events.get("share_click", 0),
                    "form_submits": events.get("form_submit", 0),
                    "outbound": outbound},
        "pages": groups,
        "form_people": form_people if isinstance(form_people, int) else 0,
    }


# ------------------------------------------------------------- Cloudflare
CF_GQL = "https://api.cloudflare.com/client/v4/graphql"

Q_REQUESTS = """
query($zone:String!,$since:Date!,$until:Date!){
  viewer{ zones(filter:{zoneTag:$zone}){
    httpRequests1dGroups(limit:60, filter:{date_geq:$since, date_leq:$until}){
      sum{ requests cachedRequests }
      uniq{ uniques }
    }}}}
"""

Q_AGENTS = """
query($zone:String!,$since:Time!){
  viewer{ zones(filter:{zoneTag:$zone}){
    httpRequestsAdaptiveGroups(limit:200, filter:{datetime_geq:$since},
      orderBy:[count_DESC]){
      count
      dimensions{ userAgent }
    }}}}
"""

# Substrings that identify an agent in a user-agent string, and the name the page
# uses for it. Order matters: the first match wins.
AI_AGENTS = [("ChatGPT-User", "ChatGPT-User"), ("Claude-User", "Claude-User"),
             ("ClaudeBot", "ClaudeBot"), ("OAI-SearchBot", "OAI-SearchBot"),
             ("GPTBot", "GPTBot"), ("PerplexityBot", "PerplexityBot"),
             ("Amazonbot", "Amazonbot"), ("Applebot", "Applebot"),
             ("Bytespider", "Bytespider"), ("meta-externalagent", "Meta-ExternalAgent"),
             ("Google-Extended", "Google-Extended"), ("CCBot", "CCBot")]
SEARCH_AGENTS = ["Googlebot", "bingbot", "DuckDuckBot", "YandexBot", "Baiduspider"]


def cf_post(token, query, variables):
    import requests
    r = requests.post(CF_GQL, timeout=60,
                      headers={"Authorization": "Bearer " + token,
                               "Content-Type": "application/json"},
                      json={"query": query, "variables": variables})
    if r.status_code != 200:
        raise RuntimeError("Cloudflare %s: %s" % (r.status_code, r.text[:300]))
    d = r.json()
    if d.get("errors"):
        raise RuntimeError("Cloudflare: %s" % json.dumps(d["errors"])[:300])
    z = d["data"]["viewer"]["zones"]
    if not z:
        raise RuntimeError("Cloudflare returned no zone; check CF_ZONE_ID")
    return z[0]


def fetch_cloudflare(days=7):
    token = os.environ.get("CF_ANALYTICS_TOKEN", "").strip()
    zone = os.environ.get("CF_ZONE_ID", "").strip()
    if not token or not zone:
        raise RuntimeError("CF_ANALYTICS_TOKEN or CF_ZONE_ID is not set")

    until = dt.date.today()
    since = until - dt.timedelta(days=days)
    out = {"window_days": days}

    z = cf_post(token, Q_REQUESTS, {"zone": zone, "since": since.isoformat(),
                                    "until": until.isoformat()})
    groups = z.get("httpRequests1dGroups") or []
    out["all_requests"] = sum(g["sum"]["requests"] for g in groups)
    out["cached_requests"] = sum(g["sum"]["cachedRequests"] for g in groups)
    out["human_visits"] = sum(g["uniq"]["uniques"] for g in groups)

    # The user-agent breakdown is a separate, narrower dataset and is not
    # available on every plan. Missing is a known state, not an error: the caller
    # carries the previous values forward and the status file says so.
    try:
        za = cf_post(token, Q_AGENTS,
                     {"zone": zone,
                      "since": (dt.datetime.utcnow() - dt.timedelta(days=days))
                      .strftime("%Y-%m-%dT%H:%M:%SZ")})
        counts, search_total = {}, 0
        for row in za.get("httpRequestsAdaptiveGroups") or []:
            ua = (row.get("dimensions") or {}).get("userAgent") or ""
            n = row.get("count") or 0
            for needle, name in AI_AGENTS:
                if needle.lower() in ua.lower():
                    counts[name] = counts.get(name, 0) + n
                    break
            else:
                if any(x.lower() in ua.lower() for x in SEARCH_AGENTS):
                    search_total += n
        agents = sorted(counts.items(), key=lambda kv: -kv[1])
        out["agents"] = [[k, v] for k, v in agents]
        out["ai_fetches"] = sum(counts.values())
        out["user_prompted"] = counts.get("ChatGPT-User", 0) + counts.get("Claude-User", 0)
        out["search_crawlers"] = search_total
        out["agents_available"] = True
    except Exception as e:
        out["agents_available"] = False
        out["agents_error"] = str(e)[:200]
    return out


# --------------------------------------------------------- Search Console
def fetch_gsc():
    site = os.environ.get("GSC_SITE", "sc-domain:hsraep.org")
    s = google_session()
    url = ("https://searchconsole.googleapis.com/webmasters/v3/sites/%s"
           "/searchAnalytics/query" % urllib.parse.quote(site, safe=""))
    # Search Console lags two to three days. The end date is deliberately not
    # "today": asking for days that do not exist yet drags the average down.
    end = dt.date.today() - dt.timedelta(days=3)
    body = {"startDate": LAUNCH, "endDate": end.isoformat(), "rowLimit": 1}
    r = s.post(url, json=body, timeout=60)
    if r.status_code != 200:
        raise RuntimeError("Search Console %s: %s" % (r.status_code, r.text[:300]))
    rows = r.json().get("rows") or [{}]
    row = rows[0]
    body["dimensions"] = ["page"]
    body["rowLimit"] = 500
    rp = s.post(url, json=body, timeout=60)
    pages = len(rp.json().get("rows") or []) if rp.status_code == 200 else None
    return {"google_clicks": as_int(row.get("clicks", 0)),
            "google_impressions": as_int(row.get("impressions", 0)),
            "google_position": round(float(row.get("position") or 0), 1),
            "pages_with_impressions": pages,
            "gsc_through": end.isoformat()}


# --------------------------------------------------------------------- main
def load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def flatten(o, p=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flatten(v, p + "." + str(k)))
    elif isinstance(o, list):
        out[p[1:]] = json.dumps(o)[:120]
    else:
        out[p[1:]] = o
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff", action="store_true",
                    help="fetch and report differences, write nothing")
    ap.add_argument("--only", default="ga4,cf,gsc")
    ap.add_argument("-o", "--out", default=OUT)
    a = ap.parse_args()
    want = set(x.strip() for x in a.only.split(","))

    prev = load(a.out)
    doc = json.loads(json.dumps(prev)) if prev else {}
    status = {"attempted": dt.datetime.now(dt.timezone.utc)
              .isoformat(timespec="seconds"), "sources": {}}
    failures = []

    if "ga4" in want:
        try:
            g = fetch_ga4()
            doc.update(g)
            status["sources"]["ga4"] = (
                "ok" if not DEGRADED
                else "ok, without: " + "; ".join(DEGRADED))
        except Exception as e:
            status["sources"]["ga4"] = "failed: %s" % str(e)[:200]
            failures.append("ga4")

    machines = dict(doc.get("machines") or {})
    if "cf" in want:
        try:
            c = fetch_cloudflare()
            machines["window_days"] = c["window_days"]
            machines["all_bot_requests"] = c["all_requests"]
            machines["cached_requests"] = c["cached_requests"]
            machines["human_visits"] = c["human_visits"]
            if c.get("agents_available"):
                machines["agents"] = c["agents"]
                machines["ai_fetches"] = c["ai_fetches"]
                machines["user_prompted"] = c["user_prompted"]
                machines["search_crawlers"] = c["search_crawlers"]
                status["sources"]["cf"] = "ok"
            else:
                status["sources"]["cf"] = ("ok, without the agent breakdown: %s"
                                           % c.get("agents_error", ""))
        except Exception as e:
            status["sources"]["cf"] = "failed: %s" % str(e)[:200]
            failures.append("cloudflare")

    if "gsc" in want:
        try:
            machines.update(fetch_gsc())
            status["sources"]["gsc"] = "ok"
        except Exception as e:
            status["sources"]["gsc"] = "failed: %s" % str(e)[:200]
            failures.append("search console")
    doc["machines"] = machines

    # Carried, not fetched: Season 1 is a locked historical record, and
    # participation comes from the response wall, not from analytics.
    doc.setdefault("season1", (prev or {}).get("season1", {}))
    doc.setdefault("participation", (prev or {}).get("participation", {}))
    if doc.get("actions", {}).get("outbound"):
        doc["participation"]["form_clicks"] = doc["actions"]["outbound"].get("tally.so", 0)
    if "form_people" in doc:
        doc["participation"]["form_people"] = doc.pop("form_people")

    doc["updated"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    doc["source"] = "GA4 Data API, Cloudflare GraphQL, Search Console API"
    doc["window"] = {"from": LAUNCH, "to": today()}

    status["ok"] = not failures
    status["failed"] = failures
    if not failures:
        status["last_success"] = status["attempted"]
    else:
        status["last_success"] = load(STATUS).get("last_success")

    if a.diff:
        before, after = flatten(prev), flatten(doc)
        keys = sorted(set(before) | set(after))
        n = 0
        for k in keys:
            if k in ("updated", "source", "window.to"):
                continue
            if before.get(k) != after.get(k):
                print("  %-38s %r -> %r" % (k, before.get(k), after.get(k)))
                n += 1
        print("%d field(s) differ" % n)
        print("status:", json.dumps(status["sources"], indent=2))
        return 0 if not failures else 1

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("wrote %s" % a.out)
    for k, v in status["sources"].items():
        print("  %-4s %s" % (k, v))
    return 0 if not failures else 1


sys.exit(main())
