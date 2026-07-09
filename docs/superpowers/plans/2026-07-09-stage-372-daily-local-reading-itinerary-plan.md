# Stage 372 Daily Local Reading Itinerary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only Daily Local Reading Itinerary to the ROW ONE homepage.

**Architecture:** Build a focused homepage itinerary from current-edition saved local article sidecars and generated local article page anchors, then render it in `index.html` after Stage 371 Daily Local Saved Article Organizer and before Saved Article Content Organization. Keep the feature out of app contracts, JSON artifacts, article pages, detail pages, source collection, fetching, scoring, ranking, LLM, connector, scheduling, analytics, personalization, recommendation, and compliance-review paths.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, static HTML string templates, existing CSS bundle in `templates.py`, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config`.

---

## File Structure

- Create `src/fashion_radar/row_one/daily_local_reading_itinerary.py`
  - Builds `RowOneDailyLocalReadingItinerary | None`.
  - Owns card/evidence dataclasses, excerpting, reason labeling, safe page href validation, paragraph index validation, evidence chip generation, dedupe, and caps.
- Create `tests/test_row_one_daily_local_reading_itinerary.py`
  - Builder tests only.
- Modify `src/fashion_radar/row_one/render.py`
  - Import builder.
  - Build itinerary after `local_article_page_hrefs_by_story_id`.
  - Pass itinerary into `render_index_html`.
  - Do not write new artifacts.
- Modify `src/fashion_radar/row_one/templates.py`
  - Import itinerary dataclasses.
  - Add optional `daily_local_reading_itinerary` parameter to `render_index_html`.
  - Render after `{daily_local_saved_article_organizer_section}` and before `{saved_article_content_organization_section}`.
  - Add render helpers and CSS selectors.
- Modify `tests/test_row_one_render.py`
  - Render fixture, unsafe href filtering, homepage-only integration, CSS selector/mobile tests.
- Modify `README.md` and `docs/row-one.md`
  - Add exact Stage 372 boundary paragraph before Stage 371.
- Modify `tests/test_row_one_docs.py`
  - Exact paragraph and stale phrase guard.
- Modify `tests/test_workflows.py`
  - App contract denylist, artifact stem denylist, generated-site-only wrapper guard.
- Add review artifacts:
  - `docs/reviews/claude-code-stage-372-plan-review.md`
  - `docs/reviews/opencode-stage-372-plan-review.md`
  - `docs/reviews/claude-code-stage-372-code-review.md`
  - `docs/reviews/opencode-stage-372-code-review.md`

## Plan Review Fixes Incorporated

Claude Code and opencode plan reviews approved the stage direction with these required fixes before implementation:

- Define `_first_paragraph_anchor(article, page_href) -> str | None` as the full same-site href for the first non-empty paragraph, or `None` when no non-empty paragraph exists.
- Compute `selected_count` as the number of unique story ids represented across rendered `Start Here` and `Skim Next` cards, and assert it in builder and render tests.
- Emit one `Source context` card per article when a paragraph anchor exists, regardless of whether Brand/Product cards were also emitted for that article; use source name, `body_source`, and paragraph-count metadata instead of repeating the raw `Start Here` paragraph text.
- Dedupe cards by the `(href, normalized reason label)` tuple across `Start Here` and `Skim Next`, and include an explicit dedupe assertion.
- Generate evidence chip labels from the best available article-backed label in this order: reference name, content-section item label, content-section title, article title, then paragraph label such as `Paragraph 1`.
- Render and test the itinerary dek.
- Compute `source_count` as the number of unique source names represented across rendered `Start Here` and `Skim Next` cards.
- Compute `evidence_count` as `len(evidence_trail)`.
- Link paragraph-index fallback cards to the content-section anchor for the containing section, not to the paragraph anchor.
- Use read-only Claude Code review commands and opencode `zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar` review commands.

---

### Task 1: Builder Tests

**Files:**
- Create: `tests/test_row_one_daily_local_reading_itinerary.py`

- [ ] **Step 1: Write the failing builder tests**

Create `tests/test_row_one_daily_local_reading_itinerary.py` with test helpers modeled on `tests/test_row_one_daily_local_saved_article_organizer.py`. Include helpers named `_lt`, `_ref`, `_story`, `_edition`, `_brief`, `_item`, `_section`, and `_article`.

The tests must include these exact test names:

- `test_build_daily_local_reading_itinerary_sequences_saved_content`
- `test_build_daily_local_reading_itinerary_filters_unsafe_inputs`
- `test_build_daily_local_reading_itinerary_uses_valid_paragraph_index_fallbacks`
- `test_build_daily_local_reading_itinerary_omits_label_only_items`
- `test_build_daily_local_reading_itinerary_caps_dedupes_and_truncates`
- `test_build_daily_local_reading_itinerary_returns_none_without_content`

`test_build_daily_local_reading_itinerary_sequences_saved_content` must assert:

```python
itinerary = build_row_one_daily_local_reading_itinerary(
    _edition(story),
    {story.id: _article(story.id)},
    {story.id: f"{story.id}.html"},
)

assert itinerary is not None
assert itinerary.title.en == "Daily Local Reading Itinerary"
assert itinerary.title.zh == "每日本地阅读路径"
assert itinerary.dek.en == "A short path through today's saved local articles."
assert itinerary.selected_count == 1
assert itinerary.source_count == 1
assert itinerary.evidence_count >= 2
assert itinerary.start_here is not None
assert itinerary.start_here.reason.en == "Start Here"
assert itinerary.start_here.href == (
    "articles/the-row-signal-1234567890.html#local-article-paragraph-1"
)
assert [card.reason.en for card in itinerary.skim_next] == [
    "Brand / people signal",
    "Product signal",
    "Source context",
]
assert itinerary.skim_next[0].href == (
    "articles/the-row-signal-1234567890.html#local-article-content-section-1"
)
assert itinerary.skim_next[1].href == (
    "articles/the-row-signal-1234567890.html#local-article-content-section-2"
)
assert itinerary.evidence_trail
assert itinerary.evidence_trail[0].label == "The Row"
assert "Margaux bag" in repr(itinerary)
```

`test_build_daily_local_reading_itinerary_filters_unsafe_inputs` must assert that only a valid story with a safe same-story page href is emitted and that `../`, protocol URLs, mismatched sidecar ids, missing hrefs, and unsafe story ids do not appear in `repr(itinerary)`.

`test_build_daily_local_reading_itinerary_uses_valid_paragraph_index_fallbacks` must create an item with `paragraph_indices=[99, -1, True, 0, 1, 1]`, blank paragraph zero, and non-empty paragraph one. It must assert that the emitted `Product signal` card uses paragraph one text and the section anchor for the matching content section.

`test_build_daily_local_reading_itinerary_omits_label_only_items` must create a product item with a label and reference but no body, no valid paragraph fallback, and no section body. It must assert that the product label is absent from `repr(itinerary)` and that no `Product signal` card is emitted.

`test_build_daily_local_reading_itinerary_caps_dedupes_and_truncates` must import and assert `DAILY_LOCAL_READING_ITINERARY_MAX_SKIM_CARDS`, `DAILY_LOCAL_READING_ITINERARY_MAX_EVIDENCE_CHIPS`, `DAILY_LOCAL_READING_ITINERARY_MAX_LABELS_PER_CARD`, and `DAILY_LOCAL_READING_ITINERARY_EXCERPT_CHARS`. It must prove caps hold, that duplicate cards with the same `(href, reason)` key collapse to one card, and that a long paragraph body does not appear in full in the representation.

`test_build_daily_local_reading_itinerary_returns_none_without_content` must assert `None` when there is no local article, no safe page href, or only blank paragraphs/briefs/sections.

- [ ] **Step 2: Run builder tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_reading_itinerary.py -q
```

Expected: fail with `ModuleNotFoundError: No module named 'fashion_radar.row_one.daily_local_reading_itinerary'`.

### Task 2: Builder Implementation

**Files:**
- Create: `src/fashion_radar/row_one/daily_local_reading_itinerary.py`
- Test: `tests/test_row_one_daily_local_reading_itinerary.py`

- [ ] **Step 1: Implement dataclasses and constants**

Create:

```python
DAILY_LOCAL_READING_ITINERARY_MAX_SKIM_CARDS = 4
DAILY_LOCAL_READING_ITINERARY_MAX_EVIDENCE_CHIPS = 6
DAILY_LOCAL_READING_ITINERARY_MAX_LABELS_PER_CARD = 4
DAILY_LOCAL_READING_ITINERARY_EXCERPT_CHARS = 170
```

Create frozen dataclasses:

```python
@dataclass(frozen=True)
class RowOneDailyLocalReadingItineraryCard:
    title: LocalizedText
    source_name: str
    reason: LocalizedText
    excerpt: LocalizedText
    href: str
    labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class RowOneDailyLocalReadingItineraryEvidence:
    label: str
    href: str


@dataclass(frozen=True)
class RowOneDailyLocalReadingItinerary:
    title: LocalizedText
    dek: LocalizedText
    selected_count: int
    source_count: int
    evidence_count: int
    start_here: RowOneDailyLocalReadingItineraryCard | None
    skim_next: tuple[RowOneDailyLocalReadingItineraryCard, ...]
    evidence_trail: tuple[RowOneDailyLocalReadingItineraryEvidence, ...]
```

- [ ] **Step 2: Implement builder behavior**

Implement `build_row_one_daily_local_reading_itinerary(edition, local_articles_by_story_id, article_hrefs_by_story_id) -> RowOneDailyLocalReadingItinerary | None` with the rules below.

Use these rules:

- title is `LocalizedText(en="Daily Local Reading Itinerary", zh="每日本地阅读路径")`
- dek is `LocalizedText(en="A short path through today's saved local articles.", zh="用一条短路径读完今日保存本地文章。")`
- `_first_paragraph_anchor(article, page_href) -> str | None` returns the full same-site href for the first non-empty paragraph, or `None` when no non-empty paragraph exists
- `Start Here` prefers the first non-empty brief section body when `_first_paragraph_anchor(article, page_href)` exists; otherwise use first non-empty paragraph
- `Skim Next` comes from content-section items and one source-context card per emitted article
- reason labels are `Brand / people signal`, `Product signal`, or `Source context`
- content-section cards link to `articles/<page_href>#local-article-content-section-N`
- paragraph-index fallback cards use paragraph text as excerpt but still link to the containing content-section anchor
- paragraph/source cards link to `articles/<page_href>#local-article-paragraph-N`
- source-context excerpts use source name, `body_source`, and paragraph-count metadata instead of repeating raw paragraph text
- labels are deduped normalized reference names, capped, and never required for rendering
- evidence chips are deduped by href and label, capped, and point only to same-site anchors
- evidence chip labels come from reference name, content-section item label, content-section title, article title, then paragraph label such as `Paragraph 1`
- invalid hrefs and unsafe story ids are filtered before card creation
- card dedupe uses the `(href, normalized reason label)` tuple across `Start Here` and `Skim Next`
- `selected_count` is the count of unique story ids represented across rendered `Start Here` and `Skim Next` cards
- `source_count` is the count of unique source names represented across rendered `Start Here` and `Skim Next` cards
- `evidence_count` is `len(evidence_trail)`

- [ ] **Step 3: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_reading_itinerary.py -q
```

Expected: all builder tests pass.

### Task 3: Renderer Tests

**Files:**
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing render tests**

Add a fixture helper `_daily_local_reading_itinerary_fixture()` near the Stage 371 fixture helpers.

Add tests named:

- `test_render_index_html_includes_daily_local_reading_itinerary`
- `test_render_daily_local_reading_itinerary_escapes_and_filters_links`
- `test_render_row_one_site_writes_daily_local_reading_itinerary_homepage_only`
- `test_row_one_css_includes_daily_local_reading_itinerary_rules`

The inclusion test must assert that the section includes:

- `Daily Local Reading Itinerary`
- `每日本地阅读路径`
- `Start Here`
- `Skim Next`
- `Evidence Trail`
- `Brand / people signal`
- `Product signal`
- `Vogue Business`
- `1 selected read`
- `1 source`
- `3 evidence links`
- `A short path through today&#x27;s saved local articles.`
- a safe `articles/<story-id>.html#local-article-content-section-1` href
- a safe `articles/<story-id>.html#local-article-paragraph-1` href
- placement after `class="daily-local-saved-article-organizer"` and before `class="saved-article-content-organization"`

The escaping/filtering test must include unsafe hrefs for zero-valued fragments, empty fragments, missing fragment, whitespace, traversal, absolute path, protocol URL, `//`, bad story id, and must assert they do not render.

The homepage-only test must assert:

- homepage includes `class="daily-local-reading-itinerary"`
- `articles/index.html`, `articles/<story-id>.html`, and `details/<story-id>.html` do not include that class
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not include `daily-local-reading-itinerary`, `Daily Local Reading Itinerary`, or `daily_local_reading_itinerary`
- no Stage 372 JSON/HTML artifact stems exist in the output root, `articles`, or `data`

The CSS test must assert selectors for:

- `.daily-local-reading-itinerary`
- `.daily-local-reading-itinerary-header`
- `.daily-local-reading-itinerary-grid`
- `.daily-local-reading-itinerary-start`
- `.daily-local-reading-itinerary-card`
- `.daily-local-reading-itinerary-evidence`
- `.daily-local-reading-itinerary-chip`

It must also assert a desktop two-column grid and a mobile one-column rule inside the responsive block.
The fixture must render the `featured=True` Start Here card with a `.daily-local-reading-itinerary-start` class.

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_local_reading_itinerary"
```

Expected: fail because renderer support does not exist yet.

### Task 4: Renderer Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Test: `tests/test_row_one_render.py`

- [ ] **Step 1: Wire builder into `render_row_one_site`**

In `render.py`, import `build_row_one_daily_local_reading_itinerary`.

Build after `daily_local_saved_article_organizer`:

```python
daily_local_reading_itinerary = build_row_one_daily_local_reading_itinerary(
    edition,
    local_articles_by_story_id,
    local_article_page_hrefs_by_story_id,
)
```

Pass `daily_local_reading_itinerary=daily_local_reading_itinerary` into `render_index_html`.

- [ ] **Step 2: Add template parameter and section placement**

In `templates.py`, add an optional `daily_local_reading_itinerary` parameter to `render_index_html`.

Compute:

```python
daily_local_reading_itinerary_section = _render_daily_local_reading_itinerary(
    daily_local_reading_itinerary
)
```

Render the section after `{daily_local_saved_article_organizer_section}` and before `{saved_article_content_organization_section}`.

- [ ] **Step 3: Add template helpers**

Implement helpers named `_render_daily_local_reading_itinerary`, `_render_daily_local_reading_itinerary_card`, `_render_daily_local_reading_itinerary_evidence`, and `_safe_daily_local_reading_itinerary_href`. The card helper accepts a `featured: bool = False` keyword flag; the href helper accepts `object` and returns `str | None`.

Use the same href-safety semantics as Stage 371. Return an empty section when all cards or evidence are unsafe.

- [ ] **Step 4: Add CSS**

Add compact, professional selectors to `row_one_css()` near Stage 371 styles. Use a restrained two-column desktop layout and one-column mobile collapse:

```css
.daily-local-reading-itinerary-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 18px;
}
```

Add responsive rule inside the existing `@media` block:

```css
.daily-local-reading-itinerary-grid { grid-template-columns: 1fr; }
```

- [ ] **Step 5: Run render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "daily_local_reading_itinerary or css_includes_daily_local_reading_itinerary"
```

Expected: all Stage 372 render tests pass.

### Task 5: Docs and Workflow Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Write failing docs/workflow tests**

Add `test_row_one_docs_describe_stage_372_daily_local_reading_itinerary_boundary` to `tests/test_row_one_docs.py`.

Use the exact boundary paragraph from the Stage 372 design doc. Assert the paragraph appears in `README.md` and `docs/row-one.md`, appears before Stage 371, and that the Stage 372 slice does not contain stale phrases such as:

- `creates data/daily-local-reading-itinerary.json`
- `writes data/daily-local-reading-itinerary.json`
- `creates daily-local-reading-itinerary.html`
- `writes daily-local-reading-itinerary.html`
- `changes row-one-app/v7`
- `adds recommendation`
- `adds compliance-review`

Update workflow denylist tests to include:

- `Daily Local Reading Itinerary`
- `daily-local-reading-itinerary`
- `local-reading-itinerary`
- `reading-itinerary`
- `daily_local_reading_itinerary`
- `local_reading_itinerary`
- `reading_itinerary`

Add a generated-site-only wrapper guard named `test_stage_372_daily_local_reading_itinerary_stays_generated_site_only`.

The wrapper guard should run `write_row_one_site_files` with one stored item and local article data, then assert only `index.html` contains the Stage 372 section and no forbidden Stage 372 artifacts exist.

- [ ] **Step 2: Run docs/workflow tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_372 or app_contract_does_not_include_generated_site_only or row_one_generated_site_does_not_write_forbidden_artifacts"
```

Expected: fail because docs and workflow guards are not updated yet.

- [ ] **Step 3: Update docs and workflow guards**

Insert the Stage 372 boundary paragraph into `README.md` and `docs/row-one.md` before the Stage 371 paragraph.

Update denylist tuples and artifact stem tuples in `tests/test_workflows.py` with the Stage 372 names.

- [ ] **Step 4: Run docs/workflow tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_372 or app_contract_does_not_include_generated_site_only or row_one_generated_site_does_not_write_forbidden_artifacts"
```

Expected: all selected docs/workflow tests pass.

### Task 6: Focused Verification, Reviews, and Full Gates

**Files:**
- Modify review artifacts under `docs/reviews/`

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "daily_local_reading_itinerary or stage_372 or reading_itinerary"
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/daily_local_reading_itinerary.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py
```

Expected: selected tests and lint pass.

- [ ] **Step 2: Request code reviews**

Run Claude Code review with `--effort max` in read-only plan mode and opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`. Save clean artifacts:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence --tools Read,Grep,Glob,LS,Bash -p "Review Stage 372 Daily Local Reading Itinerary implementation in /home/ubuntu/fashion-radar. Focus on correctness, generated-site-only boundary, href safety, article-backed content, tests, and whether Critical or Important issues remain. Return findings only, ordered by severity." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-372-code-review.md
rm -f "$tmp_review"

tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "Review Stage 372 Daily Local Reading Itinerary implementation in /home/ubuntu/fashion-radar. Focus on correctness, generated-site-only boundary, href safety, article-backed content, tests, and whether Critical or Important issues remain. Return findings only, ordered by severity." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-372-code-review.md
rm -f "$tmp_review"
```

Fix valid Critical and Important findings, then rerun focused verification.

- [ ] **Step 3: Run full gates**

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

Expected: all commands pass.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/daily_local_reading_itinerary.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py README.md docs/row-one.md docs/superpowers/specs/2026-07-09-stage-372-daily-local-reading-itinerary-design.md docs/superpowers/plans/2026-07-09-stage-372-daily-local-reading-itinerary-plan.md docs/reviews/claude-code-stage-372-plan-review.md docs/reviews/opencode-stage-372-plan-review.md docs/reviews/claude-code-stage-372-code-review.md docs/reviews/opencode-stage-372-code-review.md
git commit -m "Stage 372: add daily local reading itinerary"
git push origin main
```

Expected: commit and push succeed.
