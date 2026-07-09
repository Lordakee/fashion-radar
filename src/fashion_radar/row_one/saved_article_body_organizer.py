from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneStory,
)
from fashion_radar.row_one.text import clean_row_one_text, normalize_row_one_paragraph

LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS = 5
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ITEM_LABELS = 3
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_PARAGRAPHS_PER_ROW = 3
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_UNFILED_PARAGRAPHS = 4
LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ROUTE_LINKS = 5
LOCAL_ARTICLE_BODY_ORGANIZER_EXCERPT_CHARS = 150
LOCAL_ARTICLE_BODY_ORGANIZER_SUPPORT_CHARS = 120


@dataclass(frozen=True)
class RowOneLocalArticleBodyOrganizerParagraph:
    index: int
    label: LocalizedText
    href: str
    excerpt: LocalizedText


@dataclass(frozen=True)
class RowOneLocalArticleBodyOrganizerSectionRow:
    title: LocalizedText
    section_position: int
    section_href: str
    item_labels: tuple[LocalizedText, ...]
    support: LocalizedText | None
    paragraphs: tuple[RowOneLocalArticleBodyOrganizerParagraph, ...]


@dataclass(frozen=True)
class RowOneSavedArticleBodyOrganizer:
    title: LocalizedText
    source_name: str
    saved_paragraph_count: int
    filed_paragraph_count: int
    unfiled_paragraph_count: int
    organized_section_count: int
    read_first_route: tuple[RowOneLocalArticleBodyOrganizerParagraph, ...]
    section_rows: tuple[RowOneLocalArticleBodyOrganizerSectionRow, ...]
    unfiled_paragraphs: tuple[RowOneLocalArticleBodyOrganizerParagraph, ...]


def build_row_one_saved_article_body_organizer(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleBodyOrganizer | None:
    if story.id != local_article.story_id or not safe_local_article_story_id(story.id):
        return None

    rendered_indices = _rendered_paragraph_indices(local_article)
    if not rendered_indices:
        return None
    rendered_index_set = set(rendered_indices)

    section_rows: list[RowOneLocalArticleBodyOrganizerSectionRow] = []
    filed_indices: set[int] = set()
    for section_position, section in enumerate(local_article.content_sections, start=1):
        if len(section_rows) >= LOCAL_ARTICLE_BODY_ORGANIZER_MAX_SECTION_ROWS:
            break
        row = _section_row(
            section,
            section_position=section_position,
            local_article=local_article,
            rendered_indices=rendered_index_set,
            filed_indices=filed_indices,
        )
        if row is None:
            continue
        section_rows.append(row)

    unfiled_indices = tuple(index for index in rendered_indices if index not in filed_indices)
    unfiled_paragraphs = tuple(
        _paragraph_view_model(local_article, index)
        for index in unfiled_indices[:LOCAL_ARTICLE_BODY_ORGANIZER_MAX_UNFILED_PARAGRAPHS]
    )
    if not section_rows and not unfiled_paragraphs:
        return None

    read_first_route = tuple(
        _paragraph_view_model(local_article, index)
        for index in rendered_indices[:LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ROUTE_LINKS]
    )
    title = (local_article.title or story.headline).strip() or story.id
    source_name = normalize_row_one_paragraph(
        local_article.source_name
    ) or normalize_row_one_paragraph(story.source_name)
    return RowOneSavedArticleBodyOrganizer(
        title=LocalizedText(en=title, zh=title),
        source_name=source_name,
        saved_paragraph_count=len(rendered_indices),
        filed_paragraph_count=len(filed_indices),
        unfiled_paragraph_count=len(unfiled_indices),
        organized_section_count=len(section_rows),
        read_first_route=read_first_route,
        section_rows=tuple(section_rows),
        unfiled_paragraphs=unfiled_paragraphs,
    )


def _section_row(
    section: RowOneLocalArticleContentSection,
    *,
    section_position: int,
    local_article: RowOneLocalArticle,
    rendered_indices: set[int],
    filed_indices: set[int],
) -> RowOneLocalArticleBodyOrganizerSectionRow | None:
    item_labels: list[LocalizedText] = []
    paragraphs: list[RowOneLocalArticleBodyOrganizerParagraph] = []
    row_seen_indices: set[int] = set()
    for item in section.items:
        if len(item_labels) < LOCAL_ARTICLE_BODY_ORGANIZER_MAX_ITEM_LABELS:
            label = _nonblank_localized_text(item.label)
            if label is not None:
                item_labels.append(label)
        for index in _strict_valid_paragraph_indices(item.paragraph_indices, rendered_indices):
            filed_indices.add(index)
            if index in row_seen_indices:
                continue
            row_seen_indices.add(index)
            if len(paragraphs) >= LOCAL_ARTICLE_BODY_ORGANIZER_MAX_PARAGRAPHS_PER_ROW:
                continue
            paragraphs.append(_paragraph_view_model(local_article, index))

    title = _nonblank_localized_text(section.title)
    support = _support_text(section)
    if not item_labels and support is None and not paragraphs:
        return None
    return RowOneLocalArticleBodyOrganizerSectionRow(
        title=title
        or LocalizedText(
            en=f"Section {section_position}",
            zh=f"第 {section_position} 节",
        ),
        section_position=section_position,
        section_href=_section_href(section_position),
        item_labels=tuple(item_labels),
        support=support,
        paragraphs=tuple(paragraphs),
    )


def _rendered_paragraph_indices(article: RowOneLocalArticle) -> tuple[int, ...]:
    return tuple(index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip())


def _strict_valid_paragraph_indices(
    indices: Sequence[object], rendered_indices: set[int]
) -> tuple[int, ...]:
    # Keep validation semantics aligned with saved_article_filing_inbox; this
    # body organizer keeps ordered tuple output for same-page route rendering.
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if isinstance(index, bool) or not isinstance(index, int):
            continue
        if index not in rendered_indices or index in seen:
            continue
        valid.append(index)
        seen.add(index)
    return tuple(valid)


def _paragraph_view_model(
    article: RowOneLocalArticle, index: int
) -> RowOneLocalArticleBodyOrganizerParagraph:
    paragraph_number = index + 1
    excerpt_en = _paragraph_excerpt(article.paragraphs[index])
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    has_aligned_zh = (
        aligned_zh
        and index < len(article.paragraphs_zh)
        and bool(article.paragraphs_zh[index].strip())
    )
    excerpt_zh = _paragraph_excerpt(article.paragraphs_zh[index]) if has_aligned_zh else excerpt_en
    return RowOneLocalArticleBodyOrganizerParagraph(
        index=index,
        label=LocalizedText(
            en=f"Paragraph {paragraph_number}",
            zh=f"第 {paragraph_number} 段",
        ),
        href=f"#local-article-paragraph-{paragraph_number}",
        excerpt=LocalizedText(en=excerpt_en, zh=excerpt_zh or excerpt_en),
    )


def _paragraph_excerpt(text: str) -> str:
    cleaned = " ".join(clean_row_one_text(text).split())
    if not cleaned and text.strip():
        cleaned = normalize_row_one_paragraph(text)
    if len(cleaned) <= LOCAL_ARTICLE_BODY_ORGANIZER_EXCERPT_CHARS:
        return cleaned
    return cleaned[: max(0, LOCAL_ARTICLE_BODY_ORGANIZER_EXCERPT_CHARS - 3)].rstrip() + "..."


def _nonblank_localized_text(value: LocalizedText | None) -> LocalizedText | None:
    if value is None:
        return None
    en = normalize_row_one_paragraph(value.en)
    zh = normalize_row_one_paragraph(value.zh)
    if not en and not zh:
        return None
    return LocalizedText(en=en or zh, zh=zh or en)


def _support_text(section: RowOneLocalArticleContentSection) -> LocalizedText | None:
    for value in (section.body, *(item.body for item in section.items)):
        text = _nonblank_localized_text(value)
        if text is not None:
            return LocalizedText(
                en=_support_excerpt(text.en),
                zh=_support_excerpt(text.zh),
            )
    return None


def _support_excerpt(text: str) -> str:
    normalized = normalize_row_one_paragraph(text)
    if len(normalized) <= LOCAL_ARTICLE_BODY_ORGANIZER_SUPPORT_CHARS:
        return normalized
    return normalized[: max(0, LOCAL_ARTICLE_BODY_ORGANIZER_SUPPORT_CHARS - 3)].rstrip() + "..."


def _section_href(position: int) -> str:
    return f"#local-article-content-section-{position}"
