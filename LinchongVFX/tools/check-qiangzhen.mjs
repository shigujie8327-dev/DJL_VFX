import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import '../preview/timelines.js';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/shiguji/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(import.meta.dirname,'..'),clip=globalThis.VFX_CLIPS['Qiangzhen.block'];
const gather=clip.cues.filter(c=>c.asset==='Qiangzhen.GatherSpear'),attacks=clip.cues.filter(c=>c.asset==='Qiangzhen.Attack'),hits=clip.events.filter(e=>e.kind==='damage');
if(gather.length!==5||attacks.length!==1||hits.length!==1||hits[0].value!==32)throw Error('Gather/attack/hit count failed');
if(!(gather[0].start<attacks[0].start&&attacks[0].start<hits[0].t))throw Error('Sequence failed');
const attack=attacks[0];if(attack.anchor!=='Ground'||!attack.curve||attack.curve.endAnchor!=='Target_HitPoint'||!attack.orientToPath)throw Error('Attack must arc from ground to target');
if(Math.abs(attack.y)>65||attack.curve.control[1]>=attack.y-100)throw Error('Arc must start near ground and rise');
if(!clip.cues.some(c=>c.asset==='Qiangzhen.ArcTrail'&&c.reveal))throw Error('Physical air wake missing');
const eventLibrary=JSON.parse(fs.readFileSync(path.join(root,'Cocos/vfx-events.json')));
const eventCues=eventLibrary.events['Qiangzhen.Intercept'].cues;
if(eventCues.filter(c=>c.asset==='Qiangzhen.GatherSpear').length!==5||eventCues.filter(c=>c.asset==='Qiangzhen.Attack').length!==1||!eventCues.some(c=>c.asset==='Qiangzhen.ArcTrail'))throw Error('Cocos sequence mismatch');
if(eventLibrary.events['Qiangzhen.Activate'].cues.some(c=>!c.loop&&c.start>1))throw Error('Activation wrongly includes interception');
const b=await chromium.launch({channel:'msedge',headless:true});const page=await b.newPage({viewport:{width:1500,height:1120}});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:4173/preview/index.html?skill=Qiangzhen');await page.waitForFunction(()=>window.VFX_PREVIEW?.ready);
await page.evaluate(()=>{VFX_PREVIEW.state.playing=false;});
for(const [name,t] of [['standing',1.14],['gather',1.39],['gathered',1.50],['attack',1.66],['contact',1.745],['hit',1.79]]){
 await page.evaluate(t=>{VFX_PREVIEW.state.t=t;VFX_PREVIEW.render()},t);
 await page.locator('#stage').screenshot({path:path.join(root,`preview/qiangzhen-${name}.png`)});
}
await page.evaluate(()=>{VFX_PREVIEW.state.t=1.66;VFX_PREVIEW.render()});await page.screenshot({path:path.join(root,'preview/qiangzhen-revision-overview.png'),fullPage:true});
const report={gatherSpears:5,attackVolleys:1,hitEvents:1,damage:32,attackPath:'ground-quadratic-arc-to-target',airWake:'physical-dust-reveal',sequence:['ground-gather','curved-attack','hit'],cocosEventCuesMatch:true,errors};fs.writeFileSync(path.join(root,'docs/qiangzhen-revision-check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));await b.close();
