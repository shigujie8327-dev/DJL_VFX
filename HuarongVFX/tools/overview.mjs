import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),sharp=require('sharp');
const root=path.resolve(import.meta.dirname,'..');
const assets=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8')).assets;
const groups=[
 ['连珠箭','huarong-01_lianzhu_jian.png',['LianzhuJian.Cast','LianzhuJian.Projectile','LianzhuJian.Hit','LianzhuJian.End']],
 ['穿云箭','huarong-02_chuanyun_jian.png',['ChuanyunJian.Cast','ChuanyunJian.Projectile','ChuanyunJian.AirCone','ChuanyunJian.Hit']],
 ['退身箭','huarong-03_tuishen_jian.png',['TuishenJian.Projectile','TuishenJian.Hit','TuishenJian.Retreat','TuishenJian.Blocked']],
 ['定身箭','huarong-04_dingshen_jian.png',['DingshenJian.Projectile','DingshenJian.Hit','DingshenJian.Trigger','DingshenJian.Active']],
 ['小李广','huarong-05_xiaoliguang.png',['XiaoLiGuang.Trigger','XiaoLiGuang.Active','XiaoLiGuang.Deactivate','Common.GreenFleck']]
];
const width=1680,height=1160,composites=[];
const add=async(file,x,y,w,h)=>{const b=await sharp(file).resize(w,h,{fit:'contain',background:{r:0,g:0,b:0,alpha:0}}).png().toBuffer();composites.push({input:b,left:x,top:y});};
for(let row=0;row<groups.length;row++){
 const [name,icon,list]=groups[row],top=128+row*200;
 await add(path.join(root,'Characters/Huarong/UI',icon),40,top+10,160,160);
 for(let col=0;col<list.length;col++){const a=assets.find(x=>x.id===list[col]);await add(path.join(root,a.file),245+col*350,top+3,320,164);}
}
const labels=groups.map((g,i)=>`<text x="44" y="${121+i*200}" fill="#eef7fa" font-size="21">${g[0]}</text>${g[2].map((x,j)=>`<text x="${252+j*350}" y="${307+i*200}" fill="#9eb8bf" font-size="17">${x.split('.')[1]}</text>`).join('')}`).join('');
const graphic=`<svg width="${width}" height="${height}"><text x="42" y="62" fill="#f0f8f8" font-size="35" font-family="Microsoft YaHei">花荣 VFX · 图标与拆分组件</text><text x="43" y="95" fill="#9eb8bf" font-size="18" font-family="Microsoft YaHei">27 transparent PNG assets · 5 skills · v1.1</text>${labels}</svg>`;
composites.push({input:Buffer.from(graphic),left:0,top:0});
await sharp({create:{width,height,channels:4,background:'#101a24'}}).composite(composites).png().toFile(path.join(root,'preview/overview.png'));
