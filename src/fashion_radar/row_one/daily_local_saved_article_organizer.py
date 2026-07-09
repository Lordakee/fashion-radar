from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
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

DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_LANES = 4
DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE = 3
DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD = 4
DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS = 180


@dataclass(frozen=True)
class RowOneDailyLocalSavedArticleOrganizerReference:
    name: str
    label: str


@dataclass(frozen=True)
class RowOneDailyLocalSavedArticleOrganizerCard:
    title: LocalizedText
    source_name: str
    lane_label: LocalizedText
    excerpt: LocalizedText
    href: str
    references: tuple[RowOneDailyLocalSavedArticleOrganizerReference, ...] = ()


@dataclass(frozen=True)
class RowOneDailyLocalSavedArticleOrganizerLane:
    key: str
    title: LocalizedText
    dek: LocalizedText
    cards: tuple[RowOneDailyLocalSavedArticleOrganizerCard, ...]
    total_count: int


@dataclass(frozen=True)
class RowOneDailyLocalSavedArticleOrganizer:
    title: LocalizedText = field(
        default_factory=lambda: LocalizedText(
            en="Daily Local Saved Article Organizer",
            zh="每日保存文章整理器",
        )
    )
    dek: LocalizedText = field(
        default_factory=lambda: LocalizedText(
            en="Short, article-backed lanes from today's saved local text.",
            zh="从今日保存本地正文整理出的短篇编辑阅读线。",
        )
    )
    article_count: int = 0
    source_count: int = 0
    card_count: int = 0
    reference_count: int = 0
    lanes: tuple[RowOneDailyLocalSavedArticleOrganizerLane, ...] = ()


_LANE_ORDER = ("read_first", "people_brands", "products", "source_context")
_LANE_TITLES = {
    "read_first": LocalizedText(en="Read First", zh="优先阅读"),
    "people_brands": LocalizedText(en="People & Brands", zh="品牌与人物"),
    "products": LocalizedText(en="Products", zh="单品"),
    "source_context": LocalizedText(en="Source Context", zh="来源语境"),
}
_LANE_DEKS = {
    "read_first": LocalizedText(
        en="The shortest route into today's saved article set.",
        zh="进入今日保存文章组的最短阅读路径。",
    ),
    "people_brands": LocalizedText(
        en="Brand, designer, celebrity, and people context pulled from saved text.",
        zh="从保存正文提取品牌、设计师、明星与人物语境。",
    ),
    "products": LocalizedText(
        en="Product evidence and item-level cues from the local articles.",
        zh="来自本地文章的单品证据与物件级线索。",
    ),
    "source_context": LocalizedText(
        en="Where the saved read came from and how ROW ONE stored the local body.",
        zh="保存阅读来自哪里，以及 ROW ONE 如何保存本地正文。",
    ),
}
_PEOPLE_BRAND_TYPES = {
    "brand",
    "celebrity",
    "creative_director",
    "designer",
    "entity",
    "founder",
    "people",
    "person",
    "retailer",
    "stylist",
}
_PRODUCT_TYPES = {
    "accessory",
    "apparel",
    "bag",
    "boot",
    "flat",
    "fragrance",
    "jewelry",
    "product",
    "shoe",
    "shoes",
    "sneaker",
    "watch",
}


def build_row_one_daily_local_saved_article_organizer(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalSavedArticleOrganizer | None:
    cards_by_lane: dict[str, list[RowOneDailyLocalSavedArticleOrganizerCard]] = {
        key: [] for key in _LANE_ORDER
    }
    totals = {key: 0 for key in _LANE_ORDER}
    seen_hrefs = {key: set[str]() for key in _LANE_ORDER}
    emitted_story_ids: set[str] = set()
    emitted_sources: set[str] = set()

    for story in edition.stories:
        if not safe_local_article_story_id(story.id):
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        page_href = _safe_article_page_href(story.id, article_hrefs_by_story_id.get(story.id))
        if page_href is None:
            continue

        article_title = _article_title(story.headline, article.title, story.id)
        source_name = _source_name(article, story.source_name)

        if _add_card(
            cards_by_lane,
            totals,
            seen_hrefs,
            "read_first",
            _read_first_card(
                article,
                title=article_title,
                source_name=source_name,
                page_href=page_href,
            ),
        ):
            _record_article(emitted_story_ids, emitted_sources, story.id, source_name)

        for section_position, section in enumerate(article.content_sections, start=1):
            section_href = f"articles/{page_href}#local-article-content-section-{section_position}"
            for item in section.items:
                lane_key = _item_lane_key(item.references, section.key)
                if lane_key is None:
                    continue
                excerpt = _item_excerpt(item, section, article)
                if excerpt is None:
                    continue
                if _add_card(
                    cards_by_lane,
                    totals,
                    seen_hrefs,
                    lane_key,
                    RowOneDailyLocalSavedArticleOrganizerCard(
                        title=article_title,
                        source_name=source_name,
                        lane_label=_clean_localized(item.label, fallback=section.title),
                        excerpt=excerpt,
                        href=section_href,
                        references=_references(item.references),
                    ),
                ):
                    _record_article(emitted_story_ids, emitted_sources, story.id, source_name)

        if _add_card(
            cards_by_lane,
            totals,
            seen_hrefs,
            "source_context",
            _source_context_card(
                article,
                title=article_title,
                source_name=source_name,
                page_href=page_href,
            ),
        ):
            _record_article(emitted_story_ids, emitted_sources, story.id, source_name)

    lanes = tuple(
        RowOneDailyLocalSavedArticleOrganizerLane(
            key=lane_key,
            title=_LANE_TITLES[lane_key],
            dek=_LANE_DEKS[lane_key],
            cards=tuple(cards_by_lane[lane_key]),
            total_count=totals[lane_key],
        )
        for lane_key in _LANE_ORDER
        if cards_by_lane[lane_key]
    )[:DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_LANES]
    if not lanes:
        return None
    return RowOneDailyLocalSavedArticleOrganizer(
        article_count=len(emitted_story_ids),
        source_count=len(emitted_sources),
        card_count=sum(len(lane.cards) for lane in lanes),
        reference_count=sum(len(card.references) for lane in lanes for card in lane.cards),
        lanes=lanes,
    )


def _record_article(
    story_ids: set[str],
    source_names: set[str],
    story_id: str,
    source_name: str,
) -> None:
    story_ids.add(story_id)
    if source_name:
        source_names.add(source_name.casefold())


def _add_card(
    cards_by_lane: dict[str, list[RowOneDailyLocalSavedArticleOrganizerCard]],
    totals: dict[str, int],
    seen_hrefs: dict[str, set[str]],
    lane_key: str,
    card: RowOneDailyLocalSavedArticleOrganizerCard | None,
) -> bool:
    if card is None:
        return False
    totals[lane_key] += 1
    if card.href in seen_hrefs[lane_key]:
        return False
    if len(cards_by_lane[lane_key]) >= DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_CARDS_PER_LANE:
        return False
    seen_hrefs[lane_key].add(card.href)
    cards_by_lane[lane_key].append(card)
    return True


def _read_first_card(
    article: RowOneLocalArticle,
    *,
    title: LocalizedText,
    source_name: str,
    page_href: str,
) -> RowOneDailyLocalSavedArticleOrganizerCard | None:
    paragraph = _first_paragraph(article)
    if paragraph is None:
        return None
    index, paragraph_en, paragraph_zh = paragraph
    for section in article.brief_sections:
        excerpt = _localized_excerpt(section.body.en, section.body.zh)
        if excerpt is not None:
            return RowOneDailyLocalSavedArticleOrganizerCard(
                title=title,
                source_name=source_name,
                lane_label=_clean_localized(section.title, fallback=_LANE_TITLES["read_first"]),
                excerpt=excerpt,
                href=f"articles/{page_href}#local-article-paragraph-{index + 1}",
            )
    excerpt = _localized_excerpt(paragraph_en, paragraph_zh)
    if excerpt is None:
        return None
    return RowOneDailyLocalSavedArticleOrganizerCard(
        title=title,
        source_name=source_name,
        lane_label=_LANE_TITLES["read_first"],
        excerpt=excerpt,
        href=f"articles/{page_href}#local-article-paragraph-{index + 1}",
    )


def _source_context_card(
    article: RowOneLocalArticle,
    *,
    title: LocalizedText,
    source_name: str,
    page_href: str,
) -> RowOneDailyLocalSavedArticleOrganizerCard | None:
    paragraph = _first_paragraph(article)
    if paragraph is None:
        return None
    index, _, _ = paragraph
    body_source = row_one_body_source_label(article.body_source)
    source_display = source_name or "Saved source"
    zh_source_display = source_name or "保存来源"
    paragraph_count = len([paragraph for paragraph in article.paragraphs if paragraph.strip()])
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
    return RowOneDailyLocalSavedArticleOrganizerCard(
        title=title,
        source_name=source_name,
        lane_label=LocalizedText(en=source_display, zh=zh_source_display),
        excerpt=excerpt,
        href=f"articles/{page_href}#local-article-paragraph-{index + 1}",
    )


def _item_excerpt(
    item: RowOneLocalArticleContentItem,
    section: RowOneLocalArticleContentSection,
    article: RowOneLocalArticle,
) -> LocalizedText | None:
    if item.body is not None:
        excerpt = _localized_excerpt(item.body.en, item.body.zh)
        if excerpt is not None:
            return excerpt
    for paragraph_index in _valid_paragraph_indices(item.paragraph_indices, article):
        paragraph = _paragraph_at(article, paragraph_index)
        if paragraph is None:
            continue
        excerpt = _localized_excerpt(paragraph[0], paragraph[1])
        if excerpt is not None:
            return excerpt
    if section.body is not None:
        excerpt = _localized_excerpt(section.body.en, section.body.zh)
        if excerpt is not None:
            return excerpt
    return None


def _first_paragraph(article: RowOneLocalArticle) -> tuple[int, str, str] | None:
    for index, paragraph in enumerate(article.paragraphs):
        normalized = normalize_row_one_paragraph(paragraph)
        if not normalized:
            continue
        paragraph_pair = _paragraph_at(article, index)
        if paragraph_pair is None:
            continue
        return index, paragraph_pair[0], paragraph_pair[1]
    return None


def _paragraph_at(article: RowOneLocalArticle, index: int) -> tuple[str, str] | None:
    if index < 0 or index >= len(article.paragraphs):
        return None
    paragraph_en = normalize_row_one_paragraph(article.paragraphs[index])
    if not paragraph_en:
        return None
    paragraph_zh = (
        normalize_row_one_paragraph(article.paragraphs_zh[index])
        if len(article.paragraphs_zh) == len(article.paragraphs)
        and index < len(article.paragraphs_zh)
        else ""
    )
    return paragraph_en, paragraph_zh or paragraph_en


def _valid_paragraph_indices(
    values: Sequence[int],
    article: RowOneLocalArticle,
) -> tuple[int, ...]:
    valid: list[int] = []
    seen: set[int] = set()
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        if value in seen:
            continue
        if _paragraph_at(article, value) is None:
            continue
        seen.add(value)
        valid.append(value)
    return tuple(valid)


def _item_lane_key(
    references: Sequence[RowOneReference],
    section_key: str,
) -> str | None:
    normalized_section_key = normalize_row_one_paragraph(section_key).casefold()
    if "product" in normalized_section_key:
        return "products"
    if (
        "brand" in normalized_section_key
        or "people" in normalized_section_key
        or "entities" in normalized_section_key
        or "entity" in normalized_section_key
    ):
        return "people_brands"
    reference_keys = {
        key
        for reference in references
        for key in (
            normalize_row_one_paragraph(reference.label).casefold(),
            normalize_row_one_paragraph(reference.type).casefold(),
        )
        if key
    }
    if reference_keys & _PRODUCT_TYPES:
        return "products"
    if reference_keys & _PEOPLE_BRAND_TYPES:
        return "people_brands"
    return None


def _references(
    refs: Sequence[RowOneReference],
) -> tuple[RowOneDailyLocalSavedArticleOrganizerReference, ...]:
    rendered: list[RowOneDailyLocalSavedArticleOrganizerReference] = []
    seen: set[tuple[str, str]] = set()
    for ref in refs:
        name = normalize_row_one_paragraph(ref.name)
        ref_type = normalize_row_one_paragraph(ref.type)
        label = normalize_row_one_paragraph(ref.label) or ref_type
        if not name:
            continue
        key = (name.casefold(), label.casefold())
        if key in seen:
            continue
        seen.add(key)
        rendered.append(RowOneDailyLocalSavedArticleOrganizerReference(name=name, label=label))
        if len(rendered) >= DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_MAX_REFS_PER_CARD:
            break
    return tuple(rendered)


def _article_title(headline: str, article_title: str | None, story_id: str) -> LocalizedText:
    title = normalize_row_one_paragraph(headline) or normalize_row_one_paragraph(
        article_title or ""
    )
    title = title or story_id
    return LocalizedText(en=title, zh=title)


def _source_name(article: RowOneLocalArticle, story_source_name: str) -> str:
    return normalize_row_one_paragraph(article.source_name) or normalize_row_one_paragraph(
        story_source_name
    )


def _clean_localized(value: LocalizedText, *, fallback: LocalizedText) -> LocalizedText:
    en = normalize_row_one_paragraph(value.en)
    zh = normalize_row_one_paragraph(value.zh)
    if not en and not zh:
        return fallback
    return LocalizedText(en=en or zh, zh=zh or en)


def _localized_excerpt(en: str, zh: str) -> LocalizedText | None:
    clean_en = _truncate(en)
    clean_zh = _truncate(zh)
    if not clean_en and not clean_zh:
        return None
    return LocalizedText(en=clean_en or clean_zh, zh=clean_zh or clean_en)


def _truncate(value: str) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS:
        return normalized
    return (
        normalized[: max(0, DAILY_LOCAL_SAVED_ARTICLE_ORGANIZER_EXCERPT_CHARS - 3)].rstrip() + "..."
    )


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
