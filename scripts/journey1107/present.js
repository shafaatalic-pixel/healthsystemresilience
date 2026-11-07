/* HSREP Present path (journey-1107). Off unless the URL has ?present (or ?present=N).
   Five stops across the site, one click each, for walking a meeting through the pitch.
   Exit turns it off for the rest of the visit. Nothing is stored beyond this tab. */
(function () {
  var STOPS = [
    { t: 'Find the gap', d: 'Michigan health centers against the 72.8% target', u: '/gap-map.html' },
    { t: 'Why it matters', d: 'Screening and the follow-up step COF-E will count', u: '/initiative.html#gap' },
    { t: 'The fix', d: 'One routine, every week: find, rank, act, close', u: '/initiative.html#how' },
    { t: 'See it work', d: 'One invented person on the list', u: '/worklist/#case-P-1407' },
    { t: 'Start with your part', d: 'Host clinic, researcher or funder', u: '/initiative.html#host' }
  ];
  var KEY = 'hsrep-present';
  var q = /[?&]present(?:=(\d+))?(?:&|$)/.exec(location.search);
  try {
    if (q) sessionStorage.setItem(KEY, String(Math.min(Math.max((+q[1] || 1) - 1, 0), STOPS.length - 1)));
  } catch (e) {}
  var cur = null; try { cur = sessionStorage.getItem(KEY); } catch (e) {}
  if (cur == null) return;
  var i = +cur || 0;
  document.documentElement.classList.add('hs-presenting');
  var css = '.hs-presenting .hs-campaign,.hs-presenting #ask-launch,.hs-presenting .askhs-fab{display:none!important}' +
    '#hsPresent{position:fixed;z-index:1250;left:50%;transform:translateX(-50%);bottom:max(14px,env(safe-area-inset-bottom,0px));display:flex;align-items:center;gap:10px;' +
    'background:#1C2E4A;color:#fff;border-radius:999px;padding:8px 8px 8px 18px;box-shadow:0 10px 30px rgba(0,0,0,.25);font:500 14px/1.3 Inter,system-ui,sans-serif;max-width:calc(100vw - 24px)}' +
    '#hsPresent .hp-n{font-family:"IBM Plex Mono",monospace;font-size:12px;color:#F7A594;white-space:nowrap}' +
    '#hsPresent .hp-t{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}' +
    '#hsPresent button{font:inherit;border:0;border-radius:999px;padding:8px 14px;cursor:pointer;white-space:nowrap}' +
    '#hsPresent .hp-b{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.35)}' +
    '#hsPresent .hp-f{background:#F26D5A;color:#fff;font-weight:600}' +
    '#hsPresent .hp-x{background:transparent;color:#C9D3E0;padding:8px 10px}' +
    '#hsPresent button:focus-visible{outline:2px solid #fff;outline-offset:2px}' +
    '@media(max-width:600px){#hsPresent{left:12px;right:12px;transform:none;border-radius:16px;display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:8px 10px;padding:10px 12px}#hsPresent .hp-n{grid-column:1;grid-row:1}#hsPresent .hp-t{grid-column:2;grid-row:1}#hsPresent .hp-x{grid-column:3;grid-row:1;padding:4px 8px}#hsPresent .hp-b{grid-column:1;grid-row:2}#hsPresent .hp-f{grid-column:2/4;grid-row:2}}' +
    '.hs-presenting #tourBox{bottom:calc(76px + env(safe-area-inset-bottom,0px))}';
  var st = document.createElement('style'); st.id = 'hsPresentCss'; st.textContent = css; document.head.appendChild(st);
  function hideBar() { var b = document.querySelector('.hs-campaign'); if (b) b.remove(); document.documentElement.classList.remove('hs-bar-on'); document.documentElement.classList.add('hs-nobar'); }
  var n = 0, iv = setInterval(function () { hideBar(); if (++n > 20) clearInterval(iv); }, 250);
  function go(k) {
    i = Math.min(Math.max(k, 0), STOPS.length - 1);
    try { sessionStorage.setItem(KEY, String(i)); } catch (e) {}
    var u = STOPS[i].u, here = location.pathname.replace(/index\.html$/, '');
    var path = u.split('#')[0], hash = u.indexOf('#') >= 0 ? u.slice(u.indexOf('#')) : '';
    if (path === here && hash) { location.hash = hash; draw(); var el = document.querySelector(hash); if (el) try { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (e) {} }
    else location.href = u;
  }
  function draw() {
    var bar = document.getElementById('hsPresent');
    if (!bar) { bar = document.createElement('nav'); bar.id = 'hsPresent'; bar.setAttribute('aria-label', 'Presentation'); document.body.appendChild(bar); }
    var s = STOPS[i];
    bar.innerHTML = '<span class="hp-n">' + (i + 1) + ' / ' + STOPS.length + '</span><span class="hp-t" title="' + s.d + '"><b>' + s.t + '</b></span>' +
      '<button type="button" class="hp-b" data-hp="back"' + (i ? '' : ' disabled') + ' aria-label="Previous stop">&larr;</button>' +
      (i < STOPS.length - 1 ? '<button type="button" class="hp-f" data-hp="next">Next: ' + STOPS[i + 1].t + ' &rarr;</button>' : '<button type="button" class="hp-f" data-hp="exit">Finish</button>') +
      '<button type="button" class="hp-x" data-hp="exit" aria-label="Stop presenting">&#10005;</button>';
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-hp]'); if (!b) return;
    var a = b.getAttribute('data-hp');
    if (a === 'next') go(i + 1); else if (a === 'back') go(i - 1);
    else { try { sessionStorage.removeItem(KEY); } catch (er) {} var bar = document.getElementById('hsPresent'); if (bar) bar.remove(); document.documentElement.classList.remove('hs-presenting'); }
  });
  function start() { draw(); if (q) { var u = STOPS[i].u, hash = u.indexOf('#') >= 0 ? u.slice(u.indexOf('#')) : ''; if (hash && u.split('#')[0] === location.pathname.replace(/index\.html$/, '') && !location.hash) { var el = document.querySelector(hash); if (el) setTimeout(function () { try { el.scrollIntoView({ block: 'start' }); } catch (e) {} }, 300); } } }
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
})();
