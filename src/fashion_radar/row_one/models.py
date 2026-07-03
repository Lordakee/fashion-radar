from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from fashion_radar.utils.dates import parse_datetime_utc

RowOneSectionKey = Literal[
    "top_stories",
    "brand_moves",
    "celebrity_style",
    "hot_products",
    "rising_radar",
]
RowOneDisplayVariant = Literal["editorial", "portrait", "product", "signal"]
RowOneDisplayAccent = Literal["ink", "graphite", "steel", "cobalt", "rose"]


class LocalizedText(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zh: str
    en: str


class RowOneLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    url: str | None = None
    source_name: str


class RowOneSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: RowOneSectionKey
    title: LocalizedText
    dek: LocalizedText


class RowOneStoryImage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    src: str
    alt: LocalizedText
    credit: str | None = None
    source_url: str | None = None


class RowOneStoryDisplay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant: RowOneDisplayVariant
    accent: RowOneDisplayAccent
    image: RowOneStoryImage | None = None


class RowOneStory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    section_key: RowOneSectionKey
    headline: str
    summary: LocalizedText
    why_it_matters: LocalizedText
    editorial_takeaway: LocalizedText
    signal_context: LocalizedText
    reader_path: LocalizedText
    source_name: str
    source_url: str | None = None
    published_at: datetime | None = None
    detail_path: str
    tags: list[str] = Field(default_factory=list)
    evidence: list[RowOneLink] = Field(default_factory=list)
    display: RowOneStoryDisplay | None = None

    @field_validator("published_at", mode="before")
    @classmethod
    def normalize_published_at(cls, value: str | datetime | None) -> datetime | None:
        return parse_datetime_utc(value) if value is not None else None


class RowOneEdition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand: str = "ROW ONE"
    generated_at: datetime
    edition_date: datetime
    summary: LocalizedText
    sections: list[RowOneSection] = Field(default_factory=list)
    stories: list[RowOneStory] = Field(default_factory=list)

    @field_validator("generated_at", "edition_date", mode="before")
    @classmethod
    def normalize_datetime(cls, value: str | datetime) -> datetime:
        return parse_datetime_utc(value)

    def section_stories(self, section_key: RowOneSectionKey) -> list[RowOneStory]:
        return [story for story in self.stories if story.section_key == section_key]
