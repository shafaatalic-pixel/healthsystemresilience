/* In Brief audio: a short spoken version of each article's In Brief, narrated by an
   AI version of the founder's voice. One player per page, inside .inbrief.
   Markup: <div class="ib-listen" data-src="..." data-dur="0:51" data-article="slug"></div>
   Audio loads only when the reader presses play. */
(function () {
  var box = document.querySelector('.inbrief .ib-listen');
  if (!box || !box.getAttribute('data-src')) return;
  var css = document.createElement('style');
  css.textContent =
    '.ib-listen{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:-2px 0 14px}' +
    '.ib-play{display:inline-flex;align-items:center;gap:9px;height:38px;padding:0 15px 0 11px;border-radius:999px;border:1px solid #1C2E4A;background:#1C2E4A;color:#fff;font:600 13.5px/1 "Inter","Inter Fallback",sans-serif;cursor:pointer;transition:background .2s,border-color .2s}' +
    '.ib-play:hover{background:#F26D5A;border-color:#F26D5A}' +
    '.ib-play:focus-visible{outline:3px solid #F26D5A;outline-offset:2px}' +
    '.ib-play svg{width:18px;height:18px;fill:currentColor;flex:none}' +
    '.ib-play .ib-t{font-variant-numeric:tabular-nums;opacity:.8;font-weight:500}' +
    '.ib-bar{flex:1 1 160px;min-width:120px;height:6px;border-radius:99px;background:#EEF1F4;cursor:pointer;position:relative;overflow:hidden}' +
    '.ib-bar i{position:absolute;left:0;top:0;bottom:0;width:0;background:#F26D5A;border-radius:99px}' +
    '.ib-note{flex-basis:100%;font:500 11.5px/1.4 "Inter","Inter Fallback",sans-serif;letter-spacing:.02em;color:#5F6B78}' +
    '@media print{.ib-listen{display:none}}';
  document.head.appendChild(css);
  var src = box.getAttribute('data-src'), dur = box.getAttribute('data-dur') || '', slug = box.getAttribute('data-article') || '';
  var PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
  var PAUSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>';
  box.innerHTML =
    '<button type="button" class="ib-play" aria-label="Listen to the brief, ' + dur + '">' + PLAY + '<span class="ib-l">Listen to the brief</span><span class="ib-t">' + dur + '</span></button>' +
    '<div class="ib-bar" role="progressbar" aria-label="Audio progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i></i></div>' +
    '<div class="ib-note">Narrated by an AI version of the founder’s voice.</div>';
  var btn = box.querySelector('.ib-play'), lab = box.querySelector('.ib-l'), tim = box.querySelector('.ib-t'),
      bar = box.querySelector('.ib-bar'), fill = bar.querySelector('i'), a = null, started = false, done = false;
  function track(n, p) { try { if (window.hsTrack) window.hsTrack(n, p || {}); } catch (e) {} }
  function fmt(s) { s = Math.max(0, Math.round(s)); return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
  function ui() {
    var playing = a && !a.paused;
    btn.innerHTML = (playing ? PAUSE : PLAY) + '<span class="ib-l">' + (playing ? 'Pause' : (started && !done ? 'Resume' : 'Listen to the brief')) + '</span><span class="ib-t">' + tim.textContent + '</span>';
    lab = btn.querySelector('.ib-l'); tim = btn.querySelector('.ib-t');
    btn.setAttribute('aria-label', playing ? 'Pause the brief' : 'Listen to the brief, ' + dur);
  }
  function make() {
    a = new Audio(); a.preload = 'auto'; a.src = src;
    a.addEventListener('timeupdate', function () {
      if (!a.duration) return; var p = 100 * a.currentTime / a.duration;
      fill.style.width = p + '%'; bar.setAttribute('aria-valuenow', Math.round(p)); tim.textContent = fmt(a.duration - a.currentTime);
    });
    a.addEventListener('play', ui); a.addEventListener('pause', ui);
    a.addEventListener('ended', function () { done = true; fill.style.width = '100%'; tim.textContent = dur; ui(); track('brief_audio_complete', { article: slug }); started = false; done = false; ui(); });
    a.addEventListener('error', function () { box.querySelector('.ib-note').textContent = 'Audio could not load. The brief above has the same content.'; });
  }
  btn.addEventListener('click', function () {
    if (!a) make();
    if (a.paused) { var pr = a.play(); if (pr && pr.catch) pr.catch(function () {}); if (!started) { started = true; track('brief_audio_play', { article: slug }); } }
    else { a.pause(); track('brief_audio_pause', { article: slug, pct: a.duration ? Math.round(100 * a.currentTime / a.duration) : 0 }); }
  });
  bar.addEventListener('click', function (e) {
    if (!a) { make(); }
    var r = bar.getBoundingClientRect(), f = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width));
    var go = function () { a.currentTime = f * a.duration; };
    if (a.duration) go(); else a.addEventListener('loadedmetadata', go, { once: true });
  });
})();
