"""Refresh the listening-feedback comparison from saved audio; no API calls."""
import json

from euclid_tts import audio
from euclid_tts.text import ROOT

OUT = ROOT / "output"
NAMES = ["erasmian-google", "erasmian-kokoro", "modern-wavenet", "modern-wavenet-respelled", "modern-chirp"]
FEEDBACK = (
    "The user judged both round-1 default samples poor and rushed, with inadequate pauses for enunciation. "
    "The user reported that a native Greek listener found the Modern sample unclear and sounding like "
    "a mixture of Ancient and Modern pronunciation. These are listening results; the earlier passing "
    "file checks did not establish quality. Neither round-1 sample is an accepted final result. "
    "Original audio and pre-review reports remain in `round-1/`; see `../EXPERIMENTS.md`."
)


def read(path):
    return json.loads(path.read_text())


def write(name, lines):
    (OUT/name).write_text("\n".join(lines)+"\n", encoding="utf-8")


def record(name, folder):
    paths = list(folder.glob("euclid-I23-*.json"))
    if len(paths) != 1:
        raise ValueError(f"Expected one voice metadata file in {folder.name}")
    return {"candidate": name, "metadata": str(paths[0].relative_to(ROOT)), **read(paths[0])}


def main():
    candidates = [record(name, OUT/"round-2"/name) for name in NAMES]
    short = [record(name, OUT/"round-2/short"/name) for name in NAMES]
    e = read(OUT/"euclid-I23-erasmian.json")
    m = read(OUT/"euclid-I23-modern-female.json")
    source = read(ROOT/"input/source.json")
    assert e["selected_greek"] == m["selected_greek"]
    assert all(c["selected_greek"] == e["selected_greek"] for c in candidates)
    assert all(c["source_sha256"] == source["input_sha256"] for c in candidates)
    all_audio = []
    for folder in [OUT, ROOT/"work/slower", ROOT/"work/melina-baseline"]:
        for path in sorted(folder.rglob("*")):
            if path.suffix in {".wav", ".mp3"}:
                all_audio.append({"path": str(path.relative_to(ROOT)), **audio.inspect(path)})
    assert all(c["decode_ok"] and c["clipped_samples"] == 0 for c in all_audio)
    assert all(c["raw_overload_samples"] == 0 for c in candidates)
    (OUT/"all-audio-integrity.json").write_text(json.dumps(all_audio, ensure_ascii=False, indent=2)+"\n")

    lines = ["# Round 2: slower, phrased readings", "", FEEDBACK, "", "## Full comparisons", "",
        "Every full candidate uses synthesis rate **0.72**, with requested phrase/comma/section/sentence "
        "pauses of **0.65/0.85/1.15/1.30 seconds**. All read the same two Ancient sentences. Eleven reviewed "
        "breath groups give ten planned gaps, totaling 8.05 seconds before engine-generated silence. "
        "No finished audio was time-stretched.", "",
        "| Candidate | Engine / voice | Input | WAV duration | Build/export | Pauses ≥300 ms | MP3 |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |"]
    for c in candidates:
        a = c["audio"][0]
        style = c.get("input_style", "explicit phonemes / separate breath groups")
        mp3 = next(item["file"] for item in c["audio"] if item["file"].endswith(".mp3"))
        lines.append(f"| {c['candidate']} | {c['backend']} / {c['voice']} | {style} | {a['duration_seconds']:.3f}s | {c['elapsed_seconds']:.2f}s | {len(a['internal_silences_over_300ms'])} | [listen](round-2/{c['candidate']}/{mp3}) |")
    lines += ["", "New default files use **Google English IPA Erasmian** and **Greek WaveNet normalized**. "
        "This selects alternative engines for the next listening pass; no subjective winner is claimed. "
        "Slower local Kokoro, respelled WaveNet and slower Chirp remain available.", "",
        "## Pronunciation changes and limits", "",
        "Modern input still removes breathings/subscripts, maps accents to tonos, and expands labels. "
        "It now omits written accents on this proposition's monosyllabic function words: "
        "`πρὸς τῇ ... καὶ τῷ` becomes `προς τη ... και τω`. This fixes an input defect, "
        "without establishing that it caused the reported mixed pronunciation. "
        "[Modern Greek accent convention](https://www.greek-language.gr/greekLang/modern_greek/tools/lexica/triantafyllides/search.html?lq=%CF%84%CE%BF%CE%BD%CE%AF%CE%B6%CF%89).", "",
        "The additional WaveNet trial substitutes sound cues `δοθίσι`, `εφθία`, `σιστίσασθε` for "
        "`δοθείσῃ`, `εὐθείᾳ`, `συστήσασθαι`. These are diagnostic pronunciation inputs, "
        "not corrected orthography or translation; stress, inflections and word order remain. "
        "The normalized WaveNet reading remains the default so the spelling intervention can be compared separately.", "",
        "Both Erasmian engines use the same finite targets: stress, rough /h/, silent iota subscript, "
        "/b ɡ d/, eta/ei /eɪ/, omega /oʊ/, and documented Anglophone diphthongs. Google's English IPA "
        "tags wrap each word and each expanded letter name separately. Its documented /ɑː/ encodes "
        "Kokoro's /ɑ/ without asserting Greek vowel quantity. Actual phonetic realization remains unverified.", "",
        "Erasmian limitations remain: English rho, alpha/omicron merger, incomplete quantity/gemination, "
        "and two-phoneme /ɛʊ/ for ευ. English engines can impose vowel reduction and English rhythm. "
        "Course notes support rough /h/, silent subscript in τῷ, and equality of δέ/δή; other choices "
        "are selected prototype conventions. No reconstructed pitch accent or speaker imitation is used.", "",
        "Modern pronunciation retains Ancient grammar and wording, so it still sounds linguistically archaic. "
        "No word-level listening diagnoses were supplied; the reported mixture cannot yet be attributed "
        "to specific vowels, consonants, stress or grammar. The revisions have no human accuracy/naturalness "
        "verdict yet. No ASR completeness verdict is claimed.", "",
        "## Short controls", "",
        "Five first-sentence trials preceded the full renders, using rate **0.82** and pauses "
        "**0.45/0.65/0.90/1.10 seconds**. Exact recipes are in `../experiments/short/`; "
        "audio is in `round-2/short/`.", "",
        "| Candidate | Duration | Build/export |", "| --- | ---: | ---: |"]
    for c in short:
        lines.append(f"| {c['candidate']} | {c['audio'][0]['duration_seconds']:.3f}s | {c['elapsed_seconds']:.2f}s |")
    lines += ["", "All services accepted slower-rate SSML and produced measurable clause silences. WaveNet "
        "remained brisk relative to the others, prompting the more deliberate full preset. Rate settings "
        "do not guarantee identical timing across engines.", "", "## Verification and reproduction", "",
        f"All **{len(all_audio)}** saved WAV/MP3 files decode correctly with zero clipped decoded samples; "
        "all five full revisions also have zero raw overloads. Masters are mono 24 kHz, 16-bit PCM; MP3 "
        "copies are 128 kbit/s. Each candidate's JSON and QC report record measured pauses and peaks. "
        "These checks do not prove intelligibility or complete spoken word coverage.", "",
        "Live Google inventories confirmed FEMALE/en-US for Erasmian and FEMALE/el-GR for Modern. "
        "SSML controls within-request pauses; explicit PCM silence separates sentence/section requests. "
        "Kokoro uses cached 92.4 MB quantized weights on native ARM64 CPU, rendering each breath group. "
        "No new model download, training, OpenAI/Gemini speech, Azure or ElevenLabs was used.", "",
        "Google ADC, billing and API enablement already work; no further setup is needed. SSML markup "
        "counts toward billable characters. Character counts and request byte sizes are saved; account "
        "billing was not inspected. Short WaveNet requests cost fractions of a cent at list price; "
        "the bounded comparison costs cents outside free allowances. "
        "[Google pricing](https://cloud.google.com/text-to-speech/pricing).", "",
        "```bash", 'export UV_CACHE_DIR="$PWD/.cache/uv"', "uv sync --python 3.12 --locked", "uv run pytest -q",
        "uv run python tools/check_public_paths.py", "uv run python -m euclid_tts build",
        "uv run python -m euclid_tts --config experiments/round-2-modern-chirp.yaml build",
        "uv run python -m euclid_tts --config experiments/round-2-modern-wavenet-respelled.yaml build",
        "uv run python -m euclid_tts --config experiments/round-2-erasmian-kokoro.yaml build",
        "uv run python tools/final_report.py", "```", "",
        "All five full and five short configurations are saved in `../experiments/`. Cloud output can "
        "vary between reruns. Source provenance and reports use relative paths; the public-path checker "
        "scans project-owned text for personal absolute home paths.", "",
        "[SSML breaks and word phonemes](https://cloud.google.com/text-to-speech/docs/ssml), "
        "[English IPA](https://cloud.google.com/text-to-speech/docs/phonemes), "
        "[Greek female voices](https://cloud.google.com/text-to-speech/docs/list-voices-and-types), "
        "[Chirp SSML, currently preview](https://cloud.google.com/text-to-speech/docs/chirp3-hd)."]
    write("model-comparison.md", lines)
    comparison = {"feedback": FEEDBACK, "candidates": candidates, "short_control_candidates": short,
                  "human_review_of_revisions": "pending", "source_sha256": source["input_sha256"]}
    (OUT/"model-comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2)+"\n")
    final = ["# Saved result after listener feedback", "", FEEDBACK, "", "## New experimental defaults", "",
        "| Mode | Voice | WAV duration | Old default |", "| --- | --- | ---: | ---: |"]
    for mode, meta, stem in [("Erasmian", e, "euclid-I23-erasmian"), ("Modern female", m, "euclid-I23-modern-female")]:
        old_path = OUT/"round-1"/f"{stem}.json"
        # Original audio is local and Git-ignored; fresh clones still retain
        # the documented round-1 measurements, not fabricated baseline audio.
        old_seconds = read(old_path)["audio"][0]["duration_seconds"] if old_path.exists() else (30.003 if mode == "Erasmian" else 27.640)
        final.append(f"| {mode} | {meta['voice']} | {meta['audio'][0]['duration_seconds']:.3f}s | {old_seconds:.3f}s |")
    final += ["", "Both defaults use rate 0.72 and explicit grammatical pauses. They are readings for "
        "review; improved pronunciation and naturalness are not yet established. Alternatives remain saved.", "",
        "## Exact selected Greek", "", e["selected_greek"], "",
        f"{source['edition']}; {source['locator']}. {source['independent_pdf_column_comparison']}", "",
        f"Source SHA-256: `{source['input_sha256']}`. Source bytes are unchanged.", "",
        "See [comparisons and commands](model-comparison.md), [default QC](qc-report.md), and "
        "`all-audio-integrity.json` for measurements. Feedback is in `../EXPERIMENTS.md`. Google setup works."]
    write("final-report.md", final)
    print(f"Saved five full comparisons and five short controls; {len(all_audio)} audio files decode without clipping")


if __name__ == "__main__":
    main()
