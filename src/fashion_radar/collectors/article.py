from __future__ import annotations

import json
from typing import Protocol
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict

from fashion_radar.collectors.robots import RobotsPolicyChecker
from fashion_radar.models.source import SourceDefinition

try:
    import trafilatura
except ImportError:  # pragma: no cover - dependency is optional at runtime.
    trafilatura = None  # type: ignore[assignment]


class HtmlFetcher(Protocol):
    def __call__(self, url: str) -> str: ...


class ArticleExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
    title: str | None = None
    text: str | None = None
    published_at: str | None = None
    skipped: bool
    reason: str | None = None


def extract_article(
    url: str,
    *,
    source: SourceDefinition,
    html_fetcher: HtmlFetcher,
    robots_checker: RobotsPolicyChecker,
) -> ArticleExtractionResult:
    if not source.article.enabled:
        return _skipped(url, "disabled")

    if _is_paywalled_domain(url, source.article.paywalled_domains):
        return _skipped(url, "paywalled_domain")

    if trafilatura is None:
        return _skipped(url, "extractor_unavailable")

    if source.article.respect_robots_txt:
        try:
            if hasattr(robots_checker, "check"):
                check = robots_checker.check(url, source.http.user_agent)
            else:
                allowed = robots_checker.can_fetch(url, source.http.user_agent)
                reason = "allowed" if allowed else "robots_disallowed"
                check = type(
                    "RobotsCheckFallback",
                    (),
                    {"allowed": allowed, "reason": reason},
                )()
        except Exception:
            check = type(
                "RobotsCheckFallback",
                (),
                {"allowed": False, "reason": "robots_unavailable"},
            )()
        if not check.allowed:
            return _skipped(url, check.reason)

    try:
        html = html_fetcher(url)
        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
    except Exception:
        return _skipped(url, "extraction_failed")

    if not extracted:
        return _skipped(url, "no_extractable_text")

    return ArticleExtractionResult(
        url=url,
        text=extracted[: source.article.max_summary_chars],
        skipped=False,
        reason=None,
    )


def extractor_available() -> bool:
    return trafilatura is not None


def extract_article_with_metadata(
    url: str,
    *,
    source: SourceDefinition,
    html_fetcher: HtmlFetcher,
    robots_checker: RobotsPolicyChecker,
) -> ArticleExtractionResult:
    if not source.article.enabled:
        return _skipped(url, "disabled")
    if _is_paywalled_domain(url, source.article.paywalled_domains):
        return _skipped(url, "paywalled_domain")
    # Kept for self-contained reuse by SitemapCollector (Stage 214); HtmlCollector
    # gates via extractor_available() before calling this.
    if trafilatura is None:
        return _skipped(url, "extractor_unavailable")
    if source.article.respect_robots_txt:
        try:
            if hasattr(robots_checker, "check"):
                check = robots_checker.check(url, source.http.user_agent)
            else:
                allowed = robots_checker.can_fetch(url, source.http.user_agent)
                reason = "allowed" if allowed else "robots_disallowed"
                check = type(
                    "RobotsCheckFallback",
                    (),
                    {"allowed": allowed, "reason": reason},
                )()
        except Exception:
            check = type(
                "RobotsCheckFallback",
                (),
                {"allowed": False, "reason": "robots_unavailable"},
            )()
        if not check.allowed:
            return _skipped(url, check.reason)
    try:
        html = html_fetcher(url)
        raw = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            output_format="json",
        )
    except Exception:
        return _skipped(url, "extraction_failed")
    # trafilatura.extract(output_format="json") returns None when nothing is
    # extracted, else a JSON string with "title"/"date"/"text" keys.
    if not raw:
        return _skipped(url, "no_extractable_text")
    try:
        document = json.loads(raw)
    except (ValueError, TypeError):
        return _skipped(url, "no_extractable_text")
    text = document.get("text") or ""
    if not text.strip():
        return _skipped(url, "no_extractable_text")
    title = (document.get("title") or "").strip() or None
    date = (document.get("date") or "").strip() or None
    return ArticleExtractionResult(
        url=url,
        title=title,
        text=text[: source.article.max_summary_chars],
        published_at=date,
        skipped=False,
        reason=None,
    )


def _skipped(url: str, reason: str) -> ArticleExtractionResult:
    return ArticleExtractionResult(url=url, skipped=True, reason=reason)


def _is_paywalled_domain(url: str, paywalled_domains: list[str]) -> bool:
    hostname = (urlsplit(url).hostname or "").lower().removeprefix("www.")
    for domain in paywalled_domains:
        normalized_domain = domain.lower().removeprefix("www.")
        if hostname == normalized_domain or hostname.endswith(f".{normalized_domain}"):
            return True
    return False
