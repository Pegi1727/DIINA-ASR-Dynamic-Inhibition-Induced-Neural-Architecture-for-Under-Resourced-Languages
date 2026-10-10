#!/usr/bin/env python3
"""Transcribe an audio file in overlapping chunks with local OpenAI Whisper and find target phrases.
Requires: pip install openai-whisper; ffmpeg on PATH; a Whisper model downloaded/available locally.
Example: python search_audio_phrases.py input.mp3 --model small --chunk 60 --overlap 5
"""
import argparse, re, sys

def norm(s):
    s=s.lower().replace("ə", "e").replace("ı", "i")
    return re.sub(r"[^\w]+", " ", s, flags=re.UNICODE).strip()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('audio')
    ap.add_argument('--model', default='small')
    ap.add_argument('--chunk', type=float, default=60)
    ap.add_argument('--overlap', type=float, default=5)
    ap.add_argument('--phrases', nargs='*', default=['Bir dənə mərizin','yetimə başmaq'])
    args=ap.parse_args()
    try:
        import whisper
    except ImportError:
        sys.exit('Missing openai-whisper. Install locally and ensure ffmpeg is available.')
    model=whisper.load_model(args.model)
    # whisper.load_audio decodes to 16 kHz mono; process windows and offset segment timestamps.
    audio=whisper.load_audio(args.audio)
    rate=16000; total=len(audio)/rate
    step=args.chunk-args.overlap
    if step <= 0: sys.exit('--chunk must exceed --overlap')
    targets=[norm(x) for x in args.phrases]
    found=[]
    start=0.0
    while start < total:
        end=min(start+args.chunk,total)
        chunk=audio[int(start*rate):int(end*rate)]
        result=model.transcribe(chunk, language='az', fp16=False, verbose=False)
        for seg in result.get('segments', []):
            text=seg['text'].strip(); nt=norm(text)
            if any(t in nt for t in targets):
                found.append((start+seg['start'], start+seg['end'], text))
        start+=step
    if found:
        for a,b,t in found: print(f'{a:.2f}-{b:.2f}s\t{t}')
    else:
        print('No exact phrase match; inspect transcript manually (ASR may miss Azerbaijani wording).')
if __name__=='__main__': main()
