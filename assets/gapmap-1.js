/* Prevention Gap Map, page script. Data: window.GM_DATA or /data/gapmap-2025.json */
(function(){
'use strict';
function boot(D){
var T=D.meta.target, NS='http://www.w3.org/2000/svg';
var C=D.centers; C.forEach(function(c,i){c.i=i;c.pub=c.rate!=null;c.gap=c.pub?Math.max(0,Math.round((Math.round(T*100)-Math.round(c.rate*100))/10)/10):null;/* whole hundredths: no floating-point rounding (46.35 -> 26.5, not 26.4) */c.need=c.pub?Math.max(0,Math.ceil((728*c.den-1000*c.num)/1000)):null;c.siteCities={};});
D.sites.forEach(function(s){C[s[0]].siteCities[s[3].toLowerCase()]=1;});
var byId={};C.forEach(function(c){byId[c.id]=c;});
var MI={n:D.meta.mi_num,d:D.meta.mi_den};MI.r=100*MI.n/MI.d;
var $=function(q){return document.querySelector(q);};
var fmt=function(n){return n.toLocaleString('en-US');};
function band(c){if(!c.pub)return'np';var g=T-c.rate;if(g<=0)return'met';if(g<=10)return'b1';if(g<=25)return'b2';return'b3';}
var COL={met:'var(--gm-met)',b1:'var(--gm-b1)',b2:'var(--gm-b2)',b3:'var(--gm-b3)',np:'var(--gm-np)'};
var BANDTXT={met:'At or above target',b1:'Within 10 points',b2:'10 to 25 points below',b3:'More than 25 points below',np:'Rate not published'};
function col(c){return COL[band(c)];}
function rateTxt(c){return c.pub?String(c.rate)+'%':'Not published';}
function esc(s){return String(s).replace(/[&<>"]/g,function(m){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m];});}
var st={q:'',setting:'',band:'',sort:'name',sel:null,cmp:[],size:'equal',tsort:{k:'name',dir:1}};

function match(c){
 if(st.setting&&c.setting!==st.setting)return false;
 if(st.band&&band(c)!==st.band)return false;
 if(st.q){var q=st.q.toLowerCase();var hay=(c.name+' '+(c.aka||'')+' '+c.city).toLowerCase();
  if(hay.indexOf(q)<0&&!Object.keys(c.siteCities).some(function(k){return k.indexOf(q)>=0;}))return false;}
 return true;}
function filtered(){return C.filter(match);}
function sorted(list){var a=list.slice();
 if(st.sort==='city')a.sort(function(x,y){return x.city.localeCompare(y.city)||x.name.localeCompare(y.name);});
 else if(st.sort==='need')a.sort(function(x,y){return (y.need==null?-1:y.need)-(x.need==null?-1:x.need)||x.name.localeCompare(y.name);});
 else a.sort(function(x,y){return x.name.localeCompare(y.name);});return a;}

/* tooltip */
var tip=$('#gm-tip');
function showTip(e,c){tip.innerHTML='<b>'+esc(c.name)+'</b><span>'+esc(c.city)+' · '+rateTxt(c)+'</span>';var x=Math.min(e.clientX+14,innerWidth-275),y=e.clientY+14;if(y>innerHeight-70)y=e.clientY-60;tip.style.left=x+'px';tip.style.top=y+'px';tip.style.opacity=1;}
function hideTip(){tip.style.opacity=0;}

/* map */
var map=$('#gm-map'),W=D.W,H=D.H,vb={x:0,y:0,w:W,h:H},full={x:0,y:0,w:W,h:H};
map.setAttribute('viewBox','0 0 '+W+' '+H);
var land=document.createElementNS(NS,'path');land.setAttribute('d',D.outline);land.setAttribute('class','land');map.appendChild(land);
var gDots=document.createElementNS(NS,'g');map.appendChild(gDots);
var dots=D.sites.map(function(s){var c=C[s[0]],d=document.createElementNS(NS,'circle');d.setAttribute('cx',s[1]);d.setAttribute('cy',s[2]);d.setAttribute('fill',col(c));d.__c=c;
 d.addEventListener('mousemove',function(e){showTip(e,c);});d.addEventListener('mouseleave',hideTip);
 d.addEventListener('click',function(e){e.stopPropagation();if(!moved)select(c.id);});gDots.appendChild(d);return d;});
function sizeDots(){var r=4.4*Math.pow(vb.w/W,.72),sw=1.1;dots.forEach(function(d){d.setAttribute('r',d.classList.contains('on')?r*1.45:r);d.setAttribute('stroke-width',sw);});}
function setVB(v,anim){
 v.w=Math.max(40,Math.min(W,v.w));v.h=v.w*H/W;v.x=Math.max(-20,Math.min(W-v.w+20,v.x));v.y=Math.max(-20,Math.min(H-v.h+20,v.y));
 if(!anim){vb=v;map.setAttribute('viewBox',[v.x,v.y,v.w,v.h].join(' '));sizeDots();return;}
 var a=Object.assign({},vb),t0=performance.now();
 (function step(t){var k=Math.min(1,(t-t0)/450);k=1-Math.pow(1-k,3);vb={x:a.x+(v.x-a.x)*k,y:a.y+(v.y-a.y)*k,w:a.w+(v.w-a.w)*k,h:a.h+(v.h-a.h)*k};map.setAttribute('viewBox',[vb.x,vb.y,vb.w,vb.h].join(' '));sizeDots();if(k<1)requestAnimationFrame(step);})(t0);}
function region(k){if(k!=='all')ev('gapmap_region',{region:k});var r=k==='all'?[0,0,W,H]:D.regions[k];var w=Math.max(r[2],r[3]*W/H)*1.12;setVB({x:r[0]+r[2]/2-w/2,y:r[1]+r[3]/2-w*H/W/2,w:w},true);
 document.querySelectorAll('.gm-regions button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.region===k);});}
function zoomAt(f,px,py){var nw=Math.max(40,Math.min(W,vb.w*f));var nx=px-(px-vb.x)*nw/vb.w,ny=py-(py-vb.y)*nw/vb.w;setVB({x:nx,y:ny,w:nw},false);
 document.querySelectorAll('.gm-regions button').forEach(function(b){b.setAttribute('aria-pressed',false);});}
function svgPt(e){var r=map.getBoundingClientRect();return{x:vb.x+(e.clientX-r.left)/r.width*vb.w,y:vb.y+(e.clientY-r.top)/r.height*vb.h};}
map.addEventListener('wheel',function(e){if(!e.ctrlKey&&!e.metaKey&&vb.w>=W&&e.deltaY>0)return;e.preventDefault();var p=svgPt(e);zoomAt(e.deltaY<0?0.8:1.25,p.x,p.y);},{passive:false});
var drag=null,moved=false;
map.addEventListener('pointerdown',function(e){drag={x:e.clientX,y:e.clientY,vb:Object.assign({},vb)};moved=false;});
window.addEventListener('pointermove',function(e){if(!drag)return;var dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>4){moved=true;map.classList.add('drag');}
 if(moved){var r=map.getBoundingClientRect();setVB({x:drag.vb.x-dx/r.width*drag.vb.w,y:drag.vb.y-dy/r.height*drag.vb.h,w:drag.vb.w},false);}});
window.addEventListener('pointerup',function(){drag=null;map.classList.remove('drag');setTimeout(function(){moved=false;},0);});
$('#gm-zin').onclick=function(){zoomAt(0.7,vb.x+vb.w/2,vb.y+vb.h/2);};
$('#gm-zout').onclick=function(){zoomAt(1.43,vb.x+vb.w/2,vb.y+vb.h/2);};
$('#gm-zreset').onclick=function(){region('all');};
document.querySelectorAll('.gm-regions button').forEach(function(b){b.onclick=function(){region(b.dataset.region);};});
map.addEventListener('click',function(){if(!moved&&st.sel)clearSel();});

/* render all views */
function render(){
 var f=filtered(),ids={};f.forEach(function(c){ids[c.id]=1;});
 var nsites=0;dots.forEach(function(d){var show=!!ids[d.__c.id];d.style.display=show?'':'none';if(show)nsites++;
  d.classList.toggle('dim',!!st.sel&&d.__c.id!==st.sel);d.classList.toggle('on',d.__c.id===st.sel);});
 sizeDots();
 $('#gm-count').textContent=nsites+' sites · '+f.length+' of '+C.length+' centers';
 var ul=$('#gm-list');ul.innerHTML='';
 sorted(f).forEach(function(c){var li=document.createElement('li');li.innerHTML='<button type="button"><i style="background:'+col(c)+'"></i><span><b>'+esc(c.name)+'</b><small>'+esc(c.city)+' · '+c.setting+' · '+c.nsites+(c.nsites===1?' site':' sites')+'</small></span><em>'+(c.pub?c.rate+'%':'n/p')+'</em></button>';
  li.firstChild.onclick=function(){select(c.id);};ul.appendChild(li);});
 $('#gm-listnote').textContent=st.sort==='need'?'Planning view: ordered by the number of additional adults, not by rate. Not a ranking.':'Listed A to Z. This map is never a ranking.';
 renderTable(f);renderStrip();
}
function renderTable(f){var k=st.tsort.k,dir=st.tsort.dir,a=f.slice();
 a.sort(function(x,y){var u=x[k],v=y[k];if(u==null&&v==null)return x.name.localeCompare(y.name);if(u==null)return 1;if(v==null)return -1;return (typeof u==='string'?u.localeCompare(v):u-v)*dir||x.name.localeCompare(y.name);});
 $('#gm-tbody').innerHTML=a.map(function(c){return '<tr data-id="'+c.id+'"><td><i style="background:'+col(c)+'"></i>'+esc(c.name)+'</td><td>'+esc(c.city)+'</td><td>'+c.setting+'</td><td class="n">'+c.nsites+'</td><td class="n">'+(c.pub?c.rate+'%':'n/p')+'</td><td class="n">'+(c.pub?(c.gap===0?'met':c.gap):'')+'</td><td class="n">'+(c.pub?fmt(c.need):'')+'</td></tr>';}).join('');
 document.querySelectorAll('#gm-tbody tr').forEach(function(tr){tr.onclick=function(){select(tr.dataset.id);};});
 document.querySelectorAll('.gm-table th').forEach(function(th){th.setAttribute('aria-sort',th.dataset.k===k?(dir>0?'ascending':'descending'):'none');});}
document.querySelectorAll('.gm-table th button').forEach(function(b){b.onclick=function(){var k=b.parentNode.dataset.k;st.tsort=st.tsort.k===k?{k:k,dir:-st.tsort.dir}:{k:k,dir:1};renderTable(filtered());};});

/* detail panel */
function ev(n,p){if(window.__gmTour)return;try{if(window.gtag)window.gtag('event',n,p||{});}catch(e){}}
function select(id){var c=byId[id];if(!c)return;st.sel=id;ev('gapmap_center',{center:id});
 $('#gm-panel-empty').hidden=true;var p=$('#gm-panel-one');p.hidden=false;p.className='gm-one';
 var h='<button type="button" class="gm-back" id="gm-back">&larr; All centers</button><span class="mono" style="display:block;color:var(--pai-coral-text)">'+BANDTXT[band(c)]+'</span><h3>'+esc(c.name)+'</h3><p class="gm-sub">'+(c.aka?esc(c.aka)+' · ':'')+esc(c.city)+' · '+c.setting+' · '+c.nsites+(c.nsites===1?' clinic site':' clinic sites')+'</p>';
 if(c.pub){h+='<div class="gm-rate">'+c.rate+'<small>%</small></div><div class="gm-bar"><i style="width:'+c.rate+'%;background:'+col(c)+'"></i><b style="left:'+T+'%"></b></div><div class="gm-barlab"><span>Published rate, 2025</span><span>Target '+T+'%</span></div>'+
  '<dl class="gm-kv"><dt>Adults screened</dt><dd>'+fmt(c.num)+'</dd><dt>Eligible adults, 46 to 75</dt><dd>'+fmt(c.den)+'</dd><dt>Not up to date</dt><dd>'+fmt(c.den-c.num)+'</dd><dt>More adults to reach 72.8%</dt><dd>'+(c.need===0?'target met':fmt(c.need))+'</dd></dl>'+
  (c.need>0?'<p class="gm-callout"><b>'+fmt(c.need)+' more adults screened</b> would bring this center to the target, with the same number of eligible adults.</p>':'<p class="gm-callout">This center is at or above the 72.8% target.</p>');}
 else h+='<p>HRSA did not publish a 2025 screening rate for this center. Nothing is estimated here.</p>';
 /* journey-1107 */if(c.pub&&c.need>0)h+='<div class="gm-fix"><span class="mono">Closing the gap</span><p>Screening is step one. The Completion Worklist works the weekly list of people who are due, and of positive tests still waiting for a colonoscopy, most urgent first.</p><a href="/worklist/#case-P-1407">See one case in the demo &rarr;</a><a href="#next">Ask for a free follow-up readout &rarr;</a></div>';
 h+='<div class="gm-btns"><button type="button" class="btn pai-secondary gm-sm" id="gm-addcmp">Add to comparison</button><button type="button" class="btn pai-secondary gm-sm" id="gm-copy">Copy link to this center</button></div><p class="gm-note" id="gm-copied"></p>';
 p.innerHTML=h;$('#gm-back').onclick=clearSel;$('#gm-addcmp').onclick=function(){addCmp(id);document.getElementById('compare').scrollIntoView({behavior:'smooth'});};
 $('#gm-copy').onclick=function(){var url=location.href.split('#')[0]+'#center='+id;var done=function(){$('#gm-copied').textContent='Link copied: '+url;};
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(url).then(done,function(){$('#gm-copied').textContent=url;});else $('#gm-copied').textContent=url;};
 try{history.replaceState(null,'','#center='+id);}catch(e){}
 render();if(innerWidth<980&&!$('#gm-mapview').hidden)p.scrollIntoView({behavior:'smooth',block:'start'});}
function clearSel(){st.sel=null;$('#gm-panel-empty').hidden=false;$('#gm-panel-one').hidden=true;try{history.replaceState(null,'',location.pathname+location.search);}catch(e){}render();}

/* filters */
var qEl=$('#gm-q');qEl.addEventListener('input',function(){st.q=qEl.value.trim();render();});
$('#gm-setting').onchange=function(e){st.setting=e.target.value;render();};
$('#gm-band').onchange=function(e){st.band=e.target.value;render();};
$('#gm-sort').onchange=function(e){st.sort=e.target.value;render();};
$('#gm-reset').onclick=function(){st.q='';st.setting='';st.band='';st.sort='name';qEl.value='';$('#gm-setting').value='';$('#gm-band').value='';$('#gm-sort').value='name';clearSel();region('all');};
document.querySelectorAll('[data-setfilter]').forEach(function(a){a.addEventListener('click',function(){var kv=a.dataset.setfilter.split(':');st[kv[0]]=kv[1];$('#gm-'+kv[0]).value=kv[1];render();});});
document.querySelectorAll('[data-focus-search]').forEach(function(a){a.addEventListener('click',function(){setTimeout(function(){qEl.focus({preventScroll:true});},450);});});
function tab(which){var m=which==='map';$('#gm-tab-map').setAttribute('aria-selected',m);$('#gm-tab-table').setAttribute('aria-selected',!m);$('#gm-mapview').hidden=!m;$('#gm-tableview').hidden=m;document.querySelector('.gm-regions').style.visibility=m?'visible':'hidden';}
$('#gm-tab-map').onclick=function(){tab('map');};$('#gm-tab-table').onclick=function(){tab('table');};

/* compare */
function addCmp(id){ev('gapmap_compare',{center:id});if(st.cmp.indexOf(id)<0){if(st.cmp.length>=3)st.cmp.shift();st.cmp.push(id);}renderCmp();}
function renderCmp(){var box=$('#gm-compare'),opts='<option value="">Choose a health center</option>'+C.slice().sort(function(a,b){return a.name.localeCompare(b.name);}).map(function(c){return '<option value="'+c.id+'">'+esc(c.name)+'</option>';}).join('');
 var h='';for(var i=0;i<3;i++){var id=st.cmp[i],c=id&&byId[id];
  if(!c){h+='<div class="gm-cslot empty"><span class="mono">'+(i===0?'Start a comparison':'Add another center')+'</span><p class="gm-note" style="margin:6px 0 10px">Pick a center here, or use "Add to comparison" on the map.</p><select data-slot="'+i+'" aria-label="Choose a health center to compare">'+opts+'</select></div>';continue;}
  h+='<div class="gm-cslot"><button type="button" class="gm-x" data-rm="'+id+'" aria-label="Remove">Remove</button><h3>'+esc(c.name)+'</h3><p class="gm-sub">'+esc(c.city)+' · '+c.setting+'</p>'+
   (c.pub?'<div class="gm-rate">'+c.rate+'%</div><div class="gm-bar"><i style="width:'+c.rate+'%;background:'+col(c)+'"></i><b style="left:'+T+'%"></b></div><dl class="gm-kv"><dt>Eligible adults</dt><dd>'+fmt(c.den)+'</dd><dt>Not up to date</dt><dd>'+fmt(c.den-c.num)+'</dd><dt>More to reach 72.8%</dt><dd>'+(c.need===0?'met':fmt(c.need))+'</dd><dt>Clinic sites</dt><dd>'+c.nsites+'</dd></dl>':'<p class="gm-note">Rate not published by HRSA for 2025.</p>')+'</div>';}
 box.innerHTML=h;
 box.querySelectorAll('select').forEach(function(s){s.onchange=function(){if(s.value)addCmp(s.value);};});
 box.querySelectorAll('[data-rm]').forEach(function(b){b.onclick=function(){st.cmp=st.cmp.filter(function(x){return x!==b.dataset.rm;});renderCmp();};});}

/* distribution */
var strip=$('#gm-strip'),SX=function(v){return 50+v/100*900;},SY=118,sdots={};
(function axes(){function el(t,a,txt){var e=document.createElementNS(NS,t);for(var k in a)e.setAttribute(k,a[k]);if(txt)e.textContent=txt;strip.appendChild(e);return e;}
 el('line',{x1:SX(0),x2:SX(100),y1:212,y2:212,stroke:'#C9D3DD'});
 [0,20,40,60,80,100].forEach(function(v){el('line',{x1:SX(v),x2:SX(v),y1:208,y2:216,stroke:'#C9D3DD'});el('text',{x:SX(v),y:236,'text-anchor':'middle','font-size':12,fill:'#65717E','font-family':'IBM Plex Mono, monospace'},v+'%');});
 el('line',{x1:SX(T),x2:SX(T),y1:26,y2:212,stroke:'#1C2E4A','stroke-dasharray':'5 5'});el('text',{x:SX(T)+7,y:34,'font-size':13,fill:'#1C2E4A','font-weight':600},'Target 72.8%');
 el('line',{x1:SX(MI.r),x2:SX(MI.r),y1:44,y2:212,stroke:'#65717E'});el('text',{x:SX(MI.r)-7,y:52,'font-size':13,fill:'#65717E','text-anchor':'end'},'Michigan '+MI.r.toFixed(1)+'%');
 C.filter(function(c){return c.pub;}).forEach(function(c){var d=el('circle',{cx:SX(c.rate),cy:SY,r:7,fill:col(c)});d.addEventListener('mousemove',function(e){showTip(e,c);});d.addEventListener('mouseleave',hideTip);
  d.addEventListener('click',function(){select(c.id);document.getElementById('explore').scrollIntoView({behavior:'smooth'});});sdots[c.id]=d;});})();
function layoutStrip(){var pub=C.filter(function(c){return c.pub;}),maxD=Math.max.apply(null,pub.map(function(c){return c.den;}));
 var rad=function(c){return st.size==='den'?4+14*Math.sqrt(c.den/maxD):7.5;};
 var placed=[];pub.slice().sort(function(a,b){return rad(b)-rad(a);}).forEach(function(c){var x=SX(c.rate),r=rad(c),y=SY,s=0;
  while(placed.some(function(p){return Math.hypot(p.x-x,p.y-y)<p.r+r+1.2;})&&s<60){s++;y=SY+(s%2?-1:1)*Math.ceil(s/2)*3;}
  placed.push({x:x,y:y,r:r});var d=sdots[c.id];d.setAttribute('cx',x);d.setAttribute('cy',y);d.setAttribute('r',r);});}
function renderStrip(){var ids={};filtered().forEach(function(c){ids[c.id]=1;});Object.keys(sdots).forEach(function(id){var d=sdots[id];d.classList.toggle('dim',!ids[id]||(!!st.sel&&id!==st.sel));d.classList.toggle('on',id===st.sel);});}
document.querySelectorAll('.gm-sizebar button').forEach(function(b){b.onclick=function(){st.size=b.dataset.size;document.querySelectorAll('.gm-sizebar button').forEach(function(x){x.setAttribute('aria-pressed',x===b);});layoutStrip();};});

/* scenario */
var goal=$('#gm-goal');function scen(){var g=parseFloat(goal.value),n=Math.max(0,Math.ceil(g/100*MI.d-MI.n));$('#gm-goal-v').textContent=g+'%';$('#gm-goal-n').textContent=fmt(n);
 $('#gm-goal-p').textContent=n>0?'to move Michigan\'s health centers from '+MI.r.toFixed(1)+'% to '+g+'%.':'Michigan\'s health centers are already at this level.';}
goal.addEventListener('input',scen);$('#gm-goal-reset').onclick=function(){goal.value=T;scen();};

/* export */
$('#gm-export').onclick=function(){ev('gapmap_export',{rows:filtered().length});var rows=[['health_center','also_known_as','city','setting','clinic_sites','rate_2025_pct','points_below_72_8','adults_screened','eligible_adults_46_75','more_adults_to_72_8']];
 sorted(filtered()).forEach(function(c){rows.push([c.name,c.aka||'',c.city,c.setting,c.nsites,c.pub?c.rate:'not published',c.pub?c.gap:'',c.pub?c.num:'',c.pub?c.den:'',c.pub?c.need:'']);});
 rows.push([]);rows.push(['Source: HRSA UDS 2025 (H80-2025, Table 6B), refreshed May 7, 2026. Target: Healthy People 2030 C-07, 72.8%. Calculations by HSREP; unpublished rates are never estimated. hsraep.org/gap-map']);
 var csv=rows.map(function(r){return r.map(function(v){v=String(v);return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}).join(',');}).join('\n');
 var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='hsrep-gap-map-michigan-2025.csv';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},500);};

/* hero */
setTimeout(function(){$('#gm-track-fill').style.width=MI.r.toFixed(1)+'%';},250);

render();renderCmp();layoutStrip();scen();
var m=(location.hash||'').match(/center=([a-z0-9-]+)/);if(m&&byId[m[1]])select(m[1]);
window.GM={select:select,clearSel:clearSel,tab:tab,cmp:function(){return st.cmp.slice();},setCmp:function(a){st.cmp=a.filter(function(x){return byId[x];}).slice(0,3);renderCmp();},goal:function(v){goal.value=v==null?T:v;scen();}};
}
if(window.GM_DATA)boot(window.GM_DATA);else fetch('/data/gapmap-2025.json').then(function(r){return r.json();}).then(boot);
})();
