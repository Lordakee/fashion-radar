from pathlib import Path

from fashion_radar.extract.entities import evaluate_entity_matches, match_entities
from fashion_radar.extract.text import normalize_alias_key
from fashion_radar.importers.manual_signals import load_manual_signal_rows
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.settings import UNSAFE_COMMON_ALIASES, load_entity_config

PACK_PATH = Path("configs/entity-packs/fashion-watchlist.example.yaml")
DOC_PATH = Path("docs/entity-packs.md")
WATCHLIST_SIGNAL_PATH = Path("examples/community-signals.watchlist.example.csv")


def _entities() -> list[EntityDefinition]:
    return load_entity_config(PACK_PATH).entities


def _entities_by_name() -> dict[str, EntityDefinition]:
    return {entity.name: entity for entity in _entities()}


def test_fashion_watchlist_entity_pack_loads() -> None:
    config = load_entity_config(PACK_PATH)

    assert config.version == 1
    assert len(config.entities) >= 24


def test_fashion_watchlist_entity_pack_has_expected_type_mix() -> None:
    config = load_entity_config(PACK_PATH)
    type_counts = {
        entity_type: sum(1 for entity in config.entities if entity.type == entity_type)
        for entity_type in EntityType
    }

    assert type_counts[EntityType.BRAND] >= 8
    assert type_counts[EntityType.PRODUCT] >= 6
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


def test_fashion_watchlist_matcher_accepts_parent_brand_or_fashion_context() -> None:
    entities = _entities()

    accepted_names = {
        decision.entity_name
        for decision in match_entities(
            "The Row Margaux tote, Miu Miu Arcadie bag, Coach Tabby handbag, "
            "Mary Jane flats, and boat shoes appeared in the runway footwear report.",
            entities,
        )
    }

    assert {
        "The Row Margaux",
        "Miu Miu Arcadie",
        "Coach",
        "Mary Jane Shoes",
        "Boat Shoes",
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
