#!/usr/bin/env python3
"""Read-only dependency inventory for THIS host; never installs or claims to inspect another PC."""
import argparse, importlib.util, importlib.metadata, json, os, pathlib, platform, shutil, subprocess, sys

def command(name,args):
    exe=shutil.which(name)
    if not exe:return {'status':'missing'}
    try:
        r=subprocess.run([exe]+args,text=True,capture_output=True,timeout=12)
        return {'status':'executed' if r.returncode==0 else 'failed','path':exe,'version':(r.stdout or r.stderr).splitlines()[:2],'returncode':r.returncode}
    except (OSError,subprocess.TimeoutExpired) as e:return {'status':'failed','path':exe,'error':str(e)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',default='.');p.add_argument('--out');a=p.parse_args();project=pathlib.Path(a.project).resolve()
    report={'scope':'current_execution_host_only','platform':platform.platform(),'architecture':platform.machine(),'project':str(project),'python':sys.version.split()[0], 'python_executable':sys.executable, 'python_prefix':sys.prefix, 'project_exists':project.exists()}
    report['commands']={n:command(n,args) for n,args in [('node',['--version']),('npm',['--version']),('pnpm',['--version']),('yarn',['--version']),('ffmpeg',['-version']),('ffprobe',['-version'])]}
    report['python_modules']={n:bool(importlib.util.find_spec(n)) for n in ['numpy','scipy','PIL','soundfile','edge_tts','kokoro_onnx','faster_whisper']}
    # Inspect metadata/specs without importing engines or initializing graphics.
    report['manim']={}
    for variant,distribution,module,cli in [('manimgl','manimgl','manimlib','manimgl'),('community','manim','manim','manim')]:
        try: version=importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError: version=None
        module_found=bool(importlib.util.find_spec(module));cli_path=shutil.which(cli)
        report['manim'][variant]={'distribution':distribution,'version':version,'module_found':module_found,'cli_path':cli_path,'status':'discovered' if version or module_found or cli_path else 'missing','render_status':'not_tested'}
    report['manim_backend_modules']={n:bool(importlib.util.find_spec(n)) for n in ['manimpango','cairo','moderngl','glfw','wgpu','rendercanvas']}
    report['optional_tex_commands']={n:shutil.which(n) for n in ['latex','xelatex','dvisvgm']}
    report['graphics_checks']={'webgl':'browser capability; actual context/shader/pixels not tested','p5':'package resolution only; browser load and 2D/WEBGL drawing not tested','manim':'native graphics backend and font coverage not tested; TeX needed only for TeX objects'}
    manifest=project/'package.json'
    try:
        pkg=json.loads(manifest.read_text()) if manifest.exists() else {}
        report['declared_packages']={**pkg.get('dependencies',{}),**pkg.get('devDependencies',{})}
    except (OSError,ValueError) as e:report['manifest_error']=str(e)
    report['lockfiles']=[n for n in ['package-lock.json','pnpm-lock.yaml','yarn.lock','bun.lock','bun.lockb'] if (project/n).is_file()]
    packages=['react','remotion','@remotion/cli','@remotion/renderer','hyperframes','gsap','three','playwright','playwright-core','puppeteer','p5','p5.brush']
    if shutil.which('node'):
        js=r'''const fs=require('fs'),path=require('path');const {createRequire}=require('module');
const roots=[process.argv[1],process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES].filter(Boolean);const out={};
for(const name of JSON.parse(process.argv[2])) {let found;
 for(const root of roots){try{const req=createRequire(path.join(path.resolve(root),'__probe__.cjs'));let file;try{file=req.resolve(name+'/package.json')}catch{file=req.resolve(name)}let dir=fs.statSync(file).isDirectory()?file:path.dirname(file),pkg;
 while(dir!==path.dirname(dir)){const p=path.join(dir,'package.json');if(fs.existsSync(p)){const j=JSON.parse(fs.readFileSync(p));if(j.name===name){pkg=j;break}}dir=path.dirname(dir)}
 if(pkg){found={status:'resolved',version:pkg.version,path:dir};break}}catch{}}
 out[name]=found||{status:'not_resolved'};
}console.log(JSON.stringify(out));'''
        try:
            r=subprocess.run(['node','-e',js,str(project),json.dumps(packages)],capture_output=True,text=True,timeout=20)
            report['packages']=json.loads(r.stdout) if r.returncode==0 else {'error':r.stderr[:1000]}
        except (OSError,ValueError,subprocess.TimeoutExpired) as e:report['packages']={'error':str(e)}
    candidates=[shutil.which(x) for x in ['chromium','chromium-browser','google-chrome','chrome']]
    candidates += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    for root in [os.environ.get('PROGRAMFILES'),os.environ.get('PROGRAMFILES(X86)'),os.environ.get('LOCALAPPDATA')]:
        if root:candidates.append(str(pathlib.Path(root)/'Google/Chrome/Application/chrome.exe'))
    report['browser_executables']=[x for x in candidates if x and pathlib.Path(x).is_file()]
    report['browser_status']='not_smoke_tested; Playwright-managed browser may exist even if paths are empty'
    report['webgl_status']='not_tested'
    report['font_status']='coverage_not_tested'
    report['font_inventory_tool']=shutil.which('fc-list')
    base=project
    while not base.exists():base=base.parent
    report['disk_free_gib']=round(shutil.disk_usage(base).free/1024**3,2)
    if a.out:
        out=pathlib.Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
