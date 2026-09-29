(function(global){
const S={Jifengci:{name:'疾风刺',subtitle:'CRIMSON VELOCITY',color:'#f4414e',dna:'赤红枪势 · 银白枪锋',duration:.46,damage:'26 × 1',rule:'打断结果由战斗逻辑传入；仅成功时切断敌方行动轨迹。',branches:[['hit','普通命中'],['interrupt','成功打断']]},Huimaqiang:{name:'回马枪',subtitle:'RETURNING SPEAR',color:'#dca060',dna:'铜橙风痕 · 金白反刺',duration:.66,damage:'35 / 55 × 1',rule:'实际受击结算后才触发强化反击，多段攻击只触发一次。',branches:[['counter','受击后反击 · 55'],['normal','普通出枪 · 35']]},Hengsaoqianjun:{name:'横扫千军',subtitle:'GOLDEN CROSSWIND',color:'#ffb746',dna:'橙金横风 · 银白薄锋',duration:.88,damage:'62 × 1',rule:'先命中，再尝试近→远。风压被阻止时，62 点命中仍然保留。',branches:[['push','命中 · 强制推远'],['blocked','命中 · 变距受阻']]},Qiangzhen:{name:'枪阵',subtitle:'SILVER SENTINELS',color:'#b8c4c4',dna:'地面沙土 · 冷钢枪锋',duration:.55,damage:'32 × 1',rule:'监听敌方远→近尝试；五枪贴地聚拢后沿弧线刺向敌人，只结算一次命中。',branches:[['block','远→近尝试 · 拦截'],['expire','未触发 · 到期消散']]},Baozitou:{name:'豹子头',subtitle:'LEOPARD INSTINCT',color:'#e7d3a5',dna:'香槟金速度弧 · 银灰豹纹',duration:.25,damage:'速度 +2',rule:'成功打断或截击后获得；下一次攻击开始时消耗，平时只保留淡金枪光。',branches:[['consume','触发 · 下一次攻击消耗'],['active','触发 · 保持待机']]}};
const A={C:'Caster_WeaponPoint',T:'Target_HitPoint',G:'Ground',P:'Caster_PassivePoint',M:'Attack_MidPoint'};
function cue(asset,start,duration,anchor,w,h=w,o={}){return {asset,start,duration,anchor,w,h,x:0,y:0,alpha:1,scaleFrom:.85,scaleTo:1.08,dx:0,dy:0,rotation:0,spin:0,envelope:'pulse',...o};}
function clip(skill,branch){
const cues=[],events=[];let length=2.3;const s=S[skill];
const fx=(stage,t,d,a,w,h,o)=>cues.push(cue(skill+'.'+stage,t,d,a,w,h,o));
const common=(stage,t,d,a,w,h,o)=>cues.push(cue('Common.'+stage,t,d,a,w,h,o));
const event=(t,label,kind='phase',value)=>events.push({t,label,kind,value});
const hit=(t,value,size=250)=>{fx('Hit',t,.22,A.T,size);if(skill==='Qiangzhen')common('Dust',t,.25,A.T,180,85,{y:95,dx:35,alpha:.52});else common('Spark',t,.25,A.T,150,30,{dx:skill==='Hengsaoqianjun'?-60:60,dy:-48,rotation:skill==='Hengsaoqianjun'?24:-24});event(t,`${value} · 单段命中`,'damage',value);};
if(skill==='Jifengci'){
 fx('Cast',.22,.1,A.C,200);event(.22,'枪锋亮起');
 fx('Trail',.29,.19,A.M,570,285,{scaleFrom:.35,scaleTo:1,dx:50});event(.29,'高速突刺');
 hit(.39,26,230);fx('End',.46,.22,A.T,240,90,{dx:70,alpha:.35});
 if(branch==='interrupt'){common('Wind',.20,.20,A.T,300,95,{x:-40,dx:-70,rotation:180,alpha:.35});for(const side of [-1,1])common('Wind',.4,.20,A.T,120,44,{x:side*55,y:side*20,dx:side*45,dy:side*25,rotation:180,alpha:.25});fx('Interrupt',.40,.16,A.T,250);event(.4,'行动轨迹切断','interrupt');cues.push(cue('Baozitou.Trigger',.48,.25,A.P,112,112));cues.push(cue('Baozitou.Active',.73,1.4,A.C,150,25,{alpha:.2,envelope:'hold'}));event(.48,'豹子头 · 下一次攻击速度 +2','buff');}
 event(.68,'归位 · 演出结束');
}
if(skill==='Huimaqiang'){
 fx('Ready',.18,.42,A.C,300,190,{alpha:.18,envelope:'hold'});event(.18,'淡铜枪势 · 就绪');
 if(branch==='counter'){
 common('Wind',.40,.17,A.M,350,120,{dx:-120,rotation:180,alpha:.45});common('HitFlash',.54,.16,A.C,180);event(.54,'敌方攻击实际命中','incoming');
 fx('Trigger',.56,.24,A.C,340,180,{scaleFrom:1.15,scaleTo:.36,spin:22});event(.56,'回身风沙收束');
 }else{fx('Cast',.54,.14,A.C,190);event(.54,'非攻击行为 · 普通出枪');}
 fx('Counter',.76,.18,A.M,560,180,{scaleFrom:.45,scaleTo:1,dx:50});event(.76,'回身反刺');
 hit(.86,branch==='counter'?55:35,branch==='counter'?280:210);fx('End',.98,.22,A.T,260,95,{alpha:.3,dx:50});event(1.2,'归位 · 演出结束');length=2.5;
}
if(skill==='Hengsaoqianjun'){
 fx('Cast',.2,.22,A.C,260);event(.2,'后蓄 · 橙金凝聚');
 // Left-facing sweep: the mirrored silver hook at normalized (~0.01, ~0.56) reaches Target_HitPoint.
 fx('Trail',.40,.28,A.M,590,295,{x:58,y:-18,scaleFrom:.6,scaleTo:1,dx:0});event(.4,'银白弯钩由右向左对准受击点');
 hit(.57,62,290);common('Shard',.58,.27,A.T,300,220,{dx:-38,dy:40});
 fx('Push',.66,branch==='push'?.24:.13,A.T,340,150,{x:130,dx:branch==='push'?-100:-35,scaleFrom:.72,scaleTo:1.02,motion:'smooth',envelope:'transfer',alpha:.78,mirrorX:true});event(.66,'横向风压 · 强制变距尝试','attempt');
 if(branch==='blocked'){fx('Blocked',.78,.25,A.T,300,220,{dx:-30,dy:25});common('WeaponFlash',.77,.12,A.T,180);event(.78,'风压破碎 · 距离不变','blocked');}else event(.78,'强制推远成功','distance','FAR');
 fx('End',.86,.22,A.T,270,78,{x:200,dx:-40,alpha:.24,envelope:'transfer',mirrorX:true});event(1.08,'残风消散 · 已结算命中保留');length=2.6;
}
if(skill==='Qiangzhen'){
 fx('Cast',.20,.15,A.C,145,145,{dx:160,dy:160});event(.2,'枪尖落地 · 扬起沙土');
 fx('Ground',.30,.3,A.G,510,400);fx('Spawn',.38,.30,A.G,440,440,{y:-195,scaleFrom:.75,scaleTo:1});event(.38,'五枪入地 · 沙土扬起');
 const end=branch==='block'?1.78:1.75;
 const standingEnd=branch==='block'?1.30:end;
 fx('Loop',.65,standingEnd-.65,A.G,500,390,{alpha:.15,envelope:'hold',scaleFrom:1,scaleTo:1});fx('Spawn',.65,standingEnd-.65,A.G,430,430,{y:-195,alpha:.17,envelope:'hold',scaleFrom:1,scaleTo:1});event(.68,'低亮待机 · 等待事件');
 if(branch==='block'){
 event(1.18,'敌方 FAR→NEAR 尝试','attempt');common('Wind',1.18,.22,A.T,300,90,{rotation:180,dx:-70,alpha:.2});
 fx('Trigger',1.24,.16,A.G,220,160,{y:-35,alpha:.5});event(1.24,'枪阵响应 · 接近被阻止','blocked');
 fx('Ground',1.24,.30,A.G,500,390,{alpha:.45,scaleFrom:1,scaleTo:.12});
 for(let i=0;i<5;i++){
  const x=(i-2)*75,y=-175-(2-Math.abs(i-2))*29;
  fx('GatherSpear',1.24,.30,A.G,360,120,{x,y,dx:-15-x+(i-2)*3,dy:-35+(i-2)*4-y,rotation:-90+(i-2)*9,spin:35-(i-2)*9,scaleFrom:.78+(2-Math.abs(i-2))*.1,scaleTo:.30,motion:'smooth',rotationEase:true,envelope:'transfer'});
 }
 event(1.28,'五枪离阵 · 贴地聚拢','gather');
 fx('ArcTrail',1.52,.25,A.G,500,270,{x:135,y:-125,alpha:.72,scaleFrom:1,scaleTo:1,reveal:true,envelope:'hold',motion:'smooth'});
 fx('Attack',1.52,.25,A.G,360,120,{x:-15,y:-35,scaleFrom:.30,scaleTo:1,motion:'smooth',curve:{control:[125,-215],endAnchor:A.T,endOffset:[-125,0]},orientToPath:true,envelope:'transfer'});
 event(1.52,'五枪合势 · 自地面弧线突刺','attack');
 hit(1.74,32,250);event(1.74,'32×1 命中 · 枪阵消耗','fieldEnd');
 }else event(1.75,'林冲下次战斗行动结束 · 枪阵到期','fieldEnd');
 fx('End',end,.28,A.G,450,120,{dy:-25,alpha:.3});event(end+.28,'阵地清空');length=2.75;
}
if(skill==='Baozitou'){
 fx('Trigger',.22,.25,A.P,115);event(.22,'成功打断 / 截击','buff');
 fx('Active',.47,branch==='consume'?.91:1.8,A.C,160,26,{alpha:.22,envelope:'hold',scaleFrom:1,scaleTo:1});event(.47,'淡金枪光 · 速度 +2');
 if(branch==='consume'){
 fx('Consume',1.38,.23,A.C,190,90,{scaleFrom:1.1,scaleTo:.1,dx:42,alpha:.8});event(1.38,'下一次攻击开始 · 收束消耗','consume');fx('End',1.57,.22,A.C,110,24,{alpha:.3});event(1.79,'被动已消耗');
 }else event(1.8,'等待下一次攻击 · 状态仍生效');length=2.7;
}
return {id:skill+'.'+branch,skill,branch,length,cues,events:events.sort((a,b)=>a.t-b.t)};
}
const clips={};for(const [key,s] of Object.entries(S))for(const [branch] of s.branches)clips[key+'.'+branch]=clip(key,branch);
global.VFX_SKILLS=S;global.VFX_CLIPS=clips;
})(globalThis);
