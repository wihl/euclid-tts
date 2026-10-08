"""Finite I.23 course targets; engine approximations are applied separately."""
import re
import unicodedata as ud
from xml.sax.saxutils import escape, quoteattr

from .text import LETTERS, WORD

# Kokoro's IPA-like alphabet uses single-codepoint English diphthong tokens.
# A=aɪ, I=eɪ, O=oʊ, W=aʊ. The other symbols are course-target IPA.
# One primary stress per accented polysyllabic word; no historical pitch accent.
# Evidence: input/pronunciation-source.json and README's reconciliation table.
# Omicron selects unmerged American "off" /ɔ/; the handout gives no dialect.
LEXICON = {
    "πρὸς": "pɹɔs", "τῇ": "tI", "δοθείσῃ": "dɔˈθIsI",
    "εὐθείᾳ": "juːˈθIɑ", "καὶ": "kA", "τῷ": "tO", "αὐτῇ": "aʊˈtI",
    "σημείῳ": "sIˈmIO", "γωνίᾳ": "gOˈniːɑ", "εὐθυγράμμῳ": "juːθyˈgɹɑmO",
    "ἴσην": "ˈiːsIn", "γωνίαν": "gOˈniːɑn", "εὐθύγραμμον": "juːˈθygɹɑmɔn",
    "συστήσασθαι": "syˈstIsɑsθA", "ἔστω": "ˈɛstO", "ἡ": "hI",
    "μὲν": "mɛn", "δοθεῖσα": "dɔˈθIsɑ", "εὐθεῖα": "juːˈθIɑ", "τὸ": "tɔ",
    "δὲ": "dɛ", "σημεῖον": "sIˈmIɔn", "γωνία": "gOˈniːɑ",
    "εὐθύγραμμος": "juːˈθygɹɑmɔs", "ὑπὸ": "hyˈpɔ", "δεῖ": "dI",
    # The course note explicitly says δέ and δή are alike; exact vowel quality
    # is not transcribed. This prototype selects /ɛ/ for this pair only.
    "δὴ": "dɛ", "εἰλήφθω": "IˈlIfθO", "ἐφ᾿": "ɛf", "ἑκατέρας": "hɛkɑˈtɛɹɑs",
    "τῶν": "tOn", "τυχόντα": "tyˈxɔntɑ", "σημεῖα": "sIˈmIɑ", "τὰ": "tɑ",
    "ἐπεζεύχθω": "ɛpɛˈzjuːxθO", "ἐκ": "ɛk", "τριῶν": "tɹɪˈOn",
    "εὐθειῶν": "juːθIˈOn", "αἵ": "hA", "αἱ": "hA", "εἰσιν": "Isɪn",
    "εἰσὶν": "Iˈsiːn", "ἴσαι": "ˈiːsA", "τρισὶ": "tɹɪˈsiː", "ταῖς": "tAs",
    "τρίγωνον": "ˈtɹiːgOnɔn", "συνεστάτω": "synɛˈstɑtO", "ὥστε": "ˈhOstɛ",
    "εἶναι": "ˈInA", "τὴν": "tIn", "ἔτι": "ˈɛtɪ", "ἐπεὶ": "ɛˈpI", "οὖν": "uːn",
    "δύο": "ˈdyɔ", "ἑκατέρα": "hɛkɑˈtɛɹɑ", "ἑκατέρᾳ": "hɛkɑˈtɛɹɑ",
    "βάσις": "ˈbɑsɪs", "βάσει": "ˈbɑsI", "ἴση": "ˈiːsI", "ἄρα": "ˈɑɹɑ",
    "ἐστιν": "ɛstɪn", "συνέσταται": "syˈnɛstɑtA", "ὅπερ": "ˈhɔpɛɹ",
    "ἔδει": "ˈɛdI", "ποιῆσαι": "pɔɪˈIsA",
}
ERASMIAN_LETTERS = {
    "Α": "ˈɑlfɑ", "Β": "ˈbItɑ", "Γ": "ˈgɑmɑ", "Δ": "ˈdɛltɑ",
    "Ε": "ˈɛpsɪlɔn", "Ζ": "ˈzItɑ", "Η": "ˈItɑ",
}
CONVENTION = "bird-handout-and-class-2026-10-08"
GOOGLE_SUBSTITUTIONS = {
    "y": {"engine_ipa": "uː", "reason": "en-US lacks /y/; /uː/ preserves high rounded quality but loses frontness"},
    "x": {"engine_ipa": "k", "reason": "en-US lacks /x/; /k/ preserves velar place but loses frication"},
}
MODERN_LETTERS = {"Α": "άλφα", "Β": "βήτα", "Γ": "γάμμα", "Δ": "δέλτα", "Ε": "έψιλον", "Ζ": "ζήτα", "Η": "ήτα"}
MODERN_MONOSYLLABLES = {"πρός", "τή", "καί", "τώ", "μέν", "τό", "δέ", "δή", "δεί", "τών", "τά", "έκ", "αί", "ταίς", "τήν", "ούν"}

# Diagnostic phonetic spellings, not a translation or spelling correction.
# Keep the same inflections, stress and word order; make /i/ and /ef, af/
# explicit for unfamiliar Ancient forms. Used only with input: respelled.
MODERN_RESPELLINGS = {
    "δοθείση": "δοθίσι", "δοθείσα": "δοθίσα", "ευθεία": "εφθία",
    "αυτή": "αφτή", "σημείω": "σιμίο", "σημείον": "σιμίον",
    "ευθυγράμμω": "εφθιγράμμο", "ευθύγραμμον": "εφθίγραμμον",
    "ευθύγραμμος": "εφθίγραμμος", "ίσην": "ίσιν",
    "συστήσασθαι": "σιστίσασθε",
}


def erasmian(text: str) -> str:
    def word(match: re.Match) -> str:
        token = match.group()
        if re.fullmatch(r"[Α-Ω]+", token):
            try:
                return " ".join(ERASMIAN_LETTERS[c] for c in token)
            except KeyError as exc:
                raise ValueError(f"Unreviewed point label: {token}") from exc
        key = ud.normalize("NFC", token.lower())
        if key not in LEXICON:
            raise ValueError(f"Unreviewed Erasmian word: {token}")
        return LEXICON[key]
    result = re.sub(WORD, word, text).replace("·", ";").replace("·", ";")
    return re.sub(r"\s+", " ", result).replace("g", "ɡ").replace("aʊ", "W")


def ipa(phonemes: str) -> str:
    for token, value in {"A": "aɪ", "I": "eɪ", "O": "oʊ", "W": "aʊ"}.items():
        phonemes = phonemes.replace(token, value)
    return phonemes


def engine_phonemes(phonemes: str, backend: str) -> str:
    """Never put an English engine's missing sounds into the course lexicon."""
    if backend == "kokoro":
        # The pinned multilingual vocabulary contains /y/ and /x/. Their
        # realization by this stock American voice still needs a human ear.
        return phonemes
    if backend != "google_cloud":
        raise ValueError(f"Unreviewed Erasmian backend: {backend}")
    result = ipa(phonemes)
    for target, substitute in GOOGLE_SUBSTITUTIONS.items():
        result = result.replace(target, substitute["engine_ipa"])
    # Documented en-US vowel symbols; quantity is English engine encoding.
    return re.sub(r"ɔ(?!ɪ)", "ɔː", result.replace("ɑ", "ɑː"))


def pronunciation_record(text: str, backend: str) -> dict:
    target = erasmian(text)
    substitutions = []
    if backend == "google_cloud":
        for sound, details in GOOGLE_SUBSTITUTIONS.items():
            words = [m.group() for m in re.finditer(WORD, text) if sound in erasmian(m.group())]
            if words:
                substitutions.append({"course_ipa": sound, **details, "words": words})
    return {
        "pronunciation_convention": CONVENTION,
        "pronunciation_sources": "input/pronunciation-source.json",
        "ipa": ipa(target),
        "engine_ipa": ipa(engine_phonemes(target, backend)),
        "phoneme_substitutions": substitutions,
        "engine_vowel_encoding": "ɑ → ɑː; ɔ → ɔː (excluding ɔɪ); no claim of Greek quantity" if backend == "google_cloud" else "Kokoro diphthong tokens A/I/O/W; expanded in engine_ipa",
    }


def modern(text: str, respelled: bool = False) -> str:
    def letters(match: re.Match) -> str:
        try:
            return " ".join(MODERN_LETTERS[c] for c in match.group())
        except KeyError as exc:
            raise ValueError(f"Unreviewed point label: {match.group()}") from exc
    text = LETTERS.sub(letters, text)
    output = []
    for c in ud.normalize("NFD", text):
        if c in "\u0300\u0342":
            output.append("\u0301")  # grave/circumflex become stress (tonos)
        elif not ud.combining(c) or c in "\u0301\u0308":
            output.append(c)  # discard breathings and iota subscript
    # In Greek, ';' is a question mark. Use a comma for the source's raised
    # dot so a Modern Greek voice gets a pause without interrogative prosody.
    normalized = ud.normalize("NFC", "".join(output)).replace("·", ",").replace("·", ",").replace("᾿", "’")
    def accent_and_spelling(match):
        token = match.group()
        if token.lower() in MODERN_MONOSYLLABLES:
            token = ud.normalize("NFC", "".join(c for c in ud.normalize("NFD", token) if c != "\u0301"))
        if respelled and token.lower() in MODERN_RESPELLINGS:
            replacement = MODERN_RESPELLINGS[token.lower()]
            token = replacement.capitalize() if token[0].isupper() else replacement
        return token
    return re.sub(WORD, accent_and_spelling, normalized)


def erasmian_ssml_words(text: str) -> str:
    """One IPA tag per word; labels expand into one tag per letter name.

    Missing English /y x/ are substituted explicitly; metadata records both
    course and engine IPA. Vowel lengths are English encoding, not Greek quantity.
    """
    def tag(label, phonemes):
        phonemes = engine_phonemes(phonemes, "google_cloud")
        return f'<phoneme alphabet="ipa" ph={quoteattr(phonemes)}>{escape(label)}</phoneme>'
    def word(match):
        token = match.group()
        if re.fullmatch(r"[Α-Ω]+", token):
            return " ".join(tag(c, erasmian(c)) for c in token)
        return tag(token, erasmian(token))
    # Escape non-word text too, without escaping the tags inserted afterward.
    parts, position = [], 0
    for match in re.finditer(WORD, text):
        parts.extend([escape(text[position:match.start()]), word(match)])
        position = match.end()
    parts.append(escape(text[position:]))
    return "".join(parts).replace("·", ";").replace("·", ";")
