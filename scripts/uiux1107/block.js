
// ---- uiux-1107: start screen, sample case, grouped tours, docked tour box ----
// Picks 1 to 4 of the 7 Nov 2026 UI/UX review. Wraps existing functions; nothing above is edited.
Object.assign(BN, {
  'Start here':'এখান থেকে শুরু করুন',
  'First on the list':'তালিকায় প্রথম',
  'Next step:':'পরের ধাপ:',
  'Open the sample worklist':'নমুনা তালিকা খুলুন',
  'New here?':'নতুন?',
  'Nine steps, about five minutes: from the list to a sent message.':'নয়টি ধাপ, প্রায় পাঁচ মিনিট: তালিকা থেকে পাঠানো বার্তা পর্যন্ত।',
  'Take the five-minute tour':'পাঁচ মিনিটের ট্যুর নিন',
  'Or explore by task':'অথবা কাজ ধরে দেখুন',
  '{n} invented people. See who comes first, why, and what to do next.':'{n} জন কাল্পনিক মানুষ। কে আগে, কেন, আর এরপর কী করতে হবে দেখুন।',
  'Your list is open in this browser. Nothing is sent until someone presses Send.':'আপনার তালিকা এই ব্রাউজারেই খোলা আছে। কেউ পাঠান চাপার আগে কিছুই যায় না।',
  'How it works':'কীভাবে কাজ করে',
  'Set up a worklist':'তালিকা তৈরি করুন',
  'Steps A to C':'ধাপ ক থেকে গ',
  'Programme, your own list and your details':'কর্মসূচি, আপনার নিজের তালিকা ও আপনার তথ্য',
  'Start with this one':'এটি দিয়ে শুরু করুন',
  'For outreach staff':'আউটরিচ কর্মীদের জন্য',
  'For clinic managers':'ক্লিনিক ব্যবস্থাপকদের জন্য',
  'For quality leads and funders':'মান-উন্নয়ন প্রধান ও অর্থদাতাদের জন্য',
  'For clinical leads and IT':'ক্লিনিক্যাল প্রধান ও আইটি দলের জন্য',
  'Exit tour':'ট্যুর বন্ধ করুন'
});
const TOUR_ROLE = { overview:'Start with this one', safe:'For outreach staff', plan:'For clinic managers', works:'For quality leads and funders', ready:'For clinical leads and IT', bd:'বাংলা · Bangla' };
function tourMeta(t){
  if (t.lang === 'bn') return 'উচ্চ রক্তচাপ · বাংলা · ' + t.steps.length + ' ধাপ';
  const pr = PROFILES[t.prof]; const prog = pr ? String(pr.label.split(' · ')[1] || '').split(': ')[0] : '';
  return [prog, 'English', t.steps.length + ' steps'].filter(Boolean).map(x => '<span>' + esc(x) + '</span>').join(' · ');
}
function tourCard(t, feat){
  const bn = t.lang === 'bn';
  return '<button type="button" class="tourcard' + (feat ? ' feat' : '') + '" data-act="pubTour" data-id="' + t.id + '"' + (bn ? ' lang="bn" data-no-tr' : '') + '><span class="tc-role">' + esc(TOUR_ROLE[t.id] || '') + '</span><b>' + esc(t.t) + '</b><span class="small">' + esc(t.d) + '</span><span class="tc-meta">' + tourMeta(t) + '</span></button>';
}
function toursByTask(){ return '<h3 class="ps-sub">Or explore by task</h3><div class="tourgrid">' + TOURS.filter(t => t.id !== 'overview').map(t => tourCard(t, false)).join('') + '</div>'; }
pubToursCard = function(){ const ov = TOURS.find(t => t.id === 'overview'); return '<section class="card stack" aria-label="Guided tours"><h2>Take a guided tour</h2><div class="tourgrid">' + (ov ? tourCard(ov, true) : '') + '</div>' + toursByTask() + '</section>'; };
function sampleCase(){
  if (!isSynthetic()) return null;
  return rankList('followup', false).filter(p => isOpen(p) && !S.optOuts.includes(p.id))[0] || null;
}
function startCard(){
  const synth = isSynthetic(); const top = sampleCase();
  let c = '<section class="card stack pubstart" aria-label="Start here"><span class="eyebrow">Start here</span><h1>Help people finish the step they started.</h1>';
  c += '<p class="lede">' + esc(synth ? S.patients.length + ' invented people. See who comes first, why, and what to do next.' : 'Your list is open in this browser. Nothing is sent until someone presses Send.') + '</p><div class="ps-grid">';
  if (top){
    const n = nextStep(top); const why = urgencyWhy(top);
    const help = barriersOf(top).filter(b => PLAYBOOK[b]).map(b => PLAYBOOK[b].short);
    c += '<div class="ps-case"><span class="eyebrow">First on the list</span><div class="row" style="gap:8px;align-items:center"><span class="ps-id mono">' + esc(top.id) + '</span>' + statusChip(top) + '<span class="chip line">' + esc(LANGS[top.lang] || top.lang) + '</span></div>' +
      (why ? '<span class="small">' + esc(why) + '</span>' : '') +
      '<span class="small"><b>Next step:</b> <span>' + esc(n.title) + '</span></span>' +
      (help.length ? '<span class="small"><b>Help to offer:</b> <span>' + esc(help[0]) + '</span></span>' : '') +
      '<div class="row"><a class="btn primary" href="#case-' + esc(top.id) + '">Open the sample worklist</a></div></div>';
  } else {
    c += '<div class="ps-case"><div class="row"><a class="btn primary" href="#followup">Open the list</a></div></div>';
  }
  c += '<div class="ps-tour"><b>New here?</b><span class="small">Nine steps, about five minutes: from the list to a sent message.</span><div class="row"><button type="button" class="btn" data-act="pubTour" data-id="overview">Take the five-minute tour</button></div></div></div>';
  return c + toursByTask() + '</section>';
}
{ const base = startView; startView = function(){
  let h = base();
  const tc = pubToursCard(); if (h.indexOf(tc) >= 0) h = h.replace(tc, startCard());
  const fr = firstRunBlock(); if (fr && h.indexOf(fr) >= 0) h = h.replace(fr, '');
  h = h.replace('<span class="eyebrow">§ 01 · Get ready</span><h1>Help people finish the step they started.</h1>', '<span class="eyebrow">How it works</span>');
  const a = h.indexOf('<span class="eyebrow">Step A</span>'); const s0 = a >= 0 ? h.lastIndexOf('<section', a) : -1; const e0 = h.indexOf(pubNextSteps());
  if (s0 >= 0 && e0 > s0){
    const open = !!S.ui.setupOpen || !isSynthetic();
    h = h.slice(0, s0) + '<details class="setupwrap" id="setupWrap"' + (open ? ' open' : '') + '><summary><span class="eyebrow">Steps A to C</span><b>Set up a worklist</b><span class="small muted">Programme, your own list and your details</span></summary><div class="sw-body">' + h.slice(s0, e0) + '</div></details>' + h.slice(e0);
  }
  return h;
}; }
document.addEventListener('toggle', ev => { const t = ev.target; if (t && t.id === 'setupWrap' && S) S.ui.setupOpen = t.open; }, true);
document.addEventListener('click', ev => { if (S && ev.target.closest && ev.target.closest('.banner a[href="#start"], .ctx a[href="#start"]')) S.ui.setupOpen = true; }, true);
// One demo label: the bar under the header says it, so the header chip only shows for a real list.
{ const base = render; render = function(){ const r = base.apply(this, arguments); const sc = document.getElementById('sourceChip'); if (sc) sc.hidden = isSynthetic(); return r; }; }
// Ask HSREP sits in the bar, so no floating button covers the page.
{ const pa = document.querySelector('#pubBar .pb-a'); if (pa && !pa.querySelector('[data-askhs-open]')) pa.insertAdjacentHTML('afterbegin', '<button type="button" class="btn sm" data-askhs-open aria-haspopup="dialog" aria-expanded="false" data-no-tr>Ask HSREP</button>'); }
// A tour shows its own language and programme, but does not change what the next visit opens with.
{ const base = tourStart; tourStart = async function(id){
  const pl = store.get(UI_LANG_KEY), pp = store.get(PROFILE_KEY); const r = await base(id);
  if (pl == null) store.del(UI_LANG_KEY); else store.set(UI_LANG_KEY, pl);
  if (pp == null) store.del(PROFILE_KEY); else store.set(PROFILE_KEY, pp);
  return r; }; }
// The tour box sits beside the screen on wide screens and as a sheet below the content on narrow ones.
function tourLayout(){
  const root = document.documentElement; const box = document.getElementById('tourBox');
  if (!TOUR || !box){ root.classList.remove('touring'); root.style.removeProperty('--tour-h'); return false; }
  root.classList.add('touring');
  if (innerWidth < 1100) root.style.setProperty('--tour-h', (box.offsetHeight + 12) + 'px'); else root.style.removeProperty('--tour-h');
  return true;
}
{ const base = tourShow; tourShow = function(){
  const r = base.apply(this, arguments); const box = document.getElementById('tourBox');
  if (TOUR && box){
    const tr = TOURS.find(x => x.id === TOUR.id); const bn = tr && tr.lang === 'bn';
    const x = box.querySelector('[data-act="pubTourEnd"]'); if (x){ x.textContent = (bn ? 'ট্যুর বন্ধ করুন' : 'Exit tour') + ' ✕'; x.classList.add('tb-x'); }
  }
  if (tourLayout()){
    const tr = TOURS.find(x => x.id === TOUR.id); const st = tr && tr.steps[TOUR.i]; const el = st && (document.querySelector(st.sel) || document.querySelector(st.sel.replace(/\[aria-label=/g, '[data-en-aria-label=')));
    if (el) setTimeout(() => { try { el.scrollIntoView({ block:'start', behavior:'smooth' }); } catch(e){} }, 30);
  }
  return r; }; }
addEventListener('resize', tourLayout);
// Deep link from the website to one sample case: #case-P-1407 opens the list on that person.
function caseFromHash(){
  const m = /^#case-([A-Za-z0-9_-]+)$/.exec(location.hash || ''); if (!m || !S) return; const id = m[1];
  const go = () => {
    if (!patientById(id)) return;
    if (TOUR) tourEnd();
    S.ui.selected = id; S.ui.view = 'followup'; selectedDraftEdit = null;
    try { history.replaceState(null, '', '#followup'); } catch(e){}
    render();
    setTimeout(() => { const el = document.querySelector('.pside'); if (!el) return; el.classList.add('case-hl'); try { el.scrollIntoView({ block:'start', behavior:'smooth' }); } catch(e){} setTimeout(() => el.classList.remove('case-hl'), 2600); }, 60);
    siteEvent('worklist_sample_case', {});
  };
  if (!patientById(id)){
    if (!isSynthetic()){ try { history.replaceState(null, '', '#followup'); } catch(e){} S.ui.view = 'followup'; render(); return; }
    switchTo('us-crc', false); setTimeout(go, 40); return;
  }
  go();
}
addEventListener('hashchange', caseFromHash);
setTimeout(caseFromHash, 650);
