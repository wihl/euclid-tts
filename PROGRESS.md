# Saved checkpoint — 2026-10-08

The original experiment and follow-up comparison are saved in this repository.
No course files were changed. Source provenance and documentation now use
relative paths; project-owned text passes the personal-home-path scan.

## Listening results

The user rejected both original defaults as rushed with insufficient pauses.
A native Greek listener, as reported by the user, also found the Modern
reading unclear and mixing Ancient and Modern pronunciation. These results
are recorded in `EXPERIMENTS.md`; original audio and pre-review reports are
preserved locally in `output/round-1/` and remain excluded from Git.

## Revised candidates

Five full two-sentence candidates and five first-sentence controls were
actually synthesized. Full trials use rate 0.72, eleven grammatical breath
groups and ten explicit gaps. Short controls use 0.82 with shorter gaps.

- New default Erasmian: Google en-US-Wavenet-F, per-word IPA, 54.162 seconds.
- New default Modern female: Greek el-GR-Wavenet-B, normalized input, 38.755 seconds.
- Slower local Kokoro af_heart: 48.803 seconds.
- WaveNet Modern phonetic-spelling trial: 39.087 seconds.
- Slower Greek Chirp Aoede: 56.092 seconds.

Modern normalization now omits tonos on monosyllabic function words. A
separate spelling trial supplies modern sound cues for unfamiliar Ancient
forms. The Ancient wording, inflections and original polytonic input remain
unchanged. No accuracy or naturalness verdict is claimed for the revisions.
A native-speaker listening review remains needed.

Each candidate has PCM WAV, MP3, JSON and measured QC in `output/round-2/`.
The new defaults also occupy `output/euclid-I23-*.{wav,mp3,json}`.
`output/model-comparison.md` links all five full candidates and reports
measurements; `output/final-report.md` describes the new defaults.

## Environment and verification

Native ARM64 Python 3.12.11, uv-managed locked dependencies, FFmpeg and the
cached pinned Kokoro q8 model remain available. No new model download or
training was needed. Twenty-four automated tests pass. All 42 saved WAV/MP3
files fully decode without clipping; five full revisions have zero raw
synthesis overloads. Source SHA-256 remains
`4b364cf450c5a905e00c0320b06d1e44510fc2d840adfbe013174c40d061333e`.

Google ADC, billing and Text-to-Speech API enablement are resolved. Live
inventories verified female Greek and English voices before synthesis.
No further cloud setup is needed on the original machine. Credentials were
not copied into the project; fresh clones need README setup.

## Reproduction

```bash
export UV_CACHE_DIR="$PWD/.cache/uv"
uv sync --python 3.12 --locked
uv run pytest -q
uv run python tools/check_public_paths.py
uv run python -m euclid_tts build
uv run python -m euclid_tts --config experiments/round-2-erasmian-kokoro.yaml build
uv run python -m euclid_tts --config experiments/round-2-modern-chirp.yaml build
uv run python -m euclid_tts --config experiments/round-2-modern-wavenet-respelled.yaml build
```

All full and short configurations are saved in `experiments/`.
`uv run python tools/round_two.py` regenerates the complete comparison;
`uv run python tools/final_report.py` refreshes reports from those saved outputs.
The original short bake-off has its own report under `output/bakeoff/`.
Generated audio, model caches, environments and intermediate course extracts
are excluded from Git. Nothing was uploaded to Drive or the shared deck.
