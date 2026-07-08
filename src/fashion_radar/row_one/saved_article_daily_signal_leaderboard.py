from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_signal_facets import (
    RowOneSavedArticleSignalFacetChip,
    RowOneSavedArticleSignalFacetRow,
    RowOneSavedArticleSignalFacets,
)

SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_ITEM_LIMIT = 5
SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT = 3


@dataclass(frozen=True)
class RowOneSavedArticleDailySignalLeaderboardSupport:
    title: LocalizedText
    source_name: str
    href: str
    detail_path: str


@dataclass(frozen=True)
class RowOneSavedArticleDailySignalLeaderboardItem:
    label: LocalizedText
    article_count: int
    source_count: int
    supports: tuple[RowOneSavedArticleDailySignalLeaderboardSupport, ...]


@dataclass(frozen=True)
class RowOneSavedArticleDailySignalLeaderboardBucket:
    key: str
    title: LocalizedText
    items: tuple[RowOneSavedArticleDailySignalLeaderboardItem, ...]


@dataclass(frozen=True)
class RowOneSavedArticleDailySignalLeaderboard:
    bucket_count: int
    item_count: int
    buckets: tuple[RowOneSavedArticleDailySignalLeaderboardBucket, ...]


@dataclass
class _LeaderboardItemDraft:
    label: LocalizedText
    first_seen_index: int
    article_keys: set[str]
    source_names: set[str]
    supports: list[RowOneSavedArticleDailySignalLeaderboardSupport]


def build_row_one_saved_article_daily_signal_leaderboard(
    facets: RowOneSavedArticleSignalFacets | None,
) -> RowOneSavedArticleDailySignalLeaderboard | None:
    if facets is None or not facets.rows:
        return None

    buckets = tuple(
        bucket
        for bucket in (
            _build_leaderboard_bucket(
                "brands",
                LocalizedText(en="Brands", zh="品牌"),
                facets.rows,
            ),
            _build_leaderboard_bucket(
                "products",
                LocalizedText(en="Products", zh="产品"),
                facets.rows,
            ),
            _build_leaderboard_bucket(
                "themes",
                LocalizedText(en="Themes", zh="主题"),
                facets.rows,
            ),
        )
        if bucket is not None
    )
    if not buckets:
        return None
    return RowOneSavedArticleDailySignalLeaderboard(
        bucket_count=len(buckets),
        item_count=sum(len(bucket.items) for bucket in buckets),
        buckets=buckets,
    )


def _build_leaderboard_bucket(
    bucket_key: str,
    title: LocalizedText,
    rows: tuple[RowOneSavedArticleSignalFacetRow, ...],
) -> RowOneSavedArticleDailySignalLeaderboardBucket | None:
    drafts: dict[tuple[str, str], _LeaderboardItemDraft] = {}
    for row_index, row in enumerate(rows):
        seen_in_row: set[tuple[str, str]] = set()
        for chip in _row_chips(row, bucket_key):
            label = _clean_label(chip)
            if label is None:
                continue
            key = (label.zh.casefold(), label.en.casefold())
            if key in seen_in_row:
                continue
            seen_in_row.add(key)
            draft = drafts.get(key)
            if draft is None:
                draft = _LeaderboardItemDraft(
                    label=label,
                    first_seen_index=len(drafts),
                    article_keys=set(),
                    source_names=set(),
                    supports=[],
                )
                drafts[key] = draft
            article_key = row.detail_path or row.href or f"row-{row_index}"
            draft.article_keys.add(article_key)
            source_name = " ".join(row.source_name.split())
            if source_name:
                draft.source_names.add(source_name)
            if len(draft.supports) < SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_SUPPORT_LIMIT:
                draft.supports.append(
                    RowOneSavedArticleDailySignalLeaderboardSupport(
                        title=row.title,
                        source_name=row.source_name,
                        href=row.href,
                        detail_path=row.detail_path,
                    )
                )

    items = sorted(
        (
            RowOneSavedArticleDailySignalLeaderboardItem(
                label=draft.label,
                article_count=len(draft.article_keys),
                source_count=len(draft.source_names),
                supports=tuple(draft.supports),
            )
            for draft in drafts.values()
            if draft.article_keys
        ),
        key=lambda item: (
            -item.article_count,
            drafts[(item.label.zh.casefold(), item.label.en.casefold())].first_seen_index,
            item.label.en.casefold(),
        ),
    )[:SAVED_ARTICLE_DAILY_SIGNAL_LEADERBOARD_ITEM_LIMIT]
    if not items:
        return None
    return RowOneSavedArticleDailySignalLeaderboardBucket(
        key=bucket_key,
        title=title,
        items=tuple(items),
    )


def _row_chips(
    row: RowOneSavedArticleSignalFacetRow,
    bucket_key: str,
) -> tuple[RowOneSavedArticleSignalFacetChip, ...]:
    if bucket_key == "brands":
        return row.brands
    if bucket_key == "products":
        return row.products
    if bucket_key == "themes":
        return row.themes
    return ()


def _clean_label(chip: RowOneSavedArticleSignalFacetChip) -> LocalizedText | None:
    label = LocalizedText(
        zh=" ".join(chip.label.zh.split()),
        en=" ".join(chip.label.en.split()),
    )
    if not label.zh and not label.en:
        return None
    return label
