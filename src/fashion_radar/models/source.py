from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator


class SourceType(StrEnum):
    RSS = "rss"
    RSSHUB = "rsshub"
    GDELT = "gdelt"


class GdeltSourceSettings(BaseModel):
    rate_limit_per_second: float = Field(default=1.0, gt=0, le=1.0)


class SourceDefinition(BaseModel):
    name: str
    type: SourceType
    url: str | None = None
    query: str | None = None
    enabled: bool = True
    weight: float = Field(default=1.0, gt=0, le=5)
    tags: list[str] = Field(default_factory=list)
    gdelt: GdeltSourceSettings = Field(default_factory=GdeltSourceSettings)

    @field_validator("name")
    @classmethod
    def require_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source name cannot be empty")
        return value.strip()

    @model_validator(mode="after")
    def validate_source_target(self) -> SourceDefinition:
        if self.type in {SourceType.RSS, SourceType.RSSHUB} and not self.url:
            raise ValueError(f"{self.type.value} source requires url")
        if self.type == SourceType.GDELT and not self.query:
            raise ValueError("gdelt source requires query")
        return self
