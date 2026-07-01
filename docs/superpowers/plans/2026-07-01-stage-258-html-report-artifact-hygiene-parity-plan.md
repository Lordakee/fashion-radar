# Stage 258 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make generated companion HTML report artifacts receive the same first-run smoke, default-artifact guard, cleanup-doc, and docs-guard treatment as generated Markdown and JSON reports.

**Architecture:** Stage 257 made `report` write `fashion-radar-YYYY-MM-DD.html` alongside Markdown and JSON. This node does not change report rendering or collection behavior; it updates local artifact path helpers, smoke assertions, docs, and docs drift guards so generated HTML reports are not missed by cleanup or repository-hygiene checks.

**Tech Stack:** Python 3.12, existing first-run smoke script, pytest, Markdown docs, existing `.gitignore` and release hygiene behavior, `uv --no-config run --frozen`, review gate via Claude Code primary / opencode GLM 5.2 max fallback.

---

## Files

- Modify `scripts/check_first_run_smoke.py`
  - Change `report_paths(context)` to return Markdown, JSON, and HTML paths.
  - Assert the HTML report is non-empty during `run_first_run_flow`.
- Modify `tests/test_first_run_smoke.py`
  - Update report-path tests for the third HTML path.
  - Add default-artifact guard coverage for new, changed, and deleted
    `reports/fashion-radar-YYYY-MM-DD.html` files.
- Modify `README.md`
  - Add HTML to the first-run smoke temporary report wording where it currently
    lists temporary MD/JSON output only.
- Modify `docs/first-run.md`
  - Add HTML to cleanup/reset commands and any first-run artifact wording still
    listing only MD/JSON.
- Modify `docs/data-retention.md`
  - Replace generated "Markdown or JSON" report wording with
    "Markdown, JSON, or HTML" report wording.
- Modify `tests/test_cli_docs.py`
  - Update README and first-run docs guards that pin report paths and cleanup
    commands to include the HTML companion report.
- Modify `tests/test_data_retention_docs.py`
  - Update the retained data-retention phrase to include HTML report files.

## Scope Out

- No changes to `src/fashion_radar/html_report.py` or report rendering.
- No changes to `src/fashion_radar/workflows.py` artifact-writing behavior.
- No changes to social/platform collectors, scraping, browser automation,
  platform APIs, scheduling, source acquisition, demand proof, ranking
  semantics, or platform coverage verification.
- No dependency, `pyproject.toml`, or `uv.lock` changes.
- No release/upload behavior changes beyond local artifact hygiene guards.
- No changes to daily digest packaging. `docs/daily-digest.md` remains MD/JSON
  only because digest packaging reads the Markdown/JSON report pair, not the
  companion HTML report.

## Tasks

### Task 1: First-Run Smoke HTML Path Parity

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Write failing tests for HTML report path parity**

In `tests/test_first_run_smoke.py`, update `test_report_paths_derive_date_from_as_of` so it expects:

```python
markdown_path, json_path, html_path = smoke.report_paths(context)

assert markdown_path == context.reports_dir / "fashion-radar-2026-06-13.md"
assert json_path == context.reports_dir / "fashion-radar-2026-06-13.json"
assert html_path == context.reports_dir / "fashion-radar-2026-06-13.html"
```

Add HTML files to the default-artifact guard tests:

```python
html_file = tmp_path / "reports" / "fashion-radar-2026-06-13.html"
html_file.write_text("<!doctype html>", encoding="utf-8")
...
assert "reports/fashion-radar-2026-06-13.html" in message
```

Apply the same HTML assertion shape to:

- `test_default_artifact_guard_detects_new_repo_data_and_report_files`
- `test_default_artifact_guard_detects_changed_repo_data_and_report_files`
- `test_default_artifact_guard_detects_deleted_repo_data_or_report_files`

- [ ] **Step 2: Run the targeted tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_report_paths_derive_date_from_as_of tests/test_first_run_smoke.py::test_default_artifact_guard_detects_new_repo_data_and_report_files tests/test_first_run_smoke.py::test_default_artifact_guard_detects_changed_repo_data_and_report_files tests/test_first_run_smoke.py::test_default_artifact_guard_detects_deleted_repo_data_or_report_files -q
```

Expected before implementation: at least `test_report_paths_derive_date_from_as_of` fails because `report_paths()` returns only two paths.

- [ ] **Step 3: Implement the minimal smoke script update**

In `scripts/check_first_run_smoke.py`, change:

```python
def report_paths(context: SmokeContext) -> tuple[Path, Path]:
```

to:

```python
def report_paths(context: SmokeContext) -> tuple[Path, Path, Path]:
```

and return:

```python
return (
    context.reports_dir / f"fashion-radar-{report_date}.md",
    context.reports_dir / f"fashion-radar-{report_date}.json",
    context.reports_dir / f"fashion-radar-{report_date}.html",
)
```

In `run_first_run_flow`, change:

```python
markdown_path, json_path = report_paths(context)
assert_non_empty_file(markdown_path)
assert_non_empty_file(json_path)
```

to:

```python
markdown_path, json_path, html_path = report_paths(context)
assert_non_empty_file(markdown_path)
assert_non_empty_file(json_path)
assert_non_empty_file(html_path)
```

- [ ] **Step 4: Run the targeted tests and verify they pass**

Run the command from Step 2 again.

Expected: all selected tests pass.

### Task 2: Docs And Docs-Guard HTML Artifact Parity

**Files:**
- Modify: `README.md`
- Modify: `docs/first-run.md`
- Modify: `docs/data-retention.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `tests/test_data_retention_docs.py`

- [ ] **Step 1: Write/update docs guard assertions first**

In `tests/test_cli_docs.py`, update the README/first-run guard sections that
currently require only:

```python
"reports/fashion-radar-2026-06-13.md"
"reports/fashion-radar-2026-06-13.json"
```

so they also require:

```python
"reports/fashion-radar-2026-06-13.html"
```

Also add a normalized README-specific assertion that pins the automated smoke
description sentence so it cannot pass merely because HTML appears elsewhere in
the README:

```python
normalized = _normalized(README.read_text(encoding="utf-8"))
assert (
    "temporary dated reports such as `fashion-radar-2026-06-13.md`, "
    "`fashion-radar-2026-06-13.json`, and "
    "`fashion-radar-2026-06-13.html`"
) in normalized
```

Update the reset command guard that currently pins:

```python
"rm -f reports/fashion-radar-2026-06-13.md; "
"rm -f reports/fashion-radar-2026-06-13.json; }"
```

to include:

```python
"rm -f reports/fashion-radar-2026-06-13.html; }"
```

Rewrite the full expected reset literal rather than appending an independent
substring; the existing test pins one contiguous cleanup command.

In `tests/test_data_retention_docs.py`, change the expected phrase from:

```python
"generated Markdown or JSON report files"
```

to:

```python
"generated Markdown, JSON, or HTML report files"
```

- [ ] **Step 2: Run docs guard tests and verify they fail**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_data_retention_docs.py -q
```

Expected before docs edits: failures for the README smoke-description sentence,
first-run cleanup command, and data-retention phrase.

- [ ] **Step 3: Update docs minimally**

In `README.md`, update the wording that says:

```text
temporary dated reports such as `fashion-radar-2026-06-13.md` and
`fashion-radar-2026-06-13.json`
```

to include:

```text
`fashion-radar-2026-06-13.html`
```

In `docs/first-run.md`, add:

```bash
rm -f reports/fashion-radar-2026-06-13.html;
```

to the reset block after the JSON report deletion.

In `docs/data-retention.md`, change the "not pruned" list item to:

```text
- generated Markdown, JSON, or HTML report files
```

- [ ] **Step 4: Run docs guard tests and verify they pass**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_data_retention_docs.py -q
```

Expected: all selected tests pass.

### Task 3: Verification And Review

**Files:**
- Create review records under `docs/reviews/`.

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_data_retention_docs.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_data_retention_docs.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py tests/test_data_retention_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
```

Expected: all commands pass.

- [ ] **Step 2: Request code review**

Use Claude Code primary review command first. If unavailable, record that
honestly and use opencode fallback per `docs/REVIEW_PROTOCOL.md`.

- [ ] **Step 3: Fix critical and important review findings**

Apply only technically valid Critical/Important findings, then rerun focused
verification.

- [ ] **Step 4: Full gate before commit**

Run:

```bash
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

Expected: all commands pass.
