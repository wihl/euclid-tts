# Listening results and follow-up experiments

## Round 1 — listener feedback, 2026-10-08

The user reviewed both default two-sentence samples: Kokoro `af_heart`
Erasmian and Google `el-GR-Chirp3-HD-Aoede` Modern Greek, both at rate 1.0.
Both were judged poor and rushed, with insufficient pauses for enunciation.
The user also reported that a native Greek listener found the Modern sample
unclear and sounding like a mixture of Ancient and Modern pronunciation.
This is human listening feedback, including a second-hand native-speaker
assessment; the earlier automated file-integrity checks did not establish
pronunciation quality. Neither round-1 sample is an accepted final result.

The original audio, metadata and reports are preserved in `output/round-1/`.
The authoritative polytonic text remains unchanged. Follow-up work tests
slower synthesis, explicit pauses at grammatical boundaries, neutral tonos
on monosyllabic function words, and alternative documented voices. Modern
Greek pronunciation still reads the Ancient wording; it is not a translation.

## Public repository paths

Source provenance uses paths relative to the external course-materials root.
Project documentation, metadata and reports must not record personal absolute
home-directory paths. Credentials, private recordings, environments and model
caches remain outside the published project files.

## Round 2 — generated trials, 2026-10-08

Five first-sentence controls were rendered at rate 0.82 with explicit phrase
pauses. They range from 8.74 seconds (Greek WaveNet) to 13.93 seconds (Greek
Chirp). All services accepted SSML; decoded audio contains the requested
clause gaps. WaveNet remained relatively brisk, prompting a more deliberate
full comparison at rate 0.72 with 0.65-second phrase, 0.85-second comma,
1.15-second section and 1.30-second sentence pauses.

| Full candidate | Input change | Measured duration |
| --- | --- | ---: |
| Google en-US-Wavenet-F Erasmian | Word-level IPA, slower rate, explicit pauses | 54.162 s |
| Kokoro af_heart Erasmian | Separate breath groups, slower rate, explicit pauses | 48.803 s |
| Google el-GR-Wavenet-B Modern | Normalized accents, slower rate, SSML pauses | 38.755 s |
| Google el-GR-Wavenet-B Modern spelling trial | Explicit modern sound cues, same rate/pauses | 39.087 s |
| Google el-GR-Chirp3-HD-Aoede Modern | Normalized accents, slower rate, SSML pauses | 56.092 s |

These are generation and measurement results, not new listening verdicts.
Both revised default files use alternative WaveNet voices. Kokoro and Chirp
remain available, and the phonetic-spelling intervention can be compared
against normalized WaveNet. Ancient wording and inflections remain intact;
the Modern samples are not translations. No word-level diagnosis is yet
available for the reported pronunciation mixture.

All five full revisions have zero raw overloads; all 42 saved WAV/MP3 files
decode without clipping. Twenty-four automated tests pass, including source
preservation, SSML word/letter coverage, request byte limits and actual PCM
pause placement. The public-path scan passes. The latest measured report
and audio links are in `output/model-comparison.md`; recipes for both the
short controls and full comparisons are in `experiments/`.
