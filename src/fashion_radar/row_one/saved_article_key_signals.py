from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_reference_atlas import (
    row_one_saved_article_reference_bucket,
)

SAVED_ARTICLE_KEY_SIGNALS_REFERENCE_LIMIT = 5
SAVED_ARTICLE_KEY_SIGNALS_THEME_LIMIT = 8
SAVED_ARTICLE_KEY_SIGNALS_EVIDENCE_LIMIT = 3
SAVED_ARTICLE_KEY_SIGNALS_EXCERPT_CHARS = 150
SAVED_ARTICLE_KEY_SIGNALS_STATEMENT_CHARS = 180
_KEY_SIGNAL_REFERENCE_BUCKETS = ("brands", "products", "people")


@dataclass(frozen=True)
class RowOneSavedArticleKeySignalEvidence:
    index: int
    href: str
    excerpt: LocalizedText


@dataclass(frozen=True)
class RowOneSavedArticleKeySignalReference:
    name: str
    reference_type: str
    label: str
    bucket: str


@dataclass(frozen=True)
class RowOneSavedArticleKeySignalTheme:
    label: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneSavedArticleKeySignalGroup:
    key: str
    title: LocalizedText
    statement: LocalizedText | None = None
    references: tuple[RowOneSavedArticleKeySignalReference, ...] = ()
    themes: tuple[RowOneSavedArticleKeySignalTheme, ...] = ()
    evidence: tuple[RowOneSavedArticleKeySignalEvidence, ...] = ()
    support_count: int = 0
    reference_count: int = 0
    theme_count: int = 0
    evidence_count: int = 0


@dataclass(frozen=True)
class RowOneSavedArticleKeySignals:
    title: LocalizedText
    source_name: str
    groups: tuple[RowOneSavedArticleKeySignalGroup, ...]


def build_row_one_saved_article_key_signals(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleKeySignals | None:
    if story.id != local_article.story_id or not safe_local_article_story_id(story.id):
        return None
    if not any(paragraph.strip() for paragraph in local_article.paragraphs):
        return None

    reference_groups = _reference_groups(local_article)
    displayed_reference_names = {
        _normalized_key(reference.name)
        for group in reference_groups
        for reference in group.references
    }
    groups = [
        group
        for group in (
            _why_it_matters_group(story, local_article),
            *reference_groups,
            _themes_group(local_article, displayed_reference_names),
        )
        if group is not None and _meaningful_group(group)
    ]
    if not groups:
        return None

    return RowOneSavedArticleKeySignals(
        title=LocalizedText(en="Saved Article Key Signals", zh="已保存文章关键信号"),
        source_name=local_article.source_name.strip() or story.source_name.strip(),
        groups=tuple(groups),
    )


def _why_it_matters_group(
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleKeySignalGroup | None:
    statement: LocalizedText | None = None
    for section in local_article.brief_sections:
        if section.key != "why_it_matters":
            continue
        statement = _nonblank_localized_text(section.body)
        if statement is not None:
            break
    if statement is None:
        statement = _nonblank_localized_text(story.why_it_matters)
    if statement is None:
        return None
    return RowOneSavedArticleKeySignalGroup(
        key="why_it_matters",
        title=LocalizedText(en="Why It Matters", zh="为什么重要"),
        statement=_truncate_localized_text(
            statement,
            SAVED_ARTICLE_KEY_SIGNALS_STATEMENT_CHARS,
        ),
        support_count=1,
    )


def _reference_groups(
    local_article: RowOneLocalArticle,
) -> tuple[RowOneSavedArticleKeySignalGroup, ...]:
    collected: dict[str, list[RowOneSavedArticleKeySignalReference]] = {
        bucket: [] for bucket in _KEY_SIGNAL_REFERENCE_BUCKETS
    }
    seen_references: dict[str, set[str]] = {
        bucket: set() for bucket in _KEY_SIGNAL_REFERENCE_BUCKETS
    }
    statements: dict[str, LocalizedText] = {}
    evidence: dict[str, list[RowOneSavedArticleKeySignalEvidence]] = {
        bucket: [] for bucket in _KEY_SIGNAL_REFERENCE_BUCKETS
    }
    seen_evidence: dict[str, set[int]] = {bucket: set() for bucket in _KEY_SIGNAL_REFERENCE_BUCKETS}
    support_counts: dict[str, int] = {bucket: 0 for bucket in _KEY_SIGNAL_REFERENCE_BUCKETS}
    reference_counts: dict[str, int] = {bucket: 0 for bucket in _KEY_SIGNAL_REFERENCE_BUCKETS}
    evidence_counts: dict[str, int] = {bucket: 0 for bucket in _KEY_SIGNAL_REFERENCE_BUCKETS}

    for _section_position, section in enumerate(local_article.content_sections, start=1):
        for item in section.items:
            item_buckets = _item_reference_buckets(item)
            for bucket in item_buckets:
                support_counts[bucket] += 1
                if bucket not in statements:
                    statement = _nonblank_localized_text(
                        _support_statement(item, section),
                    )
                    if statement is not None:
                        statements[bucket] = _truncate_localized_text(
                            statement,
                            SAVED_ARTICLE_KEY_SIGNALS_STATEMENT_CHARS,
                        )
                for paragraph_index in _valid_paragraph_indices(
                    item.paragraph_indices,
                    local_article=local_article,
                ):
                    if paragraph_index in seen_evidence[bucket]:
                        continue
                    seen_evidence[bucket].add(paragraph_index)
                    evidence_counts[bucket] += 1
                    if len(evidence[bucket]) >= SAVED_ARTICLE_KEY_SIGNALS_EVIDENCE_LIMIT:
                        continue
                    evidence[bucket].append(
                        _paragraph(paragraph_index, local_article=local_article)
                    )

            for reference in item.references:
                bucket = row_one_saved_article_reference_bucket(reference)
                if bucket not in _KEY_SIGNAL_REFERENCE_BUCKETS:
                    continue
                name = _normalized_text(reference.name)
                if not name:
                    continue
                reference_key = name.casefold()
                if reference_key in seen_references[bucket]:
                    continue
                seen_references[bucket].add(reference_key)
                reference_counts[bucket] += 1
                if len(collected[bucket]) >= SAVED_ARTICLE_KEY_SIGNALS_REFERENCE_LIMIT:
                    continue
                collected[bucket].append(
                    RowOneSavedArticleKeySignalReference(
                        name=name,
                        reference_type=_normalized_text(reference.type),
                        label=_normalized_text(reference.label),
                        bucket=bucket,
                    )
                )

    groups: list[RowOneSavedArticleKeySignalGroup] = []
    for bucket, title in (
        ("brands", LocalizedText(en="Brands", zh="品牌")),
        ("products", LocalizedText(en="Products", zh="产品")),
        ("people", LocalizedText(en="People", zh="人物")),
    ):
        group = RowOneSavedArticleKeySignalGroup(
            key=bucket,
            title=title,
            statement=statements.get(bucket),
            references=tuple(collected[bucket]),
            evidence=tuple(evidence[bucket]),
            support_count=support_counts[bucket],
            reference_count=reference_counts[bucket],
            evidence_count=evidence_counts[bucket],
        )
        if _meaningful_group(group):
            groups.append(group)
    return tuple(groups)


def _item_reference_buckets(
    item: RowOneLocalArticleContentItem,
) -> set[str]:
    buckets: set[str] = set()
    for reference in item.references:
        if not _normalized_text(reference.name):
            continue
        bucket = row_one_saved_article_reference_bucket(reference)
        if bucket in _KEY_SIGNAL_REFERENCE_BUCKETS:
            buckets.add(bucket)
    return buckets


def _themes_group(
    local_article: RowOneLocalArticle,
    displayed_reference_names: set[str],
) -> RowOneSavedArticleKeySignalGroup | None:
    themes: list[RowOneSavedArticleKeySignalTheme] = []
    seen: set[str] = set()
    total = 0
    for section_position, section in enumerate(local_article.content_sections, start=1):
        href = f"#local-article-content-section-{section_position}"
        for label in _theme_labels(section):
            normalized = _normalized_key(label.en)
            if not normalized or normalized in displayed_reference_names or normalized in seen:
                continue
            seen.add(normalized)
            total += 1
            if len(themes) >= SAVED_ARTICLE_KEY_SIGNALS_THEME_LIMIT:
                continue
            themes.append(RowOneSavedArticleKeySignalTheme(label=label, href=href))
    if not themes:
        return None
    return RowOneSavedArticleKeySignalGroup(
        key="themes",
        title=LocalizedText(en="Themes", zh="主题"),
        themes=tuple(themes),
        theme_count=total,
    )


def _theme_labels(
    section: RowOneLocalArticleContentSection,
) -> tuple[LocalizedText, ...]:
    labels: list[LocalizedText] = []
    section_title = _nonblank_localized_text(section.title)
    if section_title is not None:
        labels.append(section_title)
    for item in section.items:
        item_label = _nonblank_localized_text(item.label)
        if item_label is not None:
            labels.append(item_label)
    return tuple(labels)


def _support_statement(
    item: RowOneLocalArticleContentItem,
    section: RowOneLocalArticleContentSection,
) -> LocalizedText:
    for value in (item.body, item.label, section.title):
        if value is None:
            continue
        text = _nonblank_localized_text(value)
        if text is not None:
            return text
    return LocalizedText(en="", zh="")


def _nonblank_localized_text(value: LocalizedText) -> LocalizedText | None:
    en = _normalized_text(value.en)
    zh = _normalized_text(value.zh)
    if not en and not zh:
        return None
    return LocalizedText(en=en or zh, zh=zh or en)


def _truncate_localized_text(value: LocalizedText, limit: int) -> LocalizedText:
    return LocalizedText(
        en=_truncate(value.en, limit),
        zh=_truncate(value.zh, limit),
    )


def _valid_paragraph_indices(
    values: list[int],
    *,
    local_article: RowOneLocalArticle,
) -> list[int]:
    valid: list[int] = []
    seen: set[int] = set()
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        if value < 0 or value >= len(local_article.paragraphs) or value in seen:
            continue
        if not local_article.paragraphs[value].strip():
            continue
        seen.add(value)
        valid.append(value)
    return valid


def _paragraph(
    index: int,
    *,
    local_article: RowOneLocalArticle,
) -> RowOneSavedArticleKeySignalEvidence:
    en = _truncate(
        _normalized_text(local_article.paragraphs[index]),
        SAVED_ARTICLE_KEY_SIGNALS_EXCERPT_CHARS,
    )
    zh = (
        _truncate(
            _normalized_text(local_article.paragraphs_zh[index]),
            SAVED_ARTICLE_KEY_SIGNALS_EXCERPT_CHARS,
        )
        if len(local_article.paragraphs_zh) == len(local_article.paragraphs)
        and index < len(local_article.paragraphs_zh)
        and local_article.paragraphs_zh[index].strip()
        else en
    )
    return RowOneSavedArticleKeySignalEvidence(
        index=index,
        href=f"#local-article-paragraph-{index + 1}",
        excerpt=LocalizedText(en=en, zh=zh),
    )


def _meaningful_group(group: RowOneSavedArticleKeySignalGroup) -> bool:
    return bool(
        (group.statement and (group.statement.en.strip() or group.statement.zh.strip()))
        or group.references
        or group.themes
        or group.evidence
    )


def _normalized_text(value: str) -> str:
    return " ".join(value.strip().split())


def _normalized_key(value: str) -> str:
    return _normalized_text(value).casefold()


def _truncate(value: str, limit: int) -> str:
    text = _normalized_text(value)
    if len(text) <= limit:
        return text
    suffix = "..."
    if limit <= len(suffix):
        return suffix[:limit]
    return f"{text[: limit - len(suffix)].rstrip()}{suffix}"
