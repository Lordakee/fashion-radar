from __future__ import annotations

from collections.abc import Mapping

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneDailyLocalIntelligenceItem,
    RowOneDailyLocalIntelligenceSection,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneReference,
    RowOneStory,
)

MAX_STRONGEST_READS = 4
MAX_REFERENCE_ITEMS = 6
MAX_HEAT_MOVERS = 5


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
        _story_article_item(story, article)
        for story, article in sorted_articles[:MAX_STRONGEST_READS]
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
    aggregates: dict[str, dict[str, object]] = {}
    for story, article in story_articles:
        references = _story_references(story, reference_kind=reference_kind)
        for ref in references:
            normalized = _normalize_ref_name(ref.name)
            if not normalized:
                continue
            aggregate = aggregates.setdefault(
                normalized,
                {
                    "display_name": ref.name.strip(),
                    "stories": set(),
                    "articles": set(),
                    "source_names": [],
                    "evidence_count": 0,
                    "heat_delta": None,
                    "references": [],
                    "body": None,
                    "body_zh": None,
                    "detail_path": None,
                    "paragraph_indices": [],
                },
            )
            aggregate["stories"].add(story.id)  # type: ignore[union-attr]
            aggregate["articles"].add(article.story_id)  # type: ignore[union-attr]
            aggregate["evidence_count"] = int(aggregate["evidence_count"]) + len(story.evidence)
            aggregate["heat_delta"] = _max_optional_int(aggregate["heat_delta"], story.heat_delta)
            _append_unique(aggregate["source_names"], article.source_name)  # type: ignore[arg-type]
            _append_reference(aggregate["references"], ref)  # type: ignore[arg-type]
            if aggregate["body"] is None:
                source_text = _reference_source_text(article, ref)
                aggregate["body"] = source_text.en
                aggregate["body_zh"] = source_text.zh
                aggregate["paragraph_indices"] = _reference_paragraph_indices(article, ref)
            if aggregate["detail_path"] is None:
                aggregate["detail_path"] = _local_article_detail_path(story.detail_path)

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
        _story_article_item(story, article) for story, article in heat_articles[:MAX_HEAT_MOVERS]
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


def _story_article_item(
    story: RowOneStory,
    article: RowOneLocalArticle,
) -> RowOneDailyLocalIntelligenceItem:
    takeaway = _article_takeaway(article)
    return RowOneDailyLocalIntelligenceItem(
        title=LocalizedText(zh=story.headline, en=story.headline),
        body=takeaway.text,
        detail_path=_local_article_detail_path(story.detail_path),
        source_name=article.source_name,
        source_names=[article.source_name],
        story_count=1,
        article_count=1,
        evidence_count=len(story.evidence),
        heat_delta=story.heat_delta,
        references=[*story.entity_refs, *story.designer_refs, *story.product_refs],
        paragraph_indices=takeaway.paragraph_indices,
    )


def _aggregate_item(aggregate: dict[str, object]) -> RowOneDailyLocalIntelligenceItem:
    source_names = list(aggregate["source_names"])
    source_list = ", ".join(source_names)
    body_en = str(aggregate["body"] or "").strip()
    body_zh = str(aggregate["body_zh"] or body_en).strip()
    if source_list:
        body_en = f"{body_en} Sources: {source_list}."
        body_zh = f"{body_zh} 来源：{source_list}。"
    return RowOneDailyLocalIntelligenceItem(
        title=LocalizedText(
            zh=str(aggregate["display_name"]),
            en=str(aggregate["display_name"]),
        ),
        body=LocalizedText(zh=body_zh, en=body_en),
        detail_path=aggregate["detail_path"] if isinstance(aggregate["detail_path"], str) else None,
        source_name=source_names[0] if source_names else None,
        source_names=source_names,
        story_count=len(aggregate["stories"]),  # type: ignore[arg-type]
        article_count=len(aggregate["articles"]),  # type: ignore[arg-type]
        evidence_count=int(aggregate["evidence_count"]),
        heat_delta=aggregate["heat_delta"] if isinstance(aggregate["heat_delta"], int) else None,
        references=list(aggregate["references"]),  # type: ignore[arg-type]
        paragraph_indices=list(aggregate["paragraph_indices"]),  # type: ignore[arg-type]
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
    normalized = value.casefold()
    if normalized and all(existing.casefold() != normalized for existing in values):
        values.append(value)


def _append_reference(references: list[RowOneReference], ref: RowOneReference) -> None:
    normalized = (_normalize_ref_name(ref.name), ref.type.casefold())
    existing = {(_normalize_ref_name(item.name), item.type.casefold()) for item in references}
    if normalized not in existing:
        references.append(ref)


class _ArticleTakeaway:
    def __init__(self, text: LocalizedText, paragraph_indices: list[int]) -> None:
        self.text = text
        self.paragraph_indices = paragraph_indices


def _article_takeaway(article: RowOneLocalArticle) -> _ArticleTakeaway:
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
                    list(item.paragraph_indices),
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


def _reference_source_text(article: RowOneLocalArticle, ref: RowOneReference) -> LocalizedText:
    indices = _reference_paragraph_indices(article, ref)
    if indices:
        index = indices[0]
        if 0 <= index < len(article.paragraphs) and article.paragraphs[index].strip():
            paragraph = article.paragraphs[index].strip()
            return LocalizedText(
                zh=_paragraph_zh(article, index, fallback=paragraph),
                en=paragraph,
            )
    return _article_takeaway(article).text


def _reference_paragraph_indices(article: RowOneLocalArticle, ref: RowOneReference) -> list[int]:
    normalized = _normalize_ref_name(ref.name)
    for section in article.content_sections:
        for item in section.items:
            if any(
                _normalize_ref_name(item_ref.name) == normalized for item_ref in item.references
            ):
                return list(item.paragraph_indices)
    return []


def _paragraph_zh(article: RowOneLocalArticle, index: int, *, fallback: str) -> str:
    if len(article.paragraphs_zh) == len(article.paragraphs):
        zh = article.paragraphs_zh[index].strip()
        if zh:
            return zh
    return fallback


def _local_article_detail_path(detail_path: str) -> str:
    return f"{detail_path}#local-article"
