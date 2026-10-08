import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from euclid_tts import audio
from euclid_tts.__main__ import VOICE_NAMES, validate
from euclid_tts.pronunciation import erasmian, modern
from euclid_tts.text import ROOT, SOURCE, select, sentences


def config():
    return yaml.safe_load((ROOT/"config.yaml").read_text())


def test_source_bytes_and_polytonic_preservation():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "4b364cf450c5a905e00c0320b06d1e44510fc2d840adfbe013174c40d061333e"
    text = raw.decode("utf-8")
    assert "τῇ δοθείσῃ εὐθείᾳ" in text
    assert select(text, "full") == text.strip()
    modern(text)
    erasmian(text)
    assert SOURCE.read_bytes() == raw


def test_sentence_selection_preserves_setting_out_and_specification():
    text = SOURCE.read_text()
    assert len(sentences(text)) == 5
    first = select(text, sentence_count=1)
    second = select(text, sentence_count=2)
    assert first.endswith("συστήσασθαι.")
    assert "ΑΒ" not in first
    assert "ΔΓΕ·\nδεῖ δὴ" in second
    assert second.endswith("συστήσασθαι.")
    assert "Εἰλήφθω" not in second
    assert "Ἔστω" in second
    for count in [0, 6, True, 1.5]:
        with pytest.raises(ValueError):
            select(text, sentence_count=count)


def test_erasmian_contrasts_and_letter_names():
    assert erasmian("ἡ ὑπὸ") == "hI hʊˈpɑ"
    assert erasmian("δοθεῖσα") == "dɑˈθIsɑ"
    assert erasmian("εὐθεῖα").startswith("ɛʊ")
    assert erasmian("ΑΒ ΔΓΕ") == "ˈɑlfɑ ˈbItɑ ˈdɛltɑ ˈɡɑmɑ ˈɛpsɪlɑn"
    assert erasmian("τῷ") == "tO"
    assert erasmian("δὲ") == erasmian("δὴ")
    with pytest.raises(ValueError, match="Unreviewed"):
        erasmian("ἀνεξέταστον")


def test_modern_normalization_and_geometry():
    assert modern("Ἔστω τῇ δοθείσῃ εὐθείᾳ") == "Έστω τή δοθείση ευθεία"
    assert modern("ἡ ὑπὸ ΑΒ ΔΓΕ") == "η υπό άλφα βήτα δέλτα γάμμα έψιλον"
    assert modern("ῥ ἁ ἀ ῳ ϊ ΐ") == "ρ α α ω ϊ ΐ"


@pytest.mark.parametrize("section,key,value", [
    ("speech", "rate", 0), ("speech", "rate", 1.31), ("speech", "rate", True),
    ("passage", "sentence_count", False), ("passage", "sentence_count", 6),
    ("passage", "selection", "characters"), ("passage", "proposition", "I.22"),
    ("output", "formats", ["flac"]), ("output", "formats", ["wav", "wav"]),
])
def test_invalid_config(section, key, value):
    cfg = config()
    cfg[section][key] = value
    with pytest.raises(ValueError):
        validate(cfg)


def test_valid_rate_full_and_filenames():
    cfg = config()
    cfg["speech"]["rate"] = 0.85
    cfg["passage"]["selection"] = "full"
    validate(cfg)
    assert set(VOICE_NAMES.values()) == {"euclid-I23-erasmian", "euclid-I23-modern-female"}


def test_pcm_mp3_integrity_and_silence_detection(tmp_path):
    sr = audio.SAMPLE_RATE
    tone = (0.4*np.sin(2*np.pi*220*np.arange(sr//2)/sr)).astype(np.float32)
    data = np.concatenate([np.zeros(sr//4), tone, np.zeros(sr//2), tone, np.zeros(sr//4)])
    path = tmp_path/"check.wav"
    metadata = audio.write_wav(path, data)
    wav = audio.inspect(path)
    assert metadata["raw_overload_samples"] == 0
    assert wav["clipped_samples"] == 0
    assert wav["sample_rate"] == sr
    assert 1.73 < wav["duration_seconds"] < 1.75
    assert 0.48 <= wav["internal_silences_over_300ms"][0]["duration_seconds"] <= 0.52
    assert wav["leading_silence_seconds"] <= 0.121
    mp3 = audio.inspect(audio.export_mp3(path))
    assert mp3["codec"] == "mp3" and mp3["decode_ok"]


def test_overloads_and_bad_audio_are_not_hidden(tmp_path):
    meta = audio.write_wav(tmp_path/"loud.wav", np.ones(240)*1.1)
    assert meta["raw_overload_samples"] == 240
    assert audio.inspect(tmp_path/"loud.wav")["clipped_samples"] == 0
    for data in [np.zeros(240), np.array([np.nan]), np.array([])]:
        with pytest.raises(ValueError):
            audio.write_wav(tmp_path/"bad.wav", data)
