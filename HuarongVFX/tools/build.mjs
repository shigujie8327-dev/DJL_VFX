import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';

const require = createRequire(import.meta.url);
let sharp;
try { sharp = require('sharp'); }
catch { throw new Error('Install sharp or set NODE_PATH to a node_modules directory containing sharp.'); }
const root = path.resolve(import.meta.dirname, '..');
const assets = [];
const green = '#6ce6a2', blue = '#8bceff', white = '#f2f8ff', violet = '#a995db';
const svg = (body, w=1024, h=1024) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 1024 1024"><defs><filter id="blur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="13"/></filter><radialGradient id="fade"><stop stop-color="#fff" stop-opacity=".9"/><stop offset=".2" stop-color="#b9eaff" stop-opacity=".42"/><stop offset="1" stop-color="#b9eaff" stop-opacity="0"/></radialGradient></defs>${body}</svg>`;
const p = (d, color, width, opacity=1, extra='') => `<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round" opacity="${opacity}" ${extra}/>`;
const arrow = (color=blue) => `<g><path d="M120 514L718 514 718 488 871 512 718 536 718 510Z" fill="${white}" opacity=".96"/><path d="M120 514L718 514" stroke="#344754" stroke-width="13"/><path d="M190 514l-78-48 24 47-24 47Z" fill="#dfeaf0"/><path d="M718 488L871 512 718 536Z" fill="#dbeaff" stroke="#65849d" stroke-width="5"/>${p('M110 486Q421 420 700 489',color,12,.68)}${p('M90 546Q398 584 712 535',color,8,.52)}</g>`;
const streaks = (color, count=7) => Array.from({length:count},(_,i)=>p(`M${85+i*20} ${360+i*47} Q${270+i*6} ${325+i*52} ${750-i*32} ${330+i*50}`,color,i%3===0?8:4,.35+i*.04)).join('');
const flash = color => `<circle cx="512" cy="512" r="190" fill="url(#fade)" opacity=".45"/><g filter="url(#blur)">${p('M300 512H724M512 300V724',color,55,.42)}</g>${p('M320 512H704M512 325V699',white,11,.9)}<path d="M512 428l17 67 69 17-69 17-17 67-17-67-69-17 69-17Z" fill="${white}"/>`;
const hit = (color, heavy=false) => `<g filter="url(#blur)"><circle cx="512" cy="512" r="${heavy?190:125}" fill="${color}" opacity=".32"/></g><circle cx="512" cy="512" r="${heavy?75:46}" fill="${white}" opacity=".65"/>${Array.from({length:heavy?14:9},(_,i)=>{const a=(i/(heavy?14:9))*Math.PI*2,r1=heavy?95:60,r2=(heavy?270:160)+(i*31)%80;return p(`M${512+Math.cos(a)*r1} ${512+Math.sin(a)*r1}L${512+Math.cos(a)*r2} ${512+Math.sin(a)*r2}`,i%3?color:white,i%4===0?12:6,.78)}).join('')}<path d="M512 424l19 68 68 20-68 20-19 68-19-68-68-20 68-20Z" fill="#fff"/>`;
const wind = color => `<g filter="url(#blur)">${p('M90 620Q370 330 870 430',color,60,.25)}</g>${p('M90 620Q370 330 870 430',color,16,.7)}${p('M190 675Q460 432 840 490',white,6,.75)}${p('M122 750Q412 580 754 573',color,8,.4)}${streaks(color,5)}`;
const retreatArc = (broken=false) => `<g filter="url(#blur)">${p('M165 676Q390 164 852 304',blue,58,.25)}</g>${p(broken?'M165 676Q290 387 480 312':'M165 676Q390 164 852 304',white,15,.9)}${p(broken?'M140 708Q282 411 456 343':'M140 708Q378 195 838 335',blue,43,.64)}${p(broken?'M200 737Q343 513 466 469':'M200 737Q490 412 840 392',blue,8,.66)}${broken?`<g fill="${blue}" opacity=".75"><path d="M480 313l38-45-10 51Z"/><path d="M473 358l32 16-46 20Z"/><path d="M515 386l18-17-6 38Z"/></g>`:''}`;
const chain = (subtle=false) => `<g fill="none" stroke="${blue}" opacity="${subtle?.46:.9}" stroke-width="${subtle?15:27}"><ellipse cx="512" cy="594" rx="276" ry="93"/><ellipse cx="512" cy="594" rx="186" ry="55"/></g>${Array.from({length:7},(_,i)=>{const x=276+i*78,y=590+(i%2?38:-38);return `<ellipse cx="${x}" cy="${y}" rx="43" ry="21" fill="none" stroke="${white}" stroke-width="${subtle?5:9}" transform="rotate(${i%2?22:-22} ${x} ${y})" opacity="${subtle?.4:.8}"/>`}).join('')}<path d="M512 448l41 72-41 72-41-72Z" fill="${violet}" opacity="${subtle?.4:.9}"/>`;
const aim = (active=false) => `<g fill="none" stroke="${green}" stroke-width="${active?17:23}" opacity="${active?.5:.9}"><circle cx="512" cy="512" r="${active?116:174}" stroke-dasharray="${active?'100 58':'135 82'}"/><path d="M512 206v124m0 364v124M206 512h124m364 0h124"/></g><circle cx="512" cy="512" r="${active?11:23}" fill="${white}" opacity="${active?.52:.94}"/>${p('M325 512H699',green,3,.55)}${p('M512 326V698',green,3,.55)}`;
const ribbon = color => `${p('M154 632Q368 368 822 438',color,36,.48)}${p('M185 653Q421 430 840 458',white,8,.82)}`;
const specs = [
 ['LianzhuJian','Cast','Cast',()=>svg(flash(green)+`<path d="M320 263Q555 512 320 761" fill="none" stroke="${green}" stroke-width="14" opacity=".65"/>`),{duration:.13}],
 ['LianzhuJian','Projectile','Projectile',null,{input:'Lianzhu-Arrow.png',w:2048,h:682,anchor:'Attack_MidPoint',layer:'Projectile',duration:.16}],
 ['LianzhuJian','Hit','Hit',()=>svg(hit(green)),{anchor:'Target_HitPoint',layer:'HitFX',duration:.16}],
 ['LianzhuJian','End','End',()=>svg(streaks(green,6)),{anchor:'Target_HitPoint',duration:.18}],
 ['ChuanyunJian','Cast','Cast',()=>svg(flash(blue)+ribbon(blue)),{duration:.2}],
 ['ChuanyunJian','Projectile','Projectile',null,{input:'Chuanyun-Arrow.png',w:2048,h:682,anchor:'Attack_MidPoint',layer:'Projectile',duration:.2}],
 ['ChuanyunJian','AirCone','Trail',()=>svg(`<g filter="url(#blur)">${p('M110 512L775 220M110 512L775 804',blue,24,.18)}</g>${p('M130 512L805 306',blue,13,.58)}${p('M130 512L805 718',blue,13,.58)}${p('M130 512L730 370',white,4,.72)}${p('M130 512L730 654',white,4,.72)}`),{anchor:'Target_HitPoint',layer:'WeaponTrail',duration:.17}],
 ['ChuanyunJian','Hit','Hit',()=>svg(hit(blue,true)),{anchor:'Target_HitPoint',layer:'HitFX',duration:.25}],
 ['ChuanyunJian','End','End',()=>svg(wind(blue)),{anchor:'Target_HitPoint',duration:.23}],
 ['TuishenJian','Cast','Cast',()=>svg(arrow(blue)+ribbon(blue)),{duration:.16}],
 ['TuishenJian','Projectile','Projectile',()=>svg(arrow(blue)+streaks(blue,4),2048,682),{anchor:'Attack_MidPoint',layer:'Projectile',duration:.18,w:2048,h:682}],
 ['TuishenJian','Hit','Hit',()=>svg(hit(blue)),{anchor:'Target_HitPoint',layer:'HitFX',duration:.18}],
 ['TuishenJian','Retreat','Special',()=>svg(retreatArc()),{anchor:'Caster_PassivePoint',duration:.25}],
 ['TuishenJian','Blocked','Special',()=>svg(retreatArc(true)),{anchor:'Caster_PassivePoint',duration:.16}],
 ['TuishenJian','End','End',()=>svg(streaks(blue,5)),{anchor:'Caster_PassivePoint',duration:.18}],
 ['DingshenJian','Cast','Cast',()=>svg(flash(blue)+`<circle cx="512" cy="512" r="92" fill="${violet}" opacity=".3"/>`),{duration:.15}],
 ['DingshenJian','Projectile','Projectile',()=>svg(arrow(blue)+streaks(blue,4),2048,682),{anchor:'Attack_MidPoint',layer:'Projectile',duration:.18,w:2048,h:682}],
 ['DingshenJian','Hit','Hit',()=>svg(hit(blue)+`<circle cx="512" cy="512" r="108" fill="${violet}" opacity=".17"/>`),{anchor:'Target_HitPoint',layer:'HitFX',duration:.19}],
 ['DingshenJian','Trigger','Status',()=>svg(chain(false)),{anchor:'Target_FeetPoint',layer:'Status_Front',duration:.25}],
 ['DingshenJian','Active','Status',()=>svg(chain(true)),{anchor:'Target_FeetPoint',layer:'Status_Front',duration:1,loop:true}],
 ['DingshenJian','CostPulse','Special',()=>svg(chain(false)+flash(violet)),{anchor:'Target_FeetPoint',layer:'Status_Front',duration:.22}],
 ['DingshenJian','End','End',()=>svg(`${p('M240 590Q512 740 780 590',blue,16,.35)}<g fill="${blue}" opacity=".55"><path d="M315 590l-47-29 19 50Z"/><path d="M711 567l39 22-27 38Z"/></g>`),{anchor:'Target_FeetPoint',duration:.2}],
 ['XiaoLiGuang','Trigger','Trigger',()=>svg(aim(false)+ribbon(green)),{anchor:'Target_HitPoint',layer:'Status_Front',duration:.26}],
 ['XiaoLiGuang','Active','Active',()=>svg(aim(true)),{anchor:'Caster_WeaponPoint',layer:'Status_Front',duration:1,loop:true}],
 ['XiaoLiGuang','Deactivate','Deactivate',()=>svg(aim(true)+streaks(green,3)),{anchor:'Caster_WeaponPoint',layer:'Status_Front',duration:.22}],
 ['Common','GreenFleck','GreenFleck',()=>svg(`<g fill="${green}" opacity=".8"><path d="M426 499l121-20-61 67Z"/><circle cx="633" cy="480" r="11"/><circle cx="332" cy="550" r="8"/></g>`,512,512),{w:512,h:512,duration:.16}],
 ['Common','BlueFleck','BlueFleck',()=>svg(`<g fill="${blue}" opacity=".8"><path d="M375 505l145-20-47 56Z"/><path d="M602 471l51-10-12 29Z"/></g>`,512,512),{w:512,h:512,duration:.16}],
];
for (const [skill,stage,folder,draw,opt] of specs) {
 const family=skill==='Common'?'CommonFX':skill==='XiaoLiGuang'?'PassiveSkills':'ActiveSkills';
 const name=`HR_${skill}_${stage}_01`;
 const rel=`Characters/Huarong/${family}/${skill==='Common'?'':skill+'/'}${folder}/${name}.png`;
 const dest=path.join(root,rel);fs.mkdirSync(path.dirname(dest),{recursive:true});
 if(opt.input) await sharp(path.join(root,'sources/imagegen',opt.input)).resize(opt.w,opt.h,{fit:'contain',background:{r:0,g:0,b:0,alpha:0}}).png().toFile(dest);
 else {const source=draw();fs.mkdirSync(path.join(root,'sources'),{recursive:true});fs.writeFileSync(path.join(root,'sources',name+'.svg'),source);await sharp(Buffer.from(source)).png().toFile(dest);}
 assets.push({id:`${skill}.${stage}`,file:rel,width:opt.w||1024,height:opt.h||1024,pivot:[.5,.5],anchor:opt.anchor||'Caster_WeaponPoint',layer:opt.layer||'SkillFX',duration:opt.duration,loop:!!opt.loop,blend:'normal',source:opt.input?'imagegen':'authored-vector',alpha:'straight'});
}
const manifest={version:'1.1-hr1',resolution:[1920,1080],characterHeight:400,iconReference:'2026-09-26 finalized Huarong icons',layers:['BattleFX_Back','Status_Back','Character','WeaponTrail','SkillFX','Projectile','HitFX','Status_Front','BattleUI'],assets};
fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify(manifest,null,2));
const qa=[];
for(const a of assets){const {data,info}=await sharp(path.join(root,a.file)).ensureAlpha().raw().toBuffer({resolveWithObject:true});let transparent=0,opaque=0,partial=0;for(let i=3;i<data.length;i+=4){const v=data[i];if(v===0)transparent++;else if(v===255)opaque++;else partial++;}qa.push({id:a.id,size:[info.width,info.height],channels:info.channels,transparent,opaque,partial,pass:transparent>0&&opaque+partial>0&&info.channels===4});}
fs.mkdirSync(path.join(root,'docs'),{recursive:true});fs.writeFileSync(path.join(root,'docs/alpha-report.json'),JSON.stringify(qa,null,2));
console.log(JSON.stringify({assets:assets.length,alphaPass:qa.every(x=>x.pass)}));
