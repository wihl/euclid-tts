# Saved checkpoint — 2026-10-08

The `starter.md` experiment has been implemented and run. All work is saved
locally in `/Users/wihl/Projects/codex/euclid-tts`. No course files were modified.

## Available now

- Complete source Greek: `input/euclid-I23.txt`; provenance: `input/source.json`.
- Native ARM64 Python 3.12.11 environment, `pyproject.toml`, `uv.lock`.
- Configurable one/two/full sentences and synthesis rate.
- Default Erasmian sample: Kokoro q8, stock `af_heart`, 30.003 seconds.
- Default Modern Greek female sample: Google Cloud Chirp 3 HD Aoede, 27.640 seconds.
- Original Melina fallback preserved in `work/melina-baseline/`.
- Both modes: `output/euclid-I23-*.wav` and `output/euclid-I23-*.mp3`.
- Test clips: `output/bakeoff/af_heart.*`, `af_bella.*`, `macos.*`.
- Measurements: `output/model-comparison.md`, `output/qc-report.md`, and JSON.
- Sixteen automated tests pass. PCM/MP3 decode and clipping checks pass.
- All eighteen saved WAV/MP3 files (final, bake-off, slower and backup) decode correctly with zero clipping.
- Modern female voice and Greek locale verified with macOS voice metadata.
- The full cropped Greek source column agrees with the saved input after
  documented typographic and whitespace normalization.
- Slower synthesis at 0.85 tested: one sentence takes 8.791 seconds.
- Final measured outcome: `output/final-report.md`.
- Installation, pronunciation choices, cloud setup and Slides instructions:
  `README.md`.

The Erasmian output is an **experimental approximation** with explicit
phonemes. Subjective naturalness and complete word coverage still require
a human listening check. No historical pitch reconstruction, voice cloning,
or modern-phonology substitution is claimed.

## Google Cloud status

**Resolved.** The user refreshed ADC, linked billing, and enabled the
Cloud Text-to-Speech API in `gemini-quick-start`. The live inventory confirms
`el-GR-Chirp3-HD-Aoede` is female. Both a short test and the full selected
passage have been rendered successfully with that voice. No additional
credential or setup is needed for the current project.

```bash
export UV_CACHE_DIR="$PWD/.cache/uv"
uv run python -m euclid_tts voices
uv run python -m euclid_tts build --voice modern_female
```

The early RefreshError and SERVICE_DISABLED diagnostics are historical.
Current final audio uses Google, with the previous local fallback saved.

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

## Final verification

Source preservation, ARM64 environment, sentence selection, slower local
synthesis and audio integrity are verified. The Google slower-rate check
passed (11.754 seconds for one sentence at 0.85), and final reports are saved.
The complete default build command was tested successfully. No user input is needed. A human
listening pass remains useful before presenting the experimental Erasmian
pronunciation; objective file checks do not establish naturalness.
