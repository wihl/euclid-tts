"""Source-preserving selection: Greek raised dots are internal pauses."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "input/euclid-I23.txt"
WORD = r"(?:(?![·;])[\u0370-\u03ff\u1f00-\u1fff])+"
LETTERS = re.compile(r"\b[Α-Ω]+\b")
TEST_PHRASE = "Πρὸς τῇ δοθείσῃ εὐθείᾳ καὶ τῷ πρὸς αὐτῇ σημείῳ τῇ δοθείσῃ γωνίᾳ εὐθυγράμμῳ ἴσην γωνίαν εὐθύγραμμον συστήσασθαι."


def sentences(text: str) -> list[str]:
    # No abbreviation/full stop appears inside a point label in this source.
    # An ano teleia is a semicolon, and must not split the second sentence.
    return [m.group().strip() for m in re.finditer(r"[^.!?]+(?:[.!?]|$)", text) if m.group().strip()]


def select(text: str, selection: str = "first_sentences", sentence_count: int = 2) -> str:
    if selection == "full":
        return text.strip()
    if selection != "first_sentences":
        raise ValueError("selection must be first_sentences or full")
    parts = sentences(text)
    if type(sentence_count) is not int or not 1 <= sentence_count <= len(parts):
        raise ValueError(f"sentence_count must be an integer from 1 to {len(parts)}")
    return " ".join(parts[:sentence_count])


def chunks(text: str) -> list[str]:
    """Keep clauses whole; punctuated pieces stay comfortably below 510 tokens."""
    return [m.group().strip() for m in re.finditer(r"[^,··.!?]+(?:[,··.!?]|$)", text) if m.group().strip()]
