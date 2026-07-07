from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.detail_routes import is_safe_row_one_detail_path
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

MAX_SAVED_SIGNAL_INDEX_ENTRIES = 12
MAX_SAVED_SIGNAL_INDEX_SUPPORTS = 4
MAX_SAVED_SIGNAL_INDEX_PARAGRAPH_LINKS = 3
SAVED_SIGNAL_INDEX_EXCERPT_CHARS = 220

LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_PREFIX = "local-article-content-section"
LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX = "local-article-paragraph"

_ALLOWED_REFERENCE_TYPES = frozenset(
    {
        "brand",
        "designer",
        "person",
        "product",
        "bag",
        "shoe",
        "celebrity",
    }
)
_REFERENCE_TYPE_ALIASES = {
    "brands": "brand",
    "designers": "designer",
    "people": "person",
    "products": "product",
    "bags": "bag",
    "shoes": "shoe",
}


@dataclass(frozen=True)
class RowOneSavedSignalIndexParagraphLink:
    label: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneSavedSignalIndexSupport:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    content_section_title: LocalizedText
    section_path: str
    paragraph_links: tuple[RowOneSavedSignalIndexParagraphLink, ...] = ()
    excerpt: LocalizedText | None = None


@dataclass(frozen=True)
class RowOneSavedSignalIndexEntry:
    name: str
    type: str
    label: str
    article_count: int
    source_count: int
    supporting_paragraph_count: int
    supports: list[RowOneSavedSignalIndexSupport]


@dataclass(frozen=True)
class RowOneSavedSignalIndex:
    signal_count: int
    supporting_article_count: int
    source_count: int
    supporting_paragraph_count: int
    entries: list[RowOneSavedSignalIndexEntry]


@dataclass
class _SignalEntryState:
    name: str
    type: str
    label: str
    article_ids: set[str] = field(default_factory=set)
    source_keys: set[str] = field(default_factory=set)
    supports: list[RowOneSavedSignalIndexSupport] = field(default_factory=list)
    supporting_paragraph_count: int = 0


@dataclass(frozen=True)
class _ReferenceDisplay:
    name: str
    type: str
    label: str
    key: tuple[str, str]


def build_row_one_saved_signal_index(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedSignalIndex | None:
    entries_by_key: dict[tuple[str, str], _SignalEntryState] = {}

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

        rendered_indices = _rendered_paragraph_indices(article)
        if not rendered_indices:
            continue

        _add_story_signal_supports(
            entries_by_key=entries_by_key,
            edition=edition,
            story_id=story.id,
            story_headline=story.headline,
            story_section_key=story.section_key,
            detail_path=story.detail_path,
            article=article,
            rendered_indices=rendered_indices,
        )

    if not entries_by_key:
        return None

    entry_states = sorted(
        entries_by_key.values(),
        key=_entry_state_sort_key,
    )[:MAX_SAVED_SIGNAL_INDEX_ENTRIES]
    entries = [_entry_from_state(state) for state in entry_states]
    if not entries:
        return None

    article_ids: set[str] = set()
    source_keys: set[str] = set()
    for state in entry_states:
        article_ids.update(state.article_ids)
        source_keys.update(state.source_keys)

    return RowOneSavedSignalIndex(
        signal_count=len(entries),
        supporting_article_count=len(article_ids),
        source_count=len(source_keys),
        supporting_paragraph_count=sum(entry.supporting_paragraph_count for entry in entries),
        entries=entries,
    )


def _add_story_signal_supports(
    *,
    entries_by_key: dict[tuple[str, str], _SignalEntryState],
    edition: RowOneEdition,
    story_id: str,
    story_headline: str,
    story_section_key: str,
    detail_path: str,
    article: RowOneLocalArticle,
    rendered_indices: set[int],
) -> None:
    seen_story_keys: set[tuple[str, str]] = set()
    source_name = _source_display_name(article)
    source_key = _source_key(source_name)
    section_title = _section_title(edition, story_section_key)

    for section_position, content_section in enumerate(article.content_sections, start=1):
        section_items_by_key = _section_items_by_signal_key(
            entries_by_key=entries_by_key,
            content_section=content_section,
            seen_story_keys=seen_story_keys,
        )
        for key, items in section_items_by_key.items():
            referenced_paragraph_indices = _referenced_paragraph_indices(items)
            paragraph_indices = _strict_valid_saved_signal_paragraph_indices(
                referenced_paragraph_indices,
                rendered_indices,
            )
            entries_by_key[key].article_ids.add(story_id)
            entries_by_key[key].source_keys.add(source_key)
            entries_by_key[key].supporting_paragraph_count += len(paragraph_indices)
            entries_by_key[key].supports.append(
                RowOneSavedSignalIndexSupport(
                    title=LocalizedText(zh=story_headline, en=story_headline),
                    source_name=source_name,
                    section_title=section_title,
                    content_section_title=content_section.title,
                    section_path=_content_section_path(detail_path, section_position),
                    paragraph_links=_paragraph_links(detail_path, paragraph_indices),
                    excerpt=_support_excerpt(
                        article,
                        items,
                        referenced_paragraph_indices,
                        rendered_indices,
                    ),
                )
            )
            seen_story_keys.add(key)


def _section_items_by_signal_key(
    *,
    entries_by_key: dict[tuple[str, str], _SignalEntryState],
    content_section: RowOneLocalArticleContentSection,
    seen_story_keys: set[tuple[str, str]],
) -> dict[tuple[str, str], list[RowOneLocalArticleContentItem]]:
    items_by_key: dict[tuple[str, str], list[RowOneLocalArticleContentItem]] = {}
    for item in content_section.items:
        item_keys: set[tuple[str, str]] = set()
        for ref in item.references:
            display = _reference_display(ref.name, ref.type, ref.label)
            if display is None:
                continue
            entries_by_key.setdefault(
                display.key,
                _SignalEntryState(
                    name=display.name,
                    type=display.type,
                    label=display.label,
                ),
            )
            if display.key in seen_story_keys or display.key in item_keys:
                continue
            items_by_key.setdefault(display.key, []).append(item)
            item_keys.add(display.key)
    return items_by_key


def _entry_from_state(state: _SignalEntryState) -> RowOneSavedSignalIndexEntry:
    return RowOneSavedSignalIndexEntry(
        name=state.name,
        type=state.type,
        label=state.label,
        article_count=len(state.article_ids),
        source_count=len(state.source_keys),
        supporting_paragraph_count=state.supporting_paragraph_count,
        supports=state.supports[:MAX_SAVED_SIGNAL_INDEX_SUPPORTS],
    )


def _entry_state_sort_key(state: _SignalEntryState) -> tuple[int, int, int, str, str]:
    return (
        -len(state.article_ids),
        -len(state.source_keys),
        -state.supporting_paragraph_count,
        _normalized_key(state.name),
        _normalized_key(state.type),
    )


def _reference_display(name: str, reference_type: str, label: str) -> _ReferenceDisplay | None:
    display_name = name.strip()
    if not display_name:
        return None

    display_type = _canonical_reference_type(reference_type)
    if display_type is None:
        return None
    display_label = label.strip() or display_type
    return _ReferenceDisplay(
        name=display_name,
        type=display_type,
        label=display_label,
        key=(_normalized_key(display_name), _normalized_key(display_type)),
    )


def _canonical_reference_type(reference_type: str) -> str | None:
    normalized_type = _normalized_key(reference_type)
    if not normalized_type:
        return None
    canonical_type = _REFERENCE_TYPE_ALIASES.get(normalized_type, normalized_type)
    if canonical_type not in _ALLOWED_REFERENCE_TYPES:
        return None
    return canonical_type


def _rendered_paragraph_indices(article: RowOneLocalArticle) -> set[int]:
    return {index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip()}


def _referenced_paragraph_indices(
    items: Iterable[RowOneLocalArticleContentItem],
) -> tuple[object, ...]:
    indices: list[object] = []
    for item in items:
        indices.extend(item.paragraph_indices)
    return tuple(indices)


def _strict_valid_saved_signal_paragraph_indices(
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


def _saved_signal_excerpt_text(value: str) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= SAVED_SIGNAL_INDEX_EXCERPT_CHARS:
        return normalized
    return normalized[: SAVED_SIGNAL_INDEX_EXCERPT_CHARS - 3].rstrip() + "..."


def _localized_excerpt(en: str, zh: str) -> LocalizedText | None:
    en_text = _saved_signal_excerpt_text(en)
    zh_text = _saved_signal_excerpt_text(zh)
    if not en_text and not zh_text:
        return None
    if not en_text:
        en_text = zh_text
    if not zh_text:
        zh_text = en_text
    return LocalizedText(en=en_text, zh=zh_text)


def _item_body_excerpt(
    items: Iterable[RowOneLocalArticleContentItem],
) -> LocalizedText | None:
    for item in items:
        if item.body is None:
            continue
        excerpt = _localized_excerpt(item.body.en, item.body.zh)
        if excerpt is not None:
            return excerpt
    return None


def _paragraph_excerpt(
    article: RowOneLocalArticle,
    paragraph_indices: Sequence[object],
    rendered_indices: set[int],
) -> LocalizedText | None:
    valid_indices = _strict_valid_saved_signal_paragraph_indices(
        paragraph_indices,
        rendered_indices,
    )
    for index in valid_indices:
        en = article.paragraphs[index]
        zh = article.paragraphs_zh[index] if index < len(article.paragraphs_zh) else ""
        excerpt = _localized_excerpt(en, zh)
        if excerpt is not None:
            return excerpt
    return None


def _support_excerpt(
    article: RowOneLocalArticle,
    items: Iterable[RowOneLocalArticleContentItem],
    paragraph_indices: Iterable[object],
    rendered_indices: set[int],
) -> LocalizedText | None:
    item_list = tuple(items)
    paragraph_index_list = tuple(paragraph_indices)
    return _item_body_excerpt(item_list) or _paragraph_excerpt(
        article,
        paragraph_index_list,
        rendered_indices,
    )


def _paragraph_links(
    detail_path: str,
    paragraph_indices: Iterable[int],
) -> tuple[RowOneSavedSignalIndexParagraphLink, ...]:
    links: list[RowOneSavedSignalIndexParagraphLink] = []
    for index in list(paragraph_indices)[:MAX_SAVED_SIGNAL_INDEX_PARAGRAPH_LINKS]:
        paragraph_number = index + 1
        links.append(
            RowOneSavedSignalIndexParagraphLink(
                label=LocalizedText(
                    zh=f"段落 {paragraph_number}",
                    en=f"Paragraph {paragraph_number}",
                ),
                href=(
                    f"{detail_path}#{LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX}-{paragraph_number}"
                ),
            )
        )
    return tuple(links)


def _content_section_path(detail_path: str, section_position: int) -> str:
    return f"{detail_path}#{LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_PREFIX}-{section_position}"


def _source_display_name(article: RowOneLocalArticle) -> str:
    return article.source_name.strip() or "Unknown source"


def _source_key(name: str) -> str:
    return _normalized_key(name)


def _normalized_key(value: str) -> str:
    return " ".join(value.split()).casefold()


def _section_title(edition: RowOneEdition, section_key: str) -> LocalizedText:
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    fallback = section_key.replace("_", " ").title()
    return LocalizedText(zh=fallback, en=fallback)
