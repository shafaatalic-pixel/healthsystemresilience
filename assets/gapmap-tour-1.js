/* Prevention Gap Map, guided tour. Silent by default; optional narration in an AI version of the founder's voice.
   The tour drives the real page (regions, a center, the comparison, the goal slider) through window.GM, and puts
   everything back when it ends. Clips: /assets/gapmap-vo/step-NN.mp3 */
(function(){
  var VOV='20261106a';
  var UGL='upper-great-lakes-family-health-center';
  var STEPS=[
    {sel:'.gm-herocard',ms:9000,eye:'The starting point',title:'Fewer than half are up to date.',
     line:"At Michigan's 39 federally funded health centers, 48.7% of adults aged 46 to 75 were up to date on colorectal cancer screening in 2025. The target is 72.8%."},
    {sel:'.gm-stage',ms:8500,eye:'The map',title:'Every dot is a clinic.',
     line:"Each dot is a clinic site, colored by its health center's rate: green at or above the target, deeper red the further below. Grey means HRSA did not publish a rate.",
     act:function(G){G.clearSel();G.tab('map');rg('all');}},
    {sel:'.gm-stage',ms:7500,eye:'Find your area',title:'Zoom in to where you work.',
     line:'Jump to a region like Detroit, scroll to zoom, or search any center or city, including the names people actually use.',
     act:function(G){G.clearSel();G.tab('map');rg('detroit');}},
    {sel:'.gm-stage',selM:'#gm-panel',ms:8000,eye:'One center',title:'Open any center.',
     line:'Each center shows its rate, its eligible adults, and how many more screenings would reach the target. Every center has its own link you can share.',
     act:function(G){G.tab('map');rg('up');G.select(UGL);}},
    {sel:'#compare',ms:7000,eye:'Compare',title:'Put three side by side.',
     line:'Patients, neighborhoods and resources differ, so a comparison starts a conversation. It does not settle one.',
     act:function(G){G.setCmp([UGL,'grace-health','packard-health']);}},
    {sel:'#distribution',ms:7500,eye:'Every center',title:'All 35 against one line.',
     line:'Each dot is a center with a published rate. The dashed line is the target. Size the dots by eligible adults to see where the most people are.'},
    {sel:'#signals',ms:9500,eye:'What it means',title:'Useful signals. Better questions.',
     line:'Rural centers reached 57.8%, urban centers 43.9%, and 16 centers are more than 25 points below the target. The question is what stands in the way: access, outreach, kits returned, or follow-up.'},
    {sel:'#scenario',ms:8000,eye:'A scenario',title:'Move the goal. See what it takes.',
     line:'Reaching 72.8% means 45,138 more adults screened. Even a goal of 60% would mean 21,122 more. It is arithmetic, not a forecast.',
     act:function(G){G.goal(60);}},
    {sel:'#next',ms:9000,eye:'The next step',title:'A test is only step one.',
     line:'A screening rate cannot show whether a positive stool test led to a colonoscopy. The Completion Worklist is built for that step, and you can send two counts for a free one-page readout.',
     act:function(G){G.goal();}},
    {sel:'#methods',ms:8500,eye:'How this is made',title:'Public data. Not a ranking.',
     line:"Every number comes from HRSA's public 2025 file, the methods are open, and the map is updated each year. A lower rate is a reason to look at barriers, not a judgment of care."}
  ];
  var i=-1,timer=null,paused=false,VO=false,aud=null,voEnded=false,saved=null,raf=0,target=null;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function ev(n,p){try{if(window.gtag)window.gtag('event',n,p||{});}catch(e){}}
  function rg(k){var b=document.querySelector('.gm [data-region="'+k+'"]');if(b)b.click();}
  function G(){return window.GM;}
  var SPK='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 10v4h4l5 4V6L7 10H3zm13.5 2a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z"/></svg>';
  var MUTE='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 10v4h4l5 4V6L7 10H3zm13.6 2 2.4-2.4-1.1-1.1-2.4 2.4-2.4-2.4-1.1 1.1 2.4 2.4-2.4 2.4 1.1 1.1 2.4-2.4 2.4 2.4 1.1-1.1z"/></svg>';

  var hole=document.createElement('div');hole.className='gt-hole';hole.setAttribute('aria-hidden','true');
  var bar=document.createElement('div');bar.className='gt-bar';bar.setAttribute('role','dialog');bar.setAttribute('aria-live','polite');bar.setAttribute('aria-label','Guided tour of the Gap Map');
  var launch=document.createElement('button');launch.type='button';launch.className='gt-launch';
  launch.innerHTML='&#9654; Tour';launch.setAttribute('aria-label','Take a guided tour of the Gap Map');
  launch.addEventListener('click',function(){start(false);});
  document.body.appendChild(hole);document.body.appendChild(bar);document.body.appendChild(launch);

  /* the spotlight follows its target while the page scrolls or the layout moves */
  function place(){if(!target){hole.style.opacity=0;return;}var r=target.getBoundingClientRect(),p=10,hh=headerH(),t=Math.max(r.top-p,hh+4),b=r.bottom+p;
    hole.style.top=t+'px';hole.style.left=(r.left-p)+'px';hole.style.width=(r.width+2*p)+'px';hole.style.height=Math.max(0,b-t)+'px';hole.style.opacity=1;}
  function loop(){place();raf=requestAnimationFrame(loop);}
  function headerH(){var h=0;['.hs-top','#secnav'].forEach(function(q){var e=document.querySelector(q);if(!e)return;var ps=getComputedStyle(e).position,r=e.getBoundingClientRect();if((ps==='sticky'||ps==='fixed')&&r.bottom>0&&r.top<220&&r.bottom>h)h=r.bottom;});return h;}
  function scrollTo(el){var y=el.getBoundingClientRect().top+window.pageYOffset-headerH()-18;
    try{window.scrollTo({top:Math.max(0,y),behavior:reduce?'auto':'smooth'});}catch(e){window.scrollTo(0,y);}}

  function clip(k){return '/assets/gapmap-vo/step-'+(k<9?'0':'')+(k+1)+'.mp3?v='+VOV;}
  function stopVO(){if(aud){aud.onended=null;aud.onerror=null;try{aud.pause();}catch(e){}aud=null;}voEnded=false;}
  function voFallback(){stopVO();VO=false;render();schedule();}
  function playVO(){stopVO();if(!VO||i<0)return;var k=i;aud=new Audio(clip(k));aud.preload='auto';
    aud.onended=function(){voEnded=true;if(paused||!VO)return;if(timer)clearTimeout(timer);
      timer=setTimeout(function(){if(k>=STEPS.length-1){ev('gapmap_tour_voice_complete',{});finish();}else go(k+1);},650);};
    aud.onerror=voFallback;if(!paused){var pr=aud.play();if(pr&&pr.catch)pr.catch(voFallback);}
    if(k+1<STEPS.length){try{var nx=new Audio();nx.preload='auto';nx.src=clip(k+1);}catch(e){}}}
  function setVoice(on){VO=!!on;ev(VO?'gapmap_tour_voice_on':'gapmap_tour_voice_off',{step:i+1});if(timer)clearTimeout(timer);
    if(VO){paused=false;render();playVO();}else{stopVO();render();schedule();}}

  function render(){var s=STEPS[i];if(!s)return;var last=i===STEPS.length-1;
    var dots=STEPS.map(function(_,k){return '<i'+(k===i?' class="on"':'')+'></i>';}).join('');
    bar.innerHTML='<button type="button" class="gt-x" aria-label="Close the tour">&times;</button>'+
      '<div class="gt-eye">'+s.eye+'</div><h3>'+s.title+'</h3><p>'+s.line+'</p>'+
      (VO?'<div class="gt-vo'+(paused?' paused':'')+'"><i></i>Narrated by an AI version of the founder\'s voice</div>':'')+
      '<div class="gt-ctrls"><div class="gt-dots" aria-hidden="true">'+dots+'</div><div class="gt-btns"><span class="gt-n">'+(i+1)+' / '+STEPS.length+'</span>'+
      '<button type="button" class="gt-voice" aria-pressed="'+VO+'" aria-label="'+(VO?'Turn off narration':'Play with narration')+'">'+(VO?SPK:MUTE)+'<span>'+(VO?'Voice on':'Voice')+'</span></button>'+
      '<button type="button" class="gt-prev" aria-label="Previous"'+(i===0?' disabled':'')+'>&larr;</button>'+
      ((reduce&&!VO)?'':'<button type="button" class="gt-pause" aria-label="'+(paused?'Play':'Pause')+'">'+(paused?'&#9654;':'&#10074;&#10074;')+'</button>')+
      (last?'<button type="button" class="gt-go gt-done">Done</button>':'<button type="button" class="gt-go gt-next">Next &rarr;</button>')+'</div></div>';
    bar.querySelector('.gt-x').onclick=stop;
    var b;if(b=bar.querySelector('.gt-prev'))b.onclick=function(){go(i-1);};
    if(b=bar.querySelector('.gt-next'))b.onclick=function(){go(i+1);};
    if(b=bar.querySelector('.gt-done'))b.onclick=finish;
    if(b=bar.querySelector('.gt-pause'))b.onclick=togglePause;
    if(b=bar.querySelector('.gt-voice'))b.onclick=function(){setVoice(!VO);};}
  function schedule(){if(timer)clearTimeout(timer);if(paused||reduce||VO)return;var d=STEPS[i].ms;
    timer=setTimeout(function(){if(i>=STEPS.length-1)finish();else go(i+1);},d);}
  function go(n){n=Math.max(0,Math.min(STEPS.length-1,n));i=n;var s=STEPS[i];
    if(s.act&&G()){window.__gmTour=true;try{s.act(G());}catch(e){}window.__gmTour=true;}
    target=document.querySelector((s.selM&&window.innerWidth<980)?s.selM:s.sel);render();if(target)scrollTo(target);
    if(VO)playVO();else schedule();}
  function togglePause(){paused=!paused;render();if(VO){if(timer)clearTimeout(timer);
      if(paused){if(aud)try{aud.pause();}catch(e){}}else if(voEnded||!aud){if(i>=STEPS.length-1)finish();else go(i+1);}
      else{var pr=aud.play();if(pr&&pr.catch)pr.catch(voFallback);}}else schedule();}
  function start(voice){if(!G())return;if(i>=0)return;
    saved={cmp:G().cmp()};window.__gmTour=true;VO=!!voice;paused=false;
    document.body.classList.add('gt-on');bar.classList.add('on');launch.hidden=true;
    cancelAnimationFrame(raf);loop();ev('gapmap_tour_start',{voice:VO?'on':'off'});go(0);}
  function end(){stopVO();if(timer)clearTimeout(timer);cancelAnimationFrame(raf);target=null;place();
    bar.classList.remove('on');document.body.classList.remove('gt-on');launch.hidden=false;i=-1;
    var g=G();if(g){try{g.goal();g.clearSel();g.tab('map');rg('all');if(saved)g.setCmp(saved.cmp);}catch(e){}}
    window.__gmTour=false;var top=document.getElementById('explore');if(top)scrollTo(top);}
  function stop(){if(i>=0)ev('gapmap_tour_close',{step:i+1});end();}
  function finish(){ev('gapmap_tour_complete',{voice:VO?'on':'off'});end();}
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&i>=0)stop();});
  document.addEventListener('click',function(e){var t=e.target&&e.target.closest?e.target.closest('[data-gmtour]'):null;
    if(!t)return;e.preventDefault();start(t.getAttribute('data-gmtour')==='voice');});
  window.startGapMapTour=start;
})();
