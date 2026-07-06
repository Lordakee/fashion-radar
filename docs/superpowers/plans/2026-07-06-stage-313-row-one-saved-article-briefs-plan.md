# Stage 313 ROW ONE Saved Article Briefs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> When spawning Codex subagents for this project, set `reasoning_effort` to `xhigh` as required by `AGENTS.md`.

**Goal:** Add a generated-site homepage Saved Article Briefs section that surfaces readable takeaways and reference chips from current-edition saved local articles.

**Architecture:** Add an internal dataclass builder for saved article brief cards, pass it from `render_row_one_site()` into `render_index_html()`, and render a static homepage section only when publishable saved article briefs exist. Keep the data out of app JSON, manifest/runtime contracts, schemas, Pydantic app models, and generated JSON artifacts.

**Tech Stack:** Python 3.12, dataclasses, existing ROW ONE Pydantic models, static HTML/CSS template helpers, pytest, ruff, frozen/no-config uv verification.

**Pipeline Gap Closed:** This closes a report-layer content organization gap: Stage 312 shows that local saved article coverage exists, while Stage 313 shows source-backed saved article takeaways directly on the homepage without adding collection, scoring, LLM, or app-contract surfaces.

---

## Non-Goals

- Do not add source collection, scraping, browser automation, platform APIs,
  login/cookie/proxy/CAPTCHA behavior, paywall bypass, social/community
  connectors, LLM calls, translation services, image generation, scheduling,
  scoring, demand proof, platform coverage verification, or compliance-review
  product features.
- Do not change `row-one-app/v7`, `data/edition.json`,
  `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, story IDs, detail
  routes, or paragraph anchors.
- Do not add a new JSON artifact in this stage.
- Do not republish full external articles on the homepage. The homepage card
  renders a capped local excerpt, source name, and a link into the generated
  detail page where retained local text is already attributed.
- Do not commit generated `reports/row-one/site/**`.
- Do not rewrite `uv.lock` to mirror URLs.

## Files

- Create: `src/fashion_radar/row_one/detail_routes.py`
  - Shared internal validation for ROW ONE generated detail-page paths and
    path-plus-fragment hrefs.
- Modify: `src/fashion_radar/row_one/saved_article_coverage.py`
  - Reuse the shared detail-route helper instead of owning a duplicate regex.
- Create: `src/fashion_radar/row_one/saved_article_briefs.py`
  - Internal dataclasses and builder for homepage saved article brief cards.
- Modify: `src/fashion_radar/row_one/render.py`
  - Build briefs and pass them to `render_index_html()`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Accept saved article briefs in `render_index_html()`.
  - Render homepage Saved Article Briefs section.
  - Add safe href handling and CSS selectors.
- Create: `tests/test_row_one_saved_article_briefs.py`
  - Unit coverage for builder selection, filtering, fallback, references, and cap.
- Modify: `tests/test_row_one_render.py`
  - Integration coverage for homepage rendering, escaping, contracts, href filtering, CSS.
- Modify: `tests/test_row_one_docs.py`
  - Docs boundary coverage scoped to the Stage 313 paragraph.
- Modify: `README.md`, `docs/row-one.md`
  - Document Stage 313 boundary.
- Create review artifacts under `docs/reviews/`.

## Task 1: Add Failing Builder Tests

**Files:**
- Create: `tests/test_row_one_saved_article_briefs.py`

- [ ] **Step 1: Add imports and fixtures**

Create a test file with reusable ROW ONE fixtures:

```python
from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
    RowOneReference,
    RowOneSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_briefs import (
    build_row_one_saved_article_briefs,
)

AS_OF = datetime(2026, 7, 6, 4, 0, tzinfo=UTC)


def _story(story_id: str, headline: str, *, section_key: str = "top_stories") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        section_key=section_key,
        story_type="tracked_entity",
        headline=headline,
        summary=LocalizedText(zh=f"{headline} 摘要", en=f"{headline} summary"),
        why_it_matters=LocalizedText(zh="重要。", en="Important."),
        editorial_takeaway=LocalizedText(zh="编辑判断。", en="Editorial read."),
        signal_context=LocalizedText(zh="信号背景。", en="Signal context."),
        reader_path=LocalizedText(zh="阅读路径。", en="Reader path."),
        source_name="Story Source",
        source_url="https://example.com/story",
        published_at=AS_OF,
        detail_path=f"details/{story_id}.html",
        tags=[],
        evidence=[],
    )


def _edition(*stories: RowOneStory) -> RowOneEdition:
    return RowOneEdition(
        brand="ROW ONE",
        generated_at=AS_OF,
        edition_date=AS_OF,
        summary=LocalizedText(zh="今日摘要。", en="Daily summary."),
        sections=[
            RowOneSection(
                key="top_stories",
                title=LocalizedText(zh="今日重点", en="Top Stories"),
                dek=LocalizedText(zh="重点。", en="Top reads."),
            ),
            RowOneSection(
                key="brand_moves",
                title=LocalizedText(zh="品牌动态", en="Brand Moves"),
                dek=LocalizedText(zh="品牌。", en="Brands."),
            ),
        ],
        stories=list(stories),
    )


def _article(
    story_id: str,
    *,
    source_name: str = "Vogue Business",
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        title=f"{story_id} article",
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        paragraphs_zh=paragraphs_zh,
        content_sections=content_sections or [],
    )


def _content_item(
    label: str,
    *,
    body: str | None = None,
    body_zh: str | None = None,
    references: list[RowOneReference] | None = None,
    paragraph_indices: list[int] | None = None,
) -> RowOneLocalArticleContentItem:
    return RowOneLocalArticleContentItem(
        label=LocalizedText(zh=label, en=label),
        body=(
            LocalizedText(zh=body_zh if body_zh is not None else body or "", en=body or "")
            if body is not None
            else None
        ),
        references=references or [],
        paragraph_indices=paragraph_indices or [],
    )


def _section(
    key: str,
    title: str,
    *,
    items: list[RowOneLocalArticleContentItem] | None = None,
) -> RowOneLocalArticleContentSection:
    return RowOneLocalArticleContentSection(
        key=key,
        title=LocalizedText(zh=title, en=title),
        items=items or [],
    )
```

- [ ] **Step 2: Add lead/reference extraction test**

Add:

```python
def test_saved_article_briefs_use_takeaway_and_reference_chips() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")
    coverage = build_row_one_saved_article_briefs(
        _edition(story),
        {
            story.id: _article(
                story.id,
                content_sections=[
                    _section(
                        "takeaways",
                        "Takeaways",
                        items=[
                            _content_item(
                                "Lead",
                                body="The Row pushed a quiet luxury merchandising signal.",
                                body_zh="The Row 释放安静奢华陈列信号。",
                                paragraph_indices=[0],
                            )
                        ],
                    ),
                    _section(
                        "entities",
                        "Entities",
                        items=[
                            _content_item(
                                "Brands",
                                references=[
                                    RowOneReference(
                                        name="The Row",
                                        type="brand",
                                        label="tracked",
                                    ),
                                    RowOneReference(
                                        name="Mary-Kate Olsen",
                                        type="person",
                                        label="designer",
                                    ),
                                ],
                            )
                        ],
                    ),
                    _section(
                        "product_signals",
                        "Products",
                        items=[
                            _content_item(
                                "Products",
                                references=[
                                    RowOneReference(name="Margaux", type="bag", label="product"),
                                    RowOneReference(name="Margaux", type="bag", label="product"),
                                ],
                            )
                        ],
                    ),
                ],
            )
        },
    )

    assert coverage is not None
    assert coverage.article_count == 1
    assert len(coverage.items) == 1
    item = coverage.items[0]
    assert item.title.en == "The Row coverage"
    assert item.section_title.en == "Top Stories"
    assert item.source_name == "Vogue Business"
    assert item.lead.en == "The Row pushed a quiet luxury merchandising signal."
    assert item.lead.zh == "The Row 释放安静奢华陈列信号。"
    assert item.detail_path == "details/the-row-a-1234567890.html#local-article-digest"
    assert [(ref.name, ref.type, ref.label) for ref in item.people_brands] == [
        ("The Row", "brand", "tracked"),
        ("Mary-Kate Olsen", "person", "designer"),
    ]
    assert [(ref.name, ref.type, ref.label) for ref in item.products] == [
        ("Margaux", "bag", "product"),
    ]
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_briefs.py::test_saved_article_briefs_use_takeaway_and_reference_chips -q
```

Expected: FAIL because `saved_article_briefs.py` does not exist.

- [ ] **Step 3: Add paragraph fallback/filter/cap test**

Add:

```python
def test_saved_article_briefs_filter_invalid_articles_and_cap_cards() -> None:
    stories = [_story(f"story-{index}-1234567890", f"Story {index}") for index in range(1, 7)]
    bad_path_story = _story("bad-path-1234567890", "Bad Path").model_copy(
        update={"detail_path": "../private.html"}
    )
    bad_id_story = _story("bad id", "Bad ID").model_copy(
        update={"detail_path": "details/bad-id-1234567890.html"}
    )
    coverage = build_row_one_saved_article_briefs(
        _edition(*stories, bad_path_story, bad_id_story),
        {
            **{
                story.id: _article(
                    story.id,
                    paragraphs=["   ", f"Paragraph {index}."],
                    paragraphs_zh=["   ", f"段落 {index}。"],
                )
                for index, story in enumerate(stories, start=1)
            },
            bad_path_story.id: _article(bad_path_story.id),
            bad_id_story.id: _article(bad_id_story.id),
            "not-in-edition-1234567890": _article("not-in-edition-1234567890"),
            "bad id": _article("bad id"),
        },
    )

    assert coverage is not None
    assert coverage.article_count == 6
    assert len(coverage.items) == 4
    assert [item.title.en for item in coverage.items] == [
        "Story 1",
        "Story 2",
        "Story 3",
        "Story 4",
    ]
    assert coverage.items[0].lead.en == "Paragraph 1."
    assert coverage.items[0].lead.zh == "段落 1。"
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_briefs.py::test_saved_article_briefs_filter_invalid_articles_and_cap_cards -q
```

Expected: FAIL until the builder exists.

- [ ] **Step 4: Add empty test**

Add:

```python
def test_saved_article_briefs_omit_without_publishable_articles() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")

    assert build_row_one_saved_article_briefs(_edition(story), {}) is None
    assert (
        build_row_one_saved_article_briefs(
            _edition(story),
            {story.id: _article(story.id, paragraphs=["   "])},
        )
        is None
    )
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_briefs.py::test_saved_article_briefs_omit_without_publishable_articles -q
```

Expected: FAIL until the builder exists.

## Task 2: Add Shared Detail Route Helper

**Files:**
- Create: `src/fashion_radar/row_one/detail_routes.py`
- Modify: `src/fashion_radar/row_one/saved_article_coverage.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add shared helper**

Create `src/fashion_radar/row_one/detail_routes.py`:

```python
from __future__ import annotations

import re
from pathlib import PurePosixPath

DETAIL_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}-[0-9a-f]{10}\.html$")


def validated_row_one_detail_relative_path(path: str) -> PurePosixPath | None:
    pure_path = PurePosixPath(path)
    if (
        pure_path.is_absolute()
        or len(pure_path.parts) != 2
        or pure_path.parts[0] != "details"
        or pure_path.parts[1] in ("", ".", "..")
        or ".." in pure_path.parts
        or DETAIL_FILENAME_RE.fullmatch(pure_path.name) is None
    ):
        return None
    return pure_path


def is_safe_row_one_detail_path(path: str) -> bool:
    return validated_row_one_detail_relative_path(path) is not None


def safe_row_one_detail_fragment_href(href: object, fragment: str) -> str | None:
    if not isinstance(href, str):
        return None
    if "#" not in href:
        return None
    path, actual_fragment = href.split("#", 1)
    if actual_fragment != fragment:
        return None
    if validated_row_one_detail_relative_path(path) is None:
        return None
    return href
```

- [ ] **Step 2: Reuse helper in saved article coverage**

In `src/fashion_radar/row_one/saved_article_coverage.py`, remove local
`re`, `PurePosixPath`, `_DETAIL_FILENAME_RE`, and `_safe_detail_path`. Import:

```python
from fashion_radar.row_one.detail_routes import is_safe_row_one_detail_path
```

Replace:

```python
if not _safe_detail_path(story.detail_path):
    continue
```

with:

```python
if not is_safe_row_one_detail_path(story.detail_path):
    continue
```

- [ ] **Step 3: Reuse helper in templates**

In `src/fashion_radar/row_one/templates.py`, import:

```python
from fashion_radar.row_one.detail_routes import (
    safe_row_one_detail_fragment_href,
    validated_row_one_detail_relative_path,
)
```

Keep `_validated_detail_relative_path()` as the existing local compatibility
wrapper, but implement it through the shared helper:

```python
def _validated_detail_relative_path(path: str) -> PurePosixPath | None:
    return validated_row_one_detail_relative_path(path)
```

Update `_safe_saved_article_coverage_href()`:

```python
def _safe_saved_article_coverage_href(href: object) -> str | None:
    return safe_row_one_detail_fragment_href(href, "local-article-digest")
```

- [ ] **Step 4: Verify existing coverage path tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_coverage.py tests/test_row_one_render.py::test_render_row_one_site_rejects_invalid_saved_article_coverage_links -q
```

Expected: PASS.

## Task 3: Implement Builder

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_briefs.py`

- [ ] **Step 1: Create dataclasses and constants**

Create:

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.detail_routes import is_safe_row_one_detail_path
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneReference,
)
from fashion_radar.row_one.text import normalize_row_one_paragraph

MAX_SAVED_ARTICLE_BRIEF_ITEMS = 4
MAX_SAVED_ARTICLE_BRIEF_REFERENCES = 4


@dataclass(frozen=True)
class RowOneSavedArticleBriefItem:
    title: LocalizedText
    section_title: LocalizedText
    source_name: str
    lead: LocalizedText
    detail_path: str
    people_brands: tuple[RowOneReference, ...]
    products: tuple[RowOneReference, ...]


@dataclass(frozen=True)
class RowOneSavedArticleBriefs:
    article_count: int
    items: list[RowOneSavedArticleBriefItem]
```

- [ ] **Step 2: Implement selection and helpers**

Add:

```python
def build_row_one_saved_article_briefs(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedArticleBriefs | None:
    items: list[RowOneSavedArticleBriefItem] = []
    publishable_count = 0
    for story in edition.stories:
        article = local_articles_by_story_id.get(story.id)
        if article is None:
            continue
        if not safe_local_article_story_id(story.id):
            continue
        if not is_safe_row_one_detail_path(story.detail_path):
            continue
        if not _has_nonblank_paragraph(article):
            continue
        lead = _lead_text(article)
        publishable_count += 1
        if len(items) >= MAX_SAVED_ARTICLE_BRIEF_ITEMS:
            continue
        items.append(
            RowOneSavedArticleBriefItem(
                title=LocalizedText(zh=story.headline, en=story.headline),
                section_title=_section_title(edition, story.section_key),
                source_name=article.source_name.strip() or "Unknown source",
                lead=lead,
                detail_path=f"{story.detail_path}#local-article-digest",
                people_brands=_references(article, "entities"),
                products=_references(article, "product_signals"),
            )
        )
    if publishable_count == 0:
        return None
    return RowOneSavedArticleBriefs(article_count=publishable_count, items=items)


def _has_nonblank_paragraph(article: RowOneLocalArticle) -> bool:
    return any(paragraph.strip() for paragraph in article.paragraphs)


def _lead_text(article: RowOneLocalArticle) -> LocalizedText | None:
    for section in article.content_sections:
        if section.key != "takeaways":
            continue
        for item in section.items:
            if item.body is not None and item.body.en.strip():
                return item.body
    return _first_paragraph_text(article)


def _first_paragraph_text(article: RowOneLocalArticle) -> LocalizedText | None:
    for index, paragraph in enumerate(article.paragraphs):
        if not paragraph.strip():
            continue
        zh = paragraph
        if (
            article.paragraphs_zh is not None
            and len(article.paragraphs_zh) == len(article.paragraphs)
            and article.paragraphs_zh[index].strip()
        ):
            zh = article.paragraphs_zh[index]
        return LocalizedText(zh=zh, en=paragraph)
    return None


def _references(article: RowOneLocalArticle, section_key: str) -> tuple[RowOneReference, ...]:
    refs: list[RowOneReference] = []
    seen: set[tuple[str, str, str]] = set()
    for section in article.content_sections:
        if section.key != section_key:
            continue
        for item in section.items:
            for ref in item.references:
                key = (
                    normalize_row_one_paragraph(ref.name).casefold(),
                    ref.type.strip().casefold(),
                    ref.label.strip().casefold(),
                )
                if not key[0] or key in seen:
                    continue
                seen.add(key)
                refs.append(ref)
                if len(refs) >= MAX_SAVED_ARTICLE_BRIEF_REFERENCES:
                    return tuple(refs)
    return tuple(refs)


def _section_title(edition: RowOneEdition, section_key: str) -> LocalizedText:
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    fallback = section_key.replace("_", " ").title()
    return LocalizedText(zh=fallback, en=fallback)
```

- [ ] **Step 3: Verify builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_briefs.py -q
```

Expected: PASS.

## Task 4: Add Failing Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add homepage render test**

Add a test near the saved article coverage tests:

```python
def test_render_row_one_site_includes_saved_article_briefs(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row saved source",
        url="https://example.com/the-row-local",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["Fallback paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="要点", en="Takeaways"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="要点", en="Lead"),
                        body=LocalizedText(
                            zh="The Row 保存正文要点。",
                            en="The Row saved article lead.",
                        ),
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="品牌", en="Entities"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="品牌", en="Brands"),
                        references=[RowOneReference(name="The Row", type="brand", label="tracked")],
                    )
                ],
            ),
            RowOneLocalArticleContentSection(
                key="product_signals",
                title=LocalizedText(zh="产品", en="Products"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="产品", en="Products"),
                        references=[RowOneReference(name="Margaux", type="bag", label="product")],
                    )
                ],
            ),
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_payload = json.loads((tmp_path / "data" / "edition.json").read_text())
    manifest_payload = json.loads((tmp_path / "data" / "manifest.json").read_text())
    runtime_payload = json.loads((tmp_path / "data" / "runtime.json").read_text())
    briefs_html = html[
        html.index('class="saved-article-briefs"') : html.index('class="lead-story"')
    ]

    assert '<span data-lang="en">Saved Article Briefs</span>' in briefs_html
    assert '<span data-lang="zh">保存正文简报</span>' in briefs_html
    assert "The Row saved article lead." in briefs_html
    assert "The Row 保存正文要点。" in briefs_html
    assert "Vogue Business" in briefs_html
    assert "The Row" in briefs_html
    assert "Margaux" in briefs_html
    assert 'href="details/the-row-signal-1234567890.html#local-article-digest"' in briefs_html
    assert html.index('class="saved-article-coverage"') < html.index(
        'class="saved-article-briefs"'
    )
    assert html.index('class="saved-article-briefs"') < html.index('class="lead-story"')
    assert edition_payload["contract_version"] == "row-one-app/v7"
    assert manifest_payload["contract_version"] == "row-one-manifest/v1"
    assert manifest_payload["app_contract"]["version"] == "row-one-app/v7"
    assert runtime_payload["contract_version"] == "row-one-runtime/v1"
    for app_contract_json in (
        json.dumps(edition_payload, ensure_ascii=False),
        json.dumps(manifest_payload, ensure_ascii=False),
        json.dumps(runtime_payload, ensure_ascii=False),
    ):
        assert "saved_article_briefs" not in app_contract_json
        assert "Saved Article Briefs" not in app_contract_json
        assert "saved-article-briefs" not in app_contract_json
        assert "The Row saved article lead." not in app_contract_json
    assert not (tmp_path / "data" / "saved-article-briefs.json").exists()
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_briefs -q
```

Expected: FAIL until render wiring exists.

- [ ] **Step 2: Add omission, escaping, href, and CSS tests**

Add:

```python
def test_render_row_one_site_omits_saved_article_briefs_without_saved_articles(tmp_path) -> None:
    render_row_one_site(_edition(), tmp_path)

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "saved-article-briefs" not in html


def test_render_row_one_site_escapes_saved_article_briefs(tmp_path) -> None:
    edition = _edition()
    unsafe_story = edition.stories[0].model_copy(
        update={"headline": '<script>alert("headline")</script>'}
    )
    edition.stories = [unsafe_story]
    local_article = RowOneLocalArticle(
        story_id=unsafe_story.id,
        title="Unsafe brief source",
        url="https://example.com/unsafe",
        source_name="<Vogue>",
        extracted_at=AS_OF,
        paragraphs=['<script>alert("body")</script>'],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="entities",
                title=LocalizedText(zh="品牌", en="Entities"),
                items=[
                    RowOneLocalArticleContentItem(
                        label=LocalizedText(zh="品牌", en="Brands"),
                        references=[RowOneReference(name="<The Row>", type="brand", label="tracked")],
                    )
                ],
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={unsafe_story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    briefs_html = html[
        html.index('class="saved-article-briefs"') : html.index('class="lead-story"')
    ]
    assert "&lt;script&gt;alert(&quot;headline&quot;)&lt;/script&gt;" in briefs_html
    assert "&lt;script&gt;alert(&quot;body&quot;)&lt;/script&gt;" in briefs_html
    assert "&lt;Vogue&gt;" in briefs_html
    assert "&lt;The Row&gt;" in briefs_html
    assert "<script>" not in briefs_html
    assert "<Vogue>" not in briefs_html
    assert "<The Row>" not in briefs_html


def test_row_one_css_includes_saved_article_briefs_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-briefs",
        ".saved-article-briefs-header",
        ".saved-article-briefs-grid",
        ".saved-article-brief-card",
        ".saved-article-brief-chip-list",
        ".saved-article-brief-chip",
    ):
        assert re.search(rf"(^|[}}\n,])\s*{re.escape(selector)}\s*({{|,)", css_text)
```

For direct bad-href filtering, import the new dataclasses from
`fashion_radar.row_one.saved_article_briefs` and add a small helper/test:

```python
from typing import cast


def test_render_row_one_site_rejects_invalid_saved_article_brief_links() -> None:
    briefs = RowOneSavedArticleBriefs(
        article_count=5,
        items=[
            RowOneSavedArticleBriefItem(
                title=LocalizedText(zh="Valid", en="Valid"),
                section_title=LocalizedText(zh="今日重点", en="Top Stories"),
                source_name="Vogue Business",
                lead=LocalizedText(zh="Valid digest brief.", en="Valid digest brief."),
                detail_path="details/the-row-signal-1234567890.html#local-article-digest",
                people_brands=(),
                products=(),
            ),
            RowOneSavedArticleBriefItem(
                title=LocalizedText(zh="Wrong", en="Wrong"),
                section_title=LocalizedText(zh="今日重点", en="Top Stories"),
                source_name="Vogue Business",
                lead=LocalizedText(zh="Wrong fragment brief.", en="Wrong fragment brief."),
                detail_path="details/the-row-signal-1234567890.html#local-article-body",
                people_brands=(),
                products=(),
            ),
            RowOneSavedArticleBriefItem(
                title=LocalizedText(zh="Traversal", en="Traversal"),
                section_title=LocalizedText(zh="今日重点", en="Top Stories"),
                source_name="Vogue Business",
                lead=LocalizedText(zh="Traversal brief.", en="Traversal brief."),
                detail_path="../private.html#local-article-digest",
                people_brands=(),
                products=(),
            ),
            RowOneSavedArticleBriefItem(
                title=LocalizedText(zh="Script", en="Script"),
                section_title=LocalizedText(zh="今日重点", en="Top Stories"),
                source_name="Vogue Business",
                lead=LocalizedText(zh="Script brief.", en="Script brief."),
                detail_path="javascript:alert(1)#local-article-digest",
                people_brands=(),
                products=(),
            ),
            RowOneSavedArticleBriefItem(
                title=LocalizedText(zh="Non-string", en="Non-string"),
                section_title=LocalizedText(zh="今日重点", en="Top Stories"),
                source_name="Vogue Business",
                lead=LocalizedText(zh="Non-string brief.", en="Non-string brief."),
                detail_path=cast(str, 123),
                people_brands=(),
                products=(),
            ),
        ],
    )

    html = render_index_html(_edition(), saved_article_briefs=briefs)
    briefs_html = html[
        html.index('class="saved-article-briefs"') : html.index('class="lead-story"')
    ]

    assert "Valid digest brief." in briefs_html
    assert "Wrong fragment brief" not in briefs_html
    assert "Traversal brief" not in briefs_html
    assert "Script brief" not in briefs_html
    assert "Non-string brief" not in briefs_html
    assert "#local-article-body" not in briefs_html
    assert "../private.html" not in briefs_html
    assert "javascript:alert" not in briefs_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_omits_saved_article_briefs_without_saved_articles \
  tests/test_row_one_render.py::test_render_row_one_site_escapes_saved_article_briefs \
  tests/test_row_one_render.py::test_render_row_one_site_rejects_invalid_saved_article_brief_links \
  tests/test_row_one_render.py::test_row_one_css_includes_saved_article_briefs_styles -q
```

Expected: FAIL until render wiring exists.

## Task 5: Implement Render Wiring, Template, And CSS

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Wire builder in `render.py`**

Import:

```python
from fashion_radar.row_one.saved_article_briefs import build_row_one_saved_article_briefs
```

Inside `render_row_one_site()` after `saved_article_coverage`:

```python
    saved_article_briefs = build_row_one_saved_article_briefs(
        edition,
        local_articles_by_story_id,
    )
```

Pass into `render_index_html()`:

```python
            saved_article_briefs=saved_article_briefs,
```

- [ ] **Step 2: Add template parameter and insertion point**

Import dataclasses in `templates.py`:

```python
from fashion_radar.row_one.saved_article_briefs import (
    RowOneSavedArticleBriefItem,
    RowOneSavedArticleBriefs,
)
```

Update `render_index_html()` signature:

```python
    saved_article_briefs: RowOneSavedArticleBriefs | None = None,
```

Compute:

```python
    saved_article_briefs_section = _render_saved_article_briefs(saved_article_briefs)
```

Insert after `{saved_article_coverage_section}` and before `{lead_story_block}`:

```html
{saved_article_coverage_section}
{saved_article_briefs_section}
{lead_story_block}
```

- [ ] **Step 3: Add saved brief render helpers**

Add helpers near saved article coverage helpers:

```python
def _render_saved_article_briefs(briefs: RowOneSavedArticleBriefs | None) -> str:
    if briefs is None or not briefs.items:
        return ""
    cards = [_render_saved_article_brief_card(item) for item in briefs.items]
    cards = [card for card in cards if card]
    if not cards:
        return ""
    rendered_cards = "\n".join(cards)
    return f"""<section class="saved-article-briefs" aria-label="Saved article briefs">
  <div class="saved-article-briefs-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Briefs</span>
        <span data-lang="zh">保存正文简报</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Briefs</span>
        <span data-lang="zh">保存正文简报</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">Readable takeaways from today's locally saved article bodies.</span>
      <span data-lang="zh">来自今日本地保存正文的可读要点。</span>
    </p>
  </div>
  <div class="saved-article-briefs-grid">{rendered_cards}</div>
</section>"""
```

Implement `_render_saved_article_brief_card()`, `_render_saved_article_brief_chips()`,
and `_safe_saved_article_brief_href()`:

```python
def _render_saved_article_brief_card(item: RowOneSavedArticleBriefItem) -> str:
    href = _safe_saved_article_brief_href(item.detail_path)
    if href is None:
        return ""
    people = _render_saved_article_brief_chips(
        "People & Brands",
        "品牌与人物",
        item.people_brands,
    )
    products = _render_saved_article_brief_chips("Products", "产品", item.products)
    return f"""    <a class="saved-article-brief-card" href="{_esc(href)}">
      <span class="saved-article-brief-meta">
        <span data-lang="en">{_esc(item.section_title.en)}</span>
        <span data-lang="zh">{_esc(item.section_title.zh)}</span>
        <span>{_esc(item.source_name)}</span>
      </span>
      <h3>
        <span data-lang="en">{_esc(item.title.en)}</span>
        <span data-lang="zh">{_esc(item.title.zh)}</span>
      </h3>
      <p class="saved-article-brief-lead">
        <span data-lang="en">{_esc(_meta_description(item.lead.en, limit=180))}</span>
        <span data-lang="zh">{_esc(_meta_description(item.lead.zh, limit=180))}</span>
      </p>
      {people}
      {products}
    </a>"""


def _render_saved_article_brief_chips(
    label_en: str,
    label_zh: str,
    references: Sequence[RowOneReference],
) -> str:
    if not references:
        return ""
    chips = "".join(
        f'<span class="saved-article-brief-chip">{_esc(ref.name)}</span>'
        for ref in references
    )
    return f"""<div class="saved-article-brief-chip-list">
        <span class="saved-article-brief-chip-label">
          <span data-lang="en">{_esc(label_en)}</span>
          <span data-lang="zh">{_esc(label_zh)}</span>
        </span>
        {chips}
      </div>"""


def _safe_saved_article_brief_href(href: object) -> str | None:
    return safe_row_one_detail_fragment_href(href, "local-article-digest")
```

- [ ] **Step 4: Add CSS**

Add CSS near saved article coverage:

```css
.saved-article-briefs {
  border-bottom: 1px solid var(--ink);
  margin: 0 0 32px;
  padding: 0 0 32px;
}
.saved-article-briefs-header {
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(180px, 0.42fr) minmax(0, 1fr);
  margin-bottom: 18px;
}
.saved-article-briefs-header h2 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 5.8rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.92;
  margin: 0;
}
.saved-article-briefs-header p {
  align-self: end;
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  max-width: 720px;
}
.saved-article-briefs-grid {
  background: var(--line);
  border: 1px solid var(--line);
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.saved-article-brief-card {
  background: var(--panel);
  color: inherit;
  display: grid;
  gap: 12px;
  min-height: 260px;
  padding: 18px;
  text-decoration: none;
}
.saved-article-brief-card h3 {
  font-family: RowOneSerif, Georgia, serif;
  font-size: clamp(1.45rem, 2.4vw, 2.5rem);
  font-weight: 500;
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}
.saved-article-brief-meta,
.saved-article-brief-chip-label {
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 8px 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.saved-article-brief-lead {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
}
.saved-article-brief-chip-list {
  border-top: 1px solid var(--line);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 10px;
}
.saved-article-brief-chip {
  border: 1px solid var(--line);
  color: var(--ink);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  padding: 5px 7px;
  text-transform: uppercase;
}
```

Add mobile rule under `@media (max-width: 760px)`:

```css
  .saved-article-briefs-header { grid-template-columns: 1fr; }
  .saved-article-briefs-grid { grid-template-columns: 1fr; }
```

- [ ] **Step 5: Verify render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_saved_article_briefs.py \
  tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_briefs \
  tests/test_row_one_render.py::test_render_row_one_site_omits_saved_article_briefs_without_saved_articles \
  tests/test_row_one_render.py::test_render_row_one_site_escapes_saved_article_briefs \
  tests/test_row_one_render.py::test_render_row_one_site_rejects_invalid_saved_article_brief_links \
  tests/test_row_one_render.py::test_row_one_css_includes_saved_article_briefs_styles -q
```

Expected: PASS.

## Task 6: Docs Boundary

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add docs test**

Add to `tests/test_row_one_docs.py` near the Stage 312 test:

```python
def test_row_one_docs_describe_saved_article_briefs_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")
    readme_stage_313 = readme[
        readme.index("Stage 313 adds homepage saved article briefs") : readme.index(
            "Stage 312 adds"
        )
    ]
    docs_stage_313 = docs[
        docs.index("Stage 313 adds homepage saved article briefs") : docs.index(
            "Stage 312 adds"
        )
    ]
    readme_stage_313_normalized = _normalized(readme_stage_313)
    docs_stage_313_normalized = _normalized(docs_stage_313)

    expected_phrases = [
        "saved article briefs",
        "homepage saved article briefs",
        "uses existing `data/articles/<story-id>.json` sidecars",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not write a new json artifact",
        "does not change detail routes",
        "does not change paragraph anchors",
        "does not change schemas",
        "does not add source collection",
        "does not add scoring",
        "does not add llm calls",
    ]
    for phrase in expected_phrases:
        assert phrase in readme_stage_313_normalized
        assert phrase in docs_stage_313_normalized

    forbidden_phrases = [
        "row-one-app/v8",
        "row-one-manifest/v2",
        "row-one-runtime/v2",
        "changes schemas",
        "changes detail routes",
        "adds source collection",
        "adds scoring",
        "adds llm calls",
        "adds social connectors",
        "adds community connectors",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in readme_stage_313_normalized
        assert phrase not in docs_stage_313_normalized
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_saved_article_briefs_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Add README and docs wording**

Insert before the Stage 312 paragraph in both `README.md` and `docs/row-one.md`:

```markdown
Stage 313 adds homepage saved article briefs for ROW ONE: existing saved local article sidecars are organized into capped homepage cards with a lead saved-text excerpt, source name, section context, people/brand chips, and product chips. This is homepage saved article briefs only; it uses existing `data/articles/<story-id>.json` sidecars, does not change `row-one-app/v7`, does not change `data/edition.json`, does not change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not write a new json artifact, does not change detail routes, does not change paragraph anchors, does not change schemas, does not add source collection, does not add scoring, and does not add llm calls.
```

- [ ] **Step 3: Verify docs**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_saved_article_briefs_boundary -q
```

Expected: PASS.

## Task 7: Verification, Review, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-313-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-313-code-review.md`
- Create rereview artifacts if required by review findings.

- [ ] **Step 1: Run focused verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_briefs.py tests/test_row_one_render.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
```

Expected: PASS.

- [ ] **Step 2: Run full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Expected:

- full test suite passes;
- lock check passes;
- release hygiene passes;
- build writes ROW ONE site;
- status returns `"ok": true`.

- [ ] **Step 3: Request Claude Code code review**

Create `docs/reviews/claude-code-stage-313-code-review-prompt.md` with:

```markdown
# Claude Code Stage 313 Code Review Prompt

You are the primary local Claude Code reviewer for Fashion Radar Stage 313.
Use maximum reasoning. Review the current uncommitted working tree in
`/home/ubuntu/fashion-radar`.

Goal: add a generated-site-only ROW ONE homepage Saved Article Briefs section
that surfaces readable takeaways and reference chips from current-edition saved
local article sidecars.

Required boundaries: no changes to `row-one-app/v7`, `data/edition.json`,
`row-one-manifest/v1`, `row-one-runtime/v1`, schemas, story IDs, detail routes,
or paragraph anchors; no new JSON artifact; no source collection, scraping,
scoring, LLM calls, social/community connectors, scheduling, or
compliance-review product features.

Inspect changed code, tests, docs, and review artifacts. Return findings first,
ordered by Critical, Important, then Minor. Include exact file and line
references. If no Critical or Important findings remain, say so clearly.
```

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-313-code-review-prompt.md)" > "$tmp_review"
sed -n '1,500p' "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-313-code-review.md
rm -f "$tmp_review"
```

Expected: completed Claude Code review with no Critical or Important findings.
If Claude Code is unavailable, record a clean unavailability note and use
opencode fallback with `zhipuai-coding-plan/glm-5.2 --variant max`.

- [ ] **Step 4: Fix review findings**

Fix all Critical and Important findings. If fixes are made, rerun focused
tests, full verification as needed, and request rereview.

- [ ] **Step 5: Check staged files**

```bash
git status --short --branch
git diff --check
git add README.md docs/row-one.md \
  src/fashion_radar/row_one/detail_routes.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/saved_article_coverage.py \
  src/fashion_radar/row_one/templates.py \
  src/fashion_radar/row_one/saved_article_briefs.py \
  tests/test_row_one_saved_article_briefs.py \
  tests/test_row_one_render.py tests/test_row_one_docs.py \
  docs/reviews/claude-code-stage-313-code-review-prompt.md \
  docs/reviews/claude-code-stage-313-code-review.md
git diff --cached --name-only -- uv.lock reports/row-one/site .codegraph
git diff --cached --check
```

Expected: no `uv.lock`, generated site, or CodeGraph files staged.

- [ ] **Step 6: Commit and push**

```bash
git commit -m "Stage 313: add row one saved article briefs"
git push origin main
git status --short --branch
```

Expected: push succeeds and worktree is clean.
