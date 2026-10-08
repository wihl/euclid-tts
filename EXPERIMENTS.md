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
clipping headroom and retention of original overload evidence.
The user subsequently confirmed that the Erasmian drop-off is gone. Its
remaining issue is a synthesized overall tone, compared with Modern Greek.

## Round 4 — bounded naturalness trials

The user asked whether anything else was worth trying. Two additional
one-sentence Google candidates were actually rendered: **en-US-Neural2-F
with lively style**, 14.655 seconds, and **en-US-Chirp3-HD-Leda**, 16.943
seconds. Both use the same 17-word Greek selection, explicit Erasmian IPA,
rate 0.72, three 0.65-second requested phrase pauses and the existing gentle
leveling. Live inventories verified the English female voices. No new
download, training, cloning or Modern pronunciation substitution was used.

Google accepted the full-sentence style markup and phoneme controls. Both
WAV/MP3 pairs decode without clipping; their naturalness and actual sound
realization still need listening. The current WaveNet defaults remain in
place. Neural2 introduces expressive delivery near the reference duration;
Chirp has longer pauses and an active waveform at EOF, so its final word
needs particular attention during playback. Attribute any robotic quality
to unfamiliar phoneme-controlled vocabulary only as an inference, not an
established cause.

The Neural2 style and Chirp SSML features are documented previews. Audio,
JSON and QC are in `output/round-4/`; recipes are in the two
`experiments/round-4-erasmian-*.yaml` files. The comparison report is
`output/naturalness-comparison.md`. Twenty-nine automated tests pass,
including whole-sentence style scope and preservation of the exact phoneme
word sequence. At generation time no subjective winner was claimed.

### Round-4 listening verdict

The user subsequently rejected **Chirp Leda** as terrible and worse than the
preceding iteration. **Neural2 lively** was not too bad overall, but its
words were slurred and poorly enunciated. These are human results; passing
audio-integrity checks did not establish clarity. Neither is promoted.

## Round 5 — course convention audit, then naturalness

The user identified that the Erasmian table lacked the course handout's
written convention. Read-only review covered `GreekAlphabetSequence.pdf`
pp. 1–2 (alphabet), **p. 4** (the diphthong line in this copy), the class-3
study note's “Class pronunciation” bullet, and its cited class-3 / class-2
lecture remarks. The notes override the handout where they differ; no
course file or source Greek was modified and no recording was used.

The audit changed 28 finite word entries and one letter-name entry. README's
pronunciation table gives one row per divergence, citing page/timestamp.
`input/pronunciation-source.json` preserves relative source locators, file
hashes, before/after transcriptions and explicit unresolved choices.

- ευ: /ɛʊ/ → /juː/, handout *feud*, p. 4.
- Standalone υ: /ʊ/ → target /y/, French u / German ü, p. 2. Google en-US
  lacks it: selected rounded high-vowel substitute /uː/ loses frontness.
- Accented ι: /ɪ/ → /iː/, *machine*, p. 2; unaccented ι remains *bit* /ɪ/.
- χ: lexicon target /k/ → /x/, *loch/Bach*, p. 2. Google still receives /k/
  as an explicit same-place substitute that loses frication. χ is not in
  the retained first sentence. Kokoro's pinned vocabulary accepts /y x/
  unchanged, but its American voice's realization has no listening verdict.
- ο: select unmerged American *off* /ɔ/, pp. 1–2, distinguishing α /ɑ/.
  The handout does not specify an English dialect; this is an explicit
  interpretation choice. Ε's expanded epsilon name changes accordingly.
- English /ɹ/ is now recognized as agreeing with *run*, p. 2, rather than
  being an unsupported substitute. Its sound is unchanged.

Retained classroom conventions: silent subscript in τῷ (class 3 `01:03:00`
and `01:18:52`), δέ/δή alike (`01:05:36`; /ɛ/ still a selected shared quality),
delta /d/ (handout *done*, p. 1; class 3 `01:30:12`), rough h in ὅπερ
(`01:32:20`), and ου /uː/ (class 2 `00:45:00`, handout *soup*, p. 4).
αυ /aʊ/ remains explicitly unresolved because these sources do not specify it.

The corrected default was regenerated **before** the naturalness trials:
WaveNet-F, **14.35275 seconds**, one sentence, existing rate/pauses/leveling.
All 31 tests passed. The preceding Erasmian delivery and reports are saved
in `output/round-5/pre-correction/`. Earlier ending-volume measurements
describe that archived waveform; they are not reused as new measurements.
Modern Greek remains the approved, sample-identical 10.317-second excerpt.

| Corrected trial | Purpose | Duration | Result |
| --- | --- | ---: | --- |
| Neural2-F neutral | Remove lively style | 14.353 s | WAV bytes and PCM identical to corrected WaveNet default; no new audition |
| Neural2-F firm | Change full-sentence style while keeping voice/input/pacing | 14.578 s | Distinct waveform, human review pending |
| Neural2-H neutral | Change the verified female stock voice | 12.830 s | Distinct waveform, human review pending |

The neutral duplication is observed for this request; it does not prove the
services always use the same model. Google accepted all 17 word-phoneme tags
in each new trial. Both audible alternatives keep the corrected course and
engine IPA, rate 0.72, three 0.65-second pauses and leveling. No time stretch,
new model download, cloning or training was used. The firm style follows
Google's documented whole-sentence extension. New recipes are in
`experiments/round-5-erasmian-*.yaml`; links and hashes are in
`output/naturalness-comparison.md` and its JSON.

Human listening must still check actual /juː/ and /iː/, vowel separation in
γωνίᾳ/γωνίαν, consonant clarity, audible endings and natural connected rhythm.
The English /uː/ and /k/ substitutes cannot establish exact /y/ and /x/.
Passing file and SSML checks is not a pronunciation or naturalness verdict.
