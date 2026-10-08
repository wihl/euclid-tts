"""PCM masters, conservative edge trimming, MP3 export and integrity checks."""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 24000


def read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as f:
        if f.getsampwidth() != 2 or f.getnchannels() != 1:
            raise ValueError("Expected mono 16-bit PCM WAV")
        return np.frombuffer(f.readframes(f.getnframes()), dtype="<i2").astype(np.float32) / 32768, f.getframerate()


def trim_edges(data: np.ndarray, sr: int) -> np.ndarray:
    # Preserve 120 ms around every audible edge, including quiet consonants.
    active = np.flatnonzero(np.abs(data) > 0.001)
    if not len(active):
        raise ValueError("Synthesis returned silent audio")
    pad = int(0.12 * sr)
    return data[max(0, active[0]-pad):min(len(data), active[-1]+pad+1)]


def write_wav(path: Path, data: np.ndarray, sr: int = SAMPLE_RATE) -> dict:
    data = np.asarray(data, dtype=np.float32).reshape(-1)
    if not data.size or not np.isfinite(data).all():
        raise ValueError("Empty or non-finite audio")
    raw_peak = float(np.max(np.abs(data)))
    raw_clipped = int(np.count_nonzero(np.abs(data) >= 1))
    data = trim_edges(data, sr)
    # Attenuation only; report pre-export overloads rather than hiding them.
    gain = min(1.0, 0.89 / float(np.max(np.abs(data))))
    pcm = np.rint(data * gain * 32767).astype("<i2")
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(pcm.tobytes())
    return {"raw_peak": raw_peak, "raw_overload_samples": raw_clipped, "export_gain": gain}


def export_mp3(wav: Path) -> Path:
    mp3 = wav.with_suffix(".mp3")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "128k", str(mp3)], check=True)
    return mp3


def inspect(path: Path) -> dict:
    if path.suffix == ".mp3":
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)], capture_output=True, text=True, check=True)
        info = json.loads(probe.stdout)
        # Decode all frames to floating-point PCM and check codec overshoots.
        decoded = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-acodec", "pcm_f32le", "-"], capture_output=True, check=True)
        samples = np.frombuffer(decoded.stdout, dtype="<f4")
        if not len(samples) or not np.isfinite(samples).all():
            raise ValueError("Invalid decoded MP3 samples")
        return {"file": path.name, "duration_seconds": float(info["format"]["duration"]), "codec": info["streams"][0]["codec_name"], "peak_dbfs": float(20*np.log10(np.max(np.abs(samples)))), "clipped_samples": int(np.count_nonzero(np.abs(samples) >= 1)), "decode_ok": True}
    data, sr = read_wav(path)
    active = np.flatnonzero(np.abs(data) > 0.001)
    if not len(active):
        raise ValueError("Silent WAV")
    hop = max(1, int(sr * 0.02))
    windows = [float(np.sqrt(np.mean(data[i:i+hop]**2))) for i in range(0, len(data), hop)]
    silent = np.asarray(windows) < 0.001
    runs = []
    start = None
    for i, value in enumerate([*silent, False]):
        if value and start is None:
            start = i
        if not value and start is not None:
            duration = (i-start)*hop/sr
            if start > 0 and i < len(silent) and duration >= 0.3:
                runs.append({"start_seconds": round(start*hop/sr, 2), "duration_seconds": round(duration, 2)})
            start = None
    return {"file": path.name, "duration_seconds": len(data)/sr, "sample_rate": sr, "channels": 1, "pcm_bits": 16, "peak_dbfs": float(20*np.log10(np.max(np.abs(data)))), "clipped_samples": int(np.count_nonzero(np.abs(data) >= 32767/32768)), "leading_silence_seconds": float(active[0]/sr), "trailing_silence_seconds": float((len(data)-1-active[-1])/sr), "internal_silences_over_300ms": runs, "rms_dbfs": float(20*np.log10(np.sqrt(np.mean(data**2)))), "decode_ok": True}
