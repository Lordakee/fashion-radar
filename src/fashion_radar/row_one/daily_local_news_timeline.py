from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

DAILY_LOCAL_NEWS_TIMELINE_MAX_ITEMS = 6
DAILY_LOCAL_NEWS_TIMELINE_EXCERPT_CHARS = 180


@dataclass(frozen=True)
class RowOneDailyLocalNewsTimelineItem:
    title: LocalizedText
    source_name: str
    published_at: datetime
    published_label: LocalizedText
    excerpt: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalNewsTimeline:
    title: LocalizedText
    dek: LocalizedText
    item_count: int
    source_count: int
    latest_label: LocalizedText
    items: tuple[RowOneDailyLocalNewsTimelineItem, ...]


def build_row_one_daily_local_news_timeline(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalNewsTimeline | None:
    candidates: list[tuple[int, str, RowOneDailyLocalNewsTimelineItem]] = []
    for story_index, story in enumerate(edition.stories):
        if not safe_local_article_story_id(story.id):
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        page_href = _safe_article_page_href(story.id, article_hrefs_by_story_id.get(story.id))
        if page_href is None:
            continue
        published_at = article.published_at or story.published_at
        if published_at is None:
            continue
        paragraph = _first_paragraph(article)
        if paragraph is None:
            continue
        paragraph_index, excerpt = paragraph
        candidates.append(
            (
                story_index,
                story.id,
                RowOneDailyLocalNewsTimelineItem(
                    title=_title(story.headline, article.title, story.id),
                    source_name=_source_name(article.source_name, story.source_name),
                    published_at=published_at,
                    published_label=_published_label(published_at),
                    excerpt=excerpt,
                    href=f"articles/{page_href}#local-article-paragraph-{paragraph_index + 1}",
                ),
            )
        )

    candidates.sort(key=lambda value: (-value[2].published_at.timestamp(), value[0], value[1]))
    items = tuple(
        item for _story_index, _story_id, item in candidates[:DAILY_LOCAL_NEWS_TIMELINE_MAX_ITEMS]
    )
    if not items:
        return None
    source_count = len({item.source_name.casefold() for item in items if item.source_name})
    return RowOneDailyLocalNewsTimeline(
        title=LocalizedText(en="Daily Local News Timeline", zh="每日本地新闻时间线"),
        dek=LocalizedText(
            en="Newest saved local fashion stories in publication order.",
            zh="按发布时间排列的最新本地保存时尚资讯。",
        ),
        item_count=len(items),
        source_count=source_count,
        latest_label=items[0].published_label,
        items=items,
    )


def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or "//" in href or href.startswith((".", "/", "//")):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return path.name


def _first_paragraph(article: RowOneLocalArticle) -> tuple[int, LocalizedText] | None:
    for index, paragraph in enumerate(article.paragraphs):
        paragraph_en = normalize_row_one_paragraph(paragraph)
        if not paragraph_en:
            continue
        paragraph_zh = ""
        if len(article.paragraphs_zh) == len(article.paragraphs):
            paragraph_zh = normalize_row_one_paragraph(article.paragraphs_zh[index])
        excerpt_en = _localized_excerpt(paragraph_en)
        excerpt_zh = _localized_excerpt(paragraph_zh or paragraph_en)
        return index, LocalizedText(en=excerpt_en, zh=excerpt_zh)
    return None


def _localized_excerpt(value: str) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= DAILY_LOCAL_NEWS_TIMELINE_EXCERPT_CHARS:
        return normalized
    return normalized[: DAILY_LOCAL_NEWS_TIMELINE_EXCERPT_CHARS - 3].rstrip() + "..."


def _title(story_headline: str, article_title: str | None, story_id: str) -> LocalizedText:
    title = (
        normalize_row_one_paragraph(story_headline)
        or normalize_row_one_paragraph(article_title or "")
        or story_id
    )
    return LocalizedText(en=title, zh=title)


def _source_name(article_source_name: str, story_source_name: str) -> str:
    return (
        normalize_row_one_paragraph(article_source_name)
        or normalize_row_one_paragraph(story_source_name)
        or "Unknown source"
    )


def _published_label(published_at: datetime) -> LocalizedText:
    return LocalizedText(
        en=published_at.strftime("%b %d, %Y"),
        zh=published_at.strftime("%Y-%m-%d"),
    )
