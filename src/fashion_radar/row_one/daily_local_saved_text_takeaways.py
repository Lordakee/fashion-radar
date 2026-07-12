from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_MAX_LANES = 3
DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_MAX_CARDS_PER_LANE = 3
DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS = 170

_LANE_ORDER = ("what_article_says", "brand_product_context", "inspect_next")
_LANE_TITLES = {
    "what_article_says": LocalizedText(en="What the article says", zh="文章说了什么"),
    "brand_product_context": LocalizedText(
        en="Brand / product context",
        zh="品牌与单品语境",
    ),
    "inspect_next": LocalizedText(en="Inspect next", zh="接下来检查"),
}
_LANE_DEKS = {
    "what_article_says": LocalizedText(
        en="A direct saved-text read from today's local article bodies.",
        zh="直接读取今日保存本地正文。",
    ),
    "brand_product_context": LocalizedText(
        en="Brand, product, and people context already structured in saved text.",
        zh="保存正文中已经结构化的品牌、单品与人物语境。",
    ),
    "inspect_next": LocalizedText(
        en="A second same-site anchor for deeper reading.",
        zh="继续深读的第二个站内锚点。",
    ),
}
_BRAND_PRODUCT_REFERENCE_TYPES = {
    "accessory",
    "apparel",
    "bag",
    "brand",
    "celebrity",
    "creative_director",
    "designer",
    "flat",
    "founder",
    "jewelry",
    "people",
    "person",
    "product",
    "shoe",
    "shoes",
    "sneaker",
    "watch",
}
_BRAND_PRODUCT_SECTION_KEYS = {"brand_signals", "entities", "product_signals"}


@dataclass(frozen=True)
class RowOneDailyLocalSavedTextTakeawayCard:
    title: LocalizedText
    source_name: str
    label: LocalizedText
    excerpt: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalSavedTextTakeawayLane:
    key: str
    title: LocalizedText
    dek: LocalizedText
    cards: tuple[RowOneDailyLocalSavedTextTakeawayCard, ...]
    total_count: int


@dataclass(frozen=True)
class RowOneDailyLocalSavedTextTakeaways:
    title: LocalizedText
    dek: LocalizedText
    article_count: int
    source_count: int
    card_count: int
    lanes: tuple[RowOneDailyLocalSavedTextTakeawayLane, ...]


def build_row_one_daily_local_saved_text_takeaways(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalSavedTextTakeaways | None:
    cards_by_lane: dict[str, list[RowOneDailyLocalSavedTextTakeawayCard]] = {
        lane_key: [] for lane_key in _LANE_ORDER
    }
    totals = {lane_key: 0 for lane_key in _LANE_ORDER}
    seen_hrefs = {lane_key: set[str]() for lane_key in _LANE_ORDER}
    contributing_story_ids: set[str] = set()
    contributing_sources: set[str] = set()

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
        used_hrefs: set[str] = set()
        emitted_for_story = False

        for lane_key, card in (
            ("what_article_says", _what_article_says_card(article, title, source_name, page_href)),
            (
                "brand_product_context",
                _brand_product_context_card(article, title, source_name, page_href),
            ),
            (
                "inspect_next",
                _inspect_next_card(article, title, source_name, page_href, used_hrefs),
            ),
        ):
            if card is None:
                continue
            used_hrefs.add(card.href)
            if _add_card(cards_by_lane, totals, seen_hrefs, lane_key, card):
                emitted_for_story = True

        if emitted_for_story:
            contributing_story_ids.add(story.id)
            if source_name:
                contributing_sources.add(source_name.casefold())

    if len(contributing_story_ids) < 2:
        return None

    lanes = tuple(
        RowOneDailyLocalSavedTextTakeawayLane(
            key=lane_key,
            title=_LANE_TITLES[lane_key],
            dek=_LANE_DEKS[lane_key],
            cards=tuple(cards_by_lane[lane_key]),
            total_count=totals[lane_key],
        )
        for lane_key in _LANE_ORDER
        if cards_by_lane[lane_key]
    )[:DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_MAX_LANES]
    if not lanes:
        return None

    return RowOneDailyLocalSavedTextTakeaways(
        title=LocalizedText(en="Daily Saved Text Takeaways", zh="每日保存正文要点"),
        dek=LocalizedText(
            en="Short saved-text excerpts grouped for fast homepage reading.",
            zh="把保存正文短摘按阅读意图整理到首页。",
        ),
        article_count=len(contributing_story_ids),
        source_count=len(contributing_sources),
        card_count=sum(len(lane.cards) for lane in lanes),
        lanes=lanes,
    )


def _what_article_says_card(
    article: RowOneLocalArticle,
    title: LocalizedText,
    source_name: str,
    page_href: str,
) -> RowOneDailyLocalSavedTextTakeawayCard | None:
    for index, _paragraph in enumerate(article.paragraphs):
        excerpt = _excerpt_from_paragraph(article, index)
        if excerpt is None:
            continue
        return RowOneDailyLocalSavedTextTakeawayCard(
            title=title,
            source_name=source_name,
            label=_LANE_TITLES["what_article_says"],
            excerpt=excerpt,
            href=_paragraph_href(page_href, index),
        )
    return None


def _brand_product_context_card(
    article: RowOneLocalArticle,
    title: LocalizedText,
    source_name: str,
    page_href: str,
) -> RowOneDailyLocalSavedTextTakeawayCard | None:
    for section_position, section in enumerate(article.content_sections, start=1):
        for item in section.items:
            if not _is_brand_product_context(section, item):
                continue
            excerpt = _content_item_excerpt(item, section)
            if excerpt is None:
                continue
            return RowOneDailyLocalSavedTextTakeawayCard(
                title=title,
                source_name=source_name,
                label=_clean_localized(item.label, DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS),
                excerpt=excerpt,
                href=_content_section_href(page_href, section_position),
            )
        if _section_key_is_brand_product(section.key):
            excerpt = _clean_optional_localized(
                section.body,
                DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS,
            )
            if excerpt is not None:
                return RowOneDailyLocalSavedTextTakeawayCard(
                    title=title,
                    source_name=source_name,
                    label=_clean_localized(
                        section.title,
                        DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS,
                    ),
                    excerpt=excerpt,
                    href=_content_section_href(page_href, section_position),
                )
    return None


def _inspect_next_card(
    article: RowOneLocalArticle,
    title: LocalizedText,
    source_name: str,
    page_href: str,
    used_hrefs: set[str],
) -> RowOneDailyLocalSavedTextTakeawayCard | None:
    for index in range(1, len(article.paragraphs)):
        href = _paragraph_href(page_href, index)
        if href in used_hrefs:
            continue
        excerpt = _excerpt_from_paragraph(article, index)
        if excerpt is None:
            continue
        return RowOneDailyLocalSavedTextTakeawayCard(
            title=title,
            source_name=source_name,
            label=_LANE_TITLES["inspect_next"],
            excerpt=excerpt,
            href=href,
        )
    for section_position, section in enumerate(article.content_sections, start=1):
        href = _content_section_href(page_href, section_position)
        if href in used_hrefs:
            continue
        excerpt = _clean_optional_localized(
            section.body,
            DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS,
        )
        if excerpt is None:
            continue
        return RowOneDailyLocalSavedTextTakeawayCard(
            title=title,
            source_name=source_name,
            label=_clean_localized(section.title, DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS),
            excerpt=excerpt,
            href=href,
        )
    return None


def _add_card(
    cards_by_lane: dict[str, list[RowOneDailyLocalSavedTextTakeawayCard]],
    totals: dict[str, int],
    seen_hrefs: dict[str, set[str]],
    lane_key: str,
    card: RowOneDailyLocalSavedTextTakeawayCard,
) -> bool:
    totals[lane_key] += 1
    if card.href in seen_hrefs[lane_key]:
        return False
    if len(cards_by_lane[lane_key]) >= DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_MAX_CARDS_PER_LANE:
        return False
    seen_hrefs[lane_key].add(card.href)
    cards_by_lane[lane_key].append(card)
    return True


def _is_brand_product_context(
    section: RowOneLocalArticleContentSection,
    item: RowOneLocalArticleContentItem,
) -> bool:
    if _section_key_is_brand_product(section.key):
        return True
    reference_keys = {
        normalize_row_one_paragraph(value).casefold()
        for reference in item.references
        for value in (reference.type, reference.label)
        if normalize_row_one_paragraph(value)
    }
    return bool(reference_keys & _BRAND_PRODUCT_REFERENCE_TYPES)


def _section_key_is_brand_product(section_key: str) -> bool:
    key = normalize_row_one_paragraph(section_key).casefold()
    return key in _BRAND_PRODUCT_SECTION_KEYS


def _content_item_excerpt(
    item: RowOneLocalArticleContentItem,
    section: RowOneLocalArticleContentSection,
) -> LocalizedText | None:
    excerpt = _clean_optional_localized(item.body, DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS)
    if excerpt is not None:
        return excerpt
    return _clean_optional_localized(section.body, DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS)


def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if (
        "://" in href
        or "//" in href
        or "?" in href
        or "#" in href
        or href.startswith((".", "/", "//"))
    ):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..", "index.html")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return path.name


def _paragraph_href(page_href: str, paragraph_index: int) -> str:
    return f"articles/{page_href}#local-article-paragraph-{paragraph_index + 1}"


def _content_section_href(page_href: str, section_position: int) -> str:
    return f"articles/{page_href}#local-article-content-section-{section_position}"


def _article_title(headline: str, article_title: str | None, story_id: str) -> LocalizedText:
    title = normalize_row_one_paragraph(headline) or normalize_row_one_paragraph(
        article_title or ""
    )
    title = title or story_id
    return LocalizedText(en=title, zh=title)


def _source_name(article: RowOneLocalArticle, story_source_name: str) -> str:
    return (
        normalize_row_one_paragraph(article.source_name)
        or normalize_row_one_paragraph(story_source_name)
        or "Saved local source"
    )


def _clean_optional_localized(text: LocalizedText | None, limit: int) -> LocalizedText | None:
    if text is None:
        return None
    cleaned = _clean_localized(text, limit)
    if not cleaned.en and not cleaned.zh:
        return None
    return cleaned


def _clean_localized(text: LocalizedText | None, limit: int) -> LocalizedText:
    if text is None:
        return LocalizedText(en="", zh="")
    en = _truncate(normalize_row_one_paragraph(text.en), limit)
    zh = _truncate(normalize_row_one_paragraph(text.zh), limit)
    if not zh:
        zh = en
    if not en:
        en = zh
    return LocalizedText(en=en, zh=zh)


def _excerpt_from_paragraph(
    article: RowOneLocalArticle,
    paragraph_index: int,
) -> LocalizedText | None:
    if paragraph_index < 0 or paragraph_index >= len(article.paragraphs):
        return None
    en = normalize_row_one_paragraph(article.paragraphs[paragraph_index])
    if not en:
        return None
    aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)
    zh = (
        normalize_row_one_paragraph(article.paragraphs_zh[paragraph_index])
        if aligned_zh and paragraph_index < len(article.paragraphs_zh)
        else ""
    )
    return _clean_localized(
        LocalizedText(en=en, zh=zh or en),
        DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS,
    )


def _truncate(value: str, limit: int = DAILY_LOCAL_SAVED_TEXT_TAKEAWAYS_EXCERPT_CHARS) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 3)].rstrip() + "..."
