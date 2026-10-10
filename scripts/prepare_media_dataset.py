#!/usr/bin/env python3
"""Standardize media to mono 16 kHz/16-bit PCM WAV; make 30 s sample clips."""
from pathlib import Path
import subprocess, json, csv, re
ROOT=Path('/mnt/data')
OUT=ROOT/'standardized_audio'
FULL=OUT/'full_wav'; SAMPLES=OUT/'sample_segments'
FULL.mkdir(parents=True,exist_ok=True); SAMPLES.mkdir(parents=True,exist_ok=True)
EXTS={'.mp3','.m4a','.wav','.mp4','.mov','.mkv','.aac','.flac','.ogg','.webm','.wma','.avi'}
def probe(path):
    p=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,sample_rate,channels,bits_per_sample,bits_per_raw_sample','-of','json',str(path)],capture_output=True,text=True,check=True)
    return json.loads(p.stdout)
def slug(s):
    return re.sub(r'[^A-Za-z0-9._-]+','_',s).strip('._')[:100] or 'media'
def tags(name):
    low=name.lower()
    genre='song/music' if ('song' in low or 'òran' in low or 'oran' in low) else ('narrative/story' if 'story' in low else 'unknown')
    # Do not assign language/dialect based solely on a person's name or ambiguous media.
    language='Scottish Gaelic (title-indicated; audio not independently verified)' if ('òran' in low or 'oran' in low) else 'unknown/not verified'
    return language,'unknown/not verified',genre
media=sorted(p for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() in EXTS)
if not media: raise RuntimeError('No supported media files in /mnt/data')
rows=[]; failures=[]
for i,src in enumerate(media,1):
    fid=f'M{i:03d}_{slug(src.stem)}'
    full=FULL/f'{fid}.wav'; seg=SAMPLES/f'{fid}_sample_000.wav'
    try:
        # Explicitly map first audio stream (some MP3 containers also expose cover art as video).
        subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-i',str(src),'-map','0:a:0','-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(full)],check=True,capture_output=True)
        info=probe(full); duration=float(info['format']['duration'])
        # A representative sample for taxonomy coding, not a claim of utterance/VAD boundaries.
        segdur=min(30.0,duration)
        subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-i',str(full),'-t',f'{segdur:.6f}','-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(seg)],check=True,capture_output=True)
        lang,dialect,genre=tags(src.name)
        rows.append({'file_id':fid,'language':lang,'variety_dialect':dialect,'genre_regime':genre,'duration_sec':round(segdur,3),'sample_rate':16000,'channels':1,'source_file':src.name,'segment_path':str(seg.relative_to(ROOT))})
    except Exception as e:
        failures.append((str(src),str(e)))
manifest=OUT/'dataset_manifest.csv'
with manifest.open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=['file_id','language','variety_dialect','genre_regime','duration_sec','sample_rate','channels','source_file','segment_path']); w.writeheader(); w.writerows(rows)
# Validate full WAV and segment codec properties and expected output existence.
checks=[]
for row in rows:
    full=FULL/(row['file_id']+'.wav'); seg=ROOT/row['segment_path']
    for p in (full,seg):
        inf=probe(p); aud=[s for s in inf['streams'] if s.get('codec_type')=='audio']
        assert p.is_file() and p.stat().st_size>44 and len(aud)==1
        assert aud[0].get('sample_rate')=='16000' and aud[0].get('channels')==1
        assert int(aud[0].get('bits_per_sample') or aud[0].get('bits_per_raw_sample') or 0)==16, (p,aud[0])
        checks.append(p)
print(json.dumps({'media_found':len(media),'successful':len(rows),'failures':failures,'manifest':str(manifest),'full_wav_dir':str(FULL),'sample_dir':str(SAMPLES),'sample_duration_total_sec':round(sum(r['duration_sec'] for r in rows),3),'full_duration_total_sec':round(sum(float(probe(FULL/(r['file_id']+'.wav'))['format']['duration']) for r in rows),3),'validated_wav_count':len(checks),'all_wavs_16k_mono_pcm_s16':True,'rows':rows},ensure_ascii=False,indent=2))
if failures: raise SystemExit(1)
