# Stage 382 Local Article Synthesis Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Local Article Synthesis Brief to each saved local article page so ROW ONE gives readers a compact “so what” interpretation of the locally saved article, not only links, section maps, and evidence chips.

**Architecture:** Add a focused deterministic builder that derives a short narrative synthesis from existing `RowOneStory` and `RowOneLocalArticle` fields, then render it inside `articles/<story-id>.html` after the existing Local Article Intelligence Brief and before the saved article body. The feature remains presentation-only: it reads existing local article sidecars and existing article/story metadata, creates no JSON artifact, route family, schema key, source collection behavior, scraping behavior, LLM behavior, scheduling behavior, connector behavior, schema/app/runtime/manifest/JSON contract change, or app-facing contract field.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, deterministic text helpers, `templates.py` server-rendered HTML helpers, pytest, ruff, uv with frozen `--no-config` verification commands.

---

## Product Gap

Recent ROW ONE stages made saved local article pages much richer:

- Stage 365 added the Local Article Content Segment Deck for content-section navigation.
- Stage 368 added the Local Article Body Organizer for filed/unfiled paragraph organization.
- Stage 369 added the Local Article Intelligence Brief for entity lanes, paragraph evidence, and local routes.
- Stages 377 through 381 added related saved local reads, lanes, bridge evidence, and relationship connection copy.

Those surfaces help readers navigate and verify the saved article, but they do not yet give a concise editorial synthesis of what the local article adds. Stage 382 closes that report-layer organization gap by adding a compact conclusion layer that answers:

- what the saved article adds to the ROW ONE signal;
- which thesis or trend signal it sharpens;
- how the reader should move into the saved body next.

This is not a new extraction, recommendation, scraping, or summarization engine. It is deterministic report copy assembled from fields already present in the current story and local article.

## Scope Decision From Pre-Plan Exploration

- Add a new builder module: `src/fashion_radar/row_one/local_article_synthesis_brief.py`.
- Add a new generated HTML section inside `articles/<story-id>.html`.
- Place the section after `{local_article_intelligence_brief}` and before `{local_article_section}` in `render_local_article_page_html(...)`.
- Keep the brief distinct from existing surfaces:
  - do not render entity lanes;
  - do not render key-signal buckets;
  - do not render section rows;
  - do not render related-read metrics;
  - do not render paragraph evidence grids;
  - do not duplicate the body organizer route.
  - do not repeat the same `why_it_matters` sentence already surfaced by
    Saved Article Key Signals and Local Article Intelligence Brief unless no
    other meaningful synthesis source exists.
- Use short narrative fields and at most three same-page anchors.
- Use existing story/local-article text only.
- Do not call an LLM.
- Do not fetch, scrape, collect, match, score, rank, or schedule anything.
- Do not add compliance-review product features.
- Do not add default social connectors.

## File Map

- Create `src/fashion_radar/row_one/local_article_synthesis_brief.py`
  - Add frozen dataclasses for the synthesis brief and same-page anchors.
  - Add `build_row_one_local_article_synthesis_brief(story, local_article)`.
  - Normalize and cap text deterministically.
  - Validate story/article ID alignment with `safe_local_article_story_id(...)`.
  - Use existing story/local article fields in a stable fallback order.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import the new builder/dataclasses.
  - Build and render the brief in `render_local_article_page_html(...)`.
  - Add `_render_local_article_synthesis_brief(...)`.
  - Use a synthesis-specific wrapper that delegates to `_safe_local_article_intelligence_href(...)` for fragment shape validation and then validates that same-page paragraph and content-section targets exist on the rendered local article; do not duplicate the same fragment allow-list in a second function body.
  - Add CSS selectors for `.local-article-synthesis-brief` and children.
- Create `tests/test_row_one_local_article_synthesis_brief.py`
  - Add focused builder tests.
- Modify `tests/test_row_one_render.py`
  - Add render ordering, escaping, CSS, and generated-page placement tests.
- Modify `tests/test_workflows.py`
  - Extend contract and artifact denylists.
  - Add a Stage 382 generated-site-only sentinel.
- Modify `tests/test_row_one_docs.py`
  - Add docs boundary test.
- Modify `README.md` and `docs/row-one.md`
  - Add one Stage 382 generated-site-only boundary paragraph.
- Create review artifacts under `docs/reviews/`
  - `claude-code-stage-382-plan-review.md`
  - `opencode-stage-382-plan-review.md`
  - `claude-code-stage-382-code-review.md`
  - `opencode-stage-382-code-review.md`
  - Rereview files only when Critical or Important findings require fixes.

## Internal Builder Model

These frozen dataclasses are internal Python render models only; they are not app-facing, JSON, schema, route, runtime, manifest, or connector contracts.

Add:

```python
@dataclass(frozen=True)
class RowOneLocalArticleSynthesisAnchor:
    label: LocalizedText
    href: str
    support: LocalizedText | None = None


@dataclass(frozen=True)
class RowOneLocalArticleSynthesisBrief:
    title: LocalizedText
    source_name: str
    lead: LocalizedText
    thesis: LocalizedText
    article_adds: LocalizedText
    reader_move: LocalizedText
    basis_note: LocalizedText
    anchors: tuple[RowOneLocalArticleSynthesisAnchor, ...]
```

The builder is:

```python
def build_row_one_local_article_synthesis_brief(
    *,
    story: RowOneStory,
    local_article: RowOneLocalArticle,
) -> RowOneLocalArticleSynthesisBrief | None:
    ...
```

The builder returns `None` when `story.id` and `local_article.story_id` do not match, when the story ID is not a safe local article story ID, or when no meaningful text can be derived from the current story/local article.

## Builder Rules

- `title`:
  - English: `Local Article Synthesis Brief`
  - Chinese: `本地文章综合简报`
- `source_name` uses normalized `local_article.source_name`, falling back to normalized `story.source_name`.
- Field ownership and deduplication:
  - Build candidate text with a consumed-source set and normalized consumed-text
    set so `lead`, `thesis`, and `article_adds` cannot use the same source
    field or render identical normalized text.
  - `RowOneLocalArticleBriefSection.key` is limited to `what_happened`,
    `why_it_matters`, `signal_context`, and `watch_next`. Do not look for
    `editorial_takeaway` in `local_article.brief_sections`; use
    `story.editorial_takeaway` as the only editorial-takeaway source.
  - Candidate source IDs should be stable strings such as
    `story.editorial_takeaway`, `story.summary`, `story.why_it_matters`,
    `brief.signal_context`, `brief.what_happened`, `brief.watch_next`,
    `content_section.0.body`, `content_section.0.item.0.body`, and
    `paragraph.0`.
  - All three synthesis cards are required by the data contract. If `lead`,
    `thesis`, and `article_adds` cannot each be populated with distinct
    meaningful text after source/text deduplication, return `None` instead of
    emitting a partial, one-card, two-card, empty-card, or repeated brief.
  - Do not support a partial two-card render path in Stage 382; keeping the
    required-field model and three-card HTML blueprint aligned is more important
    than rendering sparse ambiguous inputs.
- `lead` should describe the current saved article as a compact editorial read,
  preferring sources that are not already the page's primary `why_it_matters`
  copy:
  - Prefer `story.editorial_takeaway`.
  - Fall back to `story.summary`.
  - Fall back to local brief section `signal_context`.
  - Fall back to local brief section `what_happened`.
  - Fall back to local brief section `watch_next`.
  - Fall back to the first meaningful content-section body or item body not
    already consumed.
  - Fall back to the first meaningful saved paragraph not already consumed.
  - Fall back to `story.why_it_matters` only when no earlier source is usable.
  - Fall back to local brief section `why_it_matters` only when no earlier
    source is usable.
- `thesis` should answer which idea the article sharpens:
  - Prefer `story.editorial_takeaway` only if `lead` did not already consume it.
  - Fall back to local brief section `signal_context`.
  - Fall back to `story.signal_context`.
  - Fall back to the first meaningful content-section title/body pair not
    already consumed.
  - Fall back to `story.summary` only if `lead` did not already consume it.
  - Do not reference local brief section key `editorial_takeaway`; in-memory
    `RowOneLocalArticleBriefSection.key` only supports `what_happened`,
    `why_it_matters`, `signal_context`, and `watch_next`.
- `article_adds` should answer what the local article contributes:
  - Prefer the first meaningful content-section body not already consumed.
  - Fall back to the first meaningful content item body not already consumed.
  - Fall back to the first meaningful saved paragraph not already consumed.
  - Fall back to local brief section `what_happened` or `watch_next` only if no
    content body or paragraph source is usable and neither source text was
    already consumed.
  - Do not use `story.editorial_takeaway`, `story.why_it_matters`, or local
    brief section `why_it_matters` for `article_adds`.
- `reader_move` should explain how to read next:
  - If anchors exist, mention reading through the selected saved body anchors.
  - If no anchors exist but content sections exist, point the reader to the organized body.
  - Keep copy deterministic, not analytics-based.
- `basis_note` should be a compact transparency note:
  - English: `Built from saved ROW ONE story fields and local article text already stored for this page.`
  - Chinese: `基于本页已保存的 ROW ONE 故事字段与本地文章正文整理生成。`
- Text caps:
  - `lead`: 180 characters.
  - `thesis`: 160 characters.
  - `article_adds`: 160 characters.
  - `reader_move`: 160 characters.
  - `anchor.support`: 110 characters.
- Anchor rules:
  - Maximum 3 anchors.
  - Prefer the first 2 eligible content sections with meaningful titles or bodies.
  - Add the first eligible paragraph anchor if there is saved body text.
  - Paragraph anchor numbering is 1-based: paragraph index `0` renders
    `#local-article-paragraph-1`.
  - Hrefs must be only `#local-article-content-section-N` or `#local-article-paragraph-N`.
  - Do not add outbound URLs.
- Chinese fallback:
  - For localized fields, use Chinese text when present.
  - If Chinese text is absent or misaligned, fall back to the English text.
  - Never produce blank Chinese spans when English text exists.

## Render Rules

- Build the brief in `render_local_article_page_html(...)`:

```python
local_article_synthesis_brief = _render_local_article_synthesis_brief(
    build_row_one_local_article_synthesis_brief(
        story=story,
        local_article=local_article,
    )
)
```

- Insert the rendered string after `{local_article_intelligence_brief}` and before `{local_article_section}`.
- Render:

```html
<section class="local-article-synthesis-brief"
  aria-labelledby="local-article-synthesis-brief-title">
  <div class="local-article-synthesis-brief-header">
    <h2 id="local-article-synthesis-brief-title">...</h2>
    <p>...</p>
  </div>
  <div class="local-article-synthesis-brief-grid">
    <article class="local-article-synthesis-brief-card">...</article>
    <article class="local-article-synthesis-brief-card">...</article>
    <article class="local-article-synthesis-brief-card">...</article>
  </div>
  <p class="local-article-synthesis-brief-route">...</p>
  <div class="local-article-synthesis-brief-anchors">...</div>
  <p class="local-article-synthesis-brief-basis">...</p>
</section>
```

- Cards:
  - `The read` / `阅读判断` renders `lead`.
  - `What it sharpens` / `它强化了什么` renders `thesis`.
  - `What the article adds` / `文章补充了什么` renders `article_adds`.
- `reader_move` renders above anchors as a short route note.
- Omit anchors that fail `_safe_local_article_intelligence_href(...)`, or the
  shared `_safe_local_article_same_page_href(...)` if Task 5 extracts one.
- Omit the entire section if the builder returns `None`.
- Escape every rendered value with `_esc(...)`.
- Do not add new routes or JSON data.

## Acceptance Criteria

- `articles/<story-id>.html` renders a Local Article Synthesis Brief after the existing Local Article Intelligence Brief and before the saved local article body.
- The brief gives compact narrative synthesis: lead, thesis, article contribution, reader move, basis note, and safe same-page anchors.
- The brief does not duplicate entity lanes, key-signal buckets, section-row organizers, related-read metrics, or paragraph evidence grids.
- The builder returns `None` unless `lead`, `thesis`, and `article_adds` all
  contain distinct meaningful text after consumed-source and normalized-text
  deduplication.
- The synthesis brief does not repeat the same normalized `why_it_matters` text
  already rendered by Saved Article Key Signals or Local Article Intelligence
  Brief. `why_it_matters` may be used only as a last-resort fallback and only
  when it does not duplicate another visible synthesis card.
- The builder handles mismatched story/article IDs, unsafe story IDs, missing optional fields, escaped text, and missing or misaligned Chinese text.
- Unsafe hrefs never render.
- The feature is generated-site-only:
  - no generated JSON artifacts;
  - no standalone HTML route;
  - no new schema/app/runtime/manifest field;
  - no source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, analytics, personalization, recommendation, or compliance-review behavior.
- Documentation describes the generated-site-only boundary.
- Full frozen tests and release hygiene gates pass.

## Task 1: Plan Review

**Files:**
- Create: `docs/reviews/claude-code-stage-382-plan-review.md`
- Create: `docs/reviews/opencode-stage-382-plan-review.md`
- Modify after review feedback: `docs/superpowers/plans/2026-07-12-stage-382-local-article-synthesis-brief-plan.md`

- [ ] **Step 1: Ask Claude Code to review the plan**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 382 Local Article Synthesis Brief plan in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-12-stage-382-local-article-synthesis-brief-plan.md, docs/superpowers/plans/2026-07-09-stage-369-local-article-intelligence-brief-plan.md, docs/superpowers/plans/2026-07-10-stage-381-saved-local-article-related-read-connection-brief-plan.md, src/fashion_radar/row_one/local_article_intelligence_brief.py, src/fashion_radar/row_one/saved_article_body_organizer.py, src/fashion_radar/row_one/saved_article_key_signals.py, src/fashion_radar/row_one/templates.py around render_local_article_page_html and local article render helpers, tests/test_row_one_render.py around local article intelligence/body organizer tests, tests/test_workflows.py, and tests/test_row_one_docs.py. Goal: add a generated-site-only Local Article Synthesis Brief to articles/<story-id>.html that gives a compact deterministic editorial synthesis from existing story/local article fields without adding contracts, artifacts, routes, collection, scraping, LLM, scheduling, connectors, or compliance-review behavior. Check feasibility, duplication risk with existing surfaces, data-model fit, href safety, escaping, generated-site-only boundaries, test coverage, docs, and implementation sequencing. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-382-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists, contains a complete review body, and ends with `END_OF_REVIEW`.

- [ ] **Step 2: Ask opencode to cross-check the plan**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 382 Local Article Synthesis Brief plan. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/reviews/claude-code-stage-382-plan-review.md if present, docs/superpowers/plans/2026-07-12-stage-382-local-article-synthesis-brief-plan.md, src/fashion_radar/row_one/local_article_intelligence_brief.py, src/fashion_radar/row_one/saved_article_body_organizer.py, src/fashion_radar/row_one/saved_article_key_signals.py, src/fashion_radar/row_one/templates.py around local article page rendering, tests/test_row_one_render.py, tests/test_workflows.py, and tests/test_row_one_docs.py. Check feasibility, duplication with existing ROW ONE local article surfaces, generated-site-only boundaries, href safety, escaping, test coverage, docs, and whether the plan accidentally adds collection, scraping, LLM, connector, scheduling, or app contract behavior. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-382-plan-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains one coherent complete review body.

- [ ] **Step 3: Fix Critical and Important plan findings**

If either review raises Critical or Important findings, update this plan and run rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 382 Local Article Synthesis Brief plan after fixes. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-12-stage-382-local-article-synthesis-brief-plan.md, docs/reviews/claude-code-stage-382-plan-review.md, and docs/reviews/opencode-stage-382-plan-review.md. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-382-plan-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 382 Local Article Synthesis Brief plan after fixes. Read the plan and review records. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-382-plan-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important planning findings.

## Task 2: Builder RED Tests

**Files:**
- Create: `tests/test_row_one_local_article_synthesis_brief.py`

- [ ] **Step 1: Add failing builder tests**

Create tests covering:

```python
def test_build_local_article_synthesis_brief_uses_story_and_local_article_text() -> None:
    ...


def test_build_local_article_synthesis_brief_returns_none_for_mismatched_story() -> None:
    ...


def test_build_local_article_synthesis_brief_returns_none_for_unsafe_story_id() -> None:
    ...


def test_build_local_article_synthesis_brief_returns_none_without_meaningful_text() -> None:
    ...


def test_build_local_article_synthesis_brief_handles_missing_and_misaligned_zh() -> None:
    ...


def test_build_local_article_synthesis_brief_caps_text_and_anchors() -> None:
    ...


def test_build_local_article_synthesis_brief_dedupes_consumed_sources() -> None:
    ...


def test_build_local_article_synthesis_brief_returns_none_when_dedup_leaves_fewer_than_three_cards() -> None:
    ...
```

Expected behaviors:

- imports fail until the new module exists;
- a valid story/local article produces title, source name, lead, thesis, article contribution, reader move, basis note, and safe anchors;
- mismatched story/article IDs return `None`;
- unsafe story IDs return `None`;
- empty or whitespace-only story/local article text returns `None`;
- lead, thesis, and article contribution do not render duplicate normalized text
  when sparse inputs expose the same candidate through multiple fallback paths;
- the builder returns `None` when deduplication leaves fewer than three distinct
  synthesis cards, preserving the required-field data contract and three-card
  render blueprint;
- missing Chinese text falls back to English;
- long text is capped deterministically with ASCII ellipses;
- anchors are capped at three and use same-page fragments only.

- [ ] **Step 2: Run RED builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_synthesis_brief.py -q
```

Expected: FAIL because `fashion_radar.row_one.local_article_synthesis_brief` does not exist yet.

## Task 3: Builder Implementation

**Files:**
- Create: `src/fashion_radar/row_one/local_article_synthesis_brief.py`
- Test: `tests/test_row_one_local_article_synthesis_brief.py`

- [ ] **Step 1: Add dataclasses and builder**

Implement `RowOneLocalArticleSynthesisAnchor`, `RowOneLocalArticleSynthesisBrief`, and `build_row_one_local_article_synthesis_brief(...)` exactly as described in Data Contract and Builder Rules.

- [ ] **Step 2: Add private helpers**

Add helpers for:

- `_nonblank_localized_text(...)`
- `_truncate_localized_text(...)`
- `_truncate(...)`
- `_first_brief_section_text(...)`
- `_first_content_text(...)`
- `_first_paragraph_text(...)`
- `_candidate(...)`
- `_choose_candidate(...)`
- `_normalized_candidate_key(...)`
- `_anchors(...)`
- `_section_anchor(...)`
- `_paragraph_anchor(...)`

Keep helpers private to avoid creating new app-facing APIs.

- [ ] **Step 3: Run builder tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_synthesis_brief.py -q
```

Expected: PASS.

## Task 4: Render RED Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Add failing render tests**

Add tests covering:

```python
def test_render_local_article_page_includes_local_article_synthesis_brief_after_intelligence_brief() -> None:
    ...


def test_render_local_article_synthesis_brief_escapes_and_filters_links() -> None:
    ...


def test_render_row_one_site_writes_local_article_synthesis_brief_only_on_local_article_page(tmp_path) -> None:
    ...


def test_render_row_one_site_synthesis_brief_does_not_leak_contracts_or_artifacts(tmp_path) -> None:
    ...


def test_row_one_css_includes_local_article_synthesis_brief_styles() -> None:
    ...
```

Expected checks:

- HTML contains `Local Article Synthesis Brief` and `本地文章综合简报`;
- render order is content segment deck -> body organizer -> local article intelligence brief -> local article synthesis brief -> saved body;
- same-page anchors render only when safe;
- unsafe or injected href values do not render;
- text is escaped;
- DOM contains `class="local-article-synthesis-brief-card"` and
  `class="local-article-synthesis-brief-route"` when the section renders;
- homepage, saved article library, and detail pages do not contain the new section;
- the dedicated contract/artifact test checks `data/edition.json`,
  `data/manifest.json`, `data/runtime.json`, every generated
  `data/articles/*.json`, and forbidden `.json`/`.html` artifact stems.

- [ ] **Step 2: Run RED render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "synthesis_brief" -q
```

Expected: FAIL because the template does not render the new block yet.

## Task 5: Render Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Test: `tests/test_row_one_render.py`

- [ ] **Step 1: Import the new builder and dataclasses**

Modify the existing import section once:

```python
from fashion_radar.row_one.local_article_synthesis_brief import (
    RowOneLocalArticleSynthesisAnchor,
    RowOneLocalArticleSynthesisBrief,
    build_row_one_local_article_synthesis_brief,
)
```

- [ ] **Step 2: Build and insert the rendered section**

Inside `render_local_article_page_html(...)`, add:

```python
local_article_synthesis_brief = _render_local_article_synthesis_brief(
    build_row_one_local_article_synthesis_brief(
        story=story,
        local_article=local_article,
    )
)
```

Insert `{local_article_synthesis_brief}` after `{local_article_intelligence_brief}` and before `{local_article_section}`.

- [ ] **Step 3: Add render helpers**

Add:

```python
def _render_local_article_synthesis_brief(
    brief: RowOneLocalArticleSynthesisBrief | None,
) -> str:
    ...


def _render_local_article_synthesis_anchor(
    anchor: RowOneLocalArticleSynthesisAnchor,
) -> str:
    ...
```

`_render_local_article_synthesis_anchor(...)` must call the existing
`_safe_local_article_intelligence_href(...)` directly. Do not add
`_safe_local_article_synthesis_href(...)`, and do not duplicate the same regex
and whitespace validation logic in another helper.

- [ ] **Step 4: Add CSS**

Add selectors near the existing local article generated-site-only section styles:

- `.local-article-synthesis-brief`
- `.local-article-synthesis-brief-header`
- `.local-article-synthesis-brief-grid`
- `.local-article-synthesis-brief-card`
- `.local-article-synthesis-brief-route`
- `.local-article-synthesis-brief-anchors`
- `.local-article-synthesis-brief-basis`

Add responsive grid fallback near the existing local article media-query block:
`.local-article-synthesis-brief-grid { grid-template-columns: 1fr; }`.
`test_row_one_css_includes_local_article_synthesis_brief_styles` must assert
the selector tuple above plus the mobile grid fallback rule.

- [ ] **Step 5: Run render tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "synthesis_brief" -q
```

Expected: PASS.

## Task 6: Workflow And Contract Boundaries

**Files:**
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Extend generated contract denylist**

Add these strings near the local article generated-site-only denylist:

```python
"local_article_synthesis_brief",
"article_synthesis_brief",
"synthesis_brief",
"RowOneLocalArticleSynthesisBrief",
"RowOneLocalArticleSynthesisAnchor",
"Local Article Synthesis Brief",
"Article Synthesis Brief",
"Synthesis Brief",
"本地文章综合简报",
"local-article-synthesis-brief",
"article-synthesis-brief",
"synthesis-brief",
```

Insert these values in the generated contract payload assertion block near the
existing `generated_contract_payload` local-article generated-site-only checks.
This is a content/string denylist; do not mix these title/class/dataclass
strings into the artifact-stem tuple.

- [ ] **Step 2: Extend forbidden artifact stems**

Add:

```python
"local-article-synthesis-brief",
"article-synthesis-brief",
"synthesis-brief",
"local_article_synthesis_brief",
"article_synthesis_brief",
"synthesis_brief",
```

Insert these values only in the forbidden artifact-stem tuple near the existing
file-existence checks. Artifact stems should stay limited to route/file stem
forms, not human titles, class names, dataclass names, or Chinese copy.

- [ ] **Step 3: Add generated-site-only sentinel**

Add `test_stage_382_local_article_synthesis_brief_stays_generated_site_only(...)`.

Patch `_render_local_article_synthesis_brief` with `raising=True` to return a
sentinel string named `STAGE_382_LOCAL_ARTICLE_SYNTHESIS_BRIEF_SENTINEL` and
run `render_row_one_site(...)` with the existing local article fixture pattern
used by local-article workflow tests. Because the patch replaces the renderer,
the sentinel proves only generated local article pages call that renderer; no
extra fixture coupling or builder forcing is needed.
Assert:

- sentinel exact count is `1` across generated site HTML and JSON files;
- sentinel appears only in `articles/<story-id>.html`;
- sentinel does not appear in `index.html`;
- sentinel does not appear in `articles/index.html`;
- sentinel does not appear in `details/<story-id>.html`;
- sentinel does not appear in `data/edition.json`, `data/manifest.json`,
  `data/runtime.json`, or any generated `data/articles/*.json`;
- no forbidden JSON/HTML artifact stems exist.

- [ ] **Step 4: Run workflow tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py::test_stage_382_local_article_synthesis_brief_stays_generated_site_only -q
```

Expected: PASS.

## Task 7: Docs Boundary

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`

- [ ] **Step 1: Add docs paragraph**

Add this paragraph before the Stage 381 boundary paragraph in both `README.md` and `docs/row-one.md`:

```text
Stage 382 adds generated-site only Local Article Synthesis Brief inside `articles/<story-id>.html` between the Local Article Intelligence Brief and the saved local article body; it reuses current-edition saved local article sidecars, existing ROW ONE story summaries, existing story why-it-matters/editorial context, existing local article brief sections, existing local article content sections, existing saved local paragraphs, existing content-section anchors, and existing paragraph anchors to turn each saved article page into a compact synthesis of what the saved article adds, which signal it sharpens, and how to read the local body next without changing app-facing contracts; it does not create `data/local-article-synthesis-brief.json`, does not create `data/article-synthesis-brief.json`, does not create `data/synthesis-brief.json`, does not create `local-article-synthesis-brief.html`, does not create `article-synthesis-brief.html`, does not create `synthesis-brief.html`, does not create new article-source sidecars, does not create new route families, does not alter `index.html`, `articles/index.html`, or detail pages, does not publish full articles on the homepage or library index, does not add outbound article URLs as primary navigation, and does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, scraping, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 2: Add docs test**

Add `test_row_one_docs_describe_stage_382_local_article_synthesis_brief_boundary()` to `tests/test_row_one_docs.py`, mirroring the Stage 369 and Stage 381 boundary tests.

Assert:

- expected paragraph exists in both docs;
- Stage 382 paragraph appears before Stage 381 paragraph;
- the docs test slices from the exact Stage 382 paragraph start through the
  Stage 381 paragraph start and asserts `stage_382_pos < stage_381_pos`;
- stale phrases such as `creates data/local-article-synthesis-brief.json`, `writes local-article-synthesis-brief.html`, `adds scraping`, `adds llm`, `adds connector`, and `adds scheduling` do not appear inside the Stage 382 paragraph slice.
- stale phrases also include plural/common variants:
  `adds fetching`, `adds extraction`, `adds scoring`, `adds ranking`,
  `adds llm calls`, `adds connectors`, `adds recommendation`,
  `adds personalization`, `adds compliance-review`,
  `changes row-one-app/v7`, `changes row-one-manifest/v1`, and
  `changes row-one-runtime/v1`.

- [ ] **Step 3: Run docs test**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_382_local_article_synthesis_brief_boundary -q
```

Expected: PASS.

## Task 8: Focused Verification

**Files:**
- Existing changed files only.

- [ ] **Step 1: Run focused Stage 382 suite**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_local_article_synthesis_brief.py \
  tests/test_row_one_render.py -k "synthesis_brief" \
  tests/test_workflows.py::test_stage_382_local_article_synthesis_brief_stays_generated_site_only \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_382_local_article_synthesis_brief_boundary -q
```

Expected: PASS.

- [ ] **Step 2: Run formatting checks**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
```

Expected: PASS.

## Task 9: Code Review

**Files:**
- Create: `docs/reviews/claude-code-stage-382-code-review.md`
- Create: `docs/reviews/opencode-stage-382-code-review.md`
- Modify source/tests/docs only if Critical or Important findings require fixes.

- [ ] **Step 1: Ask Claude Code for code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 382 Local Article Synthesis Brief implementation in /home/ubuntu/fashion-radar. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/superpowers/plans/2026-07-12-stage-382-local-article-synthesis-brief-plan.md, git diff HEAD, src/fashion_radar/row_one/local_article_synthesis_brief.py, src/fashion_radar/row_one/templates.py, tests/test_row_one_local_article_synthesis_brief.py, tests/test_row_one_render.py, tests/test_workflows.py, tests/test_row_one_docs.py, README.md, and docs/row-one.md. Goal: generated-site-only Local Article Synthesis Brief on articles/<story-id>.html that deterministically synthesizes existing story/local article text into a compact conclusion layer without adding contracts, artifacts, routes, collection, scraping, LLM, connectors, scheduling, or compliance-review behavior. Check correctness, duplication with existing local article surfaces, href safety, escaping, generated-site-only boundary, docs, tests, and regressions. Return findings only ordered by Critical, Important, Minor. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-382-code-review.md
rm -f "$tmp_review"
```

Expected: review file exists, contains complete review body, and ends with `END_OF_REVIEW`.

- [ ] **Step 2: Ask opencode to cross-check code**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 382 Local Article Synthesis Brief implementation. Read AGENTS.md, docs/REVIEW_PROTOCOL.md, docs/reviews/claude-code-stage-382-code-review.md if present, docs/superpowers/plans/2026-07-12-stage-382-local-article-synthesis-brief-plan.md, git diff HEAD, src/fashion_radar/row_one/local_article_synthesis_brief.py, src/fashion_radar/row_one/templates.py, tests/test_row_one_local_article_synthesis_brief.py, tests/test_row_one_render.py, tests/test_workflows.py, tests/test_row_one_docs.py, README.md, and docs/row-one.md. Check correctness, duplication, href safety, escaping, generated-site-only boundaries, docs, tests, and regressions. Return the final review body only, ordered by Critical, Important, Minor. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-382-code-review.md
rm -f "$tmp_review"
```

Expected: review file exists and contains one coherent complete review body.

- [ ] **Step 3: Fix Critical and Important code findings**

If either review raises Critical or Important findings:

1. Update source/tests/docs.
2. Rerun focused tests.
3. Rerun code rereviews:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Re-review Stage 382 Local Article Synthesis Brief implementation after fixes. Read the plan, prior reviews, git diff HEAD, and changed files. Return remaining Critical and Important findings only. End with END_OF_REVIEW." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-382-code-rereview.md
rm -f "$tmp_review"
```

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Re-review Stage 382 Local Article Synthesis Brief implementation after fixes. Read the plan, prior reviews, git diff HEAD, and changed files. Return remaining Critical and Important findings only. Do not modify files." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-382-code-rereview.md
rm -f "$tmp_review"
```

Expected: no remaining Critical or Important code findings.

## Task 10: Full Release Gates And Commit

**Files:**
- Existing changed files only.

- [ ] **Step 1: Run full gates**

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

Expected:

- pytest passes;
- ruff check passes;
- ruff format check passes;
- release hygiene passes;
- lock check passes offline;
- whitespace checks pass.

- [ ] **Step 2: Inspect git status**

Run:

```bash
git status --short
```

Expected: only Stage 382 source, test, docs, and review files are modified/untracked.

- [ ] **Step 3: Commit Stage 382**

Run:

```bash
git add \
  src/fashion_radar/row_one/local_article_synthesis_brief.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_local_article_synthesis_brief.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  README.md \
  docs/row-one.md \
  docs/superpowers/plans/2026-07-12-stage-382-local-article-synthesis-brief-plan.md \
  docs/reviews/claude-code-stage-382-plan-review.md \
  docs/reviews/opencode-stage-382-plan-review.md \
  docs/reviews/claude-code-stage-382-code-review.md \
  docs/reviews/opencode-stage-382-code-review.md
git commit -m "Stage 382: add local article synthesis brief"
```

If rereview files exist because Critical or Important findings were fixed, include them in `git add`.

- [ ] **Step 4: Push**

Run:

```bash
git push origin main
```

Expected: push succeeds.

- [ ] **Step 5: Node-end Handoff Summary**

Report:

- repo status;
- latest commit hash;
- verified commands;
- uncommitted files;
- next step.

Do not paste large diffs or logs.
