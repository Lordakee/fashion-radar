from pathlib import Path

from fashion_radar.extract.entities import evaluate_entity_matches, match_entities
from fashion_radar.extract.text import normalize_alias_key
from fashion_radar.importers.manual_signals import load_manual_signal_rows
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.settings import UNSAFE_COMMON_ALIASES, load_entity_config

PACK_PATH = Path("configs/entity-packs/fashion-watchlist.example.yaml")
BUYER_BRANDS_PACK_PATH = Path("configs/entity-packs/buyer-brands.example.yaml")
DOC_PATH = Path("docs/entity-packs.md")
WATCHLIST_SIGNAL_PATH = Path("examples/community-signals.watchlist.example.csv")


def _entities() -> list[EntityDefinition]:
    return load_entity_config(PACK_PATH).entities


def _entities_by_name() -> dict[str, EntityDefinition]:
    return {entity.name: entity for entity in _entities()}


def _buyer_brand_entities() -> list[EntityDefinition]:
    return load_entity_config(BUYER_BRANDS_PACK_PATH).entities


def _buyer_brand_entities_by_name() -> dict[str, EntityDefinition]:
    return {entity.name: entity for entity in _buyer_brand_entities()}


def test_fashion_watchlist_entity_pack_loads() -> None:
    config = load_entity_config(PACK_PATH)

    assert config.version == 1
    assert len(config.entities) >= 32


def test_buyer_brands_entity_pack_loads_with_expected_examples() -> None:
    config = load_entity_config(BUYER_BRANDS_PACK_PATH)
    entities = {entity.name: entity for entity in config.entities}

    assert config.version == 1
    assert len(config.entities) >= 29
    for name in [
        "Lemaire",
        "Khaite",
        "Toteme",
        "The Row",
        "Savette",
        "Aeyde",
        "Shushu Tong",
        "Uma Wang",
        "Quiet Luxury",
        "Boho Revival",
    ]:
        assert name in entities


def test_buyer_brands_entity_pack_has_expected_type_mix_and_tags() -> None:
    entities = _buyer_brand_entities()
    type_counts = {
        entity_type: sum(1 for entity in entities if entity.type == entity_type)
        for entity_type in EntityType
    }

    assert type_counts[EntityType.BRAND] >= 24
    assert type_counts[EntityType.TREND] >= 3
    assert any("chinese_designer" in entity.tags for entity in entities)
    assert any("buyer_brand" in entity.tags for entity in entities)


def test_buyer_brands_context_aliases_require_context() -> None:
    entities = _buyer_brand_entities_by_name()
    expected_aliases = {
        "Ami Paris": {"Ami Paris"},
        "Our Legacy": {"Our Legacy"},
        "Acne Studios": {"Acne Studios"},
        "Sandy Liang": {"Sandy Liang"},
        "Hui": {"Hui Shan", "Hui by Zhao Huizhou"},
    }

    for entity_name, alias_values in expected_aliases.items():
        entity = entities[entity_name]
        gated_aliases = {alias.value for alias in entity.aliases if alias.requires_context}
        assert alias_values <= gated_aliases


def test_buyer_brands_matcher_rejects_contextless_common_aliases() -> None:
    entities = _buyer_brand_entities()

    generic_texts = [
        ("Ami joined the dinner.", "Ami Paris"),
        ("Acne is a common skin condition.", "Acne Studios"),
        ("Joseph joined the meeting.", "Joseph"),
        ("The row of seats was empty.", "The Row"),
        ("Hui Shan was mentioned at dinner.", "Hui"),
    ]
    for text, entity_name in generic_texts:
        decisions = [
            decision
            for decision in evaluate_entity_matches(text, entities)
            if decision.entity_name == entity_name
        ]
        assert decisions, f"Expected evaluated decisions for {entity_name!r}"
        assert all(not decision.accepted for decision in decisions)


def test_fashion_watchlist_entity_pack_has_expected_type_mix() -> None:
    config = load_entity_config(PACK_PATH)
    type_counts = {
        entity_type: sum(1 for entity in config.entities if entity.type == entity_type)
        for entity_type in EntityType
    }

    assert type_counts[EntityType.BRAND] >= 12
    assert type_counts[EntityType.PRODUCT] >= 8
    assert type_counts[EntityType.CATEGORY] >= 4
    assert type_counts[EntityType.DESIGNER] >= 2
    assert type_counts[EntityType.CELEBRITY] >= 2
    assert type_counts[EntityType.TREND] >= 3


def test_fashion_watchlist_entity_pack_includes_requested_watchlist_examples() -> None:
    entities = _entities_by_name()

    for name in [
        "The Row",
        "Khaite",
        "Alaia",
        "Loewe",
        "Alaia Le Teckel",
        "Miu Miu Arcadie",
        "Mary Jane Shoes",
        "East-West Bags",
        "Savette",
        "Aeyde",
        "Savette Symmetry Bag",
        "Aeyde Uma Mary Jane",
    ]:
        assert name in entities


def test_fashion_watchlist_products_reference_existing_parent_brands() -> None:
    config = load_entity_config(PACK_PATH)
    brand_names = {entity.name for entity in config.entities if entity.type == EntityType.BRAND}

    for entity in config.entities:
        if entity.type == EntityType.PRODUCT:
            assert entity.parent_brand in brand_names


def test_fashion_watchlist_high_risk_aliases_use_existing_guardrails_or_narrow_phrases() -> None:
    entities = _entities_by_name()

    assert entities["Coach"].context_terms
    assert entities["Ballet Flats"].context_terms
    assert {alias.value for alias in entities["Mary Jane Shoes"].aliases} == {
        "Mary Jane shoes",
        "Mary Janes",
        "Mary Jane flats",
    }
    assert {alias.value for alias in entities["Boat Shoes"].aliases} == {
        "boat shoes",
        "boat shoe",
    }


def test_fashion_watchlist_explicit_context_aliases_require_context() -> None:
    entities = _entities_by_name()
    expected_aliases = {
        "Mary Jane Shoes": {"Mary Jane shoes", "Mary Janes", "Mary Jane flats"},
        "East-West Bags": {"east-west bag", "east-west bags", "east west tote"},
        "Boat Shoes": {"boat shoes", "boat shoe"},
        "Suede Sneakers": {"suede sneakers", "suede sneaker"},
    }

    for entity_name, alias_values in expected_aliases.items():
        entity = entities[entity_name]
        gated_aliases = {alias.value for alias in entity.aliases if alias.requires_context}
        assert alias_values <= gated_aliases


def test_fashion_watchlist_all_single_word_and_common_aliases_are_guarded() -> None:
    for entity in _entities():
        for alias in entity.aliases:
            key = normalize_alias_key(alias.value)
            if len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES:
                assert alias.safe_single_word or entity.context_terms, (
                    f"{entity.name!r} alias {alias.value!r} needs context or safe reason"
                )
                if alias.safe_single_word:
                    assert alias.reason


def test_fashion_watchlist_matcher_rejects_generic_broad_alias_mentions() -> None:
    entities = _entities()

    generic_texts = [
        ("The row after the show was empty.", "The Row"),
        ("The coach gave a speech after practice.", "Coach"),
        ("Margaux joined the dinner list.", "The Row Margaux"),
        ("Arcadie appeared in the novel title.", "Miu Miu Arcadie"),
    ]
    for text, entity_name in generic_texts:
        decisions = [
            decision
            for decision in evaluate_entity_matches(text, entities)
            if decision.entity_name == entity_name
        ]
        assert decisions, f"Expected an evaluated decision for {entity_name!r}"
        assert all(not decision.accepted for decision in decisions)


def test_fashion_watchlist_context_gates_broad_category_aliases() -> None:
    entities = _entities()

    generic_texts = [
        ("Mary Janes joined the dinner list.", "Mary Jane Shoes"),
        ("Mary Jane shoes were noted.", "Mary Jane Shoes"),
        ("Mary Jane flats were noted.", "Mary Jane Shoes"),
        ("Boat shoes were required on the dock.", "Boat Shoes"),
        ("The east-west bag sat in storage.", "East-West Bags"),
        ("The east west tote sat in storage.", "East-West Bags"),
        ("Suede sneakers appeared in a court filing.", "Suede Sneakers"),
    ]
    for text, entity_name in generic_texts:
        decisions = [
            decision
            for decision in evaluate_entity_matches(text, entities)
            if decision.entity_name == entity_name
        ]
        assert decisions, f"Expected evaluated decisions for {entity_name!r}"
        assert all(not decision.accepted for decision in decisions)
        assert {decision.reason for decision in decisions} == {"missing_context"}


def test_fashion_watchlist_matcher_does_not_register_bare_new_product_shorthands() -> None:
    entities = _entities()

    for text, entity_name in [
        ("The symmetry of the geometry was noted.", "Savette Symmetry Bag"),
        ("Uma joined the dinner list.", "Aeyde Uma Mary Jane"),
    ]:
        decisions = [
            decision
            for decision in evaluate_entity_matches(text, entities)
            if decision.entity_name == entity_name
        ]
        assert decisions == []


def test_fashion_watchlist_matcher_accepts_parent_brand_or_fashion_context() -> None:
    entities = _entities()

    accepted_names = {
        decision.entity_name
        for decision in match_entities(
            "The Row Margaux tote, Miu Miu Arcadie bag, Coach Tabby handbag, "
            "Mary Jane flats, boat shoes, Savette Symmetry Bag, and "
            "Aeyde Uma Mary Jane shoe appeared in the runway footwear report.",
            entities,
        )
    }

    assert {
        "The Row Margaux",
        "Miu Miu Arcadie",
        "Coach",
        "Mary Jane Shoes",
        "Boat Shoes",
        "Savette Symmetry Bag",
        "Aeyde Uma Mary Jane",
    } <= accepted_names


def test_fashion_watchlist_sample_matches_expected_entities_and_types() -> None:
    entities = _entities()
    rows = load_manual_signal_rows(
        WATCHLIST_SIGNAL_PATH,
        input_format="csv",
        default_source_name="Community Watchlist Sample",
    )
    text = " ".join(f"{row.title} {row.summary}" for row in rows)

    accepted = match_entities(text, entities)
    matched_names = {decision.entity_name for decision in accepted}
    matched_types = {decision.entity_type for decision in accepted}

    assert {
        "Khaite",
        "Khaite Lotus Bag",
        "Loewe",
        "Loewe Puzzle Bag",
        "Jonathan Anderson",
        "Bella Hadid",
        "Alaia Le Teckel",
        "Miu Miu Arcadie",
        "Mary Jane Shoes",
        "Tory Burch",
        "Tory Burch Pierced Mule",
        "East-West Bags",
        "Office Siren",
        "Boho Revival",
        "Savette",
        "Savette Symmetry Bag",
        "Aeyde",
        "Aeyde Uma Mary Jane",
    } <= matched_names
    assert {"brand", "product", "designer", "celebrity", "category", "trend"} <= matched_types


def test_default_packaged_entity_config_stays_small_and_loadable() -> None:
    root_config = load_entity_config(Path("configs/entities.example.yaml"))
    packaged_config = load_entity_config(
        Path("src/fashion_radar/templates/configs/entities.example.yaml")
    )
    expected_names = [
        "The Row",
        "Miu Miu",
        "Jonathan Anderson",
        "Zendaya",
        "The Row Margaux",
        "Ballet Flats",
        "Quiet Luxury",
    ]

    assert root_config.model_dump(mode="json") == packaged_config.model_dump(mode="json")
    assert [entity.name for entity in root_config.entities] == expected_names


def test_entity_pack_docs_do_not_introduce_collect_workflow() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "fashion-radar collect" not in text
