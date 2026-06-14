# Stage 37 Local Platform Provenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve sanitized local manual/community signal `platform` provenance through storage and local review output.

**Architecture:** Add a nullable `items.platform` column with a schema v5 migration, add optional repository support, pass the already-parsed manual signal platform label into storage, and expose it in imported-signals review rows and aggregate counts. Keep platform as provenance only, not a connector, coverage metric, or heat-score input.

**Tech Stack:** Python, Pydantic v2 validators, SQLAlchemy Core, SQLite migrations, Typer CLI tests, pytest, ruff, uv. No dependency, source-collection, connector, scraping, or platform automation changes.

---

## Boundaries

In scope:

- `src/fashion_radar/db/schema.py`
- `src/fashion_radar/db/repositories.py`
- `src/fashion_radar/importers/manual_signals.py`
- `src/fashion_radar/imported_signals.py`
- `tests/test_db.py`
- `tests/test_manual_signal_import.py`
- `tests/test_imported_signals.py`
- focused `tests/test_cli.py` expectations around imported signal/platform output
- `docs/manual-signal-import.md`
- `docs/community-signal-import.md`
- `README.md`
- `docs/source-boundaries.md`
- `CHANGELOG.md`
- Stage 37 plan/review artifacts.

Out of scope:

- Heat-score formula changes.
- Platform spread scoring.
- Any source connector, social-platform functionality, scraping, crawling,
  browser automation, login/cookie flow, account automation, proxy pool, CAPTCHA
  bypass, source acquisition, source ranking, demand proof, watcher, scheduler,
  or external platform API integration.
- Storing raw/private social fields such as handles, raw comments, account IDs,
  private exports, local paths, cookies, session files, browser profiles, or
  generated reports.
- Dependency or `uv.lock` changes.

## Task -1: Claude Code Plan Review Gate

**Files:**

- Add: `docs/reviews/claude-code-stage-37-plan-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-37-plan-review.md`

- [ ] **Step 1: Request pre-execution plan review**

Create `docs/reviews/claude-code-stage-37-plan-review-prompt.md` with:

```markdown
# Claude Code Stage 37 Plan Review Prompt

You are reviewing the Stage 37 local platform provenance plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Preserve sanitized local manual/community signal `platform` provenance through
storage and local review output.

## Proposed Technical Approach

- Add nullable `items.platform` storage and bump schema version from 4 to 5.
- Add a v4-to-v5 migration that adds `platform varchar(64)` if missing.
- Add `platform: str | None = None` as a keyword-only
  `ItemRepository.upsert_item()` parameter with blank-to-None normalization.
- Persist `ManualSignalRow.platform` from local CSV/JSON handoff rows through
  that repository parameter.
- Expose `platform` in `imported-signals` review rows, table output, and local
  aggregate counts.
- Keep platform as provenance only: no heat-score changes, no platform spread
  scoring, no coverage proof, no connectors, no scraping/crawling/browser
  automation/login-cookie/account/proxy/CAPTCHA/source-acquisition functionality.
- Continue dropping private/raw fields such as `author_handle`, `raw_comment`,
  `account_id`, paths, cookies, session files, browser profiles, and generated
  reports.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-37-local-platform-provenance-design.md`
- `docs/superpowers/plans/2026-06-14-stage-37-local-platform-provenance-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 37 LOCAL PLATFORM PROVENANCE
```
```

Run:

```bash
claude --effort max --permission-mode plan --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-37-plan-review-prompt.md)" \
  > docs/reviews/claude-code-stage-37-plan-review.md
```

Expected: approval phrase appears, or the plan is revised and rereviewed before
Task 1.

## Task 1: Schema And Repository Tests

**Files:**

- Modify: `tests/test_db.py`

- [ ] **Step 1: Add schema v5 migration tests**

Add tests that assert:

- `SCHEMA_VERSION == 5`;
- newly initialized DBs have an `items.platform` column;
- a v4 database migrates to v5 and gains nullable `platform`;
- existing rows in a v4 DB retain all existing values and get `platform is None`.

- [ ] **Step 2: Add repository platform persistence tests**

Add tests that assert:

- `ItemRepository.upsert_item(..., platform="  xiaohongshu  ")` stores
  `"xiaohongshu"`;
- blank platform values are stored as `None`;
- upserting an existing normalized URL updates `platform`;
- RSS/GDELT-style items without platform store `None`.

- [ ] **Step 3: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py -q -k "schema or platform or item_repository"
```

Expected before implementation: failures because schema is still v4 and
repository platform persistence does not exist.

## Task 2: Schema And Repository Implementation

**Files:**

- Modify: `src/fashion_radar/db/schema.py`
- Modify: `src/fashion_radar/db/repositories.py`

- [ ] **Step 1: Add `items.platform` column and schema v5 migration**

In `schema.py`:

- change `SCHEMA_VERSION = 5`;
- add `Column("platform", String(64))` to `items`;
- add `_migrate_v4_to_v5(engine)`:

```python
def _migrate_v4_to_v5(engine: Engine) -> None:
    existing_columns = {column["name"] for column in inspect(engine).get_columns("items")}
    with engine.begin() as connection:
        if "platform" not in existing_columns:
            connection.exec_driver_sql("alter table items add column platform varchar(64)")
        connection.execute(update(schema_metadata).values(version=SCHEMA_VERSION))
```

- call it from `initialize_schema()` after v3-to-v4 migration:

```python
if existing_version == 4:
    _migrate_v4_to_v5(engine)
    existing_version = 5
```

- [ ] **Step 2: Add repository parameter**

In `ItemRepository.upsert_item()`, add keyword-only
`platform: str | None = None`, normalize it with `" ".join(str(value).split())`
and blank-to-None behavior, and add it to `values` so both insert and update
paths persist the latest local label.

- [ ] **Step 3: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py -q -k "schema or platform or item_repository"
```

Expected: schema/repository tests pass.

## Task 3: Repository And Manual Import Tests

**Files:**

- Modify: `tests/test_manual_signal_import.py`
- Modify: focused `tests/test_cli.py` platform assertions where import storage is checked.

- [ ] **Step 1: Update manual import storage expectations**

Change existing assertions:

```python
assert "platform" not in first
```

to:

```python
assert first["platform"] == "manual"
assert second["platform"] == "manual"
```

Keep assertions that `author_handle`, `raw_comment`, and `account_id` are not
stored.

Update CLI tests that currently assert `"platform" not in item` to assert the
sanitized platform label is preserved for manual/community imports, while raw
private fields are still absent.

- [ ] **Step 2: Verify RED**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py tests/test_manual_signal_import.py tests/test_cli.py -q -k "platform or import_signals"
```

Expected before repository/import implementation: failures because platform is
not persisted.

## Task 4: Manual Import Implementation

**Files:**

- Modify: `src/fashion_radar/importers/manual_signals.py`

- [ ] **Step 1: Pass manual row platform to repository**

In `store_manual_signal_rows()`, pass:

```python
platform=row.platform,
```

Do not store `author_handle`, `raw_comment`, `account_id`, unknown fields, or
paths.

- [ ] **Step 2: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py tests/test_manual_signal_import.py tests/test_cli.py -q -k "platform or import_signals"
```

Expected: repository/import focused tests pass.

## Task 5: Imported Signals Review Tests And Implementation

**Files:**

- Modify: `src/fashion_radar/imported_signals.py`
- Modify: `tests/test_imported_signals.py`
- Modify: focused `tests/test_cli.py` imported-signals output assertions.

- [ ] **Step 1: Add imported-signals review tests**

Add tests that:

- `query_imported_signals()` includes `platform` on review items;
- `query_imported_signals()` includes `platform_counts` for non-null local
  labels;
- `render_imported_signals_table()` includes a `Platforms:` line, `Platform`
  column, and value;
- `query_imported_signals_summary()` includes top-level `platform_counts`;
- `render_imported_signals_summary_table()` includes a `Platforms:` line;
- missing/old schema validation includes `platform` in required items columns;
- output still does not include raw handles/comments/account IDs.

- [ ] **Step 2: Implement review field**

In `ImportedSignalItem`, add:

```python
platform: str | None = None
```

Add `"platform"` to `REQUIRED_ITEMS_COLUMNS`.

In `_build_review_items()`, pass:

```python
platform=row["platform"],
```

In `render_imported_signals_table()`, change the header to:

```python
"ID | Collected At | Match | Source | Platform | Weight | Title | URL"
```

and add `platform` between source and weight, using `_table_cell(item.platform or "")`.

Add top-level `platform_counts: dict[str, int]` to `ImportedSignalsReview` and
`ImportedSignalsSourceSummary`. Populate counts from retained manual-import
rows only, excluding `NULL` or blank labels. Add a `Platforms:` line to both
table renderers.

- [ ] **Step 3: Verify GREEN**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_imported_signals.py tests/test_cli.py -q -k "imported_signals or platform"
```

Expected: imported-signals tests pass.

## Task 6: Docs, Verification, And Claude Code Release Review

**Files:**

- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-import.md`
- Modify: `CHANGELOG.md`
- Add: `docs/reviews/claude-code-stage-37-release-review-prompt.md`
- Add: `docs/reviews/claude-code-stage-37-release-review.md`

- [ ] **Step 1: Update docs**

Update manual/community docs so `platform` is described as:

- stored as a local provenance label on retained manual-import rows;
- visible in `imported-signals`;
- not platform coverage, demand proof, ranking, or source acquisition;
- not collected by Fashion Radar.

- [ ] **Step 2: Add changelog entry**

Add:

```markdown
- Preserved local manual/community signal platform provenance in retained import rows and review output.
```

- [ ] **Step 3: Focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_db.py tests/test_manual_signal_import.py tests/test_imported_signals.py tests/test_cli.py -q -k "schema or platform or import_signals or imported_signals"
UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/db/schema.py src/fashion_radar/db/repositories.py src/fashion_radar/importers/manual_signals.py src/fashion_radar/imported_signals.py tests/test_db.py tests/test_manual_signal_import.py tests/test_imported_signals.py tests/test_cli.py
UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/db/schema.py src/fashion_radar/db/repositories.py src/fashion_radar/importers/manual_signals.py src/fashion_radar/imported_signals.py tests/test_db.py tests/test_manual_signal_import.py tests/test_imported_signals.py tests/test_cli.py
```

- [ ] **Step 4: Full release verification**

Run:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 CI=true GITHUB_ACTIONS=true _TYPER_FORCE_DISABLE_TERMINAL=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

- [ ] **Step 5: Boundary scans**

Run diff-scoped scans to confirm there are no dependency, source connector,
scraping, crawling, browser automation, login/cookie, account automation,
proxy/CAPTCHA, source acquisition, source ranking, demand proof, watcher,
scheduler, data artifact, report artifact, or token changes.

- [ ] **Step 6: Claude Code release review**

Create a release review prompt that includes the diff, RED/GREEN evidence,
verification evidence, schema migration evidence, and boundary scan evidence.
Required approval phrase:

```text
APPROVED FOR STAGE 37 COMMIT AND PUSH
```

Fix Critical/Important findings before commit.

## Task 7: Commit, Push, And GitHub Actions Confirmation

**Files:**

- Git only.

- [ ] **Step 1: Stage only Stage 37 files**

Confirm only Stage 37 files are staged. `uv.lock`, dependency metadata,
generated data, generated reports, generated build artifacts, and unrelated
source files must not be staged.

- [ ] **Step 2: Commit and push**

Commit:

```bash
git commit -m "Preserve local platform provenance" \
  -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

Push with a one-shot HTTP extraheader. Do not persist the GitHub token.

- [ ] **Step 3: Confirm GitHub Actions**

Poll the latest GitHub Actions run for the pushed commit until it completes.
If it fails, debug with job logs and do not proceed to the next stage.

## Handoff Summary Requirement

At node end, write a concise Handoff Summary with:

- repo status;
- verified commands;
- GitHub Actions result;
- uncommitted files;
- next step.
