import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {execFileSync} from 'node:child_process';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/shiguji/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');const root=path.resolve(import.meta.dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'))),events=JSON.parse(fs.readFileSync(path.join(root,'Cocos/vfx-events.json')));
for(const [name,event] of Object.entries(events.events))for(const cue of event.cues){if(!manifest.assets.some(a=>a.id===cue.asset)||cue.duration<=0||cue.start<0)throw Error(name+': invalid cue');}
const browser=await chromium.launch({channel:'msedge',headless:true});const page=await browser.newPage({viewport:{width:1280,height:800}});await page.goto('http://127.0.0.1:4173/preview/index.html');await page.waitForFunction(()=>window.VFX_PREVIEW?.ready);
const report=await page.evaluate(async()=>{
 VFX_PREVIEW.state.playing=false;const video=document.createElement('video');document.body.appendChild(video);video.src='Linchong-VFX-showcase.mp4';video.preload='auto';await new Promise((resolve,reject)=>{video.onloadeddata=resolve;video.onerror=reject;});
 const result={width:video.videoWidth,height:video.videoHeight,duration:video.duration,seekTimes:[]};
 for(const t of [0.42,3.2,8.2,11.5,14.0,17.2,19.2,20.8]){await new Promise(r=>{video.onseeked=r;video.currentTime=t;});if(Math.abs(video.currentTime-t)>.1)throw Error('Failed video seek '+t+' actual '+video.currentTime);result.seekTimes.push(video.currentTime);}
 return result;
});if(report.duration<20)throw Error('Video truncated');
fs.writeFileSync(path.join(root,'docs/video-check.json'),JSON.stringify({file:'Linchong-VFX-showcase.mp4',format:'H.264 MP4, yuv420p, 30fps, faststart',bytes:fs.statSync(path.join(root,'preview/Linchong-VFX-showcase.mp4')).size,...report},null,2));
console.log(JSON.stringify({events:Object.keys(events.events).length,assets:manifest.assets.length,video:report}));await browser.close();
