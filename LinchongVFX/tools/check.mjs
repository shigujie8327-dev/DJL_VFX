import {createRequire} from 'node:module';import fs from 'node:fs';import path from 'node:path';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/shiguji/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(import.meta.dirname,'..');
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1500,height:1120},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:4173/preview/index.html');await page.waitForFunction(()=>window.VFX_PREVIEW?.ready);
const summary=await page.evaluate(()=>{
 const results=[];VFX_PREVIEW.state.playing=false;
 for(const clip of Object.values(VFX_CLIPS)){
 VFX_PREVIEW.selectSkill(clip.skill,clip.branch);
 const points=[0,...clip.events.map(e=>e.t+.025),clip.length];
 for(const t of points)VFX_PREVIEW.render(t,false);
 const missing=clip.cues.filter(c=>!VFX_MANIFEST.assets.find(a=>a.id===c.asset));
 const a=VFX_PREVIEW.anchors(clip.length);
 results.push({id:clip.id,cues:clip.cues.length,damageEvents:clip.events.filter(e=>e.kind==='damage').length,damage:clip.events.find(e=>e.kind==='damage')?.value||0,casterReset:a.caster===0,missing:missing.length});
 }
 VFX_PREVIEW.selectSkill('Hengsaoqianjun','push');VFX_PREVIEW.state.t=.59;VFX_PREVIEW.render();return results;
});
await page.screenshot({path:path.join(root,'preview/preview-overview.png'),fullPage:true});
for(const [skill,branch,t] of [['Jifengci','interrupt',.42],['Huimaqiang','counter',.87],['Qiangzhen','block',1.42],['Baozitou','consume',.31]]){
 await page.evaluate(([s,b,t])=>{VFX_PREVIEW.selectSkill(s,b);VFX_PREVIEW.state.t=t;VFX_PREVIEW.render()},[skill,branch,t]);
 await page.locator('#stage').screenshot({path:path.join(root,`preview/check-${skill}.png`)});
}
await page.selectOption('#background','light');await page.evaluate(()=>{VFX_PREVIEW.selectSkill('Jifengci','interrupt');VFX_PREVIEW.state.t=.38;VFX_PREVIEW.render()});await page.locator('#stage').screenshot({path:path.join(root,'preview/check-light.png')});
await page.selectOption('#speed','0.25');await page.locator('#scrub').fill('0.5');
const controls=await page.evaluate(()=>({speed:VFX_PREVIEW.state.speed,scrub:VFX_PREVIEW.state.t,paused:!VFX_PREVIEW.state.playing}));
await page.goto('file:///'+path.join(root,'preview/index.html').replaceAll('\\','/'));await page.waitForFunction(()=>window.VFX_PREVIEW?.ready);
const report={errors,branches:summary,controls,filePreviewLoaded:true};fs.writeFileSync(path.join(root,'docs/preview-check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
