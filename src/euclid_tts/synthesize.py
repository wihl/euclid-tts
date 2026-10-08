"""One small phoneme model, Google ADC, and an installed macOS female fallback."""
import base64
import hashlib
import io
import json
import os
import subprocess
import wave
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import numpy as np

from . import audio
from .pronunciation import engine_phonemes, erasmian, erasmian_ssml_words, modern
from .prosody import phrase_plan
from .text import ROOT, sentences

MODEL_REPO = "onnx-community/Kokoro-82M-v1.0-ONNX"
MODEL_REVISION = "1939ad2a8e416c0acfeecc08a694d14ef25f2231"
VOCAB_REVISION = "f3ff3571791e39611d31c381e3a41a3af07b4987"
CACHE = ROOT / ".cache/huggingface"


class BackendError(RuntimeError):
    pass


def google_session():
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return AuthorizedSession(credentials)


def google_voices(language_code: str = "el-GR") -> list[dict]:
    try:
        response = google_session().get("https://texttospeech.googleapis.com/v1/voices", params={"languageCode": language_code}, timeout=30)
    except Exception as exc:
        # Exception strings can contain credential paths or token responses.
        raise BackendError(f"Google authentication/network failed ({type(exc).__name__}); see README Google Cloud TTS Setup") from None
    if not response.ok:
        error = response.json().get("error", {})
        status = error.get("status", "unknown")
        reasons = [d.get("reason") for d in error.get("details", []) if d.get("reason")]
        raise BackendError(f"Google voices HTTP {response.status_code}: {status}; reasons: {', '.join(reasons) or 'unspecified'}")
    return response.json().get("voices", [])


class Kokoro:
    def __init__(self, voice: str = "af_heart"):
        from huggingface_hub import hf_hub_download
        from onnxruntime import InferenceSession, SessionOptions
        if voice not in {"af_heart", "af_bella"}:
            raise ValueError("Reviewed Kokoro voices: af_heart, af_bella")
        # Public downloads need no token; all mutable caches stay in this project.
        os.environ.setdefault("HF_HOME", str(CACHE))
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        from huggingface_hub.errors import LocalEntryNotFoundError
        def download(repo, filename, revision):
            args = dict(repo_id=repo, filename=filename, revision=revision, cache_dir=CACHE, token=False)
            try:
                return Path(hf_hub_download(**args, local_files_only=True))
            except LocalEntryNotFoundError:
                return Path(hf_hub_download(**args))
        def fetch(filename):
            return download(MODEL_REPO, filename, MODEL_REVISION)
        config_path = download("hexgrad/Kokoro-82M", "config.json", VOCAB_REVISION)
        model_path = fetch("onnx/model_quantized.onnx")
        voice_path = fetch(f"voices/{voice}.bin")
        self.vocab = json.loads(config_path.read_text())["vocab"]
        self.styles = np.fromfile(voice_path, dtype=np.float32).reshape(-1, 1, 256)
        options = SessionOptions()
        options.intra_op_num_threads = 4
        options.inter_op_num_threads = 1
        self.session = InferenceSession(str(model_path), sess_options=options, providers=["CPUExecutionProvider"])
        self.voice = voice
        self.artifacts = {"model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(), "voice_sha256": hashlib.sha256(voice_path.read_bytes()).hexdigest(), "model_bytes": model_path.stat().st_size, "voice_bytes": voice_path.stat().st_size, "revision": MODEL_REVISION, "vocab_revision": VOCAB_REVISION, "provider": self.session.get_providers()}

    def synthesize(self, text: str, rate: float) -> tuple[np.ndarray, dict]:
        phonemes = engine_phonemes(erasmian(text), "kokoro")
        unknown = sorted(set(phonemes)-self.vocab.keys())
        if unknown:
            raise ValueError(f"Unrepresentable Kokoro phonemes: {unknown}")
        ids = [self.vocab[p] for p in phonemes]
        if not 1 <= len(ids) <= 510:
            raise ValueError(f"Kokoro phoneme count {len(ids)} exceeds 510; split at punctuation")
        wave_data = self.session.run(None, {"input_ids": np.array([[0, *ids, 0]], dtype=np.int64), "style": self.styles[len(ids)], "speed": np.array([rate], dtype=np.float32)})[0]
        return np.asarray(wave_data).reshape(-1), {"greek": text, "phonemes": phonemes, "phoneme_count": len(ids), "all_tokens_encoded": True}


def kokoro_render(model: Kokoro, text: str, rate: float, pauses: dict | None = None) -> tuple[np.ndarray, dict]:
    clips, records = [], []
    plan = phrase_plan(text, pauses)
    for group in plan:
        clip, record = model.synthesize(group["greek"], rate)
        clips.append(audio.trim_edges(clip, audio.SAMPLE_RATE))
        records.append({**record, **group})
        if group["pause_after_seconds"]:
            clips.append(np.zeros(round(audio.SAMPLE_RATE * group["pause_after_seconds"]), dtype=np.float32))
    return np.concatenate(clips), {"backend": "kokoro", "voice": model.voice, "model": MODEL_REPO, "chunks": records, "phrase_plan": plan, **model.artifacts}


def google_ssml_batches(plan: list[dict], mode: str, respelled: bool = False) -> list[dict]:
    batches, groups = [], []
    def finish():
        pieces = []
        for i, group in enumerate(groups):
            greek = group["greek"]
            pieces.append(erasmian_ssml_words(greek) if mode == "erasmian" else escape(modern(greek, respelled)))
            if i < len(groups)-1:
                pieces.append(f'<break time="{round(1000*group["pause_after_seconds"])}ms"/>')
        ssml = "<speak>" + " ".join(pieces) + "</speak>"
        if len(ssml.encode("utf-8")) > 5000:
            raise ValueError("SSML request exceeds Google's 5,000-byte limit")
        batches.append({"ssml": ssml, "greek": " ".join(g["greek"] for g in groups), "pause_after_seconds": groups[-1]["pause_after_seconds"]})
    for group in plan:
        groups.append(group)
        if group["boundary"] in {"sentence", "section"}:
            finish()
            groups = []
    if groups:
        finish()
    return batches


def google_render(text: str, voice: str, rate: float, voices: list[dict] | None = None, *, mode: str = "modern_female", pauses: dict | None = None, respelled: bool = False, style: str | None = None) -> tuple[np.ndarray, dict]:
    language_code = "en-US" if mode == "erasmian" else "el-GR"
    voices = google_voices(language_code) if voices is None else voices
    selected = next((v for v in voices if v["name"] == voice), None)
    if not selected or selected.get("ssmlGender") != "FEMALE" or language_code not in selected.get("languageCodes", []):
        raise BackendError(f"Google has not confirmed {voice} as an available {language_code} female voice")
    plan = phrase_plan(text, pauses)
    batches = google_ssml_batches(plan, mode, respelled)
    if style is not None:
        if voice != "en-US-Neural2-F" or not isinstance(style, str) or style not in {"apologetic", "calm", "empathetic", "firm", "lively"}:
            raise ValueError("This prototype uses documented expressive styles only with en-US-Neural2-F")
        if len(batches) != len(sentences(text)):
            raise ValueError("Style tags require whole-sentence batches; use one sentence")
        for batch in batches:
            body = batch["ssml"].removeprefix("<speak>").removesuffix("</speak>")
            batch["ssml"] = f'<speak><google:style name={quoteattr(style)}>{body}</google:style></speak>'
            if len(batch["ssml"].encode("utf-8")) > 5000:
                raise ValueError("Styled SSML request exceeds Google's 5,000-byte limit")
    session = google_session()
    clips = []
    for batch in batches:
        payload = {"input": {"ssml": batch["ssml"]}, "voice": {"languageCode": language_code, "name": voice}, "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": audio.SAMPLE_RATE, "speakingRate": rate}}
        clip = google_request(session, payload)
        clips.append(audio.trim_edges(clip, audio.SAMPLE_RATE))
        batch["request_bytes"] = len(batch["ssml"].encode("utf-8"))
        if batch["pause_after_seconds"]:
            clips.append(np.zeros(round(audio.SAMPLE_RATE*batch["pause_after_seconds"]), dtype=np.float32))
    return np.concatenate(clips), {"backend": "google_cloud", "voice": voice, "gender": selected["ssmlGender"], "locale": language_code, "expressive_style": style, "input_style": "ipa_ssml" if mode == "erasmian" else "respelled_ssml" if respelled else "normalized_ssml", "normalized_text": modern(text, respelled) if mode != "erasmian" else None, "characters": sum(len(b["ssml"]) for b in batches), "phrase_plan": plan, "requests": batches}


def google_request(session, payload: dict) -> np.ndarray:
    try:
        response = session.post("https://texttospeech.googleapis.com/v1/text:synthesize", json=payload, timeout=60)
    except Exception as exc:
        raise BackendError(f"Google synthesis failed ({type(exc).__name__})") from None
    if not response.ok:
        error = response.json().get("error", {})
        raise BackendError(f"Google synthesis HTTP {response.status_code}: {error.get('status', 'unknown')}; {error.get('message', '')[:300]}")
    raw = base64.b64decode(response.json()["audioContent"])
    with wave.open(io.BytesIO(raw), "rb") as f:
        if f.getsampwidth() != 2 or f.getnchannels() != 1 or f.getframerate() != audio.SAMPLE_RATE:
            raise BackendError("Unexpected Google PCM format")
        samples = np.frombuffer(f.readframes(f.getnframes()), dtype="<i2").astype(np.float32)/32768
    return samples


def melina_render(text: str, rate: float, target: Path) -> tuple[np.ndarray, dict]:
    # Melina is the installed macOS el_GR female voice; never pick by locale alone.
    listing = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, check=True).stdout
    if not any(line.startswith("Melina ") and "el_GR" in line for line in listing.splitlines()):
        raise BackendError("The macOS Melina Greek female voice is not installed")
    normalized = modern(text)
    target.parent.mkdir(parents=True, exist_ok=True)
    txt = target.with_suffix(".txt")
    txt.write_text(normalized, encoding="utf-8")
    raw = target.with_suffix(".aiff")
    try:
        subprocess.run(["say", "-v", "Melina", "-r", str(round(175*rate)), "-f", str(txt), "-o", str(raw)], check=True, timeout=120, capture_output=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-ac", "1", "-ar", str(audio.SAMPLE_RATE), "-c:a", "pcm_s16le", str(target)], check=True)
    except subprocess.CalledProcessError as exc:
        raise BackendError(f"macOS Melina synthesis failed (exit {exc.returncode})") from None
    data, _ = audio.read_wav(target)
    meta = {"backend": "macos", "voice": "Melina", "locale": "el_GR", "gender": "female (macOS stock voice)", "normalized_text": normalized, "words_per_minute": round(175*rate)}
    evidence = ROOT/"work/macos-voices.json"
    if evidence.exists():
        voices = json.loads(evidence.read_text())
        if voices and all(v.get("name") == "Melina" and v.get("gender") == "female" and v.get("locale") == "el-GR" for v in voices):
            meta["voice_gender_verification"] = {"method": "macOS AVSpeechSynthesisVoice metadata via tools/voice_info.swift (saved discovery)", "voices": voices}
    return data, meta
