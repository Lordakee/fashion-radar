from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fashion_radar.extract.text import alias_pattern, normalize_alias_key
from fashion_radar.models.entity import AliasDefinition, EntityDefinition, EntityType
from fashion_radar.settings import UNSAFE_COMMON_ALIASES

REASON_ACCEPTED = "accepted"
REASON_CONTEXT = "context"
REASON_MISSING_CONTEXT = "missing_context"
REASON_PARENT_BRAND = "parent_brand"
REASON_SAFE_ALIAS = "safe_alias"


@dataclass(frozen=True, slots=True)
class EntityMatchDecision:
    entity_name: str
    entity_type: EntityType
    alias: str
    accepted: bool
    reason: str
    confidence: float
    context_terms: list[str]


def evaluate_entity_matches(
    text: str, entities: Sequence[EntityDefinition]
) -> list[EntityMatchDecision]:
    """Return accepted and rejected decisions for every alias that appears in text."""
    entity_list = list(entities)
    entities_by_name = {normalize_alias_key(entity.name): entity for entity in entity_list}

    decisions: list[EntityMatchDecision] = []
    for entity in entity_list:
        context_terms = _matched_context_terms(text, entity.context_terms)
        parent_brand_matched = _parent_brand_matched(text, entity, entities_by_name)

        for alias in entity.aliases:
            if not alias_pattern(alias.value).search(text):
                continue
            accepted, reason = _evaluate_alias(alias, entity, context_terms, parent_brand_matched)
            decisions.append(
                EntityMatchDecision(
                    entity_name=entity.name,
                    entity_type=entity.type,
                    alias=alias.value,
                    accepted=accepted,
                    reason=reason,
                    confidence=entity.match_confidence,
                    context_terms=list(context_terms),
                )
            )
    return decisions


def match_entities(text: str, entities: Sequence[EntityDefinition]) -> list[EntityMatchDecision]:
    """Return only accepted entity match decisions."""
    return [decision for decision in evaluate_entity_matches(text, entities) if decision.accepted]


def _evaluate_alias(
    alias: AliasDefinition,
    entity: EntityDefinition,
    context_terms: list[str],
    parent_brand_matched: bool,
) -> tuple[bool, str]:
    if entity.type == EntityType.PRODUCT and entity.parent_brand:
        if parent_brand_matched:
            return True, REASON_PARENT_BRAND
        if context_terms:
            return True, REASON_CONTEXT
        return False, REASON_MISSING_CONTEXT

    if alias.requires_context:
        if context_terms:
            return True, REASON_CONTEXT
        return False, REASON_MISSING_CONTEXT

    if not _requires_context(alias):
        return True, REASON_ACCEPTED
    if alias.safe_single_word and alias.reason:
        return True, REASON_SAFE_ALIAS
    if context_terms:
        return True, REASON_CONTEXT
    return False, REASON_MISSING_CONTEXT


def _requires_context(alias: AliasDefinition) -> bool:
    key = normalize_alias_key(alias.value)
    return len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES


def _matched_context_terms(text: str, context_terms: Sequence[str]) -> list[str]:
    matches: list[str] = []
    seen: set[str] = set()
    for term in context_terms:
        stripped = term.strip()
        if not stripped or not alias_pattern(stripped).search(text):
            continue
        key = normalize_alias_key(stripped)
        if key in seen:
            continue
        seen.add(key)
        matches.append(stripped)
    return matches


def _parent_brand_matched(
    text: str,
    entity: EntityDefinition,
    entities_by_name: dict[str, EntityDefinition],
) -> bool:
    if not entity.parent_brand:
        return False
    parent = entities_by_name.get(normalize_alias_key(entity.parent_brand))
    if parent is None:
        return False
    return any(alias_pattern(alias.value).search(text) for alias in parent.aliases)
