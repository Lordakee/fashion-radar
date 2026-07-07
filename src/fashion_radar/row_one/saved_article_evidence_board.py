from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneReference,
)
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
)
from fashion_radar.row_one.saved_article_library import (
    RowOneSavedArticleLibrary,
    RowOneSavedArticleLibraryEntry,
)

MAX_SAVED_ARTICLE_EVIDENCE_BOARD_GROUPS = 4
MAX_SAVED_ARTICLE_EVIDENCE_BOARD_CARDS_PER_GROUP = 3
MAX_SAVED_ARTICLE_EVIDENCE_BOARD_REFERENCES = 4
SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS = 220

_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE = re.compile(
    r"^local-article-content-section-([1-9][0-9]*)$"
)


@dataclass(frozen=True)
class RowOneSavedArticleEvidenceBoardCard:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    paragraph_number: int
    excerpt: LocalizedText
    href: str
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleEvidenceBoardGroup:
    key: str
    title: LocalizedText
    dek: LocalizedText
    card_count: int
    source_count: int
    cards: tuple[RowOneSavedArticleEvidenceBoardCard, ...]


@dataclass(frozen=True)
class RowOneSavedArticleEvidenceBoard:
    group_count: int
    card_count: int
    source_count: int
    groups: tuple[RowOneSavedArticleEvidenceBoardGroup, ...]


def build_row_one_saved_article_evidence_board(
    edition: RowOneEdition | None,
    library: RowOneSavedArticleLibrary | None,
    organization: RowOneSavedArticleContentOrganization | None,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedArticleEvidenceBoard | None:
    if edition is None or library is None or organization is None or not local_articles_by_story_id:
        return None

    allowed_detail_paths = _library_detail_paths(library)
    if not allowed_detail_paths:
        return None

    articles_by_detail_path = _local_articles_by_detail_path(
        edition,
        local_articles_by_story_id,
        allowed_detail_paths,
    )
    if not articles_by_detail_path:
        return None

    groups: list[RowOneSavedArticleEvidenceBoardGroup] = []
    global_source_keys: set[str] = set()
    paragraph_budget_by_detail_path = {
        detail_path: _publishable_paragraph_budget(article.paragraphs)
        for detail_path, article in articles_by_detail_path.items()
    }
    seen_paragraphs_by_detail_path: dict[str, set[int]] = {}
    total_cards = 0

    for group in organization.groups:
        cards: list[RowOneSavedArticleEvidenceBoardCard] = []
        group_source_keys: set[str] = set()
        seen_cards: set[tuple[str, str, int]] = set()

        for organization_card in group.cards:
            content_href = _safe_content_section_href(organization_card.detail_path)
            if content_href is None:
                continue
            detail_path = _detail_path_key(content_href)
            section_number = _content_section_number(content_href)
            if detail_path is None or section_number is None:
                continue
            article = articles_by_detail_path.get(detail_path)
            if article is None:
                continue
            section = _section_for_card(article, section_number)
            if section is None:
                continue

            for paragraph_index in _valid_paragraph_indices(
                organization_card.paragraph_indices,
                article.paragraphs,
            ):
                dedupe_key = (group.key, detail_path, paragraph_index)
                if dedupe_key in seen_cards:
                    continue
                if not _reserve_article_paragraph(
                    detail_path,
                    paragraph_index,
                    paragraph_budget_by_detail_path,
                    seen_paragraphs_by_detail_path,
                ):
                    continue
                seen_cards.add(dedupe_key)
                paragraph = _normalized_text(article.paragraphs[paragraph_index])
                source_name = _normalized_text(organization_card.source_name)
                group_source_keys.add(_source_key(source_name))
                references = _references_for_paragraph(
                    section,
                    paragraph_index,
                    organization_card.references,
                )
                cards.append(
                    RowOneSavedArticleEvidenceBoardCard(
                        title=organization_card.title,
                        source_name=source_name,
                        section_title=organization_card.section_title,
                        section_label=organization_card.section_label,
                        paragraph_number=paragraph_index + 1,
                        excerpt=_localized_excerpt(paragraph),
                        href=f"{detail_path}#local-article-paragraph-{paragraph_index + 1}",
                        references=references,
                    )
                )
                if len(cards) >= MAX_SAVED_ARTICLE_EVIDENCE_BOARD_CARDS_PER_GROUP:
                    break
            if len(cards) >= MAX_SAVED_ARTICLE_EVIDENCE_BOARD_CARDS_PER_GROUP:
                break

        if not cards:
            continue
        global_source_keys.update(group_source_keys)
        groups.append(
            RowOneSavedArticleEvidenceBoardGroup(
                key=group.key,
                title=group.title,
                dek=group.dek,
                card_count=len(cards),
                source_count=len(group_source_keys),
                cards=tuple(cards),
            )
        )
        total_cards += len(cards)
        if len(groups) >= MAX_SAVED_ARTICLE_EVIDENCE_BOARD_GROUPS:
            break

    if not groups:
        return None
    return RowOneSavedArticleEvidenceBoard(
        group_count=len(groups),
        card_count=total_cards,
        source_count=len(global_source_keys),
        groups=tuple(groups),
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
    detail_paths: set[str] = set()
    for href, fragment in (
        (entry.reader_path, "local-article-reader"),
        (entry.digest_path, "local-article-digest"),
        (entry.evidence_path, "local-article-paragraph-evidence"),
    ):
        safe_href = safe_row_one_detail_fragment_href(href, fragment)
        if safe_href is None:
            return None
        detail_path = _detail_path_key(safe_href)
        if detail_path is None:
            return None
        detail_paths.add(detail_path)
    if len(detail_paths) != 1:
        return None
    return next(iter(detail_paths))


def _local_articles_by_detail_path(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    allowed_detail_paths: set[str],
) -> dict[str, RowOneLocalArticle]:
    articles_by_detail_path: dict[str, RowOneLocalArticle] = {}
    for story in edition.stories:
        safe_detail_path = validated_row_one_detail_relative_path(story.detail_path)
        if safe_detail_path is None:
            continue
        detail_path = str(safe_detail_path)
        if detail_path not in allowed_detail_paths:
            continue
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        articles_by_detail_path[detail_path] = article
    return articles_by_detail_path


def _safe_content_section_href(href: object) -> str | None:
    if not isinstance(href, str) or "#" not in href:
        return None
    path, fragment = href.split("#", 1)
    if _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment) is None:
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


def _content_section_number(href: str) -> int | None:
    _path, separator, fragment = href.partition("#")
    if not separator:
        return None
    match = _LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch(fragment)
    if match is None:
        return None
    return int(match.group(1))


def _section_for_card(
    article: RowOneLocalArticle,
    section_number: int,
) -> RowOneLocalArticleContentSection | None:
    section_index = section_number - 1
    if section_index < 0 or section_index >= len(article.content_sections):
        return None
    return article.content_sections[section_index]


def _valid_paragraph_indices(
    paragraph_indices: tuple[object, ...],
    paragraphs: list[str],
) -> tuple[int, ...]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in paragraph_indices:
        if isinstance(index, bool) or not isinstance(index, int):
            continue
        if index < 0 or index >= len(paragraphs):
            continue
        if not _normalized_text(paragraphs[index]):
            continue
        if index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return tuple(valid)


def _publishable_paragraph_budget(paragraphs: list[str]) -> int:
    nonblank_count = sum(1 for paragraph in paragraphs if _normalized_text(paragraph))
    return max(0, nonblank_count - 1)


def _reserve_article_paragraph(
    detail_path: str,
    paragraph_index: int,
    paragraph_budget_by_detail_path: Mapping[str, int],
    seen_paragraphs_by_detail_path: dict[str, set[int]],
) -> bool:
    budget = paragraph_budget_by_detail_path.get(detail_path, 0)
    if budget <= 0:
        return False
    seen = seen_paragraphs_by_detail_path.setdefault(detail_path, set())
    if paragraph_index in seen:
        return False
    if len(seen) >= budget:
        return False
    seen.add(paragraph_index)
    return True


def _references_for_paragraph(
    section: RowOneLocalArticleContentSection,
    paragraph_index: int,
    fallback: tuple[RowOneReference, ...],
) -> tuple[RowOneReference, ...]:
    matched: list[RowOneReference] = []
    for item in section.items:
        if paragraph_index not in _valid_item_paragraph_indices(item.paragraph_indices):
            continue
        matched.extend(item.references)
    references = _deduped_references(tuple(matched))
    if references:
        return references
    return _deduped_references(fallback)


def _valid_item_paragraph_indices(indices: object) -> set[int]:
    valid: set[int] = set()
    if not isinstance(indices, list):
        return valid
    for index in indices:
        if isinstance(index, bool) or not isinstance(index, int):
            continue
        valid.add(index)
    return valid


def _deduped_references(
    references: tuple[RowOneReference, ...],
) -> tuple[RowOneReference, ...]:
    deduped: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for reference in references:
        name = _normalized_text(reference.name)
        reference_type = _normalized_text(reference.type)
        label = _normalized_text(reference.label)
        if not name:
            continue
        key = (name.casefold(), reference_type.casefold(), label.casefold())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(RowOneReference(name=name, type=reference_type, label=label))
        if len(deduped) >= MAX_SAVED_ARTICLE_EVIDENCE_BOARD_REFERENCES:
            break
    return tuple(deduped)


def _localized_excerpt(paragraph: str) -> LocalizedText:
    excerpt = _excerpt(paragraph)
    return LocalizedText(zh=excerpt, en=excerpt)


def _excerpt(paragraph: str) -> str:
    normalized = _normalized_text(paragraph)
    if len(normalized) <= SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS:
        return normalized
    return normalized[:SAVED_ARTICLE_EVIDENCE_BOARD_EXCERPT_CHARS].rstrip() + "..."


def _source_key(name: str) -> str:
    return _normalized_text(name).casefold()


def _normalized_text(value: str) -> str:
    return " ".join(value.split())
