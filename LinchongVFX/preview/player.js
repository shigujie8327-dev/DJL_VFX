const canvas=document.querySelector('#stage'),ctx=canvas.getContext('2d');
const $=id=>document.getElementById(id),images={},metadata=Object.fromEntries(VFX_MANIFEST.assets.map(a=>[a.id,a]));
const query=new URLSearchParams(location.search);
const initialSkill=VFX_SKILLS[query.get('skill')]?query.get('skill'):'Jifengci';
const state={skill:initialSkill,branch:initialSkill==='Jifengci'?'interrupt':VFX_SKILLS[initialSkill].branches[0][0],t:0,playing:true,speed:1,background:'dark',guides:true,loop:true};
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),ease=x=>1-(1-clamp(x))**3;
let loaded=false,last=performance.now();
function activeClip(){return VFX_CLIPS[state.skill+'.'+state.branch]}
function text(t,x,y,size=20,color='#9ea9a3',align='left'){ctx.font=`${size}px "Microsoft YaHei", sans-serif`;ctx.fillStyle=color;ctx.textAlign=align;ctx.fillText(t,x,y);}
function path(points,color,width=1){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
function ellipse(x,y,rx,ry,color,w=1){ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.strokeStyle=color;ctx.lineWidth=w;ctx.stroke();}
function sprite(id,x,y,w,h,alpha=1,rot=0,reveal=1,mirrorX=false){const im=images[id];if(!im||!alpha)return;ctx.save();ctx.translate(x,y);ctx.rotate(rot*Math.PI/180);ctx.scale(mirrorX?-1:1,1);ctx.globalAlpha=clamp(alpha);if(reveal<1){ctx.beginPath();ctx.rect(-w/2,-h/2,w*clamp(reveal),h);ctx.clip();}ctx.drawImage(im,-w/2,-h/2,w,h);ctx.restore();}
function micro(t,start,duration,amount){let p=(t-start)/duration;return p>0&&p<1?Math.sin(p*Math.PI*2)*amount:0;}
function anchors(t){
 let caster=0,target=0,dist=0;
 if(state.skill==='Jifengci')caster=micro(t,.28,.40,18);
 if(state.skill==='Huimaqiang')caster=micro(t,.55,.66,-16);
 if(state.skill==='Hengsaoqianjun'){caster=micro(t,.2,.88,-21);if(state.branch==='push')dist=-150*ease((t-.78)/.3);}
 const hit=activeClip().events.find(e=>e.kind==='damage');if(hit)target=micro(t,hit.t,.20,12);
 if(state.skill==='Qiangzhen'&&state.branch==='block'){target-=55*Math.sin(Math.PI*clamp((t-1.18)/.4));}
 const left=state.skill==='Hengsaoqianjun',casterX=left?1300:660,targetX=left?740:1220;
 return {Caster_WeaponPoint:[casterX+(left?-80:80)+caster,585],Target_HitPoint:[targetX+dist+target,585],Ground:[930,800],Caster_PassivePoint:[casterX+(left?66:-66)+caster,380],Attack_MidPoint:[970+caster/2,585],casterX,caster,dist};
}
function drawScene(t,a){
 const light=state.background==='light';
 if(state.background==='grid'){ctx.fillStyle='#333d40';ctx.fillRect(0,0,1920,1080);ctx.fillStyle='#414d50';for(let y=0;y<1080;y+=40)for(let x=0;x<1920;x+=40)if((x/40+y/40)%2===0)ctx.fillRect(x,y,40,40);}
 else{const g=ctx.createRadialGradient(950,560,80,950,560,1050);g.addColorStop(0,light?'#ece9df':'#263234');g.addColorStop(1,light?'#c9c7bd':'#0d1416');ctx.fillStyle=g;ctx.fillRect(0,0,1920,1080);}
 const line=light?'#adae9e':'#344243';
 ctx.save();ctx.globalAlpha=.35;
 for(let i=0;i<11;i++)path([[210+i*150,910],[670+i*57,680]],line);
 for(let i=0;i<6;i++)path([[200,695+i*i*8],[1730,695+i*i*8]],line);
 ctx.restore();
 text('LIN CHONG  /  COMBAT VFX',65,73,19,light?'#6a7069':'#91a09c');
 text('斗 将 录',1850,73,19,light?'#6a7069':'#91a09c','right');
 text(VFX_SKILLS[state.skill].subtitle,65,116,12,light?'#898d81':'#596e6b');
 ctx.save();ctx.globalAlpha=.035;text('枪',1600,650,440,light?'#000':'#ede3c8','center');ctx.restore();
 const far=state.skill==='Qiangzhen'||(state.skill==='Hengsaoqianjun'&&state.branch==='push'&&t>=.78);
 ctx.fillStyle=light?'#bdbfb3':'#263333';ctx.fillRect(826,123,270,42);text(far?'FAR  ·  远距':'NEAR  ·  近距',960,151,17,light?'#4b5753':'#d7cfb8','center');
 ellipse(a.casterX+a.caster,806,137,33,line,2);ellipse(a.Target_HitPoint[0],806,115,28,line,2);
 if(state.guides){
  stand(a.casterX+a.caster,805,false,light,state.skill==='Hengsaoqianjun');stand(a.Target_HitPoint[0],805,true,light);
  const c=light?'#68746c':'#71847f';
  text('林冲 / 施放端',a.casterX+a.caster,866,19,c,'center');text('敌方 / 受击端',a.Target_HitPoint[0],866,19,c,'center');
  for(const [name,p] of Object.entries(a)){if(!Array.isArray(p)||name==='Attack_MidPoint')continue;ctx.save();ctx.globalAlpha=.35;path([[p[0]-7,p[1]],[p[0]+7,p[1]]],c);path([[p[0],p[1]-7],[p[0],p[1]+7]],c);ctx.restore();}
 }
 const event=activeClip().events.filter(e=>e.t<=t).at(-1);
 ctx.fillStyle=light?'#d7d6ca':'#111b1e';ctx.fillRect(65,938,1790,88);
 ctx.fillStyle=VFX_SKILLS[state.skill].color;ctx.fillRect(65,938,3,88);
 text(VFX_SKILLS[state.skill].name,92,992,28,light?'#383f3a':'#eee4cd');
 text(event?.label||'准备',370,990,21,light?'#54645c':'#acbcb7');
 text(t.toFixed(2)+' s',1805,990,20,light?'#637269':'#7d948c','right');
}
function stand(x,y,target,light,facingLeft=false){
 const c=light?'#7a8070':'#62726d',fill=light?'#d4d4c5':'#202c2d';
 ctx.save();ctx.globalAlpha=.55;
 ctx.fillStyle=fill;ctx.strokeStyle=c;ctx.lineWidth=2;
 if(target){
  ctx.beginPath();ctx.moveTo(x,y-365);ctx.lineTo(x+65,y-316);ctx.lineTo(x+56,y-150);ctx.lineTo(x,y-113);ctx.lineTo(x-56,y-150);ctx.lineTo(x-65,y-316);ctx.closePath();ctx.fill();ctx.stroke();
  ellipse(x,y-220,33,45,c,2);ellipse(x,y-220,10,14,c,2);path([[x,y-112],[x,y-12]],c,6);path([[x-65,y],[x+65,y]],c,4);
 }else{
  path([[x-65,y-12],[x-34,y-265],[x,y-350],[x+34,y-265],[x+65,y-12]],c,2);
  const d=facingLeft?-1:1;path([[x-35*d,y-220],[x+160*d,y-220]],c,5);path([[x+160*d,y-220],[x+195*d,y-230],[x+177*d,y-218],[x+195*d,y-208],[x+160*d,y-220]],'#9eada4',2);
  path([[x-45,y-145],[x+45,y-145]],c,2);text('林',x,y-255,34,c,'center');
 }ctx.restore();
}
function paintCue(c,t,a){
 let p=(t-c.start)/c.duration;if(p<0||p>=1)return;
 const anchor=a[c.anchor];if(!anchor)return;
 const motion=c.motion==='smooth'?p*p*(3-2*p):c.motion==='in'?p*p:ease(p);
 let env=c.envelope==='transfer'?Math.min(1,p*20,(1-p)*20):c.envelope==='hold'?Math.min(1,p*15,(1-p)*15):Math.min(1,p*9)*Math.pow(1-p,.65);
 let scale=c.scaleFrom+(c.scaleTo-c.scaleFrom)*motion;
 let x=anchor[0]+c.x+c.dx*motion,y=anchor[1]+c.y+c.dy*motion;
 let angle=c.rotation+c.spin*(c.rotationEase?motion:p);
 if(c.curve){const start=[anchor[0]+c.x,anchor[1]+c.y],control=[anchor[0]+c.curve.control[0],anchor[1]+c.curve.control[1]],dest=a[c.curve.endAnchor],end=[dest[0]+c.curve.endOffset[0],dest[1]+c.curve.endOffset[1]],q=motion,u=1-q;
  x=u*u*start[0]+2*u*q*control[0]+q*q*end[0];y=u*u*start[1]+2*u*q*control[1]+q*q*end[1];
  if(c.orientToPath)angle=Math.atan2(2*u*(control[1]-start[1])+2*q*(end[1]-control[1]),2*u*(control[0]-start[0])+2*q*(end[0]-control[0]))*180/Math.PI;
 }
 sprite(c.asset,x,y,c.w*scale,c.h*scale,c.alpha*env,angle,c.reveal?motion:1,!!c.mirrorX);
}
function drawParticles(t,a){
 const event=activeClip().events.find(e=>e.kind==='damage');if(!event)return;let p=(t-event.t)/.28;if(p<0||p>1)return;
 if(state.skill==='Qiangzhen'){ctx.save();ctx.globalAlpha=(1-p)*.46;ctx.fillStyle='#a9a18f';for(let i=0;i<13;i++){const x=a.Target_HitPoint[0]-90+i*19+(i%3-1)*25*p,y=770-(i%4)*13-42*p+65*p*p;ctx.fillRect(x,y,3+(i%3),2+(i%2));}ctx.restore();return;}
 ctx.save();ctx.globalAlpha=(1-p)*.85;const c=VFX_SKILLS[state.skill].color;
 for(let i=0;i<14;i++){const rad=i*2.399,len=(45+(i*71)%130)*ease(p),x=a.Target_HitPoint[0]+Math.cos(rad)*len,y=585+Math.sin(rad)*len*.6+p*p*48;path([[x,y],[x-Math.cos(rad)*14*(1-p),y-Math.sin(rad)*9]],i%3===0?'#fff1d9':c,i%3===0?3:1.5);}
 ctx.restore();
}
function render(t=state.t,updateUI=true){
 if(!loaded)return;
 const a=anchors(t),clip=activeClip();drawScene(t,a);
 const sorted=[...clip.cues].sort((a,b)=>VFX_MANIFEST.layers.indexOf(metadata[a.asset].layer)-VFX_MANIFEST.layers.indexOf(metadata[b.asset].layer));
 for(const cue of sorted)paintCue(cue,t,a);drawParticles(t,a);
 const damage=clip.events.find(e=>e.kind==='damage');
 if(damage&&t>=damage.t&&t<damage.t+.68){let p=(t-damage.t)/.68;ctx.save();ctx.globalAlpha=clamp((1-p)*2);text(String(damage.value),a.Target_HitPoint[0]+28,440-60*ease(p),52,'#fff1d1','center');text('× 1',a.Target_HitPoint[0]+28,474-60*ease(p),17,'#d6c7ac','center');ctx.restore();}
 const buff=clip.events.some(e=>e.kind==='buff'&&t>=e.t)&&!clip.events.some(e=>e.kind==='consume'&&t>=e.t);
 if(buff){ctx.fillStyle='#3d382c';ctx.fillRect(506,890,230,32);text('豹子头  ·  下一击速度 +2',621,912,13,'#e7d3a5','center');}
 if(updateUI){$('time').textContent=`${t.toFixed(2)} / ${clip.length.toFixed(2)} s`;$('scrub').value=t;
 const events=clip.events.filter(e=>e.t<=t);$('phase').textContent=events.at(-1)?.label||'准备';$('events').innerHTML=events.slice(-3).map(e=>`<div><time>${e.t.toFixed(2)} s</time>${e.label}</div>`).join('');}
}
function selectSkill(skill,branch){
 state.skill=skill;state.branch=branch||VFX_SKILLS[skill].branches[0][0];state.t=0;
 const s=VFX_SKILLS[skill],index=Object.keys(VFX_SKILLS).indexOf(skill);
 document.documentElement.style.setProperty('--accent',s.color);
 $('icon').src=VFX_ASSETS['icon'+(index+1)];$('name').textContent=s.name;$('subtitle').textContent=s.subtitle;$('dna').textContent=s.dna;$('duration').textContent=s.duration.toFixed(2)+' s';$('damage').textContent=s.damage;$('rule').textContent=s.rule;
 $('branch').innerHTML=s.branches.map(([v,t])=>`<option value="${v}">${t}</option>`).join('');$('branch').value=state.branch;
 document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('active',b.dataset.skill===skill));
 $('scrub').max=activeClip().length;
 $('timeline').innerHTML=activeClip().events.filter(e=>e.kind==='phase').slice(0,5).map(e=>`<span title="${e.t}s ${e.label}">${e.label.split(' · ')[0]}</span>`).join('');
 const assets=VFX_MANIFEST.assets.filter(a=>a.id.startsWith(skill+'.'));
 $('asset-count').textContent=`${assets.length} 个技能组件 / 共 ${VFX_MANIFEST.assets.length} 个素材`;
 $('gallery').innerHTML=assets.map(a=>`<a class="asset" href="../${a.file}" target="_blank" title="打开透明 PNG"><div class="image"><img src="${VFX_ASSETS[a.id]}" alt="${a.id}"></div><p>${a.id.split('.')[1]}</p><small>${a.width} × ${a.height} · ${a.layer}</small></a>`).join('');
 render();
}
function controls(){
 $('skills').innerHTML=Object.entries(VFX_SKILLS).map(([key,s],i)=>`<button data-skill="${key}"><img src="${VFX_ASSETS['icon'+(i+1)]}" alt=""><span><b>${s.name}</b><small>${i===4?'固有被动':`主动 0${i+1}`}</small></span></button>`).join('');
 document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>selectSkill(b.dataset.skill));
 $('play').onclick=()=>{state.playing=!state.playing;$('play').textContent=state.playing?'暂停':'播放';if(state.t>=activeClip().length)state.t=0;};
 $('restart').onclick=()=>{state.t=0;state.playing=true;$('play').textContent='暂停';};
 $('speed').onchange=e=>state.speed=Number(e.target.value);$('loop').onchange=e=>state.loop=e.target.checked;
 $('branch').onchange=e=>selectSkill(state.skill,e.target.value);
 $('guides').onchange=e=>{state.guides=e.target.checked;render()};$('background').onchange=e=>{state.background=e.target.value;render()};
 $('scrub').oninput=e=>{state.t=Number(e.target.value);state.playing=false;$('play').textContent='播放';render()};
 $('full').onclick=()=>canvas.requestFullscreen?.();
 document.addEventListener('keydown',e=>{if(e.code==='Space'&&!['SELECT','INPUT','BUTTON'].includes(document.activeElement.tagName)){e.preventDefault();$('play').click()}});
}
function tick(now){const dt=Math.min((now-last)/1000,.08);last=now;if(state.playing&&loaded){state.t+=dt*state.speed;if(state.t>activeClip().length){if(state.loop)state.t%=activeClip().length;else{state.t=activeClip().length;state.playing=false;$('play').textContent='播放';}}}render();requestAnimationFrame(tick)}
window.VFX_PREVIEW={state,selectSkill,render,anchors,ready:false};
Promise.all(Object.entries(VFX_ASSETS).map(([id,src])=>new Promise((res,rej)=>{let im=new Image();im.onload=()=>{images[id]=im;res()};im.onerror=()=>rej(Error(id));im.src=src}))).then(()=>{loaded=true;controls();selectSkill(state.skill,state.branch);window.VFX_PREVIEW.ready=true;requestAnimationFrame(tick)}).catch(e=>{$('phase').textContent='素材加载失败：'+e.message;console.error(e)});
