# Active checkpoint — course pronunciation audit, 2026-10-08

The user is going offline. All course files were read without modification.
The course audit, lexicon corrections and source hashes are saved in
`src/euclid_tts/pronunciation.py`, `README.md`, and
`input/pronunciation-source.json`. All 31 tests and the public-path scan pass.

- Corrected one-sentence Erasmian WaveNet default generated: 14.35275 seconds.
- Previous Erasmian default and reports archived in `output/round-5/pre-correction/`.
- New Neural2-F neutral trial: identical WAV SHA/PCM to the corrected default.
- New Neural2-F firm trial: distinct, 14.577958 seconds; needs human listening.
- Latest human feedback: Chirp Leda rejected as worse; Neural2 lively slurred.
- Modern delivery remains the approved 10.317-second excerpt, untouched.

Remaining work: finish report regeneration and checks. One further female
Neural2-H voice check/render is being attempted; if the network drops it can
be resumed from its saved recipe. No new authentication or course edits needed.

Course targets: ευ /juː/, υ /y/, accented ι /iː/, χ /x/. Google en-US
substitutes /uː/ for /y/ and /k/ for /x/, explicitly recorded in metadata.
Omicron selects unmerged American off /ɔ/; shared δέ/δή quality remains an
explicit /ɛ/ choice since the class notes specify equality only.

The older checkpoint below is historical and predates the course audit.

---

# Saved checkpoint — 2026-10-08

The experiment, listener feedback and further trials are saved in this repository.
Source and reports use relative paths; the public-path scan passes.

## Current presentation clips

Defaults now read only the first complete sentence, the 17-word enunciation.
They retain rate 0.72 and three 0.65-second phrase pauses:

- Erasmian: en-US-Wavenet-F with explicit IPA and gentle leveling, 14.364 seconds.
- Modern female: el-GR-Wavenet-B, 10.317 seconds, delivered as an exact PCM
  excerpt of the recording judged accurate by a native Greek speaker.

The user confirmed that Erasmian leveling fixed the quiet word-ending drop-off.
Its remaining issue is a synthesized tone compared with Modern Greek.
Current audio is in `output/euclid-I23-*.{wav,mp3,json}`. Longer reviewed
reference files are preserved in `output/round-2/reviewed-defaults/`.

## New naturalness comparisons

Two one-sentence alternatives have been rendered with the same IPA targets,
rate, phrase pauses and leveling:

- en-US-Neural2-F, lively style: 14.655 seconds.
- en-US-Chirp3-HD-Leda: 16.943 seconds.

They are separate files in `output/round-4/`; the current defaults remain
user-reviewed references. Both cloud calls succeeded, and their WAV/MP3
pairs decode without clipping. Neither has a listening verdict yet. Neural2
is the first audition to try for expressive delivery near the reference
length. Chirp has longer actual pauses and an active waveform at EOF;
check its final word for completeness during playback.

Feedback and measured ending gains are recorded in `EXPERIMENTS.md`.
`output/naturalness-comparison.md` links both new trials and the reference;
`output/final-report.md` describes the current clips. Historical comparisons
and five short controls remain under `output/round-2/`.

## Environment and verification

Native ARM64 Python 3.12.11, uv-locked dependencies, FFmpeg and cached Kokoro
remain available. Twenty-nine tests pass, including unchanged source bytes,
SSML word coverage, whole-sentence style scope, preserved pauses/frame counts,
leveling audibility and clipping headroom. All 50 saved WAV/MP3 files in the
main comparison archive and original backups decode without clipping.

Google ADC, billing and API enablement work; no further setup is needed on
the original machine. Tested voices were checked against the live inventory.
No new model download, training or voice cloning was used. Source SHA-256 is
`4b364cf450c5a905e00c0320b06d1e44510fc2d840adfbe013174c40d061333e`.

## Reproduction

```bash
export UV_CACHE_DIR="$PWD/.cache/uv"
uv sync --python 3.12 --locked
uv run pytest -q
uv run python tools/check_public_paths.py
uv run python -m euclid_tts build
uv run python -m euclid_tts --config experiments/round-4-erasmian-neural2-lively.yaml build
uv run python -m euclid_tts --config experiments/round-4-erasmian-chirp-leda.yaml build
uv run python tools/final_report.py
```

Future cloud renders may vary slightly. The delivered Modern excerpt is
sample-identical to the approved reference; a fresh build uses the same
voice/input/pacing settings. `tools/round_two.py` regenerates historical
comparisons then builds current one-sentence defaults. Audio, scratch files,
credentials, caches and environments remain excluded from Git. No course
files were modified, and nothing was uploaded to Drive or the shared deck.
