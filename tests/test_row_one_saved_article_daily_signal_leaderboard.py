from __future__ import annotations

from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_ITEM_LIMIT,
    SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT,
    build_row_one_saved_article_daily_signal_leaderboard,
)
from fashion_radar.row_one.saved_article_signal_facets import (
    RowOneSavedArticleSignalFacetChip,
    RowOneSavedArticleSignalFacetRow,
    RowOneSavedArticleSignalFacets,
)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _chip(en: str, zh: str | None = None) -> RowOneSavedArticleSignalFacetChip:
    return RowOneSavedArticleSignalFacetChip(label=_lt(en, zh))


def _row(
    index: int,
    *,
    source_name: str = "Vogue Business",
    brands: tuple[RowOneSavedArticleSignalFacetChip, ...] = (),
    products: tuple[RowOneSavedArticleSignalFacetChip, ...] = (),
    themes: tuple[RowOneSavedArticleSignalFacetChip, ...] = (),
) -> RowOneSavedArticleSignalFacetRow:
    return RowOneSavedArticleSignalFacetRow(
        title=_lt(f"Article {index}", f"文章 {index}"),
        source_name=source_name,
        href=f"details/article-{index:010d}.html#local-article-digest",
        detail_path=f"details/article-{index:010d}.html",
        safe_card_count=2,
        brands=brands,
        products=products,
        themes=themes,
    )


def test_build_saved_article_daily_signal_leaderboard_aggregates_facet_chips() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=3,
        brand_count=3,
        product_count=3,
        theme_count=2,
        rows=(
            _row(
                1,
                brands=(_chip("The Row"),),
                products=(_chip("Margaux Bag"),),
                themes=(_chip("Products"),),
            ),
            _row(
                2,
                source_name="WWD",
                brands=(_chip("the row"),),
                products=(_chip("Alaia flats"),),
                themes=(_chip("Products"),),
            ),
            _row(
                3,
                brands=(_chip("Prada"),),
                products=(_chip("Margaux Bag"),),
            ),
        ),
    )

    leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)

    assert leaderboard is not None
    assert leaderboard.bucket_count == 3
    assert leaderboard.item_count == 5
    assert [bucket.key for bucket in leaderboard.buckets] == ["brands", "products", "themes"]
    brands = leaderboard.buckets[0]
    assert brands.title.en == "Brands"
    assert [(item.label.en, item.article_count, item.source_count) for item in brands.items] == [
        ("The Row", 2, 2),
        ("Prada", 1, 1),
    ]
    assert [support.title.en for support in brands.items[0].supports] == [
        "Article 1",
        "Article 2",
    ]
    products = leaderboard.buckets[1]
    assert [(item.label.en, item.article_count) for item in products.items] == [
        ("Margaux Bag", 2),
        ("Alaia flats", 1),
    ]
    themes = leaderboard.buckets[2]
    assert [(item.label.en, item.article_count) for item in themes.items] == [("Products", 2)]


def test_build_saved_article_daily_signal_leaderboard_omits_empty_buckets() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=1,
        brand_count=0,
        product_count=0,
        theme_count=1,
        rows=(_row(1, themes=(_chip("Read First"),)),),
    )

    leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)

    assert leaderboard is not None
    assert leaderboard.bucket_count == 1
    assert [bucket.key for bucket in leaderboard.buckets] == ["themes"]
    assert [item.label.en for item in leaderboard.buckets[0].items] == ["Read First"]


def test_build_saved_article_daily_signal_leaderboard_caps_items_by_support_order() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=6,
        brand_count=11,
        product_count=0,
        theme_count=0,
        rows=(
            _row(1, brands=(_chip("The Row"), _chip("Prada"), _chip("Alaia"))),
            _row(2, brands=(_chip("The Row"), _chip("Prada"), _chip("Miu Miu"))),
            _row(3, brands=(_chip("The Row"), _chip("Toteme"))),
            _row(4, brands=(_chip("Khaite"),)),
            _row(5, brands=(_chip("Alaia"),)),
            _row(6, brands=(_chip("Lemaire"),)),
        ),
    )

    leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)

    assert leaderboard is not None
    brands = leaderboard.buckets[0]
    assert len(brands.items) == SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_ITEM_LIMIT
    assert [item.label.en for item in brands.items] == [
        "The Row",
        "Prada",
        "Alaia",
        "Miu Miu",
        "Toteme",
    ]
    assert "Khaite" not in {item.label.en for item in brands.items}
    assert "Lemaire" not in {item.label.en for item in brands.items}


def test_build_saved_article_daily_signal_leaderboard_caps_supports_in_row_order() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=5,
        brand_count=5,
        product_count=0,
        theme_count=0,
        rows=tuple(_row(index, brands=(_chip("The Row"),)) for index in range(1, 6)),
    )

    leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)

    assert leaderboard is not None
    item = leaderboard.buckets[0].items[0]
    assert item.article_count == 5
    assert len(item.supports) == SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT
    assert [support.title.en for support in item.supports] == [
        "Article 1",
        "Article 2",
        "Article 3",
    ]


def test_build_saved_article_daily_signal_leaderboard_counts_unique_nonblank_sources() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=3,
        brand_count=3,
        product_count=0,
        theme_count=0,
        rows=(
            _row(1, source_name="Vogue Business", brands=(_chip("The Row"),)),
            _row(2, source_name="Vogue Business", brands=(_chip("the row"),)),
            _row(3, source_name=" ", brands=(_chip("The Row"),)),
        ),
    )

    leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)

    assert leaderboard is not None
    item = leaderboard.buckets[0].items[0]
    assert item.article_count == 3
    assert item.source_count == 1


def test_build_saved_article_daily_signal_leaderboard_counts_article_once_per_label() -> None:
    facets = RowOneSavedArticleSignalFacets(
        row_count=1,
        brand_count=2,
        product_count=0,
        theme_count=0,
        rows=(_row(1, brands=(_chip("The Row"), _chip("the row"))),),
    )

    leaderboard = build_row_one_saved_article_daily_signal_leaderboard(facets)

    assert leaderboard is not None
    item = leaderboard.buckets[0].items[0]
    assert item.article_count == 1
    assert item.source_count == 1
    assert [support.title.en for support in item.supports] == ["Article 1"]


def test_build_saved_article_daily_signal_leaderboard_omits_empty_inputs() -> None:
    assert build_row_one_saved_article_daily_signal_leaderboard(None) is None
    assert (
        build_row_one_saved_article_daily_signal_leaderboard(
            RowOneSavedArticleSignalFacets(
                row_count=0,
                brand_count=0,
                product_count=0,
                theme_count=0,
                rows=(),
            )
        )
        is None
    )
