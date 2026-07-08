from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.detail_routes import safe_row_one_detail_fragment_href
from fashion_radar.row_one.models import LocalizedText, RowOneLocalArticleBodySource
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)

SAVED_ARTICLE_READING_QUEUE_ITEM_LIMIT = 5
_LOCAL_ARTICLE_DIGEST_FRAGMENT = "local-article-digest"


@dataclass(frozen=True)
class RowOneSavedArticleReadingQueueItem:
    title: LocalizedText
    source_name: str
    body_source_label: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    href: str
    detail_path: str


@dataclass(frozen=True)
class RowOneSavedArticleReadingQueue:
    item_count: int
    items: tuple[RowOneSavedArticleReadingQueueItem, ...]


def build_row_one_saved_article_reading_queue(
    library: RowOneSavedArticleLibrary | None,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> RowOneSavedArticleReadingQueue | None:
    if library is None or not library.groups:
        return None

    items: list[RowOneSavedArticleReadingQueueItem] = []
    for group in library.groups:
        for entry in group.entries:
            item = _reading_queue_item(
                entry,
                local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
            )
            if item is None:
                continue
            items.append(item)
            if len(items) >= SAVED_ARTICLE_READING_QUEUE_ITEM_LIMIT:
                return RowOneSavedArticleReadingQueue(
                    item_count=len(items),
                    items=tuple(items),
                )

    if not items:
        return None
    return RowOneSavedArticleReadingQueue(
        item_count=len(items),
        items=tuple(items),
    )


def _reading_queue_item(
    entry: RowOneSavedArticleLibraryEntry,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> RowOneSavedArticleReadingQueueItem | None:
    safe_digest_href = safe_row_one_detail_fragment_href(
        entry.digest_path,
        _LOCAL_ARTICLE_DIGEST_FRAGMENT,
    )
    if safe_digest_href is None:
        return None
    detail_path = _detail_path_key(safe_digest_href)
    if detail_path is None:
        return None
    href = _local_article_page_digest_href(
        detail_path,
        local_article_page_hrefs_by_detail_path,
    )
    if href is None:
        href = f"../{safe_digest_href}"

    return RowOneSavedArticleReadingQueueItem(
        title=entry.title,
        source_name=entry.source_name,
        body_source_label=_body_source_label(entry.body_source),
        saved_paragraph_count=entry.saved_paragraph_count,
        organized_section_count=entry.organized_section_count,
        href=href,
        detail_path=detail_path,
    )


def _local_article_page_digest_href(
    detail_path: str,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    if not local_article_page_hrefs_by_detail_path:
        return None
    href = local_article_page_hrefs_by_detail_path.get(detail_path)
    if not isinstance(href, str):
        return None
    if href != href.strip() or any(character.isspace() for character in href):
        return None
    if href.startswith(".") or href.startswith("/") or "/" in href or not href.endswith(".html"):
        return None
    if not safe_local_article_story_id(href.removesuffix(".html")):
        return None
    return f"{href}#{_LOCAL_ARTICLE_DIGEST_FRAGMENT}"


def _detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    return path


def _body_source_label(body_source: RowOneLocalArticleBodySource) -> LocalizedText:
    if body_source == "summary_fallback":
        return LocalizedText(en="ROW ONE summary fallback", zh="ROW ONE 摘要回退")
    if body_source == "skipped":
        return LocalizedText(en="Skipped", zh="已跳过")
    return LocalizedText(en="Extracted article text", zh="已提取文章正文")
