from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneReference,
    RowOneStory,
)

SAVED_ARTICLE_LOCAL_SECTION_BINDER_SECTION_LIMIT = 8
SAVED_ARTICLE_LOCAL_SECTION_BINDER_ITEM_LIMIT = 6
SAVED_ARTICLE_LOCAL_SECTION_BINDER_REFERENCE_LIMIT = 5
SAVED_ARTICLE_LOCAL_SECTION_BINDER_PARAGRAPH_LIMIT = 4
SAVED_ARTICLE_LOCAL_SECTION_BINDER_UNFILED_PARAGRAPH_LIMIT = 4
SAVED_ARTICLE_LOCAL_SECTION_BINDER_EXCERPT_CHARS = 150


@dataclass(frozen=True)
class RowOneSavedArticleLocalSectionBinderParagraph:
    index: int
    href: str
    excerpt: LocalizedText


@dataclass(frozen=True)
class RowOneSavedArticleLocalSectionBinderRow:
    title: LocalizedText
    section_position: int
    section_href: str
    item_labels: tuple[LocalizedText, ...]
    references: tuple[RowOneReference, ...]
    paragraphs: tuple[RowOneSavedArticleLocalSectionBinderParagraph, ...]


@dataclass(frozen=True)
class RowOneSavedArticleLocalSectionBinder:
    title: LocalizedText
    source_name: str
    rows: tuple[RowOneSavedArticleLocalSectionBinderRow, ...]
    unfiled_paragraphs: tuple[RowOneSavedArticleLocalSectionBinderParagraph, ...] = ()


def build_row_one_saved_article_local_section_binder(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleLocalSectionBinder | None:
    if story.id != local_article.story_id or not safe_local_article_story_id(story.id):
        return None

    rows: list[RowOneSavedArticleLocalSectionBinderRow] = []
    cited_indices: set[int] = set()
    for section_position, section in enumerate(local_article.content_sections, start=1):
        item_labels: list[LocalizedText] = []
        references: list[RowOneReference] = []
        paragraphs: list[RowOneSavedArticleLocalSectionBinderParagraph] = []
        row_seen_indices: set[int] = set()
        seen_references: set[tuple[str, str, str]] = set()

        for item in section.items:
            if len(item_labels) < SAVED_ARTICLE_LOCAL_SECTION_BINDER_ITEM_LIMIT:
                label = _nonblank_localized_text(item.label)
                if label is not None:
                    item_labels.append(label)

            for reference in item.references:
                if len(references) >= SAVED_ARTICLE_LOCAL_SECTION_BINDER_REFERENCE_LIMIT:
                    break
                reference_key = (
                    reference.name.strip().casefold(),
                    reference.type.strip().casefold(),
                    reference.label.strip().casefold(),
                )
                if reference_key in seen_references:
                    continue
                if not any(
                    (reference.name.strip(), reference.type.strip(), reference.label.strip())
                ):
                    continue
                seen_references.add(reference_key)
                references.append(reference)

            for paragraph_index in _valid_paragraph_indices(
                item.paragraph_indices,
                local_article=local_article,
            ):
                cited_indices.add(paragraph_index)
                if paragraph_index in row_seen_indices:
                    continue
                row_seen_indices.add(paragraph_index)
                if len(paragraphs) >= SAVED_ARTICLE_LOCAL_SECTION_BINDER_PARAGRAPH_LIMIT:
                    continue
                paragraphs.append(
                    _paragraph(
                        paragraph_index,
                        local_article=local_article,
                    )
                )

        title = _nonblank_localized_text(section.title)
        if title is None and not item_labels and not references and not paragraphs:
            continue
        if not item_labels and not references and not paragraphs:
            continue
        if len(rows) >= SAVED_ARTICLE_LOCAL_SECTION_BINDER_SECTION_LIMIT:
            continue

        rows.append(
            RowOneSavedArticleLocalSectionBinderRow(
                title=title
                or LocalizedText(
                    en=f"Section {section_position}",
                    zh=f"Section {section_position}",
                ),
                section_position=section_position,
                section_href=f"#local-article-content-section-{section_position}",
                item_labels=tuple(item_labels),
                references=tuple(references),
                paragraphs=tuple(paragraphs),
            )
        )

    unfiled_paragraphs = tuple(
        _paragraph(index, local_article=local_article)
        for index in _uncited_paragraph_indices(local_article, cited_indices)[
            :SAVED_ARTICLE_LOCAL_SECTION_BINDER_UNFILED_PARAGRAPH_LIMIT
        ]
    )
    if not rows and not unfiled_paragraphs:
        return None

    return RowOneSavedArticleLocalSectionBinder(
        title=LocalizedText(
            en=(local_article.title or story.headline).strip() or story.id,
            zh=(local_article.title or story.headline).strip() or story.id,
        ),
        source_name=local_article.source_name.strip() or story.source_name.strip(),
        rows=tuple(rows),
        unfiled_paragraphs=unfiled_paragraphs,
    )


def _nonblank_localized_text(value: LocalizedText) -> LocalizedText | None:
    en = value.en.strip()
    zh = value.zh.strip()
    if not en and not zh:
        return None
    return LocalizedText(en=en or zh, zh=zh or en)


def _valid_paragraph_indices(
    values: list[int],
    *,
    local_article: RowOneLocalArticle,
) -> list[int]:
    valid: list[int] = []
    seen: set[int] = set()
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        if value < 0 or value >= len(local_article.paragraphs) or value in seen:
            continue
        if not local_article.paragraphs[value].strip():
            continue
        seen.add(value)
        valid.append(value)
    return valid


def _uncited_paragraph_indices(
    local_article: RowOneLocalArticle,
    cited_indices: set[int],
) -> list[int]:
    return [
        index
        for index, paragraph in enumerate(local_article.paragraphs)
        if index not in cited_indices and paragraph.strip()
    ]


def _paragraph(
    index: int,
    *,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleLocalSectionBinderParagraph:
    en = _excerpt(local_article.paragraphs[index])
    zh = (
        _excerpt(local_article.paragraphs_zh[index])
        if len(local_article.paragraphs_zh) == len(local_article.paragraphs)
        and index < len(local_article.paragraphs_zh)
        and local_article.paragraphs_zh[index].strip()
        else en
    )
    return RowOneSavedArticleLocalSectionBinderParagraph(
        index=index,
        href=f"#local-article-paragraph-{index + 1}",
        excerpt=LocalizedText(en=en, zh=zh),
    )


def _excerpt(value: str) -> str:
    text = " ".join(value.strip().split())
    if len(text) <= SAVED_ARTICLE_LOCAL_SECTION_BINDER_EXCERPT_CHARS:
        return text
    return f"{text[:SAVED_ARTICLE_LOCAL_SECTION_BINDER_EXCERPT_CHARS].rstrip()}…"
