/* "Ask HSREP": questions about the argument, at the end of each article.
   An inline block, not a floating bubble. HSREP's institutional voice, no video. It answers
   from the article being read and HSREP's published record (core pages), quotes figures with
   their sources and gives the corrected fact where a correction is on record.
   Calls /api/ask on this origin (the shafaat-assistant Worker, hsrep site) with from=<slug>.
   The markup is in the article (#ask-hsrep, hidden until this script runs, so readers without
   JavaScript never see a dead box). See /privacy.html#ai for how questions are handled. */
(function () {
  var box = document.getElementById('ask-hsrep');
  if (!box) return;
  var CFG = { api: '/api', ts: '0x4AAAAAAFX9JOBFpuSWsf5E', max: 6, from: box.getAttribute('data-from') || '' };
  if (!/^[a-z0-9-]{3,60}$/.test(CFG.from)) return;

  var CSS = '\
.askhs{font-family:var(--sans,Inter,"Inter Fallback",system-ui,sans-serif);margin:26px 0 26px;background:#fff;border:1px solid var(--line,#DCE3EA);border-radius:16px;padding:26px 28px 20px}\
.askhs .ak{font-family:"IBM Plex Mono","IBM Plex Mono Fallback",monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#1C2E4A;margin-bottom:8px;display:flex;align-items:center;gap:8px}\
.askhs .ak::before{content:"";width:8px;height:8px;border-radius:2px;background:#1C2E4A}\
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
.askhs form{display:flex;gap:8px;margin:14px 0 0}\
.askhs textarea{flex:1;resize:none;font-family:inherit;font-size:15px;line-height:1.4;padding:10px 12px;border:1px solid #C9D2DC;border-radius:10px;min-height:44px;max-height:140px;background:#fff;color:#28313C}\
.askhs form button{flex:0 0 auto;font-family:inherit;font-weight:700;font-size:14px;line-height:1;padding:0 20px;border:0;border-radius:999px;background:#1C2E4A;color:#fff;cursor:pointer}\
.askhs form button[disabled]{opacity:.5;cursor:default}\
.askhs .ameta{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:#5A5F66}\
.askhs .ameta a{color:#5A5F66}\
.askhs .arest{background:#FBF4E6;border:1px solid #E9CFA0;border-radius:12px;padding:12px 14px;font-size:.92rem;line-height:1.55}\
.askhs .arest a{color:#C43C25}\
[data-theme="dark"] .askhs{background:#14213A;border-color:#2A3B57}\
[data-theme="dark"] .askhs .ak,[data-theme="dark"] .askhs h2{color:#EAF1F9}\
[data-theme="dark"] .askhs .ak::before{background:#F26D5A}\
[data-theme="dark"] .askhs .asub,[data-theme="dark"] .askhs .ameta,[data-theme="dark"] .askhs .ameta a,[data-theme="dark"] .askhs .am .gn{color:#AEBCCE}\
[data-theme="dark"] .askhs .aqs button{background:#1a2942;border-color:#2A3B57;color:#EAF1F9}\
[data-theme="dark"] .askhs .aqs button:hover{border-color:#F26D5A}\
[data-theme="dark"] .askhs .am.bot{background:#1a2942;border-color:#2A3B57;color:#D4DEEA}\
[data-theme="dark"] .askhs .am.me{background:#F26D5A;color:#0A121E}\
[data-theme="dark"] .askhs .am a{color:#F26D5A}\
[data-theme="dark"] .askhs .am q{background:#14213A;border-left-color:#F26D5A}\
[data-theme="dark"] .askhs textarea{background:#0F1A2B;border-color:#2A3B57;color:#EAF1F9}\
[data-theme="dark"] .askhs form button{background:#F26D5A;color:#0A121E}\
[data-theme="dark"] .askhs .arest{background:#2a2418;border-color:#6a5530;color:#EAF1F9}\
@media(max-width:600px){.askhs{padding:22px 18px 16px}.askhs h2{font-size:1.25rem}}';

  function h(tag, attrs, html) { var e = document.createElement(tag); for (var k in attrs || {}) { if (k === 'class') e.className = attrs[k]; else e.setAttribute(k, attrs[k]); } if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function t(ev, a) { try { a = a || {}; a.from = CFG.from; if (window.hsTrack) window.hsTrack(ev, a); } catch (e) { } }

  document.head.appendChild(h('style', { id: 'askhs-css' }, CSS));
  var qs = box.querySelector('.aqs'), chat = box.querySelector('.achat'), form = box.querySelector('form'), q = box.querySelector('textarea'),
    send = form.querySelector('button'), left = box.querySelector('.aleft');
  box.hidden = false;

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
  function bot(html) { var d = h('div', { class: 'am bot' }, html); chat.appendChild(d); return d; }
  function me(text) { chat.appendChild(h('div', { class: 'am me' }, esc(text))); }
  function setLeft() { var n = Math.max(0, CFG.max - turns); if (left) left.textContent = n ? (n + ' question' + (n === 1 ? '' : 's') + ' left this visit.') : 'Question limit reached for this visit.'; if (!n) { send.disabled = true; q.disabled = true; } }
  function paused(reason) {
    state = 'off';
    qs.style.display = 'none'; form.style.display = 'none';
    chat.appendChild(h('div', { class: 'arest' }, '<b>Ask HSREP is resting' + (reason === 'daily cap' ? ' (it has answered its share for today)' : '') + '.</b> The common questions above, the <a href="/corrections.html">corrections log</a> and the <a href="/methodology.html">methodology</a> cover most of what it would say. To respond to the argument, use <a href="#engage">Respond as a professional</a>.'));
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

  function ask(text) {
    text = String(text || '').trim(); if (!text || busy || turns >= CFG.max || state === 'off') return;
    busy = true; send.disabled = true; me(text); q.value = ''; q.style.height = '';
    hist.push({ role: 'user', content: text });
    var typing = bot('<span class="atyping" aria-label="Answering"><i></i><i></i><i></i></span>'); var t0 = Date.now(); t('askhs_ask', { step: turns + 1 });
    wake().then(function (ok) {
      if (!ok) { typing.remove(); hist.pop(); busy = false; return null; }
      return (session ? Promise.resolve(null) : getTs()).then(function (tok) {
        return fetch(CFG.api + '/ask', { method: 'POST', headers: { 'content-type': 'application/json' }, credentials: 'omit', body: JSON.stringify({ messages: hist.slice(-8), session: session, turnstile: tok, ind: '', from: CFG.from }) });
      }).then(function (r) { return r.json().then(function (j) { j.__s = r.status; return j; }); }).then(function (j) {
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
})();
