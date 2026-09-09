#!/usr/bin/env python3
"""
Write the figures from data/impact.json into impact.html.

    python3 scripts/impact_render.py .

Everything lands between markers, in the markup, so the page is correct at first
paint. No fetch, no client-side arithmetic, no layout shift. Re-run after
scripts/impact_build.py and commit both files.
"""
import json
import os
import re
import sys

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
        'They are smaller than a visitor count and they are the ones worth quoting.</p></div>'
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
        'LinkedIn. Since launch this site has taken <b>%s</b> sessions from Facebook and '
        '<b>%s</b> from LinkedIn. The two platforms rank in opposite orders depending on '
        'whether you count who saw an argument or who followed it home.</p>'
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
        'person: an assistant fetching this site because someone asked it a question. Over '
        'the same seven days Google search delivered <b>%s</b> click in total, at an average '
        'position of %s.</p>'
        '<p>Scale, for honesty: %s bot requests reached the site in that window against %s '
        'human visits. Most of that is ordinary crawling and probing. The AI share is what '
        'is new.</p></div>'
        % (n(m["google_clicks"]), m["google_position"],
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
    p = d["participation"]
    fw = p["first_window"]
    return (
        '<div class="imp-tiles rv">%s%s%s</div>'
        '<div class="imp-note rv">'
        '<p>Roundtable &#8470; 01 opened on %s for fourteen days and closed on %s with no '
        'responses. <b>%s</b> people clicked through to the response form over the life of '
        'the site and none submitted one.</p>'
        '<p>Two causes, both now fixed. The question asked professionals to report on '
        'platform analytics most of them have no reason to have seen, so it was reframed on '
        '9 September and two further questions were opened beside it. And the form sat on '
        'another domain, which is where the eleven were lost; it now sits on the roundtable '
        'page itself.</p>'
        '<p>Whether that was the right diagnosis is not yet known. It will be visible here '
        'either way.</p></div>'
        '<p><a class="btn accent" href="roundtable.html#respond">Answer an open question '
        '&rarr;</a></p>'
        % (tile(n(p["form_clicks"]), "clicks through to the response form"),
           tile(n(p["responses"]), "responses received", quiet=True),
           tile("0", "of that first window's fourteen days produced one", quiet=True),
           date(fw["from"]), date(fw["to"]), n(p["form_clicks"])))


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


RENDER = {"UPDATED": r_updated, "READERS": r_readers, "ARRIVAL": r_arrival,
          "MACHINES": r_machines, "ACTIONS": r_actions,
          "PARTICIPATION": r_participation, "SEASON1": r_season1,
          "HOME": r_home}


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
                if page == "index.html":
                    continue          # the snapshot has not been added yet
                raise SystemExit("ABORT: no %s marker in %s" % (name, page))
            s = pat.sub(lambda m: m.group(1) + RENDER[name](data) + m.group(2), s, count=1)
            hit += 1
        if s != o:
            open(p, "w", encoding="utf-8").write(s)
            print("  rendered: %s (%d region%s)" % (page, hit, "" if hit == 1 else "s"))
        else:
            print("  already current: %s" % page)


if __name__ == "__main__":
    main()
