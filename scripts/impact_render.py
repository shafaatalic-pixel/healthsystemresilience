#!/usr/bin/env python3
"""
Write the figures from data/impact.json into impact.html.

    python3 scripts/impact_render.py .

Everything lands between markers, in the markup, so the page is correct at first
paint. No fetch, no client-side arithmetic, no layout shift. Re-run after
scripts/impact_build.py and commit both files.
"""
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import impact_copy                                    # noqa: E402

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
MO = ["January", "February", "March", "April", "May", "June", "July",
      "August", "September", "October", "November", "December"]


def esc(x):
    return (str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def n(x):
    return "{:,}".format(int(x))


def date(iso):
    try:
        y, m, d = iso[:10].split("-")
        return "%d %s %s" % (int(d), MO[int(m) - 1], y)
    except Exception:
        return iso


def tile(value, label, quiet=False):
    return ('<div class="imp-t%s"><b>%s</b><span>%s</span></div>'
            % (" is-quiet" if quiet else "", value, label))


def bar(label, value, total, cls=""):
    pct = (value / total * 100) if total else 0
    return ('<div class="imp-bar %s"><span>%s</span><i style="width:%.1f%%"></i><b>%s</b></div>'
            % (cls, esc(label), max(pct, 0.6), n(value)))


# --------------------------------------------------------------------------
def r_updated(d):
    w = d["window"]
    return ("Since launch &middot; %s to %s &middot; refreshed %s"
            % (date(w["from"]), date(w["to"]), date(d.get("updated", w["to"]))))


def r_readers(d):
    r, raw = d["readers"], d["raw"]
    t = ['<div class="imp-tiles rv">',
         tile(n(r["s30"]), "read past thirty seconds"),
         tile(n(r["s60"]), "past one minute"),
         tile(n(r["s120"]), "past two minutes"),
         tile(n(r["s240"]), "past four minutes"),
         tile(n(r["bottom"]), "reached the bottom of a page"),
         "</div>"]
    cities = raw.get("excluded_cities") or []
    city_line = ""
    if cities:
        joined = ", ".join(cities[:-1]) + " and " + cities[-1] if len(cities) > 1 else cities[0]
        city_line = (" Of the %s visitors Google Analytics reports over the same window, "
                     "at least <b>%s</b> resolve to %s &mdash; hyperscale datacentre "
                     "locations, not readers. Only the largest cities are reported to us, "
                     "so that deduction is a floor."
                     % (n(raw["ga_users"]), n(raw["excluded_datacentre"]), esc(joined)))
    t.append(
        '<div class="imp-note rv"><p>HSREP does not publish a visitor count.%s</p>'
        '<p>The figures above are Google Analytics engagement-time and scroll-depth '
        'buckets, which describe what someone did rather than that a request arrived. '
        'They are smaller than a visitor count, and they are the ones this page uses.</p></div>'
        % city_line)
    t.append('<div class="imp-list rv">'
             '<div><span>Pageviews</span><b>%s</b></div>'
             '<div><span>Pages per session</span><b>%.1f</b></div>'
             '<div><span>Engagement rate</span><b>%d%%</b></div>'
             '<div><span>Average engaged time</span><b>%ds</b></div>'
             '</div>'
             % (n(raw["pageviews"]),
                (raw["pageviews"] / raw["sessions"]) if raw.get("sessions") else 0,
                raw["engagement_rate"], raw["avg_engaged_seconds"]))
    return "".join(t)


def r_arrival(d):
    a = d["arrival"]
    total = max(a["direct"] + a["social"] + a["search"] + a["referral"], 1)
    b = ['<div class="imp-bars rv">',
         bar("Direct", a["direct"], total),
         bar("Organic social", a["social"], total, "alt"),
         bar("Organic search", a["search"], total, "quiet"),
         bar("Referral", a["referral"], total, "quiet"),
         "</div>"]
    soc = max(a["facebook"] + a["linkedin"], 1)
    b += ['<h3 style="font-family:var(--font-mono);font-size:12px;letter-spacing:.05em;'
          'text-transform:uppercase;color:var(--muted);margin:26px 0 12px">Within social</h3>',
          '<div class="imp-bars rv">',
          bar("Facebook", a["facebook"], soc, "alt"),
          bar("LinkedIn", a["linkedin"], soc, "alt"),
          "</div>"]
    s1 = d["season1"]["by_platform"]
    b.append(
        '<div class="imp-note rv"><p>Season 1 carried %s impressions on Facebook and %s on '
        'LinkedIn, against <b>%s</b> and <b>%s</b> sessions here since launch.</p>'
        '<p>The windows and the metrics differ, so this is not a conversion rate and is not '
        'written as one. The ordering is the finding.</p></div>'
        % (n(s1["facebook_views"]), n(s1["linkedin_impressions"]),
           n(d["arrival"]["facebook"]), n(d["arrival"]["linkedin"])))
    return "".join(b)


def r_machines(d):
    m = d["machines"]
    out = ['<div class="imp-tiles rv">',
           tile(n(m["ai_fetches"]), "AI fetches in %d days" % m["window_days"]),
           tile(n(m["user_prompted"]), "of them triggered by a person asking an assistant"),
           tile(n(m["google_clicks"]), "clicks from Google search, since launch", quiet=True),
           tile(n(m["pages_indexed"]), "pages indexed", quiet=True),
           "</div>"]
    rows = "".join(
        '<tr%s><td>%s</td><td class="n">%s</td></tr>'
        % (' class="hi"' if a[0] in ("ChatGPT-User", "Claude-User") else "", esc(a[0]), n(a[1]))
        for a in m.get("agents", []))
    out.append('<table class="imp-tab rv"><thead><tr><th>Agent</th><th>Fetches</th></tr>'
               '</thead><tbody>%s</tbody></table>' % rows)
    out.append(
        '<div class="imp-note rv"><p>The two highlighted rows are the ones that represent a '
        'person: an assistant fetching this site because someone asked it a question. The '
        'rest are building a corpus. Google&rsquo;s average position for this site is %s%s.</p>'
        '<p>Scale, for honesty: %s bot requests reached the site in that window against %s '
        'human visits. Most of that is ordinary crawling and probing. The AI share is what '
        'is new.</p></div>'
        % (m["google_position"], "" if m.get("pages_indexed") is None
           else ", across %s indexed pages" % n(m.get("pages_indexed", 0)),
           n(m["all_bot_requests"]), n(m["human_visits"])))
    return "".join(out)


def r_actions(d):
    """Every recorded action. A refresh sometimes returns the click total without
    the per-control breakdown; when that happens the list is omitted and said to
    be missing, rather than printing zeros that read as findings."""
    a, p = d["actions"], d["pages"]
    labels = {"initiative": "Open the initiative", "article_open": "Open an article",
              "roundtable": "Open the roundtable", "download_pdf": "Download a PDF",
              "respond": "Add a response", "season_open": "Open the season",
              "book_call": "Book a call", "newsletter": "Subscribe",
              "founder_site": "Founder's site", "partner": "Partnership"}
    have_cta = bool(a.get("cta")) and a.get("cta_labelled", 0) > 0
    out = []
    if have_cta:
        items = sorted(a["cta"].items(), key=lambda kv: -kv[1])
        out.append('<div class="imp-list rv">')
        out += ['<div><span>%s</span><b>%s</b></div>' % (esc(labels.get(k, k)), n(v))
                for k, v in items]
        out.append("</div>")
        out.append('<p style="font-size:14px;color:var(--muted);max-width:70ch">%s recorded '
                   'clicks in total; %s of them carry a label and are listed above. The rest '
                   'fire from controls that do not name themselves.</p>'
                   % (n(a["cta_total"]), n(a["cta_labelled"])))
    else:
        out.append('<div class="imp-list rv"><div><span>Recorded clicks</span><b>%s</b></div>'
                   '</div>' % n(a.get("cta_total", 0)))
        out.append('<p style="font-size:14px;color:var(--muted);max-width:70ch">The '
                   'per-control breakdown was not returned by the most recent refresh, so it '
                   'is left out rather than shown as zeros. It returns on the next one.</p>')

    ptot = max(sum(p.values()), 1)
    out.append('<h3 style="font-family:var(--font-mono);font-size:12px;letter-spacing:.05em;'
               'text-transform:uppercase;color:var(--muted);margin:30px 0 12px">'
               'Where attention went</h3><div class="imp-bars rv">')
    order = sorted(p.items(), key=lambda kv: -kv[1])
    out += [bar(k.title(), v, ptot, "alt" if k in ("initiative", "roundtable") else "")
            for k, v in order]
    out.append("</div>")

    # the point stands on page views alone; the click figures are added only when
    # the refresh actually carried them
    clicks = ""
    if have_cta:
        clicks = (" and <b>%s</b> calls to action against the roundtable page&rsquo;s "
                  "<b>%s</b> views and <b>%s</b>"
                  % (n(a["cta"].get("initiative", 0)), n(p.get("roundtable", 0)),
                     n(a["cta"].get("roundtable", 0))))
    else:
        clicks = " against the roundtable page&rsquo;s <b>%s</b>" % n(p.get("roundtable", 0))
    out.append(
        '<div class="imp-note rv"><p>The initiative page drew <b>%s</b> section views%s. '
        'That is the audience saying where its attention already is, and it is why the '
        'featured roundtable question is now the one that belongs to the Prevention '
        'Adoption Gap.</p></div>' % (n(p.get("initiative", 0)), clicks))
    out.append('<div class="imp-list rv">'
               '<div><span>Film plays</span><b>%s</b></div>'
               '<div><span>Resource downloads</span><b>%s</b></div>'
               '<div><span>Shares</span><b>%s</b></div></div>'
               % (n(a["film_plays"]), n(a["downloads"]), n(a["shares"])))
    return "".join(out)


def r_participation(d):
    """What did not work. Zero is the finding here, so nothing is hidden."""
    p = d["participation"]
    fw = p["first_window"]
    lost = n(p.get("form_people", p.get("form_clicks", 0)))
    clicks = n(p.get("form_clicks", 0))
    return (
        '<div class="imp-tiles rv">%s%s</div>'
        '<div class="imp-note rv">'
        '<p>Roundtable &#8470; 01 opened on %s for fourteen days and closed on %s with no '
        'responses at all.</p>'
        '<p>Two causes, both now addressed. The question asked professionals to report on '
        'platform analytics most of them have no reason to have seen, so it was reframed on '
        '9 September and two further questions were opened beside it. And the form sat on '
        'another domain, which is where the %s were lost; it now sits on the roundtable '
        'page itself.</p>'
        '<p>Whether that was the right diagnosis is not yet known. It will be visible here '
        'either way.</p></div>'
        '<p><a class="btn accent" href="roundtable.html#respond">Answer an open question '
        '&rarr;</a></p>'
        % (tile(lost, "people reached the response form"),
           tile(n(p["responses"]), "responses received", quiet=True),
           date(fw["from"]), date(fw["to"]), lost))


def r_season1(d):
    s = d["season1"]
    b = s["by_platform"]
    return (
        '<div class="imp-tiles rv">%s%s%s%s</div>'
        '<div class="imp-list rv">'
        '<div><span>Facebook views</span><b>%s</b></div>'
        '<div><span>LinkedIn impressions</span><b>%s</b></div>'
        '<div><span>Instagram native views</span><b>%s</b></div></div>'
        '<div class="imp-note rv"><p>%s Reconciled %s. Every piece, its media package and '
        'the eleven findings drawn from this data live on the season hub.</p></div>'
        '<p><a class="btn ghost" href="season-1.html">The Season 1 record &rarr;</a> '
        '<a class="btn ghost" href="methodology.html">How it is counted &rarr;</a></p>'
        % (tile(n(s["impressions_sum"]), "impressions, summed across three platforms"),
           tile(n(s["pieces"]), "published pieces"),
           tile(n(s["countries"]), "health systems examined"),
           tile("$%d" % s["paid"], "spent on promotion"),
           n(b["facebook_views"]), n(b["linkedin_impressions"]), n(b["instagram_native_views"]),
           esc(s["note"]), esc(s["reconciliation"])))


def r_home(d):
    """The four figures the home page carries, and nothing more."""
    r, m, p = d["readers"], d["machines"], d["participation"]
    t = ('<div class="snap rv">'
         '<div><b>%s</b><span>readers past thirty seconds</span></div>'
         '<div><b>%s</b><span>past four minutes</span></div>'
         '<div><b>%s</b><span>AI fetches a week</span></div>'
         '<div><b>%s</b><span>clicks from Google search</span></div>'
         '</div>' % (n(r["s30"]), n(r["s240"]), n(m["ai_fetches"]), n(m["google_clicks"])))
    t += ('<p class="snapnote">Engaged readers rather than a visitor count, with datacentre '
          'traffic deducted and named. The record also carries what did not work: %s people '
          'clicked through to the response form and none submitted one.</p>' % n(p["form_clicks"]))
    t += '<p><a class="btn accent" href="impact.html">What the record shows <span class="ar">&rarr;</span></a></p>'
    return t



# --------------------------------------------------------------------------
# The drop-off, the clock, and the machine/human split. Added 9 September 2026.
# --------------------------------------------------------------------------

def status():
    """The nightly job's own record of itself. Absent is a legitimate state."""
    try:
        with open(os.path.join(ROOT, "data", "impact_status.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _parse(ts):
    try:
        return dt.datetime.fromisoformat((ts or "").replace("Z", "+00:00"))
    except Exception:
        return None


def r_clock(d):
    """When the figures were last refreshed, and when the next one is due.

    A countdown on its own would lie: if the 03:12 job fails it keeps ticking
    toward a refresh that already did not happen. So the healthy state counts
    down and the stale state says how old the figures are instead. Both are
    written into the markup here, so the page is correct before any script runs.
    """
    st = status()
    now = dt.datetime.now(dt.timezone.utc)
    last = _parse(st.get("last_success")) or _parse(d.get("updated"))
    # 07:12 UTC nightly, which is 03:12 ET on daylight time.
    nxt = now.replace(hour=7, minute=12, second=0, microsecond=0)
    if nxt <= now:
        nxt += dt.timedelta(days=1)
    grace = dt.timedelta(hours=26)
    stale = (last is None) or (now - last > grace)

    attrs = (' data-next="%s" data-last="%s" data-stale="%s"'
             % (nxt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                last.strftime("%Y-%m-%dT%H:%M:%SZ") if last else "",
                "1" if stale else "0"))

    if not st:
        # No automated run has happened yet. Saying "refreshed nightly" here
        # would be a promise the site is not yet keeping.
        return ('<p class="imp-clock is-manual" data-stale="0"><span class="dt"></span>'
                '<b>Refreshed by hand.</b> Last updated %s. The nightly job is built '
                'but not yet switched on.</p>'
                % date((d.get("updated") or "")[:10]))

    if stale:
        age = ""
        if last:
            days = max((now - last).days, 1)
            age = " These figures are %d day%s old." % (days, "" if days == 1 else "s")
        body = ('<b>Refreshed nightly at 03:12 ET.</b> The last run did not complete.%s'
                % age)
        if last:
            body += " Last successful run %s." % date(last.date().isoformat())
        cls = " is-stale"
        cd = ""
    else:
        mins = int((nxt - now).total_seconds() // 60)
        body = ('<b>Refreshed nightly at 03:12 ET.</b> Last run %s, from %s.'
                % (date(last.date().isoformat()),
                   ", ".join(k.upper() for k in sorted((st.get("sources") or {}).keys()))
                   or "GA4, Cloudflare and Search Console"))
        cls = ""
        cd = ('<span class="cd">Next refresh in %dh %02dm.</span>'
              % (mins // 60, mins % 60))
    return ('<p class="imp-clock%s"%s><span class="dt"></span>%s %s</p>'
            % (cls, attrs, body, cd))


# The drop-off. One window, since launch, because mixing Season 1's campaign
# impressions into this would claim a causal chain across a four-month gap
# during which the site did not exist.
def r_dropoff(d):
    """People, all the way down.

    Every step has to be a subset of the one above it or the percentages are
    meaningless, and every step has to be the same unit or they are worse than
    meaningless. Until 9 September the click steps counted events while the
    reader steps counted people, which made "clicked something" larger than
    "read past thirty seconds" and produced a negative drop. Both now count
    people. Depth measures like "past four minutes" are not subsets of anything
    below them, so they stay in "Who reads it" where they belong.
    """
    r, raw = d["readers"], d["raw"]
    a, p = d["actions"], d["participation"]
    plausible = max(raw.get("ga_users", 0) - raw.get("excluded_datacentre", 0), 0)
    clicked = a.get("cta_people", a.get("cta_total", 0))
    reached = p.get("form_people", p.get("form_clicks", 0))
    people = "cta_people" in a and "form_people" in p
    steps = [
        (raw.get("ga_users", 0), "Counted as visitors",
         "Google Analytics, since launch", ""),
        (plausible, "Plausibly human",
         "after %s resolving to datacentres are deducted"
         % n(raw.get("excluded_datacentre", 0)), ""),
        (r.get("s30", 0), "Read past thirty seconds", "engagement-time buckets", ""),
        (clicked, "Clicked something",
         "people, not clicks" if people else "recorded actions", ""),
        (reached, "Reached the response form",
         "people, not clicks" if people else "outbound clicks", ""),
        (p.get("responses", 0), "Responded", "the record", "end"),
    ]
    top = max(steps[0][0], 1)
    rows, prev = [], None
    for value, label, note, kind in steps:
        pct = (value / top * 100) if top else 0
        drop = ""
        if prev is not None and prev > 0 and value <= prev:
            drop = "&minus;%d%%" % round((prev - value) / prev * 100)
        rows.append(
            '<li%s><span class="fk">%s<i>%s</i></span>'
            '<span class="ft"><em style="width:%.2f%%"></em></span>'
            '<b>%s</b><u>%s</u></li>'
            % (' class="end"' if kind == "end" else "", esc(label), esc(note),
               max(pct, 0.5) if value else 0, n(value), drop))
        prev = value
    unit = ("Every line counts people, so the gap between any two of them is a "
            "real loss rather than an artefact of comparing different things."
            if people else
            "One window, one site. The lower lines count actions rather than "
            "people, which makes them an upper bound.")
    return ('<ol class="fn rv">%s</ol>'
            '<p class="fnnote">%s Season 1&rsquo;s %s impressions are deliberately '
            'not here: that campaign ran four months before this site existed and '
            'cannot have produced these visits.</p>'
            % ("".join(rows), unit, n(d["season1"]["impressions_sum"])))


def r_split(d):
    """Machines against people, the same seven days. The ratio is the finding, so
    the bars stay linear; the near-invisible ones are the point, not a bug."""
    m = d["machines"]
    rows = [("All requests reaching the site", m.get("all_bot_requests", 0), "navy"),
            ("Search-engine crawlers", m.get("search_crawlers", 0), "navy"),
            ("AI agents", m.get("ai_fetches", 0), "coral"),
            ("Asked for by a person", m.get("user_prompted", 0), "coral"),
            ("Human visits", m.get("human_visits", 0), "navy")]
    top = max(rows[0][1], 1)
    out = ['<div class="sp rv">']
    for label, value, tone in rows:
        out.append('<div class="sp-r"><span class="sp-k">%s</span>'
                   '<span class="sp-t"><i class="%s" style="width:%.2f%%"></i></span>'
                   '<b>%s</b></div>'
                   % (esc(label), tone, max(value / top * 100, 1.4) if value else 0,
                      n(value)))
    out.append("</div>")
    out.append('<p class="fnnote">Two orders of magnitude. Most of it is ordinary crawling '
               'and probing; the AI share is the part that is new, and the fourth line is '
               'the only one where a person asked a question that brought an agent here.</p>')
    return "".join(out)



OPTIONAL = {"CLOCK", "DROPOFF", "SPLIT"}

RENDER = {"UPDATED": r_updated, "READERS": r_readers, "ARRIVAL": r_arrival,
          "MACHINES": r_machines, "ACTIONS": r_actions,
          "PARTICIPATION": r_participation, "SEASON1": r_season1,
          "HOME": r_home, "CLOCK": r_clock, "DROPOFF": r_dropoff, "SPLIT": r_split}

# Regions that carry one of the approved sentences from scripts/impact_copy.py,
# chosen by the numbers. The renderer selects; it never composes.
SAYS = {"READERS": "readers", "MACHINES": "machines",
        "PARTICIPATION": "participation", "ARRIVAL": "arrival"}


def render(name, data):
    body = RENDER[name](data)
    say = impact_copy.pick(SAYS[name], data) if name in SAYS else ""
    if say:
        body = '<p class="imp-say">%s</p>' % say + body
    return body


def main():
    data = json.load(open(os.path.join(ROOT, "data", "impact.json"), encoding="utf-8"))
    for page, names in (("impact.html", [k for k in RENDER if k != "HOME"]),
                        ("index.html", ["HOME"])):
        p = os.path.join(ROOT, page)
        s = o = open(p, encoding="utf-8").read()
        hit = 0
        for name in names:
            pat = re.compile(r"(<!--IMPACT:%s:START-->).*?(<!--IMPACT:%s:END-->)" % (name, name), re.S)
            if not pat.search(s):
                if page == "index.html" or name in OPTIONAL:
                    continue          # not scaffolded onto the page yet
                raise SystemExit("ABORT: no %s marker in %s" % (name, page))
            s = pat.sub(lambda m: m.group(1) + render(name, data) + m.group(2), s, count=1)
            hit += 1
        if s != o:
            open(p, "w", encoding="utf-8").write(s)
            print("  rendered: %s (%d region%s)" % (page, hit, "" if hit == 1 else "s"))
        else:
            print("  already current: %s" % page)


if __name__ == "__main__":
    main()
