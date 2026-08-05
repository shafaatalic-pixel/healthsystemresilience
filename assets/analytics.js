/* ============================================================
 HSREP Analytics, Google Analytics 4 + Cloudflare Web Analytics
 ------------------------------------------------------------
 TO GO LIVE: paste your two IDs on the next two lines.
 1. GA_ID, your GA4 Measurement ID (looks like G-XXXXXXXXXX)
 Google Analytics, Admin, Data streams, your web stream.
 2. CF_TOKEN, your Cloudflare Web Analytics beacon token
 Cloudflare dashboard, Analytics, Web Analytics, add
 hsraep.org, copy the token from the snippet.
 Leave a value blank to keep that tool switched off. Nothing else to change.
 Both IDs are public beacon identifiers (they ship in the page source),
 not secret keys.

 Instrumentation (every meaningful action fires a GA4 event; Cloudflare
 counts all traffic cookielessly):
   page_view (auto)          section_view        scroll_depth
   engaged_time              cta_click (+cta)    share_click
   outbound_click            theme_toggle        menu_toggle
   faq_toggle                nav_click           form_submit
   film_play / film_progress / film_complete     file_download
   engagement_action         search
 ============================================================ */
(function () {
 var GA_ID = "G-7NQTBY7GPK"; /* GA4 Measurement ID, hsraep.org property */
 var CF_TOKEN = "3156abf2ff704feda229e970b0b2787d"; /* Cloudflare Web Analytics beacon token */

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
 if (/\/articles\//.test(p)) return "article";
 if (/initiative/.test(p)) return "initiative";
 if (/roundtable/.test(p)) return "roundtable";
 if (/season-1/.test(p)) return "season";
 if (/films/.test(p)) return "films";
 if (/about/.test(p)) return "about";
 if (/media/.test(p)) return "media";
 if (/methodology/.test(p)) return "methodology";
 if (/search/.test(p)) return "search";
 if (/dashboard|bdot-demo/.test(p)) return "demo";
 if (/(privacy|terms|accessibility)/.test(p)) return "legal";
 if (p === "/" || /index\.html$/.test(p)) return "home";
 return "other";
 }
 var GROUP = pageGroup();

 function nearestSection(el) {
 var s = el && el.closest ? el.closest("section[id],[id]") : null;
 return (s && s.id) ? s.id : "unknown";
 }

 /* classify a link into a meaningful conversion / navigation kind */
 function linkClass(href, text) {
 href = href || ""; text = (text || "").toLowerCase();
 if (/tally\.so/.test(href)) return /endorse|first professional|name on the record/.test(text) ? "endorse" : "respond";
 if (/buttondown|\/go\/subscribe|subscribe|newsletter/.test(href) || /subscribe|newsletter|follow the work/.test(text)) return "newsletter";
 if (/calendly/.test(href) || /book|30 seconds|call/.test(text)) return "book_call";
 if (/\/go\/partner|partner/.test(href) || /partner|host the pilot|work with me/.test(text)) return "partner";
 if (/\/go\/discuss|roundtable/.test(href) || /roundtable|join the discussion|take part|register your interest/.test(text)) return "roundtable";
 if (/\/initiative/.test(href) || /the initiative|prevention adoption|see the evidence/.test(text)) return "initiative";
 if (/\/articles\//.test(href) || /read the (package|record|piece|original)|explore season/.test(text)) return "article_open";
 if (/\/season-1/.test(href) || /season 1/.test(text)) return "season_open";
 if (/linkedin\.com/.test(href)) return "linkedin";
 if (/facebook\.com/.test(href)) return "facebook";
 if (/(twitter|x)\.com/.test(href)) return "x";
 if (/youtube\.com|youtu\.be/.test(href)) return "youtube";
 if (/shafaatalichoyon/.test(href)) return "founder_site";
 if (/\.pdf($|\?)/i.test(href)) return "download_pdf";
 if (/\.(xlsx|csv|zip|docx|pptx)($|\?)/i.test(href)) return "download_file";
 return "link";
 }
 var CONVERSIONS = ["respond","endorse","newsletter","book_call","partner","roundtable",
 "initiative","article_open","season_open","download_pdf","download_file"];

 function fileExt(href) {
 var m = (href || "").split("?")[0].match(/\.([a-z0-9]{2,5})$/i);
 return m ? m[1].toLowerCase() : "";
 }

 function ready(fn) {
 if (document.readyState !== "loading") fn();
 else document.addEventListener("DOMContentLoaded", fn);
 }

 ready(function () {

 /* ================= CLICKS ================= */
 document.addEventListener("click", function (e) {
 var el = e.target;
 var a = el.closest ? el.closest("a,button,summary,[role=button]") : null;
 if (!a) return;
 var href = a.getAttribute && a.getAttribute("href") || "";
 var text = (a.textContent || "").trim().slice(0, 80);
 var section = nearestSection(a);
 var cls = (a.className && a.className.baseVal !== undefined) ? a.className.baseVal : (a.className || "");
 cls = String(cls);

 /* theme toggle */
 if (a.matches && a.matches(".themebtn,[data-theme-toggle],#themeToggle,#themebtn") ||
 /theme/i.test(a.getAttribute && (a.getAttribute("aria-label") || a.getAttribute("title") || "") || "")) {
 var mode = (document.documentElement.getAttribute("data-theme") || "light");
 track("theme_toggle", { engagement_type: "ui", to_mode: mode === "dark" ? "light" : "dark", page_group: GROUP });
 return;
 }
 /* mobile menu toggle */
 if (a.matches && a.matches("#hmenu-btn,.hmenu,.menubtn,[data-menu-toggle]") ||
 /^menu$/i.test(text)) {
 track("menu_toggle", { engagement_type: "ui", page_group: GROUP });
 return;
 }
 /* share / copy-link controls */
 if ((a.matches && a.matches(".blockshare,.sharebtn,.cl,.sc,.socshare a,.socshare button")) ||
 (a.getAttribute && /hsCopyAnchor|hsShareUrl/.test(a.getAttribute("onclick") || "")) ||
 /share|copy link/i.test(text)) {
 var method = /copy|¶/i.test(text) || /cl\b/.test(cls) ? "copy_link" : "share";
 track("share_click", { engagement_type: "share", method: method,
 page_group: GROUP, section: section });
 return;
 }
 /* engagement package / engage cards (.ep) */
 if (a.classList && (a.classList.contains("ep") || a.classList.contains("engage"))) {
 track("engagement_action", { engagement_type: "engage_card",
 action_label: text || "engage_card", page_group: GROUP, section: section });
 return;
 }

 if (!href || href.charAt(0) === "#") {
 /* in-page anchor jump = light navigation signal */
 if (href && href.length > 1) {
 track("nav_click", { engagement_type: "nav", nav_type: "anchor",
 target: href, page_group: GROUP, section: section });
 }
 return;
 }

 var kind = linkClass(href, text);
 var isOutbound = /^https?:\/\//.test(href) && href.indexOf(location.host) === -1;
 var ext = fileExt(href);

 /* file downloads (pdf brief, dataset, social square, film, zip) */
 if (ext && /^(pdf|xlsx|csv|zip|docx|pptx|png|jpg|jpeg|mp4|webp)$/.test(ext)) {
 track("file_download", { engagement_type: "download", file_ext: ext,
 file_url: href, link_text: text, page_group: GROUP, section: section });
 }

 /* meaningful conversion CTAs */
 if (CONVERSIONS.indexOf(kind) !== -1) {
 track("cta_click", { engagement_type: "cta", cta: kind, cta_text: text,
 page_group: GROUP, section: section, link_url: href });
 } else if (isOutbound && ["linkedin","facebook","x","youtube","founder_site"].indexOf(kind) !== -1) {
 /* social / founder outbound is also intent-ish */
 track("cta_click", { engagement_type: "cta", cta: kind, cta_text: text,
 page_group: GROUP, section: section, link_url: href });
 } else {
 /* header/footer navigation to another page on-site */
 if (!isOutbound) {
 track("nav_click", { engagement_type: "nav", nav_type: "internal",
 target: href, link_text: text, page_group: GROUP, section: section });
 }
 }

 /* outbound (any external link) */
 if (isOutbound) {
 var dom = "";
 try { dom = new URL(href).hostname.replace(/^www\./, ""); } catch (x) {}
 track("outbound_click", { engagement_type: "outbound", link_domain: dom,
 link_url: href, link_text: text, page_group: GROUP });
 }
 }, true);

 /* ================= FAQ / details toggles ================= */
 document.querySelectorAll("details").forEach(function (d) {
 d.addEventListener("toggle", function () {
 if (!d.open) return;
 var sum = d.querySelector("summary");
 var label = sum ? (sum.textContent || "").trim().slice(0, 80) : "details";
 var isFaq = /faq/i.test(d.className) || d.closest("[id*='faq' i],[id*='question' i]");
 track(isFaq ? "faq_toggle" : "engagement_action",
 { engagement_type: isFaq ? "faq" : "toggle", action_label: label,
 page_group: GROUP, section: nearestSection(d) });
 });
 });

 /* ================= FORM submits (newsletter, register, search) ================= */
 document.addEventListener("submit", function (e) {
 var f = e.target;
 if (!f || f.tagName !== "FORM") return;
 var action = (f.getAttribute("action") || "").toLowerCase();
 var cls = String(f.className || "").toLowerCase();
 var kind = "form";
 if (/nlform|buttondown|subscribe|newsletter/.test(cls + " " + action)) kind = "newsletter";
 else if (/roundtable|register|discuss/.test(cls + " " + action)) kind = "roundtable";
 else if (/search/.test(cls + " " + action) || f.querySelector("input[type=search]")) kind = "search";
 track("form_submit", { engagement_type: "form", form_kind: kind, page_group: GROUP });
 if (kind === "newsletter" || kind === "roundtable") {
 track("cta_click", { engagement_type: "cta", cta: kind, cta_text: "form_submit", page_group: GROUP });
 }
 if (kind === "search") {
 var q = f.querySelector("input[type=search],input[name*='q' i]");
 track("search", { engagement_type: "search", search_term: q ? (q.value || "").slice(0, 60) : "", page_group: GROUP });
 }
 }, true);

 /* ================= section engagement (which parts get seen) ================= */
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
 document.querySelectorAll("section[id],[id].pkgwrap,[id].engage,[id].casebox,[id].panel")
 .forEach(function (s) { secIO.observe(s); });
 }

 /* ================= scroll depth ================= */
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

 /* ================= film / video: play, progress, complete ================= */
 document.querySelectorAll("video").forEach(function (v) {
 function name() {
 return v.getAttribute("data-film") || (v.currentSrc || "").split("/").pop() || "video";
 }
 v.addEventListener("play", function () {
 track("film_play", { engagement_type: "film", film: name(), page_group: GROUP });
 });
 var pmarks = { 25: 0, 50: 0, 75: 0 };
 v.addEventListener("timeupdate", function () {
 if (!v.duration) return;
 var pct = (v.currentTime / v.duration) * 100;
 [25, 50, 75].forEach(function (m) {
 if (pct >= m && !pmarks[m]) {
 pmarks[m] = 1;
 track("film_progress", { engagement_type: "film", film: name(), percent: m, page_group: GROUP });
 }
 });
 });
 v.addEventListener("ended", function () {
 track("film_complete", { engagement_type: "film", film: name(), page_group: GROUP });
 });
 });

 /* ================= engaged-time milestones ================= */
 [30, 60, 120, 240].forEach(function (secs) {
 setTimeout(function () {
 if (document.visibilityState === "visible") {
 track("engaged_time", { engagement_type: "time", seconds: secs, page_group: GROUP });
 }
 }, secs * 1000);
 });
 });
})();
