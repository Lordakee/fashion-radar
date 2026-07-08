from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.body_source_labels import row_one_body_source_label
from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneReference,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)

SAVED_ARTICLE_LOCAL_READING_COMPANION_RELATED_LIMIT = 3
SAVED_ARTICLE_LOCAL_READING_COMPANION_REFERENCE_LIMIT = 4

_LOCAL_ARTICLE_DIGEST_FRAGMENT = "local-article-digest"
_LOCAL_ARTICLE_READER_FRAGMENT = "local-article-reader"
_LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_FRAGMENT = "local-article-paragraph-evidence"
_LOCAL_ARTICLE_CONTENT_SECTION_PREFIX = "local-article-content-section-"


@dataclass(frozen=True)
class RowOneSavedArticleLocalReadingCompanionLink:
    label: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneSavedArticleLocalReadingCompanionItem:
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
class RowOneSavedArticleLocalReadingCompanion:
    current_title: LocalizedText
    source_name: str
    section_title: LocalizedText
    group_title: LocalizedText
    group_dek: LocalizedText
    section_label: LocalizedText
    body_source_label: LocalizedText
    lead: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    evidence_count: int
    detail_path: str
    local_links: tuple[RowOneSavedArticleLocalReadingCompanionLink, ...]
    related_items: tuple[RowOneSavedArticleLocalReadingCompanionItem, ...]
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class _SafeLibraryEntry:
    detail_path: str
    order: int
    entry: RowOneSavedArticleLibraryEntry


def build_row_one_saved_article_local_reading_companion(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> RowOneSavedArticleLocalReadingCompanion | None:
    if library is None or organization is None:
        return None
    if story.id != local_article.story_id or not safe_local_article_story_id(story.id):
        return None

    current_detail_path = _story_detail_path(story)
    if current_detail_path is None:
        return None

    library_entries = _safe_library_entries_by_detail_path(library)
    current_library_entry = library_entries.get(current_detail_path)
    if current_library_entry is None:
        return None

    group_match = _current_group_match(
        organization,
        current_detail_path=current_detail_path,
    )
    if group_match is None:
        return None
    group, current_card = group_match

    local_links = _current_local_links(local_article)
    related_items = _related_items(
        group,
        current_detail_path=current_detail_path,
        library_entries=library_entries,
        local_article_page_hrefs_by_detail_path=local_article_page_hrefs_by_detail_path,
    )
    if not local_links and not related_items:
        return None

    valid_current_indices = _valid_paragraph_indices(current_card.paragraph_indices)
    entry = current_library_entry.entry
    return RowOneSavedArticleLocalReadingCompanion(
        current_title=entry.title,
        source_name=entry.source_name.strip() or current_card.source_name.strip(),
        section_title=entry.section_title,
        group_title=group.title,
        group_dek=group.dek,
        section_label=current_card.section_label,
        body_source_label=row_one_body_source_label(entry.body_source),
        lead=current_card.lead,
        saved_paragraph_count=entry.saved_paragraph_count,
        organized_section_count=entry.organized_section_count,
        evidence_count=len(valid_current_indices),
        detail_path=current_detail_path,
        local_links=tuple(local_links),
        related_items=tuple(related_items),
        references=tuple(
            current_card.references[:SAVED_ARTICLE_LOCAL_READING_COMPANION_REFERENCE_LIMIT]
        ),
    )


def _story_detail_path(story: RowOneStory) -> str | None:
    pure_path = validated_row_one_detail_relative_path(story.detail_path)
    if pure_path is None:
        return None
    return str(pure_path)


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


def _current_group_match(
    organization: RowOneSavedArticleContentOrganization,
    *,
    current_detail_path: str,
) -> (
    tuple[
        RowOneSavedArticleContentOrganizationGroup,
        RowOneSavedArticleContentOrganizationCard,
    ]
    | None
):
    for group in organization.groups:
        for card in group.cards:
            if _card_detail_path(card) == current_detail_path:
                return (group, card)
    return None


def _related_items(
    group: RowOneSavedArticleContentOrganizationGroup,
    *,
    current_detail_path: str,
    library_entries: Mapping[str, _SafeLibraryEntry],
    local_article_page_hrefs_by_detail_path: Mapping[str, str] | None,
) -> list[RowOneSavedArticleLocalReadingCompanionItem]:
    selected: dict[str, tuple[RowOneSavedArticleContentOrganizationCard, _SafeLibraryEntry]] = {}
    for card in group.cards:
        detail_path = _card_detail_path(card)
        if detail_path is None or detail_path == current_detail_path or detail_path in selected:
            continue
        safe_library_entry = library_entries.get(detail_path)
        if safe_library_entry is None:
            continue
        selected[detail_path] = (card, safe_library_entry)

    items: list[RowOneSavedArticleLocalReadingCompanionItem] = []
    for card, safe_library_entry in sorted(selected.values(), key=lambda value: value[1].order):
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
            RowOneSavedArticleLocalReadingCompanionItem(
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
                references=tuple(
                    card.references[:SAVED_ARTICLE_LOCAL_READING_COMPANION_REFERENCE_LIMIT]
                ),
            )
        )
        if len(items) >= SAVED_ARTICLE_LOCAL_READING_COMPANION_RELATED_LIMIT:
            return items
    return items


def _current_local_links(
    article: RowOneLocalArticle,
) -> list[RowOneSavedArticleLocalReadingCompanionLink]:
    links = [
        RowOneSavedArticleLocalReadingCompanionLink(
            label=LocalizedText(en="Saved text digest", zh="保存正文整理"),
            href=f"#{_LOCAL_ARTICLE_DIGEST_FRAGMENT}",
        ),
        RowOneSavedArticleLocalReadingCompanionLink(
            label=LocalizedText(en="Saved text reader", zh="保存正文阅读"),
            href=f"#{_LOCAL_ARTICLE_READER_FRAGMENT}",
        ),
    ]
    if article.content_sections:
        links.append(
            RowOneSavedArticleLocalReadingCompanionLink(
                label=LocalizedText(en="Organized sections", zh="整理栏目"),
                href=f"#{_LOCAL_ARTICLE_CONTENT_SECTION_PREFIX}1",
            )
        )
    has_paragraph_evidence = any(
        _valid_paragraph_indices(tuple(section_item.paragraph_indices))
        for section in article.content_sections
        for section_item in section.items
    )
    if has_paragraph_evidence:
        links.append(
            RowOneSavedArticleLocalReadingCompanionLink(
                label=LocalizedText(en="Paragraph evidence", zh="段落证据"),
                href=f"#{_LOCAL_ARTICLE_PARAGRAPH_EVIDENCE_FRAGMENT}",
            )
        )
    return links


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
