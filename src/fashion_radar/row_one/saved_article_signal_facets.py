from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    row_one_saved_article_reference_bucket,
)

SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT = 6
SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT = 4
_SAVED_ARTICLE_SIGNAL_FACET_THEME_GROUP_KEYS = frozenset(
    {
        "takeaways",
        "product_signals",
    }
)


@dataclass(frozen=True)
class RowOneSavedArticleSignalFacetChip:
    label: LocalizedText


@dataclass(frozen=True)
class RowOneSavedArticleSignalFacetRow:
    title: LocalizedText
    source_name: str
    href: str
    detail_path: str
    safe_card_count: int
    brands: tuple[RowOneSavedArticleSignalFacetChip, ...]
    products: tuple[RowOneSavedArticleSignalFacetChip, ...]
    themes: tuple[RowOneSavedArticleSignalFacetChip, ...]


@dataclass(frozen=True)
class RowOneSavedArticleSignalFacets:
    row_count: int
    brand_count: int
    product_count: int
    theme_count: int
    rows: tuple[RowOneSavedArticleSignalFacetRow, ...]


@dataclass(frozen=True)
class _SignalFacetCardContext:
    group_key: str
    group_title: LocalizedText
    card: RowOneSavedArticleContentOrganizationCard


def build_row_one_saved_article_signal_facets(
    library: RowOneSavedArticleLibrary,
    organization: RowOneSavedArticleContentOrganization | None,
) -> RowOneSavedArticleSignalFacets | None:
    if organization is None:
        return None
    cards_by_detail_path = _saved_article_signal_facet_cards_by_detail_path(
        library,
        organization,
    )
    rows: list[RowOneSavedArticleSignalFacetRow] = []
    for group in library.groups:
        for entry in group.entries:
            detail_path = _saved_article_library_entry_detail_path(entry)
            if detail_path is None:
                continue
            contexts = cards_by_detail_path.get(detail_path, ())
            if not contexts:
                continue
            href = _saved_article_signal_facet_entry_href(entry)
            if href is None:
                continue
            if _detail_path_key(href) != detail_path:
                continue
            row = _saved_article_signal_facet_row(
                entry,
                href=href,
                detail_path=detail_path,
                contexts=contexts,
            )
            if row is not None:
                rows.append(row)
            if len(rows) >= SAVED_ARTICLE_SIGNAL_FACET_ROW_LIMIT:
                return _saved_article_signal_facets(rows)
    return _saved_article_signal_facets(rows)


def _saved_article_signal_facet_cards_by_detail_path(
    library: RowOneSavedArticleLibrary,
    organization: RowOneSavedArticleContentOrganization,
) -> dict[str, tuple[_SignalFacetCardContext, ...]]:
    allowed_detail_paths = _library_detail_paths(library)
    grouped: dict[str, list[_SignalFacetCardContext]] = {}
    for group in organization.groups:
        for card in group.cards:
            href = _safe_saved_article_content_organization_href(card.detail_path)
            if href is None:
                continue
            detail_path = _detail_path_key(href)
            if detail_path is None or detail_path not in allowed_detail_paths:
                continue
            grouped.setdefault(detail_path, []).append(
                _SignalFacetCardContext(
                    group_key=str(group.key),
                    group_title=group.title,
                    card=card,
                )
            )
    return {detail_path: tuple(contexts) for detail_path, contexts in grouped.items()}


def _library_detail_paths(library: RowOneSavedArticleLibrary) -> set[str]:
    detail_paths: set[str] = set()
    for group in library.groups:
        for entry in group.entries:
            detail_path = _saved_article_library_entry_detail_path(entry)
            if detail_path is not None:
                detail_paths.add(detail_path)
    return detail_paths


def _saved_article_library_entry_detail_path(
    entry: RowOneSavedArticleLibraryEntry,
) -> str | None:
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


def _saved_article_signal_facet_entry_href(
    entry: RowOneSavedArticleLibraryEntry,
) -> str | None:
    return safe_row_one_detail_fragment_href(entry.digest_path, "local-article-digest")


def _safe_saved_article_content_organization_href(href: object) -> str | None:
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


def _saved_article_signal_facet_row(
    entry: RowOneSavedArticleLibraryEntry,
    *,
    href: str,
    detail_path: str,
    contexts: Sequence[_SignalFacetCardContext],
) -> RowOneSavedArticleSignalFacetRow | None:
    brands = _saved_article_signal_facet_reference_chips(contexts, "brands")
    products = _saved_article_signal_facet_reference_chips(contexts, "products")
    themes = _saved_article_signal_facet_theme_chips(contexts)
    if not brands and not products and not themes:
        return None
    return RowOneSavedArticleSignalFacetRow(
        title=entry.title,
        source_name=entry.source_name,
        href=href,
        detail_path=detail_path,
        safe_card_count=len(contexts),
        brands=brands,
        products=products,
        themes=themes,
    )


def _saved_article_signal_facet_reference_chips(
    contexts: Sequence[_SignalFacetCardContext],
    bucket: str,
) -> tuple[RowOneSavedArticleSignalFacetChip, ...]:
    labels: list[LocalizedText] = []
    for context in contexts:
        for reference in context.card.references:
            if row_one_saved_article_reference_bucket(reference) != bucket:
                continue
            label = " ".join(reference.name.split())
            if label:
                labels.append(LocalizedText(zh=label, en=label))
    return _saved_article_signal_facet_chip_values(labels)


def _saved_article_signal_facet_theme_chips(
    contexts: Sequence[_SignalFacetCardContext],
) -> tuple[RowOneSavedArticleSignalFacetChip, ...]:
    return _saved_article_signal_facet_chip_values(
        context.group_title
        for context in contexts
        if context.group_key in _SAVED_ARTICLE_SIGNAL_FACET_THEME_GROUP_KEYS
    )


def _saved_article_signal_facet_chip_values(
    values: Iterable[LocalizedText],
) -> tuple[RowOneSavedArticleSignalFacetChip, ...]:
    chips: list[RowOneSavedArticleSignalFacetChip] = []
    seen: set[tuple[str, str]] = set()
    for value in values:
        label = LocalizedText(
            zh=" ".join(value.zh.split()),
            en=" ".join(value.en.split()),
        )
        if not label.zh and not label.en:
            continue
        key = (label.zh.casefold(), label.en.casefold())
        if key in seen:
            continue
        seen.add(key)
        chips.append(RowOneSavedArticleSignalFacetChip(label=label))
        if len(chips) >= SAVED_ARTICLE_SIGNAL_FACET_CHIP_LIMIT:
            break
    return tuple(chips)


def _saved_article_signal_facets(
    rows: list[RowOneSavedArticleSignalFacetRow],
) -> RowOneSavedArticleSignalFacets | None:
    if not rows:
        return None
    return RowOneSavedArticleSignalFacets(
        row_count=len(rows),
        brand_count=sum(len(row.brands) for row in rows),
        product_count=sum(len(row.products) for row in rows),
        theme_count=sum(len(row.themes) for row in rows),
        rows=tuple(rows),
    )
