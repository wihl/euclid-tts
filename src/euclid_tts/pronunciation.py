"""A manually reviewed I.23 lexicon, not a general Ancient Greek G2P."""
import re
import unicodedata as ud

from .text import LETTERS, WORD

# Kokoro's IPA-like alphabet uses single-codepoint English diphthong tokens.
# A=aɪ, I=eɪ, O=oʊ, W=aʊ; ευ is represented with ɛ + ʊ.
# One primary stress per accented polysyllabic word; no historical pitch accent.
LEXICON = {
    "πρὸς": "pɹɑs", "τῇ": "tI", "δοθείσῃ": "dɑˈθIsI",
    "εὐθείᾳ": "ɛʊˈθIɑ", "καὶ": "kA", "τῷ": "tO", "αὐτῇ": "aʊˈtI",
    "σημείῳ": "sIˈmIO", "γωνίᾳ": "gOˈnɪɑ", "εὐθυγράμμῳ": "ɛʊθʊˈgɹɑmO",
    "ἴσην": "ˈɪsIn", "γωνίαν": "gOˈnɪɑn", "εὐθύγραμμον": "ɛʊˈθʊgɹɑmɑn",
    "συστήσασθαι": "sʊˈstIsɑsθA", "ἔστω": "ˈɛstO", "ἡ": "hI",
    "μὲν": "mɛn", "δοθεῖσα": "dɑˈθIsɑ", "εὐθεῖα": "ɛʊˈθIɑ", "τὸ": "tɑ",
    "δὲ": "dɛ", "σημεῖον": "sIˈmIɑn", "γωνία": "gOˈnɪɑ",
    "εὐθύγραμμος": "ɛʊˈθʊgɹɑmɑs", "ὑπὸ": "hʊˈpɑ", "δεῖ": "dI",
    # The course note explicitly says δέ and δή are alike; exact vowel quality
    # is not transcribed. This prototype selects /ɛ/ for this pair only.
    "δὴ": "dɛ", "εἰλήφθω": "IˈlIfθO", "ἐφ᾿": "ɛf", "ἑκατέρας": "hɛkɑˈtɛɹɑs",
    "τῶν": "tOn", "τυχόντα": "tʊˈkɑntɑ", "σημεῖα": "sIˈmIɑ", "τὰ": "tɑ",
    "ἐπεζεύχθω": "ɛpɛˈzɛʊkθO", "ἐκ": "ɛk", "τριῶν": "tɹɪˈOn",
    "εὐθειῶν": "ɛʊθIˈOn", "αἵ": "hA", "αἱ": "hA", "εἰσιν": "Isɪn",
    "εἰσὶν": "Iˈsɪn", "ἴσαι": "ˈɪsA", "τρισὶ": "tɹɪˈsɪ", "ταῖς": "tAs",
    "τρίγωνον": "ˈtɹɪgOnɑn", "συνεστάτω": "sʊnɛˈstɑtO", "ὥστε": "ˈhOstɛ",
    "εἶναι": "ˈInA", "τὴν": "tIn", "ἔτι": "ˈɛtɪ", "ἐπεὶ": "ɛˈpI", "οὖν": "uːn",
    "δύο": "ˈdʊɑ", "ἑκατέρα": "hɛkɑˈtɛɹɑ", "ἑκατέρᾳ": "hɛkɑˈtɛɹɑ",
    "βάσις": "ˈbɑsɪs", "βάσει": "ˈbɑsI", "ἴση": "ˈɪsI", "ἄρα": "ˈɑɹɑ",
    "ἐστιν": "ɛstɪn", "συνέσταται": "sʊˈnɛstɑtA", "ὅπερ": "ˈhɑpɛɹ",
    "ἔδει": "ˈɛdI", "ποιῆσαι": "pɔɪˈIsA",
}
ERASMIAN_LETTERS = {
    "Α": "ˈɑlfɑ", "Β": "ˈbItɑ", "Γ": "ˈgɑmɑ", "Δ": "ˈdɛltɑ",
    "Ε": "ˈɛpsɪlɑn", "Ζ": "ˈzItɑ", "Η": "ˈItɑ",
}
MODERN_LETTERS = {"Α": "άλφα", "Β": "βήτα", "Γ": "γάμμα", "Δ": "δέλτα", "Ε": "έψιλον", "Ζ": "ζήτα", "Η": "ήτα"}


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


def modern(text: str) -> str:
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
    return ud.normalize("NFC", "".join(output)).replace("·", ",").replace("·", ",").replace("᾿", "’")
