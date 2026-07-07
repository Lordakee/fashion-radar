from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.detail_routes import is_safe_row_one_detail_path
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneReference,
)

MAX_SAVED_ARTICLE_LIBRARY_SOURCE_GROUPS = 8
MAX_SAVED_ARTICLE_LIBRARY_ENTRIES_PER_SOURCE = 8
MAX_SAVED_ARTICLE_LIBRARY_REFERENCES = 6
MAX_SAVED_ARTICLE_LIBRARY_PARAGRAPH_LINKS = 4

LOCAL_ARTICLE_DIGEST_FRAGMENT = "local-article-digest"
LOCAL_ARTICLE_READER_FRAGMENT = "local-article-reader"
LOCAL_ARTICLE_EVIDENCE_FRAGMENT = "local-article-paragraph-evidence"
LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX = "local-article-paragraph"


@dataclass(frozen=True)
class RowOneSavedArticleLibraryParagraphLink:
    label: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneSavedArticleLibraryEntry:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    saved_paragraph_count: int
    organized_section_count: int
    digest_path: str
    reader_path: str
    evidence_path: str
    paragraph_links: tuple[RowOneSavedArticleLibraryParagraphLink, ...] = ()
    references: tuple[RowOneReference, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleLibrarySourceGroup:
    source_name: str
    article_count: int
    saved_paragraph_count: int
    organized_section_count: int
    entries: list[RowOneSavedArticleLibraryEntry]


@dataclass(frozen=True)
class RowOneSavedArticleLibrary:
    article_count: int
    source_count: int
    saved_paragraph_count: int
    organized_section_count: int
    groups: list[RowOneSavedArticleLibrarySourceGroup]


def build_row_one_saved_article_library(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedArticleLibrary | None:
    grouped_entries: dict[str, list[RowOneSavedArticleLibraryEntry]] = {}
    source_names: dict[str, str] = {}
    entries: list[RowOneSavedArticleLibraryEntry] = []

    for story in edition.stories:
        article = local_articles_by_story_id.get(story.id)
        if article is None:
            continue
        if article.story_id != story.id:
            continue
        if not safe_local_article_story_id(story.id):
            continue
        if not is_safe_row_one_detail_path(story.detail_path):
            continue
        saved_paragraph_count = _saved_paragraph_count(article)
        if saved_paragraph_count == 0:
            continue

        source_name = _source_display_name(article)
        source_key = _source_key(source_name)
        source_names.setdefault(source_key, source_name)
        entry = RowOneSavedArticleLibraryEntry(
            title=_entry_title(story.headline, article),
            source_name=source_name,
            section_title=_section_title(edition, story.section_key),
            saved_paragraph_count=saved_paragraph_count,
            organized_section_count=len(article.content_sections),
            digest_path=_detail_anchor(story.detail_path, LOCAL_ARTICLE_DIGEST_FRAGMENT),
            reader_path=_detail_anchor(story.detail_path, LOCAL_ARTICLE_READER_FRAGMENT),
            evidence_path=_detail_anchor(story.detail_path, LOCAL_ARTICLE_EVIDENCE_FRAGMENT),
            paragraph_links=_paragraph_links(story.detail_path, article),
            references=_references(article.content_sections),
        )
        entries.append(entry)
        grouped_entries.setdefault(source_key, []).append(entry)

    if not entries:
        return None

    groups: list[RowOneSavedArticleLibrarySourceGroup] = []
    for source_key, source_entries in grouped_entries.items():
        groups.append(
            RowOneSavedArticleLibrarySourceGroup(
                source_name=source_names[source_key],
                article_count=len(source_entries),
                saved_paragraph_count=sum(entry.saved_paragraph_count for entry in source_entries),
                organized_section_count=sum(
                    entry.organized_section_count for entry in source_entries
                ),
                entries=source_entries[:MAX_SAVED_ARTICLE_LIBRARY_ENTRIES_PER_SOURCE],
            )
        )
        if len(groups) >= MAX_SAVED_ARTICLE_LIBRARY_SOURCE_GROUPS:
            break

    return RowOneSavedArticleLibrary(
        article_count=len(entries),
        source_count=len(grouped_entries),
        saved_paragraph_count=sum(entry.saved_paragraph_count for entry in entries),
        organized_section_count=sum(entry.organized_section_count for entry in entries),
        groups=groups,
    )


def _entry_title(story_headline: str, article: RowOneLocalArticle) -> LocalizedText:
    title = (article.title or "").strip() or story_headline
    return LocalizedText(zh=title, en=title)


def _source_display_name(article: RowOneLocalArticle) -> str:
    return article.source_name.strip() or "Unknown source"


def _source_key(name: str) -> str:
    return " ".join(name.split()).casefold()


def _saved_paragraph_count(article: RowOneLocalArticle) -> int:
    return sum(1 for paragraph in article.paragraphs if paragraph.strip())


def _section_title(edition: RowOneEdition, section_key: str) -> LocalizedText:
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    fallback = section_key.replace("_", " ").title()
    return LocalizedText(zh=fallback, en=fallback)


def _detail_anchor(detail_path: str, fragment: str) -> str:
    return f"{detail_path}#{fragment}"


def _paragraph_links(
    detail_path: str,
    article: RowOneLocalArticle,
) -> tuple[RowOneSavedArticleLibraryParagraphLink, ...]:
    indices = _strict_valid_saved_article_library_paragraph_indices(
        _referenced_paragraph_indices(article.content_sections),
        _rendered_paragraph_indices(article),
    )
    links: list[RowOneSavedArticleLibraryParagraphLink] = []
    for index in indices[:MAX_SAVED_ARTICLE_LIBRARY_PARAGRAPH_LINKS]:
        paragraph_number = index + 1
        links.append(
            RowOneSavedArticleLibraryParagraphLink(
                label=LocalizedText(
                    zh=f"段落 {paragraph_number}",
                    en=f"Paragraph {paragraph_number}",
                ),
                href=_detail_anchor(
                    detail_path,
                    f"{LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX}-{paragraph_number}",
                ),
            )
        )
    return tuple(links)


def _referenced_paragraph_indices(
    sections: Iterable[RowOneLocalArticleContentSection],
) -> tuple[object, ...]:
    indices: list[object] = []
    for section in sections:
        for item in section.items:
            indices.extend(item.paragraph_indices)
    return tuple(indices)


def _rendered_paragraph_indices(article: RowOneLocalArticle) -> set[int]:
    return {index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}


def _strict_valid_saved_article_library_paragraph_indices(
    paragraph_indices: Iterable[object],
    rendered_indices: set[int],
) -> tuple[int, ...]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in paragraph_indices:
        if isinstance(index, bool) or not isinstance(index, int):
            continue
        if index not in rendered_indices:
            continue
        if index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return tuple(valid)


def _references(
    sections: Iterable[RowOneLocalArticleContentSection],
) -> tuple[RowOneReference, ...]:
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for section in sections:
        for item in section.items:
            for ref in item.references:
                dedupe_key = (
                    " ".join(ref.name.split()).casefold(),
                    " ".join(ref.type.split()).casefold(),
                    " ".join(ref.label.split()).casefold(),
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                refs.append(
                    RowOneReference(
                        name=ref.name.strip(),
                        type=ref.type.strip(),
                        label=ref.label.strip(),
                    )
                )
                if len(refs) >= MAX_SAVED_ARTICLE_LIBRARY_REFERENCES:
                    return tuple(refs)
    return tuple(refs)
