"""Summarize saved measurements without synthesis, credentials or API calls."""
import json
from pathlib import Path

from euclid_tts import audio
from euclid_tts.text import ROOT

out = ROOT / "output"

def read(path):
    return json.loads(path.read_text())

def write(name, lines):
    (out / name).write_text("\n".join(lines) + "\n", encoding="utf-8")

e = read(out / "euclid-I23-erasmian.json")
m = read(out / "euclid-I23-modern-female.json")
comparison = read(out / "model-comparison.json")
source = read(ROOT / "input/source.json")
cloud = m["backend"] == "google_cloud"
assert e["selected_greek"] == m["selected_greek"], "The saved voices select different passages"

all_audio = []
for folder in [out, out / "bakeoff", ROOT / "work/slower", ROOT / "work/melina-baseline"]:
    for path in sorted(folder.glob("*.wav")) + sorted(folder.glob("*.mp3")):
        all_audio.append({"path": str(path.relative_to(ROOT)), **audio.inspect(path)})
assert all(c["decode_ok"] and c["clipped_samples"] == 0 for c in all_audio)
(out / "all-audio-integrity.json").write_text(json.dumps(all_audio, ensure_ascii=False, indent=2) + "\n")

intro = "Both requested samples have been generated. Google Cloud TTS authentication, API enablement, female voice inventory and synthesis were tested successfully." if cloud else "Both local samples have been generated. Google was unavailable and the Modern female voice used the recorded macOS fallback."
lines = [
    "# Euclid I.23 experiment — final saved result", "", intro,
    "The Erasmian sample is an experimental classroom approximation. Subjective naturalness and complete spoken word coverage need a human listening pass; successful phoneme encoding is not a pronunciation-accuracy verdict.",
    "", "## Exact Greek passage", "", e["selected_greek"],
    "", "## Source and selection", "",
    f"{source['edition']}; {source['locator']}. {source['independent_pdf_column_comparison']}",
    "Two complete sentences include the enunciation, setting-out and specification. The raised dot inside the second sentence is an internal pause. Source bytes remain unchanged; Modern normalization and Erasmian phonemes are separate intermediates.",
    f"Input SHA-256: `{e['source_sha256']}`.",
    "", "## Audio and runtime", "",
    "| Mode | Actual engine/voice | PCM master duration | Cached build/export |",
    "| --- | --- | ---: | ---: |",
]
for mode, meta in [("Anglophone Erasmian", e), ("Modern Greek female", m)]:
    lines.append(f"| {mode} | {meta['backend']} / {meta['voice']} | {meta['audio'][0]['duration_seconds']:.3f}s | {meta['elapsed_seconds']:.2f}s |")
lines += [
    "", "Both final samples have mono 24 kHz, 16-bit PCM WAV masters and 128 kbit/s MP3 copies in `output/`. Their filenames are `euclid-I23-erasmian.*` and `euclid-I23-modern-female.*`.",
    f"All {len(all_audio)} saved final/test/slower/backup WAV and MP3 files decoded completely, with zero clipped or overloaded decoded samples. Both final raw synthesis outputs also have zero overloads. See `all-audio-integrity.json` and `qc-report.md` for peaks, durations and pauses. No music, effects, video or spoken introduction was added.",
    "Native ARM64 Python 3.12.11, sixteen passing automated tests, locked dependencies and pinned model/vocabulary revisions were verified. Build timings exclude earlier discovery, downloads and setup; end-to-end development time was not measured.",
    "", "## Pronunciation conventions and evaluation", "",
    "Erasmian uses stress, initial /h/ for rough breathings, silent iota subscripts, /b ɡ d/ for beta/gamma/delta, /eɪ/ for eta/ei, /oʊ/ for omega, and the documented selected Anglophone diphthongs. Course notes support rough breathing as /h/, silent iota in τῷ, and the equality of δέ/δή. Other choices are selected conventions, not independently confirmed individual habits of the professor.",
    "Every explicit phoneme token is representable in the actual downloaded vocabulary; the finite manually reviewed lexicon covers the full proposition. Geometry groups are expanded to Greek letter names. This is input-control evidence. Actual phonetic realization, missing/repeated spoken words and naturalness were not independently confirmed by listening or ASR.",
    "Known compromises include English /ɹ/, an American alpha/omicron merger, incomplete quantity/gemination, and /ɛʊ/ as two phonemes for ευ. English-trained Kokoro can add vowel reduction or English prosody. No pitch-accent reconstruction or voice cloning was attempted. The original text was never silently passed through Modern Greek TTS for the Erasmian file.",
    "Modern normalization changes accent types to tonos, removes breathings/subscripts, retains diaeresis and expands labels. Raised dots become commas, avoiding Greek question-mark intonation from a semicolon. Ancient inflections are retained; this is pronunciation, not translation.",
]
if cloud:
    lines += [f"The live Google inventory identified `{m['voice']}` as **FEMALE**, with **el-GR** language coverage; the engine checks both before synthesis. The normalized request text and service response-derived audio metadata are saved in the Modern JSON."]
else:
    lines += ["The installed Melina variants were independently identified as female and el-GR using macOS AVSpeechSynthesisVoice metadata."]
lines += ["", "## Small bake-off", "", f"Phrase: {comparison['phrase']}", "", "| Candidate | Mode | Observation | Duration | Inference |", "| --- | --- | --- | ---: | ---: |"]
for c in comparison["candidates"]:
    duration = f"{c['audio']['duration_seconds']:.3f}s" if "audio" in c else "—"
    inference = f"{c['inference_seconds']:.2f}s" if "inference_seconds" in c else "—"
    lines.append(f"| {c['candidate']} / {c.get('voice', 'unavailable')} | {c['mode']} | {c['status']} | {duration} | {inference} |")
peak_rss = max(c.get("max_process_rss_mib", 0) for c in comparison["candidates"])
lines += [
    "", f"Kokoro q8 is {e['model_bytes']:,} bytes, runs with four CPU inference threads, and costs $0 in API fees. Peak process RSS during the comparison was {peak_rss:.1f} MiB, including sequential model loads; it is not a per-model measurement. Cloud server resource use is unavailable. Inference timings exclude local model loading.",
    "`af_heart` was retained as the documented Erasmian default; no subjective superiority over `af_bella` is claimed. Both clips are preserved. Google Aoede is selected for Modern Greek when available; the full Melina baseline is retained in `work/melina-baseline/`.",
    "Piper `el_GR-rapunzelina-low` was inspected only, not downloaded or synthesized: its card documents Greek, 16 kHz, a CC0 dataset, low quality and fine-tuning from Ryan, but does not establish the resulting gender. Another model download was not justified. Kokoro and its ONNX conversion are Apache-2.0. No OpenAI, Gemini, Azure or ElevenLabs synthesis was tested.",
    "", "## Speaking rate", "", "| Mode | One sentence at 1.0 | One sentence at 0.85 |", "| --- | ---: | ---: |",
]
for mode, basename, candidate in [("Erasmian", "euclid-I23-erasmian", "Kokoro q8 / af_heart"), ("Modern female", "euclid-I23-modern-female", "google_cloud" if cloud else "macos")]:
    slow_path = ROOT / "work/slower" / f"{basename}.json"
    if slow_path.exists():
        slow = read(slow_path)
        regular = next(c for c in comparison["candidates"] if c["candidate"] == candidate)
        lines.append(f"| {mode} | {regular['audio']['duration_seconds']:.3f}s | {slow['audio'][0]['duration_seconds']:.3f}s |")
lines += ["", "Both slower checks used synthesis controls and produced valid WAV/MP3, without stretching completed audio. These are independent synthesized samples; duration is not guaranteed to be a precise inverse of the rate. Full-proposition synthesis was not part of this initial experiment.", "", "## Google setup and cost", ""]
if cloud:
    lines += ["Google setup is complete. The user refreshed ADC, linked billing and enabled `texttospeech.googleapis.com` in `gemini-quick-start`. The earlier RefreshError and SERVICE_DISABLED results are resolved historical diagnostics. No additional credential setup is currently needed; no credential was copied into the repository."]
else:
    lines += [f"Google fallback reason: {m.get('google_fallback_reason', 'local backend selected')}. See README for the exact setup instructions."]
characters = len(m["normalized_text"])
lines += [
    f"The default normalized Modern passage has {characters} characters. Chirp 3 HD's published paid price is $30/million characters beyond its 1-million-character monthly allowance, about **${characters*0.00003:.4f}** for one default rendering outside the allowance. Actual account charges were not inspected. Source: [Google pricing](https://cloud.google.com/text-to-speech/pricing).",
    "", "## Reproduction", "", "```bash", 'export UV_CACHE_DIR="$PWD/.cache/uv"', "uv sync --python 3.12 --locked", "uv run pytest -q", "uv run python -m euclid_tts bakeoff", "uv run python -m euclid_tts build", "uv run python -m euclid_tts build --voice erasmian --sentences 1 --rate 0.85 --output-dir work/slower", "uv run python -m euclid_tts build --voice modern_female --sentences 1 --rate 0.85 --output-dir work/slower", "uv run python tools/final_report.py", "```",
    "", "The modes can be generated independently with `--voice erasmian` or `--voice modern_female`. Configuration supports one/two sentences and full text. `auto` records any fallback to Melina; `google_cloud` requires cloud output. README contains Google credential setup, official feature documentation, pronunciation rules and Drive/Slides instructions. No course repository, private recording or shared deck was changed.",
    "", "## Useful next step", "", "Listen before presentation, especially to the experimental Erasmian file. Check ει/η versus Modern /i/, ευ versus /ef~ev/, rough /h/, beta/delta/gamma, each geometrical label, and the final συστήσασθαι. A specific wrong word can be corrected in the finite phoneme table or compared with the retained Bella clip. Further model experimentation is useful only after identifying a concrete audible problem; training or speculative large downloads are not justified.",
]
write("final-report.md", lines)
comparison_lines = ["# Short-phrase comparison", "", "Measured candidates and interpretation; no listening verdict is claimed.", "", *lines[lines.index("## Small bake-off"):lines.index("## Speaking rate")]]
comparison_lines += [
    "", "Naturalness and complete spoken word coverage remain unassessed by listening for every candidate. Kokoro accepts explicit IPA-like phonemes; Google and Melina tests used normalized Greek text. Greek support alone does not establish Erasmian pronunciation. The Erasmian phoneme contrasts are documented in README and the final JSON; no unsupported phonemes were silently filtered.",
    "", "The Modern Google voice's FEMALE/el-GR inventory entries were verified before rendering; Melina's female/el-GR properties were independently checked in native macOS voice metadata. The Google request used plain text, not Greek phoneme overrides. Google's supported-phoneme table does not document Greek.",
    "", "Early vocabulary-link and token-handling integration failures were corrected and preserved in `work/bakeoff-before-vocab-fix.json`. They are not evidence that the model itself is unsuitable. Authentication/API-enable errors were resolved before the successful Google clip was generated. See the JSON for raw input, resource measurements, durations, metadata and model hashes.",
]
write("model-comparison.md", comparison_lines)
print(f"Saved final report; {len(all_audio)} WAV/MP3 files decoded with zero clipping.")
