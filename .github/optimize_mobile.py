from pathlib import Path
import re

p=Path('index.html')
s=p.read_text()

def rep(old,new,count=1,label='replacement'):
    global s
    if old not in s:
        raise SystemExit(f'Missing anchor: {label}')
    s=s.replace(old,new,count)

# 1. Zero-scroll mobile battle + landscape-only play overlay
css = r'''
/* =====================================================================
   04C. MOBILE GAME LOCK / LANDSCAPE / PERFORMANCE LAYOUT
   Battle pada telefon tidak dibenarkan scroll sama sekali.
   ===================================================================== */
#rotateOverlay{display:none}
body[data-screen="battle"],body[data-screen="battle"] main,body[data-screen="battle"] #battle{overflow:hidden!important}
body[data-screen="battle"] main{height:100%;min-height:0}
body[data-screen="battle"] #battle{height:100%;min-height:0}
body[data-screen="battle"] #battle>.shell{height:100%;min-height:0;overflow:hidden;display:grid;grid-template-rows:auto minmax(0,1fr) auto auto auto;align-content:stretch}
body[data-screen="battle"] .arena-wrap{min-height:0;display:grid;grid-template-rows:minmax(0,1fr) auto}
body[data-screen="battle"] #arena{height:100%;min-height:0}
body[data-screen="battle"] .question-grid{min-height:0;overflow:hidden}
body[data-screen="battle"] .q-card{min-height:0;overflow:hidden}
.stage.completed{border-color:#65d993;background:#123d35;position:relative}
.stage.completed::before{content:'✓';position:absolute;right:5px;top:2px;color:#9dffbd;font-weight:900;font-size:13px}
.stage.completed small{color:#9dffbd}
@media(max-width:900px){
  body[data-screen="battle"]>.topbar{display:none!important}
  body[data-screen="battle"] #battle>.shell{padding:5px 7px calc(5px + env(safe-area-inset-bottom,0px));grid-template-rows:auto minmax(100px,1fr) auto auto}
  body[data-screen="battle"] .battle-note{display:none!important}
  body[data-screen="battle"] .battle-head{padding:0 0 4px;min-height:34px;gap:5px}
  body[data-screen="battle"] .battle-head h2{font-size:17px;line-height:1.05}
  body[data-screen="battle"] .battle-head .muted{font-size:11px}
  body[data-screen="battle"] .battle-head .stat{font-size:12px}
  body[data-screen="battle"] .battle-head button{min-height:32px;padding:4px 8px;font-size:12px}
  body[data-screen="battle"] .arena-caption{padding:3px 7px;font-size:10px}
  body[data-screen="battle"] .mobile-tabs:not([hidden]){margin-top:4px;gap:5px}
  body[data-screen="battle"] .mobile-tabs button{min-height:30px;padding:3px 4px;font-size:11px}
  body[data-screen="battle"] .question-grid{margin-top:4px}
  body[data-screen="battle"] .q-card{padding:7px 9px}
  body[data-screen="battle"] .q-player{font-size:12px}
  body[data-screen="battle"] .lane-power{margin-top:3px;font-size:10px}
  body[data-screen="battle"] .q-label{font-size:10px;margin-top:2px}
  body[data-screen="battle"] .q-text{font-size:clamp(18px,4.6vw,25px);margin:4px 0;line-height:1.05}
  body[data-screen="battle"] .answers{gap:4px;grid-template-columns:repeat(4,1fr)!important}
  body[data-screen="battle"] .answer-choice{min-height:36px;padding:3px 2px;font-size:14px}
  body[data-screen="battle"] .answer-form{display:none}
  body[data-screen="battle"] .q-tools{margin-top:3px}
  body[data-screen="battle"] .q-tools button{min-height:30px;padding:3px 7px;font-size:11px}
  body[data-screen="battle"] .feedback{min-height:16px;margin-top:3px;font-size:11px;line-height:1.15}
  body[data-screen="battle"] .hint-text{font-size:10px;line-height:1.2;margin-top:2px;max-height:28px;overflow:hidden}
}
@media(max-width:900px) and (orientation:portrait){
  body[data-screen="battle"] #rotateOverlay{display:flex;position:fixed;inset:0;z-index:99999;background:#06121ff5;align-items:center;justify-content:center;text-align:center;padding:26px;color:white}
  #rotateOverlay .rotate-card{max-width:360px;padding:24px;border:1px solid #41657b;border-radius:20px;background:#0d2639;box-shadow:0 20px 60px #0008}
  #rotateOverlay .rotate-icon{font-size:64px;display:block;animation:rotateHint 1.5s ease-in-out infinite}
  #rotateOverlay strong{display:block;font-size:24px;color:var(--gold);margin:8px 0}
  #rotateOverlay p{color:var(--muted);font-size:14px}
  @keyframes rotateHint{50%{transform:rotate(90deg)}}
}
'''
rep('</style>',css+'\n</style>',label='mobile css')
rep('</body>','''<div id="rotateOverlay" aria-live="polite"><div class="rotate-card"><span class="rotate-icon">📱</span><strong>Putar telefon</strong><p>Permainan mobile direka untuk landscape supaya seluruh arena dan soalan muat dalam satu skrin tanpa scroll.</p></div></div>\n</body>''',label='rotate overlay')

# 2. Faster perceived loading
start=s.index('async function loadAssets(){')
end=s.index('/* =====================================================================\n   07.',start)
new_loader=r'''const CRITICAL_ASSETS=['boy','girl','background','world','ui','result','rewards','tutorial','vfx','basic'];
function loadAssetKey(key,priority='auto'){
 return new Promise(resolve=>{
  if(images[key]?.complete&&images[key].naturalWidth)return resolve(true);
  const file=ASSETS[key],img=new Image();let settled=false;
  img.decoding='async';
  try{img.fetchPriority=priority;}catch{}
  const finish=async ok=>{if(settled)return;settled=true;clearTimeout(timeout);if(ok){images[key]=img;try{await img.decode();}catch{}}resolve(ok);};
  const timeout=setTimeout(()=>finish(false),15000);
  img.onload=()=>finish(true);img.onerror=()=>finish(false);img.src=BASE+file;
 });
}
async function preloadRemainingAssets(){
 const rest=Object.keys(ASSETS).filter(k=>!CRITICAL_ASSETS.includes(k));
 for(const key of rest){await loadAssetKey(key,'low');$('#assetProgress').value=Math.min(20,+$('#assetProgress').value+1);}
 $('#assetLabel').textContent='Semua aset permainan telah dicache.';
}
async function loadAssets(){
 assetsReady=false;$('#mapBtn').disabled=true;$('#retryAssets').hidden=true;$('#assetProgress').max=20;$('#assetProgress').value=0;
 let done=0,failed=[];
 $('#assetLabel').textContent='Memuatkan aset penting…';
 await Promise.all(CRITICAL_ASSETS.map(async key=>{const ok=await loadAssetKey(key,'high');if(!ok)failed.push(key);$('#assetProgress').value=++done;$('#assetLabel').textContent=`Aset penting: ${done} / ${CRITICAL_ASSETS.length}`;}));
 assetsReady=failed.length===0;
 $('#mapBtn').disabled=!assetsReady;$('#resumeBtn').disabled=!assetsReady;
 if(!assetsReady){$('#assetLabel').textContent=`${failed.length} aset penting gagal dimuatkan. Cuba semula.`;$('#retryAssets').hidden=false;return;}
 $('#assetLabel').textContent='Aset utama siap — boleh mula. Aset lain sedang dicache…';
 const defer=()=>preloadRemainingAssets();
 if('requestIdleCallback' in window)requestIdleCallback(defer,{timeout:1200});else setTimeout(defer,250);
}
'''
s=s[:start]+new_loader+s[end:]

# 3. Stage-completed visual state
m=re.search(r"function renderWorld\(\)\{.*?\}\n(?=/\* =====================================================================\n   09\.)",s,re.S)
if not m: raise SystemExit('renderWorld not found')
new_render=r'''function renderWorld(){const chapters=['Zombie Street','Dark Lab','Ice Zone','Boss Kingdom'];$('#stageGrid').innerHTML=Array.from({length:20},(_,i)=>{const n=i+1,s=save.stars[n]||0,done=s>0,locked=n>save.unlocked,current=n===save.unlocked&&!done;return `<button class="stage ${BOSS[n]?'boss':''} ${done?'completed':''} ${current?'current':''}" data-stage="${n}" ${locked?'disabled':''} aria-label="Stage ${n}${done?', selesai':''}${BOSS[n]?', bos '+KINDS[BOSS[n]].name:''}${locked?', dikunci':''}"><b>${locked?'🔒':n}</b><small>${done?'✓ '+'★'.repeat(s):BOSS[n]?'BOS':current?'NEXT':'·'}</small></button>`;}).join('');const doneCount=Object.values(save.stars).filter(v=>Number(v)>0).length;$('#worldSummary').textContent=`${doneCount} stage selesai · ${save.unlocked} / 20 stage dibuka · ${chapters[Math.min(3,Math.floor((save.unlocked-1)/5))]}`;updateTotals();}
'''
s=s[:m.start()]+new_render+s[m.end():]

# 4. Canvas performance
rep("const canvas=$('#arena'),ctx=canvas.getContext('2d');let W=1000,H=350,laneH=350;const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;",
    "const canvas=$('#arena'),ctx=canvas.getContext('2d',{alpha:false});let W=1000,H=350,laneH=350,lastDraw=0;const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;const bgCache=document.createElement('canvas'),bgCtx=bgCache.getContext('2d',{alpha:false});",
    label='canvas vars')

m=re.search(r"function resizeCanvas\(\)\{.*?\}\nfunction drawCrop",s,re.S)
if not m: raise SystemExit('resizeCanvas block not found')
new_resize=r'''function rebuildBackgroundCache(){const bg=images.background;if(!bg||!W||!H)return;bgCache.width=Math.max(1,Math.round(W));bgCache.height=Math.max(1,Math.round(H));const iw=bg.naturalWidth,ih=bg.naturalHeight,r=Math.max(W/iw,H/ih);bgCtx.fillStyle='#13273b';bgCtx.fillRect(0,0,W,H);bgCtx.drawImage(bg,(W-iw*r)/2,(H-ih*r)/2,iw*r,ih*r);bgCtx.fillStyle='#05172870';bgCtx.fillRect(0,0,W,H);}
function resizeCanvas(){if(screen!=='battle')return;W=Math.max(280,canvas.parentElement.clientWidth);const n=run?.lanes.length||1;const caption=$('.arena-caption')?.offsetHeight||24;const parentH=canvas.parentElement.clientHeight;const available=Math.max(100,parentH-caption);H=available;laneH=H/n;const mobile=W<900;const dpr=mobile?1:Math.min(devicePixelRatio||1,1.5);canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);canvas.style.height=H+'px';ctx.setTransform(dpr,0,0,dpr,0,0);rebuildBackgroundCache();}
function drawCrop'''
s=s[:m.start()]+new_resize+s[m.end():]

rep("function geom(lane){const mobile=W<600,n=run.lanes.length,ground=laneH*(lane.index+1)-16;const heroH=n===1?(mobile?172:235):(mobile?(n===3?68:88):116);",
    "function geom(lane){const mobile=W<600,n=run.lanes.length,ground=laneH*(lane.index+1)-10;const baseHero=n===1?(mobile?172:235):(mobile?(n===3?68:88):116);const heroH=Math.max(48,Math.min(baseHero,laneH*.78));",
    label='dynamic hero size')

rep("function drawArena(time){if(!run)return;ctx.clearRect(0,0,W,H);const bg=images.background;if(bg){const iw=bg.naturalWidth,ih=bg.naturalHeight,r=Math.max(W/iw,H/ih);ctx.drawImage(bg,(W-iw*r)/2,(H-ih*r)/2,iw*r,ih*r);}ctx.fillStyle='#05172870';ctx.fillRect(0,0,W,H);",
    "function drawArena(time){if(!run)return;ctx.clearRect(0,0,W,H);if(bgCache.width&&bgCache.height)ctx.drawImage(bgCache,0,0,W,H);else{ctx.fillStyle='#13273b';ctx.fillRect(0,0,W,H);}",
    label='cached background draw')

m=re.search(r"function frame\(now\)\{.*?requestAnimationFrame\(frame\);\}",s,re.S)
if not m: raise SystemExit('frame not found')
s=s[:m.start()]+"function frame(now){const dt=lastFrame?Math.min((now-lastFrame)/1000,.1):0;lastFrame=now;if(screen==='battle'){tick(dt);const minFrame=W<900?22:16;if(now-lastDraw>=minFrame){drawArena(now/1000);lastDraw=now;}}requestAnimationFrame(frame);}"+s[m.end():]

# Reduce frequent localStorage work
rep("function checkpoint(){if(run?.active)save.snapshot=JSON.parse(JSON.stringify(run));persist();}",
    "let checkpointTimer=0;function checkpoint(){if(run?.active)save.snapshot=JSON.parse(JSON.stringify(run));persist();}function scheduleCheckpoint(){clearTimeout(checkpointTimer);checkpointTimer=setTimeout(()=>checkpoint(),900);}",
    label='checkpoint debounce')
s=s.replace("updatePanelState(lane);updateHUD();checkpoint();\n}","updatePanelState(lane);updateHUD();scheduleCheckpoint();\n}",1)
s=s.replace("updatePanelState(l);checkpoint();}","updatePanelState(l);scheduleCheckpoint();}",1)
s=s.replace("if(saveTick>=5){saveTick=0;checkpoint();}","if(saveTick>=12){saveTick=0;checkpoint();}",1)

# If background finishes after a resize, refresh the cache.
s=s.replace("if(ok){images[key]=img;try{await img.decode();}catch{}}resolve(ok);",
            "if(ok){images[key]=img;try{await img.decode();}catch{}if(key==='background'&&screen==='battle')rebuildBackgroundCache();}resolve(ok);",1)

p.write_text(s)
