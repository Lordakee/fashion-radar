# Stage 359 Daily Local Heat Signals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only homepage section that surfaces current-day
heated brands and products when they have saved local article text behind them.

**Architecture:** Reuse existing `app_payload["daily_digest"]["briefing_topics"]`
from `briefing_topics_payload(...)`; do not add a builder, contract field, or
JSON artifact. Add a private homepage renderer in `templates.py` that filters
brand/product topics by positive heat and usable local saved article
availability, then links only through a generated-page href map derived from
`_local_article_page_specs(...)`.

**Tech Stack:** Python 3, existing ROW ONE template/render pipeline, existing
Pydantic models, pytest, ruff.

---

## File Map

- Modify `src/fashion_radar/row_one/templates.py`
  - Render `_render_daily_local_heat_signals(...)` from existing `app_payload`
    plus `local_articles_by_story_id` and a generated local article page href
    map.
  - Add safe topic/card parsing helpers and scoped CSS for
    `.daily-local-heat-signals`.
- Modify `src/fashion_radar/row_one/render.py`
  - Add a pure helper that computes safe local article page hrefs by story ID
    from existing `_local_article_page_specs(...)`.
  - Pass that mapping to `render_index_html(...)`.
- Modify `tests/test_row_one_render.py`
  - Add direct render tests for heat filtering, local article gating, escaping,
    safe local article links, placement, homepage-only site generation, and CSS.
- Modify `tests/test_workflows.py`
  - Add contract payload absence checks, forbidden artifact stems, and a
    generated-site-only wrapper test.
- Modify `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py`
  - Document the Stage 359 generated-site-only boundary.
- Add review artifacts under `docs/reviews/`.

## Task 1: Homepage Heat Signals Rendering Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing direct render test**

Add `test_render_index_html_includes_daily_local_heat_signals` near the Stage
358 homepage tests. Build an `app_payload` with:

```python
app_payload = {
    "daily_digest": {
        "briefing_topics": [
            {
                "topic_type": "brand",
                "title": {"en": "The Row <script>", "zh": "The Row <script>"},
                "label": {"en": "Brand", "zh": "品牌"},
                "story_count": 4,
                "evidence_count": 3,
                "positive_heat_delta_sum": 5,
                "max_heat_delta": 4,
                "story_ids": [
                    "the-row-signal-1234567890",
                    "missing-local-1234567890",
                    "../unsafe",
                ],
                "cards": [
                    {
                        "id": "the-row-signal-1234567890",
                        "headline": "The Row heat <b>",
                        "source_name": "Vogue <Business>",
                        "editorial_takeaway": {
                            "en": "Margaux bag is gaining heat <b>.",
                            "zh": "Margaux 手袋升温 <b>。",
                        },
                    },
                    {
                        "id": "missing-local-1234567890",
                        "headline": "Missing local",
                        "source_name": "Unsafe",
                        "editorial_takeaway": {"en": "No local.", "zh": "无本地正文。"},
                    },
                ],
                "source_refs": [
                    {"name": "The Row", "type": "brand", "label": "brand"}
                ],
            },
            {
                "topic_type": "product",
                "title": {"en": "Margaux bag", "zh": "Margaux 手袋"},
                "label": {"en": "Product", "zh": "单品"},
                "story_count": 1,
                "evidence_count": 2,
                "positive_heat_delta_sum": 8,
                "max_heat_delta": 8,
                "story_ids": ["margaux-bag-signal-1234567890"],
                "cards": [
                    {
                        "id": "margaux-bag-signal-1234567890",
                        "headline": "Margaux bag heat",
                        "source_name": "WWD",
                        "editorial_takeaway": {
                            "en": "The bag signal is moving fastest.",
                            "zh": "手袋信号升温最快。",
                        },
                    }
                ],
                "source_refs": [
                    {"name": "Margaux bag", "type": "bag", "label": "product"}
                ],
            },
            {
                "topic_type": "designer",
                "title": {"en": "Designer signal", "zh": "设计师信号"},
                "label": {"en": "Designer", "zh": "设计师"},
                "story_count": 1,
                "evidence_count": 1,
                "positive_heat_delta_sum": 9,
                "max_heat_delta": 9,
                "story_ids": ["the-row-signal-1234567890"],
                "cards": [],
                "source_refs": [],
            },
            {
                "topic_type": "product",
                "title": {"en": "Ballet flats", "zh": "芭蕾平底鞋"},
                "label": {"en": "Product", "zh": "单品"},
                "story_count": 1,
                "evidence_count": 1,
                "positive_heat_delta_sum": 0,
                "max_heat_delta": 0,
                "story_ids": ["the-row-signal-1234567890"],
                "cards": [],
                "source_refs": [
                    {"name": "Ballet flats", "type": "shoe", "label": "product"}
                ],
            },
        ]
    }
}
```

Call:

```python
html = render_index_html(
    _edition(),
    app_payload=app_payload,
    local_articles_by_story_id={
        "the-row-signal-1234567890": _signal_briefing_local_article(),
        "margaux-bag-signal-1234567890": _signal_briefing_local_article().model_copy(
            update={"story_id": "margaux-bag-signal-1234567890"}
        ),
    },
    daily_local_heat_signals_article_hrefs_by_story_id={
        "the-row-signal-1234567890": "the-row-signal-1234567890.html",
        "margaux-bag-signal-1234567890": "margaux-bag-signal-1234567890.html",
    },
)
```

Assert:
- `class="daily-local-heat-signals"` renders;
- `Daily Local Heat Signals` and `每日本地升温信号` render;
- topic type, topic title, heat/evidence/story/local article metrics render;
- local story row links to
  `href="articles/the-row-signal-1234567890.html#local-article-digest"`;
- the hotter product topic renders before the higher-story-count brand topic;
- bag subtype badge renders from `source_refs`;
- escaped display text appears and raw `<script>`, `<b>`, and `<Business>` do
  not;
- the zero-heat product topic does not render;
- the positive-heat designer topic does not render in this MVP;
- the missing-local card and unsafe story ID do not render;
- no external or traversal href renders.

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_heat_signals \
  -q
```

Expected: fail because the section does not exist.

- [ ] **Step 2: Write failing placement test**

Add `test_render_index_html_places_daily_local_heat_signals_between_sections`.
Use small fixtures for:
- Stage 358 `daily_local_signal_momentum`;
- Stage 359 heat topic app payload;
- `saved_article_content_organization`.

Assert:

```python
assert html.index('class="daily-local-signal-momentum"') < html.index(
    'class="daily-local-heat-signals"'
)
assert html.index('class="daily-local-heat-signals"') < html.index(
    'class="saved-article-content-organization"'
)
```

Run the new test and expect failure because the section is not wired.

## Task 2: Template Implementation and CSS

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`

- [ ] **Step 1: Wire the section into `render_index_html(...)`**

Compute:

```python
daily_local_heat_signals_section = _render_daily_local_heat_signals(
    app_payload,
    local_articles_by_story_id=local_articles_by_story_id,
    article_hrefs_by_story_id=daily_local_heat_signals_article_hrefs_by_story_id,
)
```

Insert it between:

```html
{daily_local_signal_momentum_section}
{saved_article_content_organization_section}
```

- [ ] **Step 2: Add private renderer helpers**

Add helpers near the Stage 358 renderer:

```python
def _render_daily_local_heat_signals(
    app_payload: dict[str, object] | None,
    *,
    local_articles_by_story_id: Mapping[str, RowOneLocalArticle],
    article_hrefs_by_story_id: Mapping[str, str] | None,
) -> str:
    ...
```

Add:
- `_daily_local_heat_signal_topics(...)`
- `_render_daily_local_heat_signal_topic(...)`
- `_render_daily_local_heat_signal_story(...)`
- `_daily_local_heat_signal_story_href(...)`
- `_daily_local_heat_signal_local_story_ids(...)`
- `_daily_local_heat_signal_card_by_id(...)`
- `_daily_local_heat_signal_subtype_labels(...)`
- `_positive_int(...)`

Rules:
- Read topics defensively with raw-dict `.get()` calls:

```python
daily_digest = (app_payload or {}).get("daily_digest", {})
if not isinstance(daily_digest, dict):
    return ""
topics = daily_digest.get("briefing_topics", [])
```

Do not direct-index raw app payload dictionaries.
- Keep only `brand` and `product` topic types for this MVP.
- Keep only dict topics with `positive_heat_delta_sum > 0` or
  `max_heat_delta > 0`.
- Keep only story IDs that are strings, pass `safe_local_article_story_id(...)`,
  exist in `local_articles_by_story_id`, and have
  `_usable_local_article_paragraph_count(article) > 0`.
- Keep only story IDs present in `article_hrefs_by_story_id`, and validate each
  mapping value is a single safe local article page filename before rendering
  `articles/<story-id>.html#local-article-digest`.
- Validate mapping values with the same `PurePosixPath` safety pattern as
  `_safe_daily_local_signal_momentum_page_href(...)`: reject non-strings,
  whitespace, leading `.`, leading `/`, leading `//`, nested paths, non-`.html`
  filenames, and filenames whose stem fails `safe_local_article_story_id(...)`.
  Either extract a shared private helper or copy that exact logic.
- Sort renderable topics by `positive_heat_delta_sum` descending,
  `max_heat_delta` descending, local article count descending, evidence count
  descending, then title.
- Render product subtype badges from `source_refs` when `type` or `label`
  normalizes to `bag`, `bags`, `shoe`, `shoes`, `footwear`, `sneaker`,
  `sneakers`, `boot`, `boots`, `flat`, `flats`, `heel`, `heels`, `sandal`, or
  `sandals`.
- `_positive_int(value)` must return `True` only for
  `isinstance(value, int) and not isinstance(value, bool) and value > 0`; it
  must return `False` for floats, strings, `None`, booleans, and zero.
- Render at most six topics and two local story rows per topic.
- Escape all display values with `_esc(...)`.
- Return an empty string when no topic has renderable local story rows.

- [ ] **Step 3: Add scoped CSS**

Add selectors:
- `.daily-local-heat-signals`
- `.daily-local-heat-signals-header`
- `.daily-local-heat-signals-metrics`
- `.daily-local-heat-signals-grid`
- `.daily-local-heat-signals-topic`
- `.daily-local-heat-signals-topic-header`
- `.daily-local-heat-signals-topic-title`
- `.daily-local-heat-signals-topic-stories`
- `.daily-local-heat-signals-story`
- `.daily-local-heat-signals-story-meta`

Add mobile grid fallback in the existing responsive block.

- [ ] **Step 4: Verify direct render tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_index_html_includes_daily_local_heat_signals \
  tests/test_row_one_render.py::test_render_index_html_places_daily_local_heat_signals_between_sections \
  tests/test_row_one_render.py::test_row_one_css_includes_daily_local_heat_signals_styles \
  -q
```

Expected: pass.

## Task 3: Site Integration

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing site integration test**

Add `test_render_row_one_site_writes_daily_local_heat_signals_homepage_only`
after the Stage 358 homepage-only test. Use `_edition().model_copy(...)` to add:

```python
story = _edition().stories[0].model_copy(
    deep=True,
    update={
        "heat_delta": 5,
        "entity_refs": [RowOneReference(name="The Row", type="brand", label="brand")],
        "product_refs": [RowOneReference(name="Margaux bag", type="bag", label="product")],
    },
)
```

Render with `local_articles_by_story_id={story.id: _signal_briefing_local_article()}`.

Assert:
- `index.html` contains `class="daily-local-heat-signals"`;
- `index.html` contains `Daily Local Heat Signals`;
- `index.html` contains `The Row` and `Margaux bag`;
- story links prefer
  `href="articles/the-row-signal-1234567890.html#local-article-digest"`;
- `articles/index.html`, generated detail pages, and
  `articles/<story-id>.html` pages do not contain `.daily-local-heat-signals`;
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not
  contain `daily_local_heat_signals`, `daily-local-heat-signals`, or
  `Daily Local Heat Signals`;
- no root, `articles/`, or `data/` artifact/route file exists for
  `daily-local-heat-signals`, `daily-local-heat`, or `heat-signals` with
  `.json` or `.html` extensions.

Run the test and expect failure before Task 2 is implemented, or pass after
Task 2 is complete only for direct render. Site generation still fails until
Step 2 passes the generated local article href map into `render_index_html(...)`.

- [ ] **Step 2: Implement actual generated-page href mapping**

Add a pure helper near `_local_article_page_hrefs_by_detail_path(...)`:

```python
def _local_article_page_hrefs_by_story_id(
    local_article_page_specs: Sequence[tuple[RowOneStory, RowOneLocalArticle, str, str]],
) -> dict[str, str]:
    return {
        story.id: article_page_href
        for story, _article, article_page_href, _detail_path in local_article_page_specs
    }
```

In `render_row_one_site(...)`, after `local_article_page_specs` is computed,
compute:

```python
local_article_page_hrefs_by_story_id = _local_article_page_hrefs_by_story_id(
    local_article_page_specs
)
```

Pass it to `render_index_html(...)`:

```python
daily_local_heat_signals_article_hrefs_by_story_id=local_article_page_hrefs_by_story_id,
```

Do not write a new file or JSON payload.

- [ ] **Step 3: Verify site integration passes**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_writes_daily_local_heat_signals_homepage_only \
  -q
```

Expected: pass.

## Task 4: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add docs test**

Add `test_row_one_docs_describe_stage_359_daily_local_heat_signals_boundary`
before Stage 358. Assert the Stage 359 paragraph appears in both docs, appears
before Stage 358, and rejects stale phrases:

- `adds historical trend`
- `historical trend`
- `historical time-series`
- `time-series`
- `creates data/daily-local-heat-signals.json`
- `writes data/daily-local-heat-signals.json`
- `creates data/daily-local-heat.json`
- `writes data/daily-local-heat.json`
- `creates data/heat-signals.json`
- `writes data/heat-signals.json`
- `creates data/daily_local_heat_signals.json`
- `writes data/daily_local_heat_signals.json`
- `creates data/heat_signals.json`
- `writes data/heat_signals.json`
- `row-one-app/v8`
- `row-one-manifest/v2`
- `row-one-runtime/v2`
- `changes schemas`
- `writes a new json artifact`
- `adds source collection`
- `adds fetching`
- `adds matching`
- `adds extraction`
- `adds scoring`
- `adds ranking`
- `adds llm`
- `adds connector`
- `adds scheduling`
- `adds deployment`
- `adds analytics`
- `adds personalization`
- `adds recommendation`
- `adds compliance review`
- `adds heat scoring`
- `adds heat ranking`
- `platform heat`
- `demand proof`

Do not denylist the bare word `heat`, because previous stages and fixtures
legitimately mention heat movers, heat scores, and heat deltas.

- [ ] **Step 2: Update docs**

Insert a Stage 359 paragraph immediately before Stage 358 in `README.md` and
`docs/row-one.md`. It must say:

- generated-site only;
- homepage-only section inside `index.html`;
- after Daily Local Signal Momentum and before Saved Article Content
  Organization;
- reuses existing `daily_digest.briefing_topics` heat fields, `source_refs`,
  saved local article availability, and generated local article page routes;
- focuses this MVP on brands and products, including bag/shoe subtype badges
  from existing source references;
- current-edition positive heat only, not historical trend deltas;
- no app contracts, schemas, JSON artifacts, fetching, scoring, LLM, connector,
  scheduling, deployment, analytics, personalization, recommendation, or
  compliance-review behavior.

- [ ] **Step 3: Update workflow guards**

In `tests/test_workflows.py`, add generated contract payload absence checks for:

- `daily_local_heat_signals`
- `daily_local_heat`
- `daily_heat_signals`
- `local_heat_signals`
- `heat_signals`
- `Daily Local Heat Signals`
- `Daily Local Heat`
- `Daily Heat Signals`
- `Local Heat Signals`
- `daily-local-heat-signals`
- `daily-local-heat`
- `daily-heat-signals`
- `local-heat-signals`
- `heat-signals`

Add forbidden artifact checks under root, `articles/`, and `data/` for `.json`
and `.html` stems:

- `daily-local-heat-signals`
- `daily-local-heat`
- `daily-heat-signals`
- `local-heat-signals`
- `heat-signals`
- `daily_local_heat_signals`
- `daily_local_heat`
- `daily_heat_signals`
- `local_heat_signals`
- `heat_signals`

Add `test_stage_359_daily_local_heat_signals_stays_generated_site_only(...)`
near the stage wrappers. Monkeypatch
`row_one_templates._render_daily_local_heat_signals` to return `""`, then call
the central workflow guard.

- [ ] **Step 4: Verify docs/workflow tests pass**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_359_daily_local_heat_signals_boundary \
  tests/test_workflows.py::test_stage_359_daily_local_heat_signals_stays_generated_site_only \
  -q
```

Expected: pass.

## Task 5: Review, Gates, Commit, Push

**Files:**
- Add: `docs/reviews/claude-code-stage-359-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-359-plan-review.md`
- Add: `docs/reviews/claude-code-stage-359-code-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-359-code-review.md`

- [ ] **Step 1: Request Claude Code plan review before coding**

Ask Claude Code to review the Stage 359 design and plan for scope creep,
duplication with existing Daily Edit, Signal Synthesis, Stage 357 digest, and
Stage 358 momentum; render ordering; local article gating; href safety; and
contract changes.

- [ ] **Step 2: Request code review after implementation**

Ask reviewers to inspect:
- homepage-only scope;
- no JSON/app/schema/runtime/manifest/sidecar changes;
- reuse of existing briefing topic heat fields without mutating app payload;
- topic and story href safety;
- escaping;
- tests/docs/workflow guard coverage.

- [ ] **Step 3: Run full gates**

Run:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
```

- [ ] **Step 4: Commit and push**

Commit message:

```text
Stage 359: add daily local heat signals
```

Push:

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy git -c http.version=HTTP/1.1 push origin main
```
