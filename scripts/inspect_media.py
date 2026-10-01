#!/usr/bin/env python3
"""Inspect a real encoded file. Detection logs require review, not automatic quality claims."""
import argparse,json,pathlib,subprocess,sys

def run(args,timeout=180):
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if r.returncode:raise RuntimeError(r.stderr[-3000:])
    return r

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('media');p.add_argument('--out',required=True);a=p.parse_args()
    media=pathlib.Path(a.media).resolve()
    try:
        meta=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(media)]).stdout)
        video=[s for s in meta.get('streams',[]) if s.get('codec_type')=='video'];audio=[s for s in meta.get('streams',[]) if s.get('codec_type')=='audio']
        if not video:raise ValueError('No video stream')
        v=video[0];info={k:v.get(k) for k in ['codec_name','width','height','pix_fmt','r_frame_rate','avg_frame_rate','duration','nb_frames','nb_read_frames']}
        scan=run(['ffmpeg','-hide_banner','-i',str(media),'-an','-vf','blackdetect=d=0.1:pix_th=0.05,freezedetect=n=-50dB:d=1','-f','null','-'])
        detections=[l for l in scan.stderr.splitlines() if 'black_start:' in l or 'freeze_' in l]
        report={'file':str(media),'video':info,'audio_streams':len(audio),'duration':meta.get('format',{}).get('duration'),'detection_log':detections,'requires_visual_review':True,'auditioned':False}
        if audio:
            levels=run(['ffmpeg','-hide_banner','-i',str(media),'-vn','-af','ebur128=peak=true','-f','null','-'])
            report['audio_loudness_summary']=levels.stderr.rsplit('Summary:',1)[-1].strip()
        out=pathlib.Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False));return 1
if __name__=='__main__':sys.exit(main())
