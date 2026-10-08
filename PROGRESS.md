# Saved checkpoint — 2026-10-08

The `starter.md` experiment has been implemented and run. All work is saved
locally in `/Users/wihl/Projects/codex/euclid-tts`. No course files were modified.

## Available now

- Complete source Greek: `input/euclid-I23.txt`; provenance: `input/source.json`.
- Native ARM64 Python 3.12.11 environment, `pyproject.toml`, `uv.lock`.
- Configurable one/two/full sentences and synthesis rate.
- Default Erasmian sample: Kokoro q8, stock `af_heart`, 30.003 seconds.
- Default Modern Greek female sample: installed macOS Melina, 25.029 seconds.
- Both modes: `output/euclid-I23-*.wav` and `output/euclid-I23-*.mp3`.
- Test clips: `output/bakeoff/af_heart.*`, `af_bella.*`, `macos.*`.
- Measurements: `output/model-comparison.md`, `output/qc-report.md`, and JSON.
- Sixteen automated tests pass. PCM/MP3 decode and clipping checks pass.
- Installation, pronunciation choices, cloud setup and Slides instructions:
  `README.md`.

The Erasmian output is an **experimental approximation** with explicit
phonemes. Subjective naturalness and complete word coverage still require
a human listening check. No historical pitch reconstruction, voice cloning,
or modern-phonology substitution is claimed.

## Google Cloud status

The user refreshed ADC with `gcloud auth application-default login`.
Authentication now succeeds, but the TTS API responds with
`403 PERMISSION_DENIED`, reason **SERVICE_DISABLED**, for the ADC quota
project `gemini-quick-start`. The suggested user-run command is:

```bash
gcloud services enable texttospeech.googleapis.com --project=gemini-quick-start
```

Billing may need to be linked in that project. No project/billing/credential
settings were changed by this program. No secrets are in the reports.
The preferred configured female voice is `el-GR-Chirp3-HD-Aoede`, confirmed
in Google's current documentation; the live inventory is checked at runtime.
Once enabled, regenerate the Modern Greek audio with:

```bash
export UV_CACHE_DIR="$PWD/.cache/uv"
uv run python -m euclid_tts voices
uv run python -m euclid_tts build --voice modern_female
```

Under `backend: auto`, a Google failure falls back to Melina and records
the reason in the voice JSON. Set `backend: google_cloud` to require Google.

## Reproduce the local experiment

```bash
export UV_CACHE_DIR="$PWD/.cache/uv"
uv sync --python 3.12 --locked
uv run pytest -q
uv run python -m euclid_tts build --voice erasmian
uv run python -m euclid_tts build --voice modern_female
```

The pinned Kokoro model is already in `.cache/huggingface`; the Erasmian
run now works without model network access. Source bytes are never changed.
Downloaded models, output audio and scratch files are excluded from Git
but remain on disk. Nothing has been uploaded to Google Drive or the deck.

## Finishing checks

Before final handoff: verify slower synthesis and source-column equivalence,
finish the measured report, and try Google once more if the API becomes
available. The local samples are already usable for listening review.
