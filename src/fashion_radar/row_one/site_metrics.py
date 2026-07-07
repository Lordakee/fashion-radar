from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from fashion_radar.row_one.models import RowOneLocalArticle


@dataclass(frozen=True)
class RowOneLocalArticleSiteMetrics:
    article_count: int = 0
    paragraph_count: int = 0
    organized_section_count: int = 0
    source_count: int = 0
    extracted_article_count: int = 0
    summary_fallback_article_count: int = 0
    skipped_article_count: int = 0


def build_row_one_local_article_site_metrics(site_dir: Path) -> RowOneLocalArticleSiteMetrics:
    articles_dir = site_dir / "data" / "articles"
    if not articles_dir.is_dir():
        return RowOneLocalArticleSiteMetrics()

    return build_row_one_local_article_metrics(
        article
        for article_path in sorted(articles_dir.glob("*.json"))
        if (article := _load_article(article_path)) is not None
    )


def build_row_one_local_article_metrics(
    articles: Iterable[RowOneLocalArticle],
) -> RowOneLocalArticleSiteMetrics:
    article_count = 0
    paragraph_count = 0
    organized_section_count = 0
    extracted_article_count = 0
    summary_fallback_article_count = 0
    skipped_article_count = 0
    sources: set[str] = set()
    for article in articles:
        article_count += 1
        paragraph_count += sum(1 for paragraph in article.paragraphs if paragraph.strip())
        organized_section_count += len(article.content_sections)
        if article.body_source == "summary_fallback":
            summary_fallback_article_count += 1
        elif article.body_source == "skipped" or article.skipped:
            skipped_article_count += 1
        else:
            extracted_article_count += 1
        source_name = article.source_name.strip()
        if source_name:
            sources.add(" ".join(source_name.split()).casefold())

    return RowOneLocalArticleSiteMetrics(
        article_count=article_count,
        paragraph_count=paragraph_count,
        organized_section_count=organized_section_count,
        source_count=len(sources),
        extracted_article_count=extracted_article_count,
        summary_fallback_article_count=summary_fallback_article_count,
        skipped_article_count=skipped_article_count,
    )


def row_one_local_article_site_metrics_payload(
    metrics: RowOneLocalArticleSiteMetrics,
) -> dict[str, int]:
    return {
        "article_count": metrics.article_count,
        "paragraph_count": metrics.paragraph_count,
        "organized_section_count": metrics.organized_section_count,
        "source_count": metrics.source_count,
        "extracted_article_count": metrics.extracted_article_count,
        "summary_fallback_article_count": metrics.summary_fallback_article_count,
        "skipped_article_count": metrics.skipped_article_count,
    }


def _load_article(path: Path) -> RowOneLocalArticle | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return RowOneLocalArticle.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError):
        return None
