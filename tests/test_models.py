from datetime import UTC, datetime

from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.source import SourceDefinition, SourceType


def test_collected_item_requires_utc_published_at() -> None:
    item = CollectedItem(
        source_name="Vogue",
        source_type=SourceType.RSS,
        url="https://example.com/article",
        title="The Row launches a new bag",
        published_at=datetime(2026, 6, 11, 10, 0, tzinfo=UTC),
    )

    assert item.published_at.tzinfo == UTC


def test_entity_definition_has_type_aliases_and_confidence_defaults() -> None:
    entity = EntityDefinition(
        name="The Row Margaux",
        type=EntityType.PRODUCT,
        aliases=["The Row Margaux", "Margaux bag"],
        parent="The Row",
    )

    assert entity.type == EntityType.PRODUCT
    assert entity.match_confidence == 1.0


def test_source_definition_defaults_to_enabled_and_weight_one() -> None:
    source = SourceDefinition(
        name="GDELT Fashion",
        type=SourceType.GDELT,
        query="fashion OR runway",
    )

    assert source.enabled is True
    assert source.weight == 1.0
