from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from html import unescape
from html.parser import HTMLParser
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
LOCAL_ARTICLE_TARGET_PARAGRAPH_CHARS = 140
LOCAL_ARTICLE_DEDUPE_MIN_CHARS = 24
LOCAL_ARTICLE_MIN_TRUNCATED_PARAGRAPH_CHARS = 24
LOCAL_ARTICLE_EXTRACTION_BUFFER_CHARS = 500
LOCAL_ARTICLE_EXTRACTION_MAX_CHARS = 12000
LOCAL_ARTICLE_PREFIX_RE = re.compile(
    r"^(?:original source summary|source summary|来源摘要)\s*[:：]\s*",
    re.IGNORECASE,
)
LOCAL_ARTICLE_BOILERPLATE = {
    "read the full story here.",
    "read full story here.",
    "read more.",
    "read more:",
    "阅读全文。",
    "点击查看全文。",
}
SENTENCE_RE = re.compile(r"[^.!?。！？]+[.!?。！？]?")
BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "br",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "li",
    "main",
    "ol",
    "p",
    "section",
    "table",
    "td",
    "th",
    "tr",
    "ul",
}


class _PlainTextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._ignored_depth += 1
            return
        if tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if not self._ignored_depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self._ignored_depth:
            self.parts.append(f"&#{name};")

    def text(self) -> str:
        return "".join(self.parts)


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
        paragraph = _normalize_paragraph(raw_paragraph)
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


def _normalize_paragraph(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _prepared_local_article_paragraphs(text: str) -> list[str]:
    cleaned = _clean_local_article_text(text)
    raw_paragraphs = [
        _normalize_paragraph(paragraph)
        for paragraph in re.split(r"\n{2,}", cleaned)
        if _normalize_paragraph(paragraph)
    ]
    prepared: list[str] = []
    seen_sentences: set[str] = set()
    for paragraph in raw_paragraphs:
        sentences = _clean_sentences(paragraph, seen_sentences)
        prepared.extend(_group_sentences(sentences))
    return prepared


def _clean_local_article_text(text: str) -> str:
    unescaped = unescape(text)
    parser = _PlainTextHTMLParser()
    parser.feed(unescaped)
    parser.close()
    cleaned = parser.text()
    cleaned = LOCAL_ARTICLE_PREFIX_RE.sub("", cleaned.strip())
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _clean_sentences(paragraph: str, seen_sentences: set[str]) -> list[str]:
    cleaned_sentences: list[str] = []
    for raw_sentence in SENTENCE_RE.findall(paragraph):
        sentence = _normalize_paragraph(raw_sentence)
        if not sentence:
            continue
        if _sentence_key(sentence) in LOCAL_ARTICLE_BOILERPLATE:
            continue
        dedupe_key = _sentence_key(sentence)
        if len(dedupe_key) >= LOCAL_ARTICLE_DEDUPE_MIN_CHARS:
            if dedupe_key in seen_sentences:
                continue
            seen_sentences.add(dedupe_key)
        cleaned_sentences.append(sentence)
    return cleaned_sentences


def _group_sentences(sentences: list[str]) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    current_chars = 0
    for sentence in sentences:
        projected = current_chars + len(sentence) + (1 if current else 0)
        if current and projected > LOCAL_ARTICLE_TARGET_PARAGRAPH_CHARS:
            paragraphs.append(" ".join(current))
            current = [sentence]
            current_chars = len(sentence)
            continue
        current.append(sentence)
        current_chars = projected
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def _sentence_key(sentence: str) -> str:
    return re.sub(r"\s+", " ", sentence).strip().casefold()


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
