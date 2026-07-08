from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.detail_routes import is_safe_row_one_detail_path
from fashion_radar.row_one.models import LocalizedText, RowOneEdition, RowOneLocalArticle
from fashion_radar.row_one.saved_article_key_signals import (
    RowOneSavedArticleKeySignalGroup,
    build_row_one_saved_article_key_signals,
)

DAILY_LOCAL_KEY_SIGNALS_DIGEST_WHY_LIMIT = 4
DAILY_LOCAL_KEY_SIGNALS_DIGEST_REFERENCE_LIMIT = 6
DAILY_LOCAL_KEY_SIGNALS_DIGEST_THEME_LIMIT = 8

_REFERENCE_GROUP_KEYS = ("brands", "products", "people")
_GROUP_TITLES = {
    "why_it_matters": LocalizedText(en="Why It Matters", zh="为什么重要"),
    "brands": LocalizedText(en="Brands", zh="品牌"),
    "products": LocalizedText(en="Products", zh="产品"),
    "people": LocalizedText(en="People", zh="人物"),
    "themes": LocalizedText(en="Themes", zh="主题"),
}
_LOCAL_ARTICLE_FRAGMENT_RE = re.compile(
    r"(?:local-article-paragraph|local-article-content-section)-[1-9][0-9]*"
)


@dataclass(frozen=True)
class RowOneDailyLocalKeySignalsDigestEntry:
    title: LocalizedText
    body: LocalizedText | None
    href: str
    source_name: str
    support_count: int = 1


@dataclass(frozen=True)
class RowOneDailyLocalKeySignalsDigestGroup:
    key: str
    title: LocalizedText
    entries: tuple[RowOneDailyLocalKeySignalsDigestEntry, ...]
    total_count: int


@dataclass(frozen=True)
class RowOneDailyLocalKeySignalsDigest:
    article_count: int
    groups: tuple[RowOneDailyLocalKeySignalsDigestGroup, ...]
    title: LocalizedText = field(
        default_factory=lambda: LocalizedText(
            en="Daily Local Key Signals Digest",
            zh="每日本地关键信号摘要",
        )
    )
    dek: LocalizedText = field(
        default_factory=lambda: LocalizedText(
            en="A cross-article read of why today's saved fashion sources matter.",
            zh="跨文章整理今日已保存时尚来源的关键信号。",
        )
    )


def build_row_one_daily_local_key_signals_digest(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneDailyLocalKeySignalsDigest | None:
    why_entries: list[RowOneDailyLocalKeySignalsDigestEntry] = []
    reference_entries: dict[str, dict[str, RowOneDailyLocalKeySignalsDigestEntry]] = {
        key: {} for key in _REFERENCE_GROUP_KEYS
    }
    reference_totals = {key: 0 for key in _REFERENCE_GROUP_KEYS}
    theme_entries: dict[str, RowOneDailyLocalKeySignalsDigestEntry] = {}
    theme_total = 0
    article_count = 0

    for story in edition.stories:
        if not safe_local_article_story_id(story.id):
            continue
        if not is_safe_row_one_detail_path(story.detail_path):
            continue
        local_article = local_articles_by_story_id.get(story.id)
        if local_article is None or local_article.story_id != story.id:
            continue

        article_href = _daily_local_key_signals_digest_article_href(story.id)
        if article_href is None:
            continue
        key_signals = build_row_one_saved_article_key_signals(
            story=story,
            local_article=local_article,
        )
        if key_signals is None:
            continue

        article_count += 1
        source_name = key_signals.source_name.strip() or local_article.source_name.strip()
        article_title = _article_title(story.headline, local_article.title)
        for group in key_signals.groups:
            if group.key == "why_it_matters":
                why_entry = _why_entry(
                    group,
                    title=article_title,
                    href=article_href,
                    source_name=source_name,
                )
                if why_entry is not None:
                    why_entries.append(why_entry)
                continue
            if group.key in _REFERENCE_GROUP_KEYS:
                reference_totals[group.key] += group.reference_count
                _add_reference_entries(
                    reference_entries[group.key],
                    group,
                    story_id=story.id,
                    article_href=article_href,
                    source_name=source_name,
                )
                continue
            if group.key == "themes":
                theme_total += group.theme_count
                _add_theme_entries(
                    theme_entries,
                    group,
                    story_id=story.id,
                    article_href=article_href,
                    source_name=source_name,
                )

    groups = _digest_groups(
        why_entries=why_entries,
        reference_entries=reference_entries,
        reference_totals=reference_totals,
        theme_entries=theme_entries,
        theme_total=theme_total,
    )
    if article_count == 0 or not groups:
        return None
    return RowOneDailyLocalKeySignalsDigest(
        article_count=article_count,
        groups=groups,
    )


def _digest_groups(
    *,
    why_entries: list[RowOneDailyLocalKeySignalsDigestEntry],
    reference_entries: dict[str, dict[str, RowOneDailyLocalKeySignalsDigestEntry]],
    reference_totals: dict[str, int],
    theme_entries: dict[str, RowOneDailyLocalKeySignalsDigestEntry],
    theme_total: int,
) -> tuple[RowOneDailyLocalKeySignalsDigestGroup, ...]:
    groups: list[RowOneDailyLocalKeySignalsDigestGroup] = []
    if why_entries:
        groups.append(
            RowOneDailyLocalKeySignalsDigestGroup(
                key="why_it_matters",
                title=_GROUP_TITLES["why_it_matters"],
                entries=tuple(why_entries[:DAILY_LOCAL_KEY_SIGNALS_DIGEST_WHY_LIMIT]),
                total_count=len(why_entries),
            )
        )
    for key in _REFERENCE_GROUP_KEYS:
        entries = tuple(reference_entries[key].values())
        if not entries:
            continue
        groups.append(
            RowOneDailyLocalKeySignalsDigestGroup(
                key=key,
                title=_GROUP_TITLES[key],
                entries=entries[:DAILY_LOCAL_KEY_SIGNALS_DIGEST_REFERENCE_LIMIT],
                total_count=reference_totals[key],
            )
        )
    theme_values = tuple(theme_entries.values())
    if theme_values:
        groups.append(
            RowOneDailyLocalKeySignalsDigestGroup(
                key="themes",
                title=_GROUP_TITLES["themes"],
                entries=theme_values[:DAILY_LOCAL_KEY_SIGNALS_DIGEST_THEME_LIMIT],
                total_count=theme_total,
            )
        )
    return tuple(groups)


def _why_entry(
    group: RowOneSavedArticleKeySignalGroup,
    *,
    title: LocalizedText,
    href: str,
    source_name: str,
) -> RowOneDailyLocalKeySignalsDigestEntry | None:
    if group.statement is None:
        return None
    return RowOneDailyLocalKeySignalsDigestEntry(
        title=title,
        body=group.statement,
        href=href,
        source_name=source_name,
        support_count=max(group.support_count, 1),
    )


def _add_reference_entries(
    entries: dict[str, RowOneDailyLocalKeySignalsDigestEntry],
    group: RowOneSavedArticleKeySignalGroup,
    *,
    story_id: str,
    article_href: str,
    source_name: str,
) -> None:
    href = _first_evidence_href(group, story_id=story_id) or article_href
    seen_in_group: set[str] = set()
    for reference in group.references:
        title = _localized(reference.name)
        key = _normalized_key(title.en)
        if not key or key in seen_in_group:
            continue
        seen_in_group.add(key)
        if key in entries:
            current = entries[key]
            entries[key] = RowOneDailyLocalKeySignalsDigestEntry(
                title=current.title,
                body=current.body,
                href=current.href,
                source_name=current.source_name,
                support_count=current.support_count + 1,
            )
            continue
        entries[key] = RowOneDailyLocalKeySignalsDigestEntry(
            title=title,
            body=group.statement,
            href=href,
            source_name=source_name,
            support_count=1,
        )


def _add_theme_entries(
    entries: dict[str, RowOneDailyLocalKeySignalsDigestEntry],
    group: RowOneSavedArticleKeySignalGroup,
    *,
    story_id: str,
    article_href: str,
    source_name: str,
) -> None:
    seen_in_group: set[str] = set()
    for theme in group.themes:
        key = _normalized_key(theme.label.en)
        if not key or key in seen_in_group:
            continue
        seen_in_group.add(key)
        if key in entries:
            current = entries[key]
            entries[key] = RowOneDailyLocalKeySignalsDigestEntry(
                title=current.title,
                body=current.body,
                href=current.href,
                source_name=current.source_name,
                support_count=current.support_count + 1,
            )
            continue
        entries[key] = RowOneDailyLocalKeySignalsDigestEntry(
            title=theme.label,
            body=group.statement,
            href=_daily_local_key_signals_digest_anchor_href(story_id, theme.href) or article_href,
            source_name=source_name,
            support_count=1,
        )


def _first_evidence_href(
    group: RowOneSavedArticleKeySignalGroup,
    *,
    story_id: str,
) -> str | None:
    for evidence in group.evidence:
        href = _daily_local_key_signals_digest_anchor_href(story_id, evidence.href)
        if href is not None:
            return href
    return None


def _daily_local_key_signals_digest_article_href(story_id: str) -> str | None:
    if not safe_local_article_story_id(story_id):
        return None
    return f"articles/{story_id}.html#saved-article-key-signals-title"


def _daily_local_key_signals_digest_anchor_href(story_id: str, href: str) -> str | None:
    if not safe_local_article_story_id(story_id):
        return None
    if not isinstance(href, str) or href != href.strip() or not href.startswith("#"):
        return None
    fragment = href[1:]
    if _LOCAL_ARTICLE_FRAGMENT_RE.fullmatch(fragment) is None:
        return None
    return f"articles/{story_id}.html#{fragment}"


def _article_title(headline: str, local_title: str | None) -> LocalizedText:
    title = _normalized_text(local_title) or _normalized_text(headline)
    return LocalizedText(en=title, zh=title)


def _localized(value: str) -> LocalizedText:
    text = _normalized_text(value)
    return LocalizedText(en=text, zh=text)


def _normalized_key(value: str) -> str:
    return _normalized_text(value).casefold()


def _normalized_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().split())
