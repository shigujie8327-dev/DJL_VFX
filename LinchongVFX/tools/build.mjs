import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require('C:/Users/shiguji/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(import.meta.dirname,'..');
const assets=[];
const colors={Jifengci:'#f4414e',Huimaqiang:'#d58d49',Hengsaoqianjun:'#ffb346',Qiangzhen:'#b8c4c4',Baozitou:'#e8d4a4',Common:'#eee9de'};
const svg=(body,c,w=1024,h=1024)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="-512 -512 1024 1024"><defs><filter id="g" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="9"/></filter><radialGradient id="a"><stop stop-color="#ffffff" stop-opacity=".95"/><stop offset=".18" stop-color="${c}" stop-opacity=".6"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></radialGradient><linearGradient id="l"><stop stop-color="${c}" stop-opacity="0"/><stop offset=".6" stop-color="${c}"/><stop offset="1" stop-color="#fffef8"/></linearGradient></defs>${body}</svg>`;
const glow=(body,c)=>`<g stroke="${c}" fill="${c}" opacity=".55" filter="url(#g)">${body}</g><g stroke="${c}" fill="none">${body}</g>`;
const line=(d,w=4)=>`<path d="${d}" stroke-width="${w}" stroke-linecap="round"/>`;
function wuxia(kind){
 const dust='<g fill="#817d73" opacity=".37"><path d="M-410 55Q-280 5-155 54Q-54 22 62 47Q215 5 405 48Q325 103 173 85Q55 113-78 81Q-247 113-410 55Z"/><path d="M-345 100Q-256 69-171 101Q-91 74-25 98Q-107 132-229 122Z" opacity=".45"/></g>';
 if(kind==='ground')return dust+'<g fill="none" stroke="#a19b8d" stroke-linecap="round" opacity=".62"><path d="M-400 64Q-315 93-241 68M-195 90Q-74 112 28 84M62 75Q176 108 318 68M-100 129Q-38 143 17 124" stroke-width="6"/><path d="M-355 125l52-9m194 26l74-6m166-36l53 3" stroke-width="3"/></g>';
 if(kind==='dust')return dust+'<g fill="#a39e92" opacity=".42"><path d="M-220 12Q-171-39-105 7Q-65-51 10-9Q116-42 198 12Q131 52 18 36Q-93 73-220 12Z"/><circle cx="-280" cy="-12" r="5"/><circle cx="166" cy="-31" r="4"/></g>';
 if(kind==='flash')return '<g fill="none" stroke-linecap="round"><path d="M-265 58Q-109-46 239-23" stroke="#e0e2db" stroke-width="13" opacity=".7"/><path d="M-302 94Q-86 25 295 27" stroke="#8b918d" stroke-width="8" opacity=".55"/></g><g fill="#ae9a7e" opacity=".55"><path d="M-155 121l-25 25 42-12ZM60 88l16 39 14-29ZM186 78l28 27-3-34Z"/></g>';
 if(kind==='hit')return '<g fill="none" stroke-linecap="round"><path d="M-283 65Q-86-61 271-81" stroke="#d9dedb" stroke-width="14"/><path d="M-222 112Q-38 16 291 19" stroke="#9ca59f" stroke-width="7" opacity=".7"/></g><g fill="#aaa399"><path d="M-184-10l-39-22 20 48ZM70-93l25-33-4 48ZM209 70l42 5-31 23Z" opacity=".75"/></g>';
 if(kind==='block')return Array.from({length:5},(_,i)=>`<g transform="translate(${(i-2)*107} 0)"><path d="M0 -265L24 -177L6 -186L6 245L-6 245L-6 -186L-24 -177Z" fill="#bbc4c1" stroke="#65706d" stroke-width="3"/></g>`).join('');
 if(kind==='arc')return '<g fill="none" stroke-linecap="round"><path d="M-310 340Q-30-455 320-340" stroke="#ccd0c8" stroke-width="10" opacity=".58"/><path d="M-290 352Q-5-426 301-335" stroke="#7d8580" stroke-width="5" opacity=".48"/><path d="M-271 333Q-4-369 253-355" stroke="#e1e0d4" stroke-width="3" opacity=".4" stroke-dasharray="90 55 155 120"/></g><g fill="#918b80" opacity=".53"><path d="M-290 350l-33 21 43-6ZM-193 53l-19 25 29-9ZM-42-230l-8-25 21 18ZM228-351l37-13-24 24Z"/></g>';
 throw Error(kind);
}
function shape(kind,c){
 if(kind==='flash')return `<circle r="210" fill="url(#a)"/>`+glow('<path d="M-210 0L-30 -12L0 -175L15 -20L210 0L24 12L0 175L-18 24Z" fill="#fffaf2" stroke="none"/>',c);
 if(kind==='hit')return `<circle r="215" fill="url(#a)"/>`+glow(Array.from({length:13},(_,i)=>{const a=i*2.399,r=125+(i*43)%170;return line(`M${Math.cos(a)*25} ${Math.sin(a)*25} L${Math.cos(a)*r} ${Math.sin(a)*r}`,i%3===0?8:3)}).join('')+'<path d="M-90 0L-12 -12L0 -95L18 -12L100 0L12 12L0 98L-12 14Z" fill="#fff" stroke="none"/>',c);
 if(kind==='spear')return glow('<path d="M-420 0L290 -7L342 -26L438 0L342 26L290 7Z" fill="url(#l)" stroke="none"/>'+line('M-330 -18Q0 -65 320 -15',3)+line('M-370 32Q-80 80 280 22',2),c);
 if(kind==='wind')return glow(Array.from({length:9},(_,i)=>line(`M${-420+i*13} ${-125+i*30} Q-130 ${-170+i*40} ${310-i*14} ${-92+i*23}`,i%3+2)).join(''),c);
 if(kind==='ring'||kind==='swoosh')return `<g fill="none" stroke-linecap="round"><path d="M-370 122Q-190-168 175-111Q288-96 354-23" stroke="${c}" stroke-width="${kind==='swoosh'?26:11}" opacity=".47"/><path d="M-344 155Q-103-95 261-60" stroke="#ddd0ab" stroke-width="${kind==='swoosh'?8:4}" opacity=".73"/><path d="M-302 171Q-135 68 118 39" stroke="#8a7663" stroke-width="5" opacity=".5"/></g><g fill="#a89170" opacity=".65"><path d="M-319 149l-50 33 56-12ZM230-91l34-12-19 25ZM277 29l44 7-34 13Z"/></g>`;
 if(kind==='ground')return glow('<ellipse rx="416" ry="170" stroke-width="3"/><ellipse rx="355" ry="136" stroke-width="2" stroke-dasharray="100 35"/>'+Array.from({length:10},(_,i)=>{const a=i*Math.PI/5;return line(`M${Math.cos(a)*350} ${Math.sin(a)*134}L${Math.cos(a)*413} ${Math.sin(a)*169}`,4)}).join(''),c);
 if(kind==='cut')return glow('<path d="M-300 255L305 -265L-255 300Z" fill="#fff" stroke="none"/>'+line('M-290 275L275 -295',8),c);
 if(kind==='block')return glow(Array.from({length:5},(_,i)=>`<g transform="translate(${(i-2)*107} 0)"><path d="M0 -265L26 -172L8 -185L6 260L-6 260L-8 -185L-26 -172Z" fill="#eafaff" stroke-width="2"/></g>`).join(''),c);
 if(kind==='shards')return Array.from({length:15},(_,i)=>{const a=i*2.399,r=100+(i*61)%240;return `<path d="M0 -16L10 2L-3 25L-11 -4Z" fill="${i%3?'#302a27':c}" transform="translate(${Math.cos(a)*r} ${Math.sin(a)*r}) rotate(${i*43})"/>`}).join('');
 if(kind==='spark')return '<path d="M-350 0L0 -30L350 0L0 30Z" fill="url(#l)"/>';
 if(kind==='dust')return Array.from({length:9},(_,i)=>`<ellipse cx="${(i-4)*70}" cy="${i%2*35}" rx="90" ry="40" fill="${c}" opacity=".08" filter="url(#g)"/>`).join('');
 throw Error(kind);
}
async function add(skill,stage,kind,opts={}){
 const family=skill==='Common'?'CommonFX':skill==='Baozitou'?'PassiveSkills':'ActiveSkills';
 const name=`LC_${skill}_${stage}_01`;
 const rel=`Characters/Linchong/${family}/${skill==='Common'?'':skill+'/'}${opts.folder||stage}/${name}.png`;
 const full=path.join(root,rel);fs.mkdirSync(path.dirname(full),{recursive:true});
 const w=opts.size||1024,h=w;
 const source=svg(skill==='Qiangzhen'?wuxia(kind):shape(kind,colors[skill]),colors[skill],w,h);
 fs.mkdirSync(path.join(root,'sources'),{recursive:true});fs.writeFileSync(path.join(root,'sources',name+'.svg'),source);
 await sharp(Buffer.from(source)).png().toFile(full);
 assets.push({id:`${skill}.${stage}`,file:rel,width:w,height:h,pivot:[.5,.5],anchor:opts.anchor||'Caster_WeaponPoint',layer:opts.layer||'SkillFX',duration:opts.duration||.25,loop:!!opts.loop,blend:'normal',source:'authored-vector',alpha:'straight'});
}
for(const s of ['Jifengci','Huimaqiang','Hengsaoqianjun','Qiangzhen']){
 await add(s,'Cast','flash',{duration:s==='Hengsaoqianjun'?.22:.1});
 await add(s,'Hit','hit',{anchor:'Target_HitPoint',layer:'HitFX',duration:.22});
 if(s!=='Hengsaoqianjun')await add(s,'End',s==='Qiangzhen'?'dust':'wind',{duration:.22});
}
await add('Jifengci','Interrupt','cut',{folder:'Special',anchor:'Target_ActionPath',layer:'HitFX',duration:.16});
await add('Huimaqiang','Ready','ring',{folder:'Status',duration:.3,loop:true});
await add('Huimaqiang','Trigger','swoosh',{folder:'Special',duration:.24});
await add('Huimaqiang','Counter','spear',{folder:'Trail',layer:'WeaponTrail',duration:.16});
await add('Hengsaoqianjun','Blocked','shards',{folder:'Special',anchor:'Target_HitPoint',duration:.25});
await add('Qiangzhen','Ground','ground',{folder:'Status',anchor:'Ground',layer:'BattleFX_Back',duration:.25});
await add('Qiangzhen','Loop','ground',{folder:'Status',anchor:'Ground',layer:'Status_Back',duration:1,loop:true});
await add('Qiangzhen','Trigger','flash',{folder:'Special',anchor:'Ground',duration:.2});
await add('Qiangzhen','Block','block',{folder:'Special',anchor:'Target_HitPoint',duration:.2});
await add('Qiangzhen','ArcTrail','arc',{folder:'Trail',anchor:'Ground',layer:'WeaponTrail',duration:.25});
await add('Baozitou','Active','spark',{layer:'Status_Front',duration:1,loop:true});
await add('Baozitou','Consume','wind',{layer:'Status_Front',duration:.23});
await add('Baozitou','End','spark',{layer:'Status_Front',duration:.22});
for(const [stage,kind] of [['WeaponFlash','flash'],['HitFlash','hit'],['Dust','dust'],['Spark','spark'],['Wind','wind'],['Shard','shards']])await add('Common',stage,kind,{size:stage==='Spark'?256:512});
const generated=[...JSON.parse(fs.readFileSync(path.join(root,'docs/generated-files.json'),'utf8')).filter(g=>!(g.skill==='Hengsaoqianjun'&&g.stage==='Trail')&&!(g.skill==='Qiangzhen'&&g.stage==='Spawn')&&!(g.skill==='Huimaqiang'&&g.stage==='Trigger')),...JSON.parse(fs.readFileSync(path.join(root,'docs/hengsao-revision-prompts.json'),'utf8')),...JSON.parse(fs.readFileSync(path.join(root,'docs/qiangzhen-wuxia-prompts.json'),'utf8'))];
for(const g of generated){
 const passive=g.skill==='Baozitou';
 const folder=g.folder||(g.skill==='Huimaqiang'||g.skill==='Qiangzhen'?'Special':g.stage);
 const rel=`Characters/Linchong/${passive?'PassiveSkills':'ActiveSkills'}/${g.skill}/${folder}/LC_${g.skill}_${g.stage}_01.png`;
 fs.mkdirSync(path.dirname(path.join(root,rel)),{recursive:true});fs.copyFileSync(path.isAbsolute(g.path)?g.path:path.join(root,g.path),path.join(root,rel));
 const m=await sharp(path.join(root,rel)).metadata();
 assets.push({id:g.skill+'.'+g.stage,file:rel,width:m.width,height:m.height,pivot:[.5,.5],anchor:g.anchor||(g.skill==='Qiangzhen'?'Ground':passive?'Caster_PassivePoint':'Caster_WeaponPoint'),layer:g.layer||(g.skill==='Qiangzhen'?'Status_Back':passive?'Status_Front':'WeaponTrail'),duration:g.duration||(passive?.25:.3),loop:false,blend:'normal',source:'imagegen',alpha:'straight'});
}
const manifest={version:'1.1-r5',referenceCommit:'6d0dad6aa0fe7454a532940cf29a418505a70286',resolution:[1920,1080],characterHeight:400,layers:['BattleFX_Back','Status_Back','Character','WeaponTrail','SkillFX','Projectile','HitFX','Status_Front','BattleUI'],assets};
fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify(manifest,null,2));
// File:// preview uses an embedded image dictionary; all standalone PNGs stay available.
const embedded={};for(const a of assets)embedded[a.id]='data:image/png;base64,'+fs.readFileSync(path.join(root,a.file)).toString('base64');
for(let i=1;i<=5;i++){const file=fs.readdirSync(path.join(root,'Characters/Linchong/UI')).find(f=>f.startsWith(`linchong-0${i}`));embedded['icon'+i]='data:image/webp;base64,'+fs.readFileSync(path.join(root,'Characters/Linchong/UI',file)).toString('base64');}
fs.writeFileSync(path.join(root,'preview/assets.js'),'window.VFX_MANIFEST='+JSON.stringify(manifest)+';\nwindow.VFX_ASSETS='+JSON.stringify(embedded)+';');
const qa=[];
for(const a of assets){const {data,info}=await sharp(path.join(root,a.file)).ensureAlpha().raw().toBuffer({resolveWithObject:true});let zero=0,partial=0,min=255,max=0;for(let i=3;i<data.length;i+=4){const v=data[i];min=Math.min(min,v);max=Math.max(max,v);if(v===0)zero++;if(v>0&&v<255)partial++;}qa.push({id:a.id,size:[info.width,info.height],channels:info.channels,alphaMin:min,alphaMax:max,transparentPixels:zero,partialPixels:partial,pass:zero>0&&max>0&&info.channels===4});}
fs.writeFileSync(path.join(root,'docs/alpha-report.json'),JSON.stringify(qa,null,2));
console.log(JSON.stringify({assets:assets.length,alphaPass:qa.every(x=>x.pass)}));
