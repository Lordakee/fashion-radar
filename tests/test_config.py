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
            http:
              timeout_seconds: 12
              per_domain_delay_seconds: 0.5
            article:
              enabled: true
              respect_robots_txt: true
              paywalled_domains: ["paywall.example"]
            health:
              max_failures: 2
              retention_hours: 12
          - name: GDELT Fashion Query
            type: gdelt
            query: fashion OR runway
            enabled: true
            weight: 1.0
            gdelt:
              rate_limit_per_second: 1.0
              lookback_hours: 48
              max_records: 75
        """,
    )

    config = load_source_config(path)

    assert config.version == 1
    assert [source.name for source in config.sources] == ["Vogue Runway", "GDELT Fashion Query"]
    assert config.sources[0].http.timeout_seconds == 12
    assert config.sources[0].http.per_domain_delay_seconds == 0.5
    assert config.sources[0].article.respect_robots_txt is True
    assert config.sources[0].article.paywalled_domains == ["paywall.example"]
    assert config.sources[0].health.max_failures == 2
    assert config.sources[0].health.retention_hours == 12
    assert config.sources[1].gdelt.rate_limit_per_second == 1.0
    assert config.sources[1].gdelt.lookback_hours == 48
    assert config.sources[1].gdelt.max_records == 75


def test_source_config_supplies_stage_3_defaults(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: GDELT Fashion Query
            type: gdelt
            query: fashion OR runway
        """,
    )

    config = load_source_config(path)
    source = config.sources[0]

    assert "FashionRadar/0.1" in source.http.user_agent
    assert source.http.timeout_seconds == 10.0
    assert source.http.per_domain_delay_seconds == 1.0
    assert source.http.max_retries == 2
    assert source.gdelt.lookback_hours == 24
    assert source.gdelt.max_records == 100
    assert source.article.enabled is True
    assert source.article.max_summary_chars == 500
    assert source.health.max_failures == 3
    assert source.health.retention_hours == 24


def test_source_config_rejects_skip_on_robots_failure_dead_switch(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "sources.yaml",
        """
        version: 1
        sources:
          - name: Vogue Runway
            type: rss
            url: https://www.vogue.com/fashion-shows/rss
            article:
              skip_on_robots_failure: false
        """,
    )

    with pytest.raises(ConfigError, match="Extra inputs are not permitted"):
        load_source_config(path)


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


def test_duplicate_entity_names_are_rejected(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: The Row
            type: brand
            aliases: ["The Row"]
            context_terms: ["margaux"]
          - name: the row
            type: brand
            aliases: ["The Row official"]
        """,
    )

    with pytest.raises(ConfigError, match="Duplicate entity name"):
        load_entity_config(path)


def test_parent_brand_must_reference_existing_brand(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Margaux
            type: product
            parent_brand: The Row
            aliases: ["Margaux"]
            context_terms: ["handbag"]
        """,
    )

    with pytest.raises(ConfigError, match="Unknown parent_brand"):
        load_entity_config(path)


def test_parent_must_reference_existing_entity(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "entities.yaml",
        """
        version: 1
        entities:
          - name: Margaux
            type: product
            parent: The Row
            aliases: ["Margaux"]
            context_terms: ["handbag"]
        """,
    )

    with pytest.raises(ConfigError, match="Unknown parent"):
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
          current_window_days: 7
          baseline_window_days: 30
          weighted_mentions_7d: 1.0
          growth_bonus: 2.0
          source_diversity_bonus: 0.75
          high_weight_source_bonus: 1.5
          high_weight_source_threshold: 1.2
          new_entity_days: 14
          new_min_mentions: 1
          rising_growth_ratio: 1.5
          rising_min_mentions: 2
          cooling_growth_ratio: 0.75
          cooling_min_baseline_mentions: 2
          hot_score_threshold: 5.0
          hot_min_distinct_sources: 2
          stable_min_mentions: 1
          min_match_confidence: 0.5
        """,
    )

    config = load_scoring_config(path)

    assert config.scoring.current_window_days == 7
    assert config.scoring.baseline_window_days == 30
    assert config.scoring.growth_bonus == 2.0
    assert config.scoring.high_weight_source_threshold == 1.2
    assert config.scoring.rising_growth_ratio == 1.5
    assert config.scoring.cooling_growth_ratio == 0.75
    assert config.scoring.hot_score_threshold == 5.0
    assert config.scoring.min_match_confidence == 0.5
    assert config.scoring.new_entity_days == 14


def test_scoring_config_rejects_invalid_thresholds(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "scoring.yaml",
        """
        version: 1
        scoring:
          current_window_days: 0
          baseline_window_days: 30
          rising_growth_ratio: 1.0
          min_match_confidence: 1.5
        """,
    )

    with pytest.raises(ConfigError, match="Invalid scoring config"):
        load_scoring_config(path)


def test_sample_configs_load_without_network() -> None:
    config_dir = Path("configs")

    source_config = load_source_config(config_dir / "sources.example.yaml")
    entity_config = load_entity_config(config_dir / "entities.example.yaml")
    scoring_config = load_scoring_config(config_dir / "scoring.example.yaml")

    assert source_config.sources
    assert entity_config.entities
    assert scoring_config.scoring.new_entity_days > 0
