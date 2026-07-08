from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.body_source_labels import row_one_body_source_label
from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import LocalizedText, RowOneReference
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)

SAVED_ARTICLE_READ_NEXT_CLUSTER_LIMIT = 3
SAVED_ARTICLE_READ_NEXT_CLUSTER_ITEM_LIMIT = 3
SAVED_ARTICLE_READ_NEXT_CLUSTER_REFERENCE_LIMIT = 4

_LOCAL_ARTICLE_DIGEST_FRAGMENT = "local-article-digest"
_LOCAL_ARTICLE_CONTENT_SECTION_PREFIX = "local-article-content-section-"


@dataclass(frozen=True)
class RowOneSavedArticleReadNextClusterItem:
    title: LocalizedText
    source_name: str
    section_label: LocalizedText
    body_source_label: LocalizedText
    lead: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    evidence_count: int
    href: str
    detail_path: str
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleReadNextCluster:
    key: str
    title: LocalizedText
    dek: LocalizedText
    item_count: int
    source_count: int
    evidence_count: int
    items: tuple[RowOneSavedArticleReadNextClusterItem, ...]


@dataclass(frozen=True)
class RowOneSavedArticleReadNextClusters:
    cluster_count: int
    item_count: int
    source_count: int
    evidence_count: int
    clusters: tuple[RowOneSavedArticleReadNextCluster, ...]


@dataclass(frozen=True)
class _SafeLibraryEntry:
    detail_path: str
    order: int
    entry: RowOneSavedArticleLibraryEntry


def build_row_one_saved_article_read_next_clusters(
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> RowOneSavedArticleReadNextClusters | None:
    if library is None or organization is None:
        return None
    if not library.groups or not organization.groups:
        return None

    library_entries = _safe_library_entries_by_detail_path(library)
    if not library_entries:
        return None

    clusters: list[RowOneSavedArticleReadNextCluster] = []
    for group in organization.groups:
        cluster = _read_next_cluster(
            group,
            library_entries=library_entries,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        if cluster is None:
            continue
        clusters.append(cluster)
        if len(clusters) >= SAVED_ARTICLE_READ_NEXT_CLUSTER_LIMIT:
            break

    if not clusters:
        return None

    source_keys = {_source_key(item.source_name) for cluster in clusters for item in cluster.items}
    return RowOneSavedArticleReadNextClusters(
        cluster_count=len(clusters),
        item_count=sum(cluster.item_count for cluster in clusters),
        source_count=len(source_keys),
        evidence_count=sum(cluster.evidence_count for cluster in clusters),
        clusters=tuple(clusters),
    )


def _safe_library_entries_by_detail_path(
    library: RowOneSavedArticleLibrary,
) -> dict[str, _SafeLibraryEntry]:
    entries: dict[str, _SafeLibraryEntry] = {}
    order = 0
    for group in library.groups:
        for entry in group.entries:
            detail_path = _library_entry_detail_path(entry)
            if detail_path is None or detail_path in entries:
                continue
            entries[detail_path] = _SafeLibraryEntry(
                detail_path=detail_path,
                order=order,
                entry=entry,
            )
            order += 1
    return entries


def _library_entry_detail_path(entry: RowOneSavedArticleLibraryEntry) -> str | None:
    safe_href = safe_row_one_detail_fragment_href(
        entry.digest_path,
        _LOCAL_ARTICLE_DIGEST_FRAGMENT,
    )
    if safe_href is None:
        return None
    return _detail_path_key(safe_href)


def _read_next_cluster(
    group: RowOneSavedArticleContentOrganizationGroup,
    *,
    library_entries: Mapping[str, _SafeLibraryEntry],
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> RowOneSavedArticleReadNextCluster | None:
    selected: dict[str, tuple[RowOneSavedArticleContentOrganizationCard, _SafeLibraryEntry]] = {}
    for card in group.cards:
        detail_path = _card_detail_path(card)
        if detail_path is None or detail_path in selected:
            continue
        safe_library_entry = library_entries.get(detail_path)
        if safe_library_entry is None:
            continue
        selected[detail_path] = (card, safe_library_entry)

    if not selected:
        return None

    ordered = sorted(selected.values(), key=lambda value: value[1].order)
    items: list[RowOneSavedArticleReadNextClusterItem] = []
    for card, safe_library_entry in ordered[:SAVED_ARTICLE_READ_NEXT_CLUSTER_ITEM_LIMIT]:
        href = _item_href(
            card,
            safe_library_entry,
            local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
        )
        if href is None:
            continue
        entry = safe_library_entry.entry
        valid_paragraph_indices = _valid_paragraph_indices(card.paragraph_indices)
        items.append(
            RowOneSavedArticleReadNextClusterItem(
                title=entry.title,
                source_name=entry.source_name.strip() or card.source_name.strip(),
                section_label=card.section_label,
                body_source_label=row_one_body_source_label(entry.body_source),
                lead=card.lead,
                saved_paragraph_count=entry.saved_paragraph_count,
                organized_section_count=entry.organized_section_count,
                evidence_count=len(valid_paragraph_indices),
                href=href,
                detail_path=safe_library_entry.detail_path,
                references=tuple(card.references[:SAVED_ARTICLE_READ_NEXT_CLUSTER_REFERENCE_LIMIT]),
            )
        )

    if not items:
        return None

    source_keys = {_source_key(item.source_name) for item in items}
    evidence_count = sum(item.evidence_count for item in items)
    return RowOneSavedArticleReadNextCluster(
        key=group.key,
        title=group.title,
        dek=group.dek,
        item_count=len(items),
        source_count=len(source_keys),
        evidence_count=evidence_count,
        items=tuple(items),
    )


def _card_detail_path(card: RowOneSavedArticleContentOrganizationCard) -> str | None:
    safe_href = _safe_content_section_href(card.detail_path)
    if safe_href is None:
        return None
    return _detail_path_key(safe_href)


def _item_href(
    card: RowOneSavedArticleContentOrganizationCard,
    safe_library_entry: _SafeLibraryEntry,
    *,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    local_href = _local_article_page_digest_href(
        safe_library_entry.detail_path,
        local_article_page_hrefs_by_detail_path,
    )
    if local_href is not None:
        return local_href

    content_href = _safe_content_section_href(card.detail_path)
    if content_href is not None:
        return f"../{content_href}"

    digest_href = safe_row_one_detail_fragment_href(
        safe_library_entry.entry.digest_path,
        _LOCAL_ARTICLE_DIGEST_FRAGMENT,
    )
    if digest_href is not None:
        return f"../{digest_href}"
    return None


def _local_article_page_digest_href(
    detail_path: str,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> str | None:
    if not local_article_page_hrefs_by_detail_path:
        return None
    href = local_article_page_hrefs_by_detail_path.get(detail_path)
    if not isinstance(href, str):
        return None
    if href != href.strip() or any(character.isspace() for character in href):
        return None
    if href.startswith(".") or href.startswith("/") or "/" in href or not href.endswith(".html"):
        return None
    if not safe_local_article_story_id(href.removesuffix(".html")):
        return None
    return f"{href}#{_LOCAL_ARTICLE_DIGEST_FRAGMENT}"


def _safe_content_section_href(href: object) -> str | None:
    if not isinstance(href, str):
        return None
    if "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if not fragment.startswith(_LOCAL_ARTICLE_CONTENT_SECTION_PREFIX):
        return None
    raw_position = fragment.removeprefix(_LOCAL_ARTICLE_CONTENT_SECTION_PREFIX)
    if not raw_position.isdigit() or int(raw_position) <= 0:
        return None
    if validated_row_one_detail_relative_path(path) is None:
        return None
    return href


def _detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
    if validated_row_one_detail_relative_path(path) is None:
        return None
    return path


def _valid_paragraph_indices(paragraph_indices: tuple[int, ...]) -> tuple[int, ...]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in paragraph_indices:
        if isinstance(index, bool) or not isinstance(index, int):
            continue
        if index < 0 or index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return tuple(valid)


def _source_key(name: str) -> str:
    return " ".join(name.split()).casefold()
