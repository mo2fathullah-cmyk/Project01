// usage: node render.js stills t1,t2,...  |  node render.js full out.mp4 [fps]
const {chromium}=require('playwright');
const {spawn}=require('child_process');
const fs=require('fs');
(async()=>{
  const mode=process.argv[2];
  const browser=await chromium.launch({args:['--force-color-profile=srgb']});
  const page=await browser.newPage({viewport:{width:540,height:960}});
  page.on('console',m=>{if(m.type()==='error')console.error('PAGE',m.text())});
  page.on('pageerror',e=>console.error('PAGEERR',e.message));
  await page.goto('http://127.0.0.1:8765/comp.html');
  await page.waitForFunction('window.READY===true',null,{timeout:120000});
  const total=await page.evaluate('TOTAL');
  fs.writeFileSync('timeline.json',JSON.stringify(await page.evaluate('({total:TOTAL,cues:CUES,tl:TLINFO})'),null,1));
  console.log('TOTAL',total.toFixed(2));
  if(mode==='stills'){
    fs.mkdirSync('stills',{recursive:true});
    for(const ts of process.argv[3].split(',')){
      const t=parseFloat(ts);
      const b64=await page.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.85).slice(23)},t);
      fs.writeFileSync(`stills/t${t.toFixed(2).padStart(7,'0')}.jpg`,Buffer.from(b64,'base64'));
    }
  } else if(mode==='full'){
    const fps=parseInt(process.argv[4]||'30');const n=Math.ceil(total*fps);
    const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',process.argv[3]],{stdio:['pipe','inherit','inherit']});
    const t0=Date.now();
    for(let i=0;i<n;i++){
      const b64=await page.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.94).slice(23)},i/fps);
      if(!ff.stdin.write(Buffer.from(b64,'base64')))await new Promise(r=>ff.stdin.once('drain',r));
      if(i%300===0)console.log(`frame ${i}/${n} ${((Date.now()-t0)/1000).toFixed(0)}s`);
    }
    ff.stdin.end();await new Promise(r=>ff.on('close',r));
    console.log('done',((Date.now()-t0)/1000).toFixed(0)+'s');
  }
  await browser.close();
})();
