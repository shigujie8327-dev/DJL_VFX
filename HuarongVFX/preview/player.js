const stage=document.getElementById('stage'), effects=document.getElementById('effects'), label=document.getElementById('event-label');
const assets=new Map(window.HR_MANIFEST.assets.map(a=>[a.id,a]));
let run=0, live=[];
const z={BattleFX_Back:1,Status_Back:2,WeaponTrail:4,SkillFX:5,Projectile:6,HitFX:7,Status_Front:8};
const anchors={Caster_WeaponPoint:[.245,.55],Caster_PassivePoint:[.23,.61],Target_HitPoint:[.75,.54],Target_FeetPoint:[.75,.73],Attack_MidPoint:[.5,.55]};
function clear(){run++;for(const v of live)v.remove();live=[];effects.replaceChildren();}
function stopTag(tag){for(const v of live.filter(v=>v.dataset.tag===tag))v.remove();live=live.filter(v=>v.dataset.tag!==tag);}
function emit(name){const entry=window.HR_EVENTS.events[name];if(!entry)throw Error(name);for(const t of entry.stopTags||[])stopTag(t);for(const c of entry.cues){const a=assets.get(c.asset);const img=document.createElement('img');img.src='../'+a.file;img.alt='';img.dataset.tag=c.tag||'';img.style.zIndex=z[a.layer]||5;effects.append(img);live.push(img);const token=run;const delay=(c.start||0)*1000;setTimeout(()=>{if(token!==run||!img.isConnected)return;const begin=performance.now();const animate=now=>{if(token!==run||!img.isConnected)return;const age=(now-begin)/1000,p=Math.min(1,age/c.duration),ease=1-(1-p)**3;const k=c.loop?Math.min(1,age/.12):Math.min(1,p*10)*Math.pow(1-p,.68);const [ax,ay]=anchors[c.anchor];const sx=stage.clientWidth/1920,sy=stage.clientHeight/1080;const x=ax*stage.clientWidth+(c.x+c.dx*ease)*sx,y=ay*stage.clientHeight+(c.y+c.dy*ease)*sy;img.style.width=`${c.w*sx}px`;img.style.height=`${c.h*sy}px`;img.style.left=`${x}px`;img.style.top=`${y}px`;img.style.opacity=(c.alpha*k).toFixed(3);img.style.transform=`translate(-50%,-50%) rotate(${c.rotation||0}deg) scale(${c.scaleFrom+(c.scaleTo-c.scaleFrom)*ease})`;if(c.loop||p<1)requestAnimationFrame(animate);else{img.remove();live=live.filter(v=>v!==img);}};requestAnimationFrame(animate);},delay);}}
const demos=[
 ['连珠箭','huarong-01_lianzhu_jian.png',()=>{emit('LianzhuJian.Cast');for(let i=0;i<4;i++){at(.11+i*.15,()=>emit('LianzhuJian.Shot'));at(.25+i*.15,()=>emit(`LianzhuJian.Hit${i+1}`));}}],
 ['穿云箭','huarong-02_chuanyun_jian.png',()=>{emit('ChuanyunJian.Cast');at(.16,()=>emit('ChuanyunJian.Shot'));at(.34,()=>emit('ChuanyunJian.Hit'));}],
 ['退身箭 · 成功','huarong-03_tuishen_jian.png',()=>retreat(false)],
 ['退身箭 · 受阻','huarong-03_tuishen_jian.png',()=>retreat(true)],
 ['定身箭','huarong-04_dingshen_jian.png',()=>{emit('DingshenJian.Cast');at(.13,()=>emit('DingshenJian.Shot'));at(.31,()=>emit('DingshenJian.Hit'));at(.4,()=>emit('DingshenJian.Apply'));at(.9,()=>emit('DingshenJian.CostPulse'));at(1.6,()=>emit('DingshenJian.Expire'));}],
 ['小李广','huarong-05_xiaoliguang.png',()=>{emit('XiaoLiGuang.EnterFar');at(1.25,()=>emit('XiaoLiGuang.LeaveFar'));}]
];
function retreat(blocked){emit('TuishenJian.Cast');at(.12,()=>emit('TuishenJian.Shot'));at(.30,()=>emit('TuishenJian.Hit'));at(.38,()=>emit(blocked?'TuishenJian.RetreatBlocked':'TuishenJian.RetreatSuccess'));}
function at(t,fn){const token=run;setTimeout(()=>{if(token===run)fn();},t*1000);}
const buttons=document.getElementById('buttons');demos.forEach(([name,icon,play])=>{const b=document.createElement('button');b.innerHTML=`<img src="../Characters/Huarong/UI/${icon}" alt=""><span>${name}</span>`;b.addEventListener('click',()=>{clear();label.textContent=name;play();});buttons.append(b);});
