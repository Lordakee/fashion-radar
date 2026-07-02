from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.row_one.models import LocalizedText, RowOneEdition
from fashion_radar.row_one.utils import isoformat_z, safe_external_url, utc_datetime


@dataclass(frozen=True)
class RowOneReadiness:
    generated_at: str
    edition_date: str
    story_count: int
    section_count: int
    safe_evidence_count: int
    empty_section_keys: list[str]
    empty_sections: LocalizedText
    readiness: LocalizedText


def build_row_one_readiness(edition: RowOneEdition) -> RowOneReadiness:
    empty_sections = [
        section for section in edition.sections if not edition.section_stories(section.key)
    ]
    safe_evidence_count = sum(
        1
        for story in edition.stories
        for link in story.evidence
        if safe_external_url(link.url) is not None
    )
    story_count = len(edition.stories)
    return RowOneReadiness(
        generated_at=isoformat_z(edition.generated_at),
        edition_date=utc_datetime(edition.edition_date).date().isoformat(),
        story_count=story_count,
        section_count=len(edition.sections),
        safe_evidence_count=safe_evidence_count,
        empty_section_keys=[section.key for section in empty_sections],
        empty_sections=LocalizedText(
            zh="，".join(section.title.zh for section in empty_sections) or "无",
            en=", ".join(section.title.en for section in empty_sections) or "none",
        ),
        readiness=LocalizedText(
            zh="可阅读" if story_count else "暂无故事",
            en="ready" if story_count else "empty",
        ),
    )
