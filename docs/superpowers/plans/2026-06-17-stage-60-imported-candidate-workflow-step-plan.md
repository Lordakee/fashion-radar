# Stage 60 Imported Candidate Workflow Step Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the existing read-only `imported-candidates` command to the print-only imported review workflow.

**Architecture:** Insert one deterministic `ImportedReviewWorkflowStep` in the existing pure workflow builder. Update tests, docs, and first-run smoke to prove the workflow has six steps and still ends with `heat-movers`.

**Tech Stack:** Python 3.11+, Pydantic models, Typer CLI, pytest, ruff, Markdown docs, existing shell-based smoke scripts.

---

## File Structure

Modify:

- `src/fashion_radar/imported_review_workflow.py`
  - Add the new printed `imported-candidates` step and renumber later steps.
- `tests/test_imported_review_workflow.py`
  - Freeze six-step order, command strings, quoting, source-name behavior, and table rendering.
- `tests/test_cli.py`
  - Freeze CLI JSON/table output and no-runtime-data-access behavior.
- `scripts/check_first_run_smoke.py`
  - Validate `imported-review-workflow --format json` in source-checkout and installed smoke.
- `tests/test_first_run_smoke.py`
  - Update expected command sequence and helper coverage for the new smoke call.
- `tests/test_cli_docs.py`
  - Add workflow-specific docs drift coverage for the imported candidate phrase step.
- `README.md`
- `docs/community-signal-import.md`
- `docs/cli-reference.md`
- `docs/architecture.md`
- `docs/source-boundaries.md`
- `docs/github-upload-checklist.md`
- `docs/manual-signal-import.md`
- `docs/community-signal-quality.md`
- `CHANGELOG.md`
  - Update current docs for the six-step workflow.

Do not modify:

- `src/fashion_radar/imported_candidates.py`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/community_handoff_workflow.py`
- `src/fashion_radar/community_handoff_manifest.py`
- `src/fashion_radar/community_signal_profile.py`
- `uv.lock`
- `pyproject.toml`
- Database schema or migration files

Implementation split:

- Execute tasks sequentially.
- Task 1 owns workflow source and direct workflow tests.
- Task 2 owns CLI tests and first-run smoke.
- Task 3 owns docs and docs drift tests.
- Do not run code-editing workers in parallel for this node; Task 2 and Task 3
  depend on Task 1’s six-step model.

---

### Task 1: Workflow Builder And Direct Tests

**Files:**

- Modify: `src/fashion_radar/imported_review_workflow.py`
- Modify: `tests/test_imported_review_workflow.py`

- [ ] **Step 1: Write failing direct workflow tests**

In `tests/test_imported_review_workflow.py`, update
`test_build_imported_review_workflow_returns_deterministic_steps()` to expect:

```python
assert workflow.step_count == 6
assert [step.name for step in workflow.steps] == [
    "summarize_imported_sources",
    "refresh_stored_matches",
    "compare_imported_entities",
    "review_imported_candidate_phrases",
    "review_unmatched_imported_rows",
    "review_local_heat_movers",
]
assert [step.suggested_effect for step in workflow.steps] == [
    "read_only",
    "updates_local_matches",
    "read_only",
    "read_only",
    "read_only",
    "read_only",
]
```

Add exact command assertions:

```python
assert workflow.steps[3].command == (
    "fashion-radar imported-candidates --config-dir configs --data-dir data "
    "--as-of 2026-06-13T12:00:00+00:00"
)
assert workflow.steps[4].command == (
    "fashion-radar imported-signals --data-dir data "
    "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 7 --unmatched-only"
)
assert workflow.steps[5].command == (
    "fashion-radar heat-movers --config-dir configs --data-dir data "
    "--as-of 2026-06-13T12:00:00+00:00"
)
```

In the quoting/source-name test, assert:

```python
assert workflow.steps[3].command == (
    "fashion-radar imported-candidates --config-dir 'config ? # & %' "
    "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
    "--source-name 'Community | Tool Export'"
)
assert "--source-name 'Community | Tool Export'" in workflow.steps[4].command
assert "--source-name" not in workflow.steps[5].command
```

In the blank source-name test, assert both candidate and heat steps omit
`--source-name`:

```python
assert "--source-name" not in workflow.steps[3].command
assert "--source-name" not in workflow.steps[5].command
```

Update the render-table fixture to include a candidate row and `Steps: 4` or use
six rows if the fixture intentionally mirrors the full workflow. If using a
compact fixture, include at least one `review_imported_candidate_phrases` row:

```python
ImportedReviewWorkflowStep(
    order=3,
    name="review_imported_candidate_phrases",
    purpose="Review imported candidate phrases.",
    command=(
        "fashion-radar imported-candidates --config-dir ./configs --data-dir ./data "
        "--as-of 2026-06-13T12:00:00+00:00"
    ),
    suggested_effect="read_only",
)
```

- [ ] **Step 2: Run direct tests and observe failure**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_imported_review_workflow.py -q
```

Expected: failures showing five steps and no candidate step.

- [ ] **Step 3: Implement workflow step**

In `src/fashion_radar/imported_review_workflow.py`, insert this step after
`compare_imported_entities` and before `review_unmatched_imported_rows`:

```python
ImportedReviewWorkflowStep(
    order=4,
    name="review_imported_candidate_phrases",
    purpose=(
        "Review observed candidate phrases from retained imported rows after "
        "stored matches are refreshed."
    ),
    command=_shell_command(
        "fashion-radar",
        "imported-candidates",
        "--config-dir",
        config_text,
        "--data-dir",
        data_text,
        "--as-of",
        as_of_text,
        *source_args,
    ),
    suggested_effect="read_only",
),
```

Renumber:

- `review_unmatched_imported_rows` to `order=5`
- `review_local_heat_movers` to `order=6`

Do not call `query_imported_candidates`, load config files, open SQLite, inspect
paths, or run subprocesses.

- [ ] **Step 4: Verify direct tests pass**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_imported_review_workflow.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py
```

Expected: all pass.

---

### Task 2: CLI And First-Run Smoke

**Files:**

- Modify: `tests/test_cli.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Write failing CLI tests**

In `tests/test_cli.py`, update the imported-review workflow JSON test to expect:

```python
assert payload["step_count"] == 6
assert payload["steps"][3]["name"] == "review_imported_candidate_phrases"
assert payload["steps"][3]["suggested_effect"] == "read_only"
assert payload["steps"][3]["command"] == (
    "fashion-radar imported-candidates "
    f"--config-dir {shlex.quote(str(config_dir))} "
    f"--data-dir {shlex.quote(str(data_dir))} "
    "--as-of 2026-06-13T12:00:00+00:00 --source-name 'Community Tool Export'"
)
assert payload["steps"][-1]["name"] == "review_local_heat_movers"
assert "--source-name" not in payload["steps"][-1]["command"]
```

The existing CLI JSON fixture uses `tmp_path / "config dir"` and
`tmp_path / "data dir"`, so assertions must quote those concrete paths instead
of using literal `configs` and `data`.

Update the table test to assert:

```python
assert "review_imported_candidate_phrases" in result.output
assert "fashion-radar imported-candidates" in result.output
```

In `_patch_imported_review_workflow_no_data_access()`, add
`"query_imported_candidates"` to the list of patched side-effect helpers if the
symbol is available in the CLI module. The helper should still fail if the
workflow command tries to run candidate review instead of printing the command.

In `test_imported_review_workflow_command_does_not_access_data_or_execute()`,
assert:

```python
assert "fashion-radar imported-candidates" in result.output
```

- [ ] **Step 2: Write failing first-run smoke tests**

Inspect `tests/test_first_run_smoke.py` and update the expected command sequence
to include an `imported-review-workflow` invocation after `match`. Also add an
`"imported-review-workflow"` entry to the fake `stdout_by_command` map that
returns a JSON payload accepted by `validate_imported_review_workflow()`. Shift
any pinned `captured[...]` index assertions after `match` by one position.

Add or update tests for the new validator helper:

```python
def test_validate_imported_review_workflow_requires_candidate_step() -> None:
    payload = {
        "execution_mode": "print_only",
        "step_count": 6,
        "steps": [
            {"name": "summarize_imported_sources", "command": "fashion-radar imported-signals-summary --data-dir data"},
            {"name": "refresh_stored_matches", "command": "fashion-radar match --config-dir configs --data-dir data"},
            {"name": "compare_imported_entities", "command": "fashion-radar imported-entity-deltas --data-dir data --as-of 2026-06-13T12:00:00+00:00 --source-name 'Community Tool Export'"},
            {"name": "review_imported_candidate_phrases", "command": "fashion-radar imported-candidates --config-dir configs --data-dir data --as-of 2026-06-13T12:00:00+00:00 --source-name 'Community Tool Export'"},
            {"name": "review_unmatched_imported_rows", "command": "fashion-radar imported-signals --data-dir data --as-of 2026-06-13T12:00:00+00:00 --lookback-days 7 --unmatched-only --source-name 'Community Tool Export'"},
            {"name": "review_local_heat_movers", "command": "fashion-radar heat-movers --config-dir configs --data-dir data --as-of 2026-06-13T12:00:00+00:00"},
        ],
    }

    validate_imported_review_workflow("imported-review-workflow", payload)
```

Also add a negative test that removes the candidate step or moves
`review_local_heat_movers` away from the final position and expects `SmokeError`.

- [ ] **Step 3: Run CLI/smoke tests and observe failure**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_first_run_smoke.py -q -k "imported_review_workflow or first_run_smoke"
```

Expected: failures until the workflow source and smoke helper are updated.

- [ ] **Step 4: Implement first-run smoke helper**

In `scripts/check_first_run_smoke.py`, add:

```python
EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEPS = (
    "summarize_imported_sources",
    "refresh_stored_matches",
    "compare_imported_entities",
    "review_imported_candidate_phrases",
    "review_unmatched_imported_rows",
    "review_local_heat_movers",
)
```

Add:

```python
def validate_imported_review_workflow(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 6)
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    names = [step.get("name") for step in steps if isinstance(step, dict)]
    assert_equal(f"{command_name} step names", names, list(EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEPS))
    candidate_step = steps[3]
    if not isinstance(candidate_step, dict):
        raise SmokeError(f"{command_name} candidate step must be a JSON object")
    candidate_command = str(candidate_step.get("command", ""))
    for expected in (
        "fashion-radar imported-candidates",
        "--config-dir",
        "--data-dir",
        "--as-of",
        "--source-name",
        SOURCE_NAME,
    ):
        if expected not in candidate_command:
            raise SmokeError(f"{command_name} candidate command missing {expected!r}")
    heat_step = steps[-1]
    if not isinstance(heat_step, dict):
        raise SmokeError(f"{command_name} heat step must be a JSON object")
    assert_equal(f"{command_name} final step", heat_step.get("name"), "review_local_heat_movers")
    heat_command = str(heat_step.get("command", ""))
    if "fashion-radar heat-movers" not in heat_command:
        raise SmokeError(f"{command_name} final heat command missing heat-movers")
    if "--source-name" in heat_command:
        raise SmokeError(f"{command_name} final heat command must not include --source-name")
```

Call the command after `match` in the main smoke flow:

```python
workflow_output = run_cli_json(
    context,
    "imported-review-workflow",
    "--config-dir",
    str(context.config_dir),
    "--data-dir",
    str(context.data_dir),
    "--as-of",
    AS_OF,
    "--source-name",
    SOURCE_NAME,
    "--format",
    "json",
)
validate_imported_review_workflow("imported-review-workflow", workflow_output)
```

Adapt the exact helper call style to existing smoke script helpers.

- [ ] **Step 5: Verify CLI/smoke tests pass**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_first_run_smoke.py -q -k "imported_review_workflow or first_run_smoke"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check tests/test_cli.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
```

Expected: all pass.

---

### Task 3: Docs And Docs Drift

**Files:**

- Modify: `tests/test_cli_docs.py`
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `docs/manual-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write failing docs drift test**

In `tests/test_cli_docs.py`, extend the imported-review workflow docs coverage.
Use workflow-specific phrases that cannot be satisfied by a standalone command
mention:

```python
IMPORTED_REVIEW_WORKFLOW_DOCS = (
    README,
    ROOT / "docs" / "community-signal-import.md",
    CLI_REFERENCE,
    ARCHITECTURE_DOC,
    SOURCE_BOUNDARIES_DOC,
    UPLOAD_CHECKLIST,
    ROOT / "docs" / "manual-signal-import.md",
    ROOT / "docs" / "community-signal-quality.md",
    CHANGELOG,
)
IMPORTED_REVIEW_WORKFLOW_REQUIRED_PHRASES = (
    "imported-review-workflow",
    "read-only imported-candidates step",
    "candidate phrase review",
    "heat-movers",
    "final",
    "read-only",
    "no demand proof",
    "no platform coverage verification",
)
```

Update the existing imported-review docs test to iterate these constants.

- [ ] **Step 2: Run docs test and observe failure**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q -k "imported_review_workflow_docs"
```

Expected: failures until docs mention the workflow-specific candidate step.

- [ ] **Step 3: Update current docs**

Update docs with concise current-state wording:

- `README.md`: `imported-review-workflow` includes a read-only
  `imported-candidates` step for candidate phrase review and still ends with the
  final read-only `heat-movers` step.
- `docs/community-signal-import.md`: same workflow wording in Review After
  Import; keep no execution/no SQLite/no artifact boundary.
- `docs/cli-reference.md`: expand the `imported-review-workflow` command entry
  with the read-only `imported-candidates` step and final `heat-movers`.
- `docs/architecture.md`: update imported review architecture wording.
- `docs/source-boundaries.md`: mention the workflow prints local read-only
  `imported-candidates` and final `heat-movers`, with no demand proof or
  platform coverage verification.
- `docs/github-upload-checklist.md`: add Stage 60 checklist wording and update
  the installed-wheel workflow JSON assertion snippet to check step count `6`,
  `review_imported_candidate_phrases`, and final `review_local_heat_movers`.
- `docs/manual-signal-import.md`: update the workflow description.
- `docs/community-signal-quality.md`: update the recommended post-import order.
- `CHANGELOG.md`: add a Stage 60 bullet.

Avoid implying the workflow executes commands or that candidate review uses
workflow `--current-days`/`--baseline-days` options.

- [ ] **Step 4: Verify docs tests pass**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check tests/test_cli_docs.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check tests/test_cli_docs.py
```

Expected: all pass.

---

### Task 4: Verification, Review, Commit, Push

**Files:**

- Create: `docs/reviews/opencode-stage-60-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-60-plan-review.md`
- Create: `docs/reviews/opencode-stage-60-release-review-prompt.md`
- Create: `docs/reviews/opencode-stage-60-release-review.md`

- [ ] **Step 1: Run targeted verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py -q -k "imported_review_workflow or first_run_smoke or cli_docs"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
git diff --check
```

- [ ] **Step 2: Run full release verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
git diff --check
```

- [ ] **Step 3: Installed-wheel smoke**

Build a wheel, install into a temp venv using the mirror for downloads only, and
run:

```bash
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
"$tmp_env/venv/bin/fashion-radar" imported-review-workflow --data-dir "$tmp_data" --config-dir "$tmp_configs" --as-of 2026-06-13T12:00:00Z --source-name "Community Tool Export" --format json
```

Assert installed JSON has:

```python
assert payload["step_count"] == 6
assert payload["steps"][3]["name"] == "review_imported_candidate_phrases"
assert "fashion-radar imported-candidates" in payload["steps"][3]["command"]
assert payload["steps"][-1]["name"] == "review_local_heat_movers"
assert "--source-name" not in payload["steps"][-1]["command"]
```

- [ ] **Step 4: Run opencode release review**

Create `docs/reviews/opencode-stage-60-release-review-prompt.md` and run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-60-release-review-prompt.md)" \
  > docs/reviews/opencode-stage-60-release-review.md \
  2> /tmp/opencode-stage60-release-review.err
```

Fix any Critical or Important findings before proceeding.

- [ ] **Step 5: Commit and push**

Before commit:

```bash
if rg -q 'ghp_[A-Za-z0-9_]+' .; then exit 1; fi
git status --short
git diff --cached --check
```

Commit:

```bash
git add <stage-60-files>
git commit -m "Add imported candidate review workflow step"
```

Push with the saved token through a temporary header only:

```bash
basic_auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 -w0)
git -c http.version=HTTP/1.1 -c http.extraHeader="AUTHORIZATION: basic $basic_auth" push origin main
```

Verify remote SHA and GitHub Actions success through the GitHub API.

- [ ] **Step 6: Handoff Summary**

Write a node-end summary with:

- Repo state
- Verified commands
- Uncommitted files
- Next step
