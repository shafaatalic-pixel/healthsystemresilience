#!/usr/bin/env python3
"""
The sentences the Impact page is allowed to say, and the conditions for each.

The page's figures change nightly, so some of its prose has to change with them.
Nothing here is generated: every sentence is written once, read once, and stored
below. The renderer *selects*; it never composes. A model writing live copy onto
a credibility page is how an unreviewed sentence ends up published at 3am under
someone's name.

Two rules, enforced in `pick()`:

  * A state with no matching rule renders nothing. A silent gap is recoverable;
    a wrong sentence is not.
  * Every number inside a sentence is substituted from the same field the tile
    reads, so the prose and the figure beside it cannot disagree.

Adding a state means writing the sentence here and reading it back aloud. That
is the review step, and it is the whole point of the file.
"""


def _n(x):
    return "{:,}".format(int(x or 0))


# Each entry: (predicate over the data dict, sentence template).
# First match wins, so order them narrowest first.
RULES = {

    # ---------------------------------------------------------------- readers
    "readers": [
        (lambda d: d["readers"].get("s30", 0) == 0,
         "Nobody stayed longer than thirty seconds in this window. That is not a "
         "presentation problem to solve on the page; it is an audience that has "
         "not arrived yet."),
        (lambda d: d["readers"].get("s240", 0) >= 50,
         "{s240} people read for more than four minutes. At this size that is not "
         "traffic, it is a readership, and it is small enough to write to by name."),
        (lambda d: d["readers"].get("s30", 0) > 0,
         "{s30} people stayed past thirty seconds and {s240} past four minutes. "
         "The second number is the one worth quoting: it describes reading, not "
         "arriving."),
    ],

    # ------------------------------------------------------------- the machines
    "machines": [
        (lambda d: d["machines"].get("ai_fetches", 0) == 0,
         "No AI agent fetched the site in this window. That is a change worth "
         "watching rather than a result."),
        (lambda d: d["machines"].get("ai_fetches", 0)
         > 20 * max(d["machines"].get("google_clicks", 0), 1),
         "AI agents fetched this site {ai} times in {days} days. Google search "
         "delivered {clicks} {clickword} over the whole life of the site. Retrieval is "
         "not a channel HSREP is preparing for; it is the channel HSREP already "
         "has."),
        (lambda d: True,
         "AI agents fetched this site {ai} times in {days} days, against {clicks} "
         "{clickword} from Google search since launch."),
    ],

    # ------------------------------------------------------- what did not work
    "participation": [
        (lambda d: d["participation"].get("responses", 0) == 0
         and d["participation"].get("form_clicks", 0) == 0,
         "Nobody reached the response form at all in this window. Whatever is "
         "wrong is upstream of the form, and no amount of work on the form will "
         "find it."),
        (lambda d: d["participation"].get("responses", 0) == 0,
         "{clicks} people opened the response form and none submitted one. The "
         "form now sits on the page rather than behind a link on another domain. "
         "Whether that was the barrier is not yet proven, and it will be visible "
         "here either way."),
        (lambda d: d["participation"].get("responses", 0) <= 2,
         "The first {responses} responses arrived after the form moved onto the "
         "page. Two is not evidence yet. It is also not zero, which is what the "
         "fourteen days before it produced."),
        (lambda d: True,
         "{responses} professionals have answered an open question. Responses "
         "began arriving once the form sat on the page itself, which is the "
         "clearest thing this record has shown about its own design."),
    ],

    # --------------------------------------------------------------- arrival
    "arrival": [
        (lambda d: d["arrival"].get("search", 0) > d["arrival"].get("social", 0),
         "Search now brings more people here than social does. That is the first "
         "sign of an audience that finds HSREP rather than one that is handed it."),
        (lambda d: d["arrival"].get("facebook", 0) > d["arrival"].get("linkedin", 0),
         "Facebook sends {fb} sessions against LinkedIn's {li}, which is the "
         "opposite of what the impressions data would predict. Impressions and "
         "arrivals rank the two platforms in opposite orders."),
        (lambda d: True,
         "LinkedIn sends {li} sessions against Facebook's {fb}, which matches "
         "what a professional audience would suggest and did not hold in "
         "Season 1."),
    ],
}


def _fields(d):
    m, p, a, r = d["machines"], d["participation"], d["arrival"], d["readers"]
    return {
        "s30": _n(r.get("s30")), "s60": _n(r.get("s60")),
        "s120": _n(r.get("s120")), "s240": _n(r.get("s240")),
        "ai": _n(m.get("ai_fetches")), "days": m.get("window_days", 7),
        "clicks": _n(m.get("google_clicks")),
        "clickword": "click" if (m.get("google_clicks") or 0) == 1 else "clicks",
        "responses": _n(p.get("responses")),
        "fb": _n(a.get("facebook")), "li": _n(a.get("linkedin")),
    }


def pick(section, d):
    """The one approved sentence for this section at these numbers, or ""."""
    f = _fields(d)
    # `clicks` means different things in two tables; keep each one local.
    for test, text in RULES.get(section, []):
        try:
            if test(d):
                local = dict(f)
                if section == "participation":
                    pn = d["participation"]
                    local["clicks"] = _n(pn.get("form_people", pn.get("form_clicks")))
                return text.format(**local)
        except Exception:
            continue
    return ""
