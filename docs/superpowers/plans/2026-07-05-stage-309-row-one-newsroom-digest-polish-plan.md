# Stage 309 ROW ONE Newsroom Digest Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ROW ONE's saved local-article digest read like organized newsroom intelligence instead of repeated link cards by clustering duplicate story/article cards, improving evidence action copy, and adding compact provenance to local article detail pages.

**Architecture:** Keep the current static-site and sidecar architecture. Add a small deterministic clustering layer inside `fashion_radar.row_one.local_intelligence` before the existing `strongest_reads` and `heat_movers` slices, and keep all rendering changes inside `fashion_radar.row_one.templates`. The generated `data/local-intelligence.json` may contain better aggregate values for existing fields, but `data/edition.json`, `row-one-app/v7`, runtime metadata, manifest metadata, source collection, matching, scoring, story IDs, and schemas do not change.

**Tech Stack:** Python 3.12, existing Pydantic ROW ONE models, pytest, static HTML/CSS template helpers, existing `UV_NO_CONFIG=1 uv --no-config run --frozen ...` verification flow.

---

## Non-Goals

- Do not add compliance-review product features.
- Do not add source collection, browser automation, external API calls, LLM calls, image generation, translation services, or network fetching.
- Do not change ranking, matching, scoring, story IDs, section membership, story detail routes, paragraph anchors, retention policy, scheduling, or local HTTP serving.
- Do not change `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, `data/edition.json`, or JSON schemas.
- Do not remove detail pages or article sidecars for duplicate-looking items; only the homepage digest cards should cluster duplicate intelligence.
- Do not redesign ROW ONE visually. Keep the current visual system and make only targeted markup/CSS additions needed for provenance.

## Files

- Modify: `src/fashion_radar/row_one/local_intelligence.py`
  - Adds deterministic story/article clustering for `strongest_reads` and `heat_movers`.
  - Aggregates existing `RowOneDailyLocalIntelligenceItem` fields across duplicate clusters.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Changes paragraph action copy from mechanical "Open paragraph N" wording to evidence/source wording without changing hrefs.
  - Adds a compact local-article provenance strip in detail pages.
  - Adds small CSS selectors for provenance if needed.
- Modify: `tests/test_row_one_local_intelligence.py`
  - Adds clustering and non-clustering coverage.
- Modify: `tests/test_row_one_render.py`
  - Adds render assertions for clustered digest cards, unchanged sidecars/detail pages, evidence action copy, and provenance output.
- Modify: `README.md`, `docs/row-one.md`
  - Documents newsroom digest polish as presentation/sidecar organization only.
- Modify: `tests/test_row_one_docs.py`
  - Pins the docs language and the no app/schema contract boundary.
- Local generated artifact refresh: `reports/row-one/site/**`
  - Regenerate the ignored local sample site after template/local-intelligence changes so `row-one status` and local preview verification see current output.
  - Do not commit `reports/row-one/site/**`; the upload checklist treats ROW ONE generated site artifacts as local outputs.
- Create/Modify review artifacts:
  - `docs/reviews/claude-code-stage-309-plan-review-prompt.md`
  - `docs/reviews/claude-code-stage-309-plan-review.md`
  - Later after implementation: code-review prompt/result files for Stage 309.

## Task 1: Write Failing Local Intelligence Clustering Tests

**Files:**
- Modify: `tests/test_row_one_local_intelligence.py`

- [ ] **Step 1: Add a helper for duplicate saved articles**

Add a helper near the existing `_article(...)` helper if the exact shape is not already present:

```python
def _article_with_title(
    story_id: str,
    *,
    title: str,
    source_name: str,
    paragraphs: list[str],
) -> RowOneLocalArticle:
    return _article(
        story_id,
        source_name=source_name,
        paragraphs=paragraphs,
    ).model_copy(update={"title": title})
```

Expected reason: clustering should be able to use existing story/article text without creating new model fields.

- [ ] **Step 2: Add a failing duplicate-cluster test**

Add:

```python
def test_build_row_one_local_article_intelligence_clusters_duplicate_story_articles() -> None:
    ref = RowOneReference(name="Coach", type="brand", label="tracked")
    product = RowOneReference(name="Brooklyn Bag", type="bag", label="product")
    stories = [
        _story(
            "coach-a-1234567890",
            "Coach Brooklyn Bag gains heat",
            detail_path="details/coach-a-1234567890.html",
            source_name="Vogue Business",
            heat_delta=4,
            entity_refs=[ref],
            product_refs=[product],
        ),
        _story(
            "coach-b-1234567890",
            "Coach Brooklyn Bag gains heat",
            detail_path="details/coach-b-1234567890.html",
            source_name="Vogue Business",
            heat_delta=9,
            entity_refs=[RowOneReference(name="coach", type="brand", label="candidate")],
            product_refs=[product],
        ),
    ]

    sections = build_row_one_local_article_intelligence(
        _edition(stories),
        {
            "coach-a-1234567890": _article_with_title(
                "coach-a-1234567890",
                title="Coach bag story",
                source_name="Vogue Business",
                paragraphs=["Coach Brooklyn Bag appears in the saved local article body."],
            ),
            "coach-b-1234567890": _article_with_title(
                "coach-b-1234567890",
                title="Coach bag story",
                source_name="Vogue Business",
                paragraphs=["Coach Brooklyn Bag appears in the saved local article body."],
            ),
        },
    )

    strongest = next(section for section in sections if section.key == "strongest_reads")
    heat = next(section for section in sections if section.key == "heat_movers")

    assert [item.title.en for item in strongest.items] == ["Coach Brooklyn Bag gains heat"]
    assert [item.title.en for item in heat.items] == ["Coach Brooklyn Bag gains heat"]
    item = strongest.items[0]
    assert item.story_count == 2
    assert item.article_count == 2
    assert item.source_names == ["Vogue Business"]
    assert item.evidence_count == 2
    assert item.heat_delta == 9
    assert [reference.name for reference in item.references] == ["Coach", "Brooklyn Bag"]
    assert item.detail_path == "details/coach-b-1234567890.html#local-article"
    assert item.paragraph_indices == [0]
    assert item.segments
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_intelligence.py::test_build_row_one_local_article_intelligence_clusters_duplicate_story_articles -q
```

Expected: FAIL because current `strongest_reads` and `heat_movers` return one item per duplicate story/article pair.

- [ ] **Step 3: Add a non-duplicate guard**

Add:

```python
def test_build_row_one_local_article_intelligence_keeps_distinct_saved_articles_separate() -> None:
    stories = [
        _story(
            "row-a-1234567890",
            "The Row market context",
            detail_path="details/row-a-1234567890.html",
            source_name="Vogue Business",
            heat_delta=3,
        ),
        _story(
            "row-b-1234567890",
            "The Row market context",
            detail_path="details/row-b-1234567890.html",
            source_name="Vogue Business",
            heat_delta=2,
        ),
    ]

    sections = build_row_one_local_article_intelligence(
        _edition(stories),
        {
            "row-a-1234567890": _article_with_title(
                "row-a-1234567890",
                title="The Row wholesale",
                source_name="Vogue Business",
                paragraphs=["The Row wholesale expansion is the first saved local signal."],
            ),
            "row-b-1234567890": _article_with_title(
                "row-b-1234567890",
                title="The Row footwear",
                source_name="Vogue Business",
                paragraphs=["The Row footwear demand is a different saved local signal."],
            ),
        },
    )

    strongest = next(section for section in sections if section.key == "strongest_reads")
    assert len(strongest.items) == 2
    assert [item.article_count for item in strongest.items] == [1, 1]
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_intelligence.py::test_build_row_one_local_article_intelligence_keeps_distinct_saved_articles_separate -q
```

Expected: PASS before and after implementation for the separate count, but it protects against over-broad headline-only clustering.

## Task 2: Implement Deterministic Story/Article Clustering

**Files:**
- Modify: `src/fashion_radar/row_one/local_intelligence.py`

- [ ] **Step 1: Add a focused aggregate dataclass**

Add below `_ReferenceAggregate` or near the existing local helper dataclasses:

```python
@dataclass
class _StoryArticleAggregate:
    canonical_story: RowOneStory
    canonical_article: RowOneLocalArticle
    stories: set[str] = field(default_factory=set)
    articles: set[str] = field(default_factory=set)
    evidence_count: int = 0
    heat_delta: int | None = None
    source_names: list[str] = field(default_factory=list)
    references: list[RowOneReference] = field(default_factory=list)
    segments: list[RowOneDailyLocalIntelligenceSegment] = field(default_factory=list)
```

If imports are missing, add `field` beside the existing `dataclass` import.

- [ ] **Step 2: Add normalization helpers**

Add helpers that use only existing local text:

```python
def _story_article_cluster_key(story: RowOneStory, article: RowOneLocalArticle) -> str:
    headline = _normalize_cluster_text(story.headline)
    source = _normalize_cluster_text(article.source_name)
    body = _normalize_cluster_text(_article_primary_cluster_text(article))
    if headline and source and body:
        return f"{headline}|{source}|{body}"
    return f"{headline}|{source}|{_normalize_cluster_text(article.title or '')}|{story.id}"


def _article_primary_cluster_text(article: RowOneLocalArticle) -> str:
    for paragraph in article.paragraphs:
        normalized = paragraph.strip()
        if normalized:
            return normalized
    for section in article.content_sections:
        for item in section.items:
            if item.body is not None and item.body.en.strip():
                return item.body.en.strip()
    return article.title or ""


def _normalize_cluster_text(value: str) -> str:
    return " ".join(value.casefold().split())
```

The fallback includes `story.id` so incomplete articles do not collapse accidentally.

Implementation note from the final review cycle: the shipped key intentionally uses
normalized `source_name` plus the full saved local article body, not `headline` plus
the first non-empty paragraph shown in the early sketch above. That final behavior
clusters duplicate saved bodies even when upstream story headlines differ, and avoids
false clustering when two articles share an opening paragraph but diverge later.

- [ ] **Step 3: Add aggregate construction helpers**

Add:

```python
def _story_article_aggregate(
    story_articles: list[tuple[RowOneStory, RowOneLocalArticle]],
) -> list[_StoryArticleAggregate]:
    aggregates: dict[str, _StoryArticleAggregate] = {}
    for story, article in story_articles:
        key = _story_article_cluster_key(story, article)
        aggregate = aggregates.setdefault(
            key,
            _StoryArticleAggregate(canonical_story=story, canonical_article=article),
        )
        _append_story_article_aggregate(aggregate, story, article)
    return list(aggregates.values())


def _append_story_article_aggregate(
    aggregate: _StoryArticleAggregate,
    story: RowOneStory,
    article: RowOneLocalArticle,
) -> None:
    aggregate.stories.add(story.id)
    aggregate.articles.add(article.story_id)
    aggregate.evidence_count += len(story.evidence)
    aggregate.heat_delta = _max_optional_int(aggregate.heat_delta, story.heat_delta)
    _append_unique(aggregate.source_names, article.source_name)
    for reference in [*story.entity_refs, *story.designer_refs, *story.product_refs]:
        # Reuse the existing normalized reference helper so clusters do not duplicate
        # case/spacing variants of the same reference.
        _append_reference(aggregate.references, reference)
    if story.id == aggregate.canonical_story.id and not aggregate.segments:
        aggregate.segments = _article_segments(article)
```

- [ ] **Step 4: Replace story item creation for clustered sections**

Change `_strongest_reads_section(...)` to sort source pairs first, cluster after sorting, then slice clusters. `_story_sort_key` sorts highest-heat/current priority first, so the highest-delta member becomes the canonical detail route for duplicate clusters:

```python
sorted_articles = sorted(story_articles, key=lambda pair: _story_sort_key(pair[0]))
items = [
    _story_article_aggregate_item(aggregate)
    for aggregate in _story_article_aggregate(sorted_articles)[:MAX_STRONGEST_READS]
]
```

Change `_heat_movers_section(...)` similarly:

```python
heat_articles.sort(key=lambda pair: _story_sort_key(pair[0]))
items = [
    _story_article_aggregate_item(aggregate)
    for aggregate in _story_article_aggregate(heat_articles)[:MAX_HEAT_MOVERS]
]
```

Add:

```python
def _story_article_aggregate_item(
    aggregate: _StoryArticleAggregate,
) -> RowOneDailyLocalIntelligenceItem:
    story = aggregate.canonical_story
    article = aggregate.canonical_article
    takeaway = _article_takeaway(article)
    segments = aggregate.segments or _article_segments(article)
    return RowOneDailyLocalIntelligenceItem(
        title=LocalizedText(zh=story.headline, en=story.headline),
        body=takeaway.text,
        detail_path=_local_article_detail_path(story.detail_path),
        source_name=aggregate.source_names[0] if aggregate.source_names else article.source_name,
        source_names=list(aggregate.source_names),
        story_count=len(aggregate.stories),
        article_count=len(aggregate.articles),
        evidence_count=aggregate.evidence_count,
        heat_delta=aggregate.heat_delta,
        references=list(aggregate.references),
        paragraph_indices=list(takeaway.paragraph_indices),
        segments=list(segments),
    )
```

Keep `_story_article_item(...)` only if existing tests or helpers still need it; otherwise remove it after tests pass.

- [ ] **Step 5: Run focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_intelligence.py -q
```

Expected: PASS.

## Task 3: Write and Implement Render Polish Tests

**Files:**
- Modify: `tests/test_row_one_render.py`
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Add or update daily intelligence action-copy assertions**

In the existing daily local intelligence render tests, assert href behavior stays unchanged and visible copy changes:

```python
assert "Open paragraph 1" not in html
assert "打开段落 1" not in html
assert "Evidence paragraph 1" in html
assert "证据段落 1" in html
assert 'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"' in html
```

Run the specific test:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_daily_local_intelligence -q
```

Expected: FAIL until template copy changes.

- [ ] **Step 2: Change action labels without changing hrefs**

In `_render_daily_local_intelligence_actions(...)`, replace only the label tuple:

```python
links.append((href, f"Evidence paragraph {label}", f"证据段落 {label}"))
```

Run the specific test again. Expected: PASS.

- [ ] **Step 3: Add detail-page provenance assertions**

In `test_render_row_one_detail_includes_local_article_content(...)` or a new focused test, use a local article with `url`, `source_name`, `extracted_at`, `published_at`, `paragraphs`, and `content_sections`. Assert:

```python
assert 'class="local-article-provenance"' in detail_html
assert "Vogue Business" in detail_html
assert 'href="https://example.com/local-article"' in detail_html
assert "Saved paragraphs" in detail_html
assert "保存段落" in detail_html
assert "Organized sections" in detail_html
assert "整理栏目" in detail_html
assert "Jul 02, 2026" in detail_html
```

Add a separate unsafe URL assertion by rendering a local article with `url="javascript:alert(1)"`:

```python
assert "javascript:alert" not in detail_html
assert "Original URL" not in detail_html
assert 'class="local-article-provenance-link"' not in detail_html
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "local_article and provenance" -q
```

Expected: FAIL until provenance markup exists.

- [ ] **Step 4: Add provenance renderer helpers**

In `templates.py`, add helper functions near `_render_local_article(...)`:

```python
def _render_local_article_provenance(article: RowOneLocalArticle) -> str:
    items = [
        _local_article_provenance_item(
            "Source",
            "来源",
            _esc(article.source_name),
        ),
        _local_article_provenance_item(
            "Saved",
            "保存时间",
            _esc(_format_datetime(article.extracted_at)),
        ),
    ]
    if article.published_at is not None:
        items.append(
            _local_article_provenance_item(
                "Published",
                "发布时间",
                _esc(_format_datetime(article.published_at)),
            )
        )
    items.append(
        _local_article_provenance_item(
            "Saved paragraphs",
            "保存段落",
            str(len(article.paragraphs)),
        )
    )
    items.append(
        _local_article_provenance_item(
            "Organized sections",
            "整理栏目",
            str(len(article.content_sections)),
        )
    )
    url = _safe_external_url(article.url)
    if url is not None:
        items.append(
            '<a class="local-article-provenance-item local-article-provenance-link" '
            f'href="{_esc(url)}" target="_blank" rel="noopener">'
            '<span data-lang="en">Original URL</span>'
            '<span data-lang="zh">原文链接</span>'
            "</a>"
        )
    return f'<div class="local-article-provenance">{"".join(items)}</div>'


def _local_article_provenance_item(label_en: str, label_zh: str, value: str) -> str:
    return (
        '<span class="local-article-provenance-item">'
        f'<span class="local-article-provenance-label" data-lang="en">{_esc(label_en)}</span>'
        f'<span class="local-article-provenance-label" data-lang="zh">{_esc(label_zh)}</span>'
        f'<span class="local-article-provenance-value">{value}</span>'
        "</span>"
    )


def _format_datetime(dt: datetime) -> str:
    return dt.strftime("%b %d, %Y")
```

Use the existing `_safe_external_url(...)` helper already present in `templates.py`; do not add a duplicate safe URL helper.

- [ ] **Step 5: Insert provenance into `_render_local_article(...)`**

Change:

```python
brief = _render_local_article_brief(article)
```

to:

```python
provenance = _render_local_article_provenance(article)
brief = _render_local_article_brief(article)
```

Then include `{provenance}` after the source paragraph and before the article title:

```python
      <p class="local-article-source">
        <span data-lang="en">Saved from {_esc(article.source_name)}</span>
        <span data-lang="zh">本地保存自 {_esc(article.source_name)}</span>
      </p>
{provenance}
      <h3>{_esc(title)}</h3>
```

- [ ] **Step 6: Add minimal CSS**

Add selectors to `row_one_css()` near local article styles:

```css
.local-article-provenance {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0 1.2rem;
}

.local-article-provenance-item {
  border: 1px solid rgba(31, 31, 29, 0.16);
  border-radius: 999px;
  color: var(--muted);
  display: inline-flex;
  gap: 0.35rem;
  padding: 0.35rem 0.65rem;
}
```

Use existing variables/palette names; do not introduce a new design theme.

- [ ] **Step 7: Run render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q
```

Expected: PASS.

## Task 4: Add Render Coverage for Duplicate Digest Cards and Sidecar Stability

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add an integration render test**

Add a focused test that renders two duplicate-looking stories with two saved local articles. In `tests/test_row_one_render.py`, use the no-argument `_edition()` helper already defined in that file:

```python
def test_render_row_one_site_clusters_duplicate_daily_local_intelligence_cards(tmp_path) -> None:
    edition = _edition()
    story_a = edition.stories[0]
    story_a.id = "coach-a-1234567890"
    story_a.headline = "Coach Brooklyn Bag gains heat"
    story_a.detail_path = "details/coach-a-1234567890.html"
    story_a.heat_delta = 6
    story_b = story_a.model_copy(
        deep=True,
        update={
            "id": "coach-b-1234567890",
            "detail_path": "details/coach-b-1234567890.html",
            "heat_delta": 9,
        },
    )
    edition.stories = [story_a, story_b]

    article_a = _local_article_for_daily_intelligence().model_copy(
        deep=True,
        update={
            "story_id": story_a.id,
            "url": "https://example.com/coach-a",
            "paragraphs": ["Coach Brooklyn Bag appears in the saved local article body."],
        },
    )
    article_b = article_a.model_copy(
        deep=True,
        update={
            "story_id": story_b.id,
            "url": "https://example.com/coach-b",
        },
    )

    render_row_one_site(
        edition,
        tmp_path,
        local_articles_by_story_id={story_a.id: article_a, story_b.id: article_b},
    )

    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    local_intelligence = json.loads(
        (tmp_path / "data" / "local-intelligence.json").read_text(encoding="utf-8")
    )
    strongest = next(section for section in local_intelligence if section["key"] == "strongest_reads")
    heat = next(section for section in local_intelligence if section["key"] == "heat_movers")

    assert len(strongest["items"]) == 1
    assert len(heat["items"]) == 1
    assert strongest["items"][0]["story_count"] == 2
    assert strongest["items"][0]["article_count"] == 2
    assert (tmp_path / "details" / "coach-a-1234567890.html").exists()
    assert (tmp_path / "details" / "coach-b-1234567890.html").exists()
    assert (tmp_path / "data" / "articles" / "coach-a-1234567890.json").exists()
    assert (tmp_path / "data" / "articles" / "coach-b-1234567890.json").exists()
    assert "local_article_intelligence" not in json.loads(
        (tmp_path / "data" / "edition.json").read_text(encoding="utf-8")
    )
    assert html.count("Coach Brooklyn Bag gains heat") >= 1
```

The important contract is one digest item per duplicate cluster while detail pages and sidecars remain per story.

- [ ] **Step 2: Run focused integration test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_clusters_duplicate_daily_local_intelligence_cards -q
```

Expected: PASS after Task 2 implementation.

## Task 5: Update Docs and Docs Drift Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add docs-drift assertions**

Extend or add a docs test:

```python
def test_row_one_docs_describe_newsroom_digest_polish_boundary() -> None:
    row_one = _normalized(_read(ROW_ONE_DOC))
    readme = _normalized(_read(README))

    for phrase in (
        "newsroom digest polish",
        "clusters duplicate saved local-article cards",
        "`data/local-intelligence.json`",
        "`strongest_reads`",
        "`heat_movers`",
        "evidence paragraph links",
        "local article provenance",
        "presentation and sidecar organization only",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
        "does not change `row-one-manifest/v1`",
        "does not change `row-one-runtime/v1`",
        "does not add source collection",
        "does not add scoring",
    ):
        assert phrase in row_one

    for phrase in (
        "newsroom digest polish",
        "local article provenance",
        "does not change `row-one-app/v7`",
        "does not change `data/edition.json`",
    ):
        assert phrase in readme

    for forbidden in (
        "row-one-app/v8",
        "adds local_intelligence to `data/edition.json`",
        "changes story ids",
        "changes detail routes",
        "changes paragraph anchors",
        "row-one status rebuilds",
        "row-one status collects",
        "row-one status fetches",
    ):
        assert forbidden not in row_one
```

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_newsroom_digest_polish_boundary -q
```

Expected: FAIL until docs are updated.

- [ ] **Step 2: Update `docs/row-one.md`**

Add concise language to the existing Daily Local Intelligence or Generated Files section:

```markdown
Stage 309 adds newsroom digest polish: ROW ONE clusters duplicate saved local-article cards in `data/local-intelligence.json` for the homepage `strongest_reads` and `heat_movers` digest sections, evidence paragraph links use reader-facing copy, and detail pages show compact local article provenance from existing source/extraction/published/count fields. This is presentation and sidecar organization only; it does not change `row-one-app/v7`, `data/edition.json`, `row-one-manifest/v1`, `row-one-runtime/v1`, collection, matching, scoring, story IDs, detail routes, paragraph anchors, or schemas. It does not add source collection and does not add scoring.
```

- [ ] **Step 3: Update `README.md`**

Add the same short boundary note near the ROW ONE usage section:

```markdown
ROW ONE also applies newsroom digest polish to saved local articles: it clusters duplicate saved local-article cards in the homepage digest, evidence paragraph links point into saved local paragraphs with reader-facing copy, and detail pages show compact local article provenance. This does not change `row-one-app/v7`, `data/edition.json`, or add source collection/scoring.
```

- [ ] **Step 4: Run docs test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
```

Expected: PASS.

## Task 6: Regenerate Site and Full Verification

**Files:**
- Write ignored local verification files under `reports/row-one/site/**`; do not stage or commit them.

- [ ] **Step 1: Regenerate ROW ONE sample site**

Run the existing documented refresh command. This writes ignored local verification artifacts under `reports/row-one/site` and applies latest-only cleanup as part of refresh.

Command:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one refresh --output-dir reports/row-one/site
```

If that documented option shape is not accepted, stop and inspect `fashion-radar row-one refresh --help` before choosing an equivalent.

- [ ] **Step 2: Run focused status check**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Expected: PASS and JSON output says the generated site is valid.

- [ ] **Step 3: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv lock --check
```

Expected: all pass. If any command fails, fix the smallest relevant issue and rerun the failing command, then rerun full verification before code review.

## Task 7: Claude Code Review, Fixes, Commit, Push

**Files:**
- Create/Modify: `docs/reviews/claude-code-stage-309-code-review-prompt.md`
- Create/Modify: `docs/reviews/claude-code-stage-309-code-review.md`
- Create/Modify if needed: `docs/reviews/claude-code-stage-309-code-rereview-prompt.md`
- Create/Modify if needed: `docs/reviews/claude-code-stage-309-code-rereview.md`

- [ ] **Step 1: Write code review prompt**

Prompt must include:

```markdown
Review Stage 309 for /home/ubuntu/fashion-radar.

Scope:
- `strongest_reads` and `heat_movers` cluster duplicate saved local-article cards.
- Paragraph action copy is reader-facing while hrefs/anchors stay unchanged.
- Detail pages show compact local article provenance and omit unsafe original URLs.
- `data/edition.json`, `row-one-app/v7`, source collection, scoring, matching, story IDs, schemas, scheduling, and runtime contracts are unchanged.

Review for correctness, escaping/safe URLs, over-broad clustering, app/schema drift, docs drift, generated-site consistency, and missing tests.
Return Critical/Important/Minor findings. Do not modify files.
```

- [ ] **Step 2: Run Claude Code review**

Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-309-code-review-prompt.md)" \
  > docs/reviews/claude-code-stage-309-code-review.md
```

- [ ] **Step 3: Fix Critical/Important findings**

If Claude Code reports Critical or Important findings, fix them, rerun focused/full verification as needed, and run a rereview prompt. Minor findings may be documented if they are out of scope.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short --branch
git add src/fashion_radar/row_one/local_intelligence.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py README.md docs/row-one.md docs/superpowers/plans/2026-07-05-stage-309-row-one-newsroom-digest-polish-plan.md docs/reviews/claude-code-stage-309-plan-review-prompt.md docs/reviews/claude-code-stage-309-plan-review.md docs/reviews/claude-code-stage-309-plan-rereview-prompt.md docs/reviews/claude-code-stage-309-plan-rereview.md docs/reviews/claude-code-stage-309-plan-final-review-prompt.md docs/reviews/claude-code-stage-309-plan-final-review.md docs/reviews/claude-code-stage-309-code-review-prompt.md docs/reviews/claude-code-stage-309-code-review.md
git commit -m "Stage 309: polish row one newsroom digest"
git push origin main
```

If rereview files exist, add them too. Do not commit unrelated local files.

## Self-Review

- Spec coverage: The plan covers duplicate digest clustering, evidence action copy, local article provenance, docs, generated site refresh, review, commit, and push.
- Placeholder scan: No TODO/TBD placeholders remain; exact commands and expected results are listed.
- Type consistency: The plan uses existing `RowOneDailyLocalIntelligenceItem`, `RowOneDailyLocalIntelligenceSegment`, `RowOneLocalArticle`, and `RowOneStory` fields only.
- Boundary check: The plan does not alter `row-one-app/v7`, schemas, source collection, scoring, matching, story IDs, scheduling, or compliance-review product behavior.
