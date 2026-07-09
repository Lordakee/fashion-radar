# Stage 373 Local Article Body Section Markers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. REQUIRED PROJECT GATE: submit this plan for Claude Code review with `--effort max` before implementation; after Claude Code's plan review, run local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar`.

**Goal:** Add generated-site-only Local Article Body Section Markers inside `articles/<story-id>.html` saved article bodies so downloaded/local ROW ONE article text is organized in the body itself, not only through pre-body summaries or outbound links.

**Architecture:** Add a focused pure builder module that derives paragraph insertion markers from an existing `RowOneStory` and matching `RowOneLocalArticle.content_sections`. Render those markers inside the existing local article body paragraph loop, immediately before the first valid saved paragraph filed under each content section, while keeping paragraph IDs/order unchanged and keeping all output same-page and generated-site-only.

**Tech Stack:** Python 3, existing ROW ONE Pydantic models, dataclasses, static HTML string templates in `templates.py`, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config`.

---

## File Structure

- Create `src/fashion_radar/row_one/local_article_body_section_markers.py`
  - Owns marker dataclass, caps, strict paragraph-index validation, support excerpt fallback, label/reference dedupe, insertion-point selection, and deterministic ordering.
- Create `tests/test_row_one_local_article_body_section_markers.py`
  - Builder tests only.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import the marker builder/dataclass.
  - Build markers in `render_local_article_page_html(...)`, where `story` and `local_article` are both in scope.
  - Pass prebuilt markers through `_render_local_article(...)` into `_render_local_article_paragraphs(...)`.
  - Insert marker HTML in `_render_local_article_paragraphs(...)` before target paragraphs when `include_body_filing_cues=True`.
  - Add render helpers and scoped CSS.
- Modify `tests/test_row_one_render.py`
  - Add article-page render tests, page-scope integration tests, contract/artifact leakage tests, and CSS selector tests.
- Modify `README.md` and `docs/row-one.md`
  - Add exact Stage 373 generated-site-only boundary paragraph before Stage 372.
- Modify `tests/test_row_one_docs.py`
  - Add exact Stage 373 paragraph and stale phrase guard.
- Modify `tests/test_workflows.py`
  - Add Stage 373 app-contract denylist, artifact denylist, and generated-site-only wrapper guard.
- Add review artifacts:
  - `docs/reviews/claude-code-stage-373-plan-review.md`
  - `docs/reviews/opencode-stage-373-plan-review.md`
  - `docs/reviews/claude-code-stage-373-code-review.md`
  - `docs/reviews/opencode-stage-373-code-review.md`

## Core Product Gap Closed

Previous stages added homepage and article-page organizers before the saved body. Stage 373 closes the local reading gap inside the saved body: it makes the downloaded/local article paragraphs self-organizing by marking where an existing content section begins in the actual reading flow.

## Parallel Execution Shape After Plan Review

Use parallel agents only with disjoint write scopes:

- Worker A: `src/fashion_radar/row_one/local_article_body_section_markers.py` and `tests/test_row_one_local_article_body_section_markers.py`.
- Worker B: `src/fashion_radar/row_one/templates.py` and Stage 373 slices of `tests/test_row_one_render.py`.
- Worker C: `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`, `tests/test_workflows.py`.

Workers must not revert other edits and must reconcile around the existing dirty worktree if another worker finishes first. Worker B owns the template call-chain signature change from `render_local_article_page_html(...)` to `_render_local_article(...)` to `_render_local_article_paragraphs(...)`; Worker A must not edit `templates.py`.

## Plan Review Fixes Incorporated

- Build body section markers in `render_local_article_page_html(...)`, where `story` is already available, then pass them into `_render_local_article(...)` and `_render_local_article_paragraphs(...)` as keyword-only internal arguments.
- Reuse the existing `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` and `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` patterns for render-time href validation.
- Keep strict paragraph-index validation local to the new builder for Stage 373 to avoid a broader refactor; add an alignment comment and tests that lock the same bool/non-int/negative/overflow/duplicate/blank-paragraph semantics used by existing local article filing/body organizer helpers.
- Use fallback title `Section N` / `第 N 节`.
- Suppress the existing Stage 366 inline body filing cue on paragraphs that carry a Stage 373 body section marker, preventing adjacent duplicate section labels and content-section links.
- Use the first non-empty item body as support before falling back to the cited paragraph excerpt.
- Define test helper signatures explicitly so matched, mismatched, and unsafe story-id cases are deterministic.
- Monkeypatch `fashion_radar.row_one.templates.build_row_one_local_article_body_section_markers` for the workflow guard, because `templates.py` imports the builder directly.

---

### Task 1: Plan Review Gate

**Files:**
- Create: `docs/reviews/claude-code-stage-373-plan-review.md`
- Create: `docs/reviews/opencode-stage-373-plan-review.md`

- [ ] **Step 1: Request Claude Code plan review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 373 Local Article Body Section Markers plan/spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-09-stage-373-local-article-body-section-markers-design.md and docs/superpowers/plans/2026-07-09-stage-373-local-article-body-section-markers-plan.md. Goal: organize downloaded/local ROW ONE article body text inside articles/<story-id>.html by inserting generated-site-only section-start markers before saved paragraphs. Technical stack: Python dataclasses, existing ROW ONE Pydantic models, templates.py static HTML renderer, pytest, ruff, uv. Implementation method: pure builder from current RowOneStory plus matching RowOneLocalArticle.content_sections, strict paragraph-index validation, render markers inside _render_local_article_paragraphs with same-page fragment hrefs only. Check feasibility, duplication with Stages 365-372, href safety, generated-site-only boundaries, app-contract/artifact leakage risk, and test plan. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-373-plan-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 2: Request opencode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 373 Local Article Body Section Markers plan/spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-09-stage-373-local-article-body-section-markers-design.md and docs/superpowers/plans/2026-07-09-stage-373-local-article-body-section-markers-plan.md. Goal: organize downloaded/local ROW ONE article body text inside articles/<story-id>.html by inserting generated-site-only section-start markers before saved paragraphs. Technical stack: Python dataclasses, existing ROW ONE Pydantic models, templates.py static HTML renderer, pytest, ruff, uv. Implementation method: pure builder from current RowOneStory plus matching RowOneLocalArticle.content_sections, strict paragraph-index validation, render markers inside _render_local_article_paragraphs with same-page fragment hrefs only. Cross-check Claude Code review if present at docs/reviews/claude-code-stage-373-plan-review.md. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-373-plan-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 3: Fix valid Critical and Important plan findings**

If either review raises Critical or Important issues, update the spec/plan before implementation and run the appropriate re-review. Do not edit production code until this gate passes.

### Task 2: Builder RED Tests

**Files:**
- Create: `tests/test_row_one_local_article_body_section_markers.py`

- [ ] **Step 1: Write failing builder tests**

Create tests with helpers `_lt`, `_ref`, `_story`, `_item`, `_section`, and `_article` using existing ROW ONE models. Use these helper signatures so matched, mismatched, and unsafe story-id cases are explicit:

```python
def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)


def _story(story_id: str = "the-row-signal-1234567890") -> RowOneStory:
    return RowOneStory(
        id=story_id,
        headline="The Row signal",
        summary="The Row summary",
        source_name="Vogue Business",
        source_url="https://example.com/the-row",
        image_url="https://example.com/the-row.jpg",
        published_at="2026-07-09T04:00:00Z",
        category="Brands",
        topic="The Row",
        region="global",
        sentiment="neutral",
        impact_score=0.7,
        novelty_score=0.5,
        relevance_score=0.8,
        heat_score=0.6,
        detail_path="details/the-row-signal-1234567890.html",
    )


def _article(
    story_id: str = "the-row-signal-1234567890",
    *,
    paragraphs: list[str] | None = None,
    paragraphs_zh: list[str] | None = None,
    content_sections: list[RowOneLocalArticleContentSection] | None = None,
) -> RowOneLocalArticle:
    return RowOneLocalArticle(
        story_id=story_id,
        source_name="Vogue Business",
        source_url="https://example.com/the-row",
        title="The Row local article",
        body_source="extracted",
        paragraphs=paragraphs
        if paragraphs is not None
        else [
            "The Row frames the season through restraint and proportion.",
            "The Margaux bag remains the commercial signal.",
        ],
        paragraphs_zh=paragraphs_zh or [],
        brief_sections=[],
        content_sections=content_sections or [],
    )
```

Required test names:

- `test_build_local_article_body_section_markers_marks_section_starts`
- `test_build_local_article_body_section_markers_filters_invalid_indices`
- `test_build_local_article_body_section_markers_dedupes_duplicate_paragraph_markers`
- `test_build_local_article_body_section_markers_uses_support_fallbacks`
- `test_build_local_article_body_section_markers_caps_labels_references_and_markers`
- `test_build_local_article_body_section_markers_returns_empty_without_markable_sections`

The first test must assert:

```python
markers = build_row_one_local_article_body_section_markers(
    story=_story(),
    local_article=_article(
        content_sections=[
            _section(
                "brand",
                title=_lt("Brand signal", "品牌信号"),
                body=_lt("The Row section context.", "The Row 分节上下文。"),
                items=[
                    _item(
                        "The Row",
                        body="Mary-Kate and Ashley Olsen's label frames the story.",
                        references=[_ref("The Row", "brand", "brand")],
                        paragraph_indices=[0, 1],
                    )
                ],
            )
        ],
    ),
)

assert len(markers) == 1
assert markers[0].paragraph_index == 0
assert markers[0].paragraph_href == "#local-article-paragraph-1"
assert markers[0].section_position == 1
assert markers[0].section_href == "#local-article-content-section-1"
assert markers[0].title.en == "Brand signal"
assert markers[0].support.en == "The Row section context."
assert [label.en for label in markers[0].item_labels] == ["The Row"]
assert [ref.name for ref in markers[0].references] == ["The Row"]
```

The invalid-index test must use `paragraph_indices=[True, "0", -1, 0, 1, 1, 99]` with paragraph zero blank and paragraph one nonblank. It must assert only `paragraph_index == 1` is used and `#local-article-paragraph-2` is emitted.

The duplicate-marker test must create two sections whose first valid paragraph is the same. It must assert only one marker is emitted for that paragraph and the first section in content-section order wins.

The fallback test must assert support falls back from section body to the first non-empty item body to saved paragraph, including safe Chinese fallback when `paragraphs_zh` is missing or misaligned.

The caps test must import:

```python
LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS
LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_LABELS
LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_REFERENCES
LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS
```

It must prove marker count, label count, reference count, and excerpt length caps hold deterministically.

The empty test must assert an empty tuple for mismatched story/local article ids, unsafe story ids, all-blank paragraphs, and sections with no valid indices.

- [ ] **Step 2: Run builder tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_body_section_markers.py -q
```

Expected: fail with `ModuleNotFoundError: No module named 'fashion_radar.row_one.local_article_body_section_markers'`.

### Task 3: Builder Implementation

**Files:**
- Create: `src/fashion_radar/row_one/local_article_body_section_markers.py`
- Test: `tests/test_row_one_local_article_body_section_markers.py`

- [ ] **Step 1: Implement constants and dataclass**

Create:

```python
LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS = 8
LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_LABELS = 3
LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_REFERENCES = 4
LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS = 150
```

Create:

```python
@dataclass(frozen=True)
class RowOneLocalArticleBodySectionMarker:
    paragraph_index: int
    paragraph_href: str
    section_position: int
    section_href: str
    title: LocalizedText
    support: LocalizedText
    item_labels: tuple[LocalizedText, ...]
    references: tuple[RowOneReference, ...]
```

- [ ] **Step 2: Implement builder behavior**

Implement:

```python
def build_row_one_local_article_body_section_markers(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> tuple[RowOneLocalArticleBodySectionMarker, ...]:
```

Rules:

- return `()` unless `story.id == local_article.story_id`
- return `()` unless `safe_local_article_story_id(story.id)` passes
- iterate `local_article.content_sections` in source order
- validate paragraph indices by rejecting bool, non-int, negative, overflow, duplicate, and blank paragraph values
- choose each section's first valid paragraph index as insertion point
- allow only one marker per paragraph index
- build `paragraph_href` as `#local-article-paragraph-{paragraph_index + 1}`
- build `section_href` as `#local-article-content-section-{section_position}`
- fallback title to `LocalizedText(en=f"Section {section_position}", zh=f"第 {section_position} 节")`
- support fallback order is section body, first non-empty item body, then paragraph excerpt
- paragraph support uses aligned `paragraphs_zh` only when `len(paragraphs_zh) == len(paragraphs)`
- dedupe labels by normalized English/Chinese text and cap
- dedupe references by `(name, type, label)` casefolded and cap
- truncate support excerpts to `LOCAL_ARTICLE_BODY_SECTION_MARKERS_EXCERPT_CHARS`
- sort returned markers by `(paragraph_index, section_position)`
- cap total markers to `LOCAL_ARTICLE_BODY_SECTION_MARKERS_MAX_MARKERS`
- include this comment above the local strict index helper:

```python
# Keep these semantics aligned with the existing local-article body filing and
# body-organizer helpers: bools/non-ints, negative values, overflow values,
# duplicate values, and blank paragraphs are not valid marker insertion points.
```

- [ ] **Step 3: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_body_section_markers.py -q
```

Expected: all builder tests pass.

### Task 4: Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add failing render tests**

Add tests named:

- `test_render_local_article_page_includes_body_section_markers_inside_body`
- `test_render_local_article_body_section_markers_escape_text_and_filter_links`
- `test_render_row_one_site_writes_body_section_markers_only_on_local_article_pages`
- `test_render_row_one_site_body_section_markers_do_not_leak_contracts_or_artifacts`
- `test_row_one_css_includes_local_article_body_section_marker_rules`

The inclusion test must assert:

- `class="local-article-body-section-marker"` appears inside `id="local-article-body"`
- marker appears before `id="local-article-paragraph-1"`
- paragraph IDs remain present and ordered
- the target paragraph does not include `class="local-article-body-filing-cue"` when a marker is rendered for that paragraph
- `Section starts here` and `本节从这里开始` render
- `href="#local-article-content-section-1"` renders
- `href="#local-article-paragraph-1"` renders
- the page still includes `id="local-article-content-section-1"` before `id="local-article-body"` so the marker's section link resolves on the same page
- marker appears after pre-body `class="local-article-intelligence-brief"` and before the target paragraph

The escaping/filtering test must use a monkeypatched marker builder returning a marker with `<script>` text and unsafe hrefs. It must assert raw script tags and unsafe hrefs do not render while escaped text does.

The page-scope test must render the full site and assert:

- `articles/<story-id>.html` includes `class="local-article-body-section-marker"`
- `index.html`, `articles/index.html`, and `details/<story-id>.html` do not include that class

The contract/artifact test must assert:

- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not contain `local-article-body-section-marker`, `Local Article Body Section Markers`, or `local_article_body_section_markers`
- no forbidden Stage 373 JSON/HTML artifact stems exist under root, `articles`, or `data`

The CSS test must assert selectors exist for:

- `.local-article-body-section-marker`
- `.local-article-body-section-marker-header`
- `.local-article-body-section-marker-title`
- `.local-article-body-section-marker-support`
- `.local-article-body-section-marker-chips`
- `.local-article-body-section-marker-ref`
- `.local-article-body-section-marker-actions`
- mobile `@media` rules covering the marker layout

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "body_section_marker or local_article_body_section_marker"
```

Expected: fail because marker rendering and CSS do not exist yet.

### Task 5: Render Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Test: `tests/test_row_one_render.py`

- [ ] **Step 1: Import builder and dataclass**

Import from `fashion_radar.row_one.local_article_body_section_markers`:

```python
RowOneLocalArticleBodySectionMarker
build_row_one_local_article_body_section_markers
```

- [ ] **Step 2: Add marker rendering helpers**

Add helpers near existing local article body filing helpers:

- `_render_local_article_body_section_marker(marker)`
- `_render_local_article_body_section_marker_ref(ref)`
- `_safe_local_article_body_section_marker_href(href)`

`_safe_local_article_body_section_marker_href` must accept only `#local-article-content-section-N` and `#local-article-paragraph-N` with `N >= 1`, and must reuse `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` and `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE`.

- [ ] **Step 3: Prebuild markers at the article page level**

Update `render_local_article_page_html(...)`:

- call `build_row_one_local_article_body_section_markers(story=story, local_article=local_article)` only when `local_article` is present
- pass the resulting tuple into `_render_local_article(local_article, include_body_filing_cues=True, body_section_markers=body_section_markers)`
- do not call the builder inside `_render_local_article_paragraphs(...)`, because `story` is not in that function's scope

- [ ] **Step 4: Insert markers in paragraph loop**

Update `_render_local_article_paragraphs(...)`:

- accept `body_section_markers: tuple[RowOneLocalArticleBodySectionMarker, ...] = ()`
- use markers only when `include_body_filing_cues=True`
- group markers by original `paragraph_index`
- before rendering a paragraph, append marker HTML for that index
- suppress `_render_local_article_body_filing_cue(...)` for any paragraph index that has a marker, because the block marker replaces the adjacent inline cue for that section-opening paragraph
- keep existing paragraph HTML and IDs unchanged
- preserve both paths: aligned `paragraphs_zh` and non-aligned single-language rendering

- [ ] **Step 5: Add scoped CSS**

Add CSS selectors for the marker and mobile layout to the existing CSS string in `templates.py`.

- [ ] **Step 6: Run render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "body_section_marker or local_article_body_section_marker"
```

Expected: Stage 373 render tests pass.

### Task 6: Docs And Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add docs tests**

Add `test_row_one_docs_describe_stage_373_local_article_body_section_markers_boundary()` to `tests/test_row_one_docs.py`.

Use the exact boundary paragraph from the Stage 373 design doc. Assert it appears in `README.md` and `docs/row-one.md`, appears before Stage 372, and that the Stage 373 slice does not contain stale phrases such as:

- `creates data/local-article-body-section-markers.json`
- `writes data/local-article-body-section-markers.json`
- `does create data/local-article-body-section-markers.json`
- `alters index.html`
- `alters articles/index.html`
- `alters detail pages`
- `adds outbound article urls as primary navigation`
- `changes row-one-app/v7`

- [ ] **Step 2: Add workflow guards**

Update Stage 373 denylist tuples in `tests/test_workflows.py` with:

- `local_article_body_section_markers`
- `local-article-body-section-markers`
- `Local Article Body Section Markers`
- `body_section_markers`
- `body-section-markers`
- `article_body_section_markers`
- `article-body-section-markers`

Update forbidden artifact stems with:

- `data/local-article-body-section-markers.json`
- `data/article-body-section-markers.json`
- `data/body-section-markers.json`
- `local-article-body-section-markers.html`
- `article-body-section-markers.html`
- `body-section-markers.html`

Add a wrapper guard named `test_stage_373_local_article_body_section_markers_stays_generated_site_only`. It should monkeypatch `fashion_radar.row_one.templates.build_row_one_local_article_body_section_markers` to return `()`, run the existing ROW ONE workflow fixture, and assert generated contracts and required pages still exist.

- [ ] **Step 3: Add documentation paragraph**

Insert the exact Stage 373 boundary paragraph into `README.md` and `docs/row-one.md` before the Stage 372 paragraph.

- [ ] **Step 4: Run docs/workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_373 or body_section_marker or local_article_body_section_marker"
```

Expected: Stage 373 docs/workflow tests pass.

### Task 7: Code Reviews, Full Gates, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-373-code-review.md`
- Create: `docs/reviews/opencode-stage-373-code-review.md`

- [ ] **Step 1: Run focused checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_body_section_markers.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "body_section_marker or local_article_body_section_marker or stage_373"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/local_article_body_section_markers.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_article_body_section_markers.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/local_article_body_section_markers.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_article_body_section_markers.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
```

Expected: all focused checks pass.

- [ ] **Step 2: Request Claude Code code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 373 Local Article Body Section Markers implementation in /home/ubuntu/fashion-radar. Focus on correctness, generated-site-only boundary, href safety, body paragraph ordering, escaping, tests, docs, workflow guards, and whether Critical or Important issues remain. Return findings only, ordered by severity." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-373-code-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 3: Request opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 373 Local Article Body Section Markers implementation in /home/ubuntu/fashion-radar. Focus on correctness, generated-site-only boundary, href safety, body paragraph ordering, escaping, tests, docs, workflow guards, and whether Critical or Important issues remain. Cross-check Claude Code review if present at docs/reviews/claude-code-stage-373-code-review.md. Return findings only, ordered by severity." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-373-code-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 4: Fix valid Critical and Important code findings**

If review findings are valid, patch them, rerun focused checks, and request re-review as needed.

- [ ] **Step 5: Run full gates**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config lock --check --offline
git diff --check
git diff --cached --check
```

Expected: all full gates pass.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add src/fashion_radar/row_one/local_article_body_section_markers.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_article_body_section_markers.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py README.md docs/row-one.md docs/superpowers/specs/2026-07-09-stage-373-local-article-body-section-markers-design.md docs/superpowers/plans/2026-07-09-stage-373-local-article-body-section-markers-plan.md docs/reviews/claude-code-stage-373-plan-review.md docs/reviews/opencode-stage-373-plan-review.md docs/reviews/claude-code-stage-373-code-review.md docs/reviews/opencode-stage-373-code-review.md
git commit -m "Stage 373: add local article body section markers"
git push origin main
```

If direct `git push` cannot reach GitHub but `api.github.com` is reachable, use the existing GitHub API fallback pattern from Stage 372 and then update local `origin/main` to the pushed commit.

## Final Handoff Summary Requirements

At node end, report:

- repo status and commit SHA
- whether push succeeded and by which route
- verified commands
- uncommitted files
- next recommended stage
- any review findings fixed or intentionally deferred
