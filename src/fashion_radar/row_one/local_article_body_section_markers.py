from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)
from fashion_radar.row_one.text import clean_row_one_text, normalize_row_one_paragraph

LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS = 8
LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_LABELS = 3
LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_REFERENCES = 4
LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS = 150


@dataclass(frozen=True)
class RowOneLocalArticleBodySectionMarker:
    paragraph_index: int
    paragraph_href: str
    section_position: int
    section_href: str
    title: LocalizedText
    support: LocalizedText
    item_labels: tuple[LocalizedText, ...]
    references: tuple[RowOneReference, ...]


def build_row_one_local_article_body_section_markers(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> tuple[RowOneLocalArticleBodySectionMarker, ...]:
    if story.id != local_article.story_id or not safe_local_article_story_id(story.id):
        return ()

    rendered_indices = _rendered_paragraph_indices(local_article)
    if not rendered_indices:
        return ()
    rendered_index_set = set(rendered_indices)

    markers: list[RowOneLocalArticleBodySectionMarker] = []
    used_paragraph_indices: set[int] = set()
    for section_position, section in enumerate(local_article.content_sections, start=1):
        marker = _section_marker(
            section,
            section_position=section_position,
            local_article=local_article,
            rendered_indices=rendered_index_set,
            used_paragraph_indices=used_paragraph_indices,
        )
        if marker is None:
            continue
        markers.append(marker)
        used_paragraph_indices.add(marker.paragraph_index)

    markers.sort(key=lambda marker: (marker.paragraph_index, marker.section_position))
    return tuple(markers[:LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS])


def _section_marker(
    section: RowOneLocalArticleContentSection,
    *,
    section_position: int,
    local_article: RowOneLocalArticle,
    rendered_indices: set[int],
    used_paragraph_indices: set[int],
) -> RowOneLocalArticleBodySectionMarker | None:
    paragraph_index = _section_first_valid_paragraph_index(
        section,
        rendered_indices=rendered_indices,
    )
    if paragraph_index is None or paragraph_index in used_paragraph_indices:
        return None

    title = _nonblank_localized_text(section.title) or LocalizedText(
        en=f"Section {section_position}",
        zh=f"第 {section_position} 节",
    )
    support = _support_text(section, local_article=local_article, paragraph_index=paragraph_index)
    if support is None:
        return None

    return RowOneLocalArticleBodySectionMarker(
        paragraph_index=paragraph_index,
        paragraph_href=f"#local-article-paragraph-{paragraph_index + 1}",
        section_position=section_position,
        section_href=f"#local-article-content-section-{section_position}",
        title=title,
        support=support,
        item_labels=_item_labels(section),
        references=_references(section),
    )


def _section_first_valid_paragraph_index(
    section: RowOneLocalArticleContentSection,
    *,
    rendered_indices: set[int],
) -> int | None:
    for item in section.items:
        for index in _strict_valid_paragraph_indices(item.paragraph_indices, rendered_indices):
            return index
    return None


def _rendered_paragraph_indices(article: RowOneLocalArticle) -> tuple[int, ...]:
    return tuple(index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip())


def _strict_valid_paragraph_indices(
    indices: Sequence[object], rendered_indices: set[int]
) -> tuple[int, ...]:
    # Keep these semantics aligned with the existing local-article body filing and
    # body-organizer helpers: bools/non-ints, negative values, overflow values,
    # duplicate values, and blank paragraphs are not valid marker insertion points.
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


def _support_text(
    section: RowOneLocalArticleContentSection,
    *,
    local_article: RowOneLocalArticle,
    paragraph_index: int,
) -> LocalizedText | None:
    section_body = _nonblank_localized_text(section.body)
    if section_body is not None:
        return _excerpt_localized_text(section_body)

    for item in section.items:
        item_body = _nonblank_localized_text(item.body)
        if item_body is not None:
            return _excerpt_localized_text(item_body)

    paragraph = _paragraph_support(local_article, paragraph_index)
    if paragraph is not None:
        return paragraph
    return None


def _paragraph_support(article: RowOneLocalArticle, paragraph_index: int) -> LocalizedText | None:
    if paragraph_index < 0 or paragraph_index >= len(article.paragraphs):
        return None
    excerpt_en = _excerpt(article.paragraphs[paragraph_index])
    if not excerpt_en:
        return None

    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    has_aligned_zh = (
        aligned_zh
        and paragraph_index < len(article.paragraphs_zh)
        and bool(article.paragraphs_zh[paragraph_index].strip())
    )
    excerpt_zh = _excerpt(article.paragraphs_zh[paragraph_index]) if has_aligned_zh else excerpt_en
    return LocalizedText(en=excerpt_en, zh=excerpt_zh or excerpt_en)


def _item_labels(section: RowOneLocalArticleContentSection) -> tuple[LocalizedText, ...]:
    labels: list[LocalizedText] = []
    seen: set[tuple[str, str]] = set()
    for item in section.items:
        label = _nonblank_localized_text(item.label)
        if label is None:
            continue
        key = _localized_key(label)
        if key in seen:
            continue
        labels.append(label)
        seen.add(key)
        if len(labels) >= LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_LABELS:
            break
    return tuple(labels)


def _references(section: RowOneLocalArticleContentSection) -> tuple[RowOneReference, ...]:
    references: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for item in section.items:
        for reference in item.references:
            key = (
                reference.name.casefold(),
                reference.type.casefold(),
                reference.label.casefold(),
            )
            if key in seen:
                continue
            references.append(reference)
            seen.add(key)
            if len(references) >= LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_REFERENCES:
                return tuple(references)
    return tuple(references)


def _nonblank_localized_text(value: LocalizedText | None) -> LocalizedText | None:
    if value is None:
        return None
    en = normalize_row_one_paragraph(value.en)
    zh = normalize_row_one_paragraph(value.zh)
    if not en and not zh:
        return None
    return LocalizedText(en=en or zh, zh=zh or en)


def _excerpt_localized_text(value: LocalizedText) -> LocalizedText:
    return LocalizedText(en=_excerpt(value.en), zh=_excerpt(value.zh) or _excerpt(value.en))


def _excerpt(text: str) -> str:
    cleaned = " ".join(clean_row_one_text(text).split())
    if not cleaned and text.strip():
        cleaned = normalize_row_one_paragraph(text)
    if len(cleaned) <= LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS:
        return cleaned
    return cleaned[: max(0, LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS - 3)].rstrip() + "..."


def _localized_key(value: LocalizedText) -> tuple[str, str]:
    return (value.en.casefold(), value.zh.casefold())
