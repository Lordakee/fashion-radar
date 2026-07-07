from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from typing import Protocol
from urllib.parse import urlsplit

from fashion_radar.collectors.article import ArticleExtractionResult, extract_article_with_metadata
from fashion_radar.collectors.robots import RobotsPolicyChecker
from fashion_radar.models.source import SourceDefinition
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleBriefSection,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentKey,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneStory,
)
from fashion_radar.row_one.text import (
    clean_row_one_sentences,
    clean_row_one_text,
    group_row_one_sentences,
    normalize_row_one_paragraph,
    protect_literal_angle_tokens,
    restore_literal_angle_tokens,
)
from fashion_radar.row_one.utils import safe_external_url, utc_datetime
from fashion_radar.utils.dates import parse_datetime_utc
from fashion_radar.utils.http import FashionHttpClient

ROW_ONE_LOCAL_ARTICLES_ENV = "ROW_ONE_LOCAL_ARTICLES"
LOCAL_ARTICLE_STORY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}$")
LOCAL_ARTICLE_REFERENCE_EXCERPT_MAX_CHARS = 280
LOCAL_ARTICLE_MIN_TRUNCATED_PARAGRAPH_CHARS = 24
LOCAL_ARTICLE_MIN_CONTEXT_CHARS = 240
LOCAL_ARTICLE_EXTRACTION_BUFFER_CHARS = 500
LOCAL_ARTICLE_EXTRACTION_MAX_CHARS = 12000


class RowOneArticleExtractor(Protocol):
    def __call__(
        self,
        url: str,
        *,
        source: SourceDefinition,
        html_fetcher,
        robots_checker: RobotsPolicyChecker,
    ) -> ArticleExtractionResult: ...


def row_one_local_articles_enabled(
    *,
    local_articles_enabled: bool = True,
    environ: Mapping[str, str] | None = None,
) -> bool:
    value = (environ or os.environ).get(ROW_ONE_LOCAL_ARTICLES_ENV)
    if value is not None and value.strip().casefold() in {"0", "false", "no", "off"}:
        return False
    return local_articles_enabled


def build_row_one_local_articles(
    edition: RowOneEdition,
    sources: Sequence[SourceDefinition],
    *,
    now=None,
    extractor: RowOneArticleExtractor = extract_article_with_metadata,
    local_articles_enabled: bool = True,
    environ: Mapping[str, str] | None = None,
) -> dict[str, RowOneLocalArticle]:
    if not row_one_local_articles_enabled(
        local_articles_enabled=local_articles_enabled,
        environ=environ,
    ):
        return {}

    extracted_at = (
        utc_datetime(parse_datetime_utc(now)) if now is not None else edition.generated_at
    )
    articles: dict[str, RowOneLocalArticle] = {}
    clients: dict[str, FashionHttpClient] = {}
    robots_checkers: dict[str, RobotsPolicyChecker] = {}
    try:
        for story in edition.stories:
            article = _build_story_local_article(
                story,
                sources,
                extracted_at=extracted_at,
                extractor=extractor,
                clients=clients,
                robots_checkers=robots_checkers,
            )
            if article is not None:
                articles[story.id] = article
    finally:
        for client in clients.values():
            client.close()
    return articles


def text_to_local_article_paragraphs(text: str, *, max_chars: int) -> list[str]:
    paragraphs: list[str] = []
    used_chars = 0
    for raw_paragraph in _prepared_local_article_paragraphs(text):
        paragraph = normalize_row_one_paragraph(raw_paragraph)
        if not paragraph:
            continue
        remaining = max_chars - used_chars
        if remaining <= 0:
            break
        if len(paragraph) > remaining:
            paragraph = _truncate_at_word_boundary(paragraph, remaining)
            if not _useful_truncated_paragraph(paragraph):
                break
        if not paragraph:
            break
        paragraphs.append(paragraph)
        used_chars += len(paragraph)
        if used_chars >= max_chars:
            break
    return paragraphs


def _story_local_article_paragraph_sets(
    story: RowOneStory,
    text: str,
    *,
    max_chars: int,
    source_paragraphs_zh: list[str] | None = None,
) -> tuple[list[str], list[str], int]:
    paragraphs = text_to_local_article_paragraphs(text, max_chars=max_chars)
    if not paragraphs:
        return [], [], 0
    paragraphs_zh = list(source_paragraphs_zh or paragraphs)
    if len(paragraphs_zh) != len(paragraphs):
        paragraphs_zh = list(paragraphs)
    source_paragraph_count = len(paragraphs)

    total_chars = sum(len(paragraph) for paragraph in paragraphs)
    if total_chars >= min(max_chars, LOCAL_ARTICLE_MIN_CONTEXT_CHARS):
        return paragraphs, paragraphs_zh, source_paragraph_count
    context_text_en = _local_article_context_text(story, language="en")
    if not context_text_en:
        return paragraphs, paragraphs_zh, source_paragraph_count
    remaining_chars = max_chars - total_chars
    if remaining_chars <= 0:
        return paragraphs, paragraphs_zh, source_paragraph_count
    context_paragraphs = text_to_local_article_paragraphs(
        context_text_en,
        max_chars=remaining_chars,
    )
    if not context_paragraphs:
        return paragraphs, paragraphs_zh, source_paragraph_count
    context_paragraphs_zh = text_to_local_article_paragraphs(
        _local_article_context_text(story, language="zh"),
        max_chars=max_chars,
    )
    context_paragraphs_zh = _align_local_article_language_paragraphs(
        context_paragraphs,
        context_paragraphs_zh,
    )
    return (
        [*paragraphs, *context_paragraphs],
        [*paragraphs_zh, *context_paragraphs_zh],
        source_paragraph_count,
    )


def _align_local_article_language_paragraphs(
    paragraphs: list[str],
    paragraphs_zh: list[str],
) -> list[str]:
    aligned = list(paragraphs_zh[: len(paragraphs)])
    if len(aligned) < len(paragraphs):
        aligned.extend(paragraphs[len(aligned) :])
    return aligned


def _local_article_context_text(story: RowOneStory, *, language: str = "en") -> str:
    return "\n\n".join(
        text for text in (getattr(story.editorial_takeaway, language),) if text.strip()
    )


def _local_article_brief_text(text: str) -> str:
    protected = protect_literal_angle_tokens(text)
    cleaned = clean_row_one_text(protected)
    sentences = clean_row_one_sentences(cleaned, set())
    return restore_literal_angle_tokens(normalize_row_one_paragraph(" ".join(sentences)))


def _local_article_brief_sections(story: RowOneStory) -> list[RowOneLocalArticleBriefSection]:
    return [
        RowOneLocalArticleBriefSection(
            key="what_happened",
            title=LocalizedText(en="What Happened", zh="发生了什么"),
            body=LocalizedText(
                en=_local_article_brief_text(story.summary.en),
                zh=_local_article_brief_text(story.summary.zh),
            ),
        ),
        RowOneLocalArticleBriefSection(
            key="why_it_matters",
            title=LocalizedText(en="Why It Matters", zh="为什么重要"),
            body=story.why_it_matters,
        ),
        RowOneLocalArticleBriefSection(
            key="signal_context",
            title=LocalizedText(en="Signal Context", zh="信号背景"),
            body=story.signal_context,
        ),
        RowOneLocalArticleBriefSection(
            key="watch_next",
            title=LocalizedText(en="Watch Next", zh="接下来观察"),
            body=story.reader_path,
        ),
    ]


def _localized_content_item(
    *,
    label_en: str,
    label_zh: str | None = None,
    body_en: str | None = None,
    body_zh: str | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=LocalizedText(en=label_en, zh=label_zh or label_en),
        body=(
            LocalizedText(en=body_en, zh=body_zh if body_zh is not None else body_en)
            if body_en is not None
            else None
        ),
        references=list(references or []),
        paragraph_indices=list(paragraph_indices or []),
    )


def _local_article_paragraph_indices(
    paragraphs: list[str],
    terms: list[str],
    *,
    limit: int = 3,
) -> list[int]:
    normalized_terms: list[str] = []
    seen_terms: set[str] = set()
    for term in terms:
        normalized = normalize_row_one_paragraph(term).casefold()
        if len(normalized) < 3 or normalized in seen_terms:
            continue
        seen_terms.add(normalized)
        normalized_terms.append(normalized)
    if not normalized_terms:
        return []
    indices: list[int] = []
    for index, paragraph in enumerate(paragraphs):
        paragraph_key = paragraph.casefold()
        if any(term in paragraph_key for term in normalized_terms):
            indices.append(index)
            if len(indices) >= limit:
                break
    return indices


def _local_article_signal_terms(story: RowOneStory) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for ref in [*story.entity_refs, *story.designer_refs, *story.product_refs]:
        term = normalize_row_one_paragraph(ref.name)
        if len(term) < 3 or (" " not in term and len(term) < 4):
            continue
        key = term.casefold()
        if key in seen:
            continue
        seen.add(key)
        terms.append(term)
    return terms


def _local_article_takeaway_indices(
    story: RowOneStory,
    paragraphs: list[str],
    *,
    limit: int = 3,
    source_paragraph_count: int | None = None,
) -> list[int]:
    scoring_paragraphs = (
        paragraphs[:source_paragraph_count] if source_paragraph_count else paragraphs
    )
    non_empty = [index for index, paragraph in enumerate(scoring_paragraphs) if paragraph.strip()]
    terms = _local_article_signal_terms(story)
    patterns = [
        re.compile(rf"(?<![a-z0-9]){re.escape(term.casefold())}(?![a-z0-9])") for term in terms
    ]
    scored = [
        (
            index,
            sum(1 for pattern in patterns if pattern.search(paragraphs[index].casefold())),
        )
        for index in non_empty
    ]
    matched = [(index, score) for index, score in scored if score > 0]
    if matched:
        matched.sort(key=lambda item: (-item[1], item[0]))
        return [index for index, _score in matched[:limit]]
    return non_empty[:limit]


def _local_article_reference_excerpt(
    paragraphs: list[str],
    paragraph_indices: list[int],
    *,
    max_chars: int = LOCAL_ARTICLE_REFERENCE_EXCERPT_MAX_CHARS,
) -> tuple[int, str] | None:
    for index in paragraph_indices:
        if index < 0 or index >= len(paragraphs):
            continue
        # Defensive re-normalization keeps this helper safe for future callers
        # that may pass raw paragraph lists instead of prepared local paragraphs.
        excerpt = normalize_row_one_paragraph(paragraphs[index])
        if not excerpt:
            continue
        if len(excerpt) > max_chars:
            excerpt = _truncate_at_word_boundary(excerpt, max_chars)
        return index, excerpt
    return None


def _local_article_reference_body(
    ref: RowOneReference,
    paragraphs: list[str],
    paragraphs_zh: list[str],
    excerpt_indices: list[int],
) -> tuple[str, str]:
    fallback = f"{ref.type} / {ref.label}"
    # Excerpt indices are name-only and limit-1; paragraph badges still use
    # the broader name+label match to preserve Stage 303 navigation.
    excerpt = _local_article_reference_excerpt(paragraphs, excerpt_indices)
    if excerpt is None:
        return fallback, fallback
    index, body_en = excerpt
    aligned_zh = _align_local_article_language_paragraphs(paragraphs, paragraphs_zh)
    body_zh = normalize_row_one_paragraph(aligned_zh[index]) if index < len(aligned_zh) else ""
    if len(body_zh) > LOCAL_ARTICLE_REFERENCE_EXCERPT_MAX_CHARS:
        body_zh = _truncate_at_word_boundary(
            body_zh,
            LOCAL_ARTICLE_REFERENCE_EXCERPT_MAX_CHARS,
        )
    # Missing or whitespace-only aligned zh text falls back to the saved source excerpt.
    return body_en, body_zh or body_en


def _local_article_takeaway_section(
    story: RowOneStory,
    paragraphs: list[str],
    paragraphs_zh: list[str],
    *,
    source_paragraph_count: int | None = None,
) -> RowOneLocalArticleContentSection | None:
    aligned_zh = _align_local_article_language_paragraphs(paragraphs, paragraphs_zh)
    items: list[RowOneLocalArticleContentItem] = []
    for position, index in enumerate(
        _local_article_takeaway_indices(
            story,
            paragraphs,
            source_paragraph_count=source_paragraph_count,
        )
    ):
        paragraph_en = paragraphs[index]
        paragraph_zh = aligned_zh[index] if index < len(aligned_zh) else ""
        if not paragraph_en.strip():
            continue
        label_en = "Source lead" if position == 0 else f"Source point {position + 1}"
        label_zh = "来源导语" if position == 0 else f"来源要点 {position + 1}"
        items.append(
            _localized_content_item(
                label_en=label_en,
                label_zh=label_zh,
                body_en=paragraph_en,
                body_zh=paragraph_zh if paragraph_zh.strip() else paragraph_en,
                paragraph_indices=[index],
            )
        )
    if not items:
        return None
    return RowOneLocalArticleContentSection(
        key="takeaways",
        title=LocalizedText(en="Takeaways", zh="要点"),
        body=LocalizedText(
            en="The saved source text points to these immediate reads.",
            zh="本地保存的来源正文首先指向这些要点。",
        ),
        items=items,
    )


def _local_article_reference_section(
    *,
    key: RowOneLocalArticleContentKey,
    title: LocalizedText,
    refs: list[RowOneReference],
    paragraphs: list[str],
    paragraphs_zh: list[str],
) -> RowOneLocalArticleContentSection | None:
    items: list[RowOneLocalArticleContentItem] = []
    seen: set[tuple[str, str, str]] = set()
    for ref in refs:
        identity = (ref.name, ref.type, ref.label)
        if identity in seen:
            continue
        seen.add(identity)
        paragraph_indices = _local_article_paragraph_indices(
            paragraphs,
            [ref.name, ref.label],
        )
        excerpt_indices = _local_article_paragraph_indices(
            paragraphs,
            [ref.name],
            limit=1,
        )
        body_en, body_zh = _local_article_reference_body(
            ref,
            paragraphs,
            paragraphs_zh,
            excerpt_indices,
        )
        items.append(
            _localized_content_item(
                label_en=ref.name,
                body_en=body_en,
                body_zh=body_zh,
                references=[ref],
                paragraph_indices=paragraph_indices,
            )
        )
    if not items:
        return None
    return RowOneLocalArticleContentSection(key=key, title=title, items=items)


def _unique_local_article_tags(tags: list[str], *, limit: int = 4) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        normalized = normalize_row_one_paragraph(tag)
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(normalized)
        if len(unique) >= limit:
            break
    return unique


def _local_article_brand_signal_section(story: RowOneStory) -> RowOneLocalArticleContentSection:
    items: list[RowOneLocalArticleContentItem] = []
    if story.signal_context.en.strip() or story.signal_context.zh.strip():
        items.append(
            RowOneLocalArticleContentItem(
                label=LocalizedText(en="Signal context", zh="信号背景"),
                body=story.signal_context,
            )
        )
    if story.heat_delta is not None:
        sign = "+" if story.heat_delta > 0 else ""
        items.append(
            _localized_content_item(
                label_en="Heat delta",
                label_zh="热度变化",
                body_en=f"{sign}{story.heat_delta}",
                body_zh=f"{sign}{story.heat_delta}",
            )
        )
    tags = _unique_local_article_tags(story.tags)
    if tags:
        tag_text = ", ".join(tags)
        items.append(
            _localized_content_item(
                label_en="Tags",
                label_zh="标签",
                body_en=tag_text,
                body_zh=tag_text,
            )
        )
    if story.market_region:
        items.append(
            _localized_content_item(
                label_en="Market region",
                label_zh="市场区域",
                body_en=story.market_region,
                body_zh=story.market_region,
            )
        )
    if story.source_region:
        items.append(
            _localized_content_item(
                label_en="Source region",
                label_zh="来源区域",
                body_en=story.source_region,
                body_zh=story.source_region,
            )
        )
    items.append(
        _localized_content_item(
            label_en="Source",
            label_zh="来源",
            body_en=story.source_name,
            body_zh=story.source_name,
        )
    )
    return RowOneLocalArticleContentSection(
        key="brand_signals",
        title=LocalizedText(en="Brand Signals", zh="品牌信号"),
        body=LocalizedText(
            en="ROW ONE tracks the metadata around this story for follow-up.",
            zh="ROW ONE 会继续追踪这条内容背后的元数据。",
        ),
        items=items,
    )


def _local_article_content_sections(
    story: RowOneStory,
    paragraphs: list[str],
    paragraphs_zh: list[str],
    *,
    source_paragraph_count: int | None = None,
) -> list[RowOneLocalArticleContentSection]:
    sections: list[RowOneLocalArticleContentSection] = []
    takeaway_section = _local_article_takeaway_section(
        story,
        paragraphs,
        paragraphs_zh,
        source_paragraph_count=source_paragraph_count,
    )
    if takeaway_section is not None:
        sections.append(takeaway_section)
    entity_refs = [*story.entity_refs, *story.designer_refs]
    entity_section = _local_article_reference_section(
        key="entities",
        title=LocalizedText(en="Entities", zh="相关对象"),
        refs=entity_refs,
        paragraphs=paragraphs,
        paragraphs_zh=paragraphs_zh,
    )
    if entity_section is not None:
        sections.append(entity_section)
    product_section = _local_article_reference_section(
        key="product_signals",
        title=LocalizedText(en="Product Signals", zh="产品信号"),
        refs=story.product_refs,
        paragraphs=paragraphs,
        paragraphs_zh=paragraphs_zh,
    )
    if product_section is not None:
        sections.append(product_section)
    sections.append(_local_article_brand_signal_section(story))
    return sections


def safe_local_article_story_id(story_id: str) -> bool:
    return LOCAL_ARTICLE_STORY_ID_RE.fullmatch(story_id) is not None


def _build_story_local_article(
    story: RowOneStory,
    sources: Sequence[SourceDefinition],
    *,
    extracted_at,
    extractor: RowOneArticleExtractor,
    clients: dict[str, FashionHttpClient],
    robots_checkers: dict[str, RobotsPolicyChecker],
) -> RowOneLocalArticle | None:
    url = safe_external_url(story.source_url)
    if url is None:
        return None
    source = _source_for_story(story, url, sources)
    if source is None:
        return None
    extraction_source = _source_for_row_one_extraction(source)
    client = clients.get(source.name)
    if client is None:
        client = FashionHttpClient(source.http)
        clients[source.name] = client
    robots_checker = robots_checkers.get(source.name)
    if robots_checker is None:
        robots_checker = RobotsPolicyChecker(
            lambda robots_url, client=client: client.get_response(robots_url)
        )
        robots_checkers[source.name] = robots_checker
    try:
        result = extractor(
            url,
            source=extraction_source,
            html_fetcher=client.get_text,
            robots_checker=robots_checker,
        )
    except Exception:
        return _fallback_story_summary_article(
            story,
            url,
            source,
            extracted_at=extracted_at,
            reason="extraction_failed",
        )
    if result.skipped:
        return _fallback_story_summary_article(
            story,
            url,
            source,
            extracted_at=extracted_at,
            reason=result.reason or "extraction_skipped",
        )
    if not result.text or not result.text.strip():
        return _fallback_story_summary_article(
            story,
            url,
            source,
            extracted_at=extracted_at,
            reason="no_extractable_text",
        )
    paragraphs, paragraphs_zh, source_paragraph_count = _story_local_article_paragraph_sets(
        story,
        result.text,
        max_chars=source.row_one_article.max_chars,
    )
    if not paragraphs:
        return _fallback_story_summary_article(
            story,
            url,
            source,
            extracted_at=extracted_at,
            reason="no_publishable_paragraphs",
        )
    return RowOneLocalArticle(
        story_id=story.id,
        title=result.title or story.headline,
        url=url,
        source_name=story.source_name,
        extracted_at=extracted_at,
        published_at=result.published_at or story.published_at,
        paragraphs=paragraphs,
        paragraphs_zh=paragraphs_zh,
        brief_sections=_local_article_brief_sections(story),
        content_sections=_local_article_content_sections(
            story,
            paragraphs,
            paragraphs_zh,
            source_paragraph_count=source_paragraph_count,
        ),
        body_source="extracted",
        skipped=False,
        reason=None,
    )


def _fallback_story_summary_article(
    story: RowOneStory,
    url: str,
    source: SourceDefinition,
    *,
    extracted_at,
    reason: str,
) -> RowOneLocalArticle:
    summary_zh = text_to_local_article_paragraphs(
        story.summary.zh,
        max_chars=source.row_one_article.max_chars,
    )
    paragraphs, paragraphs_zh, source_paragraph_count = _story_local_article_paragraph_sets(
        story,
        story.summary.en,
        max_chars=source.row_one_article.max_chars,
        source_paragraphs_zh=summary_zh,
    )
    if not paragraphs:
        return _skipped_story_local_article(
            story,
            url,
            extracted_at=extracted_at,
            reason=reason,
        )
    return RowOneLocalArticle(
        story_id=story.id,
        title=story.headline,
        url=url,
        source_name=story.source_name,
        extracted_at=extracted_at,
        published_at=story.published_at,
        paragraphs=paragraphs,
        paragraphs_zh=paragraphs_zh,
        brief_sections=_local_article_brief_sections(story),
        content_sections=_local_article_content_sections(
            story,
            paragraphs,
            paragraphs_zh,
            source_paragraph_count=source_paragraph_count,
        ),
        body_source="summary_fallback",
        skipped=False,
        reason=reason,
    )


def _skipped_story_local_article(
    story: RowOneStory,
    url: str,
    *,
    extracted_at,
    reason: str,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story.id,
        title=story.headline,
        url=url,
        source_name=story.source_name,
        extracted_at=extracted_at,
        published_at=story.published_at,
        body_source="skipped",
        skipped=True,
        reason=reason,
    )


def _source_for_story(
    story: RowOneStory,
    story_url: str,
    sources: Sequence[SourceDefinition],
) -> SourceDefinition | None:
    for source in sources:
        if source.name == story.source_name:
            return source if source.row_one_article.enabled else None

    story_host = _hostname(story_url)
    if story_host is None:
        return None
    for source in sources:
        if not source.row_one_article.enabled:
            continue
        source_hosts = {_hostname(url) for url in [source.url, *source.seed_urls] if url}
        if story_host in source_hosts:
            return source
    return None


def _source_for_row_one_extraction(source: SourceDefinition) -> SourceDefinition:
    paywalled_domains = sorted(
        {
            *source.article.paywalled_domains,
            *source.row_one_article.paywalled_domains,
        }
    )
    article_settings = source.article.model_copy(
        update={
            "enabled": True,
            "respect_robots_txt": source.row_one_article.respect_robots_txt,
            "max_summary_chars": _extraction_buffer_chars(source.row_one_article.max_chars),
            "paywalled_domains": paywalled_domains,
        }
    )
    return source.model_copy(update={"article": article_settings})


def _hostname(url: str | None) -> str | None:
    if not url:
        return None
    hostname = urlsplit(url).hostname
    return hostname.lower().removeprefix("www.") if hostname else None


def _extraction_buffer_chars(display_max_chars: int) -> int:
    return min(
        LOCAL_ARTICLE_EXTRACTION_MAX_CHARS,
        max(display_max_chars * 2, display_max_chars + LOCAL_ARTICLE_EXTRACTION_BUFFER_CHARS),
    )


def _prepared_local_article_paragraphs(text: str) -> list[str]:
    cleaned = clean_row_one_text(text)
    raw_paragraphs = [
        normalize_row_one_paragraph(paragraph)
        for paragraph in re.split(r"\n{2,}", cleaned)
        if normalize_row_one_paragraph(paragraph)
    ]
    prepared: list[str] = []
    seen_sentences: set[str] = set()
    for paragraph in raw_paragraphs:
        sentences = clean_row_one_sentences(paragraph, seen_sentences)
        prepared.extend(group_row_one_sentences(sentences))
    return prepared


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    if max_chars <= 3:
        return "." * max_chars
    truncated = text[: max_chars - 3].rstrip()
    boundary = truncated.rfind(" ")
    if boundary >= 24:
        truncated = truncated[:boundary].rstrip()
    return f"{truncated}..."


def _useful_truncated_paragraph(text: str) -> bool:
    useful_text = text.removesuffix("...").strip()
    return len(useful_text) >= LOCAL_ARTICLE_MIN_TRUNCATED_PARAGRAPH_CHARS
