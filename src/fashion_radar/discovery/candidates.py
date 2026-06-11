from __future__ import annotations

import re
from dataclasses import dataclass

from fashion_radar.extract.text import normalize_alias_key, normalize_text
from fashion_radar.settings import CandidateDiscoverySettings

FASHION_ANCHORS = {
    "bag",
    "handbag",
    "tote",
    "clutch",
    "shoe",
    "shoes",
    "sneaker",
    "sneakers",
    "boot",
    "boots",
    "loafer",
    "loafers",
    "flat",
    "flats",
    "heel",
    "heels",
    "sandal",
    "sandals",
    "pump",
    "pumps",
    "mule",
    "mules",
}

GENERIC_STOP_KEYS = {
    "fashion",
    "fashion week",
    "spring collection",
    "fall collection",
    "summer collection",
    "winter collection",
    "new york",
    "london",
    "milan",
    "paris",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}

_BOUNDARY_WORDS = {
    "and",
    "as",
    "at",
    "by",
    "during",
    "for",
    "from",
    "in",
    "of",
    "on",
    "reports",
    "the",
    "to",
    "with",
}
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*|&")
_POSSESSIVE_RE = re.compile(r"(?i)\b([a-z0-9]+)'s\b")


@dataclass(frozen=True)
class CandidatePhrase:
    phrase: str
    normalized_key: str
    candidate_type: str
    contexts: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Token:
    value: str
    normalized: str


def extract_candidate_phrases(
    text: str,
    *,
    source_name: str,
    known_keys: set[str] | None = None,
    settings: CandidateDiscoverySettings | None = None,
) -> list[CandidatePhrase]:
    """Extract deterministic candidate phrases from a title/summary string."""
    resolved_settings = settings or CandidateDiscoverySettings()
    known = {_candidate_key(key) for key in known_keys or set() if _candidate_key(key)}
    source_keys = _source_keys(source_name)
    tokens = _tokenize(text)
    candidates: list[CandidatePhrase] = []

    candidates.extend(_proper_name_candidates(tokens, resolved_settings))
    candidates.extend(_anchor_candidates(tokens, resolved_settings))
    candidates.extend(_single_token_candidates(tokens))

    by_key: dict[str, CandidatePhrase] = {}
    for candidate in candidates:
        if _should_reject_candidate(
            candidate,
            known_keys=known,
            source_keys=source_keys,
            settings=resolved_settings,
        ):
            continue
        by_key.setdefault(candidate.normalized_key, candidate)
    return list(by_key.values())


def _tokenize(text: str) -> list[_Token]:
    normalized = normalize_text(text)
    return [
        _Token(value=match.group(0), normalized=normalize_alias_key(match.group(0)))
        for match in _TOKEN_RE.finditer(normalized if text.islower() else text)
        if normalize_alias_key(match.group(0))
    ]


def _proper_name_candidates(
    tokens: list[_Token], settings: CandidateDiscoverySettings
) -> list[CandidatePhrase]:
    candidates: list[CandidatePhrase] = []
    index = 0
    while index < len(tokens):
        if not _is_title_token(tokens[index]):
            index += 1
            continue
        start = index
        index += 1
        while index < len(tokens) and (
            _is_title_token(tokens[index])
            or (
                tokens[index].value == "&"
                and index + 1 < len(tokens)
                and _is_title_token(tokens[index + 1])
            )
        ):
            index += 1
        span = tokens[start:index]
        title_tokens = [token for token in span if token.value != "&"]
        if len(title_tokens) < 2:
            continue
        for offset in range(0, len(span) - 1):
            pair = span[offset : offset + 2]
            if all(token.value != "&" and _is_title_token(token) for token in pair):
                candidates.append(
                    _candidate_from_tokens(pair, "brand_or_designer", "proper_name_span")
                )
        if 2 <= len(span) <= settings.max_phrase_words:
            candidates.append(_candidate_from_tokens(span, "brand_or_designer", "proper_name_span"))
    return candidates


def _anchor_candidates(
    tokens: list[_Token], settings: CandidateDiscoverySettings
) -> list[CandidatePhrase]:
    candidates: list[CandidatePhrase] = []
    for index, token in enumerate(tokens):
        anchor = token.normalized
        if anchor not in FASHION_ANCHORS:
            continue
        modifiers = _anchor_modifiers(tokens, index, settings)
        if not modifiers:
            continue
        if len(modifiers) >= 4 and all(_is_title_token(item) for item in modifiers[:4]):
            modifiers = modifiers[-2:]
        phrase_tokens = [*modifiers, token]
        candidates.append(
            _candidate_from_tokens(
                phrase_tokens,
                _candidate_type_for_anchor(anchor),
                "fashion_anchor",
            )
        )
    return candidates


def _anchor_modifiers(
    tokens: list[_Token], anchor_index: int, settings: CandidateDiscoverySettings
) -> list[_Token]:
    modifiers: list[_Token] = []
    cursor = anchor_index - 1
    while cursor >= 0 and len(modifiers) < settings.max_phrase_words - 1:
        token = tokens[cursor]
        if token.value == "&" or token.normalized in _BOUNDARY_WORDS:
            break
        if not (_is_title_token(token) or token.normalized.isdigit()):
            break
        modifiers.append(token)
        cursor -= 1
    return list(reversed(modifiers))


def _single_token_candidates(tokens: list[_Token]) -> list[CandidatePhrase]:
    candidates: list[CandidatePhrase] = []
    for token in tokens:
        if not _is_title_token(token):
            continue
        if token.normalized in FASHION_ANCHORS or token.normalized in _BOUNDARY_WORDS:
            continue
        candidates.append(_candidate_from_tokens([token], "unknown", "single_token"))
    return candidates


def _candidate_from_tokens(
    tokens: list[_Token], candidate_type: str, context: str
) -> CandidatePhrase:
    phrase = " ".join(token.value for token in tokens if token.value != "&")
    normalized_key = _candidate_key(phrase)
    return CandidatePhrase(
        phrase=phrase,
        normalized_key=normalized_key,
        candidate_type=candidate_type,
        contexts=(context,),
    )


def _candidate_type_for_anchor(anchor: str) -> str:
    if anchor in {"bag", "handbag", "tote", "clutch"}:
        return "bag"
    if anchor in {
        "shoe",
        "shoes",
        "sneaker",
        "sneakers",
        "boot",
        "boots",
        "loafer",
        "loafers",
        "flat",
        "flats",
        "heel",
        "heels",
        "sandal",
        "sandals",
        "pump",
        "pumps",
        "mule",
        "mules",
    }:
        return "shoe"
    return "product"


def _should_reject_candidate(
    candidate: CandidatePhrase,
    *,
    known_keys: set[str],
    source_keys: set[str],
    settings: CandidateDiscoverySettings,
) -> bool:
    key = candidate.normalized_key
    if not key or len(key) <= 1 or len(candidate.phrase) > settings.max_phrase_chars:
        return True
    if len(key.split()) > settings.max_phrase_words:
        return True
    if key in GENERIC_STOP_KEYS or key in known_keys or key in source_keys:
        return True
    if any(_contains_token_span(key, source_key) for source_key in source_keys):
        return True
    return any(_contains_token_span(key, known_key) for known_key in known_keys)


def _contains_token_span(candidate_key: str, known_key: str) -> bool:
    candidate_tokens = candidate_key.split()
    known_tokens = known_key.split()
    if not known_tokens or len(known_tokens) > len(candidate_tokens):
        return False
    for start in range(0, len(candidate_tokens) - len(known_tokens) + 1):
        if candidate_tokens[start : start + len(known_tokens)] == known_tokens:
            return True
    return False


def _source_keys(source_name: str) -> set[str]:
    key = _candidate_key(source_name)
    keys = {key} if key else set()
    keys.update(part for part in key.split() if len(part) > 1)
    return keys


def _candidate_key(value: str) -> str:
    without_possessive = _POSSESSIVE_RE.sub(r"\1", value)
    return normalize_alias_key(without_possessive)


def _is_title_token(token: _Token) -> bool:
    if token.value == "&":
        return False
    parts = [part for part in re.split(r"[-']", token.value) if part]
    return bool(parts) and all(part[:1].isupper() for part in parts)
