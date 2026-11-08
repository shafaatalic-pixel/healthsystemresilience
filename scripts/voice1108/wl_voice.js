
// ---- voice-1108: "Hear how it works", the demo narrated in an AI version of the founder's voice ----
// A seventh tour. Each step plays one clip from /assets/worklist-vo/ and moves on when it ends.
// Started from a card or button it plays at once; opened from a link (#tour-voice) it waits for one tap.
// Silent and manual like the other tours when the voice is off. Nothing about the list changes.
const VOICE_VER = '20261108a';
TOURS.push({ id:'voice', t:'Hear how it works', d:'Narrated, about four minutes: how the list works, what it changes, and where HSREP comes in.', prof:'us-crc', lang:'en', vo:'/assets/worklist-vo/', steps:[
  { v:'start', sel:'.pubstart', t:'What this is', x:'This is the Completion Worklist, and everyone in it is invented. It’s built for the step after a screening result. When a stool test comes back positive, the person still needs a colonoscopy, and that’s the step where many people get lost. The worklist tells staff who to contact first and what help to offer, and then it shows what got finished.' },
  { v:'followup', sel:'section.list', t:'The list, most urgent first', x:'The list is built from the clinic’s nightly file. It holds everyone still waiting on their next step. This week that’s 14 people overdue for a stool test and 9 positive tests waiting for a colonoscopy. The longest wait is at the top, and the numbers in color are already past the 180-day window.' },
  { v:'followup', sel:'.pside', pre:'case', id:'P-1407', t:'Why this person is first', x:'Three plain rules set the order: days overdue, days since a positive test, and missed visits. There’s no hidden model, and the reason sits beside every case, so anyone on staff can check it. P-1407 is first. Their test was positive 210 days ago, and nobody has contacted them yet.' },
  { v:'followup', sel:'.pside .nextbox', pre:'case', id:'P-1407', t:'Help that fits the barrier', x:'Here’s where this differs from the usual approach. A standard reminder goes out the same way to everyone. Here, each person gets help matched to what’s in the way. P-1407 speaks Arabic and prefers a phone call, so the help to offer is an interpreter.' },
  { v:'followup', sel:'.pside .draftbox', pre:'casedraft', id:'P-1407', t:'A message, checked by a person', x:'The tool drafts the message in Arabic from wording the clinic has already signed off. Before it goes out, a named person ticks five checks: the right site, the right instructions, safe for a shared phone, the right language, and a fix for the barrier. If anyone edits or translates it, a second person has to approve it too.' },
  { v:'outbox', sel:'#app [aria-label="Replies"]', t:'Replies are handled', x:'When someone answers, the worklist reads the reply. STOP in English, Spanish, Arabic or Bangla ends every message and booking for that person at once. A yes or a question waits for someone on staff.' },
  { v:'outbox', sel:'#app .table-box', t:'Send and book', x:'Approved messages go out through the clinic’s own accounts, and visits go on the clinic’s own calendar. US texting limits are built in: at most one a day and three a week per person. In this demo it’s all simulated, so nothing leaves your browser.' },
  { v:'steps', sel:'#app section.card', t:'The same steps for everyone', x:'Nobody depends on someone remembering. Every person follows the same plan: a text on day 0, a call on day 5, a letter on day 12 and a visit on day 20. A step only counts as done when it shows in the record.' },
  { v:'next', sel:'#app .ins-list', t:'What to do next', x:'Each week the list turns into a few plain findings, each with one action: who is close to the deadline, what keeps getting in the way, which group is falling behind. This is the page I’d go through with your quality-improvement lead every week, and together we’d decide what to change for the next one.' },
  { v:'equity', sel:'#app section.card', t:'Fair for every group', x:'Completion is also counted by language, insurance and age. That way a group that’s falling behind shows up early instead of disappearing into the average.' },
  { v:'eval', sel:'#app section.card', t:'Does it work?', x:'To know whether the routine itself made the difference, the clinic can hold back a comparison group chosen at random, if its committee approves. The worklist shows the difference with an honest range and drafts the report. With an academic partner, that evaluation is independent.' },
  { v:'start', sel:'#pubNext', t:'Where I come in', x:'Here’s my part. I map your nightly file once with your IT lead, build the weekly list, write and test the scripts with your outreach staff, and review each week with your quality-improvement lead. Your staff keep making the calls and mailing the kits, as they do now. At month three we look at the numbers together and decide whether to continue or stop. This is an HSREP initiative in development, and no clinic is running it yet. If you’d like to see how it fits your clinic, book 30 minutes with me.' } ] });
TOUR_ROLE.voice = 'Narrated · AI voice';
// The narrated tour is featured next to the overview, not repeated in the task grid.
{ const base = toursByTask; toursByTask = function(){ const h = base(); const vc = TOURS.find(t => t.id === 'voice'); return vc ? h.replace(tourCard(vc, false), '') : h; }; }
pubToursCard = function(){ const ov = TOURS.find(t => t.id === 'overview'), vc = TOURS.find(t => t.id === 'voice'); return '<section class="card stack" aria-label="Guided tours"><h2>Take a guided tour</h2><div class="tourgrid">' + (ov ? tourCard(ov, true) : '') + (vc ? tourCard(vc, true) : '') + '</div>' + toursByTask() + '</section>'; };
{ const base = startView; startView = function(){
  return base().replace('<button type="button" class="btn" data-act="pubTour" data-id="overview">Take the five-minute tour</button>', '<button type="button" class="btn" data-act="pubTour" data-id="overview">Take the five-minute tour</button><button type="button" class="btn ghost" data-act="pubTour" data-id="voice">&#9654; Hear it narrated, 4 min</button>');
}; }
// One person for the whole story: the steps marked 'case' open P-1407, and 'casedraft' adds its draft.
{ const base = tourPrep; tourPrep = async function(st){
  if ((st.pre === 'case' || st.pre === 'casedraft') && st.id && patientById(st.id)){
    const p = patientById(st.id); S.ui.selected = p.id; selectedDraftEdit = null;
    if (st.pre === 'casedraft' && !draftsFor(p.id).some(d => d.status === 'pending')){ const t = Object.values(S.templates).find(x => x.channel === 'sms' && (!x.cohort || x.cohort === 'followup')); if (t) await v9Muted(() => createDraft(p.id, t.id, t.langs[p.lang] ? p.lang : Object.keys(t.langs)[0], { noCanary:true })); }
    return;
  }
  return base(st);
}; }
const VT = { on:false, aud:null, k:-1, ended:false, paused:false, t:0 };
function vtTour(){ const tr = TOUR && TOURS.find(x => x.id === TOUR.id); return tr && tr.vo ? tr : null; }
function vtClip(tr, i){ return tr.vo + 'step-' + String(i + 1).padStart(2, '0') + '.mp3?v=' + VOICE_VER; }
function vtAudio(){
  if (!VT.aud){ VT.aud = new Audio(); VT.aud.preload = 'auto'; VT.aud.addEventListener('ended', vtEnded); VT.aud.addEventListener('error', () => { if (VT.on){ VT.on = false; vtUI(); } }); }
  return VT.aud;
}
function vtStop(){ clearTimeout(VT.t); if (VT.aud) try { VT.aud.pause(); } catch(e){} }
// Called straight from a tap, so phones allow the sound; later steps reuse the same player.
function vtStartAt(i){
  const tr = vtTour() || TOURS.find(x => x.id === 'voice'); const a = vtAudio(); clearTimeout(VT.t);
  VT.on = true; VT.paused = false; VT.ended = false; VT.k = i; a.src = vtClip(tr, i);
  const p = a.play(); if (p && p.catch) p.catch(() => { VT.on = false; vtUI(); });
}
function vtPlay(){
  const tr = vtTour(); if (!tr || !VT.on) return;
  if (VT.k === TOUR.i && !VT.ended && VT.aud && VT.aud.src.indexOf(vtClip(tr, TOUR.i).split('?')[0]) >= 0) return;
  vtStartAt(TOUR.i);
}
function vtEnded(){
  const tr = vtTour(); if (!tr || !VT.on) return; VT.ended = true; vtUI(); const k = TOUR.i;
  VT.t = setTimeout(() => { if (!TOUR || TOUR.i !== k || !VT.on || VT.paused) return; if (k < tr.steps.length - 1) tourGo(k + 1); else siteEvent('worklist_voice_complete', {}); }, 700);
}
function vtUI(){
  const box = document.getElementById('tourBox'); const tr = vtTour(); if (!box || !tr) return;
  let row = box.querySelector('.vt-row'); if (!row){ row = document.createElement('div'); row.className = 'vt-row'; const t = box.querySelector('.tb-t'); if (t) t.insertAdjacentElement('beforebegin', row); else box.appendChild(row); }
  const last = TOUR.i === tr.steps.length - 1;
  let b;
  if (!VT.on) b = '<button type="button" class="btn sm primary" data-vt="play">&#9654; Play with my voice</button>';
  else if (VT.paused || (VT.ended && last)) b = '<button type="button" class="btn sm primary" data-vt="resume">&#9654; ' + (VT.ended && last ? 'Play again' : 'Resume') + '</button>';
  else b = '<button type="button" class="btn sm" data-vt="pause">&#10074;&#10074; Pause</button>';
  const nav = box.querySelector(':scope > .row.between'); if (nav && row.nextElementSibling !== nav) row.insertAdjacentElement('afterend', nav);
  row.innerHTML = b + (VT.on ? '<button type="button" class="btn sm ghost" data-vt="mute">Voice off</button>' : '') + '<span class="vt-lbl' + (VT.on && !VT.paused && !VT.ended ? ' live' : '') + '"><i aria-hidden="true"></i>Narrated by an AI version of the founder’s voice</span>';
}
{ const base = tourShow; tourShow = function(){ const r = base.apply(this, arguments); if (vtTour()) vtUI(); return r; }; }
{ const base = tourGo; tourGo = async function(i){ clearTimeout(VT.t); const r = await base(i); if (vtTour() && VT.on) vtPlay(); else vtStop(); vtUI(); return r; }; }
{ const base = tourEnd; tourEnd = function(){ vtStop(); VT.on = false; VT.k = -1; return base.apply(this, arguments); }; }
document.addEventListener('click', ev => {
  const c = ev.target.closest && ev.target.closest('[data-act="pubTour"][data-id="voice"]');
  if (c){ VT.on = true; vtStartAt(0); siteEvent('worklist_voice_on', { step:1 }); return; }
  const b = ev.target.closest && ev.target.closest('[data-vt]'); if (!b || !vtTour()) return; ev.preventDefault();
  const a = b.dataset.vt;
  if (a === 'play'){ vtStartAt(TOUR.i); siteEvent('worklist_voice_on', { step:TOUR.i + 1 }); }
  else if (a === 'pause'){ VT.paused = true; vtStop(); }
  else if (a === 'resume'){ const tr = vtTour(); if (VT.ended && TOUR.i === tr.steps.length - 1){ VT.paused = false; tourGo(0).then(() => {}); vtStartAt(0); } else if (VT.ended){ VT.paused = false; tourGo(TOUR.i + 1); } else { VT.paused = false; const p = vtAudio().play(); if (p && p.catch) p.catch(() => {}); } }
  else if (a === 'mute'){ VT.on = false; vtStop(); siteEvent('worklist_voice_off', { step:TOUR.i + 1 }); }
  vtUI();
}, true);
// Styles for the voice row. Also: a table's hidden header text no longer widens the page on phones.
(function(){ const st = document.createElement('style'); st.id = 'vtCss'; st.textContent =
  '#tourBox .vt-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:2px 0 4px}#tourBox .vt-row + .row.between{margin:2px 0 8px}' +
  '#tourBox .vt-lbl{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--muted)}' +
  '#tourBox .vt-lbl i{width:8px;height:8px;border-radius:50%;background:var(--hair);flex:none}' +
  '#tourBox .vt-lbl.live i{background:var(--coral);animation:vtp 1.2s ease-in-out infinite}' +
  '.table-box{position:relative}' +
  '@keyframes vtp{50%{opacity:.35}}@media (prefers-reduced-motion:reduce){#tourBox .vt-lbl.live i{animation:none}}';
  document.head.appendChild(st); })();
