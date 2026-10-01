#!/usr/bin/env python3
"""Validate a recorded motion plan; cannot manufacture or establish user approval."""
import argparse,json,math,pathlib,sys

def validate(p,stage,base):
    errors=[]
    def require(ok,message):
        if not ok:errors.append(message)
    b=p.get('brief',{});revision=p.get('revision')
    require(isinstance(revision,int) and revision>=1,'revision must be a positive integer')
    for key in ['topic','audience','takeaway','style','execution_target']:
        require(isinstance(b.get(key),str) and bool(b[key].strip()),f'brief.{key} is unresolved')
    for key in ['width','height','fps']:
        value=b.get(key);require(isinstance(value,int) and not isinstance(value,bool) and value>0,f'brief.{key} must be a positive integer')
    dur=b.get('duration_seconds');fps=b.get('fps')
    valid_dur=isinstance(dur,(int,float)) and not isinstance(dur,bool) and math.isfinite(dur) and dur>0
    require(valid_dur,'brief.duration_seconds must be positive and finite')
    for key in ['palette','fonts']:require(isinstance(b.get(key),list) and len(b[key])>0,f'brief.{key} must be chosen')
    require(b.get('music') in ['provided','synthesized','none','authorized_external'],'brief.music must be chosen')
    for key in ['voice','subtitles']:require(isinstance(b.get(key),bool),f'brief.{key} must be true or false')
    needed=['brief','references','director']+(['visual'] if stage=='render' else [])
    for key in needed:
        a=p.get('approvals',{}).get(key,{})
        require(a.get('status') in ['approved','delegated'],f'{key} approval/delegation is missing')
        require(bool(str(a.get('evidence','')).strip()) and bool(str(a.get('scope','')).strip()),f'{key} requires actual user evidence and scope')
        require(a.get('revision')==revision,f'{key} belongs to an old revision')
    tech=p.get('technology',{})
    require(tech.get('route') in ['html','remotion','hyperframes','manim'],'technology.route must be html/remotion/hyperframes/manim')
    if tech.get('route')=='manim':
        require(tech.get('manim_variant') in ['manimgl','community'],'technology.manim_variant must be manimgl/community for a Manim route')
    require(bool(tech.get('graphics')) and bool(tech.get('reason')),'technology graphics and rationale required')
    refs=p.get('references',[])
    require(isinstance(refs,list) and len(refs)>0,'at least one selected reference required')
    for i,r in enumerate(refs):
        require(bool(r.get('url')) and bool(r.get('learn')) and bool(r.get('evidence_level')),f'reference {i} lacks source/learning/evidence')
    shots=p.get('shots',[]);require(isinstance(shots,list) and len(shots)>0,'storyboard shots required')
    expected=0;ids=set()
    for i,s in enumerate(shots):
        sid=s.get('id');require(bool(sid) and sid not in ids,f'shot {i} missing/duplicate id');ids.add(sid)
        start,end=s.get('start_frame'),s.get('end_frame')
        valid=all(isinstance(v,int) and not isinstance(v,bool) for v in [start,end]) and end>start>=0
        require(valid,f'shot {i} needs valid [start_frame,end_frame)')
        if valid:
            require(start==expected,f'shot {i} introduces gap/overlap in primary shot ranges');expected=end
        for k in ['task','visual','motion','camera','sound','transition']:
            require(bool(s.get(k)),f'shot {i}.{k} missing; use explicit none/fixed where intentional')
        for text in s.get('texts',[]):
            if text.get('role')=='subtitle':continue
            fully=text.get('fully_visible_frame');until=text.get('exit_start_frame')
            valid_text=valid and all(isinstance(v,int) for v in [fully,until]) and start<=fully<until<=end
            require(valid_text,f'shot {i} text needs visible interval inside the shot')
            if valid_text and isinstance(fps,int) and fps>0:
                require((until-fully)/fps>=2.5 or bool(text.get('approved_exception')),f'shot {i} core text holds less than 2.5 seconds')
    if valid_dur and isinstance(fps,int) and fps>0:
        frames=dur*fps
        require(abs(frames-round(frames))<1e-6,'duration*fps must be an integer frame count')
        require(expected==round(frames),'storyboard must cover the full intended duration')
    if stage=='render':
        env=p.get('environment',{})
        require(env.get('status')=='smoke_tested','environment must be smoke_tested before full render')
        for label,paths in [('environment',env.get('smoke_evidence',[])),('preview',p.get('preview_files',[]))]:
            require(bool(paths),label+' evidence files missing')
            for path in paths:require((base/path).is_file(),label+' evidence file not found: '+str(path))
    require(not p.get('unresolved'),'unresolved items remain')
    return errors

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('plan');a.add_argument('--stage',choices=['build','render'],required=True);x=a.parse_args()
    path=pathlib.Path(x.plan).resolve()
    try:
        p=json.loads(path.read_text(encoding='utf-8'));errors=validate(p,x.stage,path.parent)
    except (OSError,ValueError,TypeError,KeyError) as exc:errors=[str(exc)]
    print(json.dumps({'ok':not errors,'stage':x.stage,'errors':errors,'note':'Record checks do not establish actual user consent or visual quality.'},ensure_ascii=False,indent=2))
    return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
