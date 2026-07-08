from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
)
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    RowOneSavedArticleDailySignalLeaderboard,
)
from fashion_radar.row_one.saved_article_signal_facets import RowOneSavedArticleSignalFacets

SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_GROUP_LIMIT = 3
SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT = 4


@dataclass(frozen=True)
class RowOneSavedArticleOrganizationJumpIndexSourceRoute:
    label: LocalizedText
    href: str
    article_count: int


@dataclass(frozen=True)
class RowOneSavedArticleOrganizationJumpIndexItem:
    label: LocalizedText
    href: str
    count_label: LocalizedText


@dataclass(frozen=True)
class RowOneSavedArticleOrganizationJumpIndexGroup:
    key: str
    title: LocalizedText
    items: tuple[RowOneSavedArticleOrganizationJumpIndexItem, ...]


@dataclass(frozen=True)
class RowOneSavedArticleOrganizationJumpIndex:
    group_count: int
    item_count: int
    groups: tuple[RowOneSavedArticleOrganizationJumpIndexGroup, ...]


def build_row_one_saved_article_organization_jump_index(
    *,
    content_organization: RowOneSavedArticleContentOrganization | None,
    source_routes: Sequence[RowOneSavedArticleOrganizationJumpIndexSourceRoute],
    signal_facets: RowOneSavedArticleSignalFacets | None,
    daily_signal_leaderboard: RowOneSavedArticleDailySignalLeaderboard | None,
) -> RowOneSavedArticleOrganizationJumpIndex | None:
    groups = tuple(
        group
        for group in (
            _content_group(content_organization),
            _sources_group(source_routes),
            _signals_group(signal_facets, daily_signal_leaderboard),
        )
        if group is not None and group.items
    )[:SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_GROUP_LIMIT]
    if not groups:
        return None
    return RowOneSavedArticleOrganizationJumpIndex(
        group_count=len(groups),
        item_count=sum(len(group.items) for group in groups),
        groups=groups,
    )


def _content_group(
    content_organization: RowOneSavedArticleContentOrganization | None,
) -> RowOneSavedArticleOrganizationJumpIndexGroup | None:
    if content_organization is None or not content_organization.groups:
        return None
    group_count = len(content_organization.groups)
    return RowOneSavedArticleOrganizationJumpIndexGroup(
        key="content",
        title=LocalizedText(en="Content", zh="内容"),
        items=(
            RowOneSavedArticleOrganizationJumpIndexItem(
                label=LocalizedText(en="Content Organization", zh="内容组织"),
                href="#saved-article-content-organization",
                count_label=LocalizedText(
                    en=_count_label(group_count, "content group", "content groups"),
                    zh=f"{group_count} 个内容分组",
                ),
            ),
        ),
    )


def _sources_group(
    source_routes: Sequence[RowOneSavedArticleOrganizationJumpIndexSourceRoute],
) -> RowOneSavedArticleOrganizationJumpIndexGroup | None:
    items = tuple(
        RowOneSavedArticleOrganizationJumpIndexItem(
            label=route.label,
            href=route.href,
            count_label=LocalizedText(
                en=_count_label(route.article_count, "article", "articles"),
                zh=f"{route.article_count} 篇文章",
            ),
        )
        for route in source_routes
        if _safe_source_route_href(route.href)
    )[:SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT]
    if not items:
        return None
    return RowOneSavedArticleOrganizationJumpIndexGroup(
        key="sources",
        title=LocalizedText(en="Sources", zh="来源"),
        items=items,
    )


def _signals_group(
    signal_facets: RowOneSavedArticleSignalFacets | None,
    daily_signal_leaderboard: RowOneSavedArticleDailySignalLeaderboard | None,
) -> RowOneSavedArticleOrganizationJumpIndexGroup | None:
    items: list[RowOneSavedArticleOrganizationJumpIndexItem] = []
    if signal_facets is not None and signal_facets.row_count > 0:
        items.append(
            RowOneSavedArticleOrganizationJumpIndexItem(
                label=LocalizedText(en="Signal Facets", zh="信号切面"),
                href="#saved-article-signal-facets",
                count_label=LocalizedText(
                    en=_count_label(signal_facets.row_count, "article row", "article rows"),
                    zh=f"{signal_facets.row_count} 个文章行",
                ),
            )
        )
    if daily_signal_leaderboard is not None and daily_signal_leaderboard.item_count > 0:
        items.append(
            RowOneSavedArticleOrganizationJumpIndexItem(
                label=LocalizedText(en="Daily Signal Leaderboard", zh="每日信号榜"),
                href="#saved-article-daily-signal-leaderboard",
                count_label=LocalizedText(
                    en=_count_label(daily_signal_leaderboard.item_count, "signal", "signals"),
                    zh=f"{daily_signal_leaderboard.item_count} 个信号",
                ),
            )
        )
    capped = tuple(items[:SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT])
    if not capped:
        return None
    return RowOneSavedArticleOrganizationJumpIndexGroup(
        key="signals",
        title=LocalizedText(en="Signals", zh="信号"),
        items=capped,
    )


def _safe_source_route_href(href: str) -> bool:
    return (
        href.startswith("#saved-article-source-")
        and href != "#saved-article-source-routes"
        and "://" not in href
        and not any(character.isspace() for character in href)
    )


def _count_label(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"
