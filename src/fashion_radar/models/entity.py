from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from fashion_radar.utils.dates import parse_datetime_utc


class EntityType(StrEnum):
    BRAND = "brand"
    DESIGNER = "designer"
    CELEBRITY = "celebrity"
    PRODUCT = "product"
    CATEGORY = "category"
    TREND = "trend"


class AliasDefinition(BaseModel):
    value: str
    safe_single_word: bool = False
    reason: str | None = None

    @field_validator("value")
    @classmethod
    def require_value(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("alias value cannot be empty")
        return value.strip()


class EntityDefinition(BaseModel):
    name: str
    type: EntityType
    aliases: list[AliasDefinition]
    parent: str | None = None
    parent_brand: str | None = None
    tags: list[str] = Field(default_factory=list)
    category_tags: list[str] = Field(default_factory=list)
    context_terms: list[str] = Field(default_factory=list)
    initial_weight: float = Field(default=1.0, gt=0, le=5)
    match_confidence: float = Field(default=1.0, ge=0, le=1)
    active_from: Any | None = None
    active_until: Any | None = None

    @field_validator("name")
    @classmethod
    def require_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("entity name cannot be empty")
        return value.strip()

    @field_validator("aliases", mode="before")
    @classmethod
    def coerce_aliases(cls, value: list[str | dict[str, Any]]) -> list[dict[str, Any]]:
        return [{"value": item} if isinstance(item, str) else item for item in value]

    @field_validator("active_from", "active_until", mode="after")
    @classmethod
    def normalize_dates(cls, value: Any | None) -> Any | None:
        if value is None:
            return None
        return parse_datetime_utc(value)

    @model_validator(mode="after")
    def validate_active_window(self) -> EntityDefinition:
        if self.active_from and self.active_until and self.active_until < self.active_from:
            raise ValueError("active_until cannot be before active_from")
        return self
