# Codex Project: Euclid I.23 Text-to-Speech Experiment

## Objective

Build and execute a small, reproducible text-to-speech experiment that reads the opening one or two sentences of Euclid's *Elements*, Proposition I.23, in Ancient Greek.

Produce two audio samples:

1. **Anglophone Erasmian classroom pronunciation**, using stress accent rather than reconstructed Classical Greek pitch accent.
2. **Modern Greek pronunciation**, using a natural-sounding female voice.

The goal is to generate reasonably natural, intelligible audio for comparison in a Harvard Extension course presentation.

This is an experimental prototype, not a production-grade application. Prioritize producing and evaluating actual audio over implementing an elaborate framework.

The finished audio must be compatible with Google Slides.

## 1. Environment

Target machine:

- Apple Silicon Mac, M5 generation
- macOS
- Homebrew available
- `uv` for Python environments and dependencies
- FFmpeg available or installable through Homebrew
- Internet access for model downloads and cloud APIs
- Apple Silicon GPU/Metal available

Use an **ARM64-native Python environment** managed by `uv`.

Do not use Rosetta or x86_64 Python.

Select a Python version compatible with the chosen packages, preferably Python 3.12 or 3.13.

Verify the environment explicitly:

```bash
uname -m
uv run python -c "import platform; print(platform.machine())"
```

Both must report `arm64`.

Do not modify the user's global Python environment.

Use `uv` for dependency management and create a reproducible `pyproject.toml` and `uv.lock`.

Prefer models that run efficiently on Apple Silicon through PyTorch MPS, MLX, or CPU.

Do not install CUDA dependencies.

## 2. Available course materials

Codex already has access to the Harvard Extension course materials for *Reading Euclid's Elements in Greek*, including:

- the official course description of Proposition I.23;
- the assigned Ancient Greek text;
- recorded lectures;
- lecture transcripts;
- course notes;
- the existing AI-assisted lecture transcription and note-taking pipeline.

Use these materials to establish the correct text and the pronunciation conventions used in class.

The professor is Graeme Bird.

**Important correction:** The course uses **Anglophone Erasmian classroom pronunciation with stress accent**.

Do not implement reconstructed Classical Attic pronunciation, historical pitch accent, or another reconstructed pronunciation system.

The professor's recordings may be consulted to understand classroom pronunciation conventions, but do not attempt to imitate, clone, adapt, or synthesize his voice.

There is no speaker-specific synthesis component in this project.

### Existing related project

The public repository:

https://github.com/wihl/euclid-vid

contains a related Ancient Greek speech-processing project.

Inspect it only if useful for:

- Greek text handling;
- audio processing;
- FFmpeg conventions;
- project organization;
- quality-control techniques.

Do not modify that repository or create unnecessary dependencies on it.

## 3. Select the Greek passage

Locate the authoritative text of Euclid I.23 from the course materials.

Use the course's official description to establish the proposition's structure and identify the opening one or two sentences.

The complete proposition is expected to require approximately 90 seconds to read, which is unnecessarily long for this experiment.

Therefore, **default to the first two sentences**, or a shorter coherent opening passage if the first two sentences are unusually long.

The sample length must be configurable.

For example:

```yaml
passage:
  proposition: "I.23"
  selection: "first_sentences"
  sentence_count: 2
```

Support at least:

- `sentence_count: 1`
- `sentence_count: 2`
- `selection: full`

The `full` option is for future use and need not be rendered during the initial experiment.

Do not truncate a sentence merely to meet a duration target.

Do not confuse punctuation in geometrical notation with sentence boundaries.

Save the authoritative text in UTF-8:

`input/euclid-I23.txt`

Preserve the original polytonic Greek exactly.

The synthesis pipeline may use normalized or phonetic intermediate representations, but must never overwrite the authoritative text.

Document the selected passage and its source.

## 4. Pronunciation mode A: Anglophone Erasmian

This is the primary technical experiment.

Target the **Anglophone Erasmian classroom pronunciation used in the course**, not reconstructed Classical Greek.

Requirements:

- stress accent, not historical pitch accent;
- distinguish vowels and diphthongs according to the selected classroom convention;
- pronounce consonants according to that convention;
- handle rough breathings;
- use natural sentence stress and pauses;
- pronounce geometrical letters correctly;
- avoid silently converting the passage to Modern Greek phonology.

Erasmian pronunciation varies between academic traditions and individual instructors.

Use the course materials and available lecture examples to identify the specific Anglophone conventions used in this class.

Where the recordings or notes do not resolve a pronunciation choice, document the convention selected.

### Phonetic representation

Investigate whether a phoneme-controlled synthesis engine can produce the desired pronunciation.

A deterministic Greek-to-phoneme transformation may be useful.

For this short experiment, it is acceptable to construct and manually verify the phonetic representation of the selected passage rather than developing a comprehensive Ancient Greek phonology library.

Potential representations include:

- IPA;
- X-SAMPA;
- model-specific phoneme tokens;
- SSML phoneme markup, if supported by the selected engine.

The authoritative Greek text must remain separate from the phonetic representation.

The pronunciation rules should be documented sufficiently to reproduce the sample.

### Important limitation

Do not assume that a model supporting Modern Greek can correctly synthesize Anglophone Erasmian Greek.

Verify the output experimentally.

Natural-sounding but incorrectly pronounced Greek is not a successful Erasmian result.

## 5. Pronunciation mode B: Modern Greek female

Generate a natural Modern Greek reading of the same passage using a female voice.

Use a suitable Modern Greek TTS engine.

For this mode, normalize polytonic Greek into a representation appropriate for Modern Greek synthesis.

Preserve the original text separately.

Handle:

- accent placement;
- breathings;
- punctuation;
- diphthongs;
- geometrical letter names;
- appropriate pauses.

Do not use a male voice for this experiment.

The Modern Greek output serves as a comparison against the Anglophone Erasmian reading.

## 6. TTS engines and model selection

Evaluate a small number of practical synthesis approaches.

### Google Cloud Text-to-Speech

Google Cloud TTS is the preferred cloud candidate for the Modern Greek female voice.

Do not confuse Google Cloud Text-to-Speech with the Gemini API.

Existing Gemini, OpenAI, Claude, and Muse API credentials do not necessarily provide access to Google Cloud TTS.

Do not assume the user already has Google Cloud credentials.

Use Google's official documentation to verify:

- current Greek voice availability;
- female voice options;
- supported synthesis features;
- current authentication requirements;
- pricing or free-tier availability;
- whether the selected voice supports SSML or phoneme controls.

Do not invent voice identifiers or assume undocumented features are supported.

### Credential setup

Create a README section titled:

**Google Cloud TTS Setup**

Provide clear instructions for:

1. Creating or selecting a Google Cloud project.
2. Enabling billing if required.
3. Enabling the Cloud Text-to-Speech API.
4. Creating appropriate credentials.
5. Configuring authentication locally on macOS.
6. Testing that authentication works.
7. Understanding approximate costs for short samples.
8. Disabling the API or removing credentials afterward if desired.

Prefer Application Default Credentials using the Google Cloud CLI where appropriate.

Explain when an API key is supported versus when OAuth or service-account authentication is required.

Do not recommend embedding secrets in source code or committing credentials.

If credentials are unavailable, do not block the entire experiment. Continue with local alternatives and document the exact setup needed to enable Google Cloud TTS later.

### Local Hugging Face models

Investigate one or two promising pretrained TTS models available through Hugging Face.

Prefer models that:

- run on Apple Silicon;
- support phoneme or pronunciation control;
- have reasonable naturalness;
- can generate short audio efficiently;
- do not require fine-tuning;
- have clear licensing and documentation.

Consider multilingual models only when there is evidence they can help with the required pronunciation.

Do not download multiple multi-gigabyte models speculatively.

Inspect model cards, dependencies, language coverage, and Apple Silicon compatibility before downloading.

Use a project-local cache or a documented Hugging Face cache.

Do not train or fine-tune models for this experiment.

### Other cloud services

Do not evaluate Azure Speech or ElevenLabs.

Do not expand the project into a broad commercial TTS service comparison.

Existing OpenAI or Gemini credentials may be considered only if a suitable documented speech-synthesis capability is available and provides a meaningful advantage.

Do not assume general-purpose language-model APIs provide phoneme-controlled TTS.

## 7. Initial model bake-off

Before generating the full selected passage, choose a short Greek test phrase from I.23.

Aim for approximately 5–10 seconds of speech.

The phrase should contain several features that distinguish Erasmian from Modern Greek pronunciation.

Test a small number of promising approaches.

For each candidate, record:

- model or service;
- pronunciation mode;
- voice;
- whether phonetic input is supported;
- output duration;
- inference time;
- obvious pronunciation errors;
- naturalness;
- whether the complete phrase was spoken;
- resource usage;
- approximate cost, if applicable.

Do not claim pronunciation accuracy solely because a model supports Greek.

For the Erasmian version, compare the result against the documented classroom conventions.

If a candidate consistently produces Modern Greek pronunciation despite phonetic prompting, reject it for the Erasmian mode.

Do not spend hours trying to rescue a clearly unsuitable model.

Save findings in:

`output/model-comparison.md`

Distinguish observed results from untested expectations.

## 8. Generate the two final samples

Once the best approaches have been selected, synthesize the configured passage.

Required outputs:

```text
output/
  euclid-I23-erasmian.wav
  euclid-I23-erasmian.mp3
  euclid-I23-modern-female.wav
  euclid-I23-modern-female.mp3
```

If one pronunciation mode cannot be synthesized acceptably, do not fabricate a successful result.

Preserve the best available experimental output and document its limitations.

### Audio requirements

- Natural speaking rate.
- Intelligible pronunciation.
- Appropriate pauses.
- No English introduction.
- No background music.
- No artificial sound effects.
- No unnecessary silence at beginning or end.
- No clipped or truncated words.

Use WAV PCM as the master format and MP3 for Google Slides.

Do not create video.

### Speaking rate

Make speaking rate configurable.

For example:

```yaml
speech:
  rate: 1.0
```

Support reasonable slower playback, such as `0.85`, where the synthesis engine permits it.

Prefer controlling speaking rate during synthesis rather than slowing finished audio.

Do not use extreme rate adjustments that degrade pronunciation.

## 9. Configuration and command-line interface

Keep the interface simple.

A suggested configuration:

```yaml
passage:
  proposition: "I.23"
  selection: "first_sentences"
  sentence_count: 2

speech:
  rate: 1.0

voices:
  erasmian:
    enabled: true
    backend: auto

  modern_female:
    enabled: true
    backend: google_cloud

output:
  formats:
    - wav
    - mp3
```

The implementation may refine this configuration based on actual backend capabilities.

An ideal command is:

```bash
uv run python -m euclid_tts build
```

Support generating one voice independently:

```bash
uv run python -m euclid_tts build --voice erasmian
```

```bash
uv run python -m euclid_tts build --voice modern_female
```

Support overriding the number of sentences:

```bash
uv run python -m euclid_tts build --sentences 1
```

Avoid building a graphical interface.

## 10. Project structure

Use a small structure resembling:

```text
euclid-tts/
├── README.md
├── pyproject.toml
├── uv.lock
├── config.yaml
├── input/
│   └── euclid-I23.txt
├── src/
│   └── euclid_tts/
│       ├── __init__.py
│       ├── __main__.py
│       ├── text.py
│       ├── pronunciation.py
│       ├── synthesize.py
│       └── audio.py
├── work/
└── output/
    ├── euclid-I23-erasmian.wav
    ├── euclid-I23-erasmian.mp3
    ├── euclid-I23-modern-female.wav
    ├── euclid-I23-modern-female.mp3
    ├── model-comparison.md
    └── qc-report.md
```

Adjust the structure if a simpler implementation is appropriate.

Do not introduce a database, web server, frontend framework, or plugin architecture.

Keep downloaded models, caches, intermediate audio, and generated output out of Git unless there is a specific reason to retain a small example artifact.

## 11. Quality control

Run the experiment, not just the implementation.

For each generated sample:

- Verify the audio file is readable.
- Verify duration.
- Check for clipping.
- Check for unexpected silence.
- Check for missing or repeated words where feasible.
- Verify that the correct passage was selected.
- Verify the expected pronunciation mode.
- Verify the Modern Greek voice is female.
- Verify the MP3 files can be opened by ordinary media players.

For Erasmian pronunciation, inspect known phonetic contrasts rather than relying only on ASR.

Document uncertain pronunciations.

Automated tests should cover:

- UTF-8/polytonic Greek preservation;
- sentence selection;
- configurable sentence count;
- pronunciation normalization;
- Greek geometrical letter handling;
- output filenames;
- configuration validation;
- basic audio integrity.

Do not claim that automated tests establish subjective naturalness or historical pronunciation accuracy.

Generate:

`output/qc-report.md`

## 12. README requirements

The README should explain:

1. What the project does.
2. The two pronunciation modes.
3. The course's Anglophone Erasmian convention.
4. How the Greek passage was selected.
5. How to install dependencies with `uv`.
6. How to run each synthesis mode.
7. How to change the number of sentences.
8. How to change speaking rate.
9. How to obtain and configure Google Cloud TTS credentials.
10. Which local models were tested.
11. How to upload MP3 output to Google Drive and insert it into Google Slides.
12. Known limitations.

Include exact, tested commands.

Do not include secrets or private course recordings in the repository.

## 13. Execution and stopping rules

This is a bounded experiment.

Proceed through discovery, implementation, synthesis, and QC without stopping after writing code.

However:

- Do not wait indefinitely for cloud credentials.
- Do not repeatedly download unsuitable models.
- Do not train a new TTS model.
- Do not build a comprehensive Greek phonology engine.
- Do not implement voice cloning.
- Do not add male Modern Greek voices.
- Do not implement reconstructed Classical Greek.
- Do not spend hours optimizing marginal audio improvements.
- Do not introduce unnecessary abstractions.

If an approach fails, preserve diagnostics and try the next reasonable candidate.

If no available synthesis engine can produce acceptable Erasmian pronunciation, report that finding rather than silently substituting Modern Greek.

Keep the total experiment proportionate to the objective: two short samples for a class presentation.

## 14. Acceptance criteria

The experiment is complete when:

1. The authoritative I.23 Greek text has been identified from course materials.
2. The first one or two sentences can be selected through configuration.
3. The project runs under ARM64-native Python managed by `uv`.
4. An Erasmian synthesis approach has been tested and its pronunciation evaluated.
5. A Modern Greek female voice has been generated, if a suitable backend and credentials are available.
6. Available audio outputs are exported as WAV and MP3.
7. Automated tests and audio-integrity checks have been run.
8. The README explains Google Cloud TTS credential setup.
9. The final report clearly identifies successes, failures, and limitations.
10. The project can be rerun without using Codex interactively.

## 15. Final report

At completion, report:

- The exact Greek passage selected.
- The pronunciation conventions used.
- The models and services actually tested.
- Which outputs were successfully generated.
- Pronunciation errors or limitations.
- Approximate runtime.
- Whether Google Cloud credentials are still needed.
- Exact commands to reproduce the samples.
- Whether further experimentation is likely to produce a meaningful improvement.

**The principal deliverable is two short, contrasting readings of the same Greek text—not a general-purpose TTS system.**

Begin by examining the available course materials and identifying the passage. Then perform the smallest useful synthesis experiment and continue through final audio generation and QC.

