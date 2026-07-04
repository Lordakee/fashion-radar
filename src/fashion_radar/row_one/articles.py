from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from typing import Protocol
from urllib.parse import urlsplit

from fashion_radar.collectors.article import ArticleExtractionResult, extract_article_with_metadata
from fashion_radar.collectors.robots import RobotsPolicyChecker
from fashion_radar.models.source import SourceDefinition
from fashion_radar.row_one.models import RowOneEdition, RowOneLocalArticle, RowOneStory
from fashion_radar.row_one.utils import safe_external_url, utc_datetime
from fashion_radar.utils.dates import parse_datetime_utc
from fashion_radar.utils.http import FashionHttpClient

ROW_ONE_LOCAL_ARTICLES_ENV = "ROW_ONE_LOCAL_ARTICLES"
LOCAL_ARTICLE_STORY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}$")


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
    for raw_paragraph in re.split(r"\n{2,}", text):
        paragraph = _normalize_paragraph(raw_paragraph)
        if not paragraph:
            continue
        remaining = max_chars - used_chars
        if remaining <= 0:
            break
        if len(paragraph) > remaining:
            paragraph = _truncate_at_word_boundary(paragraph, remaining)
        if not paragraph:
            break
        paragraphs.append(paragraph)
        used_chars += len(paragraph)
        if used_chars >= max_chars:
            break
    return paragraphs


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
    paragraphs = text_to_local_article_paragraphs(
        result.text,
        max_chars=source.row_one_article.max_chars,
    )
    if not paragraphs:
        return None
    return RowOneLocalArticle(
        story_id=story.id,
        title=result.title or story.headline,
        url=url,
        source_name=story.source_name,
        extracted_at=extracted_at,
        published_at=result.published_at or story.published_at,
        paragraphs=paragraphs,
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
    paragraphs = text_to_local_article_paragraphs(
        story.summary.en,
        max_chars=source.row_one_article.max_chars,
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
            "max_summary_chars": source.row_one_article.max_chars,
            "paywalled_domains": paywalled_domains,
        }
    )
    return source.model_copy(update={"article": article_settings})


def _hostname(url: str | None) -> str | None:
    if not url:
        return None
    hostname = urlsplit(url).hostname
    return hostname.lower().removeprefix("www.") if hostname else None


def _normalize_paragraph(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    if max_chars <= 3:
        return "." * max_chars
    truncated = text[: max_chars - 3].rstrip()
    boundary = truncated.rfind(" ")
    if boundary >= 24:
        truncated = truncated[:boundary].rstrip()
    return f"{truncated}..."
