from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneDailyLocalIntelligenceItem,
    RowOneDailyLocalIntelligenceSection,
    RowOneDailyLocalIntelligenceSegment,
    RowOneDailyLocalIntelligenceSegmentItem,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)

MAX_STRONGEST_READS = 4
MAX_REFERENCE_ITEMS = 6
MAX_HEAT_MOVERS = 5
MAX_SEGMENTS_PER_ITEM = 4
MAX_SEGMENT_ITEMS = 3


@dataclass
class _ReferenceAggregate:
    display_name: str
    stories: set[str] = field(default_factory=set)
    articles: set[str] = field(default_factory=set)
    source_names: list[str] = field(default_factory=list)
    evidence_count: int = 0
    heat_delta: int | None = None
    references: list[RowOneReference] = field(default_factory=list)
    body: str | None = None
    body_zh: str | None = None
    detail_path: str | None = None
    paragraph_indices: list[int] = field(default_factory=list)
    segments: list[RowOneDailyLocalIntelligenceSegment] = field(default_factory=list)
    segment_match_score: int = 0


@dataclass
class _StoryArticleAggregate:
    canonical_story: RowOneStory
    canonical_article: RowOneLocalArticle
    stories: set[str] = field(default_factory=set)
    articles: set[str] = field(default_factory=set)
    source_names: list[str] = field(default_factory=list)
    evidence_count: int = 0
    heat_delta: int | None = None
    references: list[RowOneReference] = field(default_factory=list)
    segments: list[RowOneDailyLocalIntelligenceSegment] = field(default_factory=list)


def build_row_one_local_article_intelligence(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> list[RowOneDailyLocalIntelligenceSection]:
    story_articles = [
        (story, article)
        for story in edition.stories
        if (article := local_articles_by_story_id.get(story.id)) is not None
        and _has_publishable_paragraphs(article)
    ]
    if not story_articles:
        return []

    sections = [
        _strongest_reads_section(story_articles),
        _reference_watch_section(
            "brand_watch",
            LocalizedText(zh="品牌与人物观察", en="Brand Watch"),
            LocalizedText(
                zh="根据本地保存正文整理今日出现的品牌、人物与设计师。",
                en="Brands, people, and designers organized from saved local articles.",
            ),
            story_articles,
            reference_kind="entity",
        ),
        _reference_watch_section(
            "product_watch",
            LocalizedText(zh="产品观察", en="Product Watch"),
            LocalizedText(
                zh="根据本地保存正文整理今日出现的包袋、鞋履与单品。",
                en="Bags, shoes, and products organized from saved local articles.",
            ),
            story_articles,
            reference_kind="product",
        ),
        _heat_movers_section(story_articles),
    ]
    return [section for section in sections if section.items]


def _strongest_reads_section(
    story_articles: list[tuple[RowOneStory, RowOneLocalArticle]],
) -> RowOneDailyLocalIntelligenceSection:
    sorted_articles = sorted(story_articles, key=lambda pair: _story_sort_key(pair[0]))
    items = [
        _story_article_aggregate_item(aggregate)
        for aggregate in _story_article_aggregate(sorted_articles)[:MAX_STRONGEST_READS]
    ]
    return RowOneDailyLocalIntelligenceSection(
        key="strongest_reads",
        title=LocalizedText(zh="优先阅读", en="Strongest Reads"),
        dek=LocalizedText(
            zh="今日最值得先看的本地保存正文。",
            en="The saved local article bodies worth reading first today.",
        ),
        items=items,
    )


def _reference_watch_section(
    key: str,
    title: LocalizedText,
    dek: LocalizedText,
    story_articles: list[tuple[RowOneStory, RowOneLocalArticle]],
    *,
    reference_kind: str,
) -> RowOneDailyLocalIntelligenceSection:
    aggregates: dict[str, _ReferenceAggregate] = {}
    for story, article in story_articles:
        references = _story_references(story, reference_kind=reference_kind)
        for ref in references:
            normalized = _normalize_ref_name(ref.name)
            if not normalized:
                continue
            aggregate = aggregates.setdefault(
                normalized,
                _ReferenceAggregate(display_name=ref.name.strip()),
            )
            aggregate.stories.add(story.id)
            aggregate.articles.add(article.story_id)
            aggregate.evidence_count += len(story.evidence)
            aggregate.heat_delta = _max_optional_int(aggregate.heat_delta, story.heat_delta)
            _append_unique(aggregate.source_names, article.source_name)
            _append_reference(aggregate.references, ref)
            source_text = _reference_source_text(article, ref, reference_kind=reference_kind)
            paragraph_indices = _reference_paragraph_indices(
                article,
                ref,
                reference_kind=reference_kind,
            )
            segments = _reference_segments(article, ref, reference_kind=reference_kind)
            segment_match_score = _reference_segment_match_score(segments, ref)
            if aggregate.body is None or segment_match_score > aggregate.segment_match_score:
                aggregate.body = source_text.en
                aggregate.body_zh = source_text.zh
                aggregate.paragraph_indices = paragraph_indices
                aggregate.segments = segments
                aggregate.segment_match_score = segment_match_score
                aggregate.detail_path = _local_article_detail_path(story.detail_path)
            elif aggregate.detail_path is None:
                aggregate.detail_path = _local_article_detail_path(story.detail_path)

    items = [_aggregate_item(aggregate) for aggregate in aggregates.values()]
    items.sort(key=_reference_item_sort_key)
    return RowOneDailyLocalIntelligenceSection(
        key=key,
        title=title,
        dek=dek,
        items=items[:MAX_REFERENCE_ITEMS],
    )


def _heat_movers_section(
    story_articles: list[tuple[RowOneStory, RowOneLocalArticle]],
) -> RowOneDailyLocalIntelligenceSection:
    heat_articles = [
        (story, article)
        for story, article in story_articles
        if isinstance(story.heat_delta, int) and story.heat_delta > 0
    ]
    heat_articles.sort(key=lambda pair: _story_sort_key(pair[0]))
    items = [
        _story_article_aggregate_item(aggregate)
        for aggregate in _story_article_aggregate(heat_articles)[:MAX_HEAT_MOVERS]
    ]
    return RowOneDailyLocalIntelligenceSection(
        key="heat_movers",
        title=LocalizedText(zh="热度变化", en="Heat Movers"),
        dek=LocalizedText(
            zh="今日本地来源中热度变化最明显的故事。",
            en="Stories with the strongest positive local heat movement today.",
        ),
        items=items,
    )


def _story_article_aggregate(
    story_articles: list[tuple[RowOneStory, RowOneLocalArticle]],
) -> list[_StoryArticleAggregate]:
    aggregates: dict[str, _StoryArticleAggregate] = {}
    for story, article in story_articles:
        key = _story_article_cluster_key(story, article)
        aggregate = aggregates.setdefault(
            key,
            _StoryArticleAggregate(canonical_story=story, canonical_article=article),
        )
        _append_story_article_aggregate(aggregate, story, article)
    return list(aggregates.values())


def _append_story_article_aggregate(
    aggregate: _StoryArticleAggregate,
    story: RowOneStory,
    article: RowOneLocalArticle,
) -> None:
    aggregate.stories.add(story.id)
    aggregate.articles.add(article.story_id)
    aggregate.evidence_count += len(story.evidence)
    aggregate.heat_delta = _max_optional_int(aggregate.heat_delta, story.heat_delta)
    _append_unique(aggregate.source_names, article.source_name)
    for reference in [*story.entity_refs, *story.designer_refs, *story.product_refs]:
        _append_reference(aggregate.references, reference)
    if story.id == aggregate.canonical_story.id and not aggregate.segments:
        aggregate.segments = _article_segments(article)


def _story_article_cluster_key(story: RowOneStory, article: RowOneLocalArticle) -> str:
    source = _normalize_cluster_text(article.source_name)
    body = _normalize_cluster_text(_article_cluster_text(article))
    if source and body:
        return f"{source}|{body}"
    return f"{source}|{_normalize_cluster_text(article.title or '')}|{story.id}"


def _article_cluster_text(article: RowOneLocalArticle) -> str:
    paragraphs = [paragraph.strip() for paragraph in article.paragraphs if paragraph.strip()]
    if paragraphs:
        return "\n".join(paragraphs)
    bodies: list[str] = []
    for section in article.content_sections:
        for item in section.items:
            if item.body is not None and item.body.en.strip():
                bodies.append(item.body.en.strip())
    if bodies:
        return "\n".join(bodies)
    return article.title or ""


def _normalize_cluster_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _story_article_aggregate_item(
    aggregate: _StoryArticleAggregate,
) -> RowOneDailyLocalIntelligenceItem:
    story = aggregate.canonical_story
    article = aggregate.canonical_article
    takeaway = _article_takeaway(article)
    segments = aggregate.segments or _article_segments(article)
    return RowOneDailyLocalIntelligenceItem(
        title=LocalizedText(zh=story.headline, en=story.headline),
        body=takeaway.text,
        detail_path=_local_article_detail_path(story.detail_path),
        source_name=aggregate.source_names[0] if aggregate.source_names else article.source_name,
        source_names=list(aggregate.source_names),
        story_count=len(aggregate.stories),
        article_count=len(aggregate.articles),
        evidence_count=aggregate.evidence_count,
        heat_delta=aggregate.heat_delta,
        references=list(aggregate.references),
        paragraph_indices=list(takeaway.paragraph_indices),
        segments=list(segments),
    )


def _aggregate_item(aggregate: _ReferenceAggregate) -> RowOneDailyLocalIntelligenceItem:
    source_names = list(aggregate.source_names)
    source_list = ", ".join(source_names)
    body_en = (aggregate.body or "").strip()
    body_zh = (aggregate.body_zh or body_en).strip()
    if source_list:
        body_en = f"{body_en} Sources: {source_list}."
        body_zh = f"{body_zh} 来源：{source_list}。"
    return RowOneDailyLocalIntelligenceItem(
        title=LocalizedText(
            zh=aggregate.display_name,
            en=aggregate.display_name,
        ),
        body=LocalizedText(zh=body_zh, en=body_en),
        detail_path=aggregate.detail_path,
        source_name=source_names[0] if source_names else None,
        source_names=source_names,
        story_count=len(aggregate.stories),
        article_count=len(aggregate.articles),
        evidence_count=aggregate.evidence_count,
        heat_delta=aggregate.heat_delta,
        references=list(aggregate.references),
        paragraph_indices=list(aggregate.paragraph_indices),
        segments=list(aggregate.segments),
    )


def _story_references(story: RowOneStory, *, reference_kind: str) -> list[RowOneReference]:
    if reference_kind == "product":
        return list(story.product_refs)
    return [*story.entity_refs, *story.designer_refs]


def _has_publishable_paragraphs(article: RowOneLocalArticle) -> bool:
    return any(paragraph.strip() for paragraph in article.paragraphs)


def _story_sort_key(story: RowOneStory) -> tuple[int, int, str]:
    heat = story.heat_delta if isinstance(story.heat_delta, int) else 0
    return (-heat, -len(story.evidence), story.headline.casefold())


def _reference_item_sort_key(item: RowOneDailyLocalIntelligenceItem) -> tuple[int, int, int, str]:
    heat = item.heat_delta if isinstance(item.heat_delta, int) else 0
    return (-item.story_count, -item.article_count, -heat, item.title.en.casefold())


def _normalize_ref_name(name: str) -> str:
    return " ".join(name.split()).casefold()


def _max_optional_int(left: object, right: int | None) -> int | None:
    if not isinstance(right, int):
        return left if isinstance(left, int) else None
    if not isinstance(left, int):
        return right
    return max(left, right)


def _append_unique(values: list[str], value: str) -> None:
    display_value = " ".join(value.split())
    normalized = display_value.casefold()
    if normalized and all(existing.casefold() != normalized for existing in values):
        values.append(display_value)


def _append_reference(references: list[RowOneReference], ref: RowOneReference) -> None:
    normalized = (_normalize_ref_name(ref.name), ref.type.casefold())
    for index, item in enumerate(references):
        existing = (_normalize_ref_name(item.name), item.type.casefold())
        if normalized != existing:
            continue
        if _reference_display_preferred(ref, item):
            references[index] = ref
        return
    references.append(ref)


def _reference_display_preferred(candidate: RowOneReference, current: RowOneReference) -> bool:
    candidate_label = candidate.label.casefold()
    current_label = current.label.casefold()
    if candidate_label == "tracked" and current_label != "tracked":
        return True
    if candidate.name.casefold() == current.name.casefold():
        return _display_case_score(candidate.name) > _display_case_score(current.name)
    return False


def _display_case_score(value: str) -> int:
    return sum(1 for char in value if char.isupper())


class _ArticleTakeaway:
    def __init__(self, text: LocalizedText, paragraph_indices: list[int]) -> None:
        self.text = text
        self.paragraph_indices = paragraph_indices


def _article_takeaway(article: RowOneLocalArticle) -> _ArticleTakeaway:
    publishable_indices = _publishable_paragraph_indices(article)
    for section in article.content_sections:
        if section.key != "takeaways":
            continue
        for item in section.items:
            if item.body is not None and item.body.en.strip():
                return _ArticleTakeaway(
                    LocalizedText(
                        zh=item.body.zh.strip() or item.body.en.strip(),
                        en=item.body.en.strip(),
                    ),
                    _valid_article_paragraph_indices(
                        item.paragraph_indices,
                        publishable_indices,
                    ),
                )
    for index, paragraph in enumerate(article.paragraphs):
        if paragraph.strip():
            return _ArticleTakeaway(
                LocalizedText(
                    zh=_paragraph_zh(article, index, fallback=paragraph.strip()),
                    en=paragraph.strip(),
                ),
                [index],
            )
    return _ArticleTakeaway(LocalizedText(zh="", en=""), [])


def _reference_source_text(
    article: RowOneLocalArticle,
    ref: RowOneReference,
    *,
    reference_kind: str,
) -> LocalizedText:
    indices = _reference_paragraph_indices(article, ref, reference_kind=reference_kind)
    if indices:
        index = indices[0]
        if 0 <= index < len(article.paragraphs) and article.paragraphs[index].strip():
            paragraph = article.paragraphs[index].strip()
            return LocalizedText(
                zh=_paragraph_zh(article, index, fallback=paragraph),
                en=paragraph,
            )
    return _article_takeaway(article).text


def _reference_paragraph_indices(
    article: RowOneLocalArticle,
    ref: RowOneReference,
    *,
    reference_kind: str,
) -> list[int]:
    normalized = _normalize_ref_name(ref.name)
    publishable_indices = _publishable_paragraph_indices(article)
    for section in article.content_sections:
        if section.key not in _reference_segment_keys(reference_kind):
            continue
        for item in section.items:
            if any(
                _normalize_ref_name(item_ref.name) == normalized
                and item_ref.type.casefold() == ref.type.casefold()
                for item_ref in item.references
            ):
                return _valid_article_paragraph_indices(
                    item.paragraph_indices,
                    publishable_indices,
                )
    return []


def _article_segments(article: RowOneLocalArticle) -> list[RowOneDailyLocalIntelligenceSegment]:
    segments: list[RowOneDailyLocalIntelligenceSegment] = []
    publishable_indices = _publishable_paragraph_indices(article)
    for section in article.content_sections:
        segment = _content_section_segment(section, publishable_indices=publishable_indices)
        if segment is None:
            continue
        segments.append(segment)
        if len(segments) >= MAX_SEGMENTS_PER_ITEM:
            break
    return segments


def _reference_segments(
    article: RowOneLocalArticle,
    ref: RowOneReference,
    *,
    reference_kind: str,
) -> list[RowOneDailyLocalIntelligenceSegment]:
    normalized = _normalize_ref_name(ref.name)
    ref_type = ref.type.casefold()
    matched: list[RowOneDailyLocalIntelligenceSegment] = []
    publishable_indices = _publishable_paragraph_indices(article)
    for section in article.content_sections:
        if section.key not in _reference_segment_keys(reference_kind):
            continue
        segment = _content_section_segment(
            section,
            normalized_ref=normalized,
            ref_type=ref_type,
            publishable_indices=publishable_indices,
        )
        if segment is None:
            continue
        matched.append(segment)
        if len(matched) >= MAX_SEGMENTS_PER_ITEM:
            break
    if matched:
        return matched
    return _article_segments(article)[:1]


def _reference_segment_keys(reference_kind: str) -> tuple[str, ...]:
    if reference_kind == "product":
        return ("product_signals",)
    return ("entities",)


def _reference_segment_match_score(
    segments: list[RowOneDailyLocalIntelligenceSegment],
    ref: RowOneReference,
) -> int:
    normalized_name = _normalize_ref_name(ref.name)
    normalized_type = ref.type.casefold()
    for segment in segments:
        for item in segment.items:
            for item_ref in item.references:
                if (
                    _normalize_ref_name(item_ref.name) == normalized_name
                    and item_ref.type.casefold() == normalized_type
                ):
                    return 2
            if any(
                _normalize_ref_name(item_ref.name) == normalized_name
                for item_ref in item.references
            ):
                return 1
    return 0


def _content_section_segment(
    section: RowOneLocalArticleContentSection,
    *,
    normalized_ref: str | None = None,
    ref_type: str | None = None,
    publishable_indices: set[int],
) -> RowOneDailyLocalIntelligenceSegment | None:
    items: list[RowOneDailyLocalIntelligenceSegmentItem] = []
    for item in section.items:
        if (
            normalized_ref is not None
            and ref_type is not None
            and not _content_item_matches_ref(item, normalized_ref, ref_type)
        ):
            continue
        segment_item = _content_segment_item(item, publishable_indices=publishable_indices)
        if segment_item is None:
            continue
        items.append(segment_item)
        if len(items) >= MAX_SEGMENT_ITEMS:
            break
    if not items:
        return None
    return RowOneDailyLocalIntelligenceSegment(
        key=section.key,
        title=_localized_or_fallback(section.title),
        body=_optional_localized(section.body),
        items=items,
    )


def _content_segment_item(
    item: RowOneLocalArticleContentItem,
    *,
    publishable_indices: set[int],
) -> RowOneDailyLocalIntelligenceSegmentItem | None:
    body = _optional_localized(item.body)
    references = list(item.references)
    paragraph_indices = _valid_article_paragraph_indices(
        item.paragraph_indices,
        publishable_indices,
    )
    if body is None and not references and not paragraph_indices:
        return None
    return RowOneDailyLocalIntelligenceSegmentItem(
        label=_localized_or_fallback(item.label),
        body=body,
        references=references,
        paragraph_indices=paragraph_indices,
    )


def _content_item_matches_ref(
    item: RowOneLocalArticleContentItem,
    normalized_ref: str,
    ref_type: str,
) -> bool:
    return any(
        _normalize_ref_name(ref.name) == normalized_ref and ref.type.casefold() == ref_type
        for ref in item.references
    )


def _localized_or_fallback(text: LocalizedText) -> LocalizedText:
    en = text.en.strip()
    zh = text.zh.strip()
    fallback = en or zh
    return LocalizedText(zh=zh or fallback, en=en or fallback)


def _optional_localized(text: LocalizedText | None) -> LocalizedText | None:
    if text is None:
        return None
    value = _localized_or_fallback(text)
    if not value.en and not value.zh:
        return None
    return value


def _paragraph_zh(article: RowOneLocalArticle, index: int, *, fallback: str) -> str:
    if len(article.paragraphs_zh) == len(article.paragraphs):
        zh = article.paragraphs_zh[index].strip()
        if zh:
            return zh
    return fallback


def _publishable_paragraph_indices(article: RowOneLocalArticle) -> set[int]:
    return {index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}


def _valid_article_paragraph_indices(
    indices: list[int],
    publishable_indices: set[int],
) -> list[int]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in indices:
        if index not in publishable_indices or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return valid


def _local_article_detail_path(detail_path: str) -> str:
    return f"{detail_path}#local-article"
