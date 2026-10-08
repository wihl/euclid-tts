# Final checkpoint — 2026-10-08

The bounded Euclid I.23 experiment is complete. The user judged the
course-corrected round-5 Neural2-H Erasmian reading acceptable and requested
finalization. The native Greek listener had already approved Modern WaveNet.

## Final presentation audio

| Mode | Selected voice | Duration | Human verdict |
| --- | --- | ---: | --- |
| Anglophone Erasmian, stress | en-US-Neural2-H | 12.833 s | Acceptable, user |
| Modern Greek female | el-GR-Wavenet-B | 10.317 s | Accurate, native speaker as reported by user |

Both read the same complete 17-word opening sentence at synthesis rate 0.72
with three requested 0.65-second phrase pauses. Erasmian retains gentle
leveling; Modern has no leveling. Masters are mono 24 kHz 16-bit PCM WAV;
Google Slides copies are 128 kbit/s MP3.

Final files are `output/euclid-I23-erasmian.{wav,mp3,json}` and
`output/euclid-I23-modern-female.{wav,mp3,json}`. The Erasmian WAV and MP3
are exact copies of the user-accepted `output/round-5/neural2-h/` sample,
without resynthesis. The Modern WAV still agrees sample for sample with
the approved two-sentence recording's prefix. Both have zero source
overloads and zero decoded clipping. `config.yaml` now selects Neural2-H.

## Course audit and remaining limitations

The course workspace was read without modification. Source hashes and
relative locators are in `input/pronunciation-source.json`; README's
pronunciation table cites each divergence. The alphabet is on handout
pp. 1–2; the diphthong line is on p. 4 in this copy. Timestamped class
remarks override the handout where they differ.

The audit corrected 28 word entries and the epsilon label: ευ /juː/,
standalone υ target /y/, accented ι /iː/, χ target /x/, and explicitly
selected unmerged American off /ɔ/ for omicron. Google en-US substitutes
/uː/ for /y/ and /k/ for /x/; target and submitted IPA remain separate in
metadata. χ is absent from the accepted opening sentence. Silent subscript,
rough h, delta /d/, ου /uː/, and δέ/δή equality are retained. The shared
/ɛ/ quality for δέ/δή and αυ /aʊ/ remain explicit unresolved choices.
Acceptance of the short clip does not certify exact /y x/ or the full text.

## Listening history and retained alternatives

Chirp Leda was rejected as worse. Neural2-F lively had slurred enunciation.
After the course correction, neutral Neural2-F returned byte-identical WAV
and PCM to corrected WaveNet-F. Firm F was distinct but was not selected;
it has 12 full-scale source PCM samples before leveling, retained in QC.

Pre-correction Erasmian delivery/reports are in
`output/round-5/pre-correction/`. Corrected WaveNet and pre-promotion reports
are in `output/round-5/corrected-wavenet-reference/`. Round-1, round-2 and
round-4 comparisons remain intact. All verdicts and measured results are
recorded in `EXPERIMENTS.md`, `output/naturalness-comparison.md`,
`output/model-comparison.md`, `output/final-report.md` and `output/qc-report.md`.
No further voice trial is required for the presentation.

## Verification and reproduction

31 tests pass. All 60 saved WAV/MP3 files decode without clipping. Source
Greek bytes and the four course-source hashes are unchanged. Accepted audio
identity, public-path scan and whitespace checks pass. Native ARM64 Python
3.12.11, uv-locked dependencies, FFmpeg and cached Kokoro remain available.
Google ADC, billing and the TTS API work; no further setup is needed.

```bash
export UV_CACHE_DIR="$PWD/.cache/uv"
uv sync --python 3.12 --locked
uv run pytest -q
uv run python tools/check_public_paths.py
uv run python -m euclid_tts build
uv run python tools/final_report.py
```

Fresh cloud synthesis uses the accepted recipe but may vary from the saved
performance. Report refresh uses saved comparisons; it does not call Google.
Use the saved final files for the presentation. Upload MP3s to Drive and
insert them in Slides as documented in README; no upload or deck change
was performed. Credentials, private recordings, audio, scratch files,
caches and environments remain excluded from Git. Project-owned files use
relative paths. No training, cloning or new model download was used.
