#!/usr/bin/env python3
"""Refresh reference metadata and make an explainable, deduplicated shortlist. Stdlib only."""
import argparse, datetime, hashlib, html, json, pathlib, re, sys, urllib.request

SOURCES = {
    'yihui': 'https://raw.githubusercontent.com/yihui-dev/awesome-opus5-5-videos/main/data/videos.json',
    'guanmo': 'https://raw.githubusercontent.com/guanmo-ai/awesome-ai-motion/main/data/cases.json',
    'lemo': 'https://raw.githubusercontent.com/lemomo-ai/lemo-opuscar/main/styleboard/catalog.json',
}
GROUPS = {
    'product': ['product', 'promo', 'saas', 'launch', '产品', '宣传', '广告'],
    'explainer': ['explainer', 'explain', 'education', 'tutorial', '讲解', '科普', '教学', '教程'],
    'chat': ['chat', 'message', 'conversation', '聊天', '回复', '消息', '对话', '微信'],
    'ui': ['interface', 'dashboard', 'screen', ' ui ', '界面', '面板', '卡片', '录屏'],
    'typography': ['typography', 'kinetic', 'swiss', 'type ', '排版', '大字'],
    '3d': ['three.js', 'threejs', 'three', 'webgl', '3d', '空间'],
    '2.5d': ['2.5d', 'isometric', 'parallax', 'orthographic', '等距', '视差'],
    'glass': ['glass', '玻璃'], 'metal': ['chrome', 'metal', '金属'],
    'particles': ['particle', '粒子'], 'morph': ['morph', '变形', '形变'],
    'paper': ['paper', 'collage', '纸', '拼贴'],
    'handdrawn': ['watercolor', 'painted', 'brush', 'hand-drawn', '手绘', '水彩', '彩铅'],
    'whiteboard': ['whiteboard', '白板'], 'pixel': ['pixel', '像素'],
    'retro': ['retro', 'crt', 'vhs', '复古'], 'dark': ['dark', 'black', '暗', '黑'],
    'minimal': ['minimal', '极简'], 'music': ['music', 'lyric', '音乐', '歌词'],
    'character': ['character', 'cartoon', '角色', '人物', '卡通'],
    'motion': ['motion', '动效', '动态', 'showreel'],
}
CATEGORIES = {'产品宣传':'product','知识讲解':'explainer','短动效':'motion','3D 与交互':'3d','像素与角色':'character','叙事短片':'story','音乐与歌词':'music'}

def tags(text):
    text = ' ' + text.lower() + ' '
    return sorted(k for k, aliases in GROUPS.items() if any(a in text for a in aliases))

def safe_url(value):
    return value if isinstance(value, str) and value.startswith(('https://', 'http://')) else ''

def number(value):
    return float(value) if isinstance(value, (int, float)) and value > 0 else None

def identity(url, fallback):
    match = re.search(r'(?:twitter|x)\.com/[^/]+/status/(\d+)', url)
    return 'post:' + match[1] if match else fallback

def normalize(source, data):
    rows = data.get('cases') if source == 'guanmo' and isinstance(data, dict) else data
    if not isinstance(rows, list) or not rows:
        raise ValueError('Upstream schema changed: expected a nonempty list')
    out = []
    for x in rows:
        if not isinstance(x, dict):
            raise ValueError('Invalid row')
        if source == 'yihui':
            slug, url = x.get('slug'), safe_url(x.get('post_url'))
            if not slug or not url:
                raise ValueError('Missing slug/post_url')
            inferred = tags(x.get('prompt','') + ' ' + ' '.join(x.get('tech_tags',[])))
            row = dict(id=identity(url,'yihui:'+slug), title='@'+x.get('author','unknown')+' · '+', '.join(inferred or [x.get('category','motion')]),
                summary='', author=x.get('author',''), category=x.get('category','unknown'), duration=None,
                source_url=url, watch_url=safe_url(x.get('skillry_url')) or url, video_url='',
                poster_url=safe_url(x.get('poster_url')), tags=inferred, tech_tags=x.get('tech_tags',[]),
                prompt_status='partial' if x.get('prompt_partial') else ('published_text' if x.get('prompt') else 'unknown'),
                prompt_url=f'https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/{slug}.md', code_url='',
                entry_type='video')
        elif source == 'guanmo':
            url = safe_url(x.get('source',{}).get('url'))
            if not x.get('id') or not url:
                raise ValueError('Missing id/source.url')
            description = x.get('summary','')
            row = dict(id=identity(url,'guanmo:'+x['id']), title=x.get('title','Untitled'), summary=description,
                author=x.get('author',{}).get('handle',''),category=CATEGORIES.get(x.get('category'),x.get('category','unknown')),
                duration=number(x.get('media',{}).get('durationSeconds')),source_url=url, watch_url=url,
                video_url=safe_url(x.get('webPlayback',{}).get('url')),
                poster_url=('https://guanmo-ai.github.io/awesome-ai-motion/'+x['cover']['path']) if x.get('cover',{}).get('path') else '',
                tags=tags(description+' '+x.get('title','')+' '+x.get('summaryEn','')),tech_tags=[],
                prompt_status=x.get('prompt',{}).get('status','unknown'),prompt_url=safe_url(x.get('prompt',{}).get('sourceUrl')) or url,
                code_url=safe_url(x.get('codeUrl')),entry_type='video')
            row['resources'] = [{k:r.get(k) for k in ('kind','url','label','license','licenseUrl')} for r in x.get('resources',[]) if safe_url(r.get('url'))]
        else:
            slug=x.get('slug')
            if not slug:
                raise ValueError('Missing style slug')
            base=f'https://github.com/lemomo-ai/lemo-opuscar/tree/main/styles/{slug}'
            row=dict(id='lemo:'+slug,title=x.get('cn',slug)+' / '+x.get('en',slug),summary=x.get('line_cn',x.get('line','')),
                author='LemoLab',category='style',duration=number(x.get('dur')),source_url=base,watch_url=base,
                video_url='',poster_url='',tags=tags(' '.join(x.get('uses',[]))+' '+x.get('en','')+' '+x.get('cn','')+' '+slug),
                tech_tags=[],prompt_status='style_document',prompt_url=base.replace('/tree/','/blob/')+'/STYLE.md',code_url=base+'/demo',entry_type='style')
        row['sources']=[source]
        row['source_links']=[row['source_url']]
        row['review_status']='metadata_only'
        row['tag_evidence']='derived_from_metadata'
        out.append(row)
    return out

def merge(rows):
    merged={}
    for row in rows:
        key=row['id']
        if key not in merged:
            merged[key]=row; continue
        old=merged[key]
        for field in ('tags','tech_tags','sources','source_links'):
            old[field]=sorted(set(old.get(field,[])+row.get(field,[])))
        if row.get('summary'):
            old['summary']=row['summary'];old['title']=row['title'];old['category']=row['category']
        for field in ('video_url','duration','poster_url','code_url','resources'):
            if not old.get(field) and row.get(field):old[field]=row[field]
        if old.get('prompt_status') in ('unknown','partial') and row.get('prompt_status') not in ('unknown','partial'):
            old['prompt_status']=row['prompt_status'];old['prompt_url']=row['prompt_url']
    return list(merged.values())

def write_json(path, data):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def refresh(args):
    rows=[];statuses=[]
    for source,url in SOURCES.items():
        try:
            local=getattr(args,source)
            if local:raw=pathlib.Path(local).read_bytes()
            else:
                req=urllib.request.Request(url,headers={'User-Agent':'motion-director-catalog/1'})
                with urllib.request.urlopen(req,timeout=25) as response:raw=response.read(8*1024*1024+1)
            if len(raw)>8*1024*1024:raise ValueError('Source exceeds 8 MiB limit')
            result=normalize(source,json.loads(raw))
            rows+=result
            statuses.append(dict(source=source,url=url,status='ok',records=len(result),sha256=hashlib.sha256(raw).hexdigest()))
        except Exception as exc:
            statuses.append(dict(source=source,url=url,status='failed',error=str(exc)))
    result=dict(schema_version=1,fetched_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_status=statuses,entries=merge(rows))
    write_json(args.out,result)
    print(json.dumps({'out':args.out,'entries':len(result['entries']),'source_status':statuses},ensure_ascii=False))
    return 0 if all(s['status']=='ok' for s in statuses) else 2

def search(args):
    catalog=pathlib.Path(args.catalog) if args.catalog else pathlib.Path(__file__).resolve().parents[1]/'assets/catalog.json'
    data=json.loads(catalog.read_text(encoding='utf-8'))
    query=args.query.strip().lower();tokens=re.findall(r'[\w.+-]+',query)
    qtags=tags(query);results=[]
    for row in data['entries']:
        if args.category and row['category']!=args.category and args.category not in row['tags']:continue
        hay=' '.join([row['title'],row.get('summary',''),row['category'],' '.join(row['tags']),' '.join(row.get('tech_tags',[]))]).lower()
        matches=[t for t in tokens if t in hay]
        overlap=sorted(set(qtags)&set(row['tags']))
        lexical=len(matches)*3+len(overlap)*5
        if query and lexical==0:continue
        reasons=[f'keyword:{m}' for m in matches]+[f'tag:{m}' for m in overlap]
        score=lexical
        if args.duration and row.get('duration'):
            proximity=max(0,1-abs(row['duration']-args.duration)/max(args.duration,1));score+=2*proximity
            reasons.append('duration_known')
        if row.get('video_url'):score+=0.5
        results.append(dict(row,match_score=round(score,2),match_reasons=reasons))
    results.sort(key=lambda r:(-r['match_score'],r['id']))
    result={'catalog_date':data.get('fetched_at'),'source_status':data.get('source_status',[]),'query':args.query,'total_matches':len(results),'zero_matches':len(results)==0,'score_kind':'lexical_prefilter_not_visual_quality','candidates':results[:args.limit]}
    if args.out:write_json(args.out,result)
    if args.board:board(args.board,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

def board(path, result):
    esc=html.escape;cards=[]
    for i,r in enumerate(result['candidates'],1):
        poster=f'<img loading="lazy" referrerpolicy="no-referrer" src="{esc(safe_url(r.get("poster_url")),quote=True)}" alt="参考封面；不是运动核验" onerror="this.hidden=true">' if r.get('poster_url') else ''
        video=f'<video controls preload="none" playsinline src="{esc(safe_url(r.get("video_url")),quote=True)}"></video>' if r.get('video_url') else ''
        links=' '.join(f'<a target="_blank" rel="noopener noreferrer" href="{esc(safe_url(r.get(k)),quote=True)}">{label}</a>' for k,label in [('watch_url','查看作品/目录'),('source_url','原始出处'),('prompt_url','提示词/风格说明'),('code_url','实现入口')] if safe_url(r.get(k)))
        cards.append(f'<article><h2>{i}. {esc(r["title"])}</h2><p>@{esc(r["author"])} · {r.get("duration") or "时长未知"} · {esc(r["entry_type"])}</p>{poster}{video}<p>{esc(r.get("summary",""))}</p><p>{esc(", ".join(r["tags"]))}</p><p class="note">仅元数据初筛；打开播放不自动标记为 agent 已核验。</p><nav>{links}</nav></article>')
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Motion 参考候选</title><style>body{font:16px/1.6 system-ui;margin:32px;background:#f5f4ef;color:#191919}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{background:white;padding:20px;border:1px solid #ddd;border-radius:14px}img,video{width:100%;max-height:270px;object-fit:contain}nav{display:flex;gap:15px;flex-wrap:wrap}.note{color:#666;font-size:14px}h2{font-size:20px}</style><h1>参考候选</h1><p>选择编号后回到对话告诉 agent；可分别选择节奏、构图和转场。封面/播放器引用原始来源，不托管视频。</p><p>数据日期：'+esc(str(result['catalog_date']))+'</p><main>'+''.join(cards)+'</main></html>'
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(page,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
    r=subs.add_parser('refresh');r.add_argument('--out',required=True)
    for name in SOURCES:r.add_argument('--'+name,help='Local upstream JSON instead of network')
    s=subs.add_parser('search');s.add_argument('--catalog');s.add_argument('--query',required=True);s.add_argument('--category');s.add_argument('--duration',type=float);s.add_argument('--limit',type=int,default=12);s.add_argument('--out');s.add_argument('--board')
    args=p.parse_args()
    if getattr(args,'limit',1)<1:p.error('--limit must be positive')
    return refresh(args) if args.command=='refresh' else search(args)
if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,KeyError) as exc:print('catalog error: '+str(exc),file=sys.stderr);sys.exit(2)
