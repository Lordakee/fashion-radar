from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.local_article_anchors import local_article_paragraph_anchor
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneReference,
    RowOneStory,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS = 3
SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS_PER_LANE = 3
SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS = 3
SAVED_ARTICLE_LOCAL_RELATED_READS_EXCERPT_CHARS = 180


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadReference:
    name: str
    label: str


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadEvidenceBridge:
    reference: RowOneSavedArticleLocalRelatedReadReference
    current_label: LocalizedText
    current_href: str
    candidate_label: LocalizedText
    candidate_href: str


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadCard:
    candidate_story_id: str
    title: LocalizedText
    source_name: str
    reason: LocalizedText
    excerpt: LocalizedText
    href: str
    references: tuple[RowOneSavedArticleLocalRelatedReadReference, ...] = ()
    evidence_bridges: tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...] = ()


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReadLane:
    key: str
    title: LocalizedText
    dek: LocalizedText
    cards: tuple[RowOneSavedArticleLocalRelatedReadCard, ...]


@dataclass(frozen=True)
class RowOneSavedArticleLocalRelatedReads:
    title: LocalizedText
    dek: LocalizedText
    current_story_id: str
    card_count: int
    cards: tuple[RowOneSavedArticleLocalRelatedReadCard, ...]


@dataclass(frozen=True)
class _ReferenceEntry:
    key: str
    reference: RowOneSavedArticleLocalRelatedReadReference
    paragraph_indices: tuple[int, ...]


@dataclass(frozen=True)
class _Candidate:
    story_order: int
    story: RowOneStory
    article: RowOneLocalArticle
    shared_keys: tuple[str, ...]
    same_section: bool
    same_source: bool
    score: int
    href: str
    references: tuple[RowOneSavedArticleLocalRelatedReadReference, ...]
    evidence_bridges: tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...]


_LANE_COPY = {
    "shared_signal": (
        LocalizedText(en="Shared signals", zh="共同信号"),
        LocalizedText(
            en="Next reads carrying the same named fashion signal.",
            zh="包含同一时尚信号的后续阅读。",
        ),
    ),
    "same_section": (
        LocalizedText(en="Same ROW ONE section", zh="同一 ROW ONE 栏目"),
        LocalizedText(
            en="Next reads filed near this story in today's edition.",
            zh="与本文同属今日相近栏目脉络的后续阅读。",
        ),
    ),
    "same_source": (
        LocalizedText(en="Same source desk", zh="同一来源台"),
        LocalizedText(
            en="Next reads from the same saved local source context.",
            zh="来自同一保存来源语境的后续阅读。",
        ),
    ),
}


def build_row_one_saved_article_local_related_read_lanes(
    cards: Sequence[RowOneSavedArticleLocalRelatedReadCard],
) -> tuple[RowOneSavedArticleLocalRelatedReadLane, ...]:
    deduped_by_lane: dict[str, list[RowOneSavedArticleLocalRelatedReadCard]] = {
        "shared_signal": [],
        "same_section": [],
        "same_source": [],
    }
    seen: set[tuple[str, str]] = set()
    for card in cards:
        dedupe_key = (card.candidate_story_id, card.href)
        if dedupe_key in seen:
            continue
        lane_key = _related_read_lane_key(card)
        if lane_key is None:
            continue
        seen.add(dedupe_key)
        if len(deduped_by_lane[lane_key]) < SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS_PER_LANE:
            deduped_by_lane[lane_key].append(card)

    lanes = [
        lane
        for key in ("shared_signal", "same_section", "same_source")
        if (lane := _related_read_lane(key, tuple(deduped_by_lane[key]))) is not None
    ]
    return tuple(lanes)


def build_row_one_saved_article_local_related_reads(
    *,
    current_story: RowOneStory,
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    local_article_page_hrefs_by_story_id: Mapping[str, str],
    excluded_story_ids: Collection[str] = (),
) -> RowOneSavedArticleLocalRelatedReads | None:
    current_article = local_articles_by_story_id.get(current_story.id)
    if (
        current_article is None
        or current_article.story_id != current_story.id
        or not safe_local_article_story_id(current_story.id)
        or _first_nonblank_paragraph(current_article) is None
    ):
        return None

    current_refs = _article_reference_entries(current_article)
    current_ref_keys = {entry.key for entry in current_refs}
    current_ref_entries_by_key = _reference_entries_by_key(current_refs, current_article)
    excluded = {
        story_id
        for story_id in excluded_story_ids
        if isinstance(story_id, str) and safe_local_article_story_id(story_id)
    }

    candidates: list[_Candidate] = []
    for story_order, candidate_story in enumerate(edition.stories):
        if candidate_story.id == current_story.id or candidate_story.id in excluded:
            continue
        candidate = _candidate(
            story_order=story_order,
            current_story=current_story,
            current_article=current_article,
            current_ref_keys=current_ref_keys,
            current_ref_entries_by_key=current_ref_entries_by_key,
            current_has_content_sections=bool(current_article.content_sections),
            candidate_story=candidate_story,
            local_articles_by_story_id=local_articles_by_story_id,
            local_article_page_hrefs_by_story_id=local_article_page_hrefs_by_story_id,
        )
        if candidate is not None:
            candidates.append(candidate)

    if not candidates:
        return None

    candidates.sort(
        key=lambda candidate: (
            -candidate.score,
            -len(candidate.shared_keys),
            not candidate.same_section,
            not candidate.same_source,
            candidate.story_order,
            candidate.story.id,
        )
    )
    cards = tuple(
        _card(candidate) for candidate in candidates[:SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS]
    )
    if not cards:
        return None
    return RowOneSavedArticleLocalRelatedReads(
        title=LocalizedText(en="Related Saved Local Reads", zh="相关本地保存阅读"),
        dek=LocalizedText(
            en="Same-edition reads connected by references, section, or source.",
            zh="按同日信号、栏目或来源连接的相关阅读。",
        ),
        current_story_id=current_story.id,
        card_count=len(cards),
        cards=cards,
    )


def _related_read_lane_key(card: RowOneSavedArticleLocalRelatedReadCard) -> str | None:
    reason_en = normalize_row_one_paragraph(card.reason.en).casefold()
    reason_zh = normalize_row_one_paragraph(card.reason.zh)
    if reason_en.startswith("shared signal:") or reason_zh.startswith("共同信号："):
        return "shared_signal"
    if reason_en == "same row one section" or reason_zh == "同一 ROW ONE 栏目":
        return "same_section"
    if reason_en == "same source desk" or reason_zh == "同一来源":
        return "same_source"
    return None


def _related_read_lane(
    key: str,
    cards: tuple[RowOneSavedArticleLocalRelatedReadCard, ...],
) -> RowOneSavedArticleLocalRelatedReadLane | None:
    copy = _LANE_COPY.get(key)
    if copy is None or not cards:
        return None
    title, dek = copy
    return RowOneSavedArticleLocalRelatedReadLane(
        key=key,
        title=title,
        dek=dek,
        cards=cards,
    )


def _candidate(
    *,
    story_order: int,
    current_story: RowOneStory,
    current_article: RowOneLocalArticle,
    current_ref_keys: set[str],
    current_ref_entries_by_key: Mapping[str, _ReferenceEntry],
    current_has_content_sections: bool,
    candidate_story: RowOneStory,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    local_article_page_hrefs_by_story_id: Mapping[str, str],
) -> _Candidate | None:
    if not safe_local_article_story_id(candidate_story.id):
        return None
    article = local_articles_by_story_id.get(candidate_story.id)
    if article is None or article.story_id != candidate_story.id:
        return None
    if _first_nonblank_paragraph(article) is None:
        return None
    base_href = _safe_sibling_article_href(
        candidate_story.id,
        local_article_page_hrefs_by_story_id.get(candidate_story.id, ""),
    )
    if base_href is None:
        return None

    entries = _article_reference_entries(article)
    shared_keys = _shared_reference_keys(current_ref_keys, entries)
    same_section = candidate_story.section_key == current_story.section_key
    same_source = _normalized_source(candidate_story.source_name) == _normalized_source(
        current_story.source_name
    )
    if not shared_keys and not same_section and not same_source:
        return None
    score = len(shared_keys) * 100
    if same_section:
        score += 20
    if same_source:
        score += 10
    if current_has_content_sections and entries:
        score += 5
    if score <= 0:
        return None

    paragraph_index = _shared_reference_paragraph(entries, shared_keys, article)
    if paragraph_index is None:
        paragraph_index = _first_nonblank_paragraph(article)
    href = (
        f"{base_href}#{local_article_paragraph_anchor(paragraph_index)}"
        if paragraph_index is not None
        else f"{base_href}#local-article-digest"
    )
    return _Candidate(
        story_order=story_order,
        story=candidate_story,
        article=article,
        shared_keys=shared_keys,
        same_section=same_section,
        same_source=same_source,
        score=score,
        href=href,
        references=_reference_chips(entries, shared_keys),
        evidence_bridges=_evidence_bridges(
            current_article=current_article,
            candidate_article=article,
            candidate_base_href=base_href,
            current_entries_by_key=current_ref_entries_by_key,
            candidate_entries=entries,
            shared_keys=shared_keys,
        ),
    )


def _card(candidate: _Candidate) -> RowOneSavedArticleLocalRelatedReadCard:
    title = _article_title(candidate.story, candidate.article)
    return RowOneSavedArticleLocalRelatedReadCard(
        candidate_story_id=candidate.story.id,
        title=LocalizedText(en=title, zh=title),
        source_name=_source_name(candidate.story, candidate.article),
        reason=_reason(candidate),
        excerpt=_localized_excerpt(candidate.article),
        href=candidate.href,
        references=candidate.references,
        evidence_bridges=candidate.evidence_bridges,
    )


def _safe_sibling_article_href(story_id: str, href: str) -> str | None:
    clean = href.strip()
    expected = f"{story_id}.html"
    if clean != href or clean != expected:
        return None
    if (
        not safe_local_article_story_id(story_id)
        or not clean.endswith(".html")
        or any(character.isspace() for character in clean)
        or "://" in clean
        or clean.startswith(("//", "/", "."))
        or "/" in clean
        or "\\" in clean
        or ".." in clean
    ):
        return None
    return clean


def _article_reference_entries(article: RowOneLocalArticle) -> tuple[_ReferenceEntry, ...]:
    entries: list[_ReferenceEntry] = []
    seen: set[tuple[str, str]] = set()
    for section in article.content_sections:
        for item in section.items:
            valid_indices = tuple(
                index
                for value in item.paragraph_indices
                if (index := _valid_paragraph_index(value, article)) is not None
            )
            for reference in item.references:
                key = _reference_key(reference)
                if not key:
                    continue
                rendered = _rendered_reference(reference)
                if rendered is None:
                    continue
                seen_key = (key, rendered.label.casefold())
                if seen_key in seen:
                    continue
                seen.add(seen_key)
                entries.append(
                    _ReferenceEntry(
                        key=key,
                        reference=rendered,
                        paragraph_indices=valid_indices,
                    )
                )
    return tuple(entries)


def _reference_entries_by_key(
    entries: tuple[_ReferenceEntry, ...],
    article: RowOneLocalArticle,
) -> dict[str, _ReferenceEntry]:
    by_key: dict[str, _ReferenceEntry] = {}
    for entry in entries:
        if (
            entry.key
            and entry.key not in by_key
            and _first_valid_entry_paragraph(entry, article) is not None
        ):
            by_key[entry.key] = entry
    return by_key


def _reference_key(reference: RowOneReference) -> str:
    return normalize_row_one_paragraph(reference.name).casefold()


def _rendered_reference(
    reference: RowOneReference,
) -> RowOneSavedArticleLocalRelatedReadReference | None:
    name = normalize_row_one_paragraph(reference.name)
    label = normalize_row_one_paragraph(reference.label) or normalize_row_one_paragraph(
        reference.type
    )
    if not name:
        return None
    return RowOneSavedArticleLocalRelatedReadReference(name=name, label=label)


def _shared_reference_keys(
    current_ref_keys: set[str],
    candidate_entries: tuple[_ReferenceEntry, ...],
) -> tuple[str, ...]:
    shared: list[str] = []
    seen: set[str] = set()
    for entry in candidate_entries:
        if entry.key in current_ref_keys and entry.key not in seen:
            seen.add(entry.key)
            shared.append(entry.key)
    return tuple(shared)


def _reference_chips(
    entries: tuple[_ReferenceEntry, ...],
    shared_keys: tuple[str, ...],
) -> tuple[RowOneSavedArticleLocalRelatedReadReference, ...]:
    rendered: list[RowOneSavedArticleLocalRelatedReadReference] = []
    seen: set[tuple[str, str]] = set()

    def add(entry: _ReferenceEntry) -> None:
        if len(rendered) >= SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS:
            return
        key = (entry.reference.name.casefold(), entry.reference.label.casefold())
        if key in seen:
            return
        seen.add(key)
        rendered.append(entry.reference)

    for shared_key in shared_keys:
        for entry in entries:
            if entry.key == shared_key:
                add(entry)
                break
    for entry in entries:
        add(entry)
    return tuple(rendered)


def _shared_reference_paragraph(
    entries: tuple[_ReferenceEntry, ...],
    shared_keys: tuple[str, ...],
    article: RowOneLocalArticle,
) -> int | None:
    shared = set(shared_keys)
    for entry in entries:
        if entry.key not in shared:
            continue
        for index in entry.paragraph_indices:
            if _valid_paragraph_index(index, article) is not None:
                return index
    return None


def _evidence_bridges(
    *,
    current_article: RowOneLocalArticle,
    candidate_article: RowOneLocalArticle,
    candidate_base_href: str,
    current_entries_by_key: Mapping[str, _ReferenceEntry],
    candidate_entries: tuple[_ReferenceEntry, ...],
    shared_keys: tuple[str, ...],
) -> tuple[RowOneSavedArticleLocalRelatedReadEvidenceBridge, ...]:
    bridges: list[RowOneSavedArticleLocalRelatedReadEvidenceBridge] = []
    candidate_entries_by_key = _reference_entries_by_key(candidate_entries, candidate_article)
    for shared_key in shared_keys:
        if len(bridges) >= SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS:
            break
        current_entry = current_entries_by_key.get(shared_key)
        candidate_entry = candidate_entries_by_key.get(shared_key)
        if current_entry is None or candidate_entry is None:
            continue
        current_index = _first_valid_entry_paragraph(current_entry, current_article)
        candidate_index = _first_valid_entry_paragraph(candidate_entry, candidate_article)
        if current_index is None or candidate_index is None:
            continue
        bridges.append(
            RowOneSavedArticleLocalRelatedReadEvidenceBridge(
                reference=candidate_entry.reference,
                current_label=LocalizedText(
                    en=f"Here ¶{current_index + 1}",
                    zh=f"本文 ¶{current_index + 1}",
                ),
                current_href=f"#{local_article_paragraph_anchor(current_index)}",
                candidate_label=LocalizedText(
                    en=f"Next read ¶{candidate_index + 1}",
                    zh=f"下一篇 ¶{candidate_index + 1}",
                ),
                candidate_href=(
                    f"{candidate_base_href}#{local_article_paragraph_anchor(candidate_index)}"
                ),
            )
        )
    return tuple(bridges)


def _first_valid_entry_paragraph(
    entry: _ReferenceEntry,
    article: RowOneLocalArticle,
) -> int | None:
    for index in entry.paragraph_indices:
        if _valid_paragraph_index(index, article) is not None:
            return index
    return None


def _valid_paragraph_index(index: object, article: RowOneLocalArticle) -> int | None:
    if isinstance(index, bool) or not isinstance(index, int):
        return None
    if index < 0 or index >= len(article.paragraphs):
        return None
    if not normalize_row_one_paragraph(article.paragraphs[index]):
        return None
    return index


def _first_nonblank_paragraph(article: RowOneLocalArticle) -> int | None:
    for index, paragraph in enumerate(article.paragraphs):
        if normalize_row_one_paragraph(paragraph):
            return index
    return None


def _localized_excerpt(article: RowOneLocalArticle) -> LocalizedText:
    index = _first_nonblank_paragraph(article)
    if index is None:
        return LocalizedText(en="", zh="")
    en = _excerpt(article.paragraphs[index])
    zh = (
        _excerpt(article.paragraphs_zh[index])
        if len(article.paragraphs_zh) == len(article.paragraphs)
        and index < len(article.paragraphs_zh)
        and normalize_row_one_paragraph(article.paragraphs_zh[index])
        else en
    )
    return LocalizedText(en=en, zh=zh)


def _excerpt(value: str) -> str:
    text = normalize_row_one_paragraph(value)
    if len(text) <= SAVED_ARTICLE_LOCAL_RELATED_READS_EXCERPT_CHARS:
        return text
    return f"{text[:SAVED_ARTICLE_LOCAL_RELATED_READS_EXCERPT_CHARS].rstrip()}..."


def _article_title(story: RowOneStory, article: RowOneLocalArticle) -> str:
    return (
        normalize_row_one_paragraph(story.headline)
        or normalize_row_one_paragraph(article.title or "")
        or story.id
    )


def _source_name(story: RowOneStory, article: RowOneLocalArticle) -> str:
    return normalize_row_one_paragraph(article.source_name) or normalize_row_one_paragraph(
        story.source_name
    )


def _normalized_source(value: str) -> str:
    return normalize_row_one_paragraph(value).casefold()


def _reason(candidate: _Candidate) -> LocalizedText:
    if candidate.shared_keys:
        reference = candidate.references[0] if candidate.references else None
        name = reference.name if reference is not None else "shared signal"
        return LocalizedText(
            en=f"Shared signal: {name}",
            zh=f"共同信号：{name}",
        )
    if candidate.same_section:
        return LocalizedText(en="Same ROW ONE section", zh="同一 ROW ONE 栏目")
    return LocalizedText(en="Same source desk", zh="同一来源")
