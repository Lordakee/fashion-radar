from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import LocalizedText, RowOneReference
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)

MAX_SAVED_ARTICLE_READING_PATHS = 4
MAX_SAVED_ARTICLE_READING_PATH_STEPS = 3


@dataclass(frozen=True)
class RowOneSavedArticleReadingPathStep:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    lead: LocalizedText
    detail_path: str
    paragraph_indices: tuple[int, ...] = ()
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleReadingPath:
    key: str
    title: LocalizedText
    dek: LocalizedText
    step_count: int
    steps: tuple[RowOneSavedArticleReadingPathStep, ...]


@dataclass(frozen=True)
class RowOneSavedArticleReadingPaths:
    path_count: int
    step_count: int
    paths: tuple[RowOneSavedArticleReadingPath, ...]


def build_row_one_saved_article_reading_paths(
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
) -> RowOneSavedArticleReadingPaths | None:
    if library is None or organization is None:
        return None
    allowed_detail_paths = _library_detail_paths(library)
    if not allowed_detail_paths:
        return None

    paths: list[RowOneSavedArticleReadingPath] = []
    total_steps = 0
    for group in organization.groups:
        steps: list[RowOneSavedArticleReadingPathStep] = []
        seen_steps: set[tuple[str, str, str, str]] = set()
        for card in group.cards:
            step = _reading_path_step(card, allowed_detail_paths)
            if step is None:
                continue
            dedupe_key = (
                step.detail_path,
                " ".join(step.section_label.en.split()).casefold(),
                " ".join(step.lead.en.split()).casefold(),
                " ".join(step.lead.zh.split()).casefold(),
            )
            if dedupe_key in seen_steps:
                continue
            seen_steps.add(dedupe_key)
            steps.append(step)
            if len(steps) >= MAX_SAVED_ARTICLE_READING_PATH_STEPS:
                break
        if not steps:
            continue
        path = RowOneSavedArticleReadingPath(
            key=group.key,
            title=group.title,
            dek=group.dek,
            step_count=len(steps),
            steps=tuple(steps),
        )
        paths.append(path)
        total_steps += path.step_count
        if len(paths) >= MAX_SAVED_ARTICLE_READING_PATHS:
            break
    if not paths:
        return None
    return RowOneSavedArticleReadingPaths(
        path_count=len(paths),
        step_count=total_steps,
        paths=tuple(paths),
    )


def _library_detail_paths(library: RowOneSavedArticleLibrary) -> set[str]:
    detail_paths: set[str] = set()
    for group in library.groups:
        for entry in group.entries:
            detail_path = _entry_detail_path(entry)
            if detail_path is not None:
                detail_paths.add(detail_path)
    return detail_paths


def _entry_detail_path(entry: RowOneSavedArticleLibraryEntry) -> str | None:
    for href, fragment in (
        (entry.reader_path, "local-article-reader"),
        (entry.digest_path, "local-article-digest"),
        (entry.evidence_path, "local-article-paragraph-evidence"),
    ):
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            continue
        detail_path = _detail_path_key(safe_href)
        if detail_path is not None:
            return detail_path
    return None


def _reading_path_step(
    card: RowOneSavedArticleContentOrganizationCard,
    allowed_detail_paths: set[str],
) -> RowOneSavedArticleReadingPathStep | None:
    href = _safe_content_section_href(card.detail_path)
    if href is None:
        return None
    detail_path = _detail_path_key(href)
    if detail_path is None or detail_path not in allowed_detail_paths:
        return None
    return RowOneSavedArticleReadingPathStep(
        title=card.title,
        source_name=card.source_name,
        section_title=card.section_title,
        section_label=card.section_label,
        lead=card.lead,
        detail_path=href,
        paragraph_indices=card.paragraph_indices,
        references=card.references,
    )


def _safe_content_section_href(href: object) -> str | None:
    if not isinstance(href, str) or "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if not fragment.startswith("local-article-content-section-"):
        return None
    number = fragment.removeprefix("local-article-content-section-")
    if not number.isdecimal() or number != str(int(number)) or int(number) < 1:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return f"{safe_path}#{fragment}"


def _detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return str(safe_path)
