from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    row_one_saved_article_reference_bucket,
)
from fashion_radar.row_one.text import clean_row_one_text, normalize_row_one_paragraph

LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES = 4
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE = 4
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_EVIDENCE_LINKS = 4
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTE_LINKS = 4
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_EXCERPT_CHARS = 140
LOCAL_ARTICLE_INTELLIGENCE_BRIEF_SUPPORT_CHARS = 110
_REFERENCE_LANE_KEYS = ("brands", "products", "people")
_LANE_TITLES = {
    "brands": LocalizedText(en="Brands", zh="品牌"),
    "products": LocalizedText(en="Products", zh="产品"),
    "people": LocalizedText(en="People", zh="人物"),
    "themes": LocalizedText(en="Themes", zh="主题"),
}


@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceChip:
    label: LocalizedText
    href: str | None = None
    meta: str = ""


@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceLane:
    key: str
    title: LocalizedText
    chips: tuple[RowOneLocalArticleIntelligenceChip, ...]
    total_count: int


@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceEvidence:
    label: LocalizedText
    href: str
    excerpt: LocalizedText


@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceRoute:
    label: LocalizedText
    href: str
    support: LocalizedText | None


@dataclass(frozen=True)
class RowOneLocalArticleIntelligenceBrief:
    title: LocalizedText
    source_name: str
    opening_signal: LocalizedText
    lanes: tuple[RowOneLocalArticleIntelligenceLane, ...]
    evidence: tuple[RowOneLocalArticleIntelligenceEvidence, ...]
    routes: tuple[RowOneLocalArticleIntelligenceRoute, ...]


def build_row_one_local_article_intelligence_brief(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneLocalArticleIntelligenceBrief | None:
    if story.id != local_article.story_id or not safe_local_article_story_id(story.id):
        return None

    rendered_indices = _rendered_paragraph_indices(local_article)
    opening_signal = _opening_signal(story, local_article)
    lanes = _lanes(local_article)
    evidence = _evidence(local_article, set(rendered_indices))
    routes = _routes(local_article)
    if opening_signal is None and not lanes and not evidence and not routes:
        return None
    if not rendered_indices and not lanes and not routes:
        return None

    fallback_signal = opening_signal or LocalizedText(en="", zh="")
    return RowOneLocalArticleIntelligenceBrief(
        title=LocalizedText(
            en="Local Article Intelligence Brief",
            zh="本地文章情报摘要",
        ),
        source_name=normalize_row_one_paragraph(local_article.source_name)
        or normalize_row_one_paragraph(story.source_name),
        opening_signal=fallback_signal,
        lanes=lanes,
        evidence=evidence,
        routes=routes,
    )


def _opening_signal(
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> LocalizedText | None:
    for section in local_article.brief_sections:
        if section.key != "why_it_matters":
            continue
        text = _nonblank_localized_text(section.body)
        if text is not None:
            return _truncate_localized_text(
                text,
                LOCAL_ARTICLE_INTELLIGENCE_BRIEF_EXCERPT_CHARS,
            )

    story_signal = _nonblank_localized_text(story.why_it_matters)
    if story_signal is not None:
        return _truncate_localized_text(
            story_signal,
            LOCAL_ARTICLE_INTELLIGENCE_BRIEF_EXCERPT_CHARS,
        )

    for section in local_article.content_sections:
        for value in (section.body, *(item.body for item in section.items)):
            text = _nonblank_localized_text(value)
            if text is not None:
                return _truncate_localized_text(
                    text,
                    LOCAL_ARTICLE_INTELLIGENCE_BRIEF_EXCERPT_CHARS,
                )
    return None


def _lanes(
    local_article: RowOneLocalArticle,
) -> tuple[RowOneLocalArticleIntelligenceLane, ...]:
    chips_by_lane: dict[str, list[RowOneLocalArticleIntelligenceChip]] = {
        key: [] for key in (*_REFERENCE_LANE_KEYS, "themes")
    }
    totals: dict[str, int] = {key: 0 for key in chips_by_lane}
    seen_by_lane: dict[str, set[str]] = {key: set() for key in chips_by_lane}
    displayed_reference_names: set[str] = set()

    for section_position, section in enumerate(local_article.content_sections, start=1):
        section_href = _section_href(section_position)
        for item in section.items:
            for reference in item.references:
                lane_key = _reference_lane_key(reference)
                if lane_key is None:
                    continue
                label = _nonblank_reference_label(reference)
                if label is None:
                    continue
                chip_key = _normalized_key(label.en)
                if chip_key in seen_by_lane[lane_key]:
                    continue
                seen_by_lane[lane_key].add(chip_key)
                displayed_reference_names.add(chip_key)
                totals[lane_key] += 1
                if (
                    len(chips_by_lane[lane_key])
                    >= LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE
                ):
                    continue
                chips_by_lane[lane_key].append(
                    RowOneLocalArticleIntelligenceChip(
                        label=label,
                        meta=normalize_row_one_paragraph(reference.label)
                        or normalize_row_one_paragraph(reference.type),
                    )
                )

        for label in _theme_labels(section):
            label_key = _normalized_key(label.en)
            if not label_key or label_key in displayed_reference_names:
                continue
            if label_key in seen_by_lane["themes"]:
                continue
            seen_by_lane["themes"].add(label_key)
            totals["themes"] += 1
            if len(chips_by_lane["themes"]) >= LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_CHIPS_PER_LANE:
                continue
            chips_by_lane["themes"].append(
                RowOneLocalArticleIntelligenceChip(label=label, href=section_href)
            )

    lanes: list[RowOneLocalArticleIntelligenceLane] = []
    for lane_key in (*_REFERENCE_LANE_KEYS, "themes"):
        chips = tuple(chips_by_lane[lane_key])
        if not chips:
            continue
        lanes.append(
            RowOneLocalArticleIntelligenceLane(
                key=lane_key,
                title=_LANE_TITLES[lane_key],
                chips=chips,
                total_count=totals[lane_key],
            )
        )
        if len(lanes) >= LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_LANES:
            break
    return tuple(lanes)


def _evidence(
    local_article: RowOneLocalArticle,
    rendered_indices: set[int],
) -> tuple[RowOneLocalArticleIntelligenceEvidence, ...]:
    evidence: list[RowOneLocalArticleIntelligenceEvidence] = []
    seen: set[int] = set()
    for section in local_article.content_sections:
        for item in section.items:
            for index in _strict_valid_paragraph_indices(item.paragraph_indices, rendered_indices):
                if index in seen:
                    continue
                seen.add(index)
                if len(evidence) >= LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_EVIDENCE_LINKS:
                    continue
                evidence.append(_paragraph_view_model(local_article, index))
    return tuple(evidence)


def _routes(
    local_article: RowOneLocalArticle,
) -> tuple[RowOneLocalArticleIntelligenceRoute, ...]:
    routes: list[RowOneLocalArticleIntelligenceRoute] = []
    for section_position, section in enumerate(local_article.content_sections, start=1):
        route = _route(section, section_position=section_position)
        if route is None:
            continue
        routes.append(route)
        if len(routes) >= LOCAL_ARTICLE_INTELLIGENCE_BRIEF_MAX_ROUTE_LINKS:
            break
    return tuple(routes)


def _route(
    section: RowOneLocalArticleContentSection,
    *,
    section_position: int,
) -> RowOneLocalArticleIntelligenceRoute | None:
    label = _nonblank_localized_text(section.title)
    support = _route_support(section)
    has_items = any(_nonblank_localized_text(item.label) is not None for item in section.items)
    if label is None and support is None and not has_items:
        return None
    if label is None:
        label = LocalizedText(en=f"Section {section_position}", zh=f"第 {section_position} 节")
    return RowOneLocalArticleIntelligenceRoute(
        label=label,
        href=_section_href(section_position),
        support=support,
    )


def _route_support(section: RowOneLocalArticleContentSection) -> LocalizedText | None:
    for value in (
        section.body,
        *(item.body for item in section.items),
        *(item.label for item in section.items),
    ):
        text = _nonblank_localized_text(value)
        if text is not None:
            return _truncate_localized_text(
                text,
                LOCAL_ARTICLE_INTELLIGENCE_BRIEF_SUPPORT_CHARS,
            )
    return None


def _theme_labels(section: RowOneLocalArticleContentSection) -> tuple[LocalizedText, ...]:
    labels: list[LocalizedText] = []
    section_title = _nonblank_localized_text(section.title)
    if section_title is not None:
        labels.append(section_title)
    for item in section.items:
        item_label = _nonblank_localized_text(item.label)
        if item_label is not None:
            labels.append(item_label)
    return tuple(labels)


def _reference_lane_key(reference: RowOneReference) -> str | None:
    bucket = row_one_saved_article_reference_bucket(reference)
    return bucket if bucket in _REFERENCE_LANE_KEYS else None


def _nonblank_reference_label(reference: RowOneReference) -> LocalizedText | None:
    name = normalize_row_one_paragraph(reference.name)
    if not name:
        return None
    return LocalizedText(en=name, zh=name)


def _rendered_paragraph_indices(article: RowOneLocalArticle) -> tuple[int, ...]:
    return tuple(index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip())


def _strict_valid_paragraph_indices(
    indices: Sequence[object],
    rendered_indices: set[int],
) -> tuple[int, ...]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if isinstance(index, bool) or not isinstance(index, int):
            continue
        if index not in rendered_indices or index in seen:
            continue
        valid.append(index)
        seen.add(index)
    return tuple(valid)


def _paragraph_view_model(
    article: RowOneLocalArticle,
    index: int,
) -> RowOneLocalArticleIntelligenceEvidence:
    paragraph_number = index + 1
    excerpt_en = _paragraph_excerpt(article.paragraphs[index])
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    has_aligned_zh = (
        aligned_zh
        and index < len(article.paragraphs_zh)
        and bool(article.paragraphs_zh[index].strip())
    )
    excerpt_zh = _paragraph_excerpt(article.paragraphs_zh[index]) if has_aligned_zh else excerpt_en
    return RowOneLocalArticleIntelligenceEvidence(
        label=LocalizedText(
            en=f"Paragraph {paragraph_number}",
            zh=f"第 {paragraph_number} 段",
        ),
        href=f"#local-article-paragraph-{paragraph_number}",
        excerpt=LocalizedText(en=excerpt_en, zh=excerpt_zh or excerpt_en),
    )


def _paragraph_excerpt(text: str) -> str:
    cleaned = " ".join(clean_row_one_text(text).split())
    if not cleaned and text.strip():
        cleaned = normalize_row_one_paragraph(text)
    return _truncate(cleaned, LOCAL_ARTICLE_INTELLIGENCE_BRIEF_EXCERPT_CHARS)


def _nonblank_localized_text(value: LocalizedText | None) -> LocalizedText | None:
    if value is None:
        return None
    en = normalize_row_one_paragraph(value.en)
    zh = normalize_row_one_paragraph(value.zh)
    if not en and not zh:
        return None
    return LocalizedText(en=en or zh, zh=zh or en)


def _truncate_localized_text(value: LocalizedText, limit: int) -> LocalizedText:
    return LocalizedText(en=_truncate(value.en, limit), zh=_truncate(value.zh, limit))


def _truncate(value: str, limit: int) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 3)].rstrip() + "..."


def _section_href(position: int) -> str:
    return f"#local-article-content-section-{position}"


def _normalized_key(value: str) -> str:
    return normalize_row_one_paragraph(value).casefold()
