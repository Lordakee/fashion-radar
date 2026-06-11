from __future__ import annotations

import re
import unicodedata
from re import Pattern

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Normalize text for deterministic config and matching checks."""
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.replace("’", "'").replace("‘", "'")
    normalized = normalized.replace("“", '"').replace("”", '"')
    normalized = normalized.replace("–", "-").replace("—", "-")
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip().lower()


def normalize_alias_key(value: str) -> str:
    """Normalize aliases more aggressively for duplicate detection."""
    normalized = normalize_text(value)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return _WHITESPACE_RE.sub(" ", normalized).strip()


def alias_pattern(alias: str) -> Pattern[str]:
    """Build a word-boundary pattern for a literal alias."""
    escaped = re.escape(alias.strip())
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"(?<!\w){escaped}(?!\w)")
