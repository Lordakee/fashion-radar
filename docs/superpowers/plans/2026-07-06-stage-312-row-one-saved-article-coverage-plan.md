# Stage 312 ROW ONE Saved Article Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> When spawning Codex subagents for this project, set `reasoning_effort` to `xhigh` as required by `AGENTS.md`.

**Goal:** Add a generated-site homepage Saved Article Coverage section that summarizes the current ROW ONE edition's locally saved article corpus.

**Architecture:** Add a small internal dataclass builder for homepage coverage data, pass it from `render_row_one_site()` into `render_index_html()`, and render a static homepage section only when publishable local articles exist. Keep the data out of `data/edition.json`, manifest/runtime contracts, schemas, Pydantic app models, and generated JSON artifacts.

**Tech Stack:** Python 3.12, dataclasses, existing ROW ONE Pydantic models, static HTML/CSS template helpers, pytest, ruff, frozen/no-config uv verification.

**Pipeline Gap Closed:** This closes a report-layer overview gap: Stage 311 organizes one saved article on its detail page, while Stage 312 organizes the day's saved article set on the homepage without adding collection, scoring, or app-contract surfaces.

---

## Non-Goals

- Do not add source collection, scraping, browser automation, platform APIs,
  login/cookie/proxy/CAPTCHA behavior, paywall bypass, social/community
  connectors, LLM calls, translation services, image generation, scheduling,
  scoring, demand proof, or platform coverage verification.
- Do not change `row-one-app/v7`, `data/edition.json`,
  `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, story IDs, detail
  routes, or paragraph anchors.
- Do not add a new JSON artifact in this stage.
- Do not commit generated `reports/row-one/site/**`.
- Do not rewrite `uv.lock` to mirror URLs.

## Files

- Create: `src/fashion_radar/row_one/saved_article_coverage.py`
  - Internal dataclasses and builder for homepage saved article coverage.
- Modify: `src/fashion_radar/row_one/render.py`
  - Build coverage and pass it to `render_index_html()`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Accept coverage in `render_index_html()`.
  - Render homepage Saved Article Coverage section.
  - Add CSS selectors.
- Create: `tests/test_row_one_saved_article_coverage.py`
  - Unit coverage for builder counts, filtering, ordering, source grouping.
- Modify: `tests/test_row_one_render.py`
  - Integration coverage for homepage rendering, escaping, contracts, CSS.
- Modify: `tests/test_row_one_docs.py`
  - Docs boundary coverage.
- Modify: `README.md`, `docs/row-one.md`
  - Document Stage 312 boundary.
- Create review artifacts under `docs/reviews/`.

## Task 1: Add Failing Builder Tests

**Files:**
- Create: `tests/test_row_one_saved_article_coverage.py`

- [ ] **Step 1: Add builder import and fixtures**

Create the test file:

```python
from __future__ import annotations

from datetime import UTC, datetime

from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentSection,
    RowOneSection,
    RowOneStory,
)
from fashion_radar.row_one.saved_article_coverage import (
    build_row_one_saved_article_coverage,
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
    organized_sections: int = 1,
) -> RowOneLocalArticle:
    sections = [
        RowOneLocalArticleContentSection(
            key="takeaways",
            title=LocalizedText(zh="要点", en="Takeaways"),
        )
        for _ in range(organized_sections)
    ]
    return RowOneLocalArticle(
        story_id=story_id,
        title=f"{story_id} article",
        url=f"https://example.com/{story_id}",
        source_name=source_name,
        extracted_at=AS_OF,
        paragraphs=paragraphs or ["First saved paragraph.", "Second saved paragraph."],
        content_sections=sections,
    )
```

- [ ] **Step 2: Add mixed filtering/counting test**

Add:

```python
def test_saved_article_coverage_counts_only_current_publishable_articles() -> None:
    story_a = _story("the-row-a-1234567890", "The Row coverage")
    story_b = _story("coach-b-1234567890", "Coach coverage", section_key="brand_moves")
    coverage = build_row_one_saved_article_coverage(
        _edition(story_a, story_b),
        {
            story_a.id: _article(
                story_a.id,
                source_name="Vogue Business",
                paragraphs=["A paragraph.", "   ", "Another paragraph."],
                organized_sections=2,
            ),
            story_b.id: _article(
                story_b.id,
                source_name="Vogue Business",
                paragraphs=["Coach paragraph."],
                organized_sections=1,
            ),
            "not-in-edition-1234567890": _article("not-in-edition-1234567890"),
            "bad id": _article("bad id"),
        },
    )

    assert coverage is not None
    assert coverage.article_count == 2
    assert coverage.saved_paragraph_count == 3
    assert coverage.organized_section_count == 3
    assert coverage.source_count == 1
    assert [(source.name, source.article_count) for source in coverage.sources] == [
        ("Vogue Business", 2)
    ]
    assert [item.title.en for item in coverage.items] == [
        "The Row coverage",
        "Coach coverage",
    ]
    assert [item.section_title.en for item in coverage.items] == [
        "Top Stories",
        "Brand Moves",
    ]
    assert [item.saved_paragraph_count for item in coverage.items] == [2, 1]
    assert [item.organized_section_count for item in coverage.items] == [2, 1]
    assert coverage.items[0].detail_path == (
        "details/the-row-a-1234567890.html#local-article-digest"
    )
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_coverage.py::test_saved_article_coverage_counts_only_current_publishable_articles -q
```

Expected: FAIL because `saved_article_coverage.py` does not exist.

- [ ] **Step 3: Add empty/no publishable coverage test**

Add:

```python
def test_saved_article_coverage_omits_when_no_publishable_articles() -> None:
    story = _story("the-row-a-1234567890", "The Row coverage")

    assert build_row_one_saved_article_coverage(_edition(story), {}) is None
    assert (
        build_row_one_saved_article_coverage(
            _edition(story),
            {story.id: _article(story.id, paragraphs=["   "])},
        )
        is None
    )
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_coverage.py::test_saved_article_coverage_omits_when_no_publishable_articles -q
```

Expected: FAIL until the builder exists.

- [ ] **Step 4: Add item cap/source ordering test**

Add:

```python
def test_saved_article_coverage_limits_read_queue_to_four_in_edition_order() -> None:
    stories = [
        _story(f"story-{index}-1234567890", f"Story {index}")
        for index in range(1, 7)
    ]
    coverage = build_row_one_saved_article_coverage(
        _edition(*stories),
        {
            story.id: _article(
                story.id,
                source_name="Vogue" if index % 2 else "Business of Fashion",
            )
            for index, story in enumerate(stories, start=1)
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
    # Source chips preserve first-seen source order from the edition story order.
    assert [(source.name, source.article_count) for source in coverage.sources] == [
        ("Vogue", 3),
        ("Business of Fashion", 3),
    ]
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_coverage.py::test_saved_article_coverage_limits_read_queue_to_four_in_edition_order -q
```

Expected: FAIL until builder exists.

## Task 2: Implement Coverage Builder

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_coverage.py`

- [ ] **Step 1: Add dataclasses and constants**

Create:

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.models import LocalizedText, RowOneEdition, RowOneLocalArticle

MAX_SAVED_ARTICLE_COVERAGE_ITEMS = 4


@dataclass(frozen=True)
class RowOneSavedArticleCoverageSource:
    name: str
    article_count: int


@dataclass(frozen=True)
class RowOneSavedArticleCoverageItem:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    detail_path: str
    saved_paragraph_count: int
    organized_section_count: int


@dataclass(frozen=True)
class RowOneSavedArticleCoverage:
    article_count: int
    saved_paragraph_count: int
    organized_section_count: int
    source_count: int
    sources: list[RowOneSavedArticleCoverageSource]
    items: list[RowOneSavedArticleCoverageItem]
```

- [ ] **Step 2: Add helper functions**

Add:

```python
def _saved_paragraph_count(article: RowOneLocalArticle) -> int:
    return sum(1 for paragraph in article.paragraphs if paragraph.strip())


def _source_display_name(article: RowOneLocalArticle) -> str:
    return article.source_name.strip() or "Unknown source"


def _source_key(name: str) -> str:
    return " ".join(name.split()).casefold()


def _section_title(edition: RowOneEdition, section_key: str) -> LocalizedText:
    for section in edition.sections:
        if section.key == section_key:
            return section.title
    fallback = section_key.replace("_", " ").title()
    return LocalizedText(zh=fallback, en=fallback)
```

- [ ] **Step 3: Add builder**

Add:

```python
def build_row_one_saved_article_coverage(
    edition: RowOneEdition,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
) -> RowOneSavedArticleCoverage | None:
    story_articles = []
    for position, story in enumerate(edition.stories):
        article = local_articles_by_story_id.get(story.id)
        if article is None:
            continue
        if not safe_local_article_story_id(story.id):
            continue
        saved_paragraph_count = _saved_paragraph_count(article)
        if saved_paragraph_count == 0:
            continue
        story_articles.append((position, story, article, saved_paragraph_count))
    if not story_articles:
        return None

    source_counts: dict[str, tuple[str, int]] = {}
    items: list[RowOneSavedArticleCoverageItem] = []
    for _, story, article, saved_paragraph_count in story_articles:
        source_name = _source_display_name(article)
        source_key = _source_key(source_name)
        display_name, count = source_counts.get(source_key, (source_name, 0))
        source_counts[source_key] = (display_name, count + 1)
        items.append(
            RowOneSavedArticleCoverageItem(
                title=LocalizedText(zh=story.headline, en=story.headline),
                source_name=source_name,
                section_title=_section_title(edition, story.section_key),
                detail_path=f"{story.detail_path}#local-article-digest",
                saved_paragraph_count=saved_paragraph_count,
                organized_section_count=len(article.content_sections),
            )
        )

    sources = [
        RowOneSavedArticleCoverageSource(name=name, article_count=count)
        for name, count in source_counts.values()
    ]
    return RowOneSavedArticleCoverage(
        article_count=len(story_articles),
        saved_paragraph_count=sum(item.saved_paragraph_count for item in items),
        organized_section_count=sum(item.organized_section_count for item in items),
        source_count=len(sources),
        sources=sources,
        items=items[:MAX_SAVED_ARTICLE_COVERAGE_ITEMS],
    )
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_coverage.py -q
```

Expected: PASS.

## Task 3: Add Failing Homepage Render Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add homepage coverage rendering test**

Add near existing Daily Local Intelligence tests:

```python
def test_render_row_one_site_includes_saved_article_coverage(tmp_path) -> None:
    edition = _edition()
    story = edition.stories[0]
    story.section_key = "top_stories"
    local_article = RowOneLocalArticle(
        story_id=story.id,
        title="The Row saved source",
        url="https://example.com/the-row-local",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        paragraphs=["The Row saved paragraph.", "Second saved paragraph."],
        content_sections=[
            RowOneLocalArticleContentSection(
                key="takeaways",
                title=LocalizedText(zh="要点", en="Takeaways"),
            )
        ],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    edition_json = (tmp_path / "data" / "edition.json").read_text(encoding="utf-8")

    assert 'class="saved-article-coverage"' in html
    assert '<span data-lang="en">Saved Article Coverage</span>' in html
    assert '<span data-lang="zh">保存正文覆盖</span>' in html
    assert "1 saved article" in html
    assert "2 saved paragraphs" in html
    assert "1 organized section" in html
    assert "1 source" in html
    assert "Vogue Business" in html
    assert "The Row &lt;signals&gt; &quot;quiet&quot; demand" in html
    assert "Top Stories" in html
    assert (
        'href="details/the-row-signal-1234567890.html#local-article-digest"'
        in html
    )
    assert html.index('class="daily-local-intelligence"') < html.index(
        'class="saved-article-coverage"'
    )
    assert html.index('class="saved-article-coverage"') < html.index('class="lead-story"')
    assert "saved_article_coverage" not in edition_json
    assert "Saved Article Coverage" not in edition_json
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_coverage -q
```

Expected: FAIL until render wiring exists.

- [ ] **Step 2: Add omission and escaping tests**

Add:

```python
def test_render_row_one_site_omits_saved_article_coverage_without_saved_articles(
    tmp_path,
) -> None:
    render_row_one_site(_edition(), tmp_path)

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "saved-article-coverage" not in html


def test_render_row_one_site_escapes_saved_article_coverage(tmp_path) -> None:
    edition = _edition()
    unsafe_story = edition.stories[0].model_copy(
        update={"headline": '<script>alert("headline")</script>'}
    )
    edition.stories = [unsafe_story]
    local_article = RowOneLocalArticle(
        story_id=unsafe_story.id,
        title="Unsafe coverage source",
        url="https://example.com/unsafe",
        source_name="<Vogue>",
        extracted_at=AS_OF,
        paragraphs=['<script>alert("body")</script>'],
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={unsafe_story.id: local_article},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    coverage_html = html[
        html.index('class="saved-article-coverage"') : html.index('class="lead-story"')
    ]

    assert "&lt;script&gt;alert(&quot;headline&quot;)&lt;/script&gt;" in coverage_html
    assert "&lt;Vogue&gt;" in coverage_html
    assert "<script>" not in coverage_html
    assert "<Vogue>" not in coverage_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_omits_saved_article_coverage_without_saved_articles tests/test_row_one_render.py::test_render_row_one_site_escapes_saved_article_coverage -q
```

Expected: omission test may PASS before implementation; escaping test FAIL until render wiring exists.

- [ ] **Step 3: Add dedicated CSS selector test**

Add a new test:

```python
def test_row_one_css_includes_saved_article_coverage_styles(tmp_path) -> None:
    css = render_row_one_site(_edition(), tmp_path).index_path
    css_text = (css.parent / "assets" / "row-one.css").read_text(encoding="utf-8")

    for selector in (
        ".saved-article-coverage",
        ".saved-article-coverage-header",
        ".saved-article-coverage-metrics",
        ".saved-article-coverage-sources",
        ".saved-article-coverage-grid",
        ".saved-article-coverage-card",
    ):
        assert selector in css_text
```

Run the CSS test. Expected: FAIL until CSS is added.

## Task 4: Wire Coverage Into Render And Template

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Import and build coverage in render.py**

Add import:

```python
from fashion_radar.row_one.saved_article_coverage import (
    build_row_one_saved_article_coverage,
)
```

Inside `render_row_one_site()`, after `local_article_intelligence`:

```python
saved_article_coverage = build_row_one_saved_article_coverage(
    edition,
    local_articles_by_story_id,
)
```

Pass it:

```python
render_index_html(
    edition,
    app_payload=app_payload,
    local_article_intelligence=local_article_intelligence,
    saved_article_coverage=saved_article_coverage,
)
```

- [ ] **Step 2: Add template import and function parameter**

In `templates.py`, import:

```python
from fashion_radar.row_one.saved_article_coverage import RowOneSavedArticleCoverage
```

Change `render_index_html()` signature:

```python
def render_index_html(
    edition: RowOneEdition,
    *,
    app_payload: dict[str, object] | None = None,
    local_article_intelligence: Sequence[RowOneDailyLocalIntelligenceSection] | None = None,
    saved_article_coverage: RowOneSavedArticleCoverage | None = None,
) -> str:
```

Compute:

```python
saved_article_coverage_section = _render_saved_article_coverage(saved_article_coverage)
```

Insert after `{daily_local_intelligence}` and before `{lead_story_block}`.

- [ ] **Step 3: Add coverage template helpers**

Add helpers near `_render_daily_local_intelligence()`:

```python
def _render_saved_article_coverage(coverage: RowOneSavedArticleCoverage | None) -> str:
    if coverage is None or coverage.article_count == 0:
        return ""
    metrics = _render_saved_article_coverage_metrics(coverage)
    sources = _render_saved_article_coverage_sources(coverage)
    cards = "\n".join(_render_saved_article_coverage_card(item) for item in coverage.items)
    return f"""<section class="saved-article-coverage" aria-label="Saved article coverage">
  <div class="saved-article-coverage-header">
    <div>
      <p class="story-section">
        <span data-lang="en">Saved Article Coverage</span>
        <span data-lang="zh">保存正文覆盖</span>
      </p>
      <h2>
        <span data-lang="en">Saved Article Coverage</span>
        <span data-lang="zh">保存正文覆盖</span>
      </h2>
    </div>
    <p>
      <span data-lang="en">The local source set behind today's saved article pages.</span>
      <span data-lang="zh">今日保存正文页面背后的本地来源集合。</span>
    </p>
  </div>
  {metrics}
  {sources}
  <div class="saved-article-coverage-grid">{cards}</div>
</section>"""
```

Add metric helpers with singular/plural English and simple Chinese labels:

```python
def _count_label(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"
```

Use `data-lang` spans for:

- saved article/articles / 保存文章;
- saved paragraph/paragraphs / 保存段落;
- organized section/sections / 整理栏目;
- source/sources / 来源.

Coverage cards should render:

```html
<a class="saved-article-coverage-card" href="...#local-article-digest">
```

and include story title, source name, section title, paragraph count, and
organized section count. Escape all values with `_esc()`.

- [ ] **Step 4: Add CSS**

Add restrained homepage CSS near `.daily-local-intelligence` styles:

```css
.saved-article-coverage {
  border-top: 1px solid var(--ink);
  margin: 34px 0;
  padding-top: 24px;
}
.saved-article-coverage-header {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(260px, 0.42fr);
  gap: 24px;
  margin-bottom: 16px;
}
.saved-article-coverage-metrics,
.saved-article-coverage-sources {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 0 0 14px;
  padding: 0;
}
.saved-article-coverage-metrics li,
.saved-article-coverage-sources li {
  border: 1px solid var(--line);
  padding: 8px 10px;
}
.saved-article-coverage-grid {
  display: grid;
  gap: 1px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.saved-article-coverage-card {
  background: var(--panel);
  border: 1px solid var(--line);
  color: inherit;
  display: grid;
  gap: 10px;
  padding: 14px;
  text-decoration: none;
}
```

Add mobile rules under `@media (max-width: 760px)`:

```css
.saved-article-coverage-header { grid-template-columns: 1fr; }
.saved-article-coverage-grid { grid-template-columns: 1fr; }
```

Run homepage render tests and CSS test. Expected: PASS.

## Task 5: Docs And Boundary Tests

**Files:**
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add docs test**

Add near saved text digest docs test:

```python
def test_row_one_docs_describe_saved_article_coverage_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "row-one.md").read_text(encoding="utf-8")

    expected_phrases = [
        "saved article coverage",
        "homepage saved article coverage",
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
        assert phrase in readme
        assert phrase in docs
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_saved_article_coverage_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Update README and docs**

Add to both README and `docs/row-one.md`, near the Stage 311 paragraph:

```markdown
Stage 312 adds homepage saved article coverage for ROW ONE: existing saved
local article sidecars are summarized as a homepage coverage strip with saved
article counts, saved paragraph counts, source counts, source chips, and a read
queue linking into local detail-page digests. This is homepage saved article
coverage only; it uses existing `data/articles/<story-id>.json` sidecars, does
not change `row-one-app/v7`, does not change `data/edition.json`, does not
change `row-one-manifest/v1`, does not change `row-one-runtime/v1`, does not
write a new json artifact, does not change detail routes, does not change
paragraph anchors, does not change schemas, does not add source collection,
does not add scoring, and does not add llm calls.
```

Run docs test. Expected: PASS.

## Task 6: Verification, Review, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-312-code-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-312-code-review.md` or a clean
  Claude-unavailable record if Claude Code returns server-side errors.
- Create fallback opencode review artifacts if Claude Code is unavailable.

- [ ] **Step 1: Focused verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_coverage.py tests/test_row_one_render.py tests/test_row_one_docs.py -q
```

Expected: PASS.

- [ ] **Step 2: Full verification**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
```

Expected: all PASS.

- [ ] **Step 3: Build ignored sample site and check status**

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Expected: `ok: true`, app `row-one-app/v7`, manifest
`row-one-manifest/v1`, runtime `row-one-runtime/v1`.

- [ ] **Step 4: Request code review**

Use Claude Code primary route:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-312-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-312-code-review.md
```

If Claude Code returns server-side 524 timeouts again, record a clean
availability note and use opencode fallback:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-312-code-review-prompt.md)" \
  > docs/reviews/opencode-stage-312-code-review.md
```

Fix Critical/Important findings and rerun relevant verification.

- [ ] **Step 5: Stage explicitly**

```bash
git add README.md docs/row-one.md \
  docs/reviews/claude-code-stage-312-code-review-prompt.md \
  docs/reviews/claude-code-stage-312-code-review.md \
  src/fashion_radar/row_one/saved_article_coverage.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_saved_article_coverage.py \
  tests/test_row_one_render.py tests/test_row_one_docs.py
git diff --cached --name-only -- uv.lock reports/row-one/site
git diff --cached --check
```

Expected: no output from the `uv.lock` / generated-site check and no diff check
errors.

- [ ] **Step 6: Commit and push**

```bash
git commit -m "Stage 312: add row one saved article coverage"
git push origin main
```

- [ ] **Step 7: Handoff Summary**

Report repo status, commit SHA, verified commands, uncommitted files, ignored
generated site status, and next recommended stage.
