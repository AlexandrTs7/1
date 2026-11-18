const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'); const path = require('path');
const TL = JSON.parse(fs.readFileSync('timeline.json','utf8'));
const FPS = +(process.env.FPS||30);
const only = process.env.STILLS ? process.env.STILLS.split(',').map(Number) : null;
(async()=>{
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1080,height:1920}});
  await p.addInitScript(tl=>{window.__TL__=tl}, TL);
  await p.goto('file://'+path.resolve('reel.html')); await p.evaluate(()=>document.fonts.ready);
  if(only){ fs.mkdirSync('stills',{recursive:true});
    for(const t of only){ await p.evaluate(t=>render(t),t); await p.screenshot({path:`stills/t${t}.png`}); }
    await b.close(); return; }
  const n = Math.ceil(TL.total*FPS);
  const ff = spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-i','voice.wav',
    '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-r',String(FPS),
    '-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','reels_zapor_v1.mp4'],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<n;i++){ await p.evaluate(t=>render(t), i/FPS);
    const buf = await p.screenshot({type:'jpeg',quality:94});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(i%300===0) console.log('frame',i,'/',n); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done');
})();
