import hashlib
import importlib.util
import json
import re
from xml.etree import ElementTree as ET

import numpy as np
import pytest
import yaml

from euclid_tts import audio
from euclid_tts.__main__ import VOICE_NAMES, validate
from euclid_tts.pronunciation import erasmian, erasmian_ssml_words, modern
from euclid_tts.prosody import DEFAULT_PAUSES, phrase_plan
from euclid_tts.synthesize import google_ssml_batches, kokoro_render
from euclid_tts.text import ROOT, SOURCE, WORD, select, sentences


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
    assert modern("Ἔστω τῇ δοθείσῃ εὐθείᾳ") == "Έστω τη δοθείση ευθεία"
    assert modern("ἡ ὑπὸ ΑΒ ΔΓΕ") == "η υπό άλφα βήτα δέλτα γάμμα έψιλον"
    assert modern("ῥ ἁ ἀ ῳ ϊ ΐ") == "ρ α α ω ϊ ΐ"
    assert modern("ΔΓΕ· δεῖ δὴ") == "δέλτα γάμμα έψιλον, δει δη"
    assert modern("πρὸς τῇ καὶ τῷ τὸ δὲ") == "προς τη και τω το δε"
    assert modern("ὑπὸ αὐτῇ γωνίᾳ") == "υπό αυτή γωνία"
    assert modern("δοθείσῃ εὐθείᾳ συστήσασθαι", respelled=True) == "δοθίσι εφθία σιστίσασθε"


@pytest.mark.parametrize("section,key,value", [
    ("speech", "rate", 0), ("speech", "rate", 1.31), ("speech", "rate", True),
    ("passage", "sentence_count", False), ("passage", "sentence_count", 6),
    ("passage", "selection", "characters"), ("passage", "proposition", "I.22"),
    ("output", "formats", ["flac"]), ("output", "formats", ["wav", "wav"]),
    ("speech", "pauses", {"sentence": True}), ("speech", "pauses", {"phrase": -1}),
    ("speech", "pauses", {"word": 0.5}),
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
    assert mp3["clipped_samples"] == 0


def test_overloads_and_bad_audio_are_not_hidden(tmp_path):
    meta = audio.write_wav(tmp_path/"loud.wav", np.ones(240)*1.1)
    assert meta["raw_overload_samples"] == 240
    assert audio.inspect(tmp_path/"loud.wav")["clipped_samples"] == 0
    for data in [np.zeros(240), np.array([np.nan]), np.array([])]:
        with pytest.raises(ValueError):
            audio.write_wav(tmp_path/"bad.wav", data)


def test_phrase_planning_keeps_complete_source_and_geometry_groups():
    for count in [1, 2, 5]:
        selected = select(SOURCE.read_text(), sentence_count=count)
        plan = phrase_plan(selected)
        fold = lambda s: re.sub(r"\s+", " ", s).strip()
        assert fold(" ".join(p["greek"] for p in plan)) == fold(selected)
        assert plan[-1]["pause_after_seconds"] == 0
    opening = phrase_plan(select(SOURCE.read_text(), sentence_count=2))
    assert len(opening) == 11
    assert [p["greek"] for p in opening if "ΔΓΕ" in p["greek"]] == [
        "ἡ δὲ δοθεῖσα γωνία εὐθύγραμμος ἡ ὑπὸ ΔΓΕ·",
        "τῇ δοθείσῃ γωνίᾳ εὐθυγράμμῳ τῇ ὑπὸ ΔΓΕ",
    ]
    assert sum(p["pause_after_seconds"] for p in opening) == pytest.approx(6.0)


def test_google_ssml_covers_every_word_and_expanded_letter_once():
    selected = select(SOURCE.read_text(), sentence_count=2)
    expected = []
    for word in re.findall(WORD, selected):
        expected.extend(list(word) if re.fullmatch(r"[Α-Ω]+", word) else [word])
    batches = google_ssml_batches(phrase_plan(selected), "erasmian")
    actual = []
    for batch in batches:
        root = ET.fromstring(batch["ssml"])
        actual.extend(node.text for node in root.iter("phoneme"))
        assert len(batch["ssml"].encode("utf-8")) <= 5000
    assert actual == expected
    root = ET.fromstring("<speak>"+erasmian_ssml_words("ἡ ΑΒ & ὑπὸ")+"</speak>")
    assert [p.attrib["ph"] for p in root.iter("phoneme")] == ["heɪ", "ˈɑːlfɑː", "ˈbeɪtɑː", "hʊˈpɑː"]
    assert "&amp;" in ET.tostring(root, encoding="unicode")
    # Full selection also stays within the real service byte limit.
    for mode in ["erasmian", "modern_female"]:
        for batch in google_ssml_batches(phrase_plan(SOURCE.read_text().strip()), mode):
            ET.fromstring(batch["ssml"])
            assert len(batch["ssml"].encode("utf-8")) <= 5000


def test_pause_settings_change_actual_pcm_without_dropping_words():
    class FakeModel:
        voice = "test"
        artifacts = {}
        def __init__(self):
            self.words = []
        def synthesize(self, text, rate):
            self.words.append(text)
            return np.ones(2400, dtype=np.float32)*0.1, {}
    model = FakeModel()
    selected = select(SOURCE.read_text(), sentence_count=1)
    samples, _ = kokoro_render(model, selected, 0.82, {**DEFAULT_PAUSES, "phrase": 0.6})
    assert " ".join(model.words) == selected
    assert len(samples) == 4*2400 + 3*round(0.6*audio.SAMPLE_RATE)
    assert len(np.flatnonzero(samples)) == 4*2400


def test_source_provenance_is_portable():
    source = json.loads((ROOT/"input/source.json").read_text())
    assert source["course_pdf"] == "materials/books/Elements.pdf"
    assert source["course_transcription"].startswith("coursework/")


def test_public_path_scan_catches_metadata_and_home_root(tmp_path):
    spec = importlib.util.spec_from_file_location("public_paths", ROOT/"tools/check_public_paths.py")
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    # Construct test home paths without placing an absolute home in repo text.
    home = "/".join(["", "Users", "example"])
    (tmp_path/"source.json").write_text(json.dumps({"source": home+"/course/text.txt"}))
    (tmp_path/"checkpoint.md").write_text(home)
    (tmp_path/"portable.json").write_text(json.dumps({"source": "materials/books/Elements.pdf"}))
    (tmp_path/".venv").mkdir()
    (tmp_path/".venv/installed.txt").write_text(home+"/python")
    assert set(scanner.personal_paths(tmp_path)) == {"source.json", "checkpoint.md"}


def test_speech_leveling_lifts_quiet_endings_and_preserves_pauses(tmp_path):
    sr = audio.SAMPLE_RATE
    carrier = np.sin(2*np.pi*220*np.arange(sr)/sr).astype(np.float32)
    data = np.concatenate([0.5*carrier, 0.025*carrier, np.zeros(sr//2), 0.5*carrier]).astype(np.float32)
    leveled, meta = audio.level_speech(data)
    rms = lambda value: float(np.sqrt(np.mean(value**2)))
    body = slice(sr//2, sr)
    tail = slice(3*sr//2, 2*sr)
    contrast_before = 20*np.log10(rms(data[body])/rms(data[tail]))
    contrast_after = 20*np.log10(rms(leveled[body])/rms(leveled[tail]))
    assert contrast_after < contrast_before-4
    assert rms(leveled[tail]) > 1.5*rms(data[tail])
    assert len(leveled) == len(data) and meta["same_frame_count"]
    assert np.max(np.abs(leveled)) <= 0.891
    assert np.count_nonzero(leveled[2*sr:5*sr//2]) == 0
    assert meta["synthesis_raw_overload_samples"] == 0
    wav = tmp_path/"leveled.wav"
    audio.write_wav(wav, leveled)
    assert audio.inspect(audio.export_mp3(wav))["clipped_samples"] == 0


def test_leveling_does_not_hide_synthesis_overloads():
    raw = np.ones(2400, dtype=np.float32)*1.1
    leveled, meta = audio.level_speech(raw)
    assert meta["synthesis_raw_overload_samples"] == len(raw)
    assert np.max(np.abs(leveled)) <= 0.891


def test_current_defaults_use_one_sentence_and_level_only_erasmian():
    cfg = validate(config())
    assert cfg["passage"]["sentence_count"] == 1
    assert cfg["voices"]["erasmian"]["level_speech"] is True
    assert not cfg["voices"]["modern_female"].get("level_speech", False)
    cfg["voices"]["erasmian"]["level_speech"] = "true"
    with pytest.raises(ValueError, match="level_speech"):
        validate(cfg)
