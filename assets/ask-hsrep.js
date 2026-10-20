/* "Ask HSREP": HSREP's institutional assistant. No video, not a person, not the author.
   Two ways in:
   1. On each article, an inline block after "Common questions" (#ask-hsrep in the markup,
      hidden until this script runs, so readers without JavaScript never see a dead box).
   2. On every other page, the "Ask HSREP" button in the header ([data-askhs-open]) opens a
      side panel that knows which page the visitor is on. On an article, the header button
      scrolls to the inline block instead.
   The four initiative pages keep the founder assistant (assets/assistant.js) and are skipped.
   Calls /api/ask on this origin (the shafaat-assistant Worker, hsrep site) with from=<page>;
   the Worker answers from HSREP's core pages plus that page only. See /privacy.html#ai. */
(function () {
  if (/\/(initiative|initiative-next|dashboard-demo|pilot-fit)\.html$/.test(location.pathname)) return;
  var PAGES = {
    home: ['Home', ['What is HSREP, in one paragraph?', 'Why call a health system economic protection?', 'Where should a public-health professional start?']],
    'season-1': ['Season 1', ['What was Season 1’s central question?', 'How is 57,274 counted?', 'What did Season 1 lead to?']],
    articles: ['The article library', ['Which article should I read first?', 'Which articles are about Bangladesh, and which about Michigan?', 'Which articles carry corrections?']],
    impact: ['Impact', ['What do the drop-off lines mean?', 'Why are there no responses yet?', 'Why is 57,274 not on this page?']],
    methodology: ['Methodology', ['How is 57,274 counted?', 'Why don’t the chapter totals add up exactly?', 'What does reconciled at better than 94% mean?']],
    roundtable: ['Roundtables', ['Which question should I answer?', 'Will my name be published?', 'Who reads the responses before they go up?']],
    about: ['About', ['Who runs HSREP, and is it independent?', 'How does HSREP handle corrections?', 'How can my organisation work with HSREP?']],
    corrections: ['Corrections log', ['Why are some articles not edited in place?', 'Which corrections changed a figure?', 'How do I report a figure that does not hold?']],
    search: ['Search', ['What has HSREP published on prevention?', 'Which pieces cover Bangladesh?', 'Where is the Season 1 data?']],
    films: ['Films and explainers', ['What are the films about?', 'Do the films have transcripts?', 'Can I share a film?']],
    media: ['Media and brand kit', ['Can I republish an HSREP article?', 'How should I describe HSREP in a story?', 'What do the colours of the mark mean?']],
    identity: ['Identity', ['What does the Humanist Crest stand for?', 'Why three figures at the centre?', 'Where can I download the mark?']],
    accessibility: ['Accessibility', ['How accessible are the downloads?', 'Do the films have captions?', 'How do I report an accessibility problem?']],
    privacy: ['Privacy', ['What does the assistant keep?', 'Does HSREP use cookies?', 'How do I ask for my data to be deleted?']],
    terms: ['Terms of use', ['Can I reuse HSREP content?', 'Which articles are CC BY 4.0?', 'How should I cite HSREP?']],
    '404': ['This page', ['What is HSREP?', 'Where are the Season 1 articles?', 'How do I find a specific topic?']],
  };
  var path = location.pathname.replace(/\/+$/, '/');
  var key = path === '/' || /\/index\.html$/.test(path) ? 'home' : ((path.match(/^\/([a-z0-9-]+)\.html$/) || [])[1] || '');
  if (!PAGES[key] && !document.getElementById('ask-hsrep')) key = '404';

  var box = document.getElementById('ask-hsrep'), panel = !box, wrap = null, scrim = null, opener = null;
  var CFG = { api: '/api', ts: '0x4AAAAAAFX9JOBFpuSWsf5E', max: panel ? 8 : 6, from: box ? (box.getAttribute('data-from') || '') : key };
  if (!/^[a-z0-9-]{3,60}$/.test(CFG.from)) return;

  var CSS = '\
.askhs{font-family:var(--sans,Inter,"Inter Fallback",system-ui,sans-serif);margin:26px 0 26px;background:#fff;border:1px solid var(--line,#DCE3EA);border-radius:16px;padding:26px 28px 20px}\
.askhs .ak{font-family:"IBM Plex Mono","IBM Plex Mono Fallback",monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#1C2E4A;margin-bottom:8px;display:flex;align-items:center;gap:8px}\
.askhs .ak::before{content:"\\2726";font-size:13px;letter-spacing:0;color:#F26D5A}\
.askhs h2{font-family:Spectral,"Spectral Fallback",Georgia,serif;font-weight:700;font-size:1.42rem;line-height:1.24;margin:0 0 8px;color:#1C2E4A}\
.askhs .asub{margin:0 0 16px;font-size:.92rem;line-height:1.6;color:#5A5F66;max-width:62ch}\
.askhs .aqs{display:grid;gap:8px;margin:0 0 14px}\
.askhs .aqs button{font-family:inherit;font-weight:500;font-size:.95rem;line-height:1.4;text-align:left;padding:11px 14px;border:1px solid #DCE3EA;border-radius:10px;background:#F4F7FA;color:#1C2E4A;cursor:pointer;transition:border-color .15s,background .15s}\
.askhs .aqs button:hover{border-color:#1C2E4A;background:#fff}\
.askhs .aqs button::after{content:" \\2192";color:#C43C25}\
.askhs .achat{display:grid;gap:10px}\
.askhs .am{font-size:.95rem;line-height:1.6;border-radius:12px;padding:12px 15px}\
.askhs .am.me{justify-self:end;max-width:85%;background:#1C2E4A;color:#fff}\
.askhs .am.bot{background:#F4F7FA;border:1px solid #E3E9F0;color:#28313C}\
.askhs .am p{margin:0 0 8px}.askhs .am p:last-child{margin:0}\
.askhs .am ul{margin:0 0 8px;padding-left:18px}\
.askhs .am a{color:#C43C25;word-break:break-word}\
.askhs .am q{display:block;margin:6px 0;padding:6px 10px;border-left:3px solid #1C2E4A;background:#fff;font-family:Spectral,Georgia,serif;quotes:none}\
.askhs .am .gn{display:block;margin-top:8px;font-size:.8rem;color:#5A5F66}\
.askhs .atyping i{display:inline-block;width:6px;height:6px;margin:0 2px;border-radius:50%;background:#8A97A6;animation:askhsB 1s infinite}\
.askhs .atyping i:nth-child(2){animation-delay:.15s}.askhs .atyping i:nth-child(3){animation-delay:.3s}\
@keyframes askhsB{0%,80%,100%{opacity:.3}40%{opacity:1}}\
.askhs form{display:flex;gap:0;margin:16px 0 0;padding:2px;border-radius:16px;background:linear-gradient(100deg,#F26D5A,#F5B26B 40%,#1C2E4A);box-shadow:0 8px 22px rgba(242,109,90,.18);transition:box-shadow .2s}\
.askhs form:focus-within{box-shadow:0 0 0 4px rgba(242,109,90,.18),0 10px 26px rgba(242,109,90,.25)}\
.askhs textarea{flex:1;resize:none;font-family:inherit;font-size:15.5px;line-height:1.4;padding:13px 14px;border:0;border-radius:14px 0 0 14px;min-height:48px;max-height:140px;background:#fff;color:#28313C;outline:none}\
.askhs form button{flex:0 0 auto;display:flex;align-items:center;gap:6px;font-family:inherit;font-weight:700;font-size:14px;line-height:1;padding:0 18px;border:0;border-radius:0 14px 14px 0;background:#1C2E4A;color:#fff;cursor:pointer}\
.askhs form button::after{content:"\\2192";font-size:16px}\
.askhs form button[disabled]{opacity:.5;cursor:default}\
.askhs .ameta{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:#5A5F66}\
.askhs .ameta a{color:#5A5F66}\
.askhs .arest{background:#FBF4E6;border:1px solid #E9CFA0;border-radius:12px;padding:12px 14px;font-size:.92rem;line-height:1.55}\
.askhs .arest a{color:#C43C25}\
[data-theme="dark"] .askhs{background:#14213A;border-color:#2A3B57}\
[data-theme="dark"] .askhs .ak,[data-theme="dark"] .askhs h2{color:#EAF1F9}\
[data-theme="dark"] .askhs .asub,[data-theme="dark"] .askhs .ameta,[data-theme="dark"] .askhs .ameta a,[data-theme="dark"] .askhs .am .gn{color:#AEBCCE}\
[data-theme="dark"] .askhs .aqs button{background:#1a2942;border-color:#2A3B57;color:#EAF1F9}\
[data-theme="dark"] .askhs .aqs button:hover{border-color:#F26D5A}\
[data-theme="dark"] .askhs .am.bot{background:#1a2942;border-color:#2A3B57;color:#D4DEEA}\
[data-theme="dark"] .askhs .am.me{background:#F26D5A;color:#0A121E}\
[data-theme="dark"] .askhs .am a{color:#F26D5A}\
[data-theme="dark"] .askhs .am q{background:#14213A;border-left-color:#F26D5A}\
[data-theme="dark"] .askhs textarea{background:#0F1A2B;color:#EAF1F9}\
[data-theme="dark"] .askhs form button{background:#1C2E4A;color:#fff}\
[data-theme="dark"] .askhs .arest{background:#2a2418;border-color:#6a5530;color:#EAF1F9}\
@media(max-width:600px){.askhs{padding:22px 18px 16px}.askhs h2{font-size:1.25rem}}\
#askhs-panel{position:fixed;top:0;right:0;bottom:0;width:min(460px,100vw);z-index:4100;display:flex;flex-direction:column;background:#FBFCFD;box-shadow:-12px 0 40px rgba(15,32,54,.25);transform:translateX(102%);transition:transform .3s ease}\
html.askhs-on #askhs-panel{transform:none}\
#askhs-panel[hidden],#askhs-scrim[hidden]{display:none}\
#askhs-scrim{position:fixed;inset:0;z-index:4050;background:rgba(15,32,54,.35);opacity:0;transition:opacity .3s}\
html.askhs-on #askhs-scrim{opacity:1}\
/* First visit: keep the privacy-choice banner (#hs-consent) clear of the open panel. Wide screens: whole and usable left of the panel; narrow: hidden until it closes. */\
@media(min-width:900px){html.askhs-on #hs-consent{z-index:4060;left:16px;right:calc(min(460px,100vw) + 16px);max-width:560px}}\
@media(max-width:899.98px){html.askhs-on #hs-consent{visibility:hidden}}\
#askhs-panel .askhs{margin:0;border:0;border-radius:0;padding:0;display:flex;flex-direction:column;flex:1;min-height:0;background:transparent}\
#askhs-panel .ap-head{position:relative;background:radial-gradient(120% 140% at 100% 0%,rgba(242,109,90,.35),transparent 55%),#0F2036;color:#fff;padding:18px 56px 16px 20px}\
#askhs-panel .ap-head .ak{color:#AFC0D4;margin-bottom:6px}\
#askhs-panel .ap-head .ak::before{color:#F5B26B}\
#askhs-panel .ap-head h2{color:#fff;font-size:1.3rem;margin:0 0 6px}\
#askhs-panel .ap-head .asub{color:#C9D4E1;font-size:.84rem;margin:0}\
#askhs-panel .ap-close{position:absolute;top:12px;right:12px;width:36px;height:36px;border:0;border-radius:50%;background:rgba(255,255,255,.12);color:#fff;font-size:22px;line-height:1;cursor:pointer}\
#askhs-panel .ap-close:hover{background:rgba(255,255,255,.22)}\
#askhs-panel .ap-body{flex:1;overflow:auto;padding:16px 20px 8px;-webkit-overflow-scrolling:touch}\
#askhs-panel .ap-foot{padding:0 20px 14px;background:linear-gradient(180deg,#fff,#FBF6F4);box-shadow:0 -10px 24px rgba(15,32,54,.06)}\
#askhs-panel .ap-foot form{margin-top:14px}\
[data-theme="dark"] #askhs-panel{background:#0F1A2B}\
[data-theme="dark"] #askhs-panel .ap-foot{background:#14213A}\
.hs-ask[aria-expanded="true"]{color:#C43C25;border-color:#C43C25}\
@media(prefers-reduced-motion:reduce){#askhs-panel,#askhs-scrim{transition:none}}';

  function h(tag, attrs, html) { var e = document.createElement(tag); for (var k in attrs || {}) { if (k === 'class') e.className = attrs[k]; else e.setAttribute(k, attrs[k]); } if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function t(ev, a) { try { a = a || {}; a.from = CFG.from; if (window.hsTrack) window.hsTrack(ev, a); } catch (e) { } }

  document.head.appendChild(h('style', { id: 'askhs-css' }, CSS));
  function esc0(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  if (panel) {
    var pg = PAGES[key];
    scrim = h('div', { id: 'askhs-scrim', hidden: '' });
    wrap = h('aside', { id: 'askhs-panel', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'askhs-h', hidden: '' });
    wrap.innerHTML = '<section class="askhs"><div class="ap-head"><div class="ak">Ask HSREP</div><h2 id="askhs-h">Questions about ' + (key === 'home' ? 'HSREP' : 'this page') + '?</h2>' +
      '<p class="asub">You are on: ' + esc0(pg[0]) + '. An AI assistant answers from HSREP’s published record. It gives each figure with its source, and the corrected fact where a correction is on record. It is not a person.</p>' +
      '<button type="button" class="ap-close" aria-label="Close">&times;</button></div>' +
      '<div class="ap-body"><div class="aqs">' + pg[1].map(function (x) { return '<button type="button">' + esc0(x) + '</button>'; }).join('') + '</div><div class="achat" aria-live="polite"></div></div>' +
      '<div class="ap-foot"><form><textarea rows="1" maxlength="600" placeholder="Ask about HSREP or this page" aria-label="Your question"></textarea><button type="submit">Ask</button></form>' +
      '<div class="ats"></div><div class="ameta"><span class="aleft">Up to 8 questions per visit.</span><span>Do not type personal health details. <a href="/privacy.html#ai">How questions are handled</a></span></div></div></section>';
    document.body.appendChild(scrim); document.body.appendChild(wrap);
    box = wrap.querySelector('.askhs');
  }
  var qs = box.querySelector('.aqs'), chat = box.querySelector('.achat'), form = box.querySelector('form'), q = box.querySelector('textarea'),
    send = form.querySelector('button'), left = box.querySelector('.aleft');
  if (!panel) box.hidden = false;

  var hist = [], turns = 0, busy = false, session = null, tsId = null, tsTok = null, tsWait = null, state = 'unknown';
  try { session = sessionStorage.getItem('hs_askhs_session') || null; turns = parseInt(sessionStorage.getItem('hs_askhs_turns') || '0', 10) || 0; } catch (e) { }

  function fmt(s) {
    var out = [], para = [], list = null;
    function flush() { if (para.length) { out.push('<p>' + para.join(' ') + '</p>'); para = []; } if (list) { out.push('<ul>' + list.join('') + '</ul>'); list = null; } }
    esc(s).split('\n').forEach(function (ln) {
      var l = ln.trim(); if (!l) { flush(); return; }
      var m = l.match(/^[-•*]\s+(.*)$/);
      if (m) { if (para.length) { out.push('<p>' + para.join(' ') + '</p>'); para = []; } list = list || []; list.push('<li>' + m[1] + '</li>'); return; }
      if (list) { out.push('<ul>' + list.join('') + '</ul>'); list = null; }
      if (/^[“"].+[”"]$/.test(l)) { flush(); out.push('<q>' + l.replace(/^[“"]|[”"]$/g, '') + '</q>'); return; }
      para.push(l);
    });
    flush();
    return out.join('').replace(/\*\*([^*<]+)\*\*/g, '<b>$1</b>').replace(/(^|[\s(>])\*([^*<\s][^*<]*)\*(?=[\s.,;:)<]|$)/g, '$1<i>$2</i>').replace(/(https?:\/\/[^\s<)]+[^\s<).,;:])|\b([a-z0-9._-]+@hsraep\.org)\b/g, function (u, url, mail) {
      if (mail) return '<a href="mailto:' + mail + '">' + mail + '</a>';
      var same = /^https?:\/\/(www\.)?hsraep\.org/.test(url), href = same ? url.replace(/^https?:\/\/(www\.)?hsraep\.org/, '') || '/' : url;
      var label = same ? ('hsraep.org' + (href === '/' ? '' : href)) : url.replace(/^https?:\/\//, '');
      return '<a href="' + href + '"' + (same ? '' : ' rel="noopener" target="_blank"') + '>' + label + '</a>';
    });
  }
  function down() { if (panel) { var b = wrap.querySelector('.ap-body'); b.scrollTop = b.scrollHeight; } }
  function bot(html) { var d = h('div', { class: 'am bot' }, html); chat.appendChild(d); down(); return d; }
  function me(text) { chat.appendChild(h('div', { class: 'am me' }, esc(text))); down(); }
  function setLeft() { var n = Math.max(0, CFG.max - turns); if (left) left.textContent = n ? (n + ' question' + (n === 1 ? '' : 's') + ' left this visit.') : 'Question limit reached for this visit.'; if (!n) { send.disabled = true; q.disabled = true; } }
  function paused(reason) {
    state = 'off';
    qs.style.display = 'none'; form.style.display = 'none';
    chat.appendChild(h('div', { class: 'arest' }, '<b>Ask HSREP is resting' + (reason === 'daily cap' ? ' (it has answered its share for today)' : '') + '.</b> ' + (panel ? '<a href="/search.html">Search</a> covers every page, and the <a href="/corrections.html">corrections log</a> and the <a href="/methodology.html">methodology</a> hold the figures. To take part, see <a href="/roundtable.html">the roundtable</a>.' : 'The common questions above, the <a href="/corrections.html">corrections log</a> and the <a href="/methodology.html">methodology</a> cover most of what it would say. To respond to the argument, use <a href="#engage">Respond as a professional</a>.')));
    t('askhs_paused', { reason: String(reason || '') });
  }

  /* Health and Turnstile load on first interaction, not on page load. */
  var ready = null;
  function wake() {
    if (ready) return ready;
    ready = fetch(CFG.api + '/health', { credentials: 'omit' }).then(function (r) { return r.json(); })
      .then(function (j) { if (j && j.assistant === 'on') { state = 'on'; loadTs(); return true; } paused(j && j.reason); return false; })
      .catch(function () { paused('network'); return false; });
    return ready;
  }
  function loadTs() {
    if (!CFG.ts || session) return;
    if (window.turnstile) { renderTs(); return; }
    var s = h('script', { src: 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit', async: '', defer: '' }); s.onload = renderTs; document.head.appendChild(s);
  }
  function renderTs() { try { if (tsId !== null) return; tsId = window.turnstile.render(box.querySelector('.ats'), { sitekey: CFG.ts, appearance: 'interaction-only', callback: function (tok) { tsTok = tok; if (tsWait) { tsWait(tok); tsWait = null; } }, 'expired-callback': function () { tsTok = null; }, 'error-callback': function () { tsTok = null; if (tsWait) { tsWait(null); tsWait = null; } } }); } catch (e) { } }
  function getTs() {
    return new Promise(function (res) {
      if (!CFG.ts) { res(null); return; }
      var waited = 0;
      (function poll() {
        if (!window.turnstile) { if ((waited += 200) > 8000) { res(null); return; } setTimeout(poll, 200); return; }
        if (tsId === null) renderTs();
        if (tsTok) { var k = tsTok; tsTok = null; res(k); return; }
        tsWait = res;
        setTimeout(function () { if (tsWait) { tsWait = null; res(null); } }, 20000);
      })();
    });
  }

  /* A stored session can outlive the server's one-hour token (sessionStorage keeps it for the
     life of the tab). Drop it when it is near expiry, and if the server still asks for the
     person check, get a fresh Turnstile token and retry once. */
  function dropSession() { session = null; try { sessionStorage.removeItem('hs_askhs_session'); } catch (e) { } }
  function freshSession() { if (session) { var e = parseInt(String(session).split('.')[1], 10); if (!e || e * 1000 < Date.now() + 60000) dropSession(); } }
  function req(retry) {
    freshSession(); if (!session) loadTs();
    return (session ? Promise.resolve(null) : getTs()).then(function (tok) {
      return fetch(CFG.api + '/ask', { method: 'POST', headers: { 'content-type': 'application/json' }, credentials: 'omit', body: JSON.stringify({ messages: hist.slice(-8), session: session, turnstile: tok, ind: '', from: CFG.from }) });
    }).then(function (r) { return r.json().then(function (j) { j.__s = r.status; return j; }); })
      .then(function (j) { if (j && j.needTurnstile && !retry) { dropSession(); return req(true); } return j; });
  }

  function ask(text) {
    text = String(text || '').trim(); if (!text || busy || turns >= CFG.max || state === 'off') return;
    busy = true; send.disabled = true; me(text); q.value = ''; q.style.height = '';
    hist.push({ role: 'user', content: text });
    var typing = bot('<span class="atyping" aria-label="Answering"><i></i><i></i><i></i></span>'); var t0 = Date.now(); t('askhs_ask', { step: turns + 1 });
    wake().then(function (ok) {
      if (!ok) { typing.remove(); hist.pop(); busy = false; return null; }
      return req(false).then(function (j) {
        typing.remove();
        if (j.paused) { hist.pop(); paused(j.reason); return; }
        if (j.error) {
          hist.pop();
          bot(j.needTurnstile ? 'The check that you are a person did not complete (a blocker or a very old browser can cause this). Try again in a moment.' : (j.__s === 429 ? 'Too many questions in a short time. Give it a minute.' : 'Something went wrong on HSREP’s side. Try again in a moment.'));
          t('askhs_error', { reason: String(j.error).slice(0, 40) }); busy = false; send.disabled = false; return;
        }
        if (j.session) { session = j.session; try { sessionStorage.setItem('hs_askhs_session', session); } catch (e) { } }
        turns = Math.min(CFG.max, turns + 1); try { sessionStorage.setItem('hs_askhs_turns', String(turns)); } catch (e) { }
        hist.push({ role: 'assistant', content: j.reply || '' });
        var html = fmt(j.reply || '');
        bot(html);
        t('askhs_reply', { seconds: Math.round((Date.now() - t0) / 1000), step: turns, guarded: j.guarded ? 1 : 0 });
        busy = false; send.disabled = false; setLeft();
      });
    }).catch(function () { typing.remove(); hist.pop(); bot('Ask HSREP could not be reached. Check your connection and try again.'); busy = false; send.disabled = false; });
  }

  Array.prototype.forEach.call(qs.querySelectorAll('button'), function (b) {
    b.addEventListener('click', function () { b.remove(); if (!qs.querySelector('button')) qs.style.display = 'none'; ask(b.textContent); });
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); ask(q.value); });
  q.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(q.value); } });
  q.addEventListener('input', function () { q.style.height = 'auto'; q.style.height = Math.min(140, q.scrollHeight) + 'px'; });
  q.addEventListener('focus', function () { wake(); }, { once: true });
  qs.addEventListener('pointerenter', function () { wake(); }, { once: true });
  setLeft();

  /* Header button(s). */
  function open(btn) {
    opener = btn || null;
    if (!panel) { box.scrollIntoView({ behavior: 'smooth', block: 'center' }); setTimeout(function () { try { q.focus({ preventScroll: true }); } catch (e) { q.focus(); } }, 450); wake(); t('askhs_header', { mode: 'inline' }); return; }
    wrap.hidden = false; scrim.hidden = false;
    requestAnimationFrame(function () { document.documentElement.classList.add('askhs-on'); });
    setBtns(true); wake(); t('askhs_open', {});
    setTimeout(function () { q.focus(); }, 320);
  }
  function close() {
    if (!panel) return;
    document.documentElement.classList.remove('askhs-on'); setBtns(false);
    setTimeout(function () { wrap.hidden = true; scrim.hidden = true; }, 320);
    if (opener) try { opener.focus(); } catch (e) { }
  }
  function setBtns(on) { Array.prototype.forEach.call(document.querySelectorAll('[data-askhs-open]'), function (b) { b.setAttribute('aria-expanded', on ? 'true' : 'false'); }); }
  document.addEventListener('click', function (e) { var b = e.target.closest && e.target.closest('[data-askhs-open]'); if (b) { e.preventDefault(); if (panel && document.documentElement.classList.contains('askhs-on')) close(); else open(b); } });
  if (panel) {
    wrap.querySelector('.ap-close').addEventListener('click', close);
    scrim.addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && document.documentElement.classList.contains('askhs-on')) close(); });
    if (location.hash === '#ask') setTimeout(open, 400);
  }
})();
