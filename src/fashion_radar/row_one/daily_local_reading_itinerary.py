from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.body_source_labels import row_one_body_source_label
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

DAILY_LOCAL_READING_ITINERARY_MAX_SKIM_CARDS = 4
DAILY_LOCAL_READING_ITINERARY_MAX_EVIDENCE_CHIPS = 6
DAILY_LOCAL_READING_ITINERARY_MAX_LABELS_PER_CARD = 4
DAILY_LOCAL_READING_ITINERARY_EXCERPT_CHARS = 170


@dataclass(frozen=True)
class RowOneDailyLocalReadingItineraryCard:
    title: LocalizedText
    source_name: str
    reason: LocalizedText
    excerpt: LocalizedText
    href: str
    labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class RowOneDailyLocalReadingItineraryEvidence:
    label: str
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalReadingItinerary:
    title: LocalizedText
    dek: LocalizedText
    selected_count: int
    source_count: int
    evidence_count: int
    start_here: RowOneDailyLocalReadingItineraryCard | None
    skim_next: tuple[RowOneDailyLocalReadingItineraryCard, ...]
    evidence_trail: tuple[RowOneDailyLocalReadingItineraryEvidence, ...]


_BRAND_PEOPLE_TERMS = frozenset(
    {
        "brand",
        "brands",
        "designer",
        "designers",
        "person",
        "people",
        "celebrity",
        "celebrities",
        "entity",
        "entities",
        "talent",
    }
)
_PRODUCT_TERMS = frozenset(
    {
        "accessory",
        "apparel",
        "bag",
        "bags",
        "boot",
        "boots",
        "dress",
        "handbag",
        "handbags",
        "product",
        "products",
        "shoe",
        "shoes",
        "sneaker",
        "sneakers",
    }
)
_BRAND_PEOPLE_SECTION_TERMS = ("brand", "people", "person", "designer", "celebrity", "entit")
_PRODUCT_SECTION_TERMS = ("product", "bag", "shoe", "accessory", "apparel")


def build_row_one_daily_local_reading_itinerary(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalReadingItinerary | None:
    start_here: RowOneDailyLocalReadingItineraryCard | None = None
    skim_next: list[RowOneDailyLocalReadingItineraryCard] = []
    evidence_trail: list[RowOneDailyLocalReadingItineraryEvidence] = []
    seen_card_keys: set[tuple[str, str]] = set()
    seen_evidence_keys: set[tuple[str, str]] = set()

    for story in edition.stories:
        if not safe_local_article_story_id(story.id):
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        page_href = _safe_article_page_href(story.id, article_hrefs_by_story_id.get(story.id))
        if page_href is None:
            continue

        title = _article_title(story.headline, article.title, story.id)
        source_name = _source_name(article, story.source_name)

        if start_here is None:
            start_here = _start_here_card(
                article,
                title=title,
                source_name=source_name,
                page_href=page_href,
            )
            if start_here is not None:
                _record_card(
                    start_here,
                    seen_card_keys=seen_card_keys,
                )

        for section_position, section in enumerate(article.content_sections, start=1):
            section_href = f"articles/{page_href}#local-article-content-section-{section_position}"
            for item in section.items:
                reason = _reason_for_item(item, section.key)
                if reason is None:
                    continue
                excerpt = _item_excerpt(item, section, article)
                if excerpt is None:
                    continue
                card = RowOneDailyLocalReadingItineraryCard(
                    title=title,
                    source_name=source_name,
                    reason=reason,
                    excerpt=excerpt,
                    href=section_href,
                    labels=_labels(item.references),
                )
                _add_evidence(
                    evidence_trail,
                    RowOneDailyLocalReadingItineraryEvidence(
                        label=_evidence_label(item, section, article.title),
                        href=section_href,
                    ),
                    seen_evidence_keys,
                )
                if not _add_skim_card(
                    skim_next,
                    card,
                    seen_card_keys=seen_card_keys,
                ):
                    continue

        source_context = _source_context_card(
            article,
            title=title,
            source_name=source_name,
            page_href=page_href,
        )
        if source_context is not None and _add_source_context_card(
            skim_next,
            source_context,
            seen_card_keys=seen_card_keys,
        ):
            _add_evidence(
                evidence_trail,
                RowOneDailyLocalReadingItineraryEvidence(
                    label=source_name or title.en,
                    href=source_context.href,
                ),
                seen_evidence_keys,
            )

    if start_here is None and not skim_next:
        return None
    evidence = tuple(evidence_trail[:DAILY_LOCAL_READING_ITINERARY_MAX_EVIDENCE_CHIPS])
    return RowOneDailyLocalReadingItinerary(
        title=LocalizedText(en="Daily Local Reading Itinerary", zh="每日本地阅读路径"),
        dek=LocalizedText(
            en="A short path through today's saved local articles.",
            zh="用一条短路径读完今日保存本地文章。",
        ),
        selected_count=_selected_story_count(start_here, skim_next),
        source_count=_selected_source_count(start_here, skim_next),
        evidence_count=len(evidence),
        start_here=start_here,
        skim_next=tuple(skim_next[:DAILY_LOCAL_READING_ITINERARY_MAX_SKIM_CARDS]),
        evidence_trail=evidence,
    )


def _record_card(
    card: RowOneDailyLocalReadingItineraryCard,
    *,
    seen_card_keys: set[tuple[str, str]],
) -> None:
    seen_card_keys.add(_card_key(card))


def _add_skim_card(
    cards: list[RowOneDailyLocalReadingItineraryCard],
    card: RowOneDailyLocalReadingItineraryCard,
    *,
    seen_card_keys: set[tuple[str, str]],
) -> bool:
    if len(cards) >= DAILY_LOCAL_READING_ITINERARY_MAX_SKIM_CARDS:
        return False
    key = _card_key(card)
    if key in seen_card_keys:
        return False
    _record_card(
        card,
        seen_card_keys=seen_card_keys,
    )
    cards.append(card)
    return True


def _add_source_context_card(
    cards: list[RowOneDailyLocalReadingItineraryCard],
    card: RowOneDailyLocalReadingItineraryCard,
    *,
    seen_card_keys: set[tuple[str, str]],
) -> bool:
    if _add_skim_card(
        cards,
        card,
        seen_card_keys=seen_card_keys,
    ):
        return True
    key = _card_key(card)
    if key in seen_card_keys:
        return False
    for index in range(len(cards) - 1, -1, -1):
        if normalize_row_one_paragraph(cards[index].reason.en).casefold() == "source context":
            continue
        seen_card_keys.discard(_card_key(cards[index]))
        cards[index] = card
        _record_card(
            card,
            seen_card_keys=seen_card_keys,
        )
        return True
    return False


def _card_key(card: RowOneDailyLocalReadingItineraryCard) -> tuple[str, str]:
    return (card.href, normalize_row_one_paragraph(card.reason.en).casefold())


def _add_evidence(
    evidence_trail: list[RowOneDailyLocalReadingItineraryEvidence],
    evidence: RowOneDailyLocalReadingItineraryEvidence,
    seen_evidence_keys: set[tuple[str, str]],
) -> None:
    if len(evidence_trail) >= DAILY_LOCAL_READING_ITINERARY_MAX_EVIDENCE_CHIPS:
        return
    label = normalize_row_one_paragraph(evidence.label)
    if not label:
        return
    key = (evidence.href, label.casefold())
    if key in seen_evidence_keys:
        return
    seen_evidence_keys.add(key)
    evidence_trail.append(RowOneDailyLocalReadingItineraryEvidence(label=label, href=evidence.href))


def _start_here_card(
    article: RowOneLocalArticle,
    *,
    title: LocalizedText,
    source_name: str,
    page_href: str,
) -> RowOneDailyLocalReadingItineraryCard | None:
    anchor = _first_paragraph_anchor(article, page_href)
    if anchor is None:
        return None
    for brief in article.brief_sections:
        excerpt = _localized_excerpt(brief.body.en, brief.body.zh)
        if excerpt is not None:
            return RowOneDailyLocalReadingItineraryCard(
                title=title,
                source_name=source_name,
                reason=LocalizedText(en="Start Here", zh="先读这篇"),
                excerpt=excerpt,
                href=anchor,
            )
    paragraph = _first_paragraph(article)
    if paragraph is None:
        return None
    _, paragraph_en, paragraph_zh = paragraph
    excerpt = _localized_excerpt(paragraph_en, paragraph_zh)
    if excerpt is None:
        return None
    return RowOneDailyLocalReadingItineraryCard(
        title=title,
        source_name=source_name,
        reason=LocalizedText(en="Start Here", zh="先读这篇"),
        excerpt=excerpt,
        href=anchor,
    )


def _source_context_card(
    article: RowOneLocalArticle,
    *,
    title: LocalizedText,
    source_name: str,
    page_href: str,
) -> RowOneDailyLocalReadingItineraryCard | None:
    paragraph = _first_paragraph(article)
    if paragraph is None:
        return None
    paragraph_index, _, _ = paragraph
    body_source = row_one_body_source_label(article.body_source)
    source_display = source_name or "Saved source"
    zh_source_display = source_name or "保存来源"
    paragraph_count = len(
        [paragraph for paragraph in article.paragraphs if normalize_row_one_paragraph(paragraph)]
    )
    excerpt = _localized_excerpt(
        (
            f"{body_source.en} from {source_display}; "
            f"{paragraph_count} local paragraphs are available for same-site reading."
        ),
        (
            f"{body_source.zh}，来源为 {zh_source_display}；"
            f"已有 {paragraph_count} 段本地正文可在站内阅读。"
        ),
    )
    if excerpt is None:
        return None
    return RowOneDailyLocalReadingItineraryCard(
        title=title,
        source_name=source_name,
        reason=LocalizedText(en="Source context", zh="来源语境"),
        excerpt=excerpt,
        href=f"articles/{page_href}#local-article-paragraph-{paragraph_index + 1}",
        labels=(source_display,),
    )


def _first_paragraph_anchor(article: RowOneLocalArticle, page_href: str) -> str | None:
    paragraph = _first_paragraph(article)
    if paragraph is None:
        return None
    paragraph_index, _, _ = paragraph
    return f"articles/{page_href}#local-article-paragraph-{paragraph_index + 1}"


def _first_paragraph(article: RowOneLocalArticle) -> tuple[int, str, str] | None:
    for index, paragraph in enumerate(article.paragraphs):
        paragraph_en = normalize_row_one_paragraph(paragraph)
        if not paragraph_en:
            continue
        paragraph_zh = (
            normalize_row_one_paragraph(article.paragraphs_zh[index])
            if index < len(article.paragraphs_zh)
            else paragraph_en
        )
        return index, paragraph_en, paragraph_zh or paragraph_en
    return None


def _item_excerpt(
    item: RowOneLocalArticleContentItem,
    section: RowOneLocalArticleContentSection,
    article: RowOneLocalArticle,
) -> LocalizedText | None:
    if item.body is not None:
        excerpt = _localized_excerpt(item.body.en, item.body.zh)
        if excerpt is not None:
            return excerpt
    indexed = _indexed_paragraph_excerpt(item, article)
    if indexed is not None:
        return indexed
    if section.body is not None:
        return _localized_excerpt(section.body.en, section.body.zh)
    return None


def _indexed_paragraph_excerpt(
    item: RowOneLocalArticleContentItem,
    article: RowOneLocalArticle,
) -> LocalizedText | None:
    seen: set[int] = set()
    for paragraph_index in item.paragraph_indices:
        if isinstance(paragraph_index, bool) or not isinstance(paragraph_index, int):
            continue
        if paragraph_index < 0 or paragraph_index in seen:
            continue
        seen.add(paragraph_index)
        if paragraph_index >= len(article.paragraphs):
            continue
        paragraph_en = normalize_row_one_paragraph(article.paragraphs[paragraph_index])
        if not paragraph_en:
            continue
        paragraph_zh = (
            normalize_row_one_paragraph(article.paragraphs_zh[paragraph_index])
            if paragraph_index < len(article.paragraphs_zh)
            else paragraph_en
        )
        return _localized_excerpt(paragraph_en, paragraph_zh or paragraph_en)
    return None


def _reason_for_item(
    item: RowOneLocalArticleContentItem,
    section_key: str,
) -> LocalizedText | None:
    section_key_normalized = section_key.casefold()
    is_product_section = any(term in section_key_normalized for term in _PRODUCT_SECTION_TERMS)
    if is_product_section or _has_reference_term(item.references, _PRODUCT_TERMS):
        return LocalizedText(en="Product signal", zh="单品信号")
    if any(
        term in section_key_normalized for term in _BRAND_PEOPLE_SECTION_TERMS
    ) or _has_reference_term(item.references, _BRAND_PEOPLE_TERMS):
        return LocalizedText(en="Brand / people signal", zh="品牌 / 人物信号")
    return None


def _has_reference_term(references: tuple[RowOneReference, ...], terms: frozenset[str]) -> bool:
    for reference in references:
        values = (
            normalize_row_one_paragraph(reference.type).casefold(),
            normalize_row_one_paragraph(reference.label).casefold(),
        )
        if any(value in terms for value in values):
            return True
    return False


def _labels(references: tuple[RowOneReference, ...]) -> tuple[str, ...]:
    labels: list[str] = []
    seen: set[str] = set()
    for reference in references:
        name = normalize_row_one_paragraph(reference.name)
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        labels.append(name)
        if len(labels) >= DAILY_LOCAL_READING_ITINERARY_MAX_LABELS_PER_CARD:
            break
    return tuple(labels)


def _evidence_label(
    item: RowOneLocalArticleContentItem,
    section: RowOneLocalArticleContentSection,
    article_title: str | None,
) -> str:
    for reference in item.references:
        if name := normalize_row_one_paragraph(reference.name):
            return name
    if label := normalize_row_one_paragraph(item.label.en):
        return label
    if section_title := normalize_row_one_paragraph(section.title.en):
        return section_title
    return normalize_row_one_paragraph(article_title or "") or "Paragraph 1"


def _article_title(story_headline: str, article_title: str | None, story_id: str) -> LocalizedText:
    title = normalize_row_one_paragraph(article_title or "") or normalize_row_one_paragraph(
        story_headline
    )
    if not title:
        title = story_id
    return LocalizedText(en=title, zh=title)


def _selected_story_count(
    start_here: RowOneDailyLocalReadingItineraryCard | None,
    skim_next: list[RowOneDailyLocalReadingItineraryCard],
) -> int:
    story_ids = {
        story_id
        for card in ([start_here] if start_here is not None else []) + list(skim_next)
        if (story_id := _story_id_from_card_href(card.href))
    }
    return len(story_ids)


def _selected_source_count(
    start_here: RowOneDailyLocalReadingItineraryCard | None,
    skim_next: list[RowOneDailyLocalReadingItineraryCard],
) -> int:
    source_names = {
        source_name.casefold()
        for card in ([start_here] if start_here is not None else []) + list(skim_next)
        if (source_name := normalize_row_one_paragraph(card.source_name))
    }
    return len(source_names)


def _story_id_from_card_href(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    route_path = PurePosixPath(path)
    if len(route_path.parts) != 2 or route_path.parts[0] != "articles":
        return None
    story_id = route_path.name.removesuffix(".html")
    return story_id if safe_local_article_story_id(story_id) else None


def _source_name(article: RowOneLocalArticle, story_source_name: str) -> str:
    return (
        normalize_row_one_paragraph(article.source_name)
        or normalize_row_one_paragraph(story_source_name)
        or "Saved source"
    )


def _localized_excerpt(en: str, zh: str) -> LocalizedText | None:
    excerpt_en = _truncate(normalize_row_one_paragraph(en))
    excerpt_zh = _truncate(normalize_row_one_paragraph(zh))
    if not excerpt_en and not excerpt_zh:
        return None
    return LocalizedText(en=excerpt_en or excerpt_zh, zh=excerpt_zh or excerpt_en)


def _truncate(value: str) -> str:
    if len(value) <= DAILY_LOCAL_READING_ITINERARY_EXCERPT_CHARS:
        return value
    return value[: DAILY_LOCAL_READING_ITINERARY_EXCERPT_CHARS - 3].rstrip() + "..."


def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if "://" in href or "//" in href or href.startswith((".", "/", "//")):
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
