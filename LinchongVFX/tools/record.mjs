import {createRequire} from 'node:module';import fs from 'node:fs';import path from 'node:path';import {execFileSync} from 'node:child_process';
const require=createRequire(import.meta.url),{chromium}=require('C:/Users/shiguji/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(import.meta.dirname,'..');
const focusSkill=process.argv.includes('--qiangzhen')?'Qiangzhen':process.argv.includes('--hengsao')?'Hengsaoqianjun':null;
const focused=!!focusSkill;
const outputName=focusSkill==='Qiangzhen'?'Qiangzhen-Gather-Thrust':focusSkill==='Hengsaoqianjun'?'Hengsao-Trail-Push-End':'Linchong-VFX-showcase';
const browser=await chromium.launch({channel:'msedge',headless:true,args:['--disable-background-timer-throttling','--disable-renderer-backgrounding']});
const page=await browser.newPage({viewport:{width:1440,height:1000}});await page.goto('http://127.0.0.1:4173/preview/index.html');await page.waitForFunction(()=>window.VFX_PREVIEW?.ready);
const result=await page.evaluate(async(focusSkill)=>{
 const api=VFX_PREVIEW;api.state.playing=false;api.state.background='dark';
 const focused=!!focusSkill;
 const playlist=focusSkill==='Qiangzhen'?[['Qiangzhen','block',1],['Qiangzhen','block',.5],['Qiangzhen','block',.25]]:focusSkill==='Hengsaoqianjun'?[['Hengsaoqianjun','push',1],['Hengsaoqianjun','push',.5],['Hengsaoqianjun','blocked',.5]]:[['Jifengci','interrupt'],['Huimaqiang','counter'],['Huimaqiang','normal'],['Hengsaoqianjun','push'],['Hengsaoqianjun','blocked'],['Qiangzhen','block'],['Qiangzhen','expire'],['Baozitou','consume']];
 const mime=['video/mp4;codecs=avc1.42001f','video/webm;codecs=vp9','video/webm'].find(x=>MediaRecorder.isTypeSupported(x));
 const stream=document.querySelector('canvas').captureStream(30),chunks=[];
 const rec=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:8000000});
 const done=new Promise(resolve=>{rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};rec.onstop=resolve});rec.start();
 for(const [skill,branch,speed=1] of playlist){
  api.selectSkill(skill,branch);const length=VFX_CLIPS[skill+'.'+branch].length;
  const start=performance.now();await new Promise(resolve=>{function frame(now){api.state.t=Math.min((now-start)/1000*speed,length);api.render();if(focused){const ctx=document.querySelector('canvas').getContext('2d');ctx.fillStyle='#c4dfeb';ctx.font='20px Microsoft YaHei';ctx.fillText(speed+'x  /  '+(speed===1?'原速':'慢放'),65,155);}if(api.state.t>=length)resolve();else requestAnimationFrame(frame);}requestAnimationFrame(frame)});
 }
 rec.stop();await done;stream.getTracks().forEach(t=>t.stop());
 const blob=new Blob(chunks,{type:mime});const data=await new Promise(resolve=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.readAsDataURL(blob)});
 return {mime,data,bytes:blob.size};
},focusSkill);
const ext=result.mime.startsWith('video/mp4')?'mp4':'webm';const out=path.join(root,'preview',outputName+'.'+ext);fs.writeFileSync(out,Buffer.from(result.data.split(',')[1],'base64'));
const ffmpeg=process.env.VFX_FFMPEG||path.resolve(root,'../.tools/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe');
if(ext==='mp4'&&fs.existsSync(ffmpeg)){
 const normalized=out.replace('.mp4','-normalized.mp4');
 execFileSync(ffmpeg,['-v','error','-i',out,'-vf','fps=30','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-y',normalized]);
 fs.renameSync(out,path.resolve(root,'../.tools/raw-video-'+Date.now()+'.mp4'));fs.renameSync(normalized,out);
}
const verify=await page.evaluate(async filename=>{const v=document.createElement('video');v.src=filename;document.body.appendChild(v);await new Promise((res,rej)=>{v.onloadeddata=res;v.onerror=rej});await new Promise(r=>{v.onseeked=r;v.currentTime=3});return {width:v.videoWidth,height:v.videoHeight,seekPassed:Math.abs(v.currentTime-3)<.1,duration:Number.isFinite(v.duration)?v.duration:null};},outputName+'.'+ext);
fs.writeFileSync(path.join(root,focusSkill==='Qiangzhen'?'docs/qiangzhen-video-check.json':focusSkill==='Hengsaoqianjun'?'docs/hengsao-video-check.json':'docs/video-check.json'),JSON.stringify({file:path.basename(out),mime:result.mime,bytes:fs.statSync(out).size,...verify},null,2));console.log(JSON.stringify({file:out,...verify}));await browser.close();
