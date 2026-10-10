#!/usr/bin/env python3
"""Populate verified references and illustrative ASR drafts in the annotation CSV.
Draft hypotheses are deliberately labeled as simulated/error-aware drafts, not model output.
WER: casefolded word tokens with punctuation removed; CER: casefolded NFC characters
with whitespace removed. Both use Levenshtein distance / reference length.
"""
import csv, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'standardized_audio' / 'transcription_annotation_in_progress.csv'
OUTPUT = ROOT / 'transcription_annotation_populated.csv'

def norm(s):
    s = unicodedata.normalize('NFC', s or '').casefold()
    return s

def words(s):
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)*", norm(s), flags=re.UNICODE)
def chars(s):
    return ''.join(c for c in norm(s) if not c.isspace())
def distance(a, b):
    prev = list(range(len(b)+1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(cur[-1]+1, prev[j]+1, prev[j-1]+(x != y)))
        prev = cur
    return prev[-1]
def rate(ref, hyp, tokenize):
    r, h = tokenize(ref), tokenize(hyp)
    return distance(r, h) / max(1, len(r))

# Match by stable source filename / segment prefix, leaving all other rows untouched.
entries = [
 {'match':'A Story of Second Sight [485409450].m4a','id_prefix':'M001_',
  'ref':"There was ah we talk talk about it earlier on and we call it a pash. That is for seeing something that's to happen. And it was shortly after my father married his first wife.",
  'hyp':"There was, uh, we talked about it earlier, and we call it a patch. That is for seeing something that's going to happen. And it was shortly after my father married his first wife.",
  'lang':'English','dialect':'Hebridean/Scots English (verified transcript; fine-grained dialect unverified)',
  'etype':'ASR lexical substitution; disfluency/repetition normalization; function-word/phrase normalization',
  'sub':'pash→patch; repeated talk and hesitation normalized; to happen→going to happen',
  'notes':'Verified reference supplied by user. ASR hypothesis is a deliberately drafted Whisper-style error-aware baseline, not an actual model decode.'},
 {'match':'Courting on Scalpay [485399382].mp3','id_prefix':'M002_',
  'ref':'Well, yes, the the courting as we called it um it it was in in my younger days, well, I I I was participating myself. the in those days there were no cars on the island, there were very few anyway.',
  'hyp':'Well, yes, the courting as we called it, in my younger days, I was participating myself. In those days there were no cars on the island, there were very few anyway.',
  'lang':'English','dialect':'Hebridean/Scots English (verified transcript; fine-grained dialect unverified)',
  'etype':'ASR deletion; disfluency/repetition normalization; sentence-boundary normalization',
  'sub':'Repeated the/it/in/I and hesitation um omitted; lower-case restart normalized',
  'notes':'Verified reference supplied by user. ASR hypothesis is a deliberately drafted normalization-prone baseline, not an actual model decode.'},
 {'match':'Esmail Heydari Ghabrestan.mp3','id_prefix':'M003_',
  'ref':'بسم‌الله‌الرحمن‌الرحیم... بو گؤزل ایامی، بایرامی سیزلره تبریک ائلییرم...',
  'hyp':'Bismillahirrahmanirrahim... Bu güzel günleri, bayramı sizlere tebrik ediyorum...',
  'lang':'Azerbaijani (AZB)','dialect':'Azerbaijani; dialect not independently verified',
  'etype':'ASR language/script hallucination; cross-lingual lexical substitution; transliteration/normalization',
  'sub':'Azerbaijani rendered as Istanbul Turkish in Latin script; əyyamı→günleri and eləyirəm→ediyorum',
  'notes':'Verified reference supplied by user. Hypothesis intentionally models Istanbul-Turkish bias; not an actual ASR decode. Preserve Azerbaijani wording and script in reference.'},
 {'match':'VID_20261009_181945_931.mp4','id_prefix':'M005_',
  'ref':'اَبه بو بیزه باخمیر... باخ گؤر نه دئییر...',
  'hyp':'Ebe bu bize bakmıyor... Bak gör ne diyor...',
  'lang':'Azerbaijani (AZB)','dialect':'Azerbaijani; colloquial variety not independently verified',
  'etype':'ASR language/script hallucination; cross-lingual lexical substitution; phonological normalization',
  'sub':'Azerbaijani rendered as Istanbul Turkish Latin; colloquial forms normalized toward Turkish',
  'notes':'Verified reference supplied by user. Hypothesis intentionally models Istanbul-Turkish bias; not an actual ASR decode.'},
 {'match':'aRgk4-144-1791560805459.mp4','id_prefix':'M007_',
  'ref':'Bismillahir-rəhmanir-rəhim. Bu gözəl əyyamı, bayramı sizlərə təbrik eləyirəm... hər gülün bir iradı var...',
  'hyp':'Bismillahirrahmanirrahim. Bu güzel bayramı sizlere tebrik ediyorum... her gülün bir adı var...',
  'lang':'Azerbaijani (AZB)','dialect':'Azerbaijani; variety not independently verified',
  'etype':'ASR language/variety normalization; lexical substitution; orthographic normalization',
  'sub':'Azerbaijani Latin spelling and ə forms normalized toward Istanbul Turkish; əyyamı/eləyirəm/iradı altered',
  'notes':'Verified reference supplied by user. Hypothesis intentionally models Turkish-centric normalization; not an actual ASR decode.'},
 {'match':'Òran Òil ⧸ Drinking Song - Òran a’ Bhotail [485397105].mp3','id_prefix':'M009_',
  'ref':'Antigonish, Nova Scotia, on 26 May 1953. Mr. Angus MacIsaac, whose forebears came from Moidart, Scotland, is going to sing...',
  'hyp':'Antigonish, Nova Scotia, on May 26, 1953. Mr. Angus Mac Isaac, whose ancestors came from Scotland, is going to sing...',
  'lang':'English','dialect':'English narration introducing Scottish Gaelic/Hebridean material',
  'etype':'ASR normalization; proper-name spelling error; lexical substitution/deletion',
  'sub':'Date reordered; MacIsaac split; forebears→ancestors; Moidart omitted',
  'notes':'Verified reference supplied by user. Hypothesis is a Standard-English normalization-prone illustrative draft, not an actual model decode; retain Gaelic/Hebridean place/name forms.'}
]
with INPUT.open(encoding='utf-8-sig', newline='') as f:
    reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
for e in entries:
    candidates=[r for r in rows if r.get('source_file')==e['match'] and r.get('segment_id','').startswith(e['id_prefix'])]
    if len(candidates)!=1:
        raise ValueError(f"Expected one row for {e['match']} / {e['id_prefix']}; got {len(candidates)}")
    r=candidates[0]
    r.update(language=e['lang'], variety_dialect=e['dialect'],
      reference_transcript=e['ref'], asr_transcript=e['hyp'],
      wer=f"{rate(e['ref'],e['hyp'],words):.6f}", cer=f"{rate(e['ref'],e['hyp'],chars):.6f}",
      error_type=e['etype'], error_subtype=e['sub'],
      error_span='Illustrative draft discrepancy; inspect token-level comparison',
      linguistic_variation='Preserve reference dialect, disfluencies, and nonstandard forms; do not treat as errors in reference',
      code_switching='No verified code-switch in supplied reference; language/script hallucination modeled in draft where noted',
      overlap_or_noise='not assessed from reference text alone', confidence='reference verified by user; ASR draft illustrative only',
      annotator_notes=e['notes'])
with OUTPUT.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f'Wrote {OUTPUT}; updated {len(entries)} rows of {len(rows)} total')
print('Updated IDs and metrics:')
for e in entries:
    r=next(r for r in rows if r['source_file']==e['match'] and r['segment_id'].startswith(e['id_prefix']))
    print(r['segment_id'], 'WER='+r['wer'], 'CER='+r['cer'])
