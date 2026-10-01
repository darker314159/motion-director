#!/usr/bin/env node
/** Local deterministic HTML renderer. Does not install dependencies. */
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';

const args={width:1920,height:1080,fps:30,start:0};
const flags=new Set(['probe','determinism','allow-remote']);
const values=new Set(['project','out','width','height','fps','start','duration','times','audio','chrome']);
for(let i=2;i<process.argv.length;i++){
  const key=process.argv[i].replace(/^--/,'');
  if(key==='help'){console.log('render.mjs --project DIR [--probe] [--times 0,1,2] [--start S --duration S] [--out DIR] [--width W --height H --fps FPS] [--audio FILE] [--chrome FILE] [--determinism] [--allow-remote]');process.exit(0);}
  if(flags.has(key))args[key]=true;
  else if(values.has(key)&&process.argv[i+1]&&!process.argv[i+1].startsWith('--'))args[key]=process.argv[++i];
  else throw new Error('Unknown or incomplete option: '+process.argv[i]);
}
if(!args.project)throw new Error('--project is required');
const project=fs.realpathSync(path.resolve(args.project));
for(const k of ['width','height','fps','start'])args[k]=Number(args[k]);
if(![args.width,args.height,args.fps].every(v=>Number.isInteger(v)&&v>0)||!Number.isFinite(args.start)||args.start<0)throw new Error('Invalid dimensions/fps/start');
if(args.width%2||args.height%2)throw new Error('H.264 yuv420p requires even dimensions');
const roots=[project,process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES].filter(Boolean);
let chromium;
for(const root of roots){
  const req=createRequire(path.join(path.resolve(root),'__motion_resolve__.cjs'));
  for(const name of ['playwright','playwright-core']){try{chromium=req(name).chromium;break;}catch{}}
  if(chromium)break;
}
if(!chromium)throw new Error('Playwright not resolved. Install a compatible project-local playwright and browser, then rerun.');
let browser,server;
try{
  browser=await chromium.launch({headless:true,...(args.chrome?{executablePath:path.resolve(args.chrome)}:{})});
  const page=await browser.newPage({viewport:{width:args.width,height:args.height},deviceScaleFactor:1});
  if(args.probe){
    const caps=await page.evaluate(()=>{
      const canvas=document.createElement('canvas'),gl=canvas.getContext('webgl2')||canvas.getContext('webgl');
      let pixel=null;
      if(gl){gl.clearColor(.25,.5,.75,1);gl.clear(gl.COLOR_BUFFER_BIT);const p=new Uint8Array(4);gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,p);pixel=Array.from(p);}
      return {canvas2d:!!document.createElement('canvas').getContext('2d'),webgl_context:!!gl,webgl_clear_pixel:pixel,note:'Actual scene/shader still needs its own smoke frame.'};
    });
    console.log(JSON.stringify({status:'browser_smoke_tested',browser:browser.version(),...caps},null,2));
  }else{
    if(!fs.existsSync(path.join(project,'index.html')))throw new Error('Project must contain index.html');
    const out=path.resolve(args.out||path.join(project,'out'));fs.mkdirSync(out,{recursive:true});
    const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf','.mp4':'video/mp4','.wav':'audio/wav','.mp3':'audio/mpeg'};
    server=http.createServer((req,res)=>{
      try{
        const rel=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
        if(rel==='/favicon.ico'){res.writeHead(204);res.end();return;}
        let file=path.resolve(project,'.'+(rel==='/'?'/index.html':rel));
        file=fs.realpathSync(file);
        if(file!==project&&!file.startsWith(project+path.sep)){res.writeHead(403);res.end();return;}
        if(!fs.statSync(file).isFile()){res.writeHead(404);res.end();return;}
        const size=fs.statSync(file).size;
        const range=req.headers.range?.match(/^bytes=(\d+)-(\d*)$/);
        res.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');res.setHeader('Accept-Ranges','bytes');
        if(range){const start=Number(range[1]),end=range[2]?Math.min(Number(range[2]),size-1):size-1;
          if(start>end||start>=size){res.writeHead(416);res.end();return;}
          res.writeHead(206,{'Content-Range':`bytes ${start}-${end}/${size}`,'Content-Length':end-start+1});fs.createReadStream(file,{start,end}).pipe(res);
        }else{res.writeHead(200,{'Content-Length':size});fs.createReadStream(file).pipe(res);}
      }catch{res.writeHead(404);res.end();}
    });
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const origin=`http://127.0.0.1:${server.address().port}`;
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))errors.push(`HTTP ${r.status()} ${r.url()}`);});
    if(!args['allow-remote'])await page.route('**/*',route=>{
      const url=route.request().url();
      if(url.startsWith(origin+'/')||url.startsWith('data:')||url.startsWith('blob:'))return route.continue();
      errors.push('Blocked remote dependency: '+url);return route.abort();
    });
    await page.goto(origin,{waitUntil:'load'});
    await page.waitForFunction(()=>window.READY===true&&typeof window.render==='function',{},{timeout:30000});
    await page.evaluate(()=>document.fonts.ready);
    const total=await page.evaluate(()=>window.DUR);
    if(!Number.isFinite(total)||total<=0)throw new Error('window.DUR must be positive seconds');
    if(errors.length)throw new Error(errors.join('\n'));
    async function draw(t){
      await page.evaluate(async t=>{await window.render(t);},t);
      if(errors.length)throw new Error(errors.join('\n'));
      return await page.screenshot({type:'png'});
    }
    const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
    if(args.determinism){
      const t=total*.25,a=hash(await draw(t));await draw(total*.75);const b=hash(await draw(t));
      if(a!==b)throw new Error('Determinism failure: repeated timestamp changed after an out-of-order frame');
    }
    const t0=Date.now();let result;
    if(args.times!==undefined){
      const times=args.times.split(',').map(Number);
      if(!times.length||!times.every(t=>Number.isFinite(t)&&t>=0&&t<total))throw new Error('--times must be within [0, DUR)');
      const files=[];
      for(let i=0;i<times.length;i++){const file=path.join(out,`still-${String(i).padStart(3,'0')}-${times[i].toFixed(3)}.png`);fs.writeFileSync(file,await draw(times[i]));files.push(file);}
      result={mode:'stills',files,times};
    }else{
      const duration=args.duration===undefined?total-args.start:Number(args.duration);
      if(!Number.isFinite(duration)||duration<=0||args.start+duration>total+1e-7)throw new Error('Clip interval exceeds window.DUR');
      const n=Math.round(duration*args.fps);
      if(n<1||Math.abs(duration*args.fps-n)>1e-6)throw new Error('duration*fps must be an integer');
      const frames=fs.mkdtempSync(path.join(out,'frames-'));
      for(let i=0;i<n;i++){
        fs.writeFileSync(path.join(frames,`frame-${String(i).padStart(6,'0')}.png`),await draw(args.start+i/args.fps));
        if(i%Math.max(1,args.fps*5)===0)process.stderr.write(`Rendered ${i+1}/${n}\n`);
      }
      const video=path.join(out,'video.mp4');
      const enc=['-hide_banner','-loglevel','error','-y','-framerate',String(args.fps),'-i',path.join(frames,'frame-%06d.png')];
      if(args.audio){const audio=path.resolve(args.audio);if(!fs.existsSync(audio))throw new Error('Audio file not found');enc.push('-ss',String(args.start),'-i',audio,'-map','0:v:0','-map','1:a:0','-af','apad','-c:a','aac','-b:a','192k');}
      enc.push('-t',String(duration),'-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-movflags','+faststart',video);
      const encoded=spawnSync('ffmpeg',enc,{encoding:'utf8'});
      if(encoded.error||encoded.status!==0)throw new Error('FFmpeg failed: '+(encoded.error?.message||encoded.stderr));
      fs.rmSync(frames,{recursive:true});
      result={mode:'video',file:video,frames:n,start:args.start,duration,audio:args.audio||null};
    }
    result={...result,width:args.width,height:args.height,fps:args.fps,elapsed_ms:Date.now()-t0,determinism_checked:!!args.determinism,browser:browser.version()};
    fs.writeFileSync(path.join(out,'render-report.json'),JSON.stringify(result,null,2));
    console.log(JSON.stringify(result,null,2));
  }
}finally{
  if(browser)await browser.close();
  if(server)await new Promise(resolve=>server.close(resolve));
}
