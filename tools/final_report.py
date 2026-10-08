"""Refresh the listening-feedback comparison from saved audio; no API calls."""
import hashlib
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
LATEST_REVIEW = (
    "The user judged the revised readings much better. A native Greek speaker, as reported by the user, "
    "found the default Modern WaveNet reading accurate. The Erasmian reading had some overly quiet "
    "word endings. The user requested one sentence to shorten the presentation clips. Current defaults "
    "read only the opening enunciation, retaining rate 0.72 and its three phrase pauses. Erasmian adds "
    "gentle volume leveling. The user then confirmed that the Erasmian drop-off was gone, but still found "
    "its overall tone synthesized compared with Modern Greek. The user rejected Chirp Leda as worse "
    "and found Neural2 lively slurred and poorly enunciated. The course-handout audit then corrected "
    "Erasmian ευ, υ, accented ι, χ and the selected omicron vowel, including the epsilon label. "
    "The corrected WaveNet reference uses reconciled targets and explicit English-engine substitutes. "
    "Subsequent Neural2 neutral F, firm F and neutral H trials use that corrected input. The user "
    "judged round-5 Neural2-H acceptable; its exact WAV/MP3 are now the Erasmian default without "
    "resynthesis. Firm F remains unreviewed and neutral F duplicated the corrected WaveNet reference. "
    "The shortened Modern WAV delivered for this review was an exact PCM excerpt of the approved performance."
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
    assert all(c["selected_greek"] == candidates[0]["selected_greek"] for c in candidates)
    assert all(c["source_sha256"] == source["input_sha256"] for c in candidates)
    all_audio = []
    for folder in [OUT, ROOT/"work/slower", ROOT/"work/melina-baseline"]:
        for path in sorted(folder.rglob("*")):
            if path.suffix in {".wav", ".mp3"}:
                all_audio.append({"path": str(path.relative_to(ROOT)), **audio.inspect(path)})
    assert all(c["decode_ok"] and c["clipped_samples"] == 0 for c in all_audio)
    assert all(c["raw_overload_samples"] == 0 for c in candidates)
    (OUT/"all-audio-integrity.json").write_text(json.dumps(all_audio, ensure_ascii=False, indent=2)+"\n")

    lines = ["# Listening results and saved comparisons", "", LATEST_REVIEW, "",
        "The tables below preserve the historical two-sentence comparisons and short controls. "
        "Current one-sentence defaults are described in [final-report.md](final-report.md).", "",
        "## Original listening feedback", "", FEEDBACK, "", "## Round-2 full comparisons", "",
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
    lines += ["", "Current defaults use **user-accepted Neural2-H English IPA Erasmian** and **Greek WaveNet normalized**, "
        "shortened to one sentence, with Erasmian leveling. The native listener approved the normalized "
        "Modern reading. "
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
        "The historical round-2 Erasmian engines used the same pre-audit finite targets: stress, rough /h/, silent iota subscript, "
        "/b ɡ d/, eta/ei /eɪ/, omega /oʊ/, and documented Anglophone diphthongs. Google's English IPA "
        "tags wrap each word and each expanded letter name separately. Its documented /ɑː/ encodes "
        "Kokoro's /ɑ/ without asserting Greek vowel quantity. Actual phonetic realization remains unverified.", "",
        "Those historical targets contained the defects corrected by the course audit. The current "
        "default uses ευ /juː/, accented ι /iː/, υ target /y/ with Google substitute /uː/, and χ "
        "target /x/ with Google substitute /k/. Omicron now selects unmerged American off /ɔ/. "
        "English /ɹ/ already agrees with the handout's run. Source pages, timestamps, remaining "
        "interpretation choices and engine limits are in the pronunciation table in `../README.md` "
        "and `../input/pronunciation-source.json`. Historical files remain unchanged; rerunning a "
        "recipe uses the current lexicon. No reconstructed pitch accent or speaker imitation is used.", "",
        "Modern pronunciation retains Ancient grammar and wording, so it still sounds linguistically archaic. "
        "The earlier report of mixed pronunciation was superseded by the native listener's approval of "
        "the default WaveNet reading. Other Modern variants have no reported listening verdict. "
        "The user confirmed that earlier Erasmian leveling fixed the word-ending drop-off, but its "
        "tone still sounded synthesized. Chirp Leda was rejected and Neural2 lively was slurred. "
        "The user then judged corrected Neural2-H acceptable; it was promoted unchanged. Firm F "
        "remains unreviewed. No ASR completeness verdict is claimed.", "",
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
                  "latest_review": LATEST_REVIEW,
                  "human_review_of_revisions": {"modern_wavenet": "accurate, native speaker as reported by user", "erasmian_pre_audit": "drop-off resolved according to user; tone still sounds synthesized", "chirp_leda": "rejected as worse", "neural2_lively": "somewhat better, but slurred and poorly enunciated", "erasmian_neural2_h": "acceptable, user; promoted unchanged"},
                  "source_sha256": source["input_sha256"]}
    (OUT/"model-comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2)+"\n")
    final = ["# One-sentence presentation clips", "", LATEST_REVIEW, "", "## Current defaults", "",
        "| Mode | Voice | WAV duration | Round-2 two-sentence |", "| --- | --- | ---: | ---: |"]
    for mode, meta, stem in [("Erasmian", e, "euclid-I23-erasmian"), ("Modern female", m, "euclid-I23-modern-female")]:
        old_path = OUT/"round-2/reviewed-defaults"/f"{stem}.json"
        candidate_name = "erasmian-google" if mode == "Erasmian" else "modern-wavenet"
        baseline = read(old_path) if old_path.exists() else next(c for c in candidates if c["candidate"] == candidate_name)
        old_seconds = baseline["audio"][0]["duration_seconds"]
        final.append(f"| {mode} | {meta['voice']} | {meta['audio'][0]['duration_seconds']:.3f}s | {old_seconds:.3f}s |")
    final += ["", "Both defaults use rate 0.72 with four breath groups and three 0.65-second phrase "
        "pauses (1.95 seconds requested in total). The longer approved/reference files are preserved in "
        "`round-2/reviewed-defaults/`. Future Cloud reruns can vary slightly. "
        + ("This Modern PCM preserves the approved reading exactly." if m.get("render_source", {}).get("pcm_identical_to_approved_prefix") else "This is a fresh Cloud render using the reviewed Modern settings."), "",
        f"Accepted Neural2-H synthesis/export took {e['elapsed_seconds']:.2f} seconds in native "
        f"{e['architecture']} Python; measured process maximum RSS was {e['process_max_rss_mib']:.1f} MiB. "
        "Both delivered defaults have zero source overloads and zero decoded WAV/MP3 clipping. "
        "Masters are mono 24 kHz, 16-bit PCM; MP3 copies are 128 kbit/s.", "",
        "## Exact selected Greek", "", e["selected_greek"], "",
        f"{source['edition']}; {source['locator']}. {source['independent_pdf_column_comparison']}", "",
        f"Source SHA-256: `{source['input_sha256']}`. Source bytes are unchanged.", "",
        "## Course convention audit", "",
        "The alphabet was checked against GreekAlphabetSequence.pdf pp. 1–2 and the diphthongs "
        "against p. 4. Class-3 remarks at 01:03:00–01:03:09, 01:05:36–01:05:54, 01:30:12 and "
        "01:32:20 take precedence; class 2 at 00:45:00–00:45:23 confirms ου as oo. "
        "See the row-by-row table in `../README.md` and source hashes / 29 changed entries in "
        "`../input/pronunciation-source.json`. Course files were only read.", "",
        "The corrected Google input uses ευ /juː/, stressed ι /iː/ and standalone υ substitute "
        "/uː/ for target /y/. χ target /x/ becomes /k/ in this English engine; it occurs only in "
        "the longer source, not the selected sentence. Selected omicron /ɔ/ is distinct from α /ɑ/; "
        "the handout does not specify the English dialect. δέ/δή remain equal at selected /dɛ/ "
        "because the notes establish equality but do not transcribe vowel quality.", "",
        f"Convention: `{e['pronunciation_convention']}`. Target and submitted IPA plus affected-word "
        "substitutions are recorded in `euclid-I23-erasmian.json`. The user accepted this short reading; "
        "that verdict does not establish exact /y x/ or settle the unresolved classroom choices. "
        "χ and the longer passage remain unauditioned under the corrected convention. Volume leveling is retained; earlier "
        "word-ending measurements apply only to the archived pre-correction waveform.", "",
        "See [comparisons and commands](model-comparison.md), [default QC](qc-report.md), and "
        "`all-audio-integrity.json` for measurements. Feedback is in `../EXPERIMENTS.md`. Google setup works."]
    check_path = OUT/"erasmian-level-check.json"
    if check_path.exists() and read(check_path).get("after_wav_sha256") == hashlib.sha256((OUT/"euclid-I23-erasmian.wav").read_bytes()).hexdigest():
        check = read(check_path)
        final += ["", "## Erasmian ending-volume check", "",
            "Google word-mark timestamps were measured on a diagnostic render whose PCM matches the "
            "reviewed first sentence after applying its saved export gain. Each ending uses the same "
            "last-200-ms active interval before and after leveling. Some consonants and unstressed syllables "
            "naturally have less energy; these levels support the quiet-ending concern without proving "
            "pronunciation errors.", "",
            "| Word | Original ending RMS | Leveled ending RMS | Gain |",
            "| --- | ---: | ---: | ---: |"]
        for row in check["words"]:
            if row["word"] in {"εὐθείᾳ", "εὐθυγράμμῳ", "συστήσασθαι"}:
                final.append(f"| {row['word']} | {row['before_tail_dbfs']:.1f} dBFS | {row['after_tail_dbfs']:.1f} dBFS | +{row['tail_gain_db']:.1f} dB |")
        final += ["", "Erasmian uses gentle 2:1 compression at -24 dBFS, +6 dB makeup and a "
            "latency-compensated peak limiter. No frame count, pitch, synthesis speed or pause position "
            "is changed by that processing. WAV and MP3 decode without clipping. Detailed word windows "
            "are saved in `erasmian-level-check.json`. The user confirmed that the adjusted Erasmian "
            "no longer tails off, though its overall tone remains less natural than Modern Greek."]
    historical = []
    reviews = {"neural2-lively": "Somewhat better, but slurred and poorly enunciated", "chirp-leda": "Rejected: worse than the previous iteration"}
    for name, review in reviews.items():
        folder = OUT/"round-4"/name
        if folder.exists():
            historical.append({**record(name, folder), "human_review": review, "convention": "pre-course-audit"})
    naturalness = []
    reference_hash = hashlib.sha256((OUT/"euclid-I23-erasmian.wav").read_bytes()).hexdigest()
    wavenet_folder = OUT/"round-5/corrected-wavenet-reference"
    wavenet_file = wavenet_folder/"euclid-I23-erasmian.wav"
    wavenet_hash = hashlib.sha256(wavenet_file.read_bytes()).hexdigest() if wavenet_file.exists() else None
    for name in ["neural2-neutral", "neural2-firm", "neural2-h"]:
        folder = OUT/"round-5"/name
        if (folder/"euclid-I23-erasmian.json").exists():
            c = record(name, folder)
            assert c["selected_greek"] == e["selected_greek"]
            assert c["ipa"] == e["ipa"] and c["engine_ipa"] == e["engine_ipa"]
            assert c["pronunciation_convention"] == e["pronunciation_convention"]
            assert c["rate"] == e["rate"] and c["pauses"] == e["pauses"]
            assert c["leveling"]["filter"] == e["leveling"]["filter"]
            c["wav_sha256"] = hashlib.sha256((folder/"euclid-I23-erasmian.wav").read_bytes()).hexdigest()
            c["identical_wav_to_default"] = c["wav_sha256"] == reference_hash
            c["identical_wav_to_wavenet_reference"] = c["wav_sha256"] == wavenet_hash
            c["human_review"] = "Acceptable, user; promoted unchanged" if name == "neural2-h" else "Duplicate of corrected WaveNet reference" if c["identical_wav_to_wavenet_reference"] else "Unreviewed; not selected"
            naturalness.append(c)
    natural_lines = ["# Erasmian naturalness and enunciation trials", "",
        "The current default and all round-5 candidates use the course-reconciled targets, rate 0.72, "
        "three 0.65-second phrase pauses and the same gentle leveling. The corrected default was "
        "regenerated and 31 tests passed before these additional trials. The user subsequently judged "
        "Neural2-H acceptable. Its WAV and MP3 were copied exactly into the default filenames; no "
        "resynthesis altered the accepted sample. Modern remains the native-approved excerpt.", "",
        "| Candidate | Voice | Style | WAV duration | Source overload samples | Result | MP3 |",
        "| --- | --- | --- | ---: | ---: | --- | --- |",
        f"| Final default | {e['voice']} | Neutral | {e['audio'][0]['duration_seconds']:.3f}s | {e['leveling']['synthesis_raw_overload_samples']} | Acceptable, user | [listen](euclid-I23-erasmian.mp3) |"]
    for c in naturalness:
        natural_lines.append(f"| {c['candidate']} | {c['voice']} | {c.get('expressive_style') or 'Neutral'} | {c['audio'][0]['duration_seconds']:.3f}s | {c['leveling']['synthesis_raw_overload_samples']} | {c['human_review']} | [listen](round-5/{c['candidate']}/euclid-I23-erasmian.mp3) |")
    natural_lines += ["",
        "Neural2-F neutral returned the exact same WAV bytes and PCM as WaveNet-F, despite the "
        "different requested voice name. This is an observed result for this request, not proof "
        "that the services always share a model. It adds no separate listening candidate. "
        "Firm delivery changes only full-sentence style relative to neutral F, seeking stronger "
        "enunciation without the rejected lively delivery. Neural2-H changes the stock female "
        "voice with neutral style and was judged acceptable by the user. Firm F remains unreviewed "
        "and was not selected. The accepted H sample has zero source overloads.", "",
        "Live inventories confirmed FEMALE/en-US; services accepted all 17 word-phoneme tags. "
        "The firm style uses Google's documented full-sentence preview extension. No time stretch, "
        "training, cloning, source edits or Modern rerender was performed. WAV/MP3 checks pass; "
        "encoding and request acceptance do not establish audible word completeness. The firm trial "
        "contains 12 full-scale samples in Google's source PCM before leveling (0.5 ms total). "
        "This evidence is retained in metadata and QC; output headroom cannot reverse source saturation. "
        "Corrected WaveNet and H have zero source overloads. Listen for harshness in firm delivery.", "",
        "Listen for the /j/ in ευ, machine-like /iː/ in γωνίᾳ and ἴσην, clear vowel separation "
        "in γωνίᾳ/γωνίαν, audible endings and natural rhythm through συστήσασθαι. Standalone υ "
        "is still an English /uː/ approximation to /y/. χ is absent here: a longer-word check "
        "would be needed to hear its /k/ substitution. Accurate stress, connected speech and "
        "the unresolved classroom choices are not settled by an overall acceptable listening verdict.", "",
        "## Recorded round-4 feedback (old lexicon)", "",
        "| Candidate | User verdict | MP3 |", "| --- | --- | --- |"]
    for c in historical:
        natural_lines.append(f"| {c['candidate']} | {c['human_review']} | [archive](round-4/{c['candidate']}/euclid-I23-erasmian.mp3) |")
    natural_lines += ["", "These historical samples use different phoneme targets and are retained as "
        "failed comparisons. They are not controls for the corrected default. The earlier reviewed "
        "WaveNet and pre-audit reports are preserved in `round-5/pre-correction/`; corrected WaveNet "
        "is preserved in `round-5/corrected-wavenet-reference/`.", "",
        "```bash", "uv run python -m euclid_tts build --voice erasmian",
        "uv run python -m euclid_tts --config experiments/round-5-erasmian-neural2-firm.yaml build",
        "uv run python -m euclid_tts --config experiments/round-5-erasmian-neural2-h.yaml build",
        "uv run python tools/final_report.py", "```", "",
        "[Google Neural2 expressive styles](https://docs.cloud.google.com/text-to-speech/docs/ssml#styles), "
        "[Documented English IPA inventory](https://docs.cloud.google.com/text-to-speech/docs/phonemes)."]
    write("naturalness-comparison.md", natural_lines)
    (OUT/"naturalness-comparison.json").write_text(json.dumps({"reference_wav_sha256": reference_hash,
        "pronunciation_convention": e["pronunciation_convention"], "candidates": naturalness,
        "corrected_wavenet_reference_sha256": wavenet_hash, "historical_candidates": historical,
        "human_review_of_corrected_samples": {"neural2_h": "acceptable, user; promoted unchanged", "firm_f": "unreviewed; not selected"}}, ensure_ascii=False, indent=2)+"\n")
    final += ["", "## Final selection and retained comparisons", "",
        "[Neural2 firm and neutral H samples](naturalness-comparison.md) test delivery and a different "
        "stock voice after the pronunciation correction. Neural2-F neutral was byte-identical to "
        "the corrected WaveNet reference. Chirp Leda and lively Neural2 are recorded as rejected/unclear "
        "historical trials. The user accepted Neural2-H, now the exact-copy default; firm F remains "
        "unreviewed. Modern remains the approved excerpt. No additional naturalness experiment is "
        "required for this bounded presentation task.", "",
        "## Reproduce", "", "```bash", 'export UV_CACHE_DIR="$PWD/.cache/uv"',
        "uv sync --python 3.12 --locked", "uv run pytest -q", "uv run python tools/check_public_paths.py",
        "uv run python -m euclid_tts build", "uv run python tools/final_report.py", "```", "",
        "The saved final WAV/MP3 files preserve the accepted performances; fresh cloud synthesis "
        "uses the same recipe but may vary. Google credentials, billing and API enablement already work.", "",
        "At the rates checked on 2026-10-08, the 1,008-character Neural2-H request is about $0.016 "
        "and the 192-character Greek WaveNet request about $0.00077 outside monthly allowances. "
        "This is a list-price estimate, not an account billing receipt. "
        "[Google pricing](https://cloud.google.com/text-to-speech/pricing)."]
    write("final-report.md", final)
    print(f"Saved five full comparisons and five short controls; {len(all_audio)} audio files decode without clipping")


if __name__ == "__main__":
    main()
