from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.engine import Engine

from fashion_radar.db.schema import item_entities, items
from fashion_radar.extract.text import normalize_alias_key, normalize_text
from fashion_radar.models.report import RepresentativeItem
from fashion_radar.settings import CandidateDiscoverySettings, EntityConfig, ScoringSettings
from fashion_radar.utils.dates import parse_datetime_utc

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
    "le",
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
class CandidateMetric:
    phrase: str
    normalized_key: str
    candidate_type: str
    label: str
    score: float
    current_mentions: int
    baseline_mentions: int
    distinct_sources: int
    growth_ratio: float | None
    first_seen_at: datetime
    contexts: tuple[str, ...]
    representative_items: tuple[RepresentativeItem, ...]


@dataclass(frozen=True)
class _Token:
    value: str
    normalized: str


@dataclass(frozen=True)
class _CandidateMention:
    phrase: str
    normalized_key: str
    candidate_type: str
    contexts: tuple[str, ...]
    item_id: int
    source_name: str
    source_weight: float
    source_url: str
    published_at: datetime
    title: str
    summary: str | None
    collected_at: datetime


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


def configured_entity_keys(
    entity_config: EntityConfig | None,
    *,
    as_of: datetime | None = None,
) -> set[str]:
    keys: set[str] = set()
    if entity_config is None:
        return keys
    as_of_utc = parse_datetime_utc(as_of) if as_of is not None else None
    for entity in entity_config.entities:
        if as_of_utc is not None:
            active_from = parse_datetime_utc(entity.active_from) if entity.active_from else None
            active_until = parse_datetime_utc(entity.active_until) if entity.active_until else None
            if active_from is not None and active_from > as_of_utc:
                continue
            if active_until is not None and active_until < as_of_utc:
                continue
        entity_key = _candidate_key(entity.name)
        if entity_key:
            keys.add(entity_key)
        for alias in entity.aliases:
            alias_key = _candidate_key(alias.value)
            if alias_key:
                keys.add(alias_key)
    return keys


def discover_candidates(
    engine: Engine,
    *,
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
    entity_config: EntityConfig | None,
    as_of: datetime,
    limit: int | None = None,
) -> list[CandidateMetric]:
    if not settings.enabled:
        return []

    resolved_limit = (
        settings.max_candidates if limit is None else min(limit, settings.max_candidates)
    )
    if resolved_limit <= 0:
        return []

    as_of_utc = parse_datetime_utc(as_of)
    current_start = as_of_utc - timedelta(days=scoring.current_window_days)
    baseline_start = current_start - timedelta(days=scoring.baseline_window_days)
    known_keys = configured_entity_keys(entity_config, as_of=as_of_utc) | _stored_entity_keys(
        engine,
        min_match_confidence=scoring.min_match_confidence,
        as_of=as_of_utc,
    )
    mentions = _candidate_mentions(
        engine,
        known_keys=known_keys,
        settings=settings,
        baseline_start=baseline_start,
        as_of=as_of_utc,
    )

    by_key: dict[str, list[_CandidateMention]] = {}
    for mention in mentions:
        by_key.setdefault(mention.normalized_key, []).append(mention)

    metrics: list[CandidateMetric] = []
    for candidate_mentions in by_key.values():
        current_mentions = [
            mention
            for mention in candidate_mentions
            if current_start < mention.collected_at <= as_of_utc
        ]
        if not current_mentions:
            continue
        baseline_mentions = [
            mention
            for mention in candidate_mentions
            if baseline_start < mention.collected_at <= current_start
        ]
        metric = _score_candidate(
            current_mentions=current_mentions,
            baseline_mentions=baseline_mentions,
            scoring=scoring,
            settings=settings,
        )
        if metric is not None:
            metrics.append(metric)

    return sorted(
        metrics,
        key=lambda metric: (
            -metric.score,
            -metric.current_mentions,
            -metric.distinct_sources,
            metric.phrase.lower(),
        ),
    )[:resolved_limit]


def _stored_entity_keys(
    engine: Engine,
    *,
    min_match_confidence: float,
    as_of: datetime,
) -> set[str]:
    with engine.connect() as connection:
        rows = connection.execute(
            select(
                item_entities.c.entity_name,
                item_entities.c.alias,
                items.c.collected_at,
            )
            .select_from(item_entities.join(items, item_entities.c.item_id == items.c.id))
            .where(item_entities.c.confidence >= min_match_confidence)
        ).mappings()
        keys: set[str] = set()
        for row in rows:
            if parse_datetime_utc(row["collected_at"]) > as_of:
                continue
            for value in (row["entity_name"], row["alias"]):
                key = _candidate_key(value)
                if key:
                    keys.add(key)
        return keys


def _candidate_mentions(
    engine: Engine,
    *,
    known_keys: set[str],
    settings: CandidateDiscoverySettings,
    baseline_start: datetime,
    as_of: datetime,
) -> list[_CandidateMention]:
    with engine.connect() as connection:
        rows = list(
            connection.execute(
                select(
                    items.c.id,
                    items.c.source_name,
                    items.c.source_weight,
                    items.c.url,
                    items.c.published_at,
                    items.c.title,
                    items.c.summary,
                    items.c.collected_at,
                )
            ).mappings()
        )

    mentions: list[_CandidateMention] = []
    for row in rows:
        collected_at = parse_datetime_utc(row["collected_at"])
        if not (baseline_start < collected_at <= as_of):
            continue
        text = " ".join(value for value in (row["title"], row["summary"]) if isinstance(value, str))
        phrases = extract_candidate_phrases(
            text,
            source_name=row["source_name"],
            known_keys=known_keys,
            settings=settings,
        )
        by_key = _deduplicate_phrases(phrases)
        for phrase in by_key.values():
            mentions.append(
                _CandidateMention(
                    phrase=phrase.phrase,
                    normalized_key=phrase.normalized_key,
                    candidate_type=phrase.candidate_type,
                    contexts=phrase.contexts,
                    item_id=int(row["id"]),
                    source_name=row["source_name"],
                    source_weight=float(row["source_weight"] or 1.0),
                    source_url=row["url"],
                    published_at=parse_datetime_utc(row["published_at"]),
                    title=row["title"],
                    summary=row["summary"],
                    collected_at=collected_at,
                )
            )
    return mentions


def _deduplicate_phrases(phrases: list[CandidatePhrase]) -> dict[str, CandidatePhrase]:
    by_key: dict[str, CandidatePhrase] = {}
    for phrase in phrases:
        existing = by_key.get(phrase.normalized_key)
        if existing is None:
            by_key[phrase.normalized_key] = phrase
            continue
        by_key[phrase.normalized_key] = CandidatePhrase(
            phrase=existing.phrase,
            normalized_key=existing.normalized_key,
            candidate_type=existing.candidate_type,
            contexts=_merge_contexts(existing.contexts, phrase.contexts),
        )
    return by_key


def _score_candidate(
    *,
    current_mentions: list[_CandidateMention],
    baseline_mentions: list[_CandidateMention],
    scoring: ScoringSettings,
    settings: CandidateDiscoverySettings,
) -> CandidateMetric | None:
    current_count = len(current_mentions)
    distinct_sources = len({mention.source_name for mention in current_mentions})
    if current_count < settings.review_min_current_mentions:
        return None
    if distinct_sources < settings.review_min_distinct_sources:
        return None

    key = current_mentions[0].normalized_key
    if len(key.split()) == 1 and (
        current_count < settings.min_single_token_mentions
        or distinct_sources < settings.min_single_token_distinct_sources
    ):
        return None

    baseline_count = len(baseline_mentions)
    current_rate = current_count / scoring.current_window_days
    baseline_rate = baseline_count / scoring.baseline_window_days if baseline_count else 0
    growth_ratio = current_rate / baseline_rate if baseline_rate > 0 else None
    weighted_current_mentions = sum(mention.source_weight for mention in current_mentions)
    score = (
        weighted_current_mentions * scoring.weighted_mentions_7d
        + max(0, distinct_sources - 1) * scoring.source_diversity_bonus
        + (max(0.0, growth_ratio - 1) * scoring.growth_bonus if growth_ratio else 0.0)
    )
    ordered_current = sorted(
        current_mentions,
        key=lambda mention: (mention.collected_at, mention.item_id),
        reverse=True,
    )
    contexts = _merge_contexts(
        *(mention.contexts for mention in [*current_mentions, *baseline_mentions])
    )
    return CandidateMetric(
        phrase=ordered_current[0].phrase,
        normalized_key=key,
        candidate_type=ordered_current[0].candidate_type,
        label=_candidate_label(
            current_mentions=current_count,
            baseline_mentions=baseline_count,
            distinct_sources=distinct_sources,
            growth_ratio=growth_ratio,
            settings=settings,
        ),
        score=score,
        current_mentions=current_count,
        baseline_mentions=baseline_count,
        distinct_sources=distinct_sources,
        growth_ratio=growth_ratio,
        first_seen_at=min(
            mention.collected_at for mention in [*current_mentions, *baseline_mentions]
        ),
        contexts=contexts,
        representative_items=tuple(
            RepresentativeItem(
                source_name=mention.source_name,
                source_url=mention.source_url,
                published_at=mention.published_at,
                title=mention.title,
                summary=mention.summary,
            )
            for mention in ordered_current[: settings.representative_items_per_candidate]
        ),
    )


def _candidate_label(
    *,
    current_mentions: int,
    baseline_mentions: int,
    distinct_sources: int,
    growth_ratio: float | None,
    settings: CandidateDiscoverySettings,
) -> str:
    meets_label_mentions = current_mentions >= settings.min_current_mentions
    meets_label_sources = distinct_sources >= settings.min_distinct_sources
    if baseline_mentions == 0 and meets_label_mentions and meets_label_sources:
        return "new_candidate"
    if (
        baseline_mentions > 0
        and growth_ratio is not None
        and meets_label_mentions
        and meets_label_sources
        and growth_ratio >= settings.rising_growth_ratio
    ):
        return "rising_candidate"
    return "review"


def _merge_contexts(*context_groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    for contexts in context_groups:
        for context in contexts:
            if context not in ordered:
                ordered.append(context)
    return tuple(ordered)


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
        if len(span) == 2 and index < len(tokens) and tokens[index].normalized in FASHION_ANCHORS:
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
