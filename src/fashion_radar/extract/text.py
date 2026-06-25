from __future__ import annotations

import re
import unicodedata
from re import Pattern

_WHITESPACE_RE = re.compile(r"\s+")
_DIACRITIC_CLASS_BY_ASCII = {
    "a": "aàáâãäåāăąǎǟǡǻȁȃạảấầẩẫậắằẳẵặ",
    "c": "cçćĉċč",
    "e": "eèéêëēĕėęěȅȇẹẻẽếềểễệ",
    "i": "iìíîïĩīĭįıǐȉȋịỉ",
    "n": "nñńņň",
    "o": "oòóôõöøōŏőǒȍȏơọỏốồổỗộớờởỡợ",
    "u": "uùúûüũūŭůűųǔȕȗưụủứừửữự",
    "y": "yýÿŷȳỳỵỷỹ",
}
_ASCII_FOLD_OVERRIDES = {"ø": "o", "Ø": "O", "ı": "i"}


def normalize_text(value: str) -> str:
    """Normalize text for deterministic config and matching checks."""
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.replace("’", "'").replace("‘", "'")
    normalized = normalized.replace("“", '"').replace("”", '"')
    normalized = normalized.replace("–", "-").replace("—", "-")
    normalized = _fold_diacritics(normalized)
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip().lower()


def _fold_diacritics(value: str) -> str:
    folded: list[str] = []
    for char in unicodedata.normalize("NFD", value):
        if unicodedata.combining(char):
            continue
        folded.append(_ASCII_FOLD_OVERRIDES.get(char, char))
    return "".join(folded)


def normalize_alias_key(value: str) -> str:
    """Normalize aliases more aggressively for duplicate detection."""
    normalized = normalize_text(value)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return _WHITESPACE_RE.sub(" ", normalized).strip()


def alias_pattern(alias: str) -> Pattern[str]:
    """Build a case-insensitive word-boundary pattern for a literal alias.

    Ambiguous aliases still need the Stage 2 context gate before they become
    accepted entity matches.
    """
    normalized = unicodedata.normalize("NFKC", alias.strip())
    normalized = normalized.replace("’", "'").replace("‘", "'")
    normalized = normalized.replace("“", '"').replace("”", '"')
    normalized = normalized.replace("–", "-").replace("—", "-")
    folded = _fold_diacritics(normalized).lower()
    escaped = r"\s+".join(
        "".join(_alias_char_pattern(char) for char in token)
        for token in _WHITESPACE_RE.split(folded)
        if token
    )
    return re.compile(rf"(?<!\w){escaped}(?!\w)", flags=re.IGNORECASE)


def _alias_char_pattern(char: str) -> str:
    chars = _DIACRITIC_CLASS_BY_ASCII.get(char)
    if chars:
        return f"[{re.escape(chars)}]"
    return re.escape(char)
