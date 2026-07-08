from __future__ import annotations

from fashion_radar.row_one.models import LocalizedText, RowOneReference
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
    RowOneSavedArticleLibrarySourceGroup,
)
from fashion_radar.row_one.saved_article_read_next_clusters import (
    SAVED_ARTICLE_READ_NEXT_CLUSTER_ITEM_LIMIT,
    SAVED_ARTICLE_READ_NEXT_CLUSTER_LIMIT,
    SAVED_ARTICLE_READ_NEXT_CLUSTER_REFERENCE_LIMIT,
    build_row_one_saved_article_read_next_clusters,
)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _ref(index: int) -> RowOneReference:
    return RowOneReference(
        name=f"Reference {index}",
        type="source",
        label=f"Ref {index}",
    )


def _entry(
    index: int,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    detail_path: str | None = None,
    digest_path: str | None = None,
    body_source: str = "extracted",
    saved_paragraph_count: int = 3,
    organized_section_count: int = 2,
    references: tuple[RowOneReference, ...] = (),
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
        references=references,
    )


def _library(*entries: RowOneSavedArticleLibraryEntry) -> RowOneSavedArticleLibrary:
    rows = list(entries)
    groups_by_source: dict[str, list[RowOneSavedArticleLibraryEntry]] = {}
    source_names: dict[str, str] = {}
    for entry in rows:
        key = " ".join(entry.source_name.split()).casefold()
        groups_by_source.setdefault(key, []).append(entry)
        source_names.setdefault(key, entry.source_name)
    return RowOneSavedArticleLibrary(
        article_count=len(rows),
        source_count=len(groups_by_source),
        saved_paragraph_count=sum(entry.saved_paragraph_count for entry in rows),
        organized_section_count=sum(entry.organized_section_count for entry in rows),
        extracted_article_count=sum(1 for entry in rows if entry.body_source == "extracted"),
        summary_fallback_article_count=sum(
            1 for entry in rows if entry.body_source == "summary_fallback"
        ),
        skipped_article_count=sum(1 for entry in rows if entry.body_source == "skipped"),
        groups=[
            RowOneSavedArticleLibrarySourceGroup(
                source_name=source_names[key],
                article_count=len(source_entries),
                saved_paragraph_count=sum(entry.saved_paragraph_count for entry in source_entries),
                organized_section_count=sum(
                    entry.organized_section_count for entry in source_entries
                ),
                entries=source_entries,
            )
            for key, source_entries in groups_by_source.items()
        ],
    )


def _card(
    index: int,
    *,
    title: str | None = None,
    source_name: str = "Vogue Business",
    detail_path: str | None = None,
    section_number: int = 1,
    paragraph_indices: tuple[int, ...] = (0, 1),
    references: tuple[RowOneReference, ...] = (),
) -> RowOneSavedArticleContentOrganizationCard:
    path = detail_path or f"details/article-{index:010x}.html"
    return RowOneSavedArticleContentOrganizationCard(
        title=_lt(title or f"Article {index}", f"文章 {index}"),
        source_name=source_name,
        section_title=_lt("Top Stories", "今日重点"),
        section_label=_lt("Takeaway", "要点"),
        lead=_lt(f"Lead {index}", f"导语 {index}"),
        detail_path=f"{path}#local-article-content-section-{section_number}",
        paragraph_indices=paragraph_indices,
        references=references,
    )


def _group(
    key: str,
    title: str,
    *cards: RowOneSavedArticleContentOrganizationCard,
) -> RowOneSavedArticleContentOrganizationGroup:
    return RowOneSavedArticleContentOrganizationGroup(
        key=key,
        title=_lt(title, title),
        dek=_lt(f"{title} deck", f"{title} 说明"),
        cards=list(cards),
    )


def _organization(
    *groups: RowOneSavedArticleContentOrganizationGroup,
) -> RowOneSavedArticleContentOrganization:
    return RowOneSavedArticleContentOrganization(groups=list(groups))


def _base_library() -> RowOneSavedArticleLibrary:
    return _library(
        _entry(
            1,
            title="The Row signal",
            detail_path="details/the-row-signal-1234567890.html",
            source_name="Vogue Business",
            body_source="extracted",
            saved_paragraph_count=3,
            organized_section_count=2,
        ),
        _entry(
            2,
            title="Alaia signal",
            detail_path="details/alaia-signal-1234567890.html",
            source_name="Vogue Business",
            body_source="summary_fallback",
            saved_paragraph_count=2,
            organized_section_count=1,
        ),
    )


def _base_organization() -> RowOneSavedArticleContentOrganization:
    return _organization(
        _group(
            "takeaways",
            "Read First",
            _card(
                2,
                title="Alaia signal",
                detail_path="details/alaia-signal-1234567890.html",
            ),
            _card(
                1,
                title="The Row signal",
                detail_path="details/the-row-signal-1234567890.html",
            ),
            _card(
                99,
                title="Unsupported",
                detail_path="details/unsupported-signal-1234567890.html",
            ),
        ),
        _group(
            "entities",
            "People & Brands",
            _card(
                1,
                title="The Row signal",
                detail_path="details/the-row-signal-1234567890.html",
                paragraph_indices=(0,),
            ),
        ),
    )


def test_build_read_next_clusters_preserves_group_and_library_order() -> None:
    clusters = build_row_one_saved_article_read_next_clusters(
        _base_library(),
        _base_organization(),
        local_article_page_hrefs_by_detail_path={
            "details/the-row-signal-1234567890.html": "the-row-signal-1234567890.html",
        },
    )

    assert clusters is not None
    assert clusters.cluster_count == 2
    assert clusters.item_count == 3
    assert clusters.source_count == 1
    assert clusters.evidence_count == 5
    assert [cluster.title.en for cluster in clusters.clusters] == [
        "Read First",
        "People & Brands",
    ]
    assert [item.title.en for item in clusters.clusters[0].items] == [
        "The Row signal",
        "Alaia signal",
    ]
    assert (
        clusters.clusters[0].items[0].href == "the-row-signal-1234567890.html#local-article-digest"
    )
    assert (
        clusters.clusters[0].items[1].href
        == "../details/alaia-signal-1234567890.html#local-article-content-section-1"
    )
    assert clusters.clusters[0].items[0].body_source_label.en == "Extracted article text"
    assert clusters.clusters[0].items[1].body_source_label.en == "ROW ONE summary fallback"
    assert clusters.clusters[0].items[1].saved_paragraph_count == 2
    assert clusters.clusters[0].items[1].organized_section_count == 1


def test_build_read_next_clusters_caps_clusters_items_and_references() -> None:
    entries = tuple(
        _entry(index, detail_path=f"details/article-{index:010x}.html") for index in range(1, 8)
    )
    groups = tuple(
        _group(
            f"group_{group_index}",
            f"Group {group_index}",
            *(
                _card(
                    index,
                    detail_path=f"details/article-{index:010x}.html",
                    references=tuple(_ref(ref_index) for ref_index in range(1, 8)),
                )
                for index in range(1, 8)
            ),
        )
        for group_index in range(1, 6)
    )

    clusters = build_row_one_saved_article_read_next_clusters(
        _library(*entries),
        _organization(*groups),
        local_article_page_hrefs_by_detail_path={},
    )

    assert clusters is not None
    assert clusters.cluster_count == SAVED_ARTICLE_READ_NEXT_CLUSTER_LIMIT
    assert all(
        len(cluster.items) <= SAVED_ARTICLE_READ_NEXT_CLUSTER_ITEM_LIMIT
        for cluster in clusters.clusters
    )
    assert all(
        len(item.references) == SAVED_ARTICLE_READ_NEXT_CLUSTER_REFERENCE_LIMIT
        for cluster in clusters.clusters
        for item in cluster.items
    )


def test_build_read_next_clusters_omits_empty_inputs() -> None:
    empty_library = _library()
    empty_organization = _organization()

    assert (
        build_row_one_saved_article_read_next_clusters(
            None,
            _base_organization(),
            local_article_page_hrefs_by_detail_path={},
        )
        is None
    )
    assert (
        build_row_one_saved_article_read_next_clusters(
            _base_library(),
            None,
            local_article_page_hrefs_by_detail_path={},
        )
        is None
    )
    assert (
        build_row_one_saved_article_read_next_clusters(
            empty_library,
            empty_organization,
            local_article_page_hrefs_by_detail_path={},
        )
        is None
    )


def test_build_read_next_clusters_filters_unsafe_hrefs_and_missing_library_cards() -> None:
    library = _library(
        _entry(1, title="Safe", detail_path="details/safe-signal-1234567890.html"),
        _entry(
            2,
            title="Wrong digest",
            detail_path="details/wrong-digest-1234567890.html",
            digest_path="details/wrong-digest-1234567890.html#wrong-fragment",
        ),
        _entry(
            3,
            title="Traversal digest",
            detail_path="details/traversal-digest-1234567890.html",
            digest_path="details/../traversal-digest-1234567890.html#local-article-digest",
        ),
    )
    organization = _organization(
        _group(
            "takeaways",
            "Read First",
            _card(1, title="Safe", detail_path="details/safe-signal-1234567890.html"),
            _card(
                2,
                title="Wrong digest",
                detail_path="details/wrong-digest-1234567890.html",
            ),
            _card(
                3,
                title="Traversal digest",
                detail_path="details/traversal-digest-1234567890.html",
            ),
            RowOneSavedArticleContentOrganizationCard(
                title=_lt("JavaScript"),
                source_name="Bad source",
                section_title=_lt("Top Stories"),
                section_label=_lt("Bad"),
                lead=_lt("Unsafe"),
                detail_path="javascript:alert(1)#local-article-content-section-1",
                paragraph_indices=(0,),
                references=(),
            ),
            _card(
                4,
                title="Missing library",
                detail_path="details/missing-library-1234567890.html",
            ),
        )
    )

    clusters = build_row_one_saved_article_read_next_clusters(
        library,
        organization,
        local_article_page_hrefs_by_detail_path={
            "details/safe-signal-1234567890.html": " https://example.com/article.html",
            "details/wrong-digest-1234567890.html": "//example.com/article.html",
            "details/traversal-digest-1234567890.html": "bad article.html",
        },
    )

    assert clusters is not None
    assert [item.title.en for cluster in clusters.clusters for item in cluster.items] == ["Safe"]
    hrefs = {item.href for cluster in clusters.clusters for item in cluster.items}
    assert "javascript:" not in hrefs
    assert not any(href.startswith(("http:", "https:", "//")) for href in hrefs)
    assert not any(not href.strip() or href != href.strip() for href in hrefs)
    assert all(".." not in href.removeprefix("../details/") for href in hrefs)


def test_build_read_next_clusters_dedupes_same_article_per_cluster() -> None:
    organization = _organization(
        _group(
            "takeaways",
            "Read First",
            _card(1, title="First", detail_path="details/the-row-signal-1234567890.html"),
            _card(1, title="Duplicate", detail_path="details/the-row-signal-1234567890.html"),
        )
    )

    clusters = build_row_one_saved_article_read_next_clusters(
        _base_library(),
        organization,
        local_article_page_hrefs_by_detail_path={},
    )

    assert clusters is not None
    assert [item.title.en for item in clusters.clusters[0].items] == ["The Row signal"]
