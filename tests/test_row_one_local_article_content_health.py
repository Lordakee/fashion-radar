from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from fashion_radar.row_one.local_article_content_health import (
    RowOneLocalArticleContentHealth,
    build_row_one_local_article_content_health,
    row_one_local_article_content_health_payload,
    validate_row_one_local_article_content_health,
)
from fashion_radar.row_one.models import RowOneLocalArticle


def _article(
    story_id: str = "the-row-signal-1234567890",
    *,
    paragraphs: list[str] | None = None,
    content_section_count: int = 1,
    skipped: bool = False,
) -> RowOneLocalArticle:
    return RowOneLocalArticle.model_validate(
        {
            "story_id": story_id,
            "url": f"https://example.com/{story_id}",
            "title": "The Row signal",
            "source_name": "Example",
            "extracted_at": "2026-07-10T04:00:00Z",
            "body_source": "skipped" if skipped else "extracted",
            "skipped": skipped,
            "reason": "no_publishable_paragraphs" if skipped else None,
            "paragraphs": (
                ["First saved paragraph.", "Second saved paragraph."]
                if paragraphs is None
                else paragraphs
            ),
            "paragraphs_zh": (
                ["第一段。", "第二段。"]
                if paragraphs is None
                else ["翻译段落。" for _ in paragraphs]
            ),
            "brief_sections": [],
            "content_sections": [
                {
                    "key": "brand_signals",
                    "title": {"en": f"Brand Signals {index}", "zh": f"品牌信号 {index}"},
                    "body": {"en": "The Row appears.", "zh": "The Row 出现。"},
                    "items": [
                        {
                            "label": {"en": "The Row", "zh": "The Row"},
                            "body": {"en": "Brand evidence.", "zh": "品牌证据。"},
                            "references": [{"name": "The Row", "type": "brand", "label": "brand"}],
                            "paragraph_indices": [0],
                        }
                    ],
                }
                for index in range(1, content_section_count + 1)
            ],
        }
    )


def _write_article_sidecar(
    site_dir: Path,
    article: RowOneLocalArticle,
    *,
    filename_stem: str | None = None,
) -> None:
    articles_dir = site_dir / "data" / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    stem = filename_stem or article.story_id
    (articles_dir / f"{stem}.json").write_text(
        article.model_dump_json(),
        encoding="utf-8",
    )


def _write_article_page(site_dir: Path, story_id: str, html: str) -> None:
    article_dir = site_dir / "articles"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / f"{story_id}.html").write_text(html, encoding="utf-8")


def _article_html(
    *,
    article_section: bool = True,
    body_container: bool = True,
    paragraph_anchors: tuple[int, ...] = (1, 2),
    content_section_anchors: tuple[int, ...] = (1,),
) -> str:
    parts = ["<!doctype html><title>ROW ONE article</title>"]
    if article_section:
        parts.append('<section id="local-article">')
    if body_container:
        parts.append('<div id="local-article-body">')
    for number in paragraph_anchors:
        parts.append(f'<p id="local-article-paragraph-{number}">Paragraph {number}</p>')
    if body_container:
        parts.append("</div>")
    for number in content_section_anchors:
        parts.append(
            f'<article id="local-article-content-section-{number}">Section {number}</article>'
        )
    if article_section:
        parts.append("</section>")
    return "".join(parts)


def test_content_health_is_not_applicable_without_saved_article_sidecars(
    tmp_path: Path,
) -> None:
    health = build_row_one_local_article_content_health(tmp_path)

    assert health == RowOneLocalArticleContentHealth(
        status="not_applicable",
        article_count=0,
        paragraph_anchor_count=0,
        content_section_anchor_count=0,
        missing_article_sections=(),
        missing_body_containers=(),
        missing_paragraph_anchors=(),
        missing_content_section_anchors=(),
    )


def test_content_health_reports_ready_for_rendered_article_body_and_anchors(
    tmp_path: Path,
) -> None:
    article = _article()
    _write_article_page(tmp_path, article.story_id, _article_html())

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={article.story_id: article},
    )

    assert health.status == "ready"
    assert health.article_count == 1
    assert health.paragraph_anchor_count == 2
    assert health.content_section_anchor_count == 1
    assert health.missing_article_sections == ()
    assert health.missing_body_containers == ()
    assert health.missing_paragraph_anchors == ()
    assert health.missing_content_section_anchors == ()


def test_content_health_reports_missing_local_article_section(tmp_path: Path) -> None:
    article = _article()
    _write_article_page(tmp_path, article.story_id, _article_html(article_section=False))

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={article.story_id: article},
    )

    assert health.status == "missing"
    assert health.missing_article_sections == (
        "articles/the-row-signal-1234567890.html#local-article",
    )


def test_content_health_reports_missing_body_container(tmp_path: Path) -> None:
    article = _article()
    _write_article_page(tmp_path, article.story_id, _article_html(body_container=False))

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={article.story_id: article},
    )

    assert health.status == "missing"
    assert health.missing_body_containers == (
        "articles/the-row-signal-1234567890.html#local-article-body",
    )


def test_content_health_reports_missing_paragraph_anchors_deterministically(
    tmp_path: Path,
) -> None:
    first = _article("story-a-1234567890", paragraphs=["First", "", "Third"])
    second = _article("story-b-1234567890", paragraphs=["First", "Second"])
    _write_article_page(
        tmp_path,
        first.story_id,
        _article_html(paragraph_anchors=(1,), content_section_anchors=(1,)),
    )
    _write_article_page(
        tmp_path,
        second.story_id,
        _article_html(paragraph_anchors=(), content_section_anchors=(1,)),
    )

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={second.story_id: second, first.story_id: first},
    )

    assert health.status == "missing"
    assert health.paragraph_anchor_count == 1
    assert health.missing_paragraph_anchors == (
        "articles/story-a-1234567890.html#local-article-paragraph-3",
        "articles/story-b-1234567890.html#local-article-paragraph-1",
        "articles/story-b-1234567890.html#local-article-paragraph-2",
    )


def test_content_health_reports_missing_content_section_anchors_deterministically(
    tmp_path: Path,
) -> None:
    first = _article("story-a-1234567890", content_section_count=2)
    second = _article("story-b-1234567890", content_section_count=2)
    _write_article_page(
        tmp_path,
        first.story_id,
        _article_html(content_section_anchors=(1,)),
    )
    _write_article_page(
        tmp_path,
        second.story_id,
        _article_html(content_section_anchors=()),
    )

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={second.story_id: second, first.story_id: first},
    )

    assert health.status == "missing"
    assert health.content_section_anchor_count == 1
    assert health.missing_content_section_anchors == (
        "articles/story-a-1234567890.html#local-article-content-section-2",
        "articles/story-b-1234567890.html#local-article-content-section-1",
        "articles/story-b-1234567890.html#local-article-content-section-2",
    )


def test_content_health_uses_supplied_articles_exactly(tmp_path: Path) -> None:
    supplied = _article("supplied-1234567890")
    ignored = _article("ignored-1234567890")
    _write_article_sidecar(tmp_path, ignored)
    _write_article_page(tmp_path, supplied.story_id, _article_html())

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={supplied.story_id: supplied},
    )

    assert health.status == "ready"
    assert health.article_count == 1
    assert health.missing_article_sections == ()


def test_content_health_trusts_supplied_articles_without_discovery_filters(
    tmp_path: Path,
) -> None:
    article = _article("model-story-1234567890")
    supplied_story_id = "supplied-story-1234567890"
    _write_article_page(tmp_path, supplied_story_id, _article_html())

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={supplied_story_id: article},
    )

    assert health.status == "ready"
    assert health.article_count == 1
    assert health.missing_article_sections == ()


def test_content_health_payload_is_stable(tmp_path: Path) -> None:
    article = _article()
    _write_article_page(tmp_path, article.story_id, _article_html())

    payload = row_one_local_article_content_health_payload(
        build_row_one_local_article_content_health(
            tmp_path,
            articles={article.story_id: article},
        )
    )

    assert payload == {
        "status": "ready",
        "article_count": 1,
        "paragraph_anchor_count": 2,
        "content_section_anchor_count": 1,
        "missing_article_sections": [],
        "missing_body_containers": [],
        "missing_paragraph_anchors": [],
        "missing_content_section_anchors": [],
    }

    not_applicable_payload = row_one_local_article_content_health_payload(
        build_row_one_local_article_content_health(tmp_path / "empty-site")
    )

    assert not_applicable_payload == {
        "status": "not_applicable",
        "article_count": 0,
        "paragraph_anchor_count": 0,
        "content_section_anchor_count": 0,
        "missing_article_sections": [],
        "missing_body_containers": [],
        "missing_paragraph_anchors": [],
        "missing_content_section_anchors": [],
    }


def test_validate_content_health_raises_clear_errors() -> None:
    ready = RowOneLocalArticleContentHealth(
        status="ready",
        article_count=1,
        paragraph_anchor_count=2,
        content_section_anchor_count=1,
        missing_article_sections=(),
        missing_body_containers=(),
        missing_paragraph_anchors=(),
        missing_content_section_anchors=(),
    )
    validate_row_one_local_article_content_health(ready)
    validate_row_one_local_article_content_health(
        replace(ready, status="not_applicable", article_count=0)
    )

    with pytest.raises(ValueError, match="local article section is missing"):
        validate_row_one_local_article_content_health(
            replace(
                ready,
                status="missing",
                missing_article_sections=("articles/story.html#local-article",),
            )
        )
    with pytest.raises(ValueError, match="body container is missing"):
        validate_row_one_local_article_content_health(
            replace(
                ready,
                status="missing",
                missing_body_containers=("articles/story.html#local-article-body",),
            )
        )
    with pytest.raises(ValueError, match="paragraph anchor is missing"):
        validate_row_one_local_article_content_health(
            replace(
                ready,
                status="missing",
                missing_paragraph_anchors=("articles/story.html#local-article-paragraph-1",),
            )
        )
    with pytest.raises(ValueError, match="content-section anchor is missing"):
        validate_row_one_local_article_content_health(
            replace(
                ready,
                status="missing",
                missing_content_section_anchors=(
                    "articles/story.html#local-article-content-section-1",
                ),
            )
        )


def test_content_health_discovery_ignores_unsafe_sidecar_stems(tmp_path: Path) -> None:
    article = _article("safe-story-1234567890")
    _write_article_sidecar(tmp_path, article)
    _write_article_page(tmp_path, article.story_id, _article_html())
    articles_dir = tmp_path / "data" / "articles"
    (articles_dir / "unsafe story.json").write_text("{}", encoding="utf-8")
    (articles_dir / "unsafe.html").write_text("{}", encoding="utf-8")

    health = build_row_one_local_article_content_health(tmp_path)

    assert health.status == "ready"
    assert health.article_count == 1


def test_content_health_discovery_ignores_malformed_sidecars(tmp_path: Path) -> None:
    article = _article("safe-story-1234567890")
    _write_article_sidecar(tmp_path, article)
    _write_article_page(tmp_path, article.story_id, _article_html())
    articles_dir = tmp_path / "data" / "articles"
    (articles_dir / "malformed-1234567890.json").write_text("{", encoding="utf-8")
    (articles_dir / "invalid-model-1234567890.json").write_text("{}", encoding="utf-8")

    health = build_row_one_local_article_content_health(tmp_path)

    assert health.status == "ready"
    assert health.article_count == 1


def test_content_health_accepts_html_id_attribute_variants(tmp_path: Path) -> None:
    article = _article()
    _write_article_page(
        tmp_path,
        article.story_id,
        """
        <!doctype html>
        <section class="local-article" ID = 'local-article'>
          <div data-kind="body" id = 'local-article-body'>
            <p class="copy" ID="local-article-paragraph-1">One</p>
            <p id='local-article-paragraph-2' class="copy">Two</p>
          </div>
          <article data-kind="section" ID = "local-article-content-section-1"></article>
        </section>
        """,
    )

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={article.story_id: article},
    )

    assert health.status == "ready"


def test_content_health_ignores_empty_paragraph_sidecars_without_anchor_expectations(
    tmp_path: Path,
) -> None:
    article = _article(
        "empty-signal-1234567890",
        paragraphs=[],
        content_section_count=0,
        skipped=True,
    )

    health = build_row_one_local_article_content_health(
        tmp_path,
        articles={article.story_id: article},
    )

    assert health.status == "not_applicable"
    assert health.article_count == 0
    assert health.paragraph_anchor_count == 0
    assert health.content_section_anchor_count == 0
    assert health.missing_article_sections == ()
    assert health.missing_body_containers == ()
    assert health.missing_paragraph_anchors == ()
    assert health.missing_content_section_anchors == ()


def test_validate_content_health_accepts_not_applicable() -> None:
    validate_row_one_local_article_content_health(
        RowOneLocalArticleContentHealth(
            status="not_applicable",
            article_count=0,
            paragraph_anchor_count=0,
            content_section_anchor_count=0,
            missing_article_sections=(),
            missing_body_containers=(),
            missing_paragraph_anchors=(),
            missing_content_section_anchors=(),
        )
    )
