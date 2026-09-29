import fs from 'node:fs';import path from 'node:path';import '../preview/timelines.js';
const root=path.resolve(import.meta.dirname,'..');const clips=globalThis.VFX_CLIPS;
fs.writeFileSync(path.join(root,'timelines.json'),JSON.stringify(clips,null,2));
const take=(id,assets,base)=>clips[id].cues.filter(c=>assets.includes(c.asset)).map(c=>({...c,start:Math.max(0,c.start-base)}));
const one=(asset,anchor,w,h,duration=.25,extra={})=>({asset,anchor,w,h,duration,start:0,x:0,y:0,alpha:1,scaleFrom:.85,scaleTo:1.08,dx:0,dy:0,rotation:0,spin:0,envelope:'pulse',...extra});
const events={
 'Jifengci.Cast':{cues:take('Jifengci.hit',['Jifengci.Cast','Jifengci.Trail'],.22)},
 'Jifengci.Hit':{cues:take('Jifengci.hit',['Jifengci.Hit','Common.Spark','Jifengci.End'],.39)},
 'Jifengci.Interrupt':{cues:clips['Jifengci.interrupt'].cues.filter(c=>(c.asset==='Jifengci.Interrupt'||c.asset==='Common.Wind')&&c.start>=.4).map(c=>({...c,start:c.start-.4}))},
 'Huimaqiang.Ready':{stopTags:['counter-ready'],cues:[one('Huimaqiang.Ready','Caster_WeaponPoint',300,190,1,{alpha:.18,envelope:'hold',loop:true,tag:'counter-ready',scaleFrom:1,scaleTo:1})]},
 'Huimaqiang.Normal':{stopTags:['counter-ready'],cues:take('Huimaqiang.normal',['Huimaqiang.Cast','Huimaqiang.Counter'],.54)},
 'Huimaqiang.Counter':{stopTags:['counter-ready'],cues:take('Huimaqiang.counter',['Huimaqiang.Trigger','Huimaqiang.Counter'],.56)},
 'Huimaqiang.Hit35':{cues:take('Huimaqiang.normal',['Huimaqiang.Hit','Common.Spark','Huimaqiang.End'],.86)},
 'Huimaqiang.Hit55':{cues:take('Huimaqiang.counter',['Huimaqiang.Hit','Common.Spark','Huimaqiang.End'],.86)},
 'Hengsaoqianjun.Cast':{cues:take('Hengsaoqianjun.push',['Hengsaoqianjun.Cast','Hengsaoqianjun.Trail'],.2)},
 'Hengsaoqianjun.Hit':{cues:take('Hengsaoqianjun.push',['Hengsaoqianjun.Hit','Common.Shard','Common.Spark'],.57)},
 'Hengsaoqianjun.Push':{cues:take('Hengsaoqianjun.push',['Hengsaoqianjun.Push','Hengsaoqianjun.End'],.66).map(c=>({...c,tag:'forced-push'}))},
 'Hengsaoqianjun.Blocked':{stopTags:['forced-push'],cues:take('Hengsaoqianjun.blocked',['Hengsaoqianjun.Blocked','Common.WeaponFlash','Hengsaoqianjun.End'],.77)},
 'Qiangzhen.Activate':{stopTags:['field'],cues:[...take('Qiangzhen.block',['Qiangzhen.Cast','Qiangzhen.Ground'],.2).filter(c=>c.start<1),...clips['Qiangzhen.block'].cues.filter(c=>c.asset==='Qiangzhen.Spawn'&&c.start<1).map(c=>({...c,start:c.start-.2,loop:c.start>.6,tag:'field'})),one('Qiangzhen.Loop','Ground',500,390,1,{start:.45,alpha:.15,loop:true,tag:'field',envelope:'hold',scaleFrom:1,scaleTo:1})]},
 'Qiangzhen.Intercept':{stopTags:['field'],cues:clips['Qiangzhen.block'].cues.filter(c=>c.start>=1.24&&!c.asset.startsWith('Common.')).map(c=>({...c,start:c.start-1.24}))},
 'Qiangzhen.Expire':{stopTags:['field'],cues:take('Qiangzhen.expire',['Qiangzhen.End'],1.75)},
 'Baozitou.Trigger':{stopTags:['passive'],cues:[one('Baozitou.Trigger','Caster_PassivePoint',115,115,.25),one('Baozitou.Active','Caster_WeaponPoint',160,26,1,{start:.25,alpha:.22,loop:true,tag:'passive',envelope:'hold',scaleFrom:1,scaleTo:1})]},
 'Baozitou.Consume':{stopTags:['passive'],cues:take('Baozitou.consume',['Baozitou.Consume','Baozitou.End'],1.38)},
 'Baozitou.Clear':{stopTags:['passive'],cues:[one('Baozitou.End','Caster_WeaponPoint',110,24,.22,{alpha:.3})]}
};
fs.writeFileSync(path.join(root,'Cocos/vfx-events.json'),JSON.stringify({version:1,events},null,2));
console.log('Exported '+Object.keys(events).length+' event clips.');
