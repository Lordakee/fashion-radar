from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.local_article_anchors import (
    LOCAL_ARTICLE_BODY_CONTAINER_ANCHOR,
    LOCAL_ARTICLE_SECTION_ANCHOR,
    html_ids,
    local_article_content_section_anchor,
    local_article_paragraph_anchor,
)
from fashion_radar.row_one.models import RowOneLocalArticle


@dataclass(frozen=True)
class RowOneLocalArticleContentHealth:
    status: str
    article_count: int
    paragraph_anchor_count: int
    content_section_anchor_count: int
    missing_article_sections: tuple[str, ...]
    missing_body_containers: tuple[str, ...]
    missing_paragraph_anchors: tuple[str, ...]
    missing_content_section_anchors: tuple[str, ...]


def build_row_one_local_article_content_health(
    site_dir: Path,
    articles: Mapping[str, RowOneLocalArticle] | None = None,
) -> RowOneLocalArticleContentHealth:
    resolved_articles = _resolve_articles(site_dir, articles)
    renderable_articles = tuple(
        (story_id, article)
        for story_id, article in resolved_articles
        if _rendered_paragraph_indices(article)
    )
    if not renderable_articles:
        return RowOneLocalArticleContentHealth(
            status="not_applicable",
            article_count=0,
            paragraph_anchor_count=0,
            content_section_anchor_count=0,
            missing_article_sections=(),
            missing_body_containers=(),
            missing_paragraph_anchors=(),
            missing_content_section_anchors=(),
        )

    paragraph_anchor_count = 0
    content_section_anchor_count = 0
    missing_article_sections: list[str] = []
    missing_body_containers: list[str] = []
    missing_paragraph_anchors: list[str] = []
    missing_content_section_anchors: list[str] = []

    for story_id, article in renderable_articles:
        page_path = site_dir / "articles" / f"{story_id}.html"
        ids = html_ids(page_path)
        if LOCAL_ARTICLE_SECTION_ANCHOR not in ids:
            missing_article_sections.append(_anchor_path(story_id, LOCAL_ARTICLE_SECTION_ANCHOR))
        if LOCAL_ARTICLE_BODY_CONTAINER_ANCHOR not in ids:
            missing_body_containers.append(
                _anchor_path(story_id, LOCAL_ARTICLE_BODY_CONTAINER_ANCHOR)
            )

        for anchor in _expected_paragraph_anchor_ids(article):
            if anchor in ids:
                paragraph_anchor_count += 1
            else:
                missing_paragraph_anchors.append(_anchor_path(story_id, anchor))

        for anchor in _expected_content_section_anchor_ids(article):
            if anchor in ids:
                content_section_anchor_count += 1
            else:
                missing_content_section_anchors.append(_anchor_path(story_id, anchor))

    status = (
        "ready"
        if not missing_article_sections
        and not missing_body_containers
        and not missing_paragraph_anchors
        and not missing_content_section_anchors
        else "missing"
    )
    return RowOneLocalArticleContentHealth(
        status=status,
        article_count=len(renderable_articles),
        paragraph_anchor_count=paragraph_anchor_count,
        content_section_anchor_count=content_section_anchor_count,
        missing_article_sections=tuple(missing_article_sections),
        missing_body_containers=tuple(missing_body_containers),
        missing_paragraph_anchors=tuple(missing_paragraph_anchors),
        missing_content_section_anchors=tuple(missing_content_section_anchors),
    )


def row_one_local_article_content_health_payload(
    health: RowOneLocalArticleContentHealth,
) -> dict[str, object]:
    return {
        "status": health.status,
        "article_count": health.article_count,
        "paragraph_anchor_count": health.paragraph_anchor_count,
        "content_section_anchor_count": health.content_section_anchor_count,
        "missing_article_sections": list(health.missing_article_sections),
        "missing_body_containers": list(health.missing_body_containers),
        "missing_paragraph_anchors": list(health.missing_paragraph_anchors),
        "missing_content_section_anchors": list(health.missing_content_section_anchors),
    }


def validate_row_one_local_article_content_health(
    health: RowOneLocalArticleContentHealth,
) -> None:
    if health.status in {"ready", "not_applicable"}:
        return
    if health.missing_article_sections:
        raise ValueError(
            f"row-one local article section is missing: {health.missing_article_sections[0]}"
        )
    if health.missing_body_containers:
        raise ValueError(
            f"row-one local article body container is missing: {health.missing_body_containers[0]}"
        )
    if health.missing_paragraph_anchors:
        raise ValueError(
            "row-one local article paragraph anchor is missing: "
            f"{health.missing_paragraph_anchors[0]}"
        )
    if health.missing_content_section_anchors:
        raise ValueError(
            "row-one local article content-section anchor is missing: "
            f"{health.missing_content_section_anchors[0]}"
        )
    raise ValueError("row-one local article content health is missing")


def _resolve_articles(
    site_dir: Path,
    articles: Mapping[str, RowOneLocalArticle] | None,
) -> tuple[tuple[str, RowOneLocalArticle], ...]:
    if articles is not None:
        return tuple(sorted(articles.items(), key=lambda item: item[0]))

    articles_dir = site_dir / "data" / "articles"
    if not articles_dir.is_dir():
        return ()

    resolved: list[tuple[str, RowOneLocalArticle]] = []
    for article_path in sorted(articles_dir.glob("*.json")):
        story_id = article_path.stem
        if not safe_local_article_story_id(story_id):
            continue
        try:
            payload = json.loads(article_path.read_text(encoding="utf-8"))
            article = RowOneLocalArticle.model_validate(payload)
        except (OSError, json.JSONDecodeError, ValidationError):
            continue
        if article.story_id != story_id:
            continue
        resolved.append((story_id, article))
    return tuple(resolved)


def _expected_paragraph_anchor_ids(article: RowOneLocalArticle) -> tuple[str, ...]:
    return tuple(
        local_article_paragraph_anchor(index) for index in _rendered_paragraph_indices(article)
    )


def _expected_content_section_anchor_ids(article: RowOneLocalArticle) -> tuple[str, ...]:
    return tuple(
        local_article_content_section_anchor(position)
        for position, _section in enumerate(article.content_sections, start=1)
    )


def _rendered_paragraph_indices(article: RowOneLocalArticle) -> tuple[int, ...]:
    return tuple(index for index, paragraph in enumerate(article.paragraphs) if paragraph.strip())


def _anchor_path(story_id: str, anchor: str) -> str:
    return f"articles/{story_id}.html#{anchor}"
