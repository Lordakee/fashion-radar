from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import LocalizedText, RowOneEdition, RowOneLocalArticle

MAX_SAVED_ARTICLE_COVERAGE_ITEMS = 4
_DETAIL_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\.html$")


@dataclass(frozen=True)
class RowOneSavedArticleCoverageSource:
    name: str
    article_count: int


@dataclass(frozen=True)
class RowOneSavedArticleCoverageItem:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    detail_path: str
    saved_paragraph_count: int
    organized_section_count: int


@dataclass(frozen=True)
class RowOneSavedArticleCoverage:
    article_count: int
    saved_paragraph_count: int
    organized_section_count: int
    source_count: int
    sources: list[RowOneSavedArticleCoverageSource]
    items: list[RowOneSavedArticleCoverageItem]


def build_row_one_saved_article_coverage(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedArticleCoverage | None:
    story_articles = []
    for position, story in enumerate(edition.stories):
        article = local_articles_by_story_id.get(story.id)
        if article is None:
            continue
        if not safe_local_article_story_id(story.id):
            continue
        if not _safe_detail_path(story.detail_path):
            continue
        saved_paragraph_count = _saved_paragraph_count(article)
        if saved_paragraph_count == 0:
            continue
        story_articles.append((position, story, article, saved_paragraph_count))
    if not story_articles:
        return None

    source_counts: dict[str, tuple[str, int]] = {}
    items: list[RowOneSavedArticleCoverageItem] = []
    for _, story, article, saved_paragraph_count in story_articles:
        source_name = _source_display_name(article)
        source_key = _source_key(source_name)
        display_name, count = source_counts.get(source_key, (source_name, 0))
        source_counts[source_key] = (display_name, count + 1)
        items.append(
            RowOneSavedArticleCoverageItem(
                title=LocalizedText(zh=story.headline, en=story.headline),
                source_name=source_name,
                section_title=_section_title(edition, story.section_key),
                detail_path=f"{story.detail_path}#local-article-digest",
                saved_paragraph_count=saved_paragraph_count,
                organized_section_count=len(article.content_sections),
            )
        )

    sources = [
        RowOneSavedArticleCoverageSource(name=name, article_count=count)
        for name, count in source_counts.values()
    ]
    return RowOneSavedArticleCoverage(
        article_count=len(story_articles),
        saved_paragraph_count=sum(item.saved_paragraph_count for item in items),
        organized_section_count=sum(item.organized_section_count for item in items),
        source_count=len(sources),
        sources=sources,
        items=items[:MAX_SAVED_ARTICLE_COVERAGE_ITEMS],
    )


def _saved_paragraph_count(article: RowOneLocalArticle) -> int:
    return sum(1 for paragraph in article.paragraphs if paragraph.strip())


def _source_display_name(article: RowOneLocalArticle) -> str:
    return article.source_name.strip() or "Unknown source"


def _source_key(name: str) -> str:
    return " ".join(name.split()).casefold()


def _safe_detail_path(path: str) -> bool:
    pure_path = PurePosixPath(path)
    return (
        not pure_path.is_absolute()
        and len(pure_path.parts) == 2
        and pure_path.parts[0] == "details"
        and pure_path.parts[1] not in ("", ".", "..")
        and ".." not in pure_path.parts
        and _DETAIL_FILENAME_RE.fullmatch(pure_path.name) is not None
    )


def _section_title(edition: RowOneEdition, section_key: str) -> LocalizedText:
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    fallback = section_key.replace("_", " ").title()
    return LocalizedText(zh=fallback, en=fallback)
