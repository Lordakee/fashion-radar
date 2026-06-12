from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceType(StrEnum):
    RSS = "rss"
    RSSHUB = "rsshub"
    GDELT = "gdelt"
    MANUAL_IMPORT = "manual_import"


class HttpSourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_agent: str = "FashionRadar/0.1 (local-first fashion intelligence; contact: configurable)"
    timeout_seconds: float = Field(default=10.0, gt=0)
    per_domain_delay_seconds: float = Field(default=1.0, ge=0)
    max_retries: int = Field(default=2, ge=0)
    backoff_base_seconds: float = Field(default=0.5, gt=0)

    @field_validator("user_agent")
    @classmethod
    def require_user_agent(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("http.user_agent cannot be empty")
        return value.strip()


class ArticleSourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    respect_robots_txt: bool = True
    max_summary_chars: int = Field(default=500, gt=0)
    paywalled_domains: list[str] = Field(default_factory=list)

    @field_validator("paywalled_domains")
    @classmethod
    def normalize_paywalled_domains(cls, value: list[str]) -> list[str]:
        return sorted({domain.strip().lower() for domain in value if domain.strip()})


class GdeltSourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rate_limit_per_second: float = Field(default=1.0, gt=0, le=1.0)
    lookback_hours: int = Field(default=24, gt=0)
    max_records: int = Field(default=100, gt=0, le=250)


class SourceHealthSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_failures: int = Field(default=3, gt=0)
    retention_hours: int = Field(default=24, gt=0)


class SourceDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: SourceType
    url: str | None = None
    query: str | None = None
    enabled: bool = True
    weight: float = Field(default=1.0, gt=0, le=5)
    tags: list[str] = Field(default_factory=list)
    http: HttpSourceSettings = Field(default_factory=HttpSourceSettings)
    article: ArticleSourceSettings = Field(default_factory=ArticleSourceSettings)
    gdelt: GdeltSourceSettings = Field(default_factory=GdeltSourceSettings)
    health: SourceHealthSettings = Field(default_factory=SourceHealthSettings)

    @field_validator("name")
    @classmethod
    def require_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source name cannot be empty")
        return value.strip()

    @model_validator(mode="after")
    def validate_source_target(self) -> SourceDefinition:
        if self.type == SourceType.MANUAL_IMPORT:
            raise ValueError("manual_import is import-only; use fashion-radar import-signals")
        if self.type in {SourceType.RSS, SourceType.RSSHUB} and not self.url:
            raise ValueError(f"{self.type.value} source requires url")
        if self.type == SourceType.GDELT and not self.query:
            raise ValueError("gdelt source requires query")
        return self
