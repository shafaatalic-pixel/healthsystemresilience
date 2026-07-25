/* ============================================================
   HSREP Analytics — Google Analytics 4 + Cloudflare Web Analytics
   ------------------------------------------------------------
   TO GO LIVE: paste your two IDs on the next two lines.
     1. GA_ID    — your GA4 Measurement ID   (looks like  G-XXXXXXXXXX)
                   Google Analytics → Admin → Data streams → your web stream.
     2. CF_TOKEN — your Cloudflare Web Analytics beacon token
                   Cloudflare dashboard → Analytics → Web Analytics → add
                   hsraep.org → copy the token from the <!-- ... --> snippet.
   Leave a value blank to keep that tool switched off. Nothing else to change.
   Both IDs are public beacon identifiers (they ship in the page source),
   not secret keys.
   ============================================================ */
(function () {
  var GA_ID    = "G-7NQTBY7GPK";                      /* GA4 Measurement ID — hsraep.org property */
  var CF_TOKEN = "3156abf2ff704feda229e970b0b2787d";  /* Cloudflare Web Analytics beacon token */

  var GA_ON = /^G-[A-Z0-9]{6,}$/.test(GA_ID);
  var CF_ON = /^[A-Za-z0-9]{6,}$/.test(CF_TOKEN);

  /* status object the Analytics Command Center reads */
  window.HS_ANALYTICS = { ga: GA_ON, cf: CF_ON, gaId: GA_ON ? GA_ID : null };

  /* ---------- Google Analytics 4 (gtag.js) ---------- */
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  if (GA_ON) {
    var g = document.createElement("script");
    g.async = true;
    g.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(g);
    gtag("js", new Date());
    gtag("config", GA_ID, { anonymize_ip: true });
  }

  /* ---------- Cloudflare Web Analytics ---------- */
  if (CF_ON) {
    var c = document.createElement("script");
    c.defer = true;
    c.src = "https://static.cloudflareinsights.com/beacon.min.js";
    c.setAttribute("data-cf-beacon", '{"token":"' + CF_TOKEN + '"}');
    document.head.appendChild(c);
  }

  /* ---------- event helper ---------- */
  function track(name, params) {
    try { if (window.gtag && GA_ON) gtag("event", name, params || {}); } catch (e) {}
  }
  window.hsTrack = track;

  /* ---------- segment: which page / section ---------- */
  function pageGroup() {
    var p = location.pathname;
    if (p === "/" || /index\.html$/.test(p) && !/articles\//.test(p)) return "home";
    if (/\/articles\//.test(p)) return "article";
    if (/initiative/.test(p)) return "initiative";
    if (/roundtable/.test(p)) return "roundtable";
    if (/season-1/.test(p)) return "season";
    if (/films/.test(p)) return "films";
    if (/about/.test(p)) return "about";
    if (/media/.test(p)) return "media";
    if (/dashboard/.test(p)) return "command-center";
    return "other";
  }
  var GROUP = pageGroup();

  function nearestSection(el) {
    var s = el.closest ? el.closest("section,[id]") : null;
    return (s && s.id) ? s.id : "unknown";
  }
  function linkClass(href, text) {
    href = href || ""; text = (text || "").toLowerCase();
    if (/tally\.so/.test(href)) return /endorse|name/.test(text) ? "endorse" : "respond";
    if (/buttondown|subscribe/.test(href) || /subscribe/.test(text)) return "newsletter";
    if (/calendly/.test(href) || /book|call|30/.test(text)) return "book_call";
    if (/roundtable/.test(href) || /roundtable|take part|discussion/.test(text)) return "roundtable";
    if (/\/initiative/.test(href) || /pilot|initiative/.test(text)) return "initiative";
    if (/\/articles\//.test(href) || /read the package|read the/.test(text)) return "article_open";
    if (/linkedin/.test(href)) return "linkedin";
    if (/shafaatalichoyon/.test(href)) return "founder_site";
    if (/\.pdf($|\?)/.test(href)) return "download_pdf";
    return "link";
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    /* ----- clicks: CTAs, engagement paths, outbound, downloads ----- */
    document.addEventListener("click", function (e) {
      var a = e.target.closest("a,button");
      if (!a) return;
      var href = a.getAttribute("href") || "";
      var text = (a.textContent || "").trim().slice(0, 80);
      var section = nearestSection(a);

      /* share controls */
      if (a.matches(".blockshare,.sharebtn,.cl") || /share|copy link/i.test(text)) {
        track("share_click", { engagement_type: "share", method: "copy_link",
                               page_group: GROUP, section: section });
        return;
      }
      /* engagement package cards (.ep) */
      if (a.classList && a.classList.contains("ep")) {
        track("engagement_action", { engagement_type: "engage_card",
          action_label: text, page_group: GROUP, section: section });
        return;
      }
      if (!href) return;
      var kind = linkClass(href, text);
      var isOutbound = /^https?:\/\//.test(href) && href.indexOf(location.host) === -1;

      /* meaningful conversion CTAs */
      if (["respond", "endorse", "newsletter", "book_call", "roundtable",
           "initiative", "article_open", "download_pdf"].indexOf(kind) !== -1) {
        track("cta_click", { engagement_type: "cta", cta: kind, cta_text: text,
                             page_group: GROUP, section: section, link_url: href });
      }
      if (isOutbound) {
        var dom = "";
        try { dom = new URL(href).hostname.replace(/^www\./, ""); } catch (x) {}
        track("outbound_click", { engagement_type: "outbound", link_domain: dom,
                                  link_url: href, link_text: text, page_group: GROUP });
      }
    }, true);

    /* ----- segment-wise section engagement (which parts get seen) ----- */
    if ("IntersectionObserver" in window) {
      var seen = {};
      var secIO = new IntersectionObserver(function (ents) {
        ents.forEach(function (en) {
          if (en.isIntersecting) {
            var id = en.target.id || nearestSection(en.target);
            if (id && !seen[id]) {
              seen[id] = 1;
              track("section_view", { engagement_type: "section", section: id, page_group: GROUP });
            }
            secIO.unobserve(en.target);
          }
        });
      }, { threshold: 0.4 });
      document.querySelectorAll("section[id],[id].pkgwrap,[id].engage,[id].casebox")
        .forEach(function (s) { secIO.observe(s); });
    }

    /* ----- scroll depth ----- */
    var marks = [25, 50, 75, 100], fired = {};
    function onScroll() {
      var h = document.documentElement;
      var sc = h.scrollTop || document.body.scrollTop;
      var max = (h.scrollHeight - h.clientHeight) || 1;
      var pct = Math.min(100, Math.round((sc / max) * 100));
      marks.forEach(function (m) {
        if (pct >= m && !fired[m]) {
          fired[m] = 1;
          track("scroll_depth", { engagement_type: "scroll", percent: m, page_group: GROUP });
        }
      });
    }
    var st;
    window.addEventListener("scroll", function () {
      clearTimeout(st); st = setTimeout(onScroll, 180);
    }, { passive: true });

    /* ----- film / video plays ----- */
    document.querySelectorAll("video").forEach(function (v) {
      v.addEventListener("play", function () {
        var name = v.getAttribute("data-film") ||
          (v.currentSrc || "").split("/").pop() || "video";
        track("film_play", { engagement_type: "film", film: name, page_group: GROUP });
      }, { once: false });
    });

    /* ----- engaged-time milestones ----- */
    [30, 60, 120, 240].forEach(function (secs) {
      setTimeout(function () {
        track("engaged_time", { engagement_type: "time", seconds: secs, page_group: GROUP });
      }, secs * 1000);
    });
  });
})();
