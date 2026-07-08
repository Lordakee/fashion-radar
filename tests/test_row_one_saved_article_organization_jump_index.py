from __future__ import annotations

from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    RowOneSavedArticleDailySignalLeaderboard,
    RowOneSavedArticleDailySignalLeaderboardBucket,
    RowOneSavedArticleDailySignalLeaderboardItem,
)
from fashion_radar.row_one.saved_article_organization_jump_index import (
    SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT,
    RowOneSavedArticleOrganizationJumpIndexSourceRoute,
    build_row_one_saved_article_organization_jump_index,
)
from fashion_radar.row_one.saved_article_signal_facets import RowOneSavedArticleSignalFacets


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _card(index: int = 1) -> RowOneSavedArticleContentOrganizationCard:
    return RowOneSavedArticleContentOrganizationCard(
        title=_lt(f"Article {index}", f"文章 {index}"),
        source_name="Vogue Business",
        section_title=_lt("Top Stories", "今日重点"),
        section_label=_lt("Signal"),
        lead=_lt("Local article signal"),
        detail_path=f"details/article-{index:010d}.html#local-article-content-section-1",
        paragraph_indices=(0,),
        references=(),
    )


def _content_organization(
    count: int = 2,
) -> RowOneSavedArticleContentOrganization:
    return RowOneSavedArticleContentOrganization(
        groups=[
            RowOneSavedArticleContentOrganizationGroup(
                key=f"group-{index}",
                title=_lt(f"Group {index}", f"分组 {index}"),
                dek=_lt("Grouped local articles"),
                cards=[_card(index)],
            )
            for index in range(1, count + 1)
        ]
    )


def _source_route(
    label: str = "Vogue Business",
    *,
    href: str = "#saved-article-source-vogue-business",
    article_count: int = 2,
) -> RowOneSavedArticleOrganizationJumpIndexSourceRoute:
    return RowOneSavedArticleOrganizationJumpIndexSourceRoute(
        label=_lt(label),
        href=href,
        article_count=article_count,
    )


def _signal_facets() -> RowOneSavedArticleSignalFacets:
    return RowOneSavedArticleSignalFacets(
        row_count=2,
        brand_count=1,
        product_count=1,
        theme_count=1,
        rows=(),
    )


def _daily_signal_leaderboard() -> RowOneSavedArticleDailySignalLeaderboard:
    return RowOneSavedArticleDailySignalLeaderboard(
        bucket_count=1,
        item_count=1,
        buckets=(
            RowOneSavedArticleDailySignalLeaderboardBucket(
                key="brands",
                title=_lt("Brands", "品牌"),
                items=(
                    RowOneSavedArticleDailySignalLeaderboardItem(
                        label=_lt("The Row"),
                        article_count=2,
                        source_count=1,
                        supports=(),
                    ),
                ),
            ),
        ),
    )


def test_build_saved_article_organization_jump_index_links_existing_surfaces() -> None:
    index = build_row_one_saved_article_organization_jump_index(
        content_organization=_content_organization(),
        source_routes=(_source_route(),),
        signal_facets=_signal_facets(),
        daily_signal_leaderboard=_daily_signal_leaderboard(),
    )

    assert index is not None
    assert [group.key for group in index.groups] == ["content", "sources", "signals"]
    assert index.group_count == 3
    assert index.item_count == 4
    assert index.groups[0].items[0].href == "#saved-article-content-organization"
    assert index.groups[1].items[0].href == "#saved-article-source-vogue-business"
    assert index.groups[2].items[0].href == "#saved-article-signal-facets"
    assert index.groups[2].items[1].href == "#saved-article-daily-signal-leaderboard"
    assert index.groups[0].items[0].count_label.en == "2 content groups"
    assert index.groups[1].items[0].count_label.en == "2 articles"
    assert index.groups[2].items[0].count_label.en == "2 article rows"


def test_build_saved_article_organization_jump_index_caps_source_items() -> None:
    index = build_row_one_saved_article_organization_jump_index(
        content_organization=None,
        source_routes=tuple(
            _source_route(
                f"Source {index}",
                href=f"#saved-article-source-source-{index}",
                article_count=index,
            )
            for index in range(1, 7)
        ),
        signal_facets=None,
        daily_signal_leaderboard=None,
    )

    assert index is not None
    assert [group.key for group in index.groups] == ["sources"]
    assert len(index.groups[0].items) == SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT
    assert [item.label.en for item in index.groups[0].items] == [
        "Source 1",
        "Source 2",
        "Source 3",
        "Source 4",
    ]


def test_build_saved_article_organization_jump_index_omits_empty_inputs() -> None:
    assert (
        build_row_one_saved_article_organization_jump_index(
            content_organization=None,
            source_routes=(),
            signal_facets=None,
            daily_signal_leaderboard=None,
        )
        is None
    )


def test_build_saved_article_organization_jump_index_omits_empty_groups() -> None:
    index = build_row_one_saved_article_organization_jump_index(
        content_organization=None,
        source_routes=(),
        signal_facets=None,
        daily_signal_leaderboard=_daily_signal_leaderboard(),
    )

    assert index is not None
    assert [group.key for group in index.groups] == ["signals"]
    assert [item.href for item in index.groups[0].items] == [
        "#saved-article-daily-signal-leaderboard"
    ]


def test_build_saved_article_organization_jump_index_filters_unsafe_source_hrefs() -> None:
    index = build_row_one_saved_article_organization_jump_index(
        content_organization=None,
        source_routes=(
            _source_route("Unsafe", href="https://example.com/saved-article-source"),
            _source_route("Wrong namespace", href="#saved-article-source-routes"),
            _source_route("Safe", href="#saved-article-source-safe"),
        ),
        signal_facets=None,
        daily_signal_leaderboard=None,
    )

    assert index is not None
    assert [item.label.en for item in index.groups[0].items] == ["Safe"]
    assert all(item.href.startswith("#") for group in index.groups for item in group.items)
    assert not any("http" in item.href for group in index.groups for item in group.items)
