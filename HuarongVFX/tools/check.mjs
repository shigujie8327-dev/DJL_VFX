import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require('sharp');
const root=path.resolve(import.meta.dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const events=JSON.parse(fs.readFileSync(path.join(root,'Cocos/vfx-events.json'),'utf8')).events;
const ids=new Set(manifest.assets.map(a=>a.id));
const failures=[];
for(const a of manifest.assets){
 if(!fs.existsSync(path.join(root,a.file)))failures.push(`missing ${a.file}`);
 else {const m=await sharp(path.join(root,a.file)).metadata();if(m.width!==a.width||m.height!==a.height||!m.hasAlpha)failures.push(`format ${a.id}`);}
}
for(const [event,entry] of Object.entries(events))for(const cue of entry.cues){if(!ids.has(cue.asset))failures.push(`${event} -> ${cue.asset}`);if(cue.duration<=0||cue.w<=0||cue.h<=0)failures.push(`bad cue ${event}`);}
for(let i=1;i<=4;i++)if(!events[`LianzhuJian.Hit${i}`])failures.push(`missing volley Hit${i}`);
for(const event of ['TuishenJian.RetreatSuccess','TuishenJian.RetreatBlocked','DingshenJian.Apply','DingshenJian.Expire','XiaoLiGuang.EnterFar','XiaoLiGuang.LeaveFar'])if(!events[event])failures.push(`missing ${event}`);
const qa=JSON.parse(fs.readFileSync(path.join(root,'docs/alpha-report.json'),'utf8'));
if(qa.some(x=>!x.pass)||qa.length!==manifest.assets.length)failures.push('alpha QA');
console.log(JSON.stringify({assets:manifest.assets.length,events:Object.keys(events).length,alphaPass:qa.every(x=>x.pass),failures}));
if(failures.length)process.exitCode=1;
