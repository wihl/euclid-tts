"""Reproducible CLI. All reports describe measurement limits explicitly."""
import argparse
import hashlib
import json
import platform
import resource
import sys
import time
from pathlib import Path

import yaml

from . import audio
from .pronunciation import erasmian, ipa, modern
from .prosody import DEFAULT_PAUSES, pause_settings
from .synthesize import BackendError, Kokoro, google_render, google_voices, kokoro_render, melina_render
from .text import ROOT, SOURCE, TEST_PHRASE, select

VOICE_NAMES = {"erasmian": "euclid-I23-erasmian", "modern_female": "euclid-I23-modern-female"}


def validate(cfg: dict) -> dict:
    if not isinstance(cfg, dict):
        raise ValueError("Configuration must be a YAML mapping")
    for key in ["passage", "speech", "voices", "output"]:
        if not isinstance(cfg.get(key), dict):
            raise ValueError(f"Missing configuration mapping: {key}")
    p = cfg["passage"]
    if p.get("proposition") != "I.23":
        raise ValueError("Only proposition I.23 is supported")
    if p.get("selection") not in {"first_sentences", "full"}:
        raise ValueError("selection must be first_sentences or full")
    count = p.get("sentence_count")
    if type(count) is not int or not 1 <= count <= 5:
        raise ValueError("sentence_count must be an integer from 1 to 5")
    rate = cfg["speech"].get("rate")
    if type(rate) not in {int, float} or not 0.7 <= rate <= 1.3:
        raise ValueError("speech.rate must be a number from 0.7 to 1.3")
    pauses = cfg["speech"].get("pauses", {})
    if not isinstance(pauses, dict) or set(pauses)-set(DEFAULT_PAUSES):
        raise ValueError("speech.pauses must contain phrase/comma/section/sentence durations")
    if any(type(value) not in {int, float} or not 0.15 <= value <= 2.0 for value in pauses.values()):
        raise ValueError("Pause durations must be numbers from 0.15 to 2.0 seconds")
    voices = cfg["voices"]
    if set(voices) != set(VOICE_NAMES):
        raise ValueError("voices must contain erasmian and modern_female")
    for name, v in voices.items():
        if not isinstance(v, dict) or type(v.get("enabled")) is not bool:
            raise ValueError(f"{name}.enabled must be true or false")
        choices = {"auto", "kokoro", "google_cloud"} if name == "erasmian" else {"auto", "google_cloud", "macos"}
        if v.get("backend") not in choices:
            raise ValueError(f"Invalid backend for {name}")
        if not isinstance(v.get("voice"), str) or not v["voice"]:
            raise ValueError(f"Missing voice for {name}")
        if name == "erasmian" and v["backend"] != "google_cloud" and v["voice"] not in {"af_heart", "af_bella"}:
            raise ValueError("Use a reviewed Kokoro voice: af_heart or af_bella")
        if name == "erasmian" and v["backend"] == "google_cloud" and not v["voice"].startswith("en-US-"):
            raise ValueError("Google Erasmian requires an en-US voice with IPA controls")
        if name == "modern_female" and v.get("input", "normalized") not in {"normalized", "respelled"}:
            raise ValueError("modern_female.input must be normalized or respelled")
        if type(v.get("level_speech", False)) is not bool:
            raise ValueError(f"{name}.level_speech must be true or false")
    formats = cfg["output"].get("formats")
    if not isinstance(formats, list) or not formats or len(set(formats)) != len(formats) or set(formats)-{"wav", "mp3"}:
        raise ValueError("output.formats must contain wav and/or mp3 without duplicates")
    if not isinstance(cfg["output"].get("directory"), str) or not cfg["output"]["directory"]:
        raise ValueError("output.directory must be a nonempty path")
    return cfg


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def render_modern(text, v, rate, scratch, pauses=None):
    if v["backend"] in {"auto", "google_cloud"}:
        try:
            return google_render(text, v["voice"], rate, pauses=pauses, respelled=v.get("input") == "respelled")
        except BackendError as exc:
            if v["backend"] == "google_cloud":
                raise
            print(f"{exc}; using installed Melina", file=sys.stderr)
            data, meta = melina_render(text, rate, scratch)
            meta["google_fallback_reason"] = str(exc)
            return data, meta
    return melina_render(text, rate, scratch)


def build(cfg, out, voice=None, sentence_count=None):
    source_bytes = SOURCE.read_bytes()
    passage_cfg = cfg["passage"].copy()
    if sentence_count is not None:
        passage_cfg.update(selection="first_sentences", sentence_count=sentence_count)
    selected = select(source_bytes.decode("utf-8"), passage_cfg["selection"], passage_cfg["sentence_count"])
    pauses = pause_settings(cfg["speech"])
    out.mkdir(parents=True, exist_ok=True)
    for name, v in cfg["voices"].items():
        if (voice and name != voice) or not v["enabled"]:
            continue
        start = time.perf_counter()
        if name == "erasmian" and v["backend"] == "google_cloud":
            data, meta = google_render(selected, v["voice"], cfg["speech"]["rate"], mode="erasmian", pauses=pauses)
            meta["ipa"] = ipa(erasmian(selected))
        elif name == "erasmian":
            load_start = time.perf_counter()
            model = Kokoro(v["voice"])
            load_seconds = time.perf_counter()-load_start
            inference_start = time.perf_counter()
            data, meta = kokoro_render(model, selected, cfg["speech"]["rate"], pauses)
            meta["load_seconds"] = load_seconds
            meta["inference_seconds"] = time.perf_counter()-inference_start
            meta["ipa"] = ipa(erasmian(selected))
        else:
            data, meta = render_modern(selected, v, cfg["speech"]["rate"], ROOT/"work/modern-raw.wav", pauses)
        if v.get("level_speech", False):
            data, meta["leveling"] = audio.level_speech(data)
        wav = out / f"{VOICE_NAMES[name]}.wav"
        meta.update(audio.write_wav(wav, data))
        files = [wav]
        if "mp3" in cfg["output"]["formats"]:
            files.append(audio.export_mp3(wav))
        meta.update(source_sha256=hashlib.sha256(source_bytes).hexdigest(), selected_greek=selected, selection=passage_cfg, rate=cfg["speech"]["rate"], pauses=pauses, elapsed_seconds=time.perf_counter()-start, process_max_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2), architecture=platform.machine(), audio=[audio.inspect(p) for p in files])
        save_json(out/f"{VOICE_NAMES[name]}.json", meta)
        label = str(wav.relative_to(ROOT)) if wav.is_relative_to(ROOT) else wav.name
        print(f"{name}: {meta['audio'][0]['duration_seconds']:.2f}s speech → {label}", flush=True)
    qc(out)


def bakeoff(cfg, out):
    folder = out/"bakeoff"
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for voice in ["af_heart", "af_bella"]:
        candidate = {"candidate": f"Kokoro q8 / {voice}", "mode": "erasmian", "phonetic_input": True}
        try:
            start = time.perf_counter()
            model = Kokoro(voice)
            candidate["load_seconds"] = time.perf_counter()-start
            start = time.perf_counter()
            data, meta = kokoro_render(model, TEST_PHRASE, cfg["speech"]["rate"], pause_settings(cfg["speech"]))
            candidate.update(meta)
            candidate["inference_seconds"] = time.perf_counter()-start
            wav = folder/f"{voice}.wav"
            candidate.update(audio.write_wav(wav, data))
            audio.export_mp3(wav)
            candidate["audio"] = audio.inspect(wav)
            candidate["status"] = "generated; listening review pending"
        except Exception as exc:
            candidate.update(status="failed", error=type(exc).__name__)
            if isinstance(exc, (ValueError, BackendError)):
                candidate["error"] = str(exc)
        candidate["max_process_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2)
        records.append(candidate)
        print(f"{candidate['candidate']}: {candidate['status']}", flush=True)
    for backend in ["google_cloud", "macos"]:
        candidate = {"candidate": backend, "mode": "modern_female", "phonetic_input": False}
        try:
            start = time.perf_counter()
            v = dict(cfg["voices"]["modern_female"], backend=backend)
            data, meta = render_modern(TEST_PHRASE, v, cfg["speech"]["rate"], ROOT/"work/melina-test.wav", pause_settings(cfg["speech"]))
            candidate.update(meta, inference_seconds=time.perf_counter()-start)
            wav = folder/f"{backend}.wav"
            candidate.update(audio.write_wav(wav, data))
            audio.export_mp3(wav)
            candidate.update(audio=audio.inspect(wav), status="generated; listening review pending")
        except Exception as exc:
            candidate.update(status="unavailable", error=str(exc) if isinstance(exc, BackendError) else type(exc).__name__)
        candidate["max_process_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2)
        records.append(candidate)
        print(f"{backend}: {candidate['status']}", flush=True)
    save_json(folder/"model-comparison.json", {"phrase": TEST_PHRASE, "rate": cfg["speech"]["rate"], "candidates": records})
    lines = ["# Short-phrase comparison", "", f"Greek: {TEST_PHRASE}", "", f"Erasmian IPA-like input: `{erasmian(TEST_PHRASE)}`", "", f"Modern input: {modern(TEST_PHRASE)}", "", "| Candidate | Mode | Status | Duration | Inference |", "| --- | --- | --- | ---: | ---: |"]
    for c in records:
        duration = f"{c['audio']['duration_seconds']:.2f}s" if 'audio' in c else "—"
        inference = f"{c['inference_seconds']:.2f}s" if 'inference_seconds' in c else "—"
        lines.append(f"| {c['candidate']} | {c['mode']} | {c['status']} | {duration} | {inference} |")
    lines += ["", "Measured timings and input tokens are in model-comparison.json. Inference excludes local model loading. Memory is a process high-water mark, not isolated per candidate. Local calls have no API charge; Google cost depends on the account's monthly allowance.", "", "Kokoro accepts every phoneme token without filtering; its English voice is being tested outside its training language. Generated audio is experimental. Naturalness and complete word coverage require listening. Automated integrity checks do not establish pronunciation accuracy.", "", "Known compromises: English rhotic /ɹ/, non-native /ɛʊ/ for ευ, and unstressed English vowel reduction. No professor's voice is used."]
    (folder/"model-comparison.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def qc(out):
    records = []
    lines = ["# Audio QC", "", "Measured file integrity; listening feedback is recorded in EXPERIMENTS.md. Automated checks do not establish pronunciation accuracy or subjective naturalness.", ""]
    for name in VOICE_NAMES.values():
        metadata_file = out/f"{name}.json"
        if not metadata_file.exists():
            continue
        meta = json.loads(metadata_file.read_text())
        # Check the current build's files, not older exports left in the folder.
        checks = [audio.inspect(out/c["file"]) for c in meta["audio"]]
        records.append({"voice": name, "checks": checks})
        lines += [f"## {name}", "", f"Backend: {meta['backend']}; voice: {meta['voice']}; rate: {meta['rate']}.", "", "Greek passage:", "", meta["selected_greek"], "", "| File | Duration | Decode | Peak | Clipped samples |", "| --- | ---: | --- | ---: | ---: |"]
        for c in checks:
            peak = f"{c['peak_dbfs']:.2f} dBFS" if "peak_dbfs" in c else "—"
            lines.append(f"| {c['file']} | {c['duration_seconds']:.3f}s | OK | {peak} | {c.get('clipped_samples', '—')} |")
        wav = checks[0]
        lines += ["", f"Edge silence: {wav['leading_silence_seconds']:.3f}s / {wav['trailing_silence_seconds']:.3f}s. Internal pauses ≥300 ms: {wav['internal_silences_over_300ms']}.", f"Raw overload samples before export: {meta['raw_overload_samples']}. Source SHA-256: `{meta['source_sha256']}`.", ""]
        if "leveling" in meta:
            lines += [f"Speech leveling: {meta['leveling']['method']}; 2:1 compression with +6 dB makeup. Frame count unchanged. Original synthesis overloads: {meta['leveling']['synthesis_raw_overload_samples']}. Filter: `{meta['leveling']['filter']}`.", ""]
        if meta.get("render_source", {}).get("pcm_identical_to_approved_prefix"):
            lines += ["Delivered PCM is a lossless first-sentence excerpt of the Modern reading judged accurate by a native Greek speaker, as reported by the user.", ""]
        if meta["backend"] == "kokoro":
            lines += ["Pronunciation input: every token was encoded without dropping symbols; stress marks, rough breathings, diphthongs and letter names are in the recorded phoneme strings. This establishes input control. Their realization in the audio and subjective naturalness still need listening.", ""]
        if "voice_gender_verification" in meta:
            lines += ["Female voice and Greek locale independently confirmed using macOS AVSpeechSynthesisVoice metadata; both installed Melina identifiers report female and el-GR.", ""]
    save_json(out/"qc-report.json", records)
    (out/"qc-report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/"config.yaml")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("build")
    p.add_argument("--voice", choices=VOICE_NAMES)
    p.add_argument("--sentences", type=int)
    p.add_argument("--rate", type=float)
    p.add_argument("--output-dir", type=Path)
    sub.add_parser("bakeoff")
    sub.add_parser("voices")
    sub.add_parser("qc")
    args = parser.parse_args()
    try:
        if platform.machine() != "arm64":
            raise ValueError("This experiment requires ARM64-native Python")
        cfg = yaml.safe_load(args.config.read_text())
        if getattr(args, "rate", None) is not None:
            cfg["speech"]["rate"] = args.rate
        validate(cfg)
        out = getattr(args, "output_dir", None) or (args.config.resolve().parent/cfg["output"]["directory"])
        if args.command == "build":
            build(cfg, out, args.voice, args.sentences)
        elif args.command == "bakeoff":
            bakeoff(cfg, out)
        elif args.command == "voices":
            voices = google_voices()
            for v in voices:
                if v.get("ssmlGender") == "FEMALE":
                    print(v["name"])
            save_json(ROOT/"work/google-female-voices.json", [v for v in voices if v.get("ssmlGender") == "FEMALE"])
        else:
            qc(out)
    except (ValueError, BackendError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
