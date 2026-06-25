from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from fashion_radar.extract.text import normalize_alias_key
from fashion_radar.models.entity import EntityDefinition, EntityType
from fashion_radar.models.source import SourceDefinition

UNSAFE_COMMON_ALIASES = {
    "the row",
    "row",
    "ballet flat",
    "ballet flats",
    "gap",
    "coach",
    "boss",
    "guess",
    "pink",
    "sandy",
}

ConfigModel = TypeVar("ConfigModel", bound=BaseModel)


class ConfigError(ValueError):
    """Raised when a YAML config file cannot be loaded or validated."""


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal[1] = 1
    sources: list[SourceDefinition]


class EntityConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal[1] = 1
    entities: list[EntityDefinition]

    @model_validator(mode="after")
    def validate_aliases(self) -> EntityConfig:
        entity_names: dict[str, str] = {}
        seen: dict[str, str] = {}
        for entity in self.entities:
            entity_key = normalize_alias_key(entity.name)
            if entity_key in entity_names:
                raise ValueError(
                    f"Duplicate entity name {entity.name!r}; "
                    f"already defined as {entity_names[entity_key]!r}"
                )
            entity_names[entity_key] = entity.name

            entity_keys: set[str] = set()
            for alias in entity.aliases:
                key = normalize_alias_key(alias.value)
                if key in entity_keys:
                    raise ValueError(f"Duplicate alias {alias.value!r} in entity {entity.name!r}")
                entity_keys.add(key)
                if key in seen and seen[key] != entity.name:
                    raise ValueError(
                        f"Duplicate alias {alias.value!r} in entities "
                        f"{seen[key]!r} and {entity.name!r}"
                    )
                seen[key] = entity.name
                if alias.requires_context and not entity.context_terms:
                    raise ValueError(
                        f"Alias {alias.value!r} for entity {entity.name!r} "
                        "requires context but entity has no context_terms"
                    )

                is_single_or_common = len(key.split()) == 1 or key in UNSAFE_COMMON_ALIASES
                if is_single_or_common and not alias.safe_single_word and not entity.context_terms:
                    raise ValueError(
                        f"Unsafe common alias {alias.value!r} for entity {entity.name!r}; "
                        "add context_terms or mark the alias safe with a reason"
                    )

        brand_names = {
            normalize_alias_key(entity.name)
            for entity in self.entities
            if entity.type == EntityType.BRAND
        }
        all_entity_names = set(entity_names)
        for entity in self.entities:
            if entity.parent and normalize_alias_key(entity.parent) not in all_entity_names:
                raise ValueError(f"Unknown parent {entity.parent!r} for entity {entity.name!r}")
            if entity.parent_brand and normalize_alias_key(entity.parent_brand) not in brand_names:
                raise ValueError(
                    f"Unknown parent_brand {entity.parent_brand!r} for entity {entity.name!r}"
                )
        return self


class ScoringSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_window_days: int = Field(default=7, gt=0)
    baseline_window_days: int = Field(default=30, gt=0)
    weighted_mentions_7d: float = Field(default=1.0, ge=0)
    growth_bonus: float = Field(default=1.5, ge=0)
    source_diversity_bonus: float = Field(default=1.0, ge=0)
    high_weight_source_bonus: float = Field(default=0.5, ge=0)
    high_weight_source_threshold: float = Field(default=1.2, gt=0)
    new_entity_days: int = Field(default=14, gt=0)
    new_min_mentions: int = Field(default=1, ge=0)
    rising_growth_ratio: float = Field(default=1.5, gt=1)
    rising_min_mentions: int = Field(default=2, ge=0)
    cooling_growth_ratio: float = Field(default=0.75, ge=0, le=1)
    cooling_min_baseline_mentions: int = Field(default=2, ge=0)
    hot_score_threshold: float = Field(default=5.0, ge=0)
    hot_min_distinct_sources: int = Field(default=2, ge=0)
    stable_min_mentions: int = Field(default=1, ge=0)
    min_match_confidence: float = Field(default=0.5, ge=0, le=1)


class CandidateDiscoverySettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    max_candidates: int = Field(default=20, ge=0)
    representative_items_per_candidate: int = Field(default=3, ge=0)
    min_current_mentions: int = Field(default=2, ge=1)
    min_distinct_sources: int = Field(default=1, ge=1)
    rising_growth_ratio: float = Field(default=1.5, gt=1)
    review_min_current_mentions: int = Field(default=2, ge=1)
    review_min_distinct_sources: int = Field(default=1, ge=1)
    min_single_token_mentions: int = Field(default=2, ge=1)
    min_single_token_distinct_sources: int = Field(default=2, ge=1)
    max_phrase_words: int = Field(default=5, ge=2)
    max_phrase_chars: int = Field(default=80, ge=10)


class ScoringConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal[1] = 1
    scoring: ScoringSettings
    candidate_discovery: CandidateDiscoverySettings = Field(
        default_factory=CandidateDiscoverySettings
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        raise ConfigError(f"Could not read config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Config {path} must contain a YAML mapping")
    return data


def _wrap_validation(path: Path, config_name: str, factory: type[ConfigModel]) -> ConfigModel:
    data = _load_yaml(path)
    try:
        return factory.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"Invalid {config_name} config {path}: {exc}") from exc
    except ValueError as exc:
        raise ConfigError(f"Invalid {config_name} config {path}: {exc}") from exc


def load_source_config(path: Path) -> SourceConfig:
    data = _load_yaml(path)
    for source in data.get("sources", []):
        if isinstance(source, dict) and source.get("type") == "google_news_rss":
            raise ConfigError(
                "Google News RSS is not supported in v0.1.0; "
                "it may return later as a disabled experimental connector"
            )
    try:
        return SourceConfig.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"Invalid source config {path}: {exc}") from exc


def load_entity_config(path: Path) -> EntityConfig:
    return _wrap_validation(path, "entity", EntityConfig)


def load_scoring_config(path: Path) -> ScoringConfig:
    return _wrap_validation(path, "scoring", ScoringConfig)
