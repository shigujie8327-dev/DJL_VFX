import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import '../preview/timelines.js';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/shiguji/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(import.meta.dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json')));const alpha=JSON.parse(fs.readFileSync(path.join(root,'docs/alpha-report.json')));
const assets=['Trail','Push','End'].map(s=>manifest.assets.find(a=>a.id==='Hengsaoqianjun.'+s));
if(assets.some(a=>!a||a.source!=='imagegen')||assets.some(a=>!alpha.find(x=>x.id===a.id)?.pass))throw Error('Missing revised transparent assets');
const clips=globalThis.VFX_CLIPS,success=clips['Hengsaoqianjun.push'],blocked=clips['Hengsaoqianjun.blocked'];
if(success.events.filter(e=>e.kind==='damage').length!==1||blocked.events.filter(e=>e.kind==='damage').length!==1)throw Error('Hit must remain once');
const cocos=JSON.parse(fs.readFileSync(path.join(root,'Cocos/vfx-events.json')));
if(!cocos.events['Hengsaoqianjun.Blocked'].cues.some(c=>c.asset==='Hengsaoqianjun.End'))throw Error('Cocos blocked end cue missing');
const tip=success.cues.find(c=>c.asset==='Hengsaoqianjun.Trail');const p=(.57-tip.start)/tip.duration,scale=tip.scaleFrom+(tip.scaleTo-tip.scaleFrom)*(1-(1-p)**3);
const estimatedTip=[970+tip.x+(.01-.5)*tip.w*scale,585+tip.y+(.56-.5)*tip.h*scale];if(Math.abs(estimatedTip[0]-740)>15||Math.abs(estimatedTip[1]-585)>15)throw Error('Mirrored trail endpoint misses target');
if(!success.cues.find(c=>c.asset==='Hengsaoqianjun.Push')?.mirrorX||!success.cues.find(c=>c.asset==='Hengsaoqianjun.End')?.mirrorX)throw Error('Push and end must face left with the trail');
const b=await chromium.launch({channel:'msedge',headless:true});const page=await b.newPage({viewport:{width:1500,height:1120}});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:4173/preview/index.html');await page.waitForFunction(()=>window.VFX_PREVIEW?.ready);await page.evaluate(()=>{VFX_PREVIEW.state.playing=false;VFX_PREVIEW.selectSkill('Hengsaoqianjun','push');});
for(const [name,t] of [['trail',.54],['hit',.60],['push',.73],['end',.95]]){await page.evaluate(t=>{VFX_PREVIEW.state.t=t;VFX_PREVIEW.render()},t);await page.locator('#stage').screenshot({path:path.join(root,'preview/hengsao-'+name+'.png')});}
await page.evaluate(()=>{VFX_PREVIEW.selectSkill('Hengsaoqianjun','blocked');VFX_PREVIEW.state.t=.84;VFX_PREVIEW.render()});await page.locator('#stage').screenshot({path:path.join(root,'preview/hengsao-blocked.png')});
const report={threeRevisedAssets:assets.map(a=>a.file),direction:'left-facing-horizontal-mirror',estimatedTrailTip:estimatedTip,targetHitPoint:[740,585],successHitCount:1,blockedHitCount:1,pushDurationOnBlock:blocked.cues.find(c=>c.asset==='Hengsaoqianjun.Push').duration,errors};fs.writeFileSync(path.join(root,'docs/hengsao-revision-check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));await b.close();
