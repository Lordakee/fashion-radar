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
) -> tuple[list[str], list[str]]:
    paragraphs = text_to_local_article_paragraphs(text, max_chars=max_chars)
    if not paragraphs:
        return [], []
    paragraphs_zh = list(source_paragraphs_zh or paragraphs)
    if len(paragraphs_zh) != len(paragraphs):
        paragraphs_zh = list(paragraphs)

    total_chars = sum(len(paragraph) for paragraph in paragraphs)
    if total_chars >= min(max_chars, LOCAL_ARTICLE_MIN_CONTEXT_CHARS):
        return paragraphs, paragraphs_zh
    context_text_en = _local_article_context_text(story, language="en")
    if not context_text_en:
        return paragraphs, paragraphs_zh
    remaining_chars = max_chars - total_chars
    if remaining_chars <= 0:
        return paragraphs, paragraphs_zh
    context_paragraphs = text_to_local_article_paragraphs(
        context_text_en,
        max_chars=remaining_chars,
    )
    if not context_paragraphs:
        return paragraphs, paragraphs_zh
    context_paragraphs_zh = text_to_local_article_paragraphs(
        _local_article_context_text(story, language="zh"),
        max_chars=max_chars,
    )
    context_paragraphs_zh = _align_local_article_language_paragraphs(
        context_paragraphs,
        context_paragraphs_zh,
    )
    return [*paragraphs, *context_paragraphs], [*paragraphs_zh, *context_paragraphs_zh]


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
        return _fallback_story_summary_article(story, url, source, extracted_at=extracted_at)
    if result.skipped or not result.text:
        return _fallback_story_summary_article(story, url, source, extracted_at=extracted_at)
    paragraphs, paragraphs_zh = _story_local_article_paragraph_sets(
        story,
        result.text,
        max_chars=source.row_one_article.max_chars,
    )
    if not paragraphs:
        return _fallback_story_summary_article(story, url, source, extracted_at=extracted_at)
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
        skipped=False,
        reason=None,
    )


def _fallback_story_summary_article(
    story: RowOneStory,
    url: str,
    source: SourceDefinition,
    *,
    extracted_at,
) -> RowOneLocalArticle | None:
    summary_zh = text_to_local_article_paragraphs(
        story.summary.zh,
        max_chars=source.row_one_article.max_chars,
    )
    paragraphs, paragraphs_zh = _story_local_article_paragraph_sets(
        story,
        story.summary.en,
        max_chars=source.row_one_article.max_chars,
        source_paragraphs_zh=summary_zh,
    )
    if not paragraphs:
        return None
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
        skipped=False,
        reason=None,
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
