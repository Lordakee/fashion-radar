# Stage 327 ROW ONE Saved Signal Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site only Saved Signal Index inside `articles/index.html` so ROW ONE organizes current saved local articles by existing brand/person/designer/product references.

**Architecture:** Create a pure render-only builder module, `saved_signal_index.py`, that walks current `edition.stories` plus the in-memory `local_articles_by_story_id` mapping and aggregates existing `RowOneLocalArticle.content_sections[*].items[*].references`. Pass the resulting dataclass tree into the existing saved article library page renderer so the section appears inside `articles/index.html`; keep app/runtime/manifest/schema/JSON contracts unchanged.

**Tech Stack:** Python dataclasses, existing ROW ONE Pydantic models, existing static HTML/CSS string templates, pytest, Ruff, `UV_NO_CONFIG=1 uv --no-config run --frozen`, Claude Code/opencode review gates.

---

## Files

- Create: `src/fashion_radar/row_one/saved_signal_index.py`
  - Define render-only dataclasses for signal paragraph links, support rows,
    signal entries, and the index aggregate.
  - Define `build_row_one_saved_signal_index()`.
  - Reuse `safe_local_article_story_id()` and `is_safe_row_one_detail_path()`.
  - Keep caps, fragment constants, and strict paragraph-index filtering private.
  - Build only from current `edition.stories` plus current
    `local_articles_by_story_id`; never read sidecar JSON from disk.
- Create: `tests/test_row_one_saved_signal_index.py`
  - Unit-test grouping, filtering, caps, current-edition behavior, and safe
    deep-link construction.
- Modify: `src/fashion_radar/row_one/render.py`
  - Import and build the saved signal index beside the existing saved article
    builders.
  - Pass it to `render_index_html()` and `render_saved_article_library_html()`.
  - Do not change `GENERATED_CHILDREN`.
- Modify: `src/fashion_radar/row_one/templates.py`
  - Import the new dataclasses.
  - Add `saved_signal_index` to `render_index_html()` and
    `render_saved_article_library_html()`.
  - Render the signal index inside `articles/index.html` after the library hero
    and before source groups.
  - Update the homepage article-library entry copy to mention browsing by
    signals or sources.
  - Add CSS selectors for the signal index section.
- Modify: `tests/test_row_one_render.py`
  - Add render tests for the signal section, omission, escaping, relative links,
    contract stability, and CSS selectors.
- Modify: `tests/test_workflows.py`
  - Extend generated-site boundary assertions with Stage 327 private keys and
    labels.
- Modify: `tests/test_row_one_docs.py`
  - Add docs boundary checks for Stage 327 wording.
- Modify: `README.md`
  - Add a generated-site-only ROW ONE Saved Signal Index note.
- Modify: `docs/row-one.md`
  - Add the same generated-site-only boundary note in more detail.
- Create review artifacts:
  - `docs/reviews/claude-code-stage-327-plan-review-prompt.md`
  - `docs/reviews/claude-code-stage-327-plan-review.md` if Claude Code returns
    usable output
  - `docs/reviews/opencode-stage-327-plan-review-prompt.md` and
    `docs/reviews/opencode-stage-327-plan-review.md` if fallback is needed
  - `docs/reviews/opencode-stage-327-plan-rereview-prompt.md` and
    `docs/reviews/opencode-stage-327-plan-rereview.md` if the plan changes after
    findings
  - `docs/reviews/claude-code-stage-327-code-review-prompt.md`
  - `docs/reviews/claude-code-stage-327-code-review.md` if Claude Code returns
    usable output
  - `docs/reviews/opencode-stage-327-code-review-prompt.md` and
    `docs/reviews/opencode-stage-327-code-review.md` if fallback is needed

## Task 1: Add Saved Signal Index Builder With Tests

**Files:**
- Create: `tests/test_row_one_saved_signal_index.py`
- Create: `src/fashion_radar/row_one/saved_signal_index.py`

- [ ] **Step 1: Write failing builder tests**

Create `tests/test_row_one_saved_signal_index.py` with local fixtures mirroring
`tests/test_row_one_saved_article_library.py`: `_story()`, `_edition()`,
`_article()`, `_section()`, and `_item()`.

Include this first behavior test:

```python
def test_saved_signal_index_groups_references_and_builds_support_links() -> None:
    story_a = _story("the-row-a-1234567890", "The Row signal", section_key="top_stories")
    story_b = _story("the-row-b-1234567890", "Second Row signal", section_key="brand_moves")

    index = build_row_one_saved_signal_index(
        _edition(story_a, story_b),
        {
            story_a.id: _article(
                story_a.id,
                source_name="Vogue Business",
                paragraphs=["The Row paragraph.", "Margaux paragraph."],
                content_sections=[
                    _section(
                        "entities",
                        "People & Brands",
                        items=[
                            _item(
                                "The Row",
                                body="The Row appears in the saved text.",
                                paragraph_indices=[0],
                                references=[
                                    RowOneReference(
                                        name="The Row",
                                        type="brand",
                                        label="tracked",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
            story_b.id: _article(
                story_b.id,
                source_name="WWD",
                paragraphs=["The Row second paragraph."],
                content_sections=[
                    _section(
                        "product_signals",
                        "Products",
                        items=[
                            _item(
                                "Margaux",
                                body="The Row Margaux is mentioned.",
                                paragraph_indices=[0],
                                references=[
                                    RowOneReference(
                                        name=" the row ",
                                        type="brand",
                                        label="brand",
                                    ),
                                    RowOneReference(
                                        name="Margaux",
                                        type="product",
                                        label="bag",
                                    ),
                                ],
                            )
                        ],
                    )
                ],
            ),
        },
    )

    assert index is not None
    assert index.signal_count == 2
    assert index.supporting_article_count == 2
    assert index.source_count == 2
    assert index.supporting_paragraph_count == 3
    assert [entry.name for entry in index.entries] == ["The Row", "Margaux"]
    row_entry = index.entries[0]
    assert row_entry.type == "brand"
    assert row_entry.label == "tracked"
    assert row_entry.article_count == 2
    assert row_entry.source_count == 2
    assert row_entry.supporting_paragraph_count == 2
    assert [support.title.en for support in row_entry.supports] == [
        "The Row signal",
        "Second Row signal",
    ]
    assert row_entry.supports[0].section_path == (
        "details/the-row-a-1234567890.html#local-article-content-section-1"
    )
    assert row_entry.supports[0].paragraph_links[0].href == (
        "details/the-row-a-1234567890.html#local-article-paragraph-1"
    )
```

Add these additional tests with the following exact purposes:

- `test_saved_signal_index_filters_unsafe_or_unusable_articles`: create one
  valid story, one story with `detail_path="../outside.html"`, a mismatched
  local article, an outside-the-edition local article, a blank-paragraph local
  article, and a blank-reference local article. Assert the builder returns
  `None` unless the valid current-edition article has a nonblank reference.
- `test_saved_signal_index_filters_invalid_paragraph_indices`: create a content
  item with paragraph indices including `True`, `False`, `-1`, `0`, `1`, `2`,
  duplicate `2`, and `99`, with paragraph `1` blank. Assert only indices `0`
  and `2` produce links and that `0` maps to `#local-article-paragraph-1`.
- `test_strict_valid_saved_signal_paragraph_indices_rejects_bool_and_string_values`:
  call `_strict_valid_saved_signal_paragraph_indices()` directly with raw object
  values `[True, False, -1, 0, 0, 1, "2", 2, 99]` and rendered indices `{0, 2}`;
  assert the result is `(0, 2)`.
- `test_saved_signal_index_keeps_same_name_different_types_separate`: create
  `RowOneReference(name="Margaux", type="brand")` and
  `RowOneReference(name="Margaux", type="product")`; assert they produce two
  entries while whitespace/case variants of the same name/type merge.
- `test_saved_signal_index_caps_entries_supports_and_paragraph_links`: create
  more than twelve references, more than four supporting stories for one
  reference, and more than three valid paragraph indices per support; assert the
  caps are enforced.
- `test_saved_signal_index_never_derives_hrefs_from_display_strings`: create
  hostile reference names, labels, article titles, and source names containing
  `../`, `#bad-fragment`, and `<script>`; assert every emitted href still uses
  only `details/<safe-story-id>.html` plus fixed section/paragraph fragments.

- [ ] **Step 2: Run builder tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py -q
```

Expected: fail with `ModuleNotFoundError` or missing
`build_row_one_saved_signal_index`.

- [ ] **Step 3: Implement `saved_signal_index.py`**

Create `src/fashion_radar/row_one/saved_signal_index.py` with this public shape:

```python
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from fashion_radar.row_one.articles import safe_local_article_story_id
from fashion_radar.row_one.detail_routes import is_safe_row_one_detail_path
from fashion_radar.row_one.models import (
    LocalizedText,
    RowOneEdition,
    RowOneLocalArticle,
    RowOneLocalArticleContentItem,
    RowOneLocalArticleContentSection,
)

MAX_SAVED_SIGNAL_INDEX_ENTRIES = 12
MAX_SAVED_SIGNAL_INDEX_SUPPORTS = 4
MAX_SAVED_SIGNAL_INDEX_PARAGRAPH_LINKS = 3

LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_PREFIX = "local-article-content-section"
LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX = "local-article-paragraph"


@dataclass(frozen=True)
class RowOneSavedSignalIndexParagraphLink:
    label: LocalizedText
    href: str


@dataclass(frozen=True)
class RowOneSavedSignalIndexSupport:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    content_section_title: LocalizedText
    section_path: str
    paragraph_links: tuple[RowOneSavedSignalIndexParagraphLink, ...] = ()


@dataclass(frozen=True)
class RowOneSavedSignalIndexEntry:
    name: str
    type: str
    label: str
    article_count: int
    source_count: int
    supporting_paragraph_count: int
    supports: list[RowOneSavedSignalIndexSupport]


@dataclass(frozen=True)
class RowOneSavedSignalIndex:
    signal_count: int
    supporting_article_count: int
    source_count: int
    supporting_paragraph_count: int
    entries: list[RowOneSavedSignalIndexEntry]
```

Implementation requirements:

- Iterate `edition.stories`.
- Skip missing articles.
- Skip `article.story_id != story.id`.
- Skip unsafe story ids and unsafe `story.detail_path`.
- Skip articles without nonblank paragraphs.
- Iterate `article.content_sections` with one-based section positions.
- Iterate every item reference.
- Normalize the key as `(normalized_name, normalized_type)`.
- Trim display name/type/label; fallback type/label to `signal`.
- Use strict paragraph index filtering:

```python
def _strict_valid_saved_signal_paragraph_indices(
    paragraph_indices: Iterable[object],
    rendered_indices: set[int],
) -> tuple[int, ...]:
    valid: list[int] = []
    seen: set[int] = set()
    for index in paragraph_indices:
        if isinstance(index, bool) or not isinstance(index, int):
            continue
        if index not in rendered_indices:
            continue
        if index in seen:
            continue
        seen.add(index)
        valid.append(index)
    return tuple(valid)
```

- Preserve first appearance in edition order.
- Count unique article ids and source names per entry.
- Count top-level `supporting_article_count` and `source_count` as distinct
  current-edition articles and sources across all entries.
- Count top-level `supporting_paragraph_count` as the sum of per-entry
  supporting paragraph counts; the same paragraph URL can count once for each
  signal entry that references it.
- Build at most one support row per story for each signal entry. If the same
  signal appears in multiple content sections in one story, use the first
  matching content section and collect/dedupe paragraph links from matching
  items inside that section.
- Cap final `entries`, `supports`, and `paragraph_links`.
- Return `None` when there are no entries.

- [ ] **Step 4: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py -q
```

Expected: all builder tests pass.

## Task 2: Render Saved Signal Index In `articles/index.html`

**Files:**
- Modify: `src/fashion_radar/row_one/render.py`
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing render tests**

Add tests to `tests/test_row_one_render.py`:

Create
`test_render_row_one_site_includes_saved_signal_index_in_article_library(tmp_path)`.

Assertions:

- `articles/index.html` exists.
- HTML contains `Saved Signal Index` and `本地信号索引`.
- HTML contains counts like `2 saved signals`, `2 supporting articles`,
  `2 sources`, and `2 supporting paragraphs`.
- HTML contains escaped reference/source/story strings.
- HTML contains
  `href="../details/the-row-signal-1234567890.html#local-article-content-section-1"`.
- HTML contains
  `href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"`.
- Homepage entry copy contains `signals or sources` / `信号或来源`.
- `edition.json`, `manifest.json`, and `runtime.json` do not contain:
  `saved_signal_index`, `signal_index`, `entity_index`, `brand_index`,
  `product_index`, `saved-signal-index`, `Saved Signal Index`, or `本地信号索引`.
- No saved signal index JSON sidecar exists.

Add:

Create
`test_render_row_one_site_omits_saved_signal_index_without_references(tmp_path)`.

Assertions:

- `articles/index.html` can still exist when the article library exists.
- HTML does not contain `saved-signal-index`, `Saved Signal Index`, or
  `本地信号索引` when local articles have no usable references.
- Homepage HTML keeps source-only library-entry copy and does not contain
  `signals or sources` or `信号或来源`.

Add:

Create `test_row_one_css_includes_saved_signal_index_styles()`.

Assertions should check every selector listed in the spec.

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_site_includes_saved_signal_index_in_article_library \
  tests/test_row_one_render.py::test_render_row_one_site_omits_saved_signal_index_without_references \
  tests/test_row_one_render.py::test_row_one_css_includes_saved_signal_index_styles \
  -q
```

Expected: fail because render integration and CSS do not exist yet.

- [ ] **Step 3: Wire builder into render flow**

In `src/fashion_radar/row_one/render.py`:

- Import `RowOneSavedSignalIndex` and `build_row_one_saved_signal_index`.
- Build `saved_signal_index` beside `saved_article_library`.
- Pass `saved_signal_index` to `render_index_html()`.
- Pass `saved_signal_index` into `_write_saved_article_library_page()`.
- Update `_write_saved_article_library_page()` signature and call
  `render_saved_article_library_html(edition, saved_article_library, saved_signal_index=saved_signal_index)`.

Do not add to `GENERATED_CHILDREN`.

- [ ] **Step 4: Render signal index HTML**

In `src/fashion_radar/row_one/templates.py`:

- Import the new dataclasses.
- Add `saved_signal_index: RowOneSavedSignalIndex | None = None` to
  `render_index_html()`.
- Add `saved_signal_index: RowOneSavedSignalIndex | None = None` to
  `render_saved_article_library_html()`.
- Compute:

```python
signal_index = _render_saved_signal_index(saved_signal_index)
```

- Insert `{signal_index}` after the library hero and before
  `<div class="saved-article-library-grid">`.
- Update `_render_saved_article_library_entry()` copy:
  - English when `saved_signal_index is not None`: `Browse saved local articles by signals or sources.`
  - Chinese: `按信号或来源浏览本地保存文章。`
- Keep the existing source-only copy when `saved_signal_index is None`.
- Pass `saved_signal_index` into `render_index_html()` solely to drive this
  conditional homepage entry copy.
- Add helpers:

Helper signatures to add:

- `def _render_saved_signal_index(index: RowOneSavedSignalIndex | None) -> str`
- `def _render_saved_signal_index_metrics(index: RowOneSavedSignalIndex) -> str`
- `def _render_saved_signal_index_card(entry: RowOneSavedSignalIndexEntry) -> str`
- `def _render_saved_signal_index_support(support: RowOneSavedSignalIndexSupport) -> str`
- `def _safe_saved_signal_section_href(href: object) -> str | None`
- `def _safe_saved_signal_paragraph_href(href: object) -> str | None`

Safety rules:

- Validate section hrefs by splitting `path#fragment`, validating `path` with
  `validated_row_one_detail_relative_path()`, validating `fragment` with the
  existing `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE`, and returning
  `f"{safe_path}#{fragment}"`. Mirror
  `_safe_saved_article_library_paragraph_href()`.
- Validate paragraph hrefs using `validated_row_one_detail_relative_path()` and
  `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE`.
- Prefix safe hrefs with `../` only after validation.
- Escape every displayed value with `_esc()`.

- [ ] **Step 5: Add CSS**

Add compact mobile-safe styles to `row_one_css()`:

- `.saved-signal-index`
- `.saved-signal-index-header`
- `.saved-signal-index-metrics`
- `.saved-signal-index-grid`
- `.saved-signal-index-card`
- `.saved-signal-index-card-header`
- `.saved-signal-index-card-meta`
- `.saved-signal-index-support`
- `.saved-signal-index-support-row`
- `.saved-signal-index-support-meta`
- `.saved-signal-index-actions`
- `.saved-signal-index-paragraphs`

Include `min-width: 0` and `overflow-wrap: anywhere` on card/header/support
text containers.

- [ ] **Step 6: Run render tests to verify GREEN**

Run the focused render command from Step 2.

Expected: all focused render tests pass.

## Task 3: Contract, Docs, And Review Boundary Tests

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Write failing workflow/docs tests**

In `tests/test_workflows.py`, extend the generated contract sentinel block with:

```python
assert '"saved_signal_index"' not in generated_contract_payload
assert '"signal_index"' not in generated_contract_payload
assert '"entity_index"' not in generated_contract_payload
assert '"brand_index"' not in generated_contract_payload
assert '"product_index"' not in generated_contract_payload
assert '"saved_article_entity_index"' not in generated_contract_payload
assert '"saved_article_brand_index"' not in generated_contract_payload
assert '"saved_article_product_index"' not in generated_contract_payload
assert "saved-signal-index" not in generated_contract_payload
assert "Saved Signal Index" not in generated_contract_payload
assert "本地信号索引" not in generated_contract_payload
assert "saved-signal-index.json" not in generated_contract_payload

saved_signal_index_page = "saved-signal-index" + ".html"
articles_dir = output_dir / "articles"
assert not (output_dir / saved_signal_index_page).exists()
assert not (articles_dir / saved_signal_index_page).exists()
if articles_dir.exists():
    assert {path.name for path in articles_dir.iterdir()} <= {"index.html"}
```

In `tests/test_row_one_docs.py`, add:

```python
def test_row_one_docs_describe_saved_signal_index_boundary() -> None:
    expected = _normalized(
        "Stage 327 adds a generated-site only ROW ONE Saved Signal Index inside "
        "`articles/index.html`; it organizes the current edition's saved local "
        "article references by signal and links back into existing detail-page "
        "local article anchors; it does not change row-one-app/v7, "
        "row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, "
        "source collection, fetching, matching, extraction, scoring, ranking, "
        "LLM, connector, scheduling, deployment, or compliance-review behavior."
    )
    for path in (README, ROW_ONE_DOC):
        normalized = _normalized(_read(path))
        assert expected in normalized
```

Also assert the Stage 327 docs do not include boundary drift:

```python
for path in (README, ROW_ONE_DOC):
    normalized = _normalized(_read(path))
    stage = normalized[
        normalized.index("stage 327 adds a generated-site only row one") : normalized.index(
            "stage 326 adds a generated-site only row one"
        )
    ]
    for phrase in (
        "row-one-app/v8",
        "adds source collection",
        "adds fetching",
        "adds matching",
        "adds extraction",
        "adds scoring",
        "adds ranking",
        "adds llm calls",
        "adds connectors",
        "adds scheduling",
        "adds deployment behavior",
        "adds compliance review",
    ):
        assert phrase not in stage
```

- [ ] **Step 2: Run docs/workflow tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  -q
```

Expected: fail until docs are updated.

- [ ] **Step 3: Update README and docs**

Add the exact Stage 327 boundary paragraph to both `README.md` and
`docs/row-one.md` near Stage 326:

```markdown
Stage 327 adds a generated-site only ROW ONE Saved Signal Index inside
`articles/index.html`; it organizes the current edition's saved local article
references by signal and links back into existing detail-page local article
anchors; it does not change row-one-app/v7, row-one-manifest/v1,
row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching,
matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment,
or compliance-review behavior.
```

Do not add a new generated file inventory item because Stage 327 does not create
a new page or directory.

- [ ] **Step 4: Run docs/workflow tests to verify GREEN**

Run the command from Step 2.

Expected: tests pass.

## Task 4: Plan Review Gate Before Implementation

**Files:**
- Create: `docs/reviews/claude-code-stage-327-plan-review-prompt.md`
- Create fallback files if needed under `docs/reviews/`

- [ ] **Step 1: Create Claude Code plan review prompt**

Create `docs/reviews/claude-code-stage-327-plan-review-prompt.md` with:

- Stage 327 goal and scope.
- Link to spec and plan.
- Explicit boundaries:
  - generated-site only
  - no app/runtime/manifest/schema/JSON changes
  - no source/fetching/extraction/scoring/ranking/LLM/connector/scheduling/
    deployment/compliance behavior
- Ask Claude Code to review feasibility, scope containment, and tests; ask
  whether the embedded `articles/index.html` approach is feasible, whether
  no-child-page containment is adequately tested, and explicitly state not to
  propose a separate generated child page for Stage 327.

- [ ] **Step 2: Request Claude Code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --bare --effort max --permission-mode plan --no-session-persistence \
  --allowedTools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-327-plan-review-prompt.md)" > "$tmp_review"
```

If Claude Code returns usable Critical/Important/Minor findings, save it to
`docs/reviews/claude-code-stage-327-plan-review.md`.

- [ ] **Step 3: Fallback to opencode when needed**

If Claude Code times out or returns only an API error, create
`docs/reviews/opencode-stage-327-plan-review-prompt.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-327-plan-review-prompt.md)" > /tmp/opencode-stage-327-plan-review.raw
```

Save only the coherent review body to
`docs/reviews/opencode-stage-327-plan-review.md`. Do not commit timeout logs or
tool chatter as review output.

- [ ] **Step 4: Fix plan Critical/Important findings**

If review reports Critical or Important findings, update the spec and plan,
create a rereview prompt, and request rereview until Critical and Important are
clear.

## Task 5: Final Implementation Review, Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-327-code-review-prompt.md`
- Create fallback review files if needed

- [ ] **Step 1: Run focused and full verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
if git grep -n -E 'ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' -- . ':!docs/reviews/*'; then exit 1; else exit 0; fi
```

Expected: all commands exit 0 and the secret scan prints no matches.

- [ ] **Step 2: Request code review**

Create `docs/reviews/claude-code-stage-327-code-review-prompt.md` with the Stage
327 goal, spec, plan, implementation summary, and verification results. Request
Claude Code review with max effort. If Claude Code is unavailable, use opencode
`glm-5.2` fallback and save only a coherent completed review body.

- [ ] **Step 3: Fix Critical/Important findings**

If the review reports Critical or Important findings, fix them with TDD where
behavior changes are needed, rerun focused and relevant full checks, and
rerequest review until Critical and Important are clear.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short --branch
git add README.md docs/row-one.md \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  src/fashion_radar/row_one/saved_signal_index.py \
  tests/test_row_one_saved_signal_index.py \
  tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py \
  docs/superpowers/specs/2026-07-07-stage-327-row-one-saved-signal-index-design.md \
  docs/superpowers/plans/2026-07-07-stage-327-row-one-saved-signal-index-plan.md \
  docs/reviews/claude-code-stage-327-plan-review-prompt.md \
  docs/reviews/claude-code-stage-327-plan-review.md \
  docs/reviews/opencode-stage-327-plan-review-prompt.md \
  docs/reviews/opencode-stage-327-plan-review.md \
  docs/reviews/opencode-stage-327-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-327-plan-rereview.md \
  docs/reviews/claude-code-stage-327-code-review-prompt.md \
  docs/reviews/claude-code-stage-327-code-review.md \
  docs/reviews/opencode-stage-327-code-review-prompt.md \
  docs/reviews/opencode-stage-327-code-review.md
git commit -m "Stage 327: add row one saved signal index"
git push origin main
git status --short --branch
git ls-remote origin refs/heads/main
```

If some fallback review files were not needed, omit them from `git add`.

## Self-Review Checklist

- Spec coverage: builder, render section, homepage copy, docs, workflow boundary,
  review gate, verification, commit, and push are covered.
- No new top-level generated child is planned.
- JSON contracts remain unchanged.
- The plan uses TDD: tests are written and run red before implementation.
- Review gate occurs before production implementation.
- No placeholders remain.
