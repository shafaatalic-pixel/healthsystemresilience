/* media-track.js: one GA4 tracker for every audio (and video) file played on the site.
   Shared by shafaatalichoyon.com and hsraep.org (2 Nov 2026).
   Works for <audio>/<video> in the page and for `new Audio()` objects that are never attached,
   by wrapping HTMLMediaElement.prototype.play and listening (capture) for native-control plays.
   Events (sent through window.hsTrack on HSREP, window.track on the portfolio; both are consent-gated):
     media_play      {media_type, media_kind, media_file, media_label, media_duration, resume}
     media_progress  {..., percent: 25|50|75}
     media_complete  {...}
     media_pause     {..., percent}            (not sent when the clip ends)
     media_seek      {..., percent}            (at most once per 2 s)
     media_error     {...}
   media_kind comes from el.mtKind when a player sets it, else from the file path.
   media_label comes from el.mtLabel when set (case id, clip id), else the file name. */
(function () {
  if (window.__mediaTrack) return; window.__mediaTrack = 1;
  var P = window.HTMLMediaElement && HTMLMediaElement.prototype; if (!P) return;

  function send(n, p) {
    var tries = 0;
    (function go() {
      try {
        var f = window.hsTrack || window.track;
        if (f && (window.__gaOn || window.hsTrack)) { f(n, p); return; }
      } catch (e) { return; }
      if (++tries < 40) setTimeout(go, 250);
    })();
  }
  function file(el) {
    var s = el.currentSrc || el.src || '';
    try { s = new URL(s, location.href).pathname; } catch (e) {}
    return s;
  }
  function kind(el, path) {
    if (el.mtKind) return el.mtKind;
    var p = path.toLowerCase();
    if (/\/case-vo\//.test(p)) return 'case';
    if (/\/card\/audio\//.test(p)) return 'card';
    if (/\/tour-vo\//.test(p)) return 'site_tour';
    if (/\/impact-vo\//.test(p)) return 'impact_story';
    if (/--brief\.mp3$/.test(p)) return 'article_brief';
    if (/theme/.test(p)) return 'theme';
    if (/\/films?\//.test(p)) return 'film';
    if (/\/presenter\//.test(p)) return 'presenter';
    return el.tagName === 'VIDEO' ? 'video' : 'audio';
  }
  function base(el) {
    var path = file(el);
    return {
      media_type: el.tagName === 'VIDEO' ? 'video' : 'audio',
      media_kind: kind(el, path),
      media_file: path.split('/').pop().slice(0, 100),
      media_label: String(el.mtLabel || path.split('/').pop().replace(/\.[a-z0-9]+$/i, '')).slice(0, 100),
      media_duration: isFinite(el.duration) ? Math.round(el.duration) : undefined
    };
  }
  function pct(el) { return el.duration ? Math.min(100, Math.round(el.currentTime / el.duration * 100)) : 0; }
  function ext(o, k) { var r = {}; for (var a in o) if (o[a] !== undefined) r[a] = o[a]; for (var b in k) r[b] = k[b]; return r; }

  function wire(el) {
    if (el.__mt) return el.__mt;
    var st = el.__mt = { src: '', marks: {}, started: false, lastSeek: 0 };
    function reset() { var s = el.currentSrc || el.src || ''; if (s !== st.src) { st.src = s; st.marks = {}; st.started = false; } }
    function decor() { return el.muted && (el.loop || el.autoplay); } /* silent background loops are not tracked */
    el.addEventListener('play', function () {
      if (decor()) return;
      reset();
      send('media_play', ext(base(el), { resume: st.started && el.currentTime > 0.5 ? 1 : 0 }));
      st.started = true;
    });
    el.addEventListener('timeupdate', function () {
      if (!el.duration || el.paused || decor()) return;
      var p = el.currentTime / el.duration * 100;
      [25, 50, 75].forEach(function (m) {
        if (p >= m && !st.marks[m]) { st.marks[m] = 1; send('media_progress', ext(base(el), { percent: m })); }
      });
    });
    el.addEventListener('pause', function () {
      if (decor() || el.ended || (el.duration && el.currentTime >= el.duration - 0.25)) return;
      send('media_pause', ext(base(el), { percent: pct(el) }));
    });
    el.addEventListener('ended', function () {
      if (decor() || st.marks.done === st.src) return; st.marks.done = st.src;
      send('media_complete', ext(base(el), { percent: 100 }));
      st.started = false;
    });
    el.addEventListener('seeked', function () {
      var now = Date.now(); if (now - st.lastSeek < 2000 || !st.started) return; st.lastSeek = now;
      send('media_seek', ext(base(el), { percent: pct(el) }));
    });
    el.addEventListener('error', function () {
      if (!(el.currentSrc || el.src)) return;
      send('media_error', ext(base(el), { error_code: el.error ? el.error.code : 0 }));
    });
    return st;
  }

  var op = P.play;
  P.play = function () { try { wire(this); } catch (e) {} return op.apply(this, arguments); };
  /* Native controls or autoplay start playback without calling play(): catch the first play event. */
  /* Listeners added here, during the capture phase, still run when the event reaches the element. */
  document.addEventListener('play', function (e) {
    var el = e.target; if (!el || el.__mt || !el.tagName) return;
    try { wire(el); } catch (x) {}
  }, true);
})();
