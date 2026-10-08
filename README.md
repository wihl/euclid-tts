# Euclid I.23: two pronunciation experiments

This project reads the opening of *Elements* I.23 in (1) Anglophone Erasmian
classroom pronunciation with **stress**, and (2) Modern Greek with a female
voice. WAV is the PCM master; MP3 is the Google Slides copy. This is a short
experiment for MATH E-139, taught by Graeme Bird. All code and phonetic
transcriptions were prepared with AI assistance. No professor's voice is
cloned, adapted, or used to train a model.

## Final MP3s for the presentation

Insert these two files from this project's local `output/` directory into
your presentation:

- **Erasmian:** [output/euclid-I23-erasmian.mp3](output/euclid-I23-erasmian.mp3)
  — the user-accepted Neural2-H reading, **12.83 seconds**.
- **Modern Greek female:** [output/euclid-I23-modern-female.mp3](output/euclid-I23-modern-female.mp3)
  — the native-speaker-approved WaveNet reading, **10.32 seconds**.

Both contain only the same complete opening sentence. Their WAV masters
and JSON metadata are beside them. These generated audio files are saved
locally and excluded from Git, so the public repository does not include
the MP3s. Use the saved files for the accepted performances; a fresh cloud
build can vary. Google Slides insertion steps are at the end of this README.

The first samples failed the user's listening review: both sounded rushed,
and a native Greek listener found the Modern reading unclear and mixed.
Feedback is recorded in `EXPERIMENTS.md`; original samples and pre-review
reports are preserved in `output/round-1/`.

The user judged the revised readings much better, and a native Greek speaker
found the default Modern WaveNet reading accurate. The user noted quiet
Erasmian word endings and requested shorter, one-sentence clips.

Final defaults are **Google `en-US-Neural2-H` with course-reconciled Erasmian IPA
and gentle volume leveling** (12.83 seconds) and **`el-GR-Wavenet-B` with
Modern normalized text** (10.32 seconds). Both retain synthesis rate 0.72
and three phrase pauses. The delivered Modern WAV is a lossless excerpt of
the approved performance. The user confirmed that the earlier Erasmian drop-off was
gone, but its tone still sounded less natural than the Modern Greek version.
The course audit corrected the Erasmian targets. The user judged round-5
Neural2-H acceptable; its WAV and MP3 were copied exactly to the default
filenames, without resynthesis. The accepted Modern excerpt remains unchanged.
Chirp Leda was rejected as worse, and Neural2 lively was judged slurred.
The longer reference files are in `output/round-2/reviewed-defaults/`;
Kokoro, Chirp and a Modern phonetic-spelling trial remain in `output/round-2/`.
Measurements and links are in `output/final-report.md` and `model-comparison.md`.

Google authentication, billing and API enablement are set up on the original
machine. Fresh installations need the setup below; no credentials are in
this repository. The earlier Melina female fallback remains a local backup.

The local Erasmian alternative uses the small Apache-2.0
[Kokoro ONNX model](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX),
with manually specified phonemes and its stock American female `af_heart`
voice. It runs on CPU through native ARM64 ONNX Runtime. Model weights are
92.4 MB, plus about 0.52 MB per voice. There is no PyTorch, CUDA, training,
server, or dependency on the course repository after the input is saved.

The current Modern Greek trial uses Google Cloud `el-GR-Wavenet-B`.
The program checks the live inventory for **el-GR and FEMALE** before making
a synthesis request. `backend: auto` falls back to the installed macOS
**Melina** female Greek voice if Google is unavailable. `backend: google_cloud`
fails clearly instead of falling back. Google Cloud TTS and the Gemini API
are different services; this program does not use any keys in `.env`.

## Passage and source

`input/euclid-I23.txt` is the complete polytonic Greek, copied verbatim from
the six `i23` strings in the course's
`coursework/projects/2026-project-i23/greek/writeup.qmd`. Its primary source is
Richard Fitzpatrick's *Euclid's Elements of Geometry* (2007, corrected 2008),
the Greek text of J. L. Heiberg, **Book I, Proposition 23, printed/PDF p. 26**,
Greek column (`materials/books/Elements.pdf` in the course workspace).
The page image and cropped text layer were checked locally. Source paths,
hashes, and typographic extraction differences are in `input/source.json`.
This is the on-disk course edition, not the separately assigned Books 1–4
volume. The course Shiny app was identified from the project brief but its
text was not independently compared.

The default is the **first complete sentence**, the enunciation, with 17
source words in four grammatical breath groups. The selected passage is:

> Πρὸς τῇ δοθείσῃ εὐθείᾳ καὶ τῷ πρὸς αὐτῇ σημείῳ τῇ δοθείσῃ γωνίᾳ εὐθυγράμμῳ ἴσην γωνίαν εὐθύγραμμον συστήσασθαι.

`--sentences 2` remains available for the former 65-token selection. Its raised
dot after ΔΓΕ is an internal pause, so the second sentence includes both the
setting-out and the specification. The complete source text is preserved.

Changing the selection never edits the input. Modern normalization and the
Erasmian phonemes are recorded separately in output JSON files.

## Install and run

Use a native Apple Silicon terminal, with `uv`, `ffmpeg`, `ffprobe`, and, for
the fallback, macOS `say`. Python 3.12.11 was used here. These commands operate
inside a project-local environment/cache and do not change global Python:

```bash
export UV_CACHE_DIR="$PWD/.cache/uv"
uv sync --python 3.12 --locked
uname -m
uv run python -c "import platform; print(platform.machine())"
uv run pytest -q
uv run python -m euclid_tts build
```

Both architecture commands must print `arm64`. The first local Kokoro run
downloads only the pinned model, phoneme vocabulary and selected stock voice
to `.cache/huggingface`. Subsequent local runs reuse them without network
access. `uv.lock` pins Python packages; the synthesis module pins model and
vocabulary revisions and records downloaded file hashes. Memory use for the
tested local voices stayed below 1 GB. The local alternative works without
Cloud access after caching its weights; both current defaults require Google.

Independently generate either voice:

```bash
uv run python -m euclid_tts build --voice erasmian
uv run python -m euclid_tts build --voice modern_female
```

Request two sentences or override synthesis speed:

```bash
uv run python -m euclid_tts build --sentences 2 --output-dir work/two-sentences
uv run python -m euclid_tts build --voice erasmian --sentences 1 --rate 0.82 --output-dir work/slower
uv run python -m euclid_tts qc
```

`--rate` controls synthesis speed, not playback speed. The accepted range is
0.7–1.3. The macOS fallback scales its words-per-minute setting. Google rate
support is validated by actually submitting requests; a service error is
reported rather than claiming an ignored setting worked.

Edit `config.yaml` to persist `speech.rate`, `passage.sentence_count`, voice,
backend, pause durations, output directory or formats. `passage.selection: full` selects all
five complete sentences; full synthesis is supported but was not part of the
initial run. The Erasmian lexicon is deliberately limited to this proposition.
Unknown words or model phonemes fail instead of being dropped. A WAV master
is always retained, including when MP3 is the only requested export format.

An alternative configuration can be used with
`uv run python -m euclid_tts --config path/to/config.yaml build`.

## Follow-up comparisons and pauses

Regenerate the historical five full samples and five short controls, then
build the current one-sentence defaults and reports:

```bash
uv run python tools/round_two.py
```

Or render one alternative independently:

```bash
uv run python -m euclid_tts --config experiments/round-2-erasmian-kokoro.yaml build
uv run python -m euclid_tts --config experiments/round-2-modern-chirp.yaml build
uv run python -m euclid_tts --config experiments/round-2-modern-wavenet-respelled.yaml build
uv run python -m euclid_tts --config experiments/short/round-2-modern-wavenet.yaml build
```

Full recipes use rate 0.72; short controls use 0.82 and shorter pauses.
Both sets have saved configurations. Cloud output can vary between calls.
The current opening sentence has four breath groups and three gaps totaling
1.95 seconds. Historical two-sentence samples have eleven groups and ten
gaps totaling 8.05 seconds. Both preserve all selected words and labels:

```yaml
speech:
  rate: 0.72
  pauses:
    phrase: 0.65
    comma: 0.85
    section: 1.15
    sentence: 1.3
```

Pause durations accept 0.15–2.0 seconds. Google receives `<break>` tags
within sentence/section requests; explicit PCM silence separates those
requests. Kokoro renders breath groups separated by PCM silence. Engine
silence can add to the settings; decoded pause measurements are recorded.
The optional macOS fallback uses native punctuation rather than these explicit
pause controls. Defaults require Google so fallback cannot replace the trials.

## Erasmian word-ending volume

Historical word-mark timestamps from Google locate the pre-correction sentence's words.
The diagnostic waveform matches the reviewed Erasmian first sentence after
applying its saved export gain. The last 200 ms of the final active word
region drops about 11 dB below the stronger part of `συστήσασθαι`.
Some soft consonants and unstressed syllables are naturally quieter; these
measurements support the user's report without diagnosing a pronunciation error.

`voices.erasmian.level_speech: true` applies gentle 2:1 compression above
-24 dBFS, +6 dB makeup gain and a peak limiter. Measured ending RMS increases
are +4.3 dB for `εὐθείᾳ`, +3.6 dB for `εὐθυγράμμῳ`, and +6.7 dB for
`συστήσασθαι`. Processing preserves the sample count and pause timing;
WAV/MP3 exports have no clipping. The user confirmed that the stronger
Erasmian endings resolve the drop-off. Set the flag to `false` to compare
the untreated reading.
Modern Greek receives no volume leveling. The exact filter, source overloads
and export measurements are saved in voice metadata; word windows and file
fingerprints are in `output/erasmian-level-check.json`.
Those ending measurements describe the archived pre-correction waveform,
not the fresh course-corrected render. The same leveling remains enabled.

## Final Erasmian selection and naturalness comparisons

The user rejected round-4 Chirp Leda as worse than the preceding version.
Neural2 lively was somewhat better but had slurred, poorly enunciated words.
Both used the old lexicon; their files remain as historical failed comparisons.

After regenerating the corrected WaveNet reference (14.353 seconds), round 5
compared Neural2-F with neutral delivery and full-sentence `firm` style,
and a different stock female voice, Neural2-H. All retain the
corrected phonemes, rate 0.72, three 0.65-second phrase pauses and leveling.
This tests removing lively delivery, changing style to seek clearer
enunciation, and changing the neutral voice. Neural2-F neutral returned the
**exact same WAV bytes and PCM as the corrected WaveNet reference**, so it adds no
audition. Firm F is distinct at **14.578 seconds**; neutral H is distinct at
**12.833 seconds**. The user judged **Neural2-H acceptable**, and it is now
the default. Firm F remains unreviewed and was not selected. The accepted
files are preserved in `output/round-5/neural2-h/` and copied byte for byte
to `output/euclid-I23-erasmian.{wav,mp3}`. Corrected WaveNet is archived in
`output/round-5/corrected-wavenet-reference/`.
The firm trial's Google source PCM contains 12 full-scale samples before
leveling; QC retains that evidence. Corrected WaveNet and H have zero source
overloads. All exported WAV/MP3 files decode without clipping.

```bash
uv run python -m euclid_tts --config experiments/round-5-erasmian-neural2-firm.yaml build
uv run python -m euclid_tts --config experiments/round-5-erasmian-neural2-h.yaml build
```

`output/naturalness-comparison.md` records the verdicts and retained comparisons.
The bounded naturalness experiment is complete; further voice trials are
not required for this presentation. Cloud reruns may differ from the accepted
saved performance even with identical settings.
The [Neural2 expressive-style feature](https://docs.cloud.google.com/text-to-speech/docs/ssml#styles)
and [Chirp SSML support](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd)
are currently preview. Styles are wrapped around a complete sentence; the
prototype requires `en-US-Neural2-F` and refuses styles on split clauses.
The phonetic target stays Anglophone Erasmian with stress accent. Expressive
sentence intonation does not implement historical Greek pitch accent.

## Pronunciation conventions and evidence

**The timestamped class remarks override the handout; the handout governs
where the remarks are silent.** The following locators are relative to the
external course workspace, which was read without modification:

- **H**: `materials/course/greek-resources/GreekAlphabetSequence.pdf`, alphabet
  pp. 1–2. In this four-page copy, “A few hints for reading Greek” and the
  diphthong line are on **p. 4**, not p. 2; both text and page images were checked.
- **S3**: `coursework/study/class-03-greek-notes.md`, “Class pronunciation” bullet.
- **C3**: `coursework/lectures/2026-class-03/lecture-note.md`, timestamps below.
- **C2**: `coursework/lectures/2026-class-02/lecture-note.md`, pronunciation at
  `00:45:00–00:45:23`.

The pronunciation table has one row per divergence, including documentation
errors and explicit engine compromises. `input/pronunciation-source.json`
records source hashes, locators and all 29 changed word/letter entries.

| Feature / divergence | Previous value | Course target and actual engine input | Evidence |
| --- | --- | --- | --- |
| ευ | /ɛʊ/ | **/juː/**, the vowel/glide sequence in *feud*, including stressed εύ in ἐπεζεύχθω. Google receives /juː/. | H p. 4, diphthong line |
| Standalone υ (outside a diphthong) | /ʊ/ | **/y/**, high front rounded German ü / French u. Google en-US lacks /y/: selected nearest rounded high-vowel substitute **/uː/** loses frontness, so this is not exact. Kokoro's pinned vocabulary accepts /y/ directly; stock American-voice realization is unverified. | H p. 2, υ |
| Accented ι, including grave | /ɪ/ throughout | **/iː/** as in *machine*: γωνίᾳ, γωνίαν, γωνία, ἴσην, ἴση, ἴσαι, τρίγωνον, εἰσὶν, τρισὶ. Unaccented ι remains /ɪ/ as in *bit*; ει follows its separate diphthong rule. | H p. 2, ι; H p. 4, accented vowel marked |
| χ | /k/ described as the target | **/x/** as in *loch/Bach* in τυχόντα and ἐπεζεύχθω. Google en-US lacks /x/: selected same-place substitute **/k/** retains velar articulation but loses frication. Its actual input remains /k/ for this explicit engine reason. Kokoro accepts /x/ directly, unverified by ear. χ does not occur in the retained first sentence. | H p. 2, χ |
| ο versus α | Both /ɑ/, silently merged | Select unmerged American **off /ɔ/** for ο, retaining **father /ɑ/** for α; Google uses /ɔː/ and /ɑː/. The handout does not fix an English dialect, so merged /ɑ/ can also be an American *off*; the chosen distinction is an implementation choice, not an attested Bird vowel. | H p. 1, α; H p. 2, ο |
| Ε, expanded epsilon label | /ˈɛpsɪlɑn/ | **/ˈɛpsɪlɔn/**; its omicron follows the selected *off* vowel. Α/Β/Γ/Δ/Ζ/Η were checked and remain unchanged: α=father, η=late, ζ=zoo, stop β/γ/δ. | H pp. 1–2; ο p. 2 |
| ρ described as an English compromise | /ɹ/, previously said to replace a Greek rho | **/ɹ/** is supported by the handout's *run*. Sound unchanged; the claim that it diverges from the course convention is removed. | H p. 2, ρ |
| δέ / δή versus the handout's ε / η distinction | Both /dɛ/ | Keep both **/dɛ/** because Bird specifies equality. The notes do not transcribe the shared vowel: /ɛ/ remains an explicit selected quality, not a claim of exact recorded pronunciation. Elsewhere η remains /eɪ/ as in *late*. | C3 `01:05:36–01:05:54` overrides H p. 1; S3 |

All four flagged features differ at the **course-target** level. χ has no
change in Google's actual /k/ input because the engine cannot represent its
specified /x/, not because the old target was correct. Google's documented
[en-US phoneme inventory](https://docs.cloud.google.com/text-to-speech/docs/phonemes)
lacks both /y/ and /x/. The substitutes above prioritize height/rounding for
υ and place for χ; no uniquely closest substitute is established by these
sources. Metadata exposes `ipa` (course targets), `engine_ipa` (submitted
sounds), and `phoneme_substitutions` with affected words and reasons.

Other checked conventions already agree: β/γ/δ are /b ɡ d/ (H p. 1;
C3 `01:30:12` for the delta correction); θ/φ are /θ f/ (H pp. 1–2);
η/ω are /eɪ oʊ/ (H pp. 1–2); αι/ει/οι are /aɪ eɪ ɔɪ/ (H p. 4).
ου remains /uː/, matching H p. 4's *soup* and C2 `00:45:00–00:45:23`'s *oo*.
Rough /h/ is retained (H p. 1; ὅπερ at C3 `01:32:20`, surrounding
`01:29:50–01:32:25`). τῷ remains /toʊ/, silent subscript, per C3
`01:03:00–01:03:09` and `01:18:52–01:19:25`; extending this to other
subscripted inflections is stated explicitly. αυ /aʊ/ remains unresolved:
the handout's diphthong list omits it and these remarks do not settle it.
Stress follows the accented syllable, as requested; no historical pitch
accent, comprehensive quantity or gemination is implemented. The lecture
recordings were not opened and no speaker voice was imitated.

`LEXICON` and `ERASMIAN_LETTERS` store course targets. Kokoro uses tokens
`A/I/O/W` for English diphthongs; all tokens, including /y x/, are checked
against its pinned vocabulary. Google wraps each word and expanded letter
name in an English IPA `<phoneme>` tag, applying documented approximations
separately. /ɑː ɔː iː uː/ are English sound/encoding choices, not an assertion
of Greek vowel quantity. Both final modes preserve the same Greek selection.

Modern normalization maps acute/grave/circumflex to tonos, removes breathings
and iota subscripts, keeps diaeresis, and expands labels. Raised dots become
commas for pauses: a semicolon would be a Greek question mark. It retains Ancient
Greek words and inflections: this is their pronunciation with Modern Greek
sounds, not a Modern Greek translation. Monosyllabic function words now omit
tonos according to the [Modern convention](https://www.greek-language.gr/greekLang/modern_greek/tools/lexica/triantafyllides/search.html?lq=%CF%84%CE%BF%CE%BD%CE%AF%CE%B6%CF%89).
The optional `modern_female.input: respelled` trial makes /i/ and /ef, af/
explicit in unfamiliar Ancient forms: `δοθείσῃ` → `δοθίσι`, `εὐθείᾳ` →
`εφθία`, `συστήσασθαι` → `σιστίσασθε`. These are phonetic input cues,
not proper Greek orthography. Their effectiveness needs human review.

## Google Cloud TTS Setup

Follow Google's [getting-started guide](https://cloud.google.com/text-to-speech/docs/get-started)
and [authentication documentation](https://cloud.google.com/text-to-speech/docs/authentication).

1. Create or select a Google Cloud project in the Cloud Console. With the
   CLI, an existing project can be selected with `gcloud config set project
   PROJECT_ID`; a new one can be created with `gcloud projects create PROJECT_ID`.
2. Link a billing account using the Console's **Billing** page. Billing is
   required even when the short samples fall within a free allowance.
3. Enable **Cloud Text-to-Speech API**, not only Gemini:

   ```bash
   gcloud services enable texttospeech.googleapis.com --project=PROJECT_ID
   ```

4. Install the Google Cloud CLI if needed, using Google's macOS instructions.
   Use your own user credentials through **Application Default Credentials**:

   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project PROJECT_ID
   ```

   The quota project needs billing, the enabled API, and permission for your
   principal to use services (normally `roles/serviceusage.serviceUsageConsumer`).
   The account enabling the API needs the appropriate Service Usage permission.
   `gcloud auth login` and Application Default Credentials are separate stores.
   On macOS, user ADC normally lives at
   `~/.config/gcloud/application_default_credentials.json`. Keep it outside
   this repository. No copy of it is needed here.
5. Verify authentication and Greek female availability without displaying
   tokens:

   ```bash
   uv run python -m euclid_tts voices
   uv run python -m euclid_tts build --voice modern_female
   ```

   Select `backend: google_cloud` in the configuration to require the cloud
   voice. Under `auto`, read the output JSON to see whether fallback occurred.
   `RefreshError` usually means reauthentication is needed. `SERVICE_DISABLED`
   means enable the API in the **ADC quota project**, which can differ from
   the CLI's active project. Billing and IAM errors need the named project's
   account owner to resolve them.
6. For an automated workload, use an attached service account or service
   account impersonation through ADC. If a service-account JSON file is
   unavoidable, keep it outside the repository and set
   `GOOGLE_APPLICATION_CREDENTIALS` to its path. Do not embed credentials in
   Python, YAML, command output, logs or Git.
7. Google's [current pricing](https://cloud.google.com/text-to-speech/pricing)
   lists Chirp 3 HD at $30 per million characters beyond a 1-million-character
   monthly allowance. WaveNet/Standard is $4 per million beyond a
   4-million-character allowance. **Neural2**, used for the final Erasmian
   voice, is **$16 per million** beyond a 1-million-character allowance.
   The accepted Erasmian request contains 1,008 characters, about **$0.016**
   outside that allowance; the saved Modern request contains 192 characters,
   about **$0.00077**. Rates were checked on 2026-10-08.
   SSML tags count toward billable characters;
   output JSON records request character counts and byte sizes. Short WaveNet
   requests cost fractions of a cent at list price; the bounded comparison
   costs cents outside allowances. This is an estimate, not a billing receipt.
   Check the linked table before use.
8. Afterward, optional cleanup is:

   ```bash
   gcloud auth application-default revoke
   gcloud services disable texttospeech.googleapis.com --project=PROJECT_ID
   ```

   Disabling the API affects other applications using that project. Separately
   remove a service-account credential/key if you created one; this program
   neither creates keys nor changes your Cloud project.

**API keys versus OAuth:** Google's
[v1 discovery document](https://texttospeech.googleapis.com/$discovery/rest?version=v1)
defines an API-key parameter for REST calls. A key must belong to an enabled,
billable Cloud project and have restrictions that allow the TTS API. It does
not automatically grant access to methods that require an authenticated IAM
principal. A Gemini/AI Studio key is not evidence of Cloud TTS access. This
project implements the documented OAuth/ADC route, including service-account
ADC, and does not implement key authentication. See Google's
[API-key distinctions](https://cloud.google.com/docs/authentication/api-keys).

**Voice features:** Google's
[live voice list](https://cloud.google.com/text-to-speech/docs/list-voices-and-types)
documents Greek Chirp 3 HD female voices, plus `el-GR-Wavenet-B` and
`el-GR-Standard-B`. The older `-A` identifiers are absent from that current
list. Revised cloud candidates use SSML breaks. Google's
[Chirp 3 documentation](https://cloud.google.com/text-to-speech/docs/chirp3-hd)
currently describes preview SSML/voice controls. Its
[phoneme language table](https://cloud.google.com/text-to-speech/docs/phonemes)
does not list Greek, so Modern candidates use normalized or respelled text
without Greek IPA overrides. The Erasmian alternative uses the documented
English alphabet with a verified English female voice. Markup acceptance
does not establish the actual pronunciation heard in the audio.

## Tested approaches and output

The original `uv run python -m euclid_tts bakeoff` renders the opening
statement. It tests Kokoro q8 with `af_heart` and `af_bella`, Google
Modern Greek with the configured female voice if accessible, and macOS Melina.
It saves clips and comparison reports in `output/bakeoff/`. Use
`tools/round_two.py` for the revised engine comparisons. Both record
duration, mode, voice, model hashes, resource measurements and failures.

The second Hugging Face candidate,
[Piper el_GR-rapunzelina-low](https://huggingface.co/rhasspy/piper-voices/blob/main/el/el_GR/rapunzelina/low/MODEL_CARD),
was **inspected, not downloaded or synthesized**. Its card says Greek,
16 kHz, low quality, a CC0 dataset, and fine-tuning from the English Ryan
voice. It does not establish the resulting voice's gender. With an installed
Greek female fallback already available, another model download was not
justified. Kokoro's code/model license is Apache-2.0; the ONNX conversion's
card provides its own license and usage instructions.

Final files, when the respective backend succeeds:

```text
output/euclid-I23-erasmian.wav
output/euclid-I23-erasmian.mp3
output/euclid-I23-modern-female.wav
output/euclid-I23-modern-female.mp3
output/model-comparison.md
output/qc-report.md
```

Each final voice also has JSON metadata. `work/` holds intermediates and
failure diagnostics; `.cache/` holds downloads. None is tracked by Git.
`input/`, configuration, code, tests and the lockfile are enough to rerun.

## QC and limitations

The tests cover immutable UTF-8/polytonic source bytes, both sentence counts,
full selection, normalization, breathings, geometrical names, output names,
invalid configuration, SSML word coverage and request byte limits, actual
PCM pause placement, portable provenance, PCM/MP3 decoding and overloads.
Output reports include duration, sample format, clipping, RMS/peak levels,
leading/trailing silence, internal pauses, and the exact selected text. WAV
export preserves 120 ms around audible edges. It attenuates only when needed,
and reports any overload in the original generated samples.

The local run also verified Melina's female gender and `el-GR` locale using
Apple's voice metadata. If Swift is installed, that discovery can be repeated:

```bash
swift -module-cache-path .cache/swift-modules tools/voice_info.swift
```

Saved final, test, slower and backup WAV/MP3 files were fully decoded.
The measured completion report is `output/final-report.md`; the full decode
record is `output/all-audio-integrity.json`. `PROGRESS.md` records the completed
Cloud setup, feedback and revisions. Refresh reports after generating the
round-2 configurations with `uv run python tools/final_report.py`.

Provenance paths are relative to the external course-materials root; reports
use project-relative paths. Before publishing, run:

```bash
uv run python tools/check_public_paths.py
```

This scans project-owned text, including ignored reports, for personal absolute
home paths. Dependencies, caches, Git internals and binary artifacts are excluded.

No automated check proves subjective naturalness, historical accuracy or
complete word coverage. The user accepted the corrected Neural2-H reading;
that overall verdict does not establish exact /y x/ or settle unresolved
classroom choices. For future pronunciation review, compare ει/η with Modern /i/, ευ with
Modern /ef~ev/, /h/ in ἡ and ὑπό, /b/ in beta versus Modern /v/, and /d ɡ/
in delta/gamma versus Modern /ð ɣ/. Confirm the final συστήσασθαι is audible
and no word or label repeats. English-trained Kokoro may reduce vowels,
blend ευ poorly, or give unfamiliar Greek an English rhythm. Its successful
phoneme encoding is evidence about input control, not a listening verdict.

The first review identified pacing and mixed pronunciation as problems.
The later native-speaker review judged the default Modern WaveNet reading
accurate; that supersedes the earlier negative report for this voice/input.
The user found the Erasmian improved but noted quiet endings, addressed by
leveling. After the course audit and further voice comparisons, the user
accepted Neural2-H. Final clips use one sentence. Ancient wording remains
unchanged, and other Modern variants have no reported review. αυ and the
exact shared δέ/δή quality remain explicitly unresolved; χ is absent from
the accepted short clip. No training or broad phonology engine is involved.

## Put the MP3s in Google Slides

Upload `output/euclid-I23-erasmian.mp3` and
`output/euclid-I23-modern-female.mp3` to Google Drive. Open the desired slide, choose
**Insert → Audio**, and select the appropriate Drive file. In **Format
options → Audio playback**, choose click-to-play or automatic playback.
Ensure the people viewing the deck can access the audio files. Google
[documents support for Drive MP3/WAV audio](https://support.google.com/docs/answer/97447).
The files were fully decoded with FFmpeg; this experiment does not upload
them to Drive or modify the group's deck.
