# Stage 375 Local Article Content Health Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. REQUIRED PROJECT GATE: submit this plan for Claude Code review with `--effort max` before implementation; after Claude Code's plan review, run local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar`.

**Goal:** Add read-only Local Article Content Health so ROW ONE detects generated sites where saved local article sidecars exist but article pages lack the local article section, saved-body container, paragraph anchors, or content-section anchors.

**Architecture:** Add one pure analyzer module that checks existing generated site files and returns a small dataclass/payload. Add a shared local article anchor/helper module so status integrity and content health use the same anchor constants and HTML id parser. Integrate content health into strict `row-one status` validation alongside Stage 374 route health, and into read-only `row-one ops-check` diagnostics without changing generated app/runtime/manifest JSON contracts or rendering new page sections.

**Tech Stack:** Python 3, dataclasses, pathlib, `html.parser.HTMLParser`, existing ROW ONE `RowOneLocalArticle` models, Typer CLI, pytest, ruff, uv with `UV_NO_CONFIG=1 uv --no-config`.

---

## File Structure

- Create `src/fashion_radar/row_one/local_article_anchors.py`
  - Owns local article anchor constants, one-based anchor builders, and shared HTML id parsing.
- Create `src/fashion_radar/row_one/local_article_content_health.py`
  - Owns `RowOneLocalArticleContentHealth`, analyzer, payload conversion, and strict validator.
- Create `tests/test_row_one_local_article_content_health.py`
  - Analyzer and validator tests.
- Modify `src/fashion_radar/row_one/status_integrity.py`
  - Imports shared anchor constants/HTML id parser.
  - Computes content health from already validated current sidecars and validates it after route health.
- Modify `src/fashion_radar/cli.py`
  - Adds CLI-only `local_article_content` status payload and human output line.
  - Adds ops-check human output line.
- Modify `src/fashion_radar/row_one/ops_check.py`
  - Adds read-only content health payload, status influence, and refresh action.
- Modify `tests/test_row_one_cli.py`
  - Adds status JSON and strict-failure tests.
- Modify `tests/test_row_one_ops_check.py`
  - Adds ops-check JSON/status/action/human output coverage.
- Modify `README.md` and `docs/row-one.md`
  - Adds exact Stage 375 boundary paragraph before Stage 374.
- Modify `tests/test_row_one_docs.py`
  - Adds exact Stage 375 paragraph, ordering assertion, and stale phrase guard.
- Modify `tests/test_workflows.py`
  - Adds app-contract denylist, artifact denylist, and generated-site-only read-only guard.
- Add review artifacts under `docs/reviews/`
  - `claude-code-stage-375-plan-review.md`
  - `claude-code-stage-375-plan-rereview.md`
  - `opencode-stage-375-plan-review.md`
  - `claude-code-stage-375-code-review.md`
  - `opencode-stage-375-code-review.md`

## Core Product Gap Closed

Stage 374 verifies that saved local article routes are present and linked. Stage 375 verifies that those generated article pages contain the actual local reading anchors needed for the user to read downloaded/saved article content locally.

## Parallel Execution Shape After Plan Review

Use parallel workers only with disjoint write scopes:

- Worker A: `src/fashion_radar/row_one/local_article_anchors.py`, `src/fashion_radar/row_one/local_article_content_health.py`, and `tests/test_row_one_local_article_content_health.py`.
- Worker B: `src/fashion_radar/row_one/status_integrity.py`, `src/fashion_radar/cli.py`, and `tests/test_row_one_cli.py`.
- Worker C: `src/fashion_radar/row_one/ops_check.py`, `src/fashion_radar/cli.py`, and `tests/test_row_one_ops_check.py`.
- Worker D: `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`, and `tests/test_workflows.py`.

Workers must not revert edits made by others and must adjust to existing changes when integrating. Workers B and C both touch `src/fashion_radar/cli.py`; do not run those two edits concurrently unless their patches are coordinated by the controller.
Workers B and C also import the new modules from Worker A, so they should start
after Task 3 lands even if their final write scopes are otherwise separate.

---

### Task 1: Plan Review Gate

**Files:**
- Create: `docs/reviews/claude-code-stage-375-plan-review.md`
- Create: `docs/reviews/claude-code-stage-375-plan-rereview.md`
- Create: `docs/reviews/opencode-stage-375-plan-review.md`

- [ ] **Step 1: Request Claude Code plan review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 375 Local Article Content Health plan/spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-10-stage-375-local-article-content-health-design.md and docs/superpowers/plans/2026-07-10-stage-375-local-article-content-health-plan.md. Goal: detect generated ROW ONE sites where saved local article sidecars exist but articles/<story-id>.html lacks id=local-article, id=local-article-body, expected paragraph anchors, or expected local content-section anchors. Technical stack: Python dataclasses, pathlib, HTMLParser, existing ROW ONE RowOneLocalArticle models, Typer CLI, pytest, ruff, uv. Implementation method: pure read-only content health analyzer, shared local article anchor constants/HTML id parser, strict status_integrity validation using already validated sidecars, CLI-only row-one status --json local_article_content field, ops-check diagnostic field/action, no generated JSON artifacts or app/runtime/manifest contract changes. Check feasibility, anchor correctness, read-only behavior, generated-site-only boundaries, app-contract/artifact leakage risk, duplication with existing local article stages, and test plan. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-375-plan-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 2: Request opencode plan review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 375 Local Article Content Health plan/spec in /home/ubuntu/fashion-radar. Read docs/superpowers/specs/2026-07-10-stage-375-local-article-content-health-design.md and docs/superpowers/plans/2026-07-10-stage-375-local-article-content-health-plan.md. Also read docs/reviews/claude-code-stage-375-plan-review.md if present and cross-check it. Goal: detect generated ROW ONE sites where saved local article sidecars exist but articles/<story-id>.html lacks id=local-article, id=local-article-body, expected paragraph anchors, or expected local content-section anchors. Technical stack: Python dataclasses, pathlib, HTMLParser, existing ROW ONE RowOneLocalArticle models, Typer CLI, pytest, ruff, uv. Implementation method: pure read-only content health analyzer, shared local article anchor constants/HTML id parser, strict status_integrity validation using already validated sidecars, CLI-only row-one status --json local_article_content field, ops-check diagnostic field/action, no generated JSON artifacts or app/runtime/manifest contract changes. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-375-plan-review.md
rm -f "$tmp_review"
```

Expected: review is saved and contains no live-capture/tool chatter.

- [ ] **Step 3: Fix valid Critical and Important plan findings**

If either review raises Critical or Important issues, update the spec/plan before implementation and run a matching re-review. Do not edit production code until this gate passes.

### Task 2: Analyzer RED Tests

**Files:**
- Create: `tests/test_row_one_local_article_content_health.py`

- [ ] **Step 1: Write failing analyzer tests**

Create tests that import the not-yet-created module:

```python
from fashion_radar.row_one.local_article_content_health import (
    RowOneLocalArticleContentHealth,
    build_row_one_local_article_content_health,
    row_one_local_article_content_health_payload,
    validate_row_one_local_article_content_health,
)
```

Use `RowOneLocalArticle.model_validate(...)` fixtures with:

```python
{
    "story_id": "the-row-signal",
    "url": "https://example.com/the-row-signal",
    "title": "The Row signal",
    "source_name": "Example",
    "extracted_at": "2026-07-10T04:00:00Z",
    "body_source": "extracted",
    "paragraphs": ["First saved paragraph.", "Second saved paragraph."],
    "paragraphs_zh": ["第一段。", "第二段。"],
    "brief_sections": [],
    "content_sections": [
        {
            "key": "brand_signals",
            "title": {"en": "Brand Signals", "zh": "品牌信号"},
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
    ],
}
```

Use helpers:

```python
def _write_article_page(site_dir: Path, story_id: str, html: str) -> None:
    article_dir = site_dir / "articles"
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / f"{story_id}.html").write_text(html, encoding="utf-8")
```

Required test names:

- `test_content_health_is_not_applicable_without_saved_article_sidecars`
- `test_content_health_reports_ready_for_rendered_article_body_and_anchors`
- `test_content_health_reports_missing_local_article_section`
- `test_content_health_reports_missing_body_container`
- `test_content_health_reports_missing_paragraph_anchors_deterministically`
- `test_content_health_reports_missing_content_section_anchors_deterministically`
- `test_content_health_uses_supplied_articles_exactly`
- `test_content_health_payload_is_stable`
- `test_validate_content_health_raises_clear_errors`
- `test_content_health_discovery_ignores_unsafe_sidecar_stems`
- `test_content_health_discovery_ignores_malformed_sidecars`
- `test_content_health_accepts_html_id_attribute_variants`
- `test_content_health_ignores_empty_paragraph_sidecars_without_anchor_expectations`
- `test_validate_content_health_accepts_not_applicable`

Key expectations:

```python
health = build_row_one_local_article_content_health(
    site_dir,
    articles={"the-row-signal": article},
)
assert health.status == "ready"
assert health.article_count == 1
assert health.paragraph_anchor_count == 2
assert health.content_section_anchor_count == 1
assert health.missing_article_sections == ()
assert health.missing_body_containers == ()
assert health.missing_paragraph_anchors == ()
assert health.missing_content_section_anchors == ()
```

Validator failure checks must assert all clear error branches:

```python
with pytest.raises(ValueError, match="local article section is missing"):
    validate_row_one_local_article_content_health(missing_article_section_health)
with pytest.raises(ValueError, match="body container is missing"):
    validate_row_one_local_article_content_health(missing_body_container_health)
with pytest.raises(ValueError, match="paragraph anchor is missing"):
    validate_row_one_local_article_content_health(missing_paragraph_health)
with pytest.raises(ValueError, match="content-section anchor is missing"):
    validate_row_one_local_article_content_health(missing_content_section_health)
validate_row_one_local_article_content_health(not_applicable_health)
```

For `test_content_health_ignores_empty_paragraph_sidecars_without_anchor_expectations`,
use a valid `RowOneLocalArticle` fixture with `paragraphs=[]`, `skipped=True`,
and no `content_sections`; write no article-page HTML and assert:

```python
health = build_row_one_local_article_content_health(
    site_dir,
    articles={"empty-signal": empty_article},
)
assert health.status == "not_applicable"
assert health.article_count == 0
assert health.paragraph_anchor_count == 0
assert health.content_section_anchor_count == 0
assert health.missing_article_sections == ()
assert health.missing_body_containers == ()
assert health.missing_paragraph_anchors == ()
assert health.missing_content_section_anchors == ()
```

- [ ] **Step 2: Run analyzer tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_content_health.py -q
```

Expected: fail with `ModuleNotFoundError: No module named 'fashion_radar.row_one.local_article_content_health'`.

### Task 3: Shared Anchors And Analyzer Implementation

**Files:**
- Create: `src/fashion_radar/row_one/local_article_anchors.py`
- Create: `src/fashion_radar/row_one/local_article_content_health.py`
- Test: `tests/test_row_one_local_article_content_health.py`

- [ ] **Step 1: Implement shared anchor constants and HTML id parser**

Create `src/fashion_radar/row_one/local_article_anchors.py`:

```python
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

LOCAL_ARTICLE_SECTION_ANCHOR = "local-article"
LOCAL_ARTICLE_BODY_CONTAINER_ANCHOR = "local-article-body"
LOCAL_ARTICLE_PARAGRAPH_ANCHOR_PREFIX = "local-article-paragraph-"
LOCAL_ARTICLE_CONTENT_SECTION_ANCHOR_PREFIX = "local-article-content-section-"
```

Implement:

- `local_article_paragraph_anchor(index: int) -> str`
  - Returns `f"{LOCAL_ARTICLE_PARAGRAPH_ANCHOR_PREFIX}{index + 1}"`.
- `local_article_content_section_anchor(position: int) -> str`
  - Returns `f"{LOCAL_ARTICLE_CONTENT_SECTION_ANCHOR_PREFIX}{position}"`.
- `parse_html_ids(html: str) -> set[str]`
  - Parses already-read HTML and returns `id` attributes.
  - Keeps HTMLParser's existing attribute-name normalization behavior, so
    `id`, `ID`, and mixed-case variants are treated consistently.
- `html_ids(path: Path) -> set[str]`
  - Reads UTF-8 HTML and returns `parse_html_ids(...)`.
  - Returns an empty set on `OSError`.

Do not edit `status_integrity.py` in this task; Worker B handles that migration during Task 5 to avoid overlapping write scopes.

- [ ] **Step 2: Implement dataclass, discovery, analyzer, payload, and validator**

Create `src/fashion_radar/row_one/local_article_content_health.py`.

Use the dataclass from the design. Implement:

- `build_row_one_local_article_content_health(site_dir, articles=None)`
- `_resolve_articles(site_dir, articles)`
- `_expected_paragraph_anchor_ids(article)`
- `_expected_content_section_anchor_ids(article)`
- `row_one_local_article_content_health_payload(...)`
- `validate_row_one_local_article_content_health(...)`

Discovery should read only safe `data/articles/*.json` filenames. Invalid JSON or invalid sidecars should not crash the ops discovery path because strict schema enforcement already belongs to `row-one status`; ignore invalid discovered files and let status use the strict already-validated mapping.

Expected paragraph anchors must preserve original one-based paragraph numbering: blank paragraph slots are skipped but do not shift later anchor numbers. Expected content-section anchors must preserve original one-based sidecar `content_sections` positions and include every sidecar content section, matching `_render_local_article_content_sections(...)`.

Content health should evaluate only renderable sidecars with at least one
non-empty saved paragraph. Empty-paragraph sidecars, including skipped sidecars,
do not create local article section, body container, paragraph, or
content-section anchor expectations because the current renderer omits the whole
local article section for them. If no renderable sidecars remain, return
`not_applicable`.

- [ ] **Step 3: Run analyzer tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_content_health.py -q
```

Expected: all analyzer tests pass.

### Task 4: Status Integration RED Tests

**Files:**
- Modify: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add status tests**

Add tests near existing local article route health tests:

- `test_row_one_status_json_includes_local_article_content_health`
- `test_row_one_status_prints_local_article_content_health`
- `test_row_one_status_rejects_missing_local_article_section_anchor`
- `test_row_one_status_rejects_missing_local_article_body_container_anchor`
- `test_row_one_status_rejects_missing_local_article_paragraph_anchor`
- `test_row_one_status_rejects_missing_local_article_content_section_anchor`

The fixture should start from the existing generated ROW ONE site helpers used for route-health status tests, then remove the relevant id from `articles/<story-id>.html`.

Expected JSON fragment:

```python
assert payload["local_article_content"]["status"] == "ready"
assert payload["local_article_content"]["article_count"] == 1
assert payload["local_article_content"]["paragraph_anchor_count"] >= 1
```

- [ ] **Step 2: Run status tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "local_article_content or local_article_route"
```

Expected: new `local_article_content` tests fail because `local_article_content` is not integrated; existing `local_article_route` tests should continue to pass.

### Task 5: Status Integration Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/status_integrity.py`
- Modify: `src/fashion_radar/cli.py`
- Test: `tests/test_row_one_cli.py`

- [ ] **Step 1: Add combined status health return value**

In `status_integrity.py`, add:

```python
@dataclass(frozen=True)
class RowOneGeneratedSiteHealth:
    local_article_routes: RowOneLocalArticleRouteHealth
    local_article_content: RowOneLocalArticleContentHealth
```

Return this object from `validate_row_one_generated_site_integrity(...)` instead of only the route-health object. Build content health using the already validated `article_sidecars` mapping.

Also migrate `status_integrity.py` to import shared local article anchor constants and `parse_html_ids(...)` from `local_article_anchors.py` instead of keeping private `_LOCAL_ARTICLE_FRAGMENT`, `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_PREFIX`, `_html_ids()`, and `_IdCollectingHTMLParser` definitions. Keep the existing `html_cache` behavior by parsing cached HTML strings with `parse_html_ids(...)`; do not replace cached string parsing with repeated path reads.

- [ ] **Step 2: Add CLI status payload and text output**

Update `_build_row_one_status_payload(...)` to accept the combined health object and add:

```python
"local_article_content": row_one_local_article_content_health_payload(
    generated_site_health.local_article_content
)
```

Update human output:

```python
typer.echo(
    "Local article content: "
    f"{local_article_content['status']} "
    f"({_format_saved_local_article_count(local_article_content['article_count'])}, "
    f"{local_article_content['paragraph_anchor_count']} paragraph anchors)"
)
```

Reuse the existing `_format_saved_local_article_count(...)` helper in `cli.py`; do not duplicate saved-article count wording.

- [ ] **Step 3: Run status tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_cli.py -q -k "local_article_content or local_article_route"
```

Expected: selected status tests pass.

### Task 6: Ops-Check RED Tests

**Files:**
- Modify: `tests/test_row_one_ops_check.py`

- [ ] **Step 1: Add ops-check tests**

Add:

- `test_ops_check_reports_local_article_content_health_ready`
- `test_ops_check_reports_attention_for_missing_local_article_content`
- `test_ops_check_text_includes_local_article_content_health`

Expected JSON checks:

```python
assert payload["local_article_content"]["status"] == "ready"
assert payload["local_article_content"]["article_count"] == 1
assert payload["status"] == "attention"
assert any("row-one refresh" in action for action in payload["actions"])
```

- [ ] **Step 2: Run ops-check tests to verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py -q -k "local_article_content or local_article_route"
```

Expected: new `local_article_content` tests fail because ops-check does not include content health yet; existing `local_article_route` tests should continue to pass.

### Task 7: Ops-Check Implementation

**Files:**
- Modify: `src/fashion_radar/row_one/ops_check.py`
- Modify: `src/fashion_radar/cli.py`
- Test: `tests/test_row_one_ops_check.py`

- [ ] **Step 1: Add content health payload to ops-check**

In `build_row_one_ops_check_payload(...)`, compute:

```python
local_article_content = row_one_local_article_content_health_payload(
    build_row_one_local_article_content_health(site_dir),
)
```

Include it in the returned payload. Update `_actions(...)` and `_overall_status(...)` so `status == "missing"` behaves like route health: attention plus refresh action.

- [ ] **Step 2: Add human ops-check output line in `src/fashion_radar/cli.py`**

In `_render_row_one_ops_check_text(...)`, add:

```python
f"Local article content: {local_article_content.get('status', 'unknown')}",
```

- [ ] **Step 3: Run ops-check tests to verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_ops_check.py -q -k "local_article_content or local_article_route"
```

Expected: selected ops-check tests pass.

### Task 8: Docs And Boundary Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/row-one.md`
- Modify: `tests/test_row_one_docs.py`
- Modify: `tests/test_workflows.py`

- [ ] **Step 1: Add RED docs/workflow tests**

In `tests/test_row_one_docs.py`, add a Stage 375 exact paragraph test using the boundary paragraph from the design. Also assert that the Stage 375 paragraph appears before the Stage 374 paragraph in both `README.md` and `docs/row-one.md`.

In `tests/test_workflows.py`, extend denylist tests so generated contracts and forbidden artifacts do not contain:

- `local_article_content_health`
- `article_content_health`
- `content_health`
- `local-article-content-health`
- `article-content-health`
- `content-health`

- [ ] **Step 2: Verify docs/workflow RED**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_375 or content_health"
```

Expected: docs paragraph tests fail until docs are updated.

- [ ] **Step 3: Update README and docs/row-one.md**

Insert the exact Stage 375 documentation boundary paragraph before the Stage 374 paragraph in both docs.

- [ ] **Step 4: Verify docs/workflow GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q -k "stage_375 or content_health"
```

Expected: selected docs and workflow tests pass.

### Task 9: Code Review, Full Verification, Commit, Push

**Files:**
- Create: `docs/reviews/claude-code-stage-375-code-review.md`
- Create: `docs/reviews/opencode-stage-375-code-review.md`
- Modify as needed from review findings.

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_local_article_content_health.py tests/test_row_one_cli.py tests/test_row_one_ops_check.py tests/test_row_one_docs.py tests/test_workflows.py -q
```

Expected: selected tests pass.

- [ ] **Step 2: Request Claude Code code review**

Run:

```bash
tmp_review="$(mktemp)"
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review Stage 375 Local Article Content Health implementation in /home/ubuntu/fashion-radar. Review the diff from HEAD and the spec/plan docs/superpowers/specs/2026-07-10-stage-375-local-article-content-health-design.md and docs/superpowers/plans/2026-07-10-stage-375-local-article-content-health-plan.md. Check correctness, read-only behavior, strict status validation, ops-check diagnostic behavior, app-contract/artifact boundaries, tests, and docs. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/claude-code-stage-375-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 3: Request opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Review Stage 375 Local Article Content Health implementation in /home/ubuntu/fashion-radar. Read docs/reviews/claude-code-stage-375-code-review.md if present and cross-check it. Review the current diff from HEAD and the spec/plan docs/superpowers/specs/2026-07-10-stage-375-local-article-content-health-design.md and docs/superpowers/plans/2026-07-10-stage-375-local-article-content-health-plan.md. Check correctness, read-only behavior, strict status validation, ops-check diagnostic behavior, app-contract/artifact boundaries, tests, and docs. Return findings only, ordered by Critical, Important, Minor." > "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-375-code-review.md
rm -f "$tmp_review"
```

- [ ] **Step 4: Fix Critical and Important findings**

If reviews raise valid Critical or Important issues, fix them and run matching rereviews:

- `docs/reviews/claude-code-stage-375-code-rereview.md`
- `docs/reviews/opencode-stage-375-code-rereview.md`

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

Expected: all gates pass.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-07-10-stage-375-local-article-content-health-design.md \
  docs/superpowers/plans/2026-07-10-stage-375-local-article-content-health-plan.md \
  docs/reviews/claude-code-stage-375-plan-review.md \
  docs/reviews/claude-code-stage-375-plan-rereview.md \
  docs/reviews/opencode-stage-375-plan-review.md \
  docs/reviews/claude-code-stage-375-code-review.md \
  docs/reviews/opencode-stage-375-code-review.md \
  README.md docs/row-one.md src/fashion_radar/row_one/local_article_anchors.py \
  src/fashion_radar/row_one/local_article_content_health.py \
  src/fashion_radar/row_one/status_integrity.py src/fashion_radar/row_one/ops_check.py \
  src/fashion_radar/cli.py tests/test_row_one_local_article_content_health.py \
  tests/test_row_one_cli.py tests/test_row_one_ops_check.py tests/test_row_one_docs.py \
  tests/test_workflows.py
git commit -m "Stage 375: add local article content health"
git push origin main
```

Expected: commit is pushed to `origin/main`.
