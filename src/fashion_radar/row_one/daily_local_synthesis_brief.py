from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.local_article_synthesis_brief import (
    RowOneLocalArticleSynthesisAnchor,
    build_row_one_local_article_synthesis_brief,
)
from fashion_radar.row_one.models import LocalizedText, RowOneEdition, RowOneLocalArticle
from fashion_radar.row_one.text import normalize_row_one_paragraph

DAILY_LOCAL_SYNTHESIS_BRIEF_MAX_CARDS = 3
DAILY_LOCAL_SYNTHESIS_BRIEF_CARD_READ_CHARS = 150
DAILY_LOCAL_SYNTHESIS_BRIEF_CARD_ADDS_CHARS = 140
DAILY_LOCAL_SYNTHESIS_BRIEF_MAX_EVIDENCE_LINKS = 2
DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_CHARS = 180
DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS = 56
DAILY_LOCAL_SYNTHESIS_BRIEF_THESIS_CHARS = 160


@dataclass(frozen=True)
class RowOneDailyLocalSynthesisEvidenceLink:
    label: LocalizedText
    href: str
    support: LocalizedText | None = None


@dataclass(frozen=True)
class RowOneDailyLocalSynthesisBriefCard:
    title: LocalizedText
    source_name: str
    href: str
    read: LocalizedText
    adds: LocalizedText
    route_label: LocalizedText
    evidence_links: tuple[RowOneDailyLocalSynthesisEvidenceLink, ...] = ()


@dataclass(frozen=True)
class RowOneDailyLocalSynthesisBrief:
    title: LocalizedText
    dek: LocalizedText
    opening_read: LocalizedText
    thesis: LocalizedText
    article_count: int
    source_count: int
    card_count: int
    cards: tuple[RowOneDailyLocalSynthesisBriefCard, ...]
    basis_note: LocalizedText


@dataclass(frozen=True)
class _Candidate:
    card: RowOneDailyLocalSynthesisBriefCard
    thesis: LocalizedText


def build_row_one_daily_local_synthesis_brief(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str],
) -> RowOneDailyLocalSynthesisBrief | None:
    candidates: list[_Candidate] = []
    seen_title_hrefs: set[tuple[str, str]] = set()
    seen_reads: set[str] = set()

    for story in edition.stories:
        article = local_articles_by_story_id.get(story.id)
        if article is None or article.story_id != story.id:
            continue
        page_href = _safe_article_page_href(story.id, article_hrefs_by_story_id.get(story.id))
        if page_href is None:
            continue
        synthesis = build_row_one_local_article_synthesis_brief(
            story=story,
            local_article=article,
        )
        if synthesis is None:
            continue

        title_text = article.title or story.headline or story.id
        title = _localized_text(title_text, title_text)
        title_key = _key(title.en or title.zh)
        title_href_key = (title_key, page_href)
        if title_href_key in seen_title_hrefs:
            continue

        read = _clean_localized(synthesis.lead, DAILY_LOCAL_SYNTHESIS_BRIEF_CARD_READ_CHARS)
        read_key = _localized_key(read)
        if not read_key or read_key in seen_reads:
            continue

        adds = _clean_localized(synthesis.article_adds, DAILY_LOCAL_SYNTHESIS_BRIEF_CARD_ADDS_CHARS)
        source_name = normalize_row_one_paragraph(
            synthesis.source_name
        ) or normalize_row_one_paragraph(story.source_name)
        card = RowOneDailyLocalSynthesisBriefCard(
            title=title,
            source_name=source_name,
            href=page_href,
            read=read,
            adds=adds,
            route_label=LocalizedText(en="Read the saved article", zh="阅读保存文章"),
            evidence_links=_evidence_links(
                page_href=page_href,
                anchors=synthesis.anchors,
            ),
        )
        candidates.append(
            _Candidate(
                card=card,
                thesis=_clean_localized(synthesis.thesis, DAILY_LOCAL_SYNTHESIS_BRIEF_THESIS_CHARS),
            )
        )
        seen_title_hrefs.add(title_href_key)
        seen_reads.add(read_key)

    if len(candidates) < 2:
        return None

    cards = tuple(
        candidate.card for candidate in candidates[:DAILY_LOCAL_SYNTHESIS_BRIEF_MAX_CARDS]
    )
    source_names = {
        source_name
        for candidate in candidates
        if (source_name := normalize_row_one_paragraph(candidate.card.source_name).casefold())
    }
    return RowOneDailyLocalSynthesisBrief(
        title=LocalizedText(en="Daily Local Synthesis Brief", zh="每日本地综合简报"),
        dek=LocalizedText(
            en="A cross-article read assembled from today's saved local text.",
            zh="基于今日已保存本地正文整理出的跨文章判断。",
        ),
        opening_read=_opening_read(cards),
        thesis=_first_distinct_thesis(candidates),
        article_count=len(candidates),
        source_count=len(source_names),
        card_count=len(cards),
        cards=cards,
        basis_note=LocalizedText(
            en=(
                "Built from current-edition ROW ONE stories and saved local article synthesis "
                "already generated for article pages."
            ),
            zh="基于当前版本 ROW ONE 故事与文章页已生成的本地文章综合简报整理。",
        ),
    )


def _safe_article_page_href(story_id: str, href: object) -> str | None:
    if not safe_local_article_story_id(story_id) or not isinstance(href, str):
        return None
    if href != href.strip() or not href or any(character.isspace() for character in href):
        return None
    if (
        "://" in href
        or "//" in href
        or "?" in href
        or "#" in href
        or href.startswith((".", "/", "//"))
    ):
        return None
    path = PurePosixPath(href)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in ("", ".", "..", "index.html")
        or ".." in path.parts
        or not path.name.endswith(".html")
    ):
        return None
    mapped_story_id = path.name.removesuffix(".html")
    if mapped_story_id != story_id or not safe_local_article_story_id(mapped_story_id):
        return None
    return path.name


def _evidence_links(
    *,
    page_href: str,
    anchors: tuple[RowOneLocalArticleSynthesisAnchor, ...],
) -> tuple[RowOneDailyLocalSynthesisEvidenceLink, ...]:
    links: list[RowOneDailyLocalSynthesisEvidenceLink] = []
    seen_labels: set[str] = set()
    for anchor in anchors:
        href = _safe_evidence_href(page_href, anchor.href)
        label = _clean_localized(anchor.label, DAILY_LOCAL_SYNTHESIS_BRIEF_CARD_ADDS_CHARS)
        label_key = _localized_key(label)
        if href is None or not label_key:
            continue
        if label_key in seen_labels:
            continue
        support = (
            _clean_localized(anchor.support, DAILY_LOCAL_SYNTHESIS_BRIEF_CARD_ADDS_CHARS)
            if anchor.support is not None
            else None
        )
        links.append(
            RowOneDailyLocalSynthesisEvidenceLink(
                label=label,
                href=href,
                support=support,
            )
        )
        seen_labels.add(label_key)
        if len(links) >= DAILY_LOCAL_SYNTHESIS_BRIEF_MAX_EVIDENCE_LINKS:
            break
    return tuple(links)


def _safe_evidence_href(page_href: str, fragment_href: object) -> str | None:
    if not isinstance(fragment_href, str):
        return None
    if fragment_href != fragment_href.strip() or not fragment_href.startswith("#"):
        return None
    fragment = fragment_href[1:]
    if not fragment or any(character.isspace() for character in fragment):
        return None
    if fragment.startswith("local-article-content-section-"):
        suffix = fragment.removeprefix("local-article-content-section-")
    elif fragment.startswith("local-article-paragraph-"):
        suffix = fragment.removeprefix("local-article-paragraph-")
    else:
        return None
    if not suffix.isdigit() or suffix != str(int(suffix)) or int(suffix) < 1:
        return None
    story_id = page_href.removesuffix(".html")
    if _safe_article_page_href(story_id, page_href) is None:
        return None
    return f"{page_href}#{fragment}"


def _opening_read(cards: tuple[RowOneDailyLocalSynthesisBriefCard, ...]) -> LocalizedText:
    distinct_cards: list[RowOneDailyLocalSynthesisBriefCard] = []
    seen_reads: set[str] = set()
    for card in cards:
        read_key = _localized_key(card.read)
        if not read_key or read_key in seen_reads:
            continue
        distinct_cards.append(card)
        seen_reads.add(read_key)
        if len(distinct_cards) >= 2:
            break

    if len(distinct_cards) >= 2:
        first = distinct_cards[0].title
        second = distinct_cards[1].title
        first_en = _truncate_title(
            first.en or first.zh,
            DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS,
        )
        second_en = _truncate_title(
            second.en or second.zh,
            DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS,
        )
        first_zh = _truncate_title(
            first.zh or first.en,
            DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS,
        )
        second_zh = _truncate_title(
            second.zh or second.en,
            DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_TITLE_CHARS,
        )
        return LocalizedText(
            en=_truncate(
                f"Today's local read connects {first_en} with {second_en}.",
                DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_CHARS,
            ),
            zh=_truncate(
                f"今日本地阅读把《{first_zh}》与《{second_zh}》连接起来。",
                DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_CHARS,
            ),
        )

    first_read = cards[0].read
    return _clean_localized(first_read, DAILY_LOCAL_SYNTHESIS_BRIEF_OPENING_CHARS)


def _first_distinct_thesis(candidates: list[_Candidate]) -> LocalizedText:
    seen: set[str] = set()
    for candidate in candidates:
        thesis = _clean_localized(candidate.thesis, DAILY_LOCAL_SYNTHESIS_BRIEF_THESIS_CHARS)
        key = _localized_key(thesis)
        if key and key not in seen:
            return thesis
        if key:
            seen.add(key)
    for candidate in candidates:
        adds = _clean_localized(candidate.card.adds, DAILY_LOCAL_SYNTHESIS_BRIEF_THESIS_CHARS)
        key = _localized_key(adds)
        if key and key not in seen:
            return adds
    return LocalizedText(en="", zh="")


def _localized_text(en: str, zh: str) -> LocalizedText:
    en_clean = normalize_row_one_paragraph(en)
    zh_clean = normalize_row_one_paragraph(zh)
    return LocalizedText(en=en_clean or zh_clean, zh=zh_clean or en_clean)


def _clean_localized(value: LocalizedText, limit: int) -> LocalizedText:
    en = _truncate(value.en or value.zh, limit)
    zh = _truncate(value.zh or value.en, limit)
    return LocalizedText(en=en or zh, zh=zh or en)


def _localized_key(value: LocalizedText) -> str:
    return " ".join(part for part in (_key(value.en), _key(value.zh)) if part)


def _key(value: str) -> str:
    return normalize_row_one_paragraph(value).casefold()


def _truncate(value: str, limit: int) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 3)].rstrip() + "..."


def _truncate_title(value: str, limit: int) -> str:
    normalized = normalize_row_one_paragraph(value)
    if len(normalized) <= limit:
        return normalized
    clipped = normalized[: max(0, limit - 3)].rstrip()
    if " " in clipped:
        word_boundary = clipped.rfind(" ")
        if word_boundary >= max(12, limit // 2):
            clipped = clipped[:word_boundary].rstrip()
    return f"{clipped}..."
