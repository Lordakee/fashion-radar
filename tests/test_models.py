from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from fashion_radar.models.entity import AliasDefinition, EntityDefinition, EntityType
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


def test_alias_definition_defaults_requires_context_to_false() -> None:
    alias = AliasDefinition(value="boat shoes")

    assert alias.requires_context is False


def test_alias_definition_preserves_requires_context_true() -> None:
    alias = AliasDefinition(value="boat shoes", requires_context=True)

    assert alias.requires_context is True


def test_source_definition_defaults_to_enabled_and_weight_one() -> None:
    source = SourceDefinition(
        name="GDELT Fashion",
        type=SourceType.GDELT,
        query="fashion OR runway",
    )

    assert source.enabled is True
    assert source.weight == 1.0


def test_manual_import_source_type_exists() -> None:
    assert SourceType.MANUAL_IMPORT.value == "manual_import"


def test_manual_import_is_rejected_in_source_config() -> None:
    with pytest.raises(ValidationError, match="manual_import is import-only"):
        SourceDefinition(name="Manual Export", type=SourceType.MANUAL_IMPORT)
