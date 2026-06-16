# Stage 58 Imported Heat Review Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the print-only `imported-review-workflow` with a final local read-only `heat-movers` review step.

**Architecture:** Append one deterministic workflow step in `imported_review_workflow.py` and let existing CLI JSON/table rendering include it naturally. Update direct tests, CLI tests, docs drift tests, and docs so the post-import external/community signal path points to local heat review without adding collection, connectors, schema, dependencies, reports, dashboard writes, or scheduling.

**Tech Stack:** Python 3.12, Pydantic v2, Typer, pytest, ruff, existing Fashion Radar local workflow helpers.

---

## Review Gate

Before implementation, submit this design and plan to local `opencode`:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-58-plan-review-prompt.md)" \
  > docs/reviews/opencode-stage-58-plan-review.md \
  2> /tmp/opencode-stage58-plan-review.err
```

Fix Critical and Important findings before touching production code.

## Files

Create:

- `docs/reviews/opencode-stage-58-plan-review-prompt.md`
- `docs/reviews/opencode-stage-58-plan-review.md`
- `docs/reviews/opencode-stage-58-release-review-prompt.md`
- `docs/reviews/opencode-stage-58-release-review.md`

Modify:

- `src/fashion_radar/imported_review_workflow.py`
- `tests/test_imported_review_workflow.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/community-signal-import.md`
- `docs/cli-reference.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`

Do not modify:

- `pyproject.toml`
- `uv.lock`
- database schema or migration files
- collector modules
- source packs or source acquisition behavior
- `community_signal_profile.py`
- `community_handoff_manifest.py`
- `community_handoff_workflow.py`
- `community_handoff_check.py`
- `heat_movers.py`
- report/digest generation code
- dashboard code

## Task 1: Imported Review Workflow Step

**Files:**

- Modify: `src/fashion_radar/imported_review_workflow.py`
- Modify: `tests/test_imported_review_workflow.py`

- [ ] **Step 1: Write failing direct workflow tests**

Update `test_build_imported_review_workflow_returns_deterministic_steps()` so it expects five steps:

```python
assert workflow.step_count == 5
assert [step.name for step in workflow.steps] == [
    "summarize_imported_sources",
    "refresh_stored_matches",
    "compare_imported_entities",
    "review_unmatched_imported_rows",
    "review_local_heat_movers",
]
assert [step.suggested_effect for step in workflow.steps] == [
    "read_only",
    "updates_local_matches",
    "read_only",
    "read_only",
    "read_only",
]
assert workflow.steps[4].command == (
    "fashion-radar heat-movers --config-dir configs --data-dir data "
    "--as-of 2026-06-13T12:00:00+00:00"
)
```

Update `test_build_imported_review_workflow_quotes_paths_and_source_name()` so it asserts:

```python
assert workflow.steps[4].command == (
    "fashion-radar heat-movers --config-dir 'config ? # & %' "
    "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00"
)
assert "--source-name" not in workflow.steps[4].command
```

Update `test_build_imported_review_workflow_blank_source_name_is_no_filter()`:

```python
assert "--source-name" not in workflow.steps[4].command
```

Update `test_render_imported_review_workflow_table()` fixture to include a
third step. Change `step_count=2` to `step_count=3`, add this third step to the
`steps=[...]` list, change the expected `"Steps: 2"` line to `"Steps: 3"`, and
append the corresponding expected rendered row:

```python
ImportedReviewWorkflowStep(
    order=3,
    name="review_local_heat_movers",
    purpose="Review local observed heat movement.",
    command=(
        "fashion-radar heat-movers --config-dir ./configs --data-dir ./data "
        "--as-of 2026-06-13T12:00:00+00:00"
    ),
    suggested_effect="read_only",
)
```

Expected rendered row:

```python
"3 | review_local_heat_movers | read_only | Review local observed heat movement. | "
"fashion-radar heat-movers --config-dir ./configs --data-dir ./data "
"--as-of 2026-06-13T12:00:00+00:00"
```

Expected red command:

```bash
uv run pytest tests/test_imported_review_workflow.py -q
```

Expected: failures showing current workflow has four steps and no heat-movers
step.

- [ ] **Step 2: Implement the workflow step**

In `src/fashion_radar/imported_review_workflow.py`, append after
`review_unmatched_imported_rows`:

```python
ImportedReviewWorkflowStep(
    order=5,
    name="review_local_heat_movers",
    purpose="Review local observed heat movement after imported rows are matched.",
    command=_shell_command(
        "fashion-radar",
        "heat-movers",
        "--config-dir",
        config_text,
        "--data-dir",
        data_text,
        "--as-of",
        as_of_text,
    ),
    suggested_effect="read_only",
),
```

Do not add `--source-name`; `heat-movers` reviews the configured local source
set and imported local signals after matching.

- [ ] **Step 3: Run direct workflow checks**

```bash
uv run pytest tests/test_imported_review_workflow.py -q
uv run ruff check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py
uv run ruff format --check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py
```

Expected: all pass.

## Task 2: CLI Coverage

**Files:**

- Modify: `tests/test_cli.py`

- [ ] **Step 1: Update CLI tests for JSON/table output**

Update existing `imported-review-workflow` tests near the current
`imported-review-workflow` block.

Add assertions that:

```python
assert payload["step_count"] == 5
assert payload["steps"][-1]["name"] == "review_local_heat_movers"
assert payload["steps"][-1]["suggested_effect"] == "read_only"
assert payload["steps"][-1]["command"] == (
    "fashion-radar heat-movers --config-dir <expected_config_dir> "
    "--data-dir <expected_data_dir> --as-of <expected_as_of>"
)
```

For table output, assert:

```python
assert "review_local_heat_movers" in result.output
assert "fashion-radar heat-movers" in result.output
assert "Commands were not executed." in result.output
```

Replace existing `payload["step_count"] == 4` expectations with
`payload["step_count"] == 5`; do not leave both assertions in place.

For no-artifact/no-data-access tests, reuse the existing patch targets and
artifact assertions. No new patch target is needed because the Stage 58 change
prints a command string only; add only a lightweight assertion that
`fashion-radar heat-movers` appears in successful workflow output when a
successful output test already exists.

Expected red command:

```bash
uv run pytest tests/test_cli.py -q -k imported_review_workflow
```

Expected: failures because the CLI output still has four workflow steps.

- [ ] **Step 2: Run CLI checks after Task 1 implementation**

No additional production CLI code should be needed; the CLI delegates to
`build_imported_review_workflow()`.

```bash
uv run pytest tests/test_cli.py -q -k imported_review_workflow
uv run ruff check tests/test_cli.py
uv run ruff format --check tests/test_cli.py
```

Expected: all pass.

## Task 3: Docs And Docs Drift

**Files:**

- Modify: `tests/test_cli_docs.py`
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add failing docs drift tests**

In `tests/test_cli_docs.py`, add a focused test:

```python
IMPORTED_REVIEW_HEAT_DOCS = (
    README,
    ROOT / "docs" / "community-signal-import.md",
    CLI_REFERENCE,
    ARCHITECTURE_DOC,
    SOURCE_BOUNDARIES_DOC,
    UPLOAD_CHECKLIST,
    CHANGELOG,
)


def test_imported_review_workflow_docs_link_to_heat_movers_review() -> None:
    required = (
        "imported-review-workflow",
        "heat-movers",
        "local observed heat movement",
        "read-only",
        "no demand proof",
        "no platform coverage verification",
    )
    for path in IMPORTED_REVIEW_HEAT_DOCS:
        normalized = _normalized_doc_text(path).casefold()
        for phrase in required:
            assert phrase in normalized, f"{path.relative_to(ROOT)} missing {phrase!r}"
```

Expected red command:

```bash
uv run pytest tests/test_cli_docs.py -q -k imported_review_workflow_docs
```

Expected: docs missing the new post-import heat review wording.

- [ ] **Step 2: Update docs**

Update docs to say:

- `imported-review-workflow` remains print-only and does not execute commands.
- It now includes a final `heat-movers` command after `match`.
- The final step reviews local observed heat movement from configured sources
  and imported local signals.
- The output needs review and provides no demand proof or platform coverage
  verification.
- The workflow does not add source acquisition, platform connectors, scraping,
  browser automation, monitoring, scheduling, report writes, dashboard writes,
  schema changes, or compliance-review features.

Example command text:

```bash
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF"
```

Do not change docs to imply `community-handoff-check-dir` runs heat review; that
command remains pre-import.

- [ ] **Step 3: Run docs checks**

```bash
uv run pytest tests/test_cli_docs.py -q -k "imported_review_workflow_docs or heat_movers"
uv run ruff check tests/test_cli_docs.py
uv run ruff format --check tests/test_cli_docs.py
git diff --check -- tests/test_cli_docs.py README.md docs/community-signal-import.md docs/cli-reference.md docs/architecture.md docs/source-boundaries.md docs/github-upload-checklist.md CHANGELOG.md
```

Expected: all pass.

## Task 4: Integration Verification And Release Review

**Files:**

- Create: `docs/reviews/opencode-stage-58-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-58-release-review.md`

- [ ] **Step 1: Run targeted checks**

```bash
uv run pytest tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py -q
uv run ruff check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py
uv run ruff format --check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py
git diff --check
```

- [ ] **Step 2: Run full release checks**

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

- [ ] **Step 3: Run installed-wheel smoke**

Use a temporary build and venv. Include:

```bash
fashion-radar --help
fashion-radar imported-review-workflow --help
fashion-radar imported-review-workflow --data-dir "$tmp_data" --config-dir "$tmp_configs" --as-of 2026-06-13T12:00:00Z --format json
```

Validate the installed JSON includes:

```text
"step_count": 5
"review_local_heat_movers"
"fashion-radar heat-movers"
```

- [ ] **Step 4: Submit release review to opencode**

The release review prompt must ask `opencode` to verify:

- `imported-review-workflow` remains print-only.
- The new `heat-movers` step is read-only and local-only.
- No command execution, imports, DB writes, source acquisition, scraping,
  platform API calls, browser automation, monitoring, scheduling, schema,
  dependencies, reports/digests/dashboard writes, or compliance-review features
  were added.
- Docs accurately describe the post-import heat review handoff without
  platform-wide/demand claims.
- Full verification commands passed.

Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-58-release-review-prompt.md)" \
  > docs/reviews/opencode-stage-58-release-review.md \
  2> /tmp/opencode-stage58-release-review.err
```

Fix Critical and Important findings before commit.

- [ ] **Step 5: Commit and upload**

After verification and release approval:

```bash
git status --short --branch
git add src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py README.md docs/community-signal-import.md docs/cli-reference.md docs/architecture.md docs/source-boundaries.md docs/github-upload-checklist.md CHANGELOG.md docs/superpowers/specs/2026-06-17-stage-58-imported-heat-review-workflow-design.md docs/superpowers/plans/2026-06-17-stage-58-imported-heat-review-workflow-plan.md docs/reviews/opencode-stage-58-plan-review-prompt.md docs/reviews/opencode-stage-58-plan-review.md docs/reviews/opencode-stage-58-release-review-prompt.md docs/reviews/opencode-stage-58-release-review.md
git diff --cached --check
git commit -m "Add imported heat review workflow step"
git push origin main
```

If normal `git push` fails, use the existing token-backed basic auth header or
the GitHub API fast-forward path without writing the token into the remote URL
or repository files.
