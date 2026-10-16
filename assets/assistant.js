/* "Ask me about the pilot": the founder assistant on the four initiative pages
   (initiative, initiative-next, dashboard-demo, pilot-fit). The rest of the site has
   Ask HSREP (assets/ask-hsrep.js), HSREP's institutional voice.
   A slide-in panel with Shafaat's video presenter and a chat grounded in the HSREP pages.
   Calls /api/ask on this origin (the shafaat-assistant Worker, hsrep site). Nothing else.
   Opens from any element with [data-ask-open], and from the launcher it adds itself.
   See /privacy.html#ai for how questions are handled. */
(function () {
  var PM = location.pathname.match(/\/(initiative|initiative-next|dashboard-demo|pilot-fit)\.html$/);
  if (!PM) return;
  var ONINIT = PM[1] === 'initiative', HOST = ONINIT ? '#host' : '/initiative.html#host';
  var CFG = { api: '/api', ts: '0x4AAAAAAFX9JOBFpuSWsf5E', cal: 'https://calendly.com/shafaat-alic/30min', max: 8, from: PM[1] };
  var PATHS = [
    ['clinic', 'I run a clinic', [
      'What would my staff actually do each week?',
      'Who pays for what?',
      'What do you need from our IT lead?',
      'What happens at month three?',
      'Can we stop if it is not working?',
      'What do we get if it works?']],
    ['research', 'I evaluate or research', [
      'What is the evaluation protocol?',
      'Who holds the grant?',
      'What is published, and when?',
      'How is authorship decided?',
      'What is still open in the design?',
      'What does the feasibility phase measure?']],
    ['fund', 'I fund', [
      'What is the ask, in dollars and months?',
      'What is spent before month four?',
      'What are the gates?',
      'What benchmark exists?',
      'Who else is involved?',
      'What happens if it fails?']],
    ['care', 'I work in care and want to help', [
      'What is the Prevention Adoption Gap?',
      'Why colorectal screening first?',
      'What is the roundtable?',
      'Can my clinic do this later?',
      'How is this different from what we do now?',
      'Who is behind this?']],
  ];
  var CSS = '\
#ask-launch{position:fixed;right:18px;bottom:18px;z-index:4000;display:flex;align-items:center;gap:10px;padding:8px 16px 8px 8px;border:0;border-radius:999px;background:#0F2036;color:#fff;font:600 14px/1 Inter,"Inter Fallback",system-ui,sans-serif;box-shadow:0 10px 28px rgba(15,32,54,.35);cursor:pointer}\
#ask-launch img{width:38px;height:38px;border-radius:50%;object-fit:cover;object-position:50% 20%;display:block}\
#ask-launch:hover{background:#1C2E4A}\
#ask-launch:focus-visible{outline:3px solid #F26D5A;outline-offset:2px}\
html.ask-on #ask-launch{display:none}\
#ask-panel{position:fixed;top:0;right:0;bottom:0;width:min(440px,100vw);z-index:4100;background:#FBFCFD;color:#28313C;box-shadow:-12px 0 40px rgba(15,32,54,.25);display:flex;flex-direction:column;font-family:Inter,"Inter Fallback",system-ui,sans-serif;transform:translateX(102%);transition:transform .32s ease}\
html.ask-on #ask-panel{transform:none}\
#ask-panel[hidden]{display:none}\
#ask-scrim{position:fixed;inset:0;z-index:4050;background:rgba(15,32,54,.35);opacity:0;pointer-events:none;transition:opacity .3s}\
html.ask-on #ask-scrim{opacity:1;pointer-events:auto}\
.ask-head{display:flex;gap:14px;align-items:flex-end;padding:16px 16px 12px;background:#0F2036;color:#fff}\
.ask-pres{position:relative;width:92px;flex:0 0 auto}\
.ask-pres .pw{position:relative;width:92px;aspect-ratio:3/4;border-radius:12px;overflow:hidden;background:#1C2E4A;box-shadow:0 10px 24px rgba(0,0,0,.35)}\
.ask-pres video,.ask-pres img.pp{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .45s}\
.ask-pres video.on,.ask-pres img.pp.on{opacity:1}\
.ask-pres.talking .pw{box-shadow:0 10px 24px rgba(0,0,0,.35),0 0 0 3px rgba(242,109,90,.7)}\
.ask-pres .st{display:block;margin-top:6px;font:600 10.5px/1 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.12em;text-transform:uppercase;color:#AFC0D4}\
.ask-title{flex:1;min-width:0}\
.ask-title b{display:block;font-family:Spectral,Georgia,serif;font-size:20px;line-height:1.15;font-weight:600}\
.ask-title p{margin:6px 0 0;font-size:12.5px;line-height:1.45;color:#C9D4E1}\
.ask-close{position:absolute;top:10px;right:10px;width:34px;height:34px;border:0;border-radius:50%;background:rgba(255,255,255,.1);color:#fff;font-size:20px;line-height:1;cursor:pointer}\
.ask-close:hover{background:rgba(255,255,255,.2)}\
.ask-body{flex:1;overflow:auto;padding:14px 16px 8px;-webkit-overflow-scrolling:touch}\
.ask-paths{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 12px}\
.ask-paths button,.ask-sugg button{font:600 13px/1.3 Inter,"Inter Fallback",system-ui,sans-serif;text-align:left;padding:10px 12px;border:1px solid #D9E1E9;border-radius:10px;background:#fff;color:#1C2E4A;cursor:pointer}\
.ask-paths button[aria-pressed="true"]{background:#1C2E4A;color:#fff;border-color:#1C2E4A}\
.ask-sugg{display:grid;gap:6px;margin:0 0 12px}\
.ask-sugg button{font-weight:500;background:#F3F6F9}\
.ask-sugg button:hover,.ask-paths button:hover{border-color:#1C2E4A}\
.ask-msg{display:flex;gap:10px;margin:0 0 12px;align-items:flex-start}\
.ask-msg .bub{background:#F3F6F9;border:1px solid #E3E9F0;border-radius:12px;padding:10px 13px;font-size:14.5px;line-height:1.55;max-width:100%}\
.ask-msg .bub p{margin:0 0 8px}.ask-msg .bub p:last-child{margin:0}\
.ask-msg .bub ul{margin:0 0 8px;padding-left:18px}\
.ask-msg .bub a{color:#BC3A26}\
.ask-msg .bub blockquote,.ask-msg .bub q{display:block;margin:6px 0;padding:6px 10px;border-left:3px solid #F26D5A;background:#fff;font-family:Spectral,Georgia,serif;font-size:14.5px;quotes:none}\
.ask-msg.me{justify-content:flex-end}\
.ask-msg.me .bub{background:#1C2E4A;color:#fff;border-color:#1C2E4A}\
.ask-msg .av{width:30px;height:30px;border-radius:50%;object-fit:cover;object-position:50% 20%;flex:0 0 auto;margin-top:2px}\
.ask-typing i{display:inline-block;width:6px;height:6px;margin:0 2px;border-radius:50%;background:#8A97A6;animation:askB 1s infinite}\
.ask-typing i:nth-child(2){animation-delay:.15s}.ask-typing i:nth-child(3){animation-delay:.3s}\
@keyframes askB{0%,80%,100%{opacity:.3}40%{opacity:1}}\
.ask-form{display:flex;gap:8px;padding:10px 16px 6px;border-top:1px solid #D9E1E9;background:#fff}\
.ask-form textarea{flex:1;resize:none;font:15px/1.4 Inter,"Inter Fallback",system-ui,sans-serif;padding:10px 12px;border:1px solid #C9D2DC;border-radius:10px;min-height:42px;max-height:140px}\
.ask-form button{flex:0 0 auto;font:700 14px/1 Inter,"Inter Fallback",system-ui,sans-serif;padding:0 18px;border:0;border-radius:999px;background:#BC3A26;color:#fff;cursor:pointer}\
.ask-form button[disabled]{opacity:.5;cursor:default}\
.ask-meta{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:4px 16px 12px;font-size:12px;color:#5A6572;background:#fff}\
.ask-meta a{color:#5A6572}\
.ask-rest{background:#FBF4E6;border:1px solid #E9CFA0;border-radius:12px;padding:12px 14px;font-size:14px;line-height:1.5;margin:0 0 12px}\
.ask-rest a{color:#BC3A26}\
.ask-actions{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 0}\
.ask-actions a{display:inline-block;font:600 13px/1 Inter,"Inter Fallback",system-ui,sans-serif;padding:9px 13px;border-radius:999px;border:1px solid #1C2E4A;color:#1C2E4A;text-decoration:none}\
.ask-actions a.cal{background:#BC3A26;border-color:#BC3A26;color:#fff}\
#ask-ts{min-height:0}\
@media(max-width:640px){#ask-launch{right:12px;bottom:12px;padding:7px 14px 7px 7px;font-size:13px}#ask-panel{width:100vw}.ask-pres{width:70px}.ask-pres .pw{width:70px}.ask-title b{font-size:17px}.ask-paths{grid-template-columns:1fr}}\
@media(prefers-reduced-motion:reduce){#ask-panel,#ask-scrim{transition:none}}';

  var P = '/assets/presenter/';
  var CLIP = { idle: P + 'idle.mp4', greet: P + 'greet.mp4', thinking: P + 'think.mp4', talking: P + 'talk.mp4' };
  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SMALL = window.matchMedia && window.matchMedia('(max-width: 640px)').matches;

  function h(tag, attrs, html) { var e = document.createElement(tag); for (var k in attrs || {}) { if (k === 'class') e.className = attrs[k]; else e.setAttribute(k, attrs[k]); } if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function t(ev, a) { try { if (window.hsTrack) window.hsTrack(ev, a || {}); } catch (e) { } }

  /* ---------- build ---------- */
  var style = h('style', { id: 'ask-css' }, CSS); document.head.appendChild(style);
  var launch = h('button', { id: 'ask-launch', type: 'button', 'aria-haspopup': 'dialog', 'aria-controls': 'ask-panel' },
    '<img src="' + P + 'poster.jpg" alt="" width="38" height="38"><span>Ask me about the pilot</span>');
  var scrim = h('div', { id: 'ask-scrim', hidden: '' });
  var panel = h('aside', { id: 'ask-panel', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'ask-h', hidden: '' });
  panel.innerHTML =
    '<div class="ask-head"><div class="ask-pres" id="ask-pres"><div class="pw">' +
    (SMALL || RM ? '<img class="pp on" src="' + P + 'poster.jpg" alt="">' :
      '<video class="on" id="ask-v0" muted playsinline loop preload="none" poster="' + P + 'poster.jpg"></video><video id="ask-v1" muted playsinline loop preload="none"></video>') +
    '</div><span class="st" id="ask-st">Listening</span></div>' +
    '<div class="ask-title"><b id="ask-h">Ask me about the pilot</b><p>An AI version of me. It answers from what HSREP has published; on data, money and clinical matters it quotes the page and offers a conversation with the real me.</p></div>' +
    '<button type="button" class="ask-close" id="ask-close" aria-label="Close">&times;</button></div>' +
    '<div class="ask-body" id="ask-body"><div id="ask-rest"></div><div class="ask-paths" id="ask-paths" role="group" aria-label="Who are you?"></div><div class="ask-sugg" id="ask-sugg"></div><div id="ask-chat" aria-live="polite"></div></div>' +
    '<form class="ask-form" id="ask-form"><textarea id="ask-q" rows="1" maxlength="600" placeholder="Ask about the pilot" aria-label="Your question"></textarea><button type="submit" id="ask-send">Ask</button></form>' +
    '<div id="ask-ts"></div>' +
    '<div class="ask-meta"><span id="ask-left">Up to 8 questions per visit.</span><span><a href="/privacy.html#ai">How questions are handled</a></span></div>';
  document.body.appendChild(launch); document.body.appendChild(scrim); document.body.appendChild(panel);

  var chat = panel.querySelector('#ask-chat'), form = panel.querySelector('#ask-form'), q = panel.querySelector('#ask-q'), send = panel.querySelector('#ask-send'),
    rest = panel.querySelector('#ask-rest'), paths = panel.querySelector('#ask-paths'), sugg = panel.querySelector('#ask-sugg'), left = panel.querySelector('#ask-left'),
    pres = panel.querySelector('#ask-pres'), pst = panel.querySelector('#ask-st'), PV = [panel.querySelector('#ask-v0'), panel.querySelector('#ask-v1')];
  var videoOK = !!(PV[0] && PV[0].canPlayType && PV[0].canPlayType('video/mp4')), pvCur = 0, curClip = '', greetT = null;

  function clip(name) {
    if (!videoOK || curClip === name) return; curClip = name;
    var nxt = PV[1 - pvCur], prev = PV[pvCur]; nxt.src = CLIP[name]; nxt.currentTime = 0; var pr = nxt.play();
    function swap() { nxt.classList.add('on'); prev.classList.remove('on'); setTimeout(function () { try { prev.pause(); } catch (e) { } }, 500); pvCur = 1 - pvCur; }
    if (pr && pr.then) pr.then(swap).catch(function (e) { if (e && e.name === 'NotAllowedError') { videoOK = false; PV[0].classList.add('on'); } }); else swap();
  }
  function pose(n) { clearTimeout(greetT); pres.className = 'ask-pres ' + n; pst.textContent = n === 'thinking' ? 'Thinking' : n === 'talking' ? 'Answering' : n === 'greet' ? 'Hello' : 'Listening'; if (n === 'greet') { clip('greet'); greetT = setTimeout(function () { pose('idle'); }, 3600); } else clip(n); }

  /* ---------- state ---------- */
  var hist = [], turns = 0, busy = false, session = null, tsId = null, tsTok = null, tsWait = null, state = 'unknown', path = '';
  try { session = sessionStorage.getItem('hs_ask_session') || null; turns = parseInt(sessionStorage.getItem('hs_ask_turns') || '0', 10) || 0; } catch (e) { }

  function fmt(s) {
    var out = [], para = [], list = null;
    function flush() { if (para.length) { out.push('<p>' + para.join(' ') + '</p>'); para = []; } if (list) { out.push('<ul>' + list.join('') + '</ul>'); list = null; } }
    esc(s).split('\n').forEach(function (ln) {
      var l = ln.trim(); if (!l) { flush(); return; }
      var m = l.match(/^[-•*]\s+(.*)$/);
      if (m) { if (para.length) { out.push('<p>' + para.join(' ') + '</p>'); para = []; } list = list || []; list.push('<li>' + m[1] + '</li>'); return; }
      if (list) { out.push('<ul>' + list.join('') + '</ul>'); list = null; }
      // a line that is only a quotation becomes a quote block
      if (/^[“"].+[”"]$/.test(l)) { flush(); out.push('<q>' + l.replace(/^[“"]|[”"]$/g, '') + '</q>'); return; }
      para.push(l);
    });
    flush();
    return out.join('').replace(/\*\*([^*<]+)\*\*/g, '<b>$1</b>').replace(/(^|[\s(>])\*([^*<\s][^*<]*)\*(?=[\s.,;:)<]|$)/g, '$1<i>$2</i>').replace(/(https?:\/\/[^\s<)]+[^\s<).,;:])/g, function (u) {
      var same = /^https?:\/\/(www\.)?hsraep\.org/.test(u), href = same ? u.replace(/^https?:\/\/(www\.)?hsraep\.org/, '') || '/' : u;
      var label = same ? ('hsraep.org' + (href === '/' ? '' : href)) : u.replace(/^https?:\/\//, '');
      return '<a href="' + href + '"' + (same ? '' : ' rel="noopener" target="_blank"') + '>' + label + '</a>';
    });
  }
  function bot(html) { var d = h('div', { class: 'ask-msg' }, '<img class="av" src="' + P + 'poster.jpg" alt="" width="30" height="30"><div class="bub">' + html + '</div>'); chat.appendChild(d); d.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); return d; }
  function me(text) { chat.appendChild(h('div', { class: 'ask-msg me' }, '<div class="bub">' + esc(text) + '</div>')); }
  function setLeft() { var n = Math.max(0, CFG.max - turns); left.textContent = n ? (n + ' question' + (n === 1 ? '' : 's') + ' left this visit.') : 'Question limit reached for this visit.'; if (!n) { send.disabled = true; q.disabled = true; } }
  function paused(reason) {
    state = 'off';
    rest.innerHTML = '<div class="ask-rest"><b>My AI stand-in is resting' + (reason === 'daily cap' ? ' (it has answered its share for today)' : '') + '.</b> Everything it would say is on ' + (ONINIT ? 'this page' : 'the initiative page') + ': <a href="' + HOST + '">the terms for a host clinic</a>, <a href="/pilot-fit.html">the fit check</a>, and <a href="' + CFG.cal + '">a 30-minute conversation</a> with me.</div>';
    form.style.display = 'none'; paths.style.display = 'none'; sugg.style.display = 'none'; t('ask_paused', { reason: String(reason || '') });
  }
  function showPaths() {
    paths.innerHTML = '';
    PATHS.forEach(function (p) { var b = h('button', { type: 'button', 'aria-pressed': path === p[0] ? 'true' : 'false' }, esc(p[1])); b.addEventListener('click', function () { path = p[0]; showPaths(); showSugg(); t('ask_path', { path: path }); }); paths.appendChild(b); });
  }
  function showSugg() {
    sugg.innerHTML = ''; var p = PATHS.filter(function (x) { return x[0] === path; })[0]; if (!p) return;
    p[2].forEach(function (s) { var b = h('button', { type: 'button' }, esc(s)); b.addEventListener('click', function () { q.value = s; ask(); }); sugg.appendChild(b); });
  }
  function intro() {
    if (chat.querySelector('.ask-msg')) return;
    bot('<p><b>Ask me anything about the pilot.</b> What your staff would do, who pays, what the IT lead has to produce, what happens at month three. I answer from what HSREP has published on the initiative page, the roadmap, the worklist demo and the fit check. On patient data, money and clinical questions I quote the page rather than improvise, and the real conversation is 30 minutes away.</p><p>Pick who you are, or type a question.</p>');
    showPaths();
  }
  function open() {
    panel.hidden = false; scrim.hidden = false;
    requestAnimationFrame(function () { document.documentElement.classList.add('ask-on'); });
    pose('greet'); intro(); setLeft();
    if (state === 'unknown') {
      fetch(CFG.api + '/health', { credentials: 'omit' }).then(function (r) { return r.json(); })
        .then(function (j) { if (j && j.assistant === 'on') { state = 'on'; loadTs(); } else paused(j && j.reason); })
        .catch(function () { paused('network'); });
    }
    t('ask_open', {}); setTimeout(function () { q.focus(); }, 350);
  }
  function close() { document.documentElement.classList.remove('ask-on'); setTimeout(function () { panel.hidden = true; scrim.hidden = true; }, 330); try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e) { } launch.focus(); }

  /* Turnstile: loaded when the panel opens; invisible unless a visitor looks like a bot. */
  function loadTs() {
    if (!CFG.ts || session) return;
    if (window.turnstile) { renderTs(); return; }
    var s = h('script', { src: 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit', async: '', defer: '' }); s.onload = renderTs; document.head.appendChild(s);
  }
  function renderTs() { try { tsId = window.turnstile.render('#ask-ts', { sitekey: CFG.ts, appearance: 'interaction-only', callback: function (tok) { tsTok = tok; if (tsWait) { tsWait(tok); tsWait = null; } }, 'expired-callback': function () { tsTok = null; }, 'error-callback': function () { tsTok = null; if (tsWait) { tsWait(null); tsWait = null; } } }); } catch (e) { } }
  function getTs() {
    return new Promise(function (res) {
      if (!CFG.ts || !window.turnstile) { res(null); return; }
      if (tsId === null) renderTs();
      if (tsTok) { var k = tsTok; tsTok = null; res(k); return; }
      tsWait = res; if (tsId !== null) { try { window.turnstile.reset(tsId); } catch (e) { } }
      setTimeout(function () { if (tsWait) { tsWait = null; res(null); } }, 20000);
    });
  }

  function ask() {
    var text = q.value.trim(); if (!text || busy || turns >= CFG.max) return;
    busy = true; send.disabled = true; sugg.style.display = 'none'; paths.style.display = 'none'; me(text); q.value = ''; q.style.height = '';
    hist.push({ role: 'user', content: text }); pose('thinking');
    var typing = bot('<span class="ask-typing"><i></i><i></i><i></i></span>'); var t0 = Date.now(); t('ask_ask', { step: turns + 1, path: path });
    (session ? Promise.resolve(null) : getTs()).then(function (tok) {
      return fetch(CFG.api + '/ask', { method: 'POST', headers: { 'content-type': 'application/json' }, credentials: 'omit', body: JSON.stringify({ messages: hist.slice(-8), session: session, turnstile: tok, ind: path, from: CFG.from }) });
    })
      .then(function (r) { return r.json().then(function (j) { j.__s = r.status; return j; }); })
      .then(function (j) {
        typing.remove();
        if (j.paused) { pose('idle'); paused(j.reason); hist.pop(); return; }
        if (j.error) {
          pose('idle'); hist.pop();
          bot(j.needTurnstile ? 'I could not confirm you are a person (a blocker or a very old browser can cause this). Try again, or go straight to <a href="' + HOST + '">the terms for a host clinic</a>.' : (j.__s === 429 ? 'Too many questions in a short time. Give it a minute.' : 'Something went wrong on my side. Try again in a moment, or read <a href="' + HOST + '">the terms for a host clinic</a>.'));
          t('ask_error', { reason: String(j.error).slice(0, 40) }); busy = false; send.disabled = false; return;
        }
        if (j.session) { session = j.session; try { sessionStorage.setItem('hs_ask_session', session); } catch (e) { } }
        turns = j.turns || turns + 1; try { sessionStorage.setItem('hs_ask_turns', String(turns)); } catch (e) { }
        hist.push({ role: 'assistant', content: j.reply || '' });
        var html = fmt(j.reply || '');
        var acts = [];
        if (/calendly\.com/.test(j.reply || '') || j.guarded || turns >= CFG.max) acts.push('<a class="cal" href="' + CFG.cal + '" target="_blank" rel="noopener">Talk to the real me: 30 minutes</a>');
        if (/pilot-fit/.test(j.reply || '')) acts.push('<a href="/pilot-fit.html">Check your clinic’s fit</a>');
        if (/dashboard-demo/.test(j.reply || '')) acts.push('<a href="/dashboard-demo.html">Open the worklist demo</a>');
        if (acts.length) html += '<div class="ask-actions">' + acts.join('') + '</div>';
        var d = bot(html); pose('talking'); setTimeout(function () { pose('greet'); }, Math.min(9000, 1200 + (j.reply || '').length * 12));
        t('ask_reply', { seconds: Math.round((Date.now() - t0) / 1000), step: turns, guarded: j.guarded ? 1 : 0, path: path });
        busy = false; send.disabled = false; setLeft(); sugg.style.display = ''; if (turns < CFG.max) q.focus();
      })
      .catch(function () { pose('idle'); typing.remove(); hist.pop(); bot('I could not reach the assistant. Check your connection and try again, or read <a href="' + HOST + '">the terms for a host clinic</a>.'); busy = false; send.disabled = false; });
  }

  form.addEventListener('submit', function (e) { e.preventDefault(); ask(); });
  q.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); } });
  q.addEventListener('input', function () { q.style.height = 'auto'; q.style.height = Math.min(140, q.scrollHeight) + 'px'; });
  launch.addEventListener('click', open);
  /* Keep the launcher clear of the privacy-choice banner while it is on screen. */
  (function lift() {
    var c = document.getElementById('hs-consent'), r = c && c.getClientRects().length && getComputedStyle(c).visibility !== 'hidden' ? c.getBoundingClientRect() : null;
    launch.style.bottom = r && r.height ? Math.round(window.innerHeight - r.top + 12) + 'px' : '';
    setTimeout(lift, 400);
  })();
  panel.querySelector('#ask-close').addEventListener('click', close);
  scrim.addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && document.documentElement.classList.contains('ask-on')) close(); });
  document.addEventListener('click', function (e) { var a = e.target.closest && e.target.closest('[data-ask-open]'); if (a) { e.preventDefault(); open(); } });
  if (location.hash === '#ask') setTimeout(open, 400);
})();
