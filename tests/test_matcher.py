from __future__ import annotations

import pytest

from fashion_radar.extract.entities import (
    EntityMatchDecision,
    evaluate_entity_matches,
    match_entities,
)
from fashion_radar.models.entity import EntityDefinition, EntityType


def _entity(
    name: str,
    entity_type: EntityType,
    aliases: list[str | dict[str, object]],
    *,
    context_terms: list[str] | None = None,
    parent_brand: str | None = None,
    match_confidence: float = 1.0,
) -> EntityDefinition:
    return EntityDefinition(
        name=name,
        type=entity_type,
        aliases=aliases,
        context_terms=context_terms or [],
        parent_brand=parent_brand,
        match_confidence=match_confidence,
    )


def _fashion_entities() -> list[EntityDefinition]:
    return [
        _entity(
            "The Row",
            EntityType.BRAND,
            ["The Row", "Row"],
            context_terms=["margaux", "handbag", "runway", "collection"],
        ),
        _entity(
            "The Row Margaux",
            EntityType.PRODUCT,
            ["Margaux"],
            context_terms=["handbag", "bag"],
            parent_brand="The Row",
            match_confidence=0.88,
        ),
        _entity("Miu Miu", EntityType.BRAND, ["Miu Miu"]),
        _entity("Coach", EntityType.BRAND, ["Coach"], context_terms=["bag", "handbag"]),
        _entity("Gap", EntityType.BRAND, ["Gap"], context_terms=["denim", "campaign"]),
        _entity("Boss", EntityType.BRAND, ["Boss"], context_terms=["suit", "runway"]),
        _entity("Pink", EntityType.BRAND, ["Pink"], context_terms=["lingerie", "collection"]),
        _entity(
            "Ballet Flats",
            EntityType.CATEGORY,
            ["ballet flats", "ballet flat"],
            context_terms=["shoes", "footwear"],
            match_confidence=0.7,
        ),
        _entity(
            "Zendaya",
            EntityType.CELEBRITY,
            [
                {
                    "value": "Zendaya",
                    "safe_single_word": True,
                    "reason": "globally distinctive public figure",
                }
            ],
            match_confidence=0.92,
        ),
        _entity(
            "Jonathan Anderson",
            EntityType.DESIGNER,
            ["Jonathan Anderson"],
            context_terms=["creative director", "designer"],
            match_confidence=0.85,
        ),
    ]


@pytest.mark.parametrize(
    ("text", "entity_name"),
    [
        ("front row seat", "The Row"),
        ("the row after the show", "The Row"),
        ("coach the team", "Coach"),
        ("mind the gap", "Gap"),
        ("boss said", "Boss"),
        ("pink room", "Pink"),
        ("ballet flats", "Ballet Flats"),
    ],
)
def test_common_language_alias_hits_are_rejected_without_context(
    text: str, entity_name: str
) -> None:
    decisions = [
        decision
        for decision in evaluate_entity_matches(text, _fashion_entities())
        if decision.entity_name == entity_name
    ]

    assert decisions
    assert all(isinstance(decision, EntityMatchDecision) for decision in decisions)
    assert all(not decision.accepted for decision in decisions)
    assert {decision.reason for decision in decisions} == {"missing_context"}
    assert entity_name not in {
        decision.entity_name for decision in match_entities(text, _fashion_entities())
    }


def test_parent_brand_and_product_context_accept_the_row_margaux() -> None:
    accepted = match_entities("The Row Margaux handbag", _fashion_entities())

    accepted_names = {decision.entity_name for decision in accepted}
    assert {"The Row", "The Row Margaux"} <= accepted_names

    product = next(decision for decision in accepted if decision.entity_name == "The Row Margaux")
    assert product.entity_type == EntityType.PRODUCT
    assert product.alias == "Margaux"
    assert product.reason == "parent_brand"
    assert product.confidence == 0.88


def test_parent_brand_alias_can_accept_product_without_product_context() -> None:
    accepted = match_entities("The Row Margaux edit", _fashion_entities())

    product = next(decision for decision in accepted if decision.entity_name == "The Row Margaux")
    assert product.reason == "parent_brand"
    assert product.context_terms == []


def test_product_alias_without_parent_brand_or_narrow_context_is_rejected() -> None:
    decisions = [
        decision
        for decision in evaluate_entity_matches("Margaux fashion trend", _fashion_entities())
        if decision.entity_name == "The Row Margaux"
    ]

    assert len(decisions) == 1
    assert not decisions[0].accepted
    assert decisions[0].reason == "missing_context"


def test_multi_word_brand_alias_is_accepted_without_context() -> None:
    accepted = match_entities("Miu Miu ballet flats", _fashion_entities())

    decision = next(decision for decision in accepted if decision.entity_name == "Miu Miu")
    assert decision.entity_type == EntityType.BRAND
    assert decision.reason == "accepted"


def test_safe_single_word_alias_is_accepted_with_stable_reason() -> None:
    accepted = match_entities("Zendaya red carpet", _fashion_entities())

    decision = next(decision for decision in accepted if decision.entity_name == "Zendaya")
    assert decision.entity_type == EntityType.CELEBRITY
    assert decision.reason == "safe_alias"
    assert decision.confidence == 0.92


def test_designer_alias_is_accepted_with_match_confidence() -> None:
    accepted = match_entities("Jonathan Anderson creative director", _fashion_entities())

    decision = next(
        decision for decision in accepted if decision.entity_name == "Jonathan Anderson"
    )
    assert decision.entity_type == EntityType.DESIGNER
    assert decision.reason == "accepted"
    assert decision.confidence == 0.85


def test_generic_category_alias_is_accepted_when_own_context_term_matches() -> None:
    accepted = match_entities("ballet flats shoes trend", _fashion_entities())

    decision = next(decision for decision in accepted if decision.entity_name == "Ballet Flats")
    assert decision.entity_type == EntityType.CATEGORY
    assert decision.reason == "context"
    assert decision.context_terms == ["shoes"]
    assert decision.confidence == 0.7


def test_context_terms_are_case_insensitive_word_boundary_matches() -> None:
    entities = [
        _entity("Acme", EntityType.BRAND, ["Acme"], context_terms=["boss"], match_confidence=0.42)
    ]

    rejected = evaluate_entity_matches("Acme bossy jacket", entities)
    assert len(rejected) == 1
    assert not rejected[0].accepted
    assert rejected[0].reason == "missing_context"

    accepted = match_entities("Acme BOSS jacket", entities)
    assert len(accepted) == 1
    assert accepted[0].reason == "context"
    assert accepted[0].context_terms == ["boss"]
    assert accepted[0].confidence == 0.42
