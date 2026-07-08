from __future__ import annotations

from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibrarySourceGroup,
)
from fashion_radar.row_one.saved_article_reading_queue import (
    SAVED_ARTICLE_READING_QUEUE_ITEM_LIMIT,
    build_row_one_saved_article_reading_queue,
)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _entry(
    index: int,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    detail_path: str | None = None,
    digest_path: str | None = None,
    body_source: str = "extracted",
    saved_paragraph_count: int = 2,
    organized_section_count: int = 1,
) -> RowOneSavedArticleLibraryEntry:
    path = detail_path or f"details/article-{index:010x}.html"
    return RowOneSavedArticleLibraryEntry(
        title=_lt(title or f"Article {index}", f"文章 {index}"),
        source_name=source_name,
        section_title=_lt("Top Stories", "今日重点"),
        saved_paragraph_count=saved_paragraph_count,
        organized_section_count=organized_section_count,
        body_source=body_source,
        digest_path=digest_path if digest_path is not None else f"{path}#local-article-digest",
        reader_path=f"{path}#local-article-reader",
        evidence_path=f"{path}#local-article-paragraph-evidence",
        paragraph_links=(),
        references=(),
    )


def _library(*entries: RowOneSavedArticleLibraryEntry) -> RowOneSavedArticleLibrary:
    rows = list(entries)
    return RowOneSavedArticleLibrary(
        article_count=len(rows),
        source_count=1 if rows else 0,
        saved_paragraph_count=sum(entry.saved_paragraph_count for entry in rows),
        organized_section_count=sum(entry.organized_section_count for entry in rows),
        extracted_article_count=sum(1 for entry in rows if entry.body_source == "extracted"),
        summary_fallback_article_count=sum(
            1 for entry in rows if entry.body_source == "summary_fallback"
        ),
        skipped_article_count=sum(1 for entry in rows if entry.body_source == "skipped"),
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name="Vogue Business",
                article_count=len(rows),
                saved_paragraph_count=sum(entry.saved_paragraph_count for entry in rows),
                organized_section_count=sum(entry.organized_section_count for entry in rows),
                entries=rows,
            )
        ],
    )


def test_build_saved_article_reading_queue_preserves_library_order() -> None:
    library = _library(
        _entry(
            1,
            title="The Row signal",
            detail_path="details/the-row-signal-1234567890.html",
            body_source="summary_fallback",
        ),
        _entry(
            2,
            title="Alaia signal",
            detail_path="details/alaia-signal-1234567890.html",
            body_source="extracted",
            saved_paragraph_count=3,
            organized_section_count=2,
        ),
    )

    queue = build_row_one_saved_article_reading_queue(
        library,
        local_article_page_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
        },
    )

    assert queue is not None
    assert queue.item_count == 2
    assert [item.title.en for item in queue.items] == ["The Row signal", "Alaia signal"]
    assert queue.items[0].href == "the-row-signal-1234567890.html#local-article-digest"
    assert queue.items[1].href == "../details/alaia-signal-1234567890.html#local-article-digest"
    assert queue.items[0].source_name == "Vogue Business"
    assert queue.items[0].body_source_label.en == "ROW ONE summary fallback"
    assert queue.items[1].body_source_label.en == "Extracted article text"
    assert queue.items[1].saved_paragraph_count == 3
    assert queue.items[1].organized_section_count == 2


def test_build_saved_article_reading_queue_caps_safe_items() -> None:
    library = _library(
        *(
            _entry(
                index,
                detail_path=f"details/article-{index:010x}.html",
                title=f"Article {index}",
            )
            for index in range(1, 8)
        )
    )

    queue = build_row_one_saved_article_reading_queue(
        library,
        local_article_page_hrefs_by_detail_path={},
    )

    assert queue is not None
    assert len(queue.items) == SAVED_ARTICLE_READING_QUEUE_ITEM_LIMIT
    assert [item.title.en for item in queue.items] == [
        "Article 1",
        "Article 2",
        "Article 3",
        "Article 4",
        "Article 5",
    ]


def test_build_saved_article_reading_queue_omits_empty_inputs() -> None:
    empty_library = _library()

    assert (
        build_row_one_saved_article_reading_queue(
            None,
            local_article_page_hrefs_by_detail_path={},
        )
        is None
    )
    assert (
        build_row_one_saved_article_reading_queue(
            empty_library,
            local_article_page_hrefs_by_detail_path={},
        )
        is None
    )


def test_build_saved_article_reading_queue_filters_unsafe_and_missing_hrefs() -> None:
    library = _library(
        _entry(
            1,
            title="Unsafe traversal",
            detail_path="details/../unsafe-1234567890.html",
        ),
        _entry(
            2,
            title="Unsafe javascript",
            detail_path="details/javascript-signal-1234567890.html",
            digest_path="javascript:alert(1)#local-article-digest",
        ),
        _entry(
            3,
            title="Missing fragment",
            detail_path="details/missing-signal-1234567890.html",
            digest_path="details/missing-signal-1234567890.html#other-fragment",
        ),
        _entry(
            4,
            title="Safe fallback",
            detail_path="details/safe-signal-1234567890.html",
        ),
    )

    queue = build_row_one_saved_article_reading_queue(
        library,
        local_article_page_hrefs_by_detail_path={
            "details/../unsafe-1234567890.html": "https://example.com/article.html",
            "details/javascript-signal-1234567890.html": "javascript-alert.html ",
        },
    )

    assert queue is not None
    assert [item.title.en for item in queue.items] == ["Safe fallback"]
    hrefs = {item.href for item in queue.items}
    assert "javascript:" not in hrefs
    assert not any(href.startswith(("http:", "https:", "//")) for href in hrefs)
    assert not any(not href.strip() or href != href.strip() for href in hrefs)
    assert all(".." not in href.removeprefix("../details/") for href in hrefs)


def test_build_saved_article_reading_queue_returns_none_when_no_safe_entries() -> None:
    library = _library(
        _entry(
            1,
            title="Unsafe only",
            detail_path="details/unsafe-only-1234567890.html",
            digest_path="details/unsafe-only-1234567890.html#other-fragment",
        )
    )

    assert (
        build_row_one_saved_article_reading_queue(
            library,
            local_article_page_hrefs_by_detail_path={},
        )
        is None
    )
