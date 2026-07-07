from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import LocalizedText, RowOneReference
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)

MAX_SAVED_ARTICLE_THEME_DIGEST_THEMES = 4
MAX_SAVED_ARTICLE_THEME_DIGEST_ITEMS = 3


@dataclass(frozen=True)
class RowOneSavedArticleThemeDigestItem:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    lead: LocalizedText
    detail_path: str
    paragraph_indices: tuple[int, ...] = ()
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleThemeDigestTheme:
    key: str
    title: LocalizedText
    dek: LocalizedText
    item_count: int
    source_count: int
    items: tuple[RowOneSavedArticleThemeDigestItem, ...]


@dataclass(frozen=True)
class RowOneSavedArticleThemeDigest:
    theme_count: int
    item_count: int
    source_count: int
    themes: tuple[RowOneSavedArticleThemeDigestTheme, ...]


_THEME_BY_GROUP_KEY: dict[str, tuple[str, LocalizedText, LocalizedText]] = {
    "takeaways": (
        "read_first",
        LocalizedText(en="Read First", zh="优先阅读"),
        LocalizedText(
            en="The strongest opening reads from today's saved local text.",
            zh="今天本地保存文本中最适合作为入口的内容。",
        ),
    ),
    "entities": (
        "people_brands",
        LocalizedText(en="People & Brands", zh="人物与品牌"),
        LocalizedText(
            en=("Designers, celebrities, brands, and creative figures shaping the saved set."),
            zh="影响今天保存内容的设计师、明星、品牌与创意人物。",
        ),
    ),
    "product_signals": (
        "products",
        LocalizedText(en="Products", zh="产品"),
        LocalizedText(
            en="Bags, shoes, silhouettes, and product cues appearing across saved articles.",
            zh="在保存文章中反复出现的包袋、鞋履、廓形与产品线索。",
        ),
    ),
    "brand_signals": (
        "source_structure",
        LocalizedText(en="Source Structure", zh="来源结构"),
        LocalizedText(
            en="How sources structure the context around the saved local text.",
            zh="不同来源如何组织今天保存文本里的语境。",
        ),
    ),
}


def build_row_one_saved_article_theme_digest(
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
) -> RowOneSavedArticleThemeDigest | None:
    if library is None or organization is None:
        return None

    allowed_detail_paths = _library_detail_paths(library)
    if not allowed_detail_paths:
        return None

    themes: list[RowOneSavedArticleThemeDigestTheme] = []
    total_items = 0
    global_source_keys: set[str] = set()

    for group in organization.groups:
        theme_config = _THEME_BY_GROUP_KEY.get(group.key)
        if theme_config is None:
            continue
        theme_key, title, dek = theme_config
        items: list[RowOneSavedArticleThemeDigestItem] = []
        seen_items: set[tuple[str, str, str, str]] = set()
        source_keys: set[str] = set()

        for card in group.cards:
            item = _theme_item(card, allowed_detail_paths)
            if item is None:
                continue
            dedupe_key = (
                theme_key,
                item.detail_path,
                _normalized_text(item.lead.en),
                _normalized_text(item.lead.zh),
            )
            if dedupe_key in seen_items:
                continue
            seen_items.add(dedupe_key)
            items.append(item)
            source_key = _source_key(item.source_name)
            source_keys.add(source_key)
            global_source_keys.add(source_key)
            if len(items) >= MAX_SAVED_ARTICLE_THEME_DIGEST_ITEMS:
                break

        if not items:
            continue
        theme = RowOneSavedArticleThemeDigestTheme(
            key=theme_key,
            title=title,
            dek=dek,
            item_count=len(items),
            source_count=len(source_keys),
            items=tuple(items),
        )
        themes.append(theme)
        total_items += theme.item_count
        if len(themes) >= MAX_SAVED_ARTICLE_THEME_DIGEST_THEMES:
            break

    if not themes:
        return None
    return RowOneSavedArticleThemeDigest(
        theme_count=len(themes),
        item_count=total_items,
        source_count=len(global_source_keys),
        themes=tuple(themes),
    )


def _library_detail_paths(library: RowOneSavedArticleLibrary) -> set[str]:
    detail_paths: set[str] = set()
    for group in library.groups:
        for entry in group.entries:
            detail_path = _entry_detail_path(entry)
            if detail_path is not None:
                detail_paths.add(detail_path)
    return detail_paths


def _entry_detail_path(entry: RowOneSavedArticleLibraryEntry) -> str | None:
    for href, fragment in (
        (entry.reader_path, "local-article-reader"),
        (entry.digest_path, "local-article-digest"),
        (entry.evidence_path, "local-article-paragraph-evidence"),
    ):
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            continue
        detail_path = _detail_path_key(safe_href)
        if detail_path is not None:
            return detail_path
    return None


def _theme_item(
    card: RowOneSavedArticleContentOrganizationCard,
    allowed_detail_paths: set[str],
) -> RowOneSavedArticleThemeDigestItem | None:
    href = _safe_content_section_href(card.detail_path)
    if href is None:
        return None
    detail_path = _detail_path_key(href)
    if detail_path is None or detail_path not in allowed_detail_paths:
        return None
    return RowOneSavedArticleThemeDigestItem(
        title=card.title,
        source_name=card.source_name,
        section_title=card.section_title,
        section_label=card.section_label,
        lead=card.lead,
        detail_path=href,
        paragraph_indices=card.paragraph_indices,
        references=card.references,
    )


def _safe_content_section_href(href: object) -> str | None:
    if not isinstance(href, str) or "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if not fragment.startswith("local-article-content-section-"):
        return None
    number = fragment.removeprefix("local-article-content-section-")
    if not number.isascii() or not number.isdecimal() or len(number) > 6:
        return None
    section_index = int(number)
    if number != str(section_index) or section_index < 1:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return f"{safe_path}#{fragment}"


def _detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    safe_path = validated_row_one_detail_relative_path(path)
    if safe_path is None:
        return None
    return str(safe_path)


def _source_key(name: str) -> str:
    return _normalized_text(name).casefold()


def _normalized_text(value: str) -> str:
    return " ".join(value.split())
