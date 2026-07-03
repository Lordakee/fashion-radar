from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime
from urllib.parse import urlsplit

from fashion_radar.models.report import CandidateReport, DailyReport, EntityReport
from fashion_radar.row_one.display import display_for_section
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLink,
    RowOneSection,
    RowOneSectionKey,
    RowOneStory,
)
from fashion_radar.utils.dates import parse_datetime_utc

SECTION_CAPS: dict[RowOneSectionKey, int] = {
    "top_stories": 6,
    "brand_moves": 8,
    "celebrity_style": 8,
    "hot_products": 8,
    "rising_radar": 8,
}

PRODUCT_CANDIDATE_TYPES = {"bag", "shoe", "product"}
SECTION_DEFINITIONS: tuple[RowOneSection, ...] = (
    RowOneSection(
        key="top_stories",
        title=LocalizedText(zh="今日重点", en="Top Stories"),
        dek=LocalizedText(zh="今日最值得先看的时尚信号。", en="The fashion signals to read first."),
    ),
    RowOneSection(
        key="brand_moves",
        title=LocalizedText(zh="品牌动态", en="Brand Moves"),
        dek=LocalizedText(zh="品牌、零售与商业动作。", en="Brand, retail, and market moves."),
    ),
    RowOneSection(
        key="celebrity_style",
        title=LocalizedText(zh="明星穿搭", en="Celebrity Style"),
        dek=LocalizedText(
            zh="红毯、街拍与造型信号。",
            en="Red-carpet, street-style, and styling signals.",
        ),
    ),
    RowOneSection(
        key="hot_products",
        title=LocalizedText(zh="热门包鞋单品", en="Hot Products"),
        dek=LocalizedText(
            zh="正在升温的包、鞋和关键单品。",
            en="Rising bags, shoes, and key items.",
        ),
    ),
    RowOneSection(
        key="rising_radar",
        title=LocalizedText(zh="上升雷达", en="Rising Radar"),
        dek=LocalizedText(
            zh="值得继续观察的新词和新信号。",
            en="New terms and signals worth watching.",
        ),
    ),
)


def build_row_one_edition(
    *,
    report: DailyReport,
    recent_items: Sequence[Mapping[str, object]] | None = None,
    as_of: str | datetime | None = None,
    max_stories: int | None = None,
) -> RowOneEdition:
    edition_date = parse_datetime_utc(as_of) if as_of is not None else report.metadata.report_date
    stories: list[RowOneStory] = []

    brand_stories = _entity_stories(report.entities, entity_type="brand", section_key="brand_moves")
    celebrity_stories = _entity_stories(
        report.entities,
        entity_type="celebrity",
        section_key="celebrity_style",
    )
    product_stories = _candidate_stories(
        report.candidates,
        section_key="hot_products",
        candidate_types=PRODUCT_CANDIDATE_TYPES,
        include_matching=True,
    )
    rising_stories = _candidate_stories(
        report.candidates,
        section_key="rising_radar",
        candidate_types=PRODUCT_CANDIDATE_TYPES,
        include_matching=False,
    )
    top_stories = _top_stories(
        report=report,
        recent_items=recent_items or [],
        limit=SECTION_CAPS["top_stories"],
    )

    for section_key, section_stories in (
        ("top_stories", top_stories),
        ("brand_moves", brand_stories),
        ("celebrity_style", celebrity_stories),
        ("hot_products", product_stories),
        ("rising_radar", rising_stories),
    ):
        stories.extend(section_stories[: SECTION_CAPS[section_key]])

    if max_stories is not None:
        stories = stories[:max_stories]
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=report.metadata.generated_at,
        edition_date=edition_date,
        summary=_edition_summary(stories),
        sections=list(SECTION_DEFINITIONS),
        stories=stories,
    )


def _entity_stories(
    entities: Iterable[EntityReport],
    *,
    entity_type: str,
    section_key: RowOneSectionKey,
) -> list[RowOneStory]:
    matched = [entity for entity in entities if entity.entity_type == entity_type]
    matched.sort(
        key=lambda entity: (-entity.heat_score, entity.entity_name.casefold(), entity.entity_name)
    )
    return [_story_from_entity(entity, section_key=section_key) for entity in matched]


def _candidate_stories(
    candidates: Iterable[CandidateReport],
    *,
    section_key: RowOneSectionKey,
    candidate_types: set[str],
    include_matching: bool,
) -> list[RowOneStory]:
    matched = [
        candidate
        for candidate in candidates
        if (candidate.candidate_type in candidate_types) is include_matching
    ]
    matched.sort(
        key=lambda candidate: (-candidate.score, candidate.phrase.casefold(), candidate.phrase)
    )
    return [_story_from_candidate(candidate, section_key=section_key) for candidate in matched]


def _top_stories(
    *,
    report: DailyReport,
    recent_items: Sequence[Mapping[str, object]],
    limit: int,
) -> list[RowOneStory]:
    stories: list[RowOneStory] = []
    seen: set[str] = set()
    ranked_entities = sorted(
        report.entities,
        key=lambda entity: (-entity.heat_score, entity.entity_name.casefold(), entity.entity_name),
    )
    ranked_candidates = sorted(
        report.candidates,
        key=lambda candidate: (-candidate.score, candidate.phrase.casefold(), candidate.phrase),
    )

    def add_story(story: RowOneStory) -> None:
        if story.id in seen or len(stories) >= limit:
            return
        seen.add(story.id)
        stories.append(story)

    for entity in ranked_entities[:3]:
        add_story(_story_from_entity(entity, section_key="top_stories"))
    for candidate in ranked_candidates[:3]:
        add_story(_story_from_candidate(candidate, section_key="top_stories"))
    for item in recent_items:
        if len(stories) >= limit:
            break
        add_story(_story_from_recent_item(item, section_key="top_stories"))
    return stories


def _story_from_entity(entity: EntityReport, *, section_key: RowOneSectionKey) -> RowOneStory:
    item = entity.representative_items[0] if entity.representative_items else None
    source_name = item.source_name if item is not None else "Fashion Radar"
    source_url = _safe_url(item.source_url if item is not None else None)
    item_summary = item.summary if item is not None else None
    title = item.title if item is not None else entity.entity_name
    story_id = _story_id(section_key, title, source_url or source_name)
    editorial_takeaway, signal_context, reader_path = _entity_synthesis(
        entity,
        section_key=section_key,
    )
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        display=display_for_section(section_key),
        headline=title,
        summary=_localized_summary(item_summary or title),
        why_it_matters=LocalizedText(
            zh=(
                f"ROW ONE 将其归入{_section_title(section_key).zh}，"
                f"当前热度 {entity.heat_score:.1f}，来自 {entity.distinct_sources} 个来源。"
            ),
            en=(
                f"ROW ONE places this in {_section_title(section_key).en} with a "
                f"{entity.heat_score:.1f} heat score across {entity.distinct_sources} sources."
            ),
        ),
        editorial_takeaway=editorial_takeaway,
        signal_context=signal_context,
        reader_path=reader_path,
        source_name=source_name,
        source_url=source_url,
        published_at=item.published_at if item is not None else None,
        detail_path=f"details/{story_id}.html",
        tags=[entity.entity_type, entity.label, entity.entity_name],
        evidence=[
            RowOneLink(
                title=item.title if item is not None else title,
                url=source_url,
                source_name=source_name,
            )
        ],
    )


def _story_from_candidate(
    candidate: CandidateReport,
    *,
    section_key: RowOneSectionKey,
) -> RowOneStory:
    item = candidate.representative_items[0] if candidate.representative_items else None
    source_name = item.source_name if item is not None else "Fashion Radar"
    source_url = _safe_url(item.source_url if item is not None else None)
    item_summary = item.summary if item is not None else None
    title = item.title if item is not None else candidate.phrase
    story_id = _story_id(section_key, title, source_url or source_name)
    editorial_takeaway, signal_context, reader_path = _candidate_synthesis(
        candidate,
        section_key=section_key,
    )
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        display=display_for_section(section_key),
        headline=title,
        summary=_localized_summary(item_summary or title),
        why_it_matters=LocalizedText(
            zh=(
                f"这是一个需要继续观察的本地候选信号，得分 {candidate.score:.1f}，"
                f"来自 {candidate.distinct_sources} 个来源。"
            ),
            en=(
                f"This is a local candidate signal to keep watching, scoring "
                f"{candidate.score:.1f} across {candidate.distinct_sources} sources."
            ),
        ),
        editorial_takeaway=editorial_takeaway,
        signal_context=signal_context,
        reader_path=reader_path,
        source_name=source_name,
        source_url=source_url,
        published_at=item.published_at if item is not None else candidate.first_seen_at,
        detail_path=f"details/{story_id}.html",
        tags=[candidate.candidate_type, candidate.label, candidate.phrase],
        evidence=[
            RowOneLink(
                title=item.title if item is not None else title,
                url=source_url,
                source_name=source_name,
            )
        ],
    )


def _story_from_recent_item(
    item: Mapping[str, object],
    *,
    section_key: RowOneSectionKey,
) -> RowOneStory:
    title = _string_value(item.get("title")) or "Untitled fashion signal"
    source_name = _string_value(item.get("source_name")) or "Fashion Radar"
    source_url = _safe_url(_string_value(item.get("url")))
    summary = _string_value(item.get("summary")) or title
    story_id = _story_id(section_key, title, source_url or source_name)
    editorial_takeaway, signal_context, reader_path = _recent_item_synthesis(
        title,
        source_name=source_name,
        section_key=section_key,
    )
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        display=display_for_section(section_key),
        headline=title,
        summary=_localized_summary(summary),
        why_it_matters=LocalizedText(
            zh=f"这条来自 {source_name} 的新近信号进入今日编辑精选。",
            en=f"This recent signal from {source_name} is part of today's editorial selection.",
        ),
        editorial_takeaway=editorial_takeaway,
        signal_context=signal_context,
        reader_path=reader_path,
        source_name=source_name,
        source_url=source_url,
        published_at=_optional_datetime(item.get("collected_at")),
        detail_path=f"details/{story_id}.html",
        tags=["recent"],
        evidence=[RowOneLink(title=title, url=source_url, source_name=source_name)],
    )


def _entity_synthesis(
    entity: EntityReport,
    *,
    section_key: RowOneSectionKey,
) -> tuple[LocalizedText, LocalizedText, LocalizedText]:
    section = _section_title(section_key)
    baseline = entity.baseline_mentions
    if entity.growth_ratio is None:
        signal_context = LocalizedText(
            zh=(
                f"本地窗口记录 {entity.current_mentions} 次当前提及，对比基线 "
                f"{baseline} 次，暂无增长倍数。"
            ),
            en=(
                f"The local window shows {entity.current_mentions} current mentions versus "
                f"{baseline} baseline; growth ratio is unavailable."
            ),
        )
    else:
        growth = _growth_ratio_label(entity.growth_ratio)
        signal_context = LocalizedText(
            zh=(
                f"本地窗口记录 {entity.current_mentions} 次当前提及，对比基线 "
                f"{baseline} 次，增长倍数 {growth}。"
            ),
            en=(
                f"The local window shows {entity.current_mentions} current mentions versus "
                f"{baseline} baseline, a {growth}x growth ratio."
            ),
        )
    return (
        LocalizedText(
            zh=f"{entity.entity_name} 是今日 {section.zh} 中最值得先看的信号之一。",
            en=f"{entity.entity_name} is one of today's priority signals in {section.en}.",
        ),
        signal_context,
        LocalizedText(
            zh=f"先按 {entity.label} 标签阅读，再对照{section.zh}中的同类信号。",
            en=(
                f"Read it as a {entity.label} signal, then compare it with nearby "
                f"{section.en} stories."
            ),
        ),
    )


def _candidate_synthesis(
    candidate: CandidateReport,
    *,
    section_key: RowOneSectionKey,
) -> tuple[LocalizedText, LocalizedText, LocalizedText]:
    section = _section_title(section_key)
    baseline = candidate.baseline_mentions
    first_seen = candidate.first_seen_at.date().isoformat()
    return (
        LocalizedText(
            zh=f"{candidate.phrase} 正被 ROW ONE 归入{section.zh}观察。",
            en=f"{candidate.phrase} is being tracked by ROW ONE inside {section.en}.",
        ),
        LocalizedText(
            zh=(
                f"本地窗口记录 {candidate.current_mentions} 次当前提及，对比基线 "
                f"{baseline} 次，首次出现于 {first_seen}。"
            ),
            en=(
                f"The local window shows {candidate.current_mentions} current mentions versus "
                f"{baseline} baseline, first seen on {first_seen}."
            ),
        ),
        LocalizedText(
            zh=f"把它作为 {candidate.label} 的{section.zh}线索，而不是已验证需求证明。",
            en=f"Treat it as a {candidate.label} {section.en} signal, not demand proof.",
        ),
    )


def _recent_item_synthesis(
    title: str,
    *,
    source_name: str,
    section_key: RowOneSectionKey,
) -> tuple[LocalizedText, LocalizedText, LocalizedText]:
    section = _section_title(section_key)
    return (
        LocalizedText(
            zh=f"《{title}》这条来自 {source_name} 的新近内容被纳入今日{section.zh}。",
            en=f"{title} from {source_name} is included in today's {section.en}.",
        ),
        LocalizedText(
            zh=f"这是一条来自 {source_name} 的本地保留条目，尚未额外推断市场地域或需求规模。",
            en=(
                f"This is a retained local item from {source_name}; ROW ONE does not "
                "infer market region or demand size from it."
            ),
        ),
        LocalizedText(
            zh=f"把它作为 {source_name} 的快速阅读入口，再进入原始来源核对细节。",
            en=(
                f"Use it as a fast {source_name} reading entry point, then open the "
                "original source for details."
            ),
        ),
    )


def _localized_summary(text: str) -> LocalizedText:
    normalized = _collapse_whitespace(text) or "No source summary available."
    return LocalizedText(
        zh=f"来源摘要：{normalized}",
        en=f"Original source summary: {normalized}",
    )


def _edition_summary(stories: Sequence[RowOneStory]) -> LocalizedText:
    if not stories:
        return LocalizedText(
            zh="暂无 ROW ONE 故事。请先运行采集、匹配和报告流程，再生成站点。",
            en="No ROW ONE stories yet. Run collect, match, and report before building the site.",
        )
    return LocalizedText(
        zh=f"ROW ONE 今日整理了 {len(stories)} 条本地时尚信号。",
        en=f"ROW ONE organized {len(stories)} local fashion signals for today.",
    )


def _section_title(section_key: RowOneSectionKey) -> LocalizedText:
    for section in SECTION_DEFINITIONS:
        if section.key == section_key:
            return section.title
    return LocalizedText(zh="ROW ONE", en="ROW ONE")


def _story_id(section_key: RowOneSectionKey, title: str, discriminator: str) -> str:
    slug = _slug(title) or "story"
    digest = hashlib.sha1(f"{section_key}|{title}|{discriminator}".encode()).hexdigest()
    return f"{slug}-{digest[:10]}"


def _slug(value: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug[:64].strip("-")


def _safe_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return url


def _string_value(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return _collapse_whitespace(value)


def _collapse_whitespace(value: str) -> str:
    return " ".join(value.split())


def _optional_datetime(value: object) -> datetime | None:
    if isinstance(value, (str, datetime)):
        return parse_datetime_utc(value)
    return None


def _growth_ratio_label(value: float | None) -> str:
    return f"{value:.1f}" if value is not None else "n/a"
