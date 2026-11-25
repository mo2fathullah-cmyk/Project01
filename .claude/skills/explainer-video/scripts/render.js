// Render a GSAP video page (exposes window.ready -> duration, window.seek(t)) to a sharp MP4.
// Anti-blur settings: capture at 2x (2160x3840), Lanczos downscale to 1080x1920, x264 CRF 16, tune animation, 30 fps.
//
//   node render.js <page.html> stills <outdir> <t1,t2,...>     -> PNG stills at 1x for review
//   node render.js <page.html> video  <out.mp4> [workers=4] [audio.wav]
const {chromium} = require('playwright');
const {spawn} = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = 30;
const [, , html, mode, out, arg4, arg5] = process.argv;
const url = 'file://' + path.resolve(html);

async function openPage(browser, scale) {
  const p = await browser.newPage({viewport: {width: 1080, height: 1920}, deviceScaleFactor: scale});
  p.on('pageerror', e => console.error('PAGE ERROR:', e.message));
  await p.goto(url);
  const dur = await p.evaluate(() => window.ready);
  await p.waitForTimeout(300);
  return {p, dur};
}

async function segment(idx, f0, f1, file) {
  const browser = await chromium.launch();
  const {p} = await openPage(browser, 2);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-tune', 'animation',
    '-profile:v', 'high', '-level', '4.2', '-pix_fmt', 'yuv420p', '-r', String(FPS), file], {stdio: ['pipe', 'inherit', 'inherit']});
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg ' + c)))));
  await p.evaluate(() => seek(0));
  for (let i = f0; i < f1; i++) {
    await p.evaluate(t => seek(t), i / FPS);
    const buf = await p.screenshot({type: 'jpeg', quality: 95});
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - f0) % 150 === 0) console.log(`worker ${idx}: frame ${i}/${f1}`);
  }
  ff.stdin.end();
  await done;
  await browser.close();
}

(async () => {
  if (mode === 'stills') {
    fs.mkdirSync(out, {recursive: true});
    const browser = await chromium.launch();
    const {p} = await openPage(browser, 1);
    for (const t of arg4.split(',').map(Number)) {
      await p.evaluate(() => seek(0));
      await p.evaluate(t => seek(t), t);
      await p.screenshot({path: path.join(out, `t${String(t).replace('.', '_')}.png`)});
    }
    await browser.close();
    return;
  }
  const workers = Number(arg4 || 4);
  const audio = arg5;
  const b = await chromium.launch();
  const {dur} = await openPage(b, 1);
  await b.close();
  const total = Math.round(dur * FPS);
  const tmp = out + '.parts';
  fs.mkdirSync(tmp, {recursive: true});
  const per = Math.ceil(total / workers);
  const files = [];
  const jobs = [];
  for (let w = 0; w < workers; w++) {
    const f0 = w * per, f1 = Math.min(total, f0 + per);
    if (f0 >= f1) break;
    const file = path.join(tmp, `seg${w}.mp4`);
    files.push(file);
    jobs.push(segment(w, f0, f1, file));
  }
  await Promise.all(jobs);
  fs.writeFileSync(path.join(tmp, 'list.txt'), files.map(f => `file '${path.resolve(f)}'`).join('\n'));
  const aIn = audio ? ['-i', audio] : ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo'];
  await new Promise((res, rej) => {
    const f = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'list.txt'), ...aIn,
      '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out],
      {stdio: 'inherit'});
    f.on('close', c => (c === 0 ? res() : rej(new Error('concat ' + c))));
  });
  fs.rmSync(tmp, {recursive: true, force: true});
  console.log('done', out, 'duration', dur, 'frames', total);
})();
