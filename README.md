# Euclid I.23: two pronunciation experiments

This project reads the opening of *Elements* I.23 in (1) Anglophone Erasmian
classroom pronunciation with **stress**, and (2) Modern Greek with a female
voice. WAV is the PCM master; MP3 is the Google Slides copy. This is a short
experiment for MATH E-139, taught by Graeme Bird. All code and phonetic
transcriptions were prepared with AI assistance. No professor's voice is
cloned, adapted, or used to train a model.

The Erasmian output uses the small Apache-2.0
[Kokoro ONNX model](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX),
with manually specified phonemes and its stock American female `af_heart`
voice. It runs on CPU through native ARM64 ONNX Runtime. Model weights are
92.4 MB, plus about 0.52 MB per voice. There is no PyTorch, CUDA, training,
server, or dependency on the course repository after the input is saved.

The preferred Modern Greek voice is Google Cloud `el-GR-Chirp3-HD-Aoede`.
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

The default is the **first two complete sentences**, 65 source word/label
tokens. The raised dot after ΔΓΕ is an internal pause, so the second sentence
includes both the setting-out and the specification. The passage is:

> Πρὸς τῇ δοθείσῃ εὐθείᾳ καὶ τῷ πρὸς αὐτῇ σημείῳ τῇ δοθείσῃ γωνίᾳ εὐθυγράμμῳ ἴσην γωνίαν εὐθύγραμμον συστήσασθαι.
>
> Ἔστω ἡ μὲν δοθεῖσα εὐθεῖα ἡ ΑΒ, τὸ δὲ πρὸς αὐτῇ σημεῖον τὸ Α, ἡ δὲ δοθεῖσα γωνία εὐθύγραμμος ἡ ὑπὸ ΔΓΕ· δεῖ δὴ πρὸς τῇ δοθείσῃ εὐθείᾳ τῇ ΑΒ καὶ τῷ πρὸς αὐτῇ σημείῳ τῷ Α τῇ δοθείσῃ γωνίᾳ εὐθυγράμμῳ τῇ ὑπὸ ΔΓΕ ἴσην γωνίαν εὐθύγραμμον συστήσασθαι.

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
uv run python -m euclid_tts bakeoff
uv run python -m euclid_tts build
```

Both architecture commands must print `arm64`. The first Erasmian run
downloads only the pinned model, phoneme vocabulary and selected stock voice
to `.cache/huggingface`. Subsequent local runs reuse them without network
access. `uv.lock` pins Python packages; the synthesis module pins model and
vocabulary revisions and records downloaded file hashes. Memory use for the
tested local voices stayed below 1 GB. On this Mac, the cached 30-second
Erasmian sample took about 11 seconds to generate and export.

Independently generate either voice:

```bash
uv run python -m euclid_tts build --voice erasmian
uv run python -m euclid_tts build --voice modern_female
```

Render one sentence or a slower reading:

```bash
uv run python -m euclid_tts build --sentences 1
uv run python -m euclid_tts build --voice erasmian --sentences 1 --rate 0.85 --output-dir work/slower
uv run python -m euclid_tts qc
```

`--rate` controls synthesis speed, not playback speed. The accepted range is
0.7–1.3. The macOS fallback scales its words-per-minute setting. Google rate
support is validated by actually submitting requests; a service error is
reported rather than claiming an ignored setting worked.

Edit `config.yaml` to persist `speech.rate`, `passage.sentence_count`, voice,
backend, output directory or formats. `passage.selection: full` selects all
five complete sentences; full synthesis is supported but was not part of the
initial run. The Erasmian lexicon is deliberately limited to this proposition.
Unknown words or model phonemes fail instead of being dropped. A WAV master
is always retained, including when MP3 is the only requested export format.

An alternative configuration can be used with
`uv run python -m euclid_tts --config path/to/config.yaml build`.

## Pronunciation conventions and evidence

The user's correction establishes **Anglophone Erasmian with stress accent**.
Course study notes (`coursework/study/greek-01-notes.md`, *Breathings*) support
rough breathing as initial /h/. The class-3 lecture note (*01:02:16–01:07:30*)
records τῷ as “tō,” with silent iota subscript, and δέ/δή pronounced alike.
These are written course-note observations; the recordings were not opened
and no additional pronunciation was attributed to the professor.

For unresolved choices, this prototype uses:

| Feature | Erasmian approximation | Modern Greek target |
| --- | --- | --- |
| β, γ, δ | /b ɡ d/ | /v ɣ~ʝ ð/ |
| θ, φ, χ | /θ f k/ | /θ f x~ç/ |
| α, ε, ι, ο, υ | /ɑ ɛ ɪ ɑ ʊ/ | /a e i o i/ |
| η, ω | /eɪ oʊ/ | /i o/ |
| αι, ει, οι, αυ, ευ, ου | /aɪ eɪ ɔɪ aʊ ɛʊ uː/ | /e i i av~af ev~ef u/ |
| Rough breathing | /h/, including ἡ and ὑπό | Silent |
| Iota subscript | Silent, extending the documented τῷ convention | Silent |
| Accent | Word stress on the accented syllable | Stress (tonos) |
| Geometry | Greek names with the selected Erasmian sounds | άλφα, βήτα, γάμμα, δέλτα, έψιλον, ζήτα, ήτα |

δέ and δή both use /dɛ/ as a documented prototype exception: their equality
is in the class note, but the exact vowel quality is not. Omicron and alpha
merge in this American approximation. English /ɹ/ replaces Greek rho; vowel
quantity and gemination are not comprehensively represented. /ɛʊ/ is a
two-phoneme approximation for ευ, and an English-trained model can introduce
unwanted reduction or prosody. None of those choices is presented as a
historically reconstructed Attic system or as a complete match to Bird.

`pronunciation.py` contains the manually reviewed finite word table. Kokoro
uses IPA-like tokens `A`, `I`, `O`, `W` for English diphthongs; output JSON
also contains an expanded IPA display. Every input token is checked against
the model vocabulary. Greek letter groups ΑΒ and ΔΓΕ are expanded to
individual Greek letter names. The two final modes read the same selection.

Modern normalization maps acute/grave/circumflex to tonos, removes breathings
and iota subscripts, keeps diaeresis, and expands labels. It retains Ancient
Greek words and inflections: this is their pronunciation with Modern Greek
sounds, not a Modern Greek translation. Monosyllables may retain a tonos
that modern orthography would omit.

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
   monthly allowance. The selected Modern input is 406 characters, about
   **$0.0122** at the paid rate; a small bake-off and rebuild cost pennies
   if outside the allowance. This is a list-price estimate, not a billing
   receipt. The current table lists WaveNet/Standard at $4 per million beyond
   a 4-million-character allowance. Check the linked table before use.
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
list. The selected Chirp voice uses plain text. Google's
[Chirp 3 documentation](https://cloud.google.com/text-to-speech/docs/chirp3-hd)
currently describes preview SSML/voice controls. Its
[phoneme language table](https://cloud.google.com/text-to-speech/docs/phonemes)
does not list Greek, so Greek phoneme overrides are not assumed to work.
This is why Modern Greek language support is not used as evidence for
Erasmian synthesis.

## Tested approaches and output

`uv run python -m euclid_tts bakeoff` renders the complete opening statement
as a 5–10-second test. It tests Kokoro q8 with `af_heart` and `af_bella`, Google
Modern Greek with the configured female voice if accessible, and macOS Melina.
It saves each clip plus `output/model-comparison.md` and JSON with timings,
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
invalid configuration, real PCM/MP3 decoding, silence and overload detection.
Output reports include duration, sample format, clipping, RMS/peak levels,
leading/trailing silence, internal pauses, and the exact selected text. WAV
export preserves 120 ms around audible edges. It attenuates only when needed,
and reports any overload in the original generated samples.

No automated check proves subjective naturalness, historical accuracy or
complete word coverage. A human listening pass is required before presenting
the experimental Erasmian output. Compare ει/η with Modern /i/, ευ with
Modern /ef~ev/, /h/ in ἡ and ὑπό, /b/ in beta versus Modern /v/, and /d ɡ/
in delta/gamma versus Modern /ð ɣ/. Confirm the final συστήσασθαι is audible
and no word or label repeats. English-trained Kokoro may reduce vowels,
blend ευ poorly, or give unfamiliar Greek an English rhythm. Its successful
phoneme encoding is evidence about input control, not a listening verdict.

Further experimentation is useful if listening finds a particular wrong
vowel, stress or missing word: adjust that word's finite phoneme entry or try
the other saved stock voice. Improving the approximation to the professor's
individual classroom conventions requires an additional documented example.
There is no reason to train a model or expand into a general phonology engine.

## Put the MP3s in Google Slides

Upload the two `.mp3` files to Google Drive. Open the desired slide, choose
**Insert → Audio**, and select the appropriate Drive file. In **Format
options → Audio playback**, choose click-to-play or automatic playback.
Ensure the people viewing the deck can access the audio files. Google
[documents support for Drive MP3/WAV audio](https://support.google.com/docs/answer/97447).
The files were fully decoded with FFmpeg; this experiment does not upload
them to Drive or modify the group's deck.
