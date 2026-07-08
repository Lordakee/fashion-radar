# Stage 351 Saved Article Organization Jump Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generated-site-only organization jump index that gives readers compact same-page navigation across existing saved article content, source, and signal surfaces.

**Architecture:** Build a small in-memory view model from already-built saved article page surfaces, then render it only in `articles/index.html`. The index uses safe same-page anchors and existing counts; it does not inspect raw article text, create new artifacts, change app contracts, or add ranking/analytics behavior.

**Tech Stack:** Python 3.12, existing ROW ONE dataclasses, HTML string rendering in `templates.py`, pytest, ruff, uv.

---

## File Structure

- Create `src/fashion_radar/row_one/saved_article_organization_jump_index.py`
  - Add constants:
    - `SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_GROUP_LIMIT = 3`
    - `SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT = 4`
  - Add frozen dataclasses:
    - `RowOneSavedArticleOrganizationJumpIndex`
    - `RowOneSavedArticleOrganizationJumpIndexGroup`
    - `RowOneSavedArticleOrganizationJumpIndexItem`
  - Add builder:
    - `build_row_one_saved_article_organization_jump_index(...)`
  - Build content, source, and signal navigation groups from existing local view models and concrete source-route anchors.
- Modify `src/fashion_radar/row_one/render.py`
  - Pass the Stage 349/350 surfaces through to `_write_saved_article_library_page(...)`; the final jump index should be built in the library template path after source routes are derived.
- Modify `src/fashion_radar/row_one/templates.py`
  - Accept the typed jump index in `render_saved_article_library_html(...)`.
  - Add `_render_saved_article_organization_jump_index(...)`.
  - Add CSS selectors for the new section, groups, items, labels, and counts.
  - Render after saved article daily summary and before content organization.
- Add `tests/test_row_one_saved_article_organization_jump_index.py`
  - Cover safe item generation, caps, stable existing-order behavior, empty omission, and same-page href filtering.
- Modify `tests/test_row_one_render.py`
  - Add rendering, placement, escaping, homepage absence, empty-shell, and CSS selector coverage.
- Modify `tests/test_workflows.py`
  - Add Stage 351 generated-site-only guards and forbidden artifact assertions.
- Modify `tests/test_row_one_docs.py`
  - Add Stage 351 boundary documentation guard.
- Modify `README.md` and `docs/row-one.md`
  - Add one concise Stage 351 boundary paragraph before Stage 350.
- Add `docs/reviews/claude-code-stage-351-plan-review-prompt.md`.
- Add `docs/reviews/opencode-stage-351-plan-review-prompt.md`.

## Task 1: Write Failing Builder Tests

**Files:**
- Create: `tests/test_row_one_saved_article_organization_jump_index.py`

- [ ] **Step 1: Add fixtures from existing Stage 346-350 dataclasses**

Create local helpers that build minimal content organization, source routes,
signal facets, and daily leaderboard objects. Use same-page anchors only:

```python
from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
    RowOneSavedArticleContentOrganizationCard,
    RowOneSavedArticleContentOrganizationGroup,
)
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    RowOneSavedArticleDailySignalLeaderboard,
    RowOneSavedArticleDailySignalLeaderboardBucket,
    RowOneSavedArticleDailySignalLeaderboardItem,
)
from fashion_radar.row_one.saved_article_organization_jump_index import (
    SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT,
    build_row_one_saved_article_organization_jump_index,
)
from fashion_radar.row_one.saved_article_signal_facets import (
    RowOneSavedArticleSignalFacets,
)


def _lt(en: str, zh: str | None = None) -> LocalizedText:
    return LocalizedText(en=en, zh=zh or en)
```

- [ ] **Step 2: Add the main aggregation/navigation test**

Add a test named:

```python
def test_build_saved_article_organization_jump_index_links_existing_surfaces() -> None:
    ...
```

The test should build:

- a content organization with two groups and card counts;
- source route item inputs with at least one concrete per-source same-page anchor;
- a signal facets object with nonzero row, brand, product, and theme counts;
- a daily signal leaderboard with at least one bucket and one item.

Assert:

```python
index = build_row_one_saved_article_organization_jump_index(
    content_organization=content_organization,
    source_routes=source_routes,
    signal_facets=signal_facets,
    daily_signal_leaderboard=daily_signal_leaderboard,
)

assert index is not None
assert [group.key for group in index.groups] == ["content", "sources", "signals"]
assert index.item_count >= 4
assert index.groups[0].items[0].href == "#saved-article-content-organization"
assert index.groups[1].items[0].href == "#saved-article-source-vogue-business"
assert index.groups[2].items[0].href == "#saved-article-signal-facets"
assert index.groups[2].items[1].href == "#saved-article-daily-signal-leaderboard"
```

Expected before implementation: import or name failure because the module does
not exist.

- [ ] **Step 3: Add caps, empty, and href safety tests**

Add tests that assert:

```python
assert len(index.groups[0].items) <= SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT
assert build_row_one_saved_article_organization_jump_index(
    content_organization=None,
    source_routes=(),
    signal_facets=None,
    daily_signal_leaderboard=None,
) is None
assert all(item.href.startswith("#") for group in index.groups for item in group.items)
assert not any("http" in item.href for group in index.groups for item in group.items)
```

Also add a partial-empty test where only `daily_signal_leaderboard` is present
and assert the index contains only the `signals` group.

- [ ] **Step 4: Run tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_organization_jump_index.py -q
```

Expected: FAIL because `fashion_radar.row_one.saved_article_organization_jump_index` is missing.

## Task 2: Implement The Jump Index Builder

**Files:**
- Create: `src/fashion_radar/row_one/saved_article_organization_jump_index.py`

- [ ] **Step 1: Add dataclasses and constants**

Implement:

```python
from __future__ import annotations

from dataclasses import dataclass

from fashion_radar.row_one.models import LocalizedText
from fashion_radar.row_one.saved_article_content_organization import (
    RowOneSavedArticleContentOrganization,
)
from fashion_radar.row_one.saved_article_daily_signal_leaderboard import (
    RowOneSavedArticleDailySignalLeaderboard,
)
from fashion_radar.row_one.saved_article_signal_facets import RowOneSavedArticleSignalFacets

SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_GROUP_LIMIT = 3
SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT = 4


@dataclass(frozen=True)
class RowOneSavedArticleOrganizationJumpIndexSourceRoute:
    label: LocalizedText
    href: str
    article_count: int


@dataclass(frozen=True)
class RowOneSavedArticleOrganizationJumpIndexItem:
    label: LocalizedText
    href: str
    count_label: LocalizedText


@dataclass(frozen=True)
class RowOneSavedArticleOrganizationJumpIndexGroup:
    key: str
    title: LocalizedText
    items: tuple[RowOneSavedArticleOrganizationJumpIndexItem, ...]


@dataclass(frozen=True)
class RowOneSavedArticleOrganizationJumpIndex:
    group_count: int
    item_count: int
    groups: tuple[RowOneSavedArticleOrganizationJumpIndexGroup, ...]
```

- [ ] **Step 2: Add builder logic**

Implement `build_row_one_saved_article_organization_jump_index(...)` with this
behavior:

- content group:
  - one item for the full content organization section when content groups exist;
  - label `Content Organization` / `内容组织`;
  - href `#saved-article-content-organization`;
  - count label from number of groups.
- sources group:
  - one item per safe source route up to the item cap;
  - use the source route label;
  - use the concrete source route href such as `#saved-article-source-vogue-business`;
  - count label from the source route article count.
- signals group:
  - one item for `Signal Facets` when `signal_facets` has rows;
  - one item for `Daily Signal Leaderboard` when the leaderboard has items;
  - existing anchors only.

Return `None` when all groups are empty. Cap each group at
`SAVED_ARTICLE_ORGANIZATION_JUMP_INDEX_ITEM_LIMIT`. Reject source route hrefs
that do not start with `#saved-article-source-`.

- [ ] **Step 3: Run builder tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_organization_jump_index.py -q
```

Expected: PASS.

## Task 3: Wire Render Pipeline And Template

**Files:**
- Modify: `src/fashion_radar/row_one/templates.py`
- Modify: `tests/test_row_one_render.py`

- [ ] **Step 1: Write failing render tests**

Add tests that assert:

```python
assert 'class="saved-article-organization-jump-index"' in library_html
assert library_html.index('class="saved-article-daily-summary"') < library_html.index(
    'class="saved-article-organization-jump-index"'
)
assert library_html.index('class="saved-article-organization-jump-index"') < library_html.index(
    'class="saved-article-content-organization"'
)
assert 'class="saved-article-organization-jump-index"' not in homepage_html
assert 'href="#saved-article-source-vogue-business"' in section_html
assert 'href="#saved-article-signal-facets"' in section_html
assert 'href="#saved-article-daily-signal-leaderboard"' in section_html
```

Add an escaping test with labels containing `<script>` and assert escaped text
is present while raw script text is not.

Add an empty-shell test where `saved_article_organization_jump_index=None` and
an empty index object both omit the section.

Add a target-id test for the rendered article library page:

```python
jump_hrefs = re.findall(
    r'class="saved-article-organization-jump-index-link" href="#([^"]+)"',
    library_html,
)
assert jump_hrefs
for target_id in jump_hrefs:
    assert f'id="{target_id}"' in library_html
```

Add a detail-page absence test that renders at least one detail article page and
asserts `saved-article-organization-jump-index` is not present.

- [ ] **Step 2: Run render tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "organization_jump_index"
```

Expected: FAIL because template support is missing.

- [ ] **Step 3: Build with real source route anchors in the library template path**

Import the builder and source-route input dataclass into `templates.py`. Reuse
the existing `_saved_article_source_routes(library.groups)` result already
computed inside `render_saved_article_library_html(...)`, convert each route
into a jump-index source route with `href=f"#{route.anchor_id}"`, and build the
jump index in that template path after all rendered surface strings are known.

Do not hardcode or create `#saved-article-source-routes`; the existing wrapper
has no id. Source jump links must target concrete per-source anchors already
assigned to `.saved-article-library-source` sections.

- [ ] **Step 4: Render template and CSS**

Add `_render_saved_article_organization_jump_index(...)` and helper functions.
The renderer should:

- return an empty string for `None`, empty groups, or empty items;
- escape labels and count labels;
- accept only hrefs that target a known rendered same-page id;
- render no outbound links.

Add CSS near the saved article organization sections.

- [ ] **Step 5: Run render tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "organization_jump_index or saved_article_daily_signal_leaderboard"
```

Expected: PASS.

## Task 4: Add Workflow And Documentation Guards

**Files:**
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_row_one_docs.py`
- Modify: `README.md`
- Modify: `docs/row-one.md`

- [ ] **Step 1: Add failing workflow guard**

In `tests/test_workflows.py`, add a thin wrapper:

```python
def test_stage_351_saved_article_organization_jump_index_stays_generated_site_only(
    tmp_path: Path,
) -> None:
    test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)
```

Extend the generated contract payload denylist with:

```python
assert "saved_article_organization_jump_index" not in generated_contract_payload
assert "organization_jump_index" not in generated_contract_payload
assert "local_article_organization" not in generated_contract_payload
assert "article_organization" not in generated_contract_payload
assert "Saved Article Organization Jump Index" not in generated_contract_payload
assert "saved-article-organization-jump-index" not in generated_contract_payload
assert "local-article-organization" not in generated_contract_payload
assert "article-organization" not in generated_contract_payload
```

Extend forbidden artifact checks for root, `articles/`, and `data/` variants of:

- `saved-article-organization-jump-index.json/html`
- `organization-jump-index.json/html`
- `local-article-organization.json/html`
- `article-organization.json/html`

- [ ] **Step 2: Add failing docs guard**

In `tests/test_row_one_docs.py`, add:

```python
def test_row_one_docs_describe_stage_351_saved_article_organization_jump_index_boundary() -> None:
    for doc in (README_TEXT, ROW_ONE_DOC_TEXT):
        assert "Stage 351" in doc
        assert "Saved Article Organization Jump Index" in doc
        assert "generated-site only" in doc
        assert "articles/index.html" in doc
        assert "data/saved-article-organization-jump-index.json" in doc
        assert "row-one-app/v7" in doc
        assert "compliance-review behavior" in doc
```

- [ ] **Step 3: Run guard tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q -k "stage_351 or organization_jump_index"
```

Expected: FAIL until docs and guards are implemented.

- [ ] **Step 4: Add documentation boundary paragraphs**

Add one paragraph near Stage 350 in `README.md` and `docs/row-one.md`:

```text
Stage 351 adds generated-site only Saved Article Organization Jump Index inside `articles/index.html`; it reuses existing local saved article content organization, existing source routes, existing signal facets, existing daily signal leaderboard data, and existing same-page saved article anchors to provide compact navigation across local saved article surfaces without changing app-facing contracts; it does not create `data/saved-article-organization-jump-index.json`, does not create `data/local-article-organization.json`, does not create new article-source sidecars, does not create new route families, does not publish full articles on the library index, does not add outbound article URLs as primary navigation, does not change row-one-app/v7, row-one-manifest/v1, row-one-runtime/v1, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, analytics, personalization, recommendation, or compliance-review behavior.
```

- [ ] **Step 5: Run guard tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py tests/test_row_one_docs.py -q -k "stage_351 or organization_jump_index"
```

Expected: PASS.

## Task 5: Review, Full Verification, And Commit

**Files:**
- All Stage 351 files.

- [ ] **Step 1: Run focused Stage 351 tests**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_organization_jump_index.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q -k "organization_jump_index or stage_351"
```

Expected: PASS.

- [ ] **Step 2: Run full quality gate**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check
git diff --check
```

Expected: all commands pass.

- [ ] **Step 3: Commit**

Run:

```bash
git status --short
git add src/fashion_radar/row_one/saved_article_organization_jump_index.py \
  src/fashion_radar/row_one/render.py \
  src/fashion_radar/row_one/templates.py \
  tests/test_row_one_saved_article_organization_jump_index.py \
  tests/test_row_one_render.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py \
  README.md docs/row-one.md \
  docs/superpowers/specs/2026-07-08-stage-351-saved-article-organization-jump-index-design.md \
  docs/superpowers/plans/2026-07-08-stage-351-saved-article-organization-jump-index-plan.md \
  docs/reviews/claude-code-stage-351-plan-review-prompt.md \
  docs/reviews/opencode-stage-351-plan-review-prompt.md
git commit -m "Stage 351: add saved article organization jump index"
```

Expected: commit succeeds with only Stage 351 changes.
