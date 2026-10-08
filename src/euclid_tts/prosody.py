"""Reviewed grammatical breath groups for the opening; punctuation elsewhere."""
import re

from .text import SOURCE, chunks, select

DEFAULT_PAUSES = {"phrase": 0.45, "comma": 0.65, "section": 0.9, "sentence": 1.1}

# These boundaries preserve every source word and punctuation mark. Avoid
# splitting article+noun or individual letters within a geometrical label.
OPENING_GROUPS = [
    ("Πρὸς τῇ δοθείσῃ εὐθείᾳ", "phrase"),
    ("καὶ τῷ πρὸς αὐτῇ σημείῳ", "phrase"),
    ("τῇ δοθείσῃ γωνίᾳ εὐθυγράμμῳ", "phrase"),
    ("ἴσην γωνίαν εὐθύγραμμον συστήσασθαι.", "sentence"),
    ("Ἔστω ἡ μὲν δοθεῖσα εὐθεῖα ἡ ΑΒ,", "comma"),
    ("τὸ δὲ πρὸς αὐτῇ σημεῖον τὸ Α,", "comma"),
    ("ἡ δὲ δοθεῖσα γωνία εὐθύγραμμος ἡ ὑπὸ ΔΓΕ·", "section"),
    ("δεῖ δὴ πρὸς τῇ δοθείσῃ εὐθείᾳ τῇ ΑΒ", "phrase"),
    ("καὶ τῷ πρὸς αὐτῇ σημείῳ τῷ Α", "phrase"),
    ("τῇ δοθείσῃ γωνίᾳ εὐθυγράμμῳ τῇ ὑπὸ ΔΓΕ", "phrase"),
    ("ἴσην γωνίαν εὐθύγραμμον συστήσασθαι.", "sentence"),
]


def pause_settings(speech: dict) -> dict:
    return {**DEFAULT_PAUSES, **speech.get("pauses", {})}


def phrase_plan(text: str, pauses: dict | None = None) -> list[dict]:
    pauses = DEFAULT_PAUSES if pauses is None else pauses
    fold = lambda value: re.sub(r"\s+", " ", value).strip()
    remaining = fold(text)
    opening = fold(select(SOURCE.read_text(), sentence_count=2))
    groups = []
    if opening.startswith(remaining) or remaining.startswith(opening):
        for greek, boundary in OPENING_GROUPS:
            if not remaining.startswith(greek):
                break
            groups.append({"greek": greek, "boundary": boundary})
            remaining = remaining[len(greek):].strip()
            if not remaining:
                break
    for greek in chunks(remaining):
        boundary = "sentence" if greek.endswith(".") else "section" if greek.endswith(("·", "·")) else "comma"
        groups.append({"greek": greek, "boundary": boundary})
    if fold(" ".join(g["greek"] for g in groups)) != fold(text):
        raise ValueError("Phrase planning changed the selected source text")
    for i, group in enumerate(groups):
        group["pause_after_seconds"] = pauses[group["boundary"]] if i < len(groups)-1 else 0.0
    return groups
