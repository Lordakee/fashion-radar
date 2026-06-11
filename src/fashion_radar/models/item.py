from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from fashion_radar.models.source import SourceType
from fashion_radar.utils.dates import parse_datetime_utc


class CollectedItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_name: str
    source_type: SourceType
    url: str
    title: str
    published_at: datetime
    summary: str | None = None

    @field_validator("source_name", "url", "title")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field cannot be empty")
        return value.strip()

    @field_validator("published_at", mode="before")
    @classmethod
    def normalize_published_at(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)
