# Transcription annotation template

The CSV contains one row per standardized sample segment. `segment_id` identifies the sample; `file_id`, `source_file`, language, variety/dialect, and genre/regime are copied from the dataset manifest. `segment_start_sec` and `segment_end_sec` give the sample bounds (the provided sample clips start at 0 seconds). Transcript and annotation columns are intentionally blank.

## Suggested coding values

Use the following controlled values consistently; use `uncertain` when the audio does not support a confident decision, and add detail in `annotator_notes` as needed.

- `error_type`: `substitution`, `deletion`, `insertion`, `normalization` (orthographic/tokenization-only difference), `other`, or `not_applicable`. Identify an error only by comparing ASR output with a verified reference.
- `error_subtype`: free-text specific subtype (e.g. `homophone`, `word-boundary`, `morphology`, `named-entity`); blank if not applicable.
- `error_span`: quote the relevant ASR/reference span and clarify which side it comes from.
- `linguistic_variation`: `none`, `phonological`, `morphological`, `lexical`, `syntactic`, `discourse`, `other`, or `uncertain`; note the form/context where useful.
- `code_switching`: `yes`, `no`, or `uncertain`; optionally identify languages in notes.
- `overlap_or_noise`: `none`, `overlap`, `noise`, `both`, or `uncertain`; describe specifics in notes.
- `confidence`: suggested integer scale 1–5 (1 = low, 5 = high); note the judgment being rated.
- `wer` and `cer`: word/character error rates calculated against the reference transcript, only when both reference and ASR text are available and the normalization/tokenization policy is documented.

## Recognition error vs. linguistic variation

A computational recognition error is a mismatch between what the speaker audibly produced and the ASR transcript, assessed against a human-verified reference. Genuine linguistic variation (including dialect pronunciations, grammatical forms, vocabulary, and code-switching) is a feature of the speech, not an error in itself. Preserve such forms in the reference transcript where possible; annotate variation separately. Count it as an ASR error only if the recognizer misheard or incorrectly rendered the audible form under the chosen transcription convention. Do not infer a dialect or “correct” a speaker from a presumed standard.
