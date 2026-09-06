import subprocess, re
from pathlib import Path

BASE_COMMIT = '13bb9a418b2e283bfadc7b7bd3783e280d4377e8'
p = Path('index.html')
s = subprocess.check_output(['git','show',f'{BASE_COMMIT}:index.html'], text=True)

def rep(old, new, count=1, label='replacement'):
    global s
    if old not in s:
        raise SystemExit(f'Missing anchor for {label}')
    s = s.replace(old, new, count)

rep('<meta name="viewport" content="width=device-width, initial-scale=1">',
    '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">', label='viewport')

extra_css = r'''
/* =====================================================================
   04B. PENAMBAHBAIKAN: FULLSCREEN / MOBILE / POWER / MAP NEXT
   Tidak mengubah struktur asal permainan.
   ===================================================================== */
html,body{min-height:100%;overscroll-behavior:none}
body[data-screen="battle"]{height:100dvh;overflow:hidden;display:flex;flex-direction:column}
body[data-screen="battle"]>.topbar{flex:0 0 auto}
body[data-screen="battle"] main{flex:1 1 auto;min-height:0;overflow:auto}
body[data-screen="battle"] #battle{width:100%;max-width:none;min-height:100%;padding:0}
body[data-screen="battle"] #battle>.shell{width:100%;max-width:none;padding:10px 12px calc(10px + env(safe-area-inset-bottom,0px))}
body[data-screen="battle"] .arena-wrap{width:100%}
#fullscreenBtn{white-space:nowrap}
.lane-power{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:7px;margin-top:8px;font-size:12px;color:var(--muted);font-weight:800}
.lane-power-track{height:9px;border-radius:999px;background:#071827;border:1px solid #41657b;overflow:hidden}
.lane-power-track i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--accent),#8dffa8,var(--gold));transition:width .2s}
.lane-power b{min-width:34px;text-align:right;color:var(--gold)}
.stage.current{position:relative;overflow:visible;animation:nextStagePulse 1.6s ease-in-out infinite}
.stage.current::after{content:'➜ NEXT';position:absolute;left:50%;top:-19px;transform:translateX(-50%);font-size:10px;line-height:1;white-space:nowrap;color:var(--gold);font-weight:900;text-shadow:0 1px 4px #000;pointer-events:none}
@keyframes nextStagePulse{50%{box-shadow:0 0 0 3px var(--accent),0 0 18px #73eafa88}}
@media(max-width:800px){
 body[data-screen="battle"] .topbar{padding-top:max(7px,env(safe-area-inset-top,0px));}
 body[data-screen="battle"] #battle>.shell{padding:7px 8px calc(8px + env(safe-area-inset-bottom,0px))}
 body[data-screen="battle"] .battle-head{gap:7px;margin-bottom:4px}
 body[data-screen="battle"] .battle-head h2{font-size:19px}
 body[data-screen="battle"] .arena-caption{font-size:11px;padding:5px 9px}
 body[data-screen="battle"] .question-grid{margin-top:8px}
 body[data-screen="battle"] .q-card{padding:11px}
 body[data-screen="battle"] .q-text{font-size:clamp(20px,6vw,29px);margin:8px 0}
 body[data-screen="battle"] .answer-choice{min-height:44px;font-size:16px}
 body[data-screen="battle"] .battle-note{display:none}
 .stage.current::after{top:-16px;font-size:9px}
}
@media(max-width:430px){
 #fullscreenBtn{font-size:0;min-width:40px;padding:7px 9px}
 #fullscreenBtn::after{content:'⛶';font-size:18px}
 body[data-screen="battle"] .topbar{padding-left:8px;padding-right:8px}
}
'''
rep('</style>', extra_css + '\n</style>', label='enhancement css')

rep('<button id="soundBtn" class="small ghost" aria-pressed="false">Bunyi: tutup</button><button id="helpBtn" class="small ghost">Cara main</button>',
    '<button id="fullscreenBtn" class="small ghost" type="button">Skrin penuh</button><button id="soundBtn" class="small ghost" aria-pressed="true">Bunyi: buka</button><button id="helpBtn" class="small ghost">Cara main</button>', label='header controls')

rep('<span class="badge combo-label">Combo 0</span></div><div class="q-label"></div>',
    '<span class="badge combo-label">Combo 0</span></div><div class="lane-power"><span>⚡ Power</span><div class="lane-power-track"><i></i></div><b>0%</b></div><div class="q-label"></div>', label='lane power ui')

rep('combo:0,best:0,skill:0,recent:[]', 'combo:0,best:0,power:0,skill:0,recent:[]', label='lane power state')

audio_engine = r'''/* =====================================================================
   16. AUDIO FAIL GITHUB /sound
   Nama fail ialah canonical event mapping permainan.
   ===================================================================== */
const SOUND_BASE='./sound/';
const SOUND_FILES={
 bgm:'bgm_math_defenders_main_theme.wav',correct:'sfx_answer_correct.wav',wrong:'sfx_answer_wrong.wav',blaster:'sfx_blaster_shot.wav',
 bossDefeat:'sfx_boss_defeat.wav',bossHit:'sfx_boss_hit.wav',bossIntro:'sfx_boss_intro.wav',bossWarning:'sfx_boss_warning.wav',
 coin:'sfx_coin_pickup.wav',comboBig:'sfx_combo_big.wav',comboUp:'sfx_combo_up.wav',defeat:'sfx_defeat.wav',heroHit:'sfx_hero_hit.wav',
 heroVictory:'sfx_hero_victory.wav',hint:'sfx_hint.wav',levelUp:'sfx_level_up.wav',mathPower:'sfx_math_power.wav',impact:'sfx_projectile_impact.wav',
 rapidFire:'sfx_rapid_fire.wav',rewardChest:'sfx_reward_chest.wav',stageClear:'sfx_stage_clear.wav',click:'sfx_ui_click.wav',victory:'sfx_victory.wav',
 xp:'sfx_xp_gain.wav',zombieAttack:'sfx_zombie_attack.wav',zombieDefeat:'sfx_zombie_defeat.wav',zombieHit:'sfx_zombie_hit_01.wav',
 zombieHitHeavy:'sfx_zombie_hit_heavy.wav',zombieWalk:'sfx_zombie_walk_loop.wav'
};
let sound=true;
const sfxCache={};
let bgmAudio=null,zombieWalkAudio=null,audioPrimed=false;
function initGameAudio(){for(const [k,f] of Object.entries(SOUND_FILES)){if(k==='bgm'||k==='zombieWalk')continue;const a=new Audio(SOUND_BASE+f);a.preload='auto';sfxCache[k]=a;}bgmAudio=new Audio(SOUND_BASE+SOUND_FILES.bgm);bgmAudio.loop=true;bgmAudio.volume=.20;zombieWalkAudio=new Audio(SOUND_BASE+SOUND_FILES.zombieWalk);zombieWalkAudio.loop=true;zombieWalkAudio.volume=.10;}
function playSfx(name,volume=.65){if(!sound||!sfxCache[name])return;try{const a=sfxCache[name].cloneNode();a.volume=clamp(volume,0,1);a.play().catch(()=>{});}catch{}}
function syncAudioScene(){if(!sound){bgmAudio?.pause();zombieWalkAudio?.pause();return;}bgmAudio?.play().catch(()=>{});if(screen==='battle'&&run?.active&&!paused)zombieWalkAudio?.play().catch(()=>{});else zombieWalkAudio?.pause();}
function primeAudio(){if(audioPrimed)return;audioPrimed=true;syncAudioScene();}
function tone(kind){if(!sound)return;const map={shot:'blaster',wrong:'wrong',hit:'impact',hurt:'heroHit',boss:'bossWarning',team:'rapidFire',win:'victory'};if(map[kind])playSfx(map[kind],kind==='boss'||kind==='win'?.82:.62);}
const WRONG_ANSWER_STEP=.055;
'''
s, n = re.subn(r"/\* =====================================================================\n   16\. BUNYI RINGKAS.*?function tone\(kind\)\{.*?\}\n(?=/\* =====================================================================\n   17\.)", audio_engine, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not replace legacy audio section')

rep("function startStage(stage){if(!assetsReady||stage>save.unlocked)return;save.snapshot=null;", "function startStage(stage){if(!assetsReady||stage>save.unlocked)return;primeAudio();save.snapshot=null;", label='start audio on stage')
rep("if(boss){announce('BOS: '+def.name,3);tone('boss');}renderQuestion(lane);}", "if(boss){announce('BOS: '+def.name,3);tone('boss');setTimeout(()=>playSfx('bossIntro',.82),500);}renderQuestion(lane);}", label='boss audio')

new_submit = r'''function submitAnswer(index,value){const lane=run?.lanes[index];if(!lane||!canAnswer(lane))return;const answer=parseAnswer(value);if(!Number.isFinite(answer)){lane.feedback='Masukkan nombor, perpuluhan atau pecahan yang sah.';updatePanelState(lane);return;}const q=lane.q;const topicStats=lane.topicStats[q.topic]||(lane.topicStats[q.topic]={correct:0,wrong:0});q.attempts++;
 if(Math.abs(answer-q.answer)<1e-6){lane.stats.correct++;topicStats.correct++;lane.stats.time+=q.elapsed;lane.combo++;lane.best=Math.max(lane.best,lane.combo);updateAdaptive(lane,true);lane.teamReady=true;
  const firstTry=q.attempts===1;let quickMult=1,powerGain=8,quickLabel='';
  if(firstTry&&q.elapsed<=3){quickMult=2;powerGain=30;quickLabel='PERFECT QUICK · 2×';}
  else if(firstTry&&q.elapsed<=5){quickMult=1.5;powerGain=18;quickLabel='QUICK BONUS · 1.5×';}
  lane.power=clamp((lane.power||0)+powerGain,0,100);let damage=comboDamage(lane.combo)*quickMult;let powerShot=false;
  if(lane.power>=100){lane.power=0;damage+=2;powerShot=true;playSfx('mathPower',.9);setTimeout(()=>playSfx('rapidFire',.72),100);quickLabel='MATH POWER!';}
  playSfx('correct',.5);if(lane.combo===3)playSfx('comboUp',.6);if(lane.combo===5||lane.combo===10)playSfx('comboBig',.72);
  lane.feedback=`Betul! ${quickLabel?quickLabel+' · ':''}${lane.combo>=3?'Combo '+lane.combo+'! ':''}Blaster dilepaskan.`;shoot(lane,damage,true,powerShot);tone('shot');
  if(run.lanes.length>1&&run.lanes.every(l=>l.teamReady)){run.lanes.forEach(l=>{l.teamReady=false;if(l.enemy?.state==='walk')shoot(l,1,false,false);});announce('SERANGAN PASUKAN!',2.5);tone('team');}}
 else{lane.stats.wrong++;topicStats.wrong++;lane.combo=0;lane.teamReady=false;updateAdaptive(lane,false);if(lane.enemy?.state==='walk')lane.enemy.progress=Math.min(.94,lane.enemy.progress+WRONG_ANSWER_STEP);lane.feedback='Belum tepat. Zombi mara satu langkah! Cuba lagi, soalan masih sama.';q.draft='';tone('wrong');}
 updatePanelState(lane);updateHUD();checkpoint();
}
function useHint'''
s, n = re.subn(r"function submitAnswer\(index,value\)\{.*?\n\}\nfunction useHint", new_submit, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not replace submitAnswer')

rep("function useHint(index){const l=run?.lanes[index];if(!l||!canAnswer(l))return;if(!l.q.hinted){l.q.hinted=true;l.stats.hints++;}updatePanelState(l);checkpoint();}", "function useHint(index){const l=run?.lanes[index];if(!l||!canAnswer(l))return;if(!l.q.hinted){l.q.hinted=true;l.stats.hints++;playSfx('hint',.5);}updatePanelState(l);checkpoint();}", label='hint sound')
rep("function shoot(lane,damage,main){lane.shoot=.38;lane.bullets.push({enemyId:lane.enemy.id,progress:0,damage,main,delay:main?0:.17});lane.fx.push({type:'muzzle',life:.23,max:.23,at:0});}", "function shoot(lane,damage,main,powerShot=false){lane.shoot=.38;lane.bullets.push({enemyId:lane.enemy.id,progress:0,damage,main,powerShot,delay:main?0:.17});lane.fx.push({type:'muzzle',life:.23,max:.23,at:0});}", label='power projectile state')
rep("lane.fx.push({type:'impact',life:.55,max:.55,at:z.progress,label:'−'+bullet.damage});tone('hit');if(z.hp===0){", "lane.fx.push({type:'impact',life:.55,max:.55,at:z.progress,label:'−'+bullet.damage});tone('hit');playSfx(KINDS[z.kind].boss?'bossHit':(bullet.damage>=2?'zombieHitHeavy':'zombieHit'),.7);if(z.hp===0){playSfx(KINDS[z.kind].boss?'bossDefeat':'zombieDefeat',.82);playSfx('coin',.4);", label='impact sounds')
rep("function breach(lane){const z=lane.enemy;if(!z||z.state!=='walk')return;run.hp=Math.max(0,run.hp-1);", "function breach(lane){const z=lane.enemy;if(!z||z.state!=='walk')return;playSfx('zombieAttack',.72);run.hp=Math.max(0,run.hp-1);", label='zombie attack sound')
rep("for(const b of l.bullets){if(b.delay>0)continue;const x=g.muzzleX+b.progress*g.span;const size=b.main?64:85;drawArt('bullet',x-size*.65,g.muzzleY-20,size,42);}", "for(const b of l.bullets){if(b.delay>0)continue;const x=g.muzzleX+b.progress*g.span;const size=b.powerShot?105:(b.main?64:85);drawArt('bullet',x-size*.65,g.muzzleY-(b.powerShot?30:20),size,b.powerShot?62:42);}", label='power projectile visual')
rep("root.querySelector('.feedback').textContent=l.feedback;root.querySelector('.combo-label').textContent='Combo '+l.combo;root.querySelector('.lane-progress').textContent=", "root.querySelector('.feedback').textContent=l.feedback;root.querySelector('.combo-label').textContent='Combo '+l.combo;const power=clamp(Number(l.power)||0,0,100);const powerBar=root.querySelector('.lane-power i');const powerText=root.querySelector('.lane-power b');if(powerBar)powerBar.style.width=power+'%';if(powerText)powerText.textContent=Math.round(power)+'%';root.querySelector('.lane-progress').textContent=", label='power ui update')
rep("$('#nextStage').hidden=!won||run.stage>=20;show('result');tone(won?'win':'hurt');}", "$('#nextStage').hidden=!won||run.stage>=20;show('result');if(won){playSfx('stageClear',.76);setTimeout(()=>playSfx('victory',.82),180);setTimeout(()=>playSfx('heroVictory',.65),330);if(run.xp>0)playSfx('xp',.42);}else{playSfx('defeat',.76);}tone(won?'win':'hurt');syncAudioScene();}", label='result sounds')
rep("run.lanes.forEach(l=>{questionId=Math.max(questionId,l.q?.id||0);enemyId=Math.max(enemyId,l.enemy?.id||0);});paused=true;", "run.lanes.forEach(l=>{if(!Number.isFinite(l.power))l.power=0;questionId=Math.max(questionId,l.q?.id||0);enemyId=Math.max(enemyId,l.enemy?.id||0);});paused=true;", label='restore power default')
rep("function show(id){screen=id;document.body.dataset.screen=id;$$('.screen').forEach(el=>el.hidden=el.id!==id);window.scrollTo({top:0,behavior:'instant'});if(id==='battle'){resizeCanvas();updateHUD();}}", "function show(id){screen=id;document.body.dataset.screen=id;$$('.screen').forEach(el=>el.hidden=el.id!==id);window.scrollTo({top:0,behavior:'instant'});if(id==='battle'){resizeCanvas();updateHUD();}syncAudioScene();}", label='scene audio sync')
rep("$('#resultMap').onclick=()=>{renderWorld();show('world');};$('#replay').onclick=()=>startStage(run.stage);$('#nextStage').onclick=()=>startStage(run.stage+1);$('#soundBtn').onclick=()=>{sound=!sound;$('#soundBtn').textContent='Bunyi: '+(sound?'buka':'tutup');$('#soundBtn').setAttribute('aria-pressed',String(sound));if(sound)tone('team');};$('#retryAssets').onclick=loadAssets;", "$('#resultMap').onclick=()=>{renderWorld();show('world');};$('#replay').onclick=()=>startStage(run.stage);$('#nextStage').onclick=()=>startStage(run.stage+1);$('#soundBtn').onclick=()=>{sound=!sound;$('#soundBtn').textContent='Bunyi: '+(sound?'buka':'tutup');$('#soundBtn').setAttribute('aria-pressed',String(sound));if(sound){primeAudio();playSfx('click',.35);}syncAudioScene();};$('#fullscreenBtn').onclick=async()=>{playSfx('click',.35);try{if(document.fullscreenElement)await document.exitFullscreen();else if(document.documentElement.requestFullscreen)await document.documentElement.requestFullscreen();}catch{}};$('#retryAssets').onclick=loadAssets;", label='sound/fullscreen handlers')
rep("readSave();renderPlayers();renderTopics();fillArt();updateTotals();", "initGameAudio();document.addEventListener('pointerdown',()=>{primeAudio();syncAudioScene();},{once:true});readSave();renderPlayers();renderTopics();fillArt();updateTotals();", label='audio boot')

p.write_text(s, encoding='utf-8')
print('Patched index.html:', len(s), 'bytes')
