from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from fashion_radar.utils.dates import parse_datetime_utc


class ReportMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: datetime
    report_date: datetime
    item_count: int = 0

    @field_validator("generated_at", "report_date", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)
