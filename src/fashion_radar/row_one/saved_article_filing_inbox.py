from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.body_source_labels import row_one_body_source_label
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
)
from fashion_radar.row_one.text import clean_row_one_text

SAVED_ARTICLE_FILING_INBOX_MAX_ARTICLES = 8
SAVED_ARTICLE_FILING_INBOX_MAX_PARAGRAPHS_PER_ARTICLE = 3
SAVED_ARTICLE_FILING_INBOX_EXCERPT_CHARS = 140


@dataclass(frozen=True)
class RowOneSavedArticleFilingInboxParagraph:
    index: int
    label: LocalizedText
    href: str
    excerpt: LocalizedText


@dataclass(frozen=True)
class RowOneSavedArticleFilingInboxItem:
    title: LocalizedText
    source_name: str
    body_source_label: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    unfiled_paragraph_count: int
    paragraphs: tuple[RowOneSavedArticleFilingInboxParagraph, ...]


@dataclass(frozen=True)
class RowOneSavedArticleFilingInbox:
    items: tuple[RowOneSavedArticleFilingInboxItem, ...]


def build_row_one_saved_article_filing_inbox(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> RowOneSavedArticleFilingInbox | None:
    if not local_articles_by_story_id or not local_article_page_hrefs_by_detail_path:
        return None

    items: list[RowOneSavedArticleFilingInboxItem] = []
    for story in edition.stories:
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue

        page_href = _safe_filing_inbox_article_href(
            local_article_page_hrefs_by_detail_path.get(story.detail_path)
        )
        if page_href is None:
            continue

        rendered_indices = _rendered_paragraph_indices(article)
        if not rendered_indices:
            continue

        filed_indices = _filed_paragraph_indices(article, rendered_indices)
        unfiled_indices = tuple(
            index for index in sorted(rendered_indices) if index not in filed_indices
        )
        if not unfiled_indices:
            continue

        paragraphs = tuple(
            _paragraph_view_model(article, index, page_href)
            for index in unfiled_indices[:SAVED_ARTICLE_FILING_INBOX_MAX_PARAGRAPHS_PER_ARTICLE]
        )
        items.append(
            RowOneSavedArticleFilingInboxItem(
                title=LocalizedText(
                    en=(article.title or story.headline).strip() or story.headline,
                    zh=(article.title or story.headline).strip() or story.headline,
                ),
                source_name=article.source_name.strip() or story.source_name.strip(),
                body_source_label=_body_source_label(article),
                saved_paragraph_count=len(rendered_indices),
                organized_section_count=len(article.content_sections),
                unfiled_paragraph_count=len(unfiled_indices),
                paragraphs=paragraphs,
            )
        )
        if len(items) >= SAVED_ARTICLE_FILING_INBOX_MAX_ARTICLES:
            break

    if not items:
        return None
    return RowOneSavedArticleFilingInbox(items=tuple(items))


def _safe_filing_inbox_article_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if href != href.strip() or not href:
        return None
    lowered = href.casefold()
    if lowered.startswith(("http:", "https:", "//", "javascript:", ".", "/")):
        return None
    if any(character.isspace() for character in href):
        return None
    if "/" in href or "\\" in href:
        return None
    if not href.endswith(".html"):
        return None
    story_id = href.removesuffix(".html")
    if not safe_local_article_story_id(story_id):
        return None
    return href


def _rendered_paragraph_indices(article: RowOneLocalArticle) -> set[int]:
    return {
        index for index, paragraph in enumerate(article.paragraphs) if _paragraph_excerpt(paragraph)
    }


def _filed_paragraph_indices(article: RowOneLocalArticle, rendered_indices: set[int]) -> set[int]:
    filed_indices: set[int] = set()
    for section in article.content_sections:
        for item in section.items:
            filed_indices.update(
                _strict_valid_paragraph_indices(item.paragraph_indices, rendered_indices)
            )
    return filed_indices


def _strict_valid_paragraph_indices(
    indices: Sequence[object], rendered_indices: set[int]
) -> tuple[int, ...]:
    # Keep validation semantics aligned with saved_article_body_organizer; the
    # filing inbox uses the same index safety rules for article-library links.
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


def _paragraph_excerpt(text: str) -> str:
    cleaned = " ".join(clean_row_one_text(text).split())
    if len(cleaned) <= SAVED_ARTICLE_FILING_INBOX_EXCERPT_CHARS:
        return cleaned
    return cleaned[: max(0, SAVED_ARTICLE_FILING_INBOX_EXCERPT_CHARS - 3)].rstrip() + "..."


def _body_source_label(article: RowOneLocalArticle) -> LocalizedText:
    return row_one_body_source_label(article.body_source)


def _paragraph_view_model(
    article: RowOneLocalArticle, index: int, page_href: str
) -> RowOneSavedArticleFilingInboxParagraph:
    paragraph_number = index + 1
    excerpt_en = _paragraph_excerpt(article.paragraphs[index])
    excerpt_zh = (
        _paragraph_excerpt(article.paragraphs_zh[index])
        if index < len(article.paragraphs_zh)
        else ""
    )
    return RowOneSavedArticleFilingInboxParagraph(
        index=index,
        label=LocalizedText(
            en=f"Paragraph {paragraph_number}",
            zh=f"第 {paragraph_number} 段",
        ),
        href=f"{page_href}#local-article-paragraph-{paragraph_number}",
        excerpt=LocalizedText(en=excerpt_en, zh=excerpt_zh or excerpt_en),
    )
