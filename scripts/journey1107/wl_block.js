
// ---- journey-1107: deep links from the website into the demo ----
// #prog-<programme>  opens that programme's list (demo data) on its first person; Bangladesh programmes open in Bangla.
// #draft-<code>      opens that person with a message drafted from signed-off wording, ready for the checks.
// #tour-<id>-<n>     starts a tour at step n.
// None of them changes the saved programme or language, and none replaces a real list.
function jKeepPrefs(fn){ const pl = store.get(UI_LANG_KEY), pp = store.get(PROFILE_KEY); try { return fn(); } finally { setTimeout(() => { if (pl == null) store.del(UI_LANG_KEY); else store.set(UI_LANG_KEY, pl); if (pp == null) store.del(PROFILE_KEY); else store.set(PROFILE_KEY, pp); }, 80); } }
function jShowPerson(id, sel){
  S.ui.selected = id; S.ui.view = 'followup'; selectedDraftEdit = null;
  try { history.replaceState(null, '', '#followup'); } catch(e){}
  render();
  setTimeout(() => { const el = document.querySelector(sel) || document.querySelector('.pside'); if (!el) return; el.classList.add('case-hl'); try { el.scrollIntoView({ block:'start', behavior:'smooth' }); } catch(e){} setTimeout(() => el.classList.remove('case-hl'), 2600); }, 80);
}
async function journeyFromHash(){
  const h = location.hash || ''; if (!S) return;
  let m = /^#prog-([a-z0-9-]+)$/.exec(h);
  if (m){
    const pid = m[1]; if (!PROFILES[pid] || (!isSynthetic() && S.profileId !== pid)) return;
    if (TOUR) tourEnd();
    jKeepPrefs(() => { if (S.profileId !== pid) switchTo(pid, false); setUiLang(PROFILES[pid].country === 'BD' ? 'bn' : 'en'); });
    setTimeout(() => { const first = rankList('followup', false).filter(p => isOpen(p) && !S.optOuts.includes(p.id))[0]; if (first) jShowPerson(first.id, 'section.list'); else { S.ui.view = 'followup'; render(); } siteEvent('worklist_programme_link', { programme: pid }); }, 60);
    return;
  }
  m = /^#draft-([A-Za-z0-9_-]+)$/.exec(h);
  if (m){
    const id = m[1];
    if (!patientById(id)){ if (!isSynthetic()) return; jKeepPrefs(() => switchTo('us-crc', false)); await new Promise(r => setTimeout(r, 60)); }
    const p = patientById(id); if (!p) return; if (TOUR) tourEnd();
    if (!draftsFor(id).some(d => d.status === 'pending')){ const t = Object.values(S.templates).find(x => x.channel === 'sms' && (!x.cohort || x.cohort === 'followup')); if (t) await v9Muted(() => createDraft(p.id, t.id, t.langs[p.lang] ? p.lang : Object.keys(t.langs)[0], { noCanary:true })); }
    jShowPerson(id, '.pside .draftbox');
    siteEvent('worklist_draft_link', {});
    return;
  }
  m = /^#tour-([a-z]+)-(\d+)$/.exec(h);
  if (m && TOURS.some(t => t.id === m[1])){
    const tr = TOURS.find(t => t.id === m[1]); const n = Math.min(Math.max(1, +m[2]), tr.steps.length);
    await tourStart(m[1]); if (n > 1) await tourGo(n - 1);
  }
}
addEventListener('hashchange', journeyFromHash);
setTimeout(journeyFromHash, 700);
