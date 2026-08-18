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

 /* ---------- shared campaign slot + conversion hierarchy ---------- */
 function addCampaignStyles() {
 if (document.getElementById("hsrep-campaign-css")) return;
 var s = document.createElement("style");
 s.id = "hsrep-campaign-css";
 s.textContent = [
 ".hs-campaign{position:relative;z-index:1200;background:#0F2036;color:#fff;border-bottom:1px solid rgba(255,255,255,.16);font-family:Inter,system-ui,sans-serif}",
 ".hs-campaign-inner{max-width:1180px;margin:0 auto;min-height:42px;padding:7px clamp(18px,4vw,34px);display:flex;align-items:center;justify-content:center;gap:12px}",
 ".hs-campaign-kicker{flex:0 0 auto;font:700 10px/1 'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.13em;text-transform:uppercase;color:#F26D5A}",
 ".hs-campaign-main{color:#fff;text-decoration:none;font-size:13.5px;line-height:1.35;font-weight:600}",
 ".hs-campaign-main:hover,.hs-campaign-main:focus-visible{text-decoration:underline;text-underline-offset:3px}",
 ".hs-campaign-main strong{color:#F7A594;font-weight:700;white-space:nowrap}",
 ".hs-campaign-close{flex:0 0 auto;margin-left:5px;width:30px;height:30px;border:0;border-radius:999px;background:transparent;color:#AFC0D2;font:400 22px/1 Arial,sans-serif;cursor:pointer}",
 ".hs-campaign-close:hover,.hs-campaign-close:focus-visible{background:rgba(255,255,255,.1);color:#fff}",
 ".hs-campaign-mobile{display:none}",
 ".hs-initiative-bridge{margin:28px 0;padding:24px;border:1px solid #D9E1E9;border-left:4px solid #C43C25;border-radius:12px;background:#F7F9FB;color:#25364D;font-family:Inter,system-ui,sans-serif}",
 ".hs-initiative-bridge .hsib-k{font:700 10.5px/1 'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:#C43C25;margin-bottom:10px}",
 ".hs-initiative-bridge h2{margin:0 0 8px!important;color:#1C2E4A!important;font:600 clamp(1.25rem,1.05rem + .5vw,1.55rem)/1.25 Spectral,Georgia,serif!important}",
 ".hs-initiative-bridge p{margin:0 0 17px!important;max-width:68ch;font:400 14.5px/1.6 Inter,system-ui,sans-serif!important;color:#4C5968!important}",
 ".hsib-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap}",
 ".hsib-primary,.hsib-secondary{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:10px 16px;text-decoration:none!important;font:700 13px/1 Inter,system-ui,sans-serif!important}",
 ".hsib-primary{background:#C43C25;color:#fff!important;border:1px solid #C43C25}",
 ".hsib-primary:hover{background:#A83722;border-color:#A83722}",
 ".hsib-secondary{background:transparent;color:#1C2E4A!important;border:1px solid #C9D2DC}",
 ".hsib-follow{font:600 12.5px/1.3 Inter,system-ui,sans-serif!important;color:#5A6673!important;text-decoration:none!important}",
 ".engage .epaths.hs-prioritized{display:grid!important;grid-template-columns:minmax(0,1.35fr) minmax(220px,.65fr)!important;gap:12px!important}",
 ".engage .epaths.hs-prioritized .ep{min-width:0!important}",
 ".engage .epaths.hs-prioritized .hs-engage-primary{grid-row:span 2;background:#C43C25!important;border-color:#C43C25!important;color:#fff!important;padding:24px!important}",
 ".engage .epaths.hs-prioritized .hs-engage-primary b,.engage .epaths.hs-prioritized .hs-engage-primary span{color:#fff!important}",
 ".engage .epaths.hs-prioritized .hs-engage-secondary{border-color:#99A8B8!important}",
 ".engage .epaths.hs-prioritized .hs-engage-tertiary,.engage .epaths.hs-prioritized .hs-engage-fallback{background:transparent!important;border-color:transparent!important;padding:8px 2px!important}",
 ".engage .epaths.hs-prioritized .hs-engage-tertiary span,.engage .epaths.hs-prioritized .hs-engage-fallback span{font-size:11.5px!important}",
 "#secnav{scroll-padding-inline:24px;overscroll-behavior-inline:contain}",
 "#secnav a{scroll-margin-inline:18px}",
 "@media(max-width:720px){.hs-campaign-inner{justify-content:flex-start;gap:9px;min-height:44px;padding-right:10px}.hs-campaign-kicker,.hs-campaign-desktop{display:none}.hs-campaign-mobile{display:inline}.hs-campaign-main{font-size:12.5px;flex:1}.hs-campaign-close{margin-left:auto}.engage .epaths.hs-prioritized{grid-template-columns:1fr!important}.engage .epaths.hs-prioritized .hs-engage-primary{grid-row:auto}.hs-initiative-bridge{padding:20px}.hsib-actions{align-items:stretch;flex-direction:column}.hsib-primary,.hsib-secondary{width:100%}}"
 ].join("");
 document.head.appendChild(s);
 }

 function campaignState(cfg) {
 var now = new Date();
 var open = new Date((cfg.open || "2026-08-11") + "T00:00:00");
 var close = new Date((cfg.close || "2026-08-25") + "T23:59:59");
 if (now >= open && now <= close) return "roundtable";
 if (now > close) return "season2";
 return "upcoming";
 }

 function configureHeaderCta(state) {
 var ctas = document.querySelectorAll("header.site .row > a.btn.accent,header.site .row > a.cta,.hs-sitehdr .hs-hcta");
 ctas.forEach(function (a) {
 if (GROUP === "article") {
 a.href = "#engage"; a.textContent = "Add your response";
 } else if (GROUP === "initiative") {
 a.href = "#host"; a.textContent = "Request presentation";
 } else if (GROUP === "roundtable") {
 a.href = "/roundtable.html"; a.textContent = state === "roundtable" ? "Join Roundtable" : "Roundtable record";
 } else if (state === "roundtable") {
 a.href = "/roundtable.html"; a.textContent = "Join Roundtable";
 } else {
 a.href = "https://buttondown.com/shafaat"; a.target = "_blank"; a.rel = "noopener"; a.textContent = "Season 2 updates";
 }
 });
 }

 function renderCampaign(cfg) {
 var state = campaignState(cfg);
 configureHeaderCta(state);
 if (document.querySelector(".hs-campaign")) document.querySelector(".hs-campaign").remove();
 try { if (sessionStorage.getItem("hsrep-campaign-dismissed-v2") === state) return; } catch (e) {}
 var bar = document.createElement("div");
 bar.className = "hs-campaign";
 bar.setAttribute("role", "region");
 bar.setAttribute("aria-label", "Current HSREP campaign");
 var mainHref, kicker, desktop, mobile, action;
 if (state === "roundtable") {
 mainHref = "https://tally.so/r/VLBbYM"; kicker = "Roundtable № 01";
 desktop = "Open through August 25.";
 mobile = "Open through Aug 25."; action = "Respond now →";
 } else if (state === "upcoming") {
 mainHref = "/roundtable.html"; kicker = "Roundtable № 01";
 desktop = "Opens August 11.";
 mobile = "Opens Aug 11."; action = "View the question →";
 } else {
 mainHref = "https://buttondown.com/shafaat"; kicker = "Next season";
 desktop = "Season 2 is in development.";
 mobile = "Season 2 is in development."; action = "Get notified when it opens →";
 }
 bar.innerHTML = '<div class="hs-campaign-inner"><span class="hs-campaign-kicker">' + kicker + '</span>' +
 '<a class="hs-campaign-main" href="' + mainHref + '"' + (mainHref.indexOf("http") === 0 ? ' target="_blank" rel="noopener"' : "") + '>' +
 '<span class="hs-campaign-desktop">' + desktop + ' </span><span class="hs-campaign-mobile">' + mobile + ' </span><strong>' + action + '</strong></a>' +
 '<button class="hs-campaign-close" type="button" aria-label="Dismiss announcement">×</button></div>';
 var anchor = document.querySelector("header,.hs-sitehdr,#artnav,main");
 if (anchor) anchor.parentNode.insertBefore(bar, anchor); else document.body.insertBefore(bar, document.body.firstChild);
 bar.querySelector(".hs-campaign-close").addEventListener("click", function () {
 try { sessionStorage.setItem("hsrep-campaign-dismissed-v2", state); } catch (e) {}
 bar.remove();
 });
 }

 function installCampaign() {
 var fallback = { open: "2026-08-11", close: "2026-08-25" };
 renderCampaign(fallback);
 if (!window.fetch) return;
 fetch("/roundtables/rt-01.json", { cache: "no-store" })
 .then(function (r) { return r.ok ? r.json() : fallback; })
 .then(function (cfg) { renderCampaign(cfg || fallback); })
 .catch(function () {});
 }

 function improveSiteIA() {
 document.querySelectorAll("header nav a,.hs-hnav a,#hmenu-panel a").forEach(function (a) {
 if (/season-1\.html/.test(a.getAttribute("href") || "")) a.textContent = "Evidence";
 });
 var skip = document.querySelector(".skip-link");
 if (skip && document.body.firstElementChild !== skip) document.body.insertBefore(skip, document.body.firstChild);
 document.querySelectorAll(".chip,.er-chip").forEach(function (b) {
 function sync() { b.setAttribute("aria-pressed", b.classList.contains("on") ? "true" : "false"); }
 sync(); b.addEventListener("click", sync);
 });
 document.addEventListener("focusin", function (e) {
 var a = e.target && e.target.closest ? e.target.closest("#secnav a") : null;
 if (a && a.scrollIntoView) a.scrollIntoView({ block: "nearest", inline: "center" });
 });
 }

 function enhanceArticleEngagement() {
 if (GROUP !== "article") return;
 var engage = document.querySelector(".engage");
 if (!engage) return;
 var paths = engage.querySelector(".epaths");
 if (paths) {
 var items = Array.prototype.slice.call(paths.children);
 function match(rx) { return items.filter(function (x) { return rx.test((x.textContent || "").toLowerCase()); })[0]; }
 var respond = match(/respond/), share = match(/share/), endorse = match(/endorse/), newsletter = match(/new arguments|newsletter|follow/);
 if (respond) respond.classList.add("hs-engage-primary");
 if (share) share.classList.add("hs-engage-secondary");
 if (endorse) endorse.classList.add("hs-engage-tertiary");
 if (newsletter) newsletter.classList.add("hs-engage-fallback");
 [respond, share, endorse, newsletter].forEach(function (x) { if (x) paths.appendChild(x); });
 paths.classList.add("hs-prioritized");
 }
 var proof = engage.querySelector(".eproof");
 if (proof) proof.innerHTML = 'Season 1 generated <b>57,274 platform-reported views and impressions</b> across Facebook, LinkedIn, and Instagram at <b>$0</b> ad spend. This is a distribution measure, not unique reach or program impact. <a href="/methodology.html">See the methodology →</a>';
 var relevant = /when-we-ignore-prevention-we-pay|public-health-reform-for-economic-growth|increasing-public-health-investment/.test(location.pathname);
 if (relevant && !document.querySelector(".hs-initiative-bridge")) {
 var bridge = document.createElement("aside");
 bridge.className = "hs-initiative-bridge";
 bridge.setAttribute("aria-labelledby", "hsib-title");
 bridge.innerHTML = '<div class="hsib-k">From argument to application</div><h2 id="hsib-title">Could your organization help test a prevention-completion pilot?</h2>' +
 '<p>The proposed Prevention Adoption Initiative starts with one Southeast Michigan safety-net clinic and an independent academic evaluation partner. The first conversation is a focused 30-minute presentation—no commitment required.</p>' +
 '<div class="hsib-actions"><a class="hsib-primary" href="https://calendly.com/shafaat-alic/30min" target="_blank" rel="noopener">Request the 30-minute presentation →</a>' +
 '<a class="hsib-secondary" href="/initiative.html">Review the proposed pilot →</a><a class="hsib-follow" href="https://buttondown.com/shafaat" target="_blank" rel="noopener">or follow initiative updates →</a></div>';
 engage.parentNode.insertBefore(bridge, engage);
 }
 }

 ready(function () {

 addCampaignStyles();
 improveSiteIA();
 installCampaign();
 enhanceArticleEngagement();

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
