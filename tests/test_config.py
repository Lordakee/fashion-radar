from pathlib import Path
from textwrap import dedent

import pytest

from fashion_radar.settings import (
    ConfigError,
    load_entity_config,
    load_scoring_config,
    load_source_config,
)


def write_yaml(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def test_loads_valid_source_config(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Vogue Runway
            type: rss
            url: https://www.vogue.com/fashion-shows/rss
            enabled: true
            weight: 1.4
            tags: [fashion_media, runway]
          - name: GDELT Fashion Query
            type: gdelt
            query: fashion OR runway
            enabled: true
            weight: 1.0
            gdelt:
              rate_limit_per_second: 1.0
        """,
    )

    config = load_source_config(path)

    assert config.version == 1
    assert [source.name for source in config.sources] == ["Vogue Runway", "GDELT Fashion Query"]
    assert config.sources[1].gdelt.rate_limit_per_second == 1.0


def test_google_news_source_is_rejected_for_v0_1(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Google News Fashion Query
            type: google_news_rss
            query: The Row Margaux
            enabled: true
        """,
    )

    with pytest.raises(ConfigError, match="Google News RSS is not supported in v0.1.0"):
        load_source_config(path)


def test_duplicate_aliases_are_rejected(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: The Row
            type: brand
            aliases: ["The Row", "TR"]
            context_terms: ["fashion", "brand"]
          - name: Totally Relevant
            type: brand
            aliases: ["tr"]
        """,
    )

    with pytest.raises(ConfigError, match="Duplicate alias"):
        load_entity_config(path)


def test_unsafe_common_alias_requires_context(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: The Row
            type: brand
            aliases: ["the row"]
        """,
    )

    with pytest.raises(ConfigError, match="Unsafe common alias"):
        load_entity_config(path)


def test_common_alias_with_context_is_allowed(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: The Row
            type: brand
            aliases: ["the row"]
            context_terms: ["fashion", "brand", "margaux"]
        """,
    )

    config = load_entity_config(path)

    assert config.entities[0].name == "The Row"
    assert config.entities[0].context_terms == ["fashion", "brand", "margaux"]


def test_loads_scoring_config(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "scoring.yaml",
        """
        version: 1
        scoring:
          weighted_mentions_7d: 1.0
          growth_bonus: 2.0
          source_diversity_bonus: 0.75
          high_weight_source_bonus: 1.5
          new_entity_days: 14
        """,
    )

    config = load_scoring_config(path)

    assert config.scoring.growth_bonus == 2.0
    assert config.scoring.new_entity_days == 14


def test_sample_configs_load_without_network() -> None:
    config_dir = Path("configs")

    source_config = load_source_config(config_dir / "sources.example.yaml")
    entity_config = load_entity_config(config_dir / "entities.example.yaml")
    scoring_config = load_scoring_config(config_dir / "scoring.example.yaml")

    assert source_config.sources
    assert entity_config.entities
    assert scoring_config.scoring.new_entity_days > 0
