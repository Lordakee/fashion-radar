from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.detail_routes import is_safe_row_one_detail_path
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneReference,
)

MAX_SAVED_ARTICLE_BRIEF_ITEMS = 4
MAX_SAVED_ARTICLE_BRIEF_REFERENCES = 4


@dataclass(frozen=True)
class RowOneSavedArticleBriefItem:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    lead: LocalizedText
    detail_path: str
    people_brands: tuple[RowOneReference, ...] = ()
    products: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleBriefs:
    article_count: int
    items: list[RowOneSavedArticleBriefItem]


def build_row_one_saved_article_briefs(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedArticleBriefs | None:
    items: list[RowOneSavedArticleBriefItem] = []
    publishable_count = 0
    for story in edition.stories:
        article = local_articles_by_story_id.get(story.id)
        if article is None:
            continue
        if article.story_id != story.id:
            continue
        if not safe_local_article_story_id(story.id):
            continue
        if not is_safe_row_one_detail_path(story.detail_path):
            continue
        if not _has_nonblank_paragraph(article):
            continue
        lead = _lead_text(article)
        if lead is None:
            continue
        publishable_count += 1
        if len(items) >= MAX_SAVED_ARTICLE_BRIEF_ITEMS:
            continue
        items.append(
            RowOneSavedArticleBriefItem(
                title=LocalizedText(zh=story.headline, en=story.headline),
                source_name=_source_display_name(article),
                section_title=_section_title(edition, story.section_key),
                lead=lead,
                detail_path=f"{story.detail_path}#local-article-digest",
                people_brands=_references(article.content_sections, "entities"),
                products=_references(article.content_sections, "product_signals"),
            )
        )
    if not items:
        return None
    return RowOneSavedArticleBriefs(article_count=publishable_count, items=items)


def _has_nonblank_paragraph(article: RowOneLocalArticle) -> bool:
    return any(paragraph.strip() for paragraph in article.paragraphs)


def _lead_text(article: RowOneLocalArticle) -> LocalizedText | None:
    takeaway = _takeaway_text(article.content_sections)
    if takeaway is not None:
        return takeaway
    return _first_paragraph_text(article)


def _takeaway_text(sections: Iterable[RowOneLocalArticleContentSection]) -> LocalizedText | None:
    for section in sections:
        if section.key != "takeaways":
            continue
        for item in section.items:
            if item.body is None:
                continue
            en = item.body.en.strip()
            zh = item.body.zh.strip()
            if not en and not zh:
                continue
            return LocalizedText(zh=zh or en, en=en or zh)
    return None


def _first_paragraph_text(article: RowOneLocalArticle) -> LocalizedText | None:
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    for index, paragraph in enumerate(article.paragraphs):
        en = paragraph.strip()
        if not en:
            continue
        zh = article.paragraphs_zh[index].strip() if aligned_zh else ""
        return LocalizedText(zh=zh or en, en=en)
    return None


def _references(
    sections: Iterable[RowOneLocalArticleContentSection],
    key: str,
) -> tuple[RowOneReference, ...]:
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for section in sections:
        if section.key != key:
            continue
        for item in section.items:
            for ref in item.references:
                dedupe_key = (
                    " ".join(ref.name.split()).casefold(),
                    " ".join(ref.type.split()).casefold(),
                    " ".join(ref.label.split()).casefold(),
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                refs.append(ref)
                if len(refs) >= MAX_SAVED_ARTICLE_BRIEF_REFERENCES:
                    return tuple(refs)
    return tuple(refs)


def _source_display_name(article: RowOneLocalArticle) -> str:
    return article.source_name.strip() or "Unknown source"


def _section_title(edition: RowOneEdition, section_key: str) -> LocalizedText:
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    fallback = section_key.replace("_", " ").title()
    return LocalizedText(zh=fallback, en=fallback)
