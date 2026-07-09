from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.local_article_intelligence_brief import (
    RowOneLocalArticleIntelligenceBrief,
    build_row_one_local_article_intelligence_brief,
)
from fashion_radar.row_one.models import LocalizedText, RowOneEdition, RowOneLocalArticle
from fashion_radar.row_one.text import normalize_row_one_paragraph

DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES = 4
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES = 4
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE = 5
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTES = 4
DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_OPENING_CHARS = 180
_LOCAL_ARTICLE_FRAGMENT_RE = re.compile(r"local-article-(?:paragraph|content-section)-[1-9][0-9]*")


@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBriefLaneChip:
    label: LocalizedText
    support_count: int


@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBriefLane:
    key: str
    title: LocalizedText
    chips: tuple[RowOneDailyLocalArticleIntelligenceBriefLaneChip, ...]
    total_count: int


@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBriefRoute:
    label: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBriefArticle:
    title: LocalizedText
    source_name: str
    opening_signal: LocalizedText
    href: str
    evidence_count: int
    routes: tuple[RowOneDailyLocalArticleIntelligenceBriefRoute, ...]


@dataclass(frozen=True)
class RowOneDailyLocalArticleIntelligenceBrief:
    title: LocalizedText
    opening_signal: LocalizedText
    article_count: int
    source_count: int
    signal_count: int
    evidence_count: int
    lanes: tuple[RowOneDailyLocalArticleIntelligenceBriefLane, ...]
    articles: tuple[RowOneDailyLocalArticleIntelligenceBriefArticle, ...]


@dataclass(frozen=True)
class _ArticleBrief:
    story_id: str
    story_index: int
    headline: str
    page_href: str
    source_name: str
    brief: RowOneLocalArticleIntelligenceBrief


def build_row_one_daily_local_article_intelligence_brief(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalArticleIntelligenceBrief | None:
    article_briefs: list[_ArticleBrief] = []
    for story_index, story in enumerate(edition.stories):
        if not safe_local_article_story_id(story.id):
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        page_href = _safe_article_page_href(story.id, article_hrefs_by_story_id.get(story.id))
        if page_href is None:
            continue
        brief = build_row_one_local_article_intelligence_brief(
            story=story,
            local_article=article,
        )
        if brief is None:
            continue
        article_briefs.append(
            _ArticleBrief(
                story_id=story.id,
                story_index=story_index,
                headline=normalize_row_one_paragraph(story.headline),
                page_href=page_href,
                source_name=brief.source_name,
                brief=brief,
            )
        )

    article_cards = tuple(
        (article_brief, article)
        for article_brief in article_briefs
        if (article := _article_card(article_brief)) is not None
    )[:DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ARTICLES]
    articles = tuple(article for _article_brief, article in article_cards)
    if not articles:
        return None

    included_article_briefs = [article_brief for article_brief, _article in article_cards]
    lanes = _aggregate_lanes(included_article_briefs)
    signal_count = sum(lane.total_count for lane in lanes)
    evidence_count = sum(
        len(article_brief.brief.evidence) for article_brief in included_article_briefs
    )
    sources = {
        normalize_row_one_paragraph(article.source_name).casefold()
        for article in articles
        if normalize_row_one_paragraph(article.source_name)
    }
    return RowOneDailyLocalArticleIntelligenceBrief(
        title=LocalizedText(
            en="Daily Local Article Intelligence Brief",
            zh="每日文章情报摘要",
        ),
        opening_signal=_opening_signal(included_article_briefs),
        article_count=len(articles),
        source_count=len(sources),
        signal_count=signal_count,
        evidence_count=evidence_count,
        lanes=lanes,
        articles=articles,
    )


def _aggregate_lanes(
    article_briefs: list[_ArticleBrief],
) -> tuple[RowOneDailyLocalArticleIntelligenceBriefLane, ...]:
    lane_totals: dict[str, int] = {}
    lane_titles: dict[str, LocalizedText] = {}
    chip_support: dict[str, dict[str, tuple[LocalizedText, int, int]]] = {}
    for article_brief in article_briefs:
        for lane in article_brief.brief.lanes:
            lane_totals[lane.key] = lane_totals.get(lane.key, 0) + lane.total_count
            lane_titles.setdefault(lane.key, lane.title)
            chips = chip_support.setdefault(lane.key, {})
            for chip_index, chip in enumerate(lane.chips):
                key = normalize_row_one_paragraph(chip.label.en or chip.label.zh).casefold()
                if not key:
                    continue
                existing = chips.get(key)
                first_seen = article_brief.story_index * 1000 + chip_index
                if existing is None:
                    chips[key] = (chip.label, 1, first_seen)
                else:
                    label, support_count, previous_first_seen = existing
                    chips[key] = (
                        label,
                        support_count + 1,
                        min(previous_first_seen, first_seen),
                    )

    lanes: list[RowOneDailyLocalArticleIntelligenceBriefLane] = []
    for lane_key in ("brands", "products", "people", "themes"):
        if lane_key not in lane_totals:
            continue
        sorted_chips = sorted(
            chip_support.get(lane_key, {}).values(),
            key=lambda item: (-item[1], item[2], normalize_row_one_paragraph(item[0].en)),
        )
        chips = tuple(
            RowOneDailyLocalArticleIntelligenceBriefLaneChip(
                label=label,
                support_count=support_count,
            )
            for label, support_count, _ in sorted_chips[
                :DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE
            ]
        )
        if not chips:
            continue
        lanes.append(
            RowOneDailyLocalArticleIntelligenceBriefLane(
                key=lane_key,
                title=lane_titles[lane_key],
                chips=chips,
                total_count=lane_totals[lane_key],
            )
        )
        if len(lanes) >= DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES:
            break
    return tuple(lanes)


def _article_card(
    article_brief: _ArticleBrief,
) -> RowOneDailyLocalArticleIntelligenceBriefArticle | None:
    routes = _routes(article_brief)
    if not routes:
        return None
    title = normalize_row_one_paragraph(article_brief.headline) or article_brief.story_id
    return RowOneDailyLocalArticleIntelligenceBriefArticle(
        title=LocalizedText(en=title, zh=title),
        source_name=normalize_row_one_paragraph(article_brief.source_name),
        opening_signal=article_brief.brief.opening_signal,
        href=routes[0].href,
        evidence_count=len(article_brief.brief.evidence),
        routes=routes,
    )


def _routes(
    article_brief: _ArticleBrief,
) -> tuple[RowOneDailyLocalArticleIntelligenceBriefRoute, ...]:
    routes: list[RowOneDailyLocalArticleIntelligenceBriefRoute] = []
    for route in article_brief.brief.routes:
        href = _converted_href(article_brief.page_href, route.href)
        if href is None:
            continue
        routes.append(
            RowOneDailyLocalArticleIntelligenceBriefRoute(
                label=route.label,
                href=href,
            )
        )
        if len(routes) >= DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTES:
            return tuple(routes)

    for evidence in article_brief.brief.evidence:
        href = _converted_href(article_brief.page_href, evidence.href)
        if href is None:
            continue
        routes.append(
            RowOneDailyLocalArticleIntelligenceBriefRoute(
                label=evidence.label,
                href=href,
            )
        )
        if len(routes) >= DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTES:
            break
    return tuple(routes)


def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if href.startswith((".", "/", "//")):
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


def _converted_href(page_href: str, fragment_href: object) -> str | None:
    if (
        not isinstance(fragment_href, str)
        or fragment_href != fragment_href.strip()
        or not fragment_href.startswith("#")
        or any(character.isspace() for character in fragment_href)
    ):
        return None
    fragment = fragment_href[1:]
    if _LOCAL_ARTICLE_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"articles/{page_href}#{fragment}"


def _opening_signal(article_briefs: list[_ArticleBrief]) -> LocalizedText:
    for article_brief in article_briefs:
        opening = article_brief.brief.opening_signal
        en = _truncate(
            opening.en or opening.zh,
            DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_OPENING_CHARS,
        )
        zh = _truncate(
            opening.zh or opening.en,
            DAILY_LOCAL_ARTICLE_INTELLIGENCE_BRIEF_OPENING_CHARS,
        )
        if en or zh:
            return LocalizedText(en=en, zh=zh or en)
    return LocalizedText(en="", zh="")


def _truncate(value: str, limit: int) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 3)].rstrip() + "..."
