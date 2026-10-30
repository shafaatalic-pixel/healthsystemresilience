/* Feedback under assistant replies (shared by Ask Shafaat, Ask HSREP, Ask me about the pilot and hsrep.bd).
   Under each reply: "Was this helpful?" with a thumbs up and a thumbs down.
   Once per visit (after the first vote, or after the third reply): "What would you need to say yes?"
   Sends to /api/feedback on this origin (the shafaat-assistant Worker) with the visit's signed session,
   so only a real chat can leave feedback. Stored without names; see the site's privacy page.
   Usage: AskFB.attach(replyEl, { api: '/api', key: 'hs_ask', session: fn, turn: n, from: 'initiative', ind: fn }) */
(function () {
  if (window.AskFB) return;
  var CSS = '.afb{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:8px 0 0;font-size:12.5px;line-height:1.3}' +
    '.afb .afb-q{opacity:.75;margin-right:2px}' +
    '.afb button{font:inherit;font-size:14px;line-height:1;padding:5px 10px;border-radius:999px;border:1px solid rgba(127,127,127,.45);background:transparent;color:inherit;cursor:pointer}' +
    '.afb button:hover{border-color:currentColor}' +
    '.afb button:focus-visible{outline:2px solid currentColor;outline-offset:2px}' +
    '.afb .afb-ok{opacity:.75}' +
    '.afb-need{margin:10px 0 2px;padding:12px 13px;border:1px dashed rgba(127,127,127,.6);border-radius:12px;font-size:13.5px;line-height:1.45}' +
    '.afb-need b{display:block;font-size:14px}' +
    '.afb-need .afb-sub{display:block;opacity:.75;font-size:12.5px;margin-top:2px}' +
    '.afb-need textarea{display:block;width:100%;box-sizing:border-box;margin:8px 0;font:inherit;font-size:14px;padding:8px 10px;border-radius:8px;border:1px solid rgba(127,127,127,.5);background:transparent;color:inherit;min-height:58px;resize:vertical}' +
    '.afb-need .afb-row{display:flex;gap:8px;flex-wrap:wrap}' +
    '.afb-need button{font:inherit;font-size:13px;font-weight:600;padding:7px 14px;border-radius:999px;border:1px solid currentColor;background:transparent;color:inherit;cursor:pointer}' +
    '.afb-need button.afb-send{border-color:transparent;background:#BC3A26;color:#fff}' +
    '.afb-need button[disabled]{opacity:.5;cursor:default}';
  var st = document.createElement('style'); st.id = 'afb-css'; st.textContent = CSS; document.head.appendChild(st);

  function get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { } }
  function track(o, ev, a) { try { if (o.track) o.track(ev, a || {}); } catch (e) { } }
  function post(o, body) {
    var s = o.session && o.session(); if (!s) return Promise.resolve(false);
    body.session = s; body.from = o.from || ''; body.ind = (o.ind && o.ind()) || ''; body.turn = o.turn || 0;
    return fetch((o.api || '/api') + '/feedback', { method: 'POST', headers: { 'content-type': 'application/json' }, credentials: 'omit', keepalive: true, body: JSON.stringify(body) })
      .then(function (r) { return r.ok; }).catch(function () { return false; });
  }

  function need(o, host) {
    var k = (o.key || 'ask') + '_need'; if (get(k)) return; set(k, '1');
    var box = document.createElement('div'); box.className = 'afb-need';
    box.innerHTML = '<b>' + (o.needQ || 'What would you need to say yes?') + '</b><span class="afb-sub">One line is plenty. Optional, and stored without your name.</span>' +
      '<textarea maxlength="500" rows="2" aria-label="' + (o.needQ || 'What would you need to say yes?') + '"></textarea>' +
      '<div class="afb-row"><button type="button" class="afb-send">Send</button><button type="button" class="afb-skip">Not now</button></div>';
    host.appendChild(box);
    var ta = box.querySelector('textarea'), sendB = box.querySelector('.afb-send');
    box.querySelector('.afb-skip').addEventListener('click', function () { box.remove(); track(o, 'ask_need_skip', { turn: o.turn }); });
    sendB.addEventListener('click', function () {
      var v = ta.value.trim(); if (!v) { ta.focus(); return; }
      sendB.disabled = true;
      post(o, { need: v }).then(function () { box.innerHTML = '<span>Thank you. Noted, and read.</span>'; track(o, 'ask_need', { turn: o.turn, chars: v.length }); });
    });
    try { box.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); } catch (e) { }
  }

  window.AskFB = {
    attach: function (el, o) {
      if (!el || !o) return;
      var row = document.createElement('div'); row.className = 'afb';
      row.innerHTML = '<span class="afb-q">Was this helpful?</span><button type="button" data-v="up" aria-label="Yes, helpful">👍</button><button type="button" data-v="down" aria-label="No, not helpful">👎</button>';
      el.appendChild(row);
      Array.prototype.forEach.call(row.querySelectorAll('button'), function (b) {
        b.addEventListener('click', function () {
          var v = b.getAttribute('data-v');
          row.innerHTML = '<span class="afb-ok">' + (v === 'up' ? 'Thanks for the 👍' : 'Thanks. That helps fix it.') + '</span>';
          post(o, { vote: v }); track(o, 'ask_vote', { vote: v, turn: o.turn });
          need(o, el);
        });
      });
      if ((o.turn || 0) >= 3) need(o, el);
    }
  };
})();
