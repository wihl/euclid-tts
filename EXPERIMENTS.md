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

These were generation and measurement results before the next listening review.
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

## Round 3 — approval, quiet endings and shorter delivery

The user judged the revised default readings much better. A native Greek
speaker, as reported by the user, judged the default normalized Modern
WaveNet reading accurate. This supersedes the previous mixed-pronunciation
report for that reading, without establishing results for the Chirp or
phonetic-spelling alternatives. The user reported that some Erasmian word
endings tailed off too quietly, and requested only the first sentence because
the longer paused clips were too long for presentation.

The reviewed two-sentence defaults and pre-review reports are preserved in
`output/round-2/reviewed-defaults/`. Current defaults select the 17-word
enunciation, retain rate 0.72 and three 0.65-second phrase pauses, and last
**14.364 seconds Erasmian** and **10.317 seconds Modern Greek**. The delivered
Modern WAV is a lossless PCM excerpt of the approved performance; the longer
source and the excerpt agree sample for sample. No new Modern pronunciation,
pace or volume settings were introduced.

A diagnostic Google render with 17 word-mark timestamps matches the reviewed
Erasmian first sentence exactly after its saved export gain. Energy in the
last 200 ms of active endings drops noticeably: the final `συστήσασθαι`
ending is about 11 dB below its stronger region. These windows include
natural consonant and stress effects, so they do not imply a pronunciation
error or prove that every quiet word is problematic.

Gentle 2:1 compression at -24 dBFS with +6 dB makeup and a compensated peak
limiter raises the endings without stretching or resynthesizing phonemes:

| Ending | Original RMS | Leveled RMS | Change |
| --- | ---: | ---: | ---: |
| εὐθείᾳ | -25.8 dBFS | -21.5 dBFS | +4.3 dB |
| εὐθυγράμμῳ | -24.5 dBFS | -20.8 dBFS | +3.6 dB |
| συστήσασθαι | -31.8 dBFS | -25.1 dBFS | +6.7 dB |

The comparisons use identical timestamped windows. Detailed measurements and
audio fingerprints are in `output/erasmian-level-check.json`. Modern Greek
does not receive this processing. Twenty-seven automated tests pass,
including quiet-region audibility, preserved silent gaps and frame counts,
clipping headroom and retention of original overload evidence. Listening
approval of the new Erasmian volume adjustment remains pending.
