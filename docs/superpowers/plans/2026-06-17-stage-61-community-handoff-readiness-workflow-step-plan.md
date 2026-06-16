# Stage 61 Community Handoff Readiness Workflow Step Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the existing local-only `community-handoff-check-dir` command as a read-only readiness report step inside the print-only `community-handoff-workflow`.

**Architecture:** Reuse the existing `CommunityHandoffWorkflowStep` model and shell-command rendering. Add exactly one generated command string in `build_community_handoff_workflow`; update tests, smoke validation, embedded manifest expectations, and docs to recognize the six-step workflow. Do not add runtime data access to the workflow builder.

**Tech Stack:** Python 3.11, Typer CLI, Pydantic models, pytest, ruff, uv. No new dependencies.

---

## File Structure

- Modify `src/fashion_radar/community_handoff_workflow.py`: add one read-only step and renumber later steps.
- Modify `tests/test_community_handoff_workflow.py`: builder and renderer expectations.
- Modify `tests/test_cli.py`: CLI JSON/table/no-side-effect tests and manifest embedded workflow expectations.
- Modify `tests/test_community_handoff_manifest.py`: manifest embedded workflow model expectations.
- Modify `scripts/check_first_run_smoke.py`: JSON validation for `community-handoff-workflow`.
- Modify `tests/test_first_run_smoke.py`: fake stdout and captured command expectations.
- Modify `tests/test_cli_docs.py`: docs drift expectations, especially manifest workflow assertions.
- Modify docs: `README.md`, `docs/cli-reference.md`, `docs/community-signal-import.md`, `docs/community-signal-quality.md`, `docs/first-run.md`, `docs/architecture.md`, `docs/source-boundaries.md`, `docs/github-upload-checklist.md`, `CHANGELOG.md`.
- Add review artifacts under `docs/reviews/` after opencode plan/release reviews.

## Task 1: Red Tests For Workflow Builder

**Files:**
- Modify: `tests/test_community_handoff_workflow.py`

- [ ] **Step 1: Update deterministic builder expectations**

In `test_build_community_handoff_workflow_returns_deterministic_steps`, change
the expected shape to six steps:

```python
assert workflow.step_count == 6
assert [step.order for step in workflow.steps] == [1, 2, 3, 4, 5, 6]
assert [step.name for step in workflow.steps] == [
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert [step.suggested_effect for step in workflow.steps] == [
    "read_only",
    "read_only",
    "read_only",
    "read_only",
    "updates_local_imports",
    "print_only",
]
```

Add the new command expectation immediately after the candidate preview command:

```python
assert workflow.steps[2].command == (
    "fashion-radar community-handoff-check-dir exports --input-format csv "
    "--pattern '*.csv' --config-dir configs --as-of 2026-06-13T12:00:00+00:00 "
    "--source-name 'Community Tool Export' --strict"
)
```

Renumber the dry-run command to `workflow.steps[3]`, the import command to
`workflow.steps[4]`, and the post-import review command to `workflow.steps[5]`.

- [ ] **Step 2: Update quoting expectations**

In `test_build_community_handoff_workflow_quotes_paths_pattern_and_source_name`,
assert the readiness command quotes directory/config/pattern/source:

```python
assert "'exports ? # & %'" in workflow.steps[2].command
assert "--pattern '*.json'" in workflow.steps[2].command
assert "--config-dir 'config ? # & %'" in workflow.steps[2].command
assert "--source-name 'Community | Tool Export'" in workflow.steps[2].command
```

- [ ] **Step 3: Run the red test**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_workflow.py -q
```

Expected: fail because `review_handoff_readiness` is not yet generated and
`step_count` is still 5.

## Task 2: Implement Workflow Step

**Files:**
- Modify: `src/fashion_radar/community_handoff_workflow.py`

- [ ] **Step 1: Add the readiness step**

Insert this `CommunityHandoffWorkflowStep` after the candidate preview step and
before the dry-run step:

```python
CommunityHandoffWorkflowStep(
    order=3,
    name="review_handoff_readiness",
    purpose="Review the local-only handoff readiness report before importing rows.",
    command=_shell_command(
        "fashion-radar",
        "community-handoff-check-dir",
        directory_text,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--config-dir",
        config_text,
        "--as-of",
        as_of_text,
        "--source-name",
        source_text,
        "--strict",
    ),
    suggested_effect="read_only",
),
```

Renumber `dry_run_directory_import` to `order=4`,
`import_directory_signals` to `order=5`, and
`print_post_import_review` to `order=6`.

- [ ] **Step 2: Run the green test**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_workflow.py -q
```

Expected: all tests in that file pass.

- [ ] **Step 3: Run format/lint on touched files**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/community_handoff_workflow.py tests/test_community_handoff_workflow.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/community_handoff_workflow.py tests/test_community_handoff_workflow.py
```

Expected: both pass.

## Task 3: Update CLI, Manifest, And Smoke Tests

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `tests/test_community_handoff_manifest.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Update CLI workflow JSON expectations**

In `test_community_handoff_workflow_command_prints_json_with_stable_keys`,
change `step_count` to 6, add `review_handoff_readiness` to the expected step
names, assert step 3 is read-only and contains the readiness command, and move
the write-step assertion to index 4:

```python
assert payload["step_count"] == 6
assert [step["name"] for step in payload["steps"]] == [
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert payload["steps"][2]["suggested_effect"] == "read_only"
assert "fashion-radar community-handoff-check-dir" in payload["steps"][2]["command"]
assert "--strict" in payload["steps"][2]["command"]
assert payload["steps"][4]["suggested_effect"] == "updates_local_imports"
```

- [ ] **Step 2: Update CLI table/no-side-effect tests**

In `test_community_handoff_workflow_command_prints_table_without_artifacts`,
assert the table includes `community-handoff-check-dir` and
`review_handoff_readiness`.

In `test_community_handoff_workflow_does_not_read_directory_or_run_side_effects`,
keep the existing path/subprocess guards and assert the printed output contains
`community-handoff-check-dir`. Do not add any real directory reads.

- [ ] **Step 3: Update manifest embedded workflow expectations**

In `tests/test_cli.py`,
`test_community_handoff_manifest_command_prints_json_with_stable_keys`, change:

```python
assert payload["workflow"]["step_count"] == 6
assert payload["workflow"]["steps"][2]["name"] == "review_handoff_readiness"
assert "community-handoff-check-dir" in payload["workflow"]["steps"][2]["command"]
```

Keep the existing no-artifact assertions for the manifest CLI test.

In `tests/test_community_handoff_manifest.py`, update
`test_build_community_handoff_manifest_has_stable_directory_contract`:

```python
assert manifest.workflow.step_count == 6
assert [step.name for step in manifest.workflow.steps] == [
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert "community-handoff-check-dir" in manifest.workflow.steps[2].command
```

Update
`test_build_community_handoff_manifest_uses_json_filename_and_quotes_workflow`
so the `--data-dir` assertion points at `manifest.workflow.steps[3].command`,
and add quote checks for the readiness command:

```python
assert "'exports ? # & %'" in manifest.workflow.steps[2].command
assert "--pattern '*.json'" in manifest.workflow.steps[2].command
assert "--config-dir 'config ? # & %'" in manifest.workflow.steps[2].command
assert "--source-name 'Community | Tool Export'" in manifest.workflow.steps[2].command
assert "--data-dir 'data ? # & %'" in manifest.workflow.steps[3].command
```

- [ ] **Step 4: Extend first-run smoke JSON validation**

In `scripts/check_first_run_smoke.py`, add:

```python
EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS = (
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
)
```

Add a validator:

```python
def validate_community_handoff_workflow(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 6)
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    names = [step.get("name") for step in steps if isinstance(step, dict)]
    assert_equal(
        f"{command_name} step names",
        names,
        list(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS),
    )
    readiness_step = steps[2]
    if not isinstance(readiness_step, dict):
        raise SmokeError(f"{command_name} readiness step must be a JSON object")
    readiness_command = str(readiness_step.get("command", ""))
    for expected in (
        "fashion-radar community-handoff-check-dir",
        "--input-format",
        "--pattern",
        "--config-dir",
        "--as-of",
        "--source-name",
        "--strict",
        SOURCE_NAME,
    ):
        if expected not in readiness_command:
            raise SmokeError(f"{command_name} readiness command missing {expected!r}")
```

Change the first-run `community-handoff-workflow` invocation to use
`--format json`, parse it with `validate_json_output`, and call the validator.

- [ ] **Step 5: Add focused first-run smoke validator tests**

In `tests/test_first_run_smoke.py`, add a helper next to the existing fake JSON
payload helpers:

```python
def community_handoff_workflow_payload() -> dict[str, object]:
    return {
        "execution_mode": "print_only",
        "step_count": 6,
        "steps": [
            {"name": "lint_handoff_directory", "command": "fashion-radar community-signal-lint-dir"},
            {"name": "preview_candidate_phrases", "command": "fashion-radar community-candidates-dir"},
            {
                "name": "review_handoff_readiness",
                "command": (
                    "fashion-radar community-handoff-check-dir "
                    "--input-format csv --pattern '*.csv' --config-dir configs "
                    "--as-of 2026-06-13T12:00:00Z --source-name "
                    "'Community Tool Export' --strict"
                ),
            },
            {"name": "dry_run_directory_import", "command": "fashion-radar import-signals-dir --dry-run"},
            {"name": "import_directory_signals", "command": "fashion-radar import-signals-dir"},
            {"name": "print_post_import_review", "command": "fashion-radar imported-review-workflow"},
        ],
    }
```

Add a positive validator test:

```python
def test_validate_community_handoff_workflow_accepts_six_step_readiness_shape() -> None:
    smoke.validate_community_handoff_workflow(
        "community-handoff-workflow",
        community_handoff_workflow_payload(),
    )
```

Add a negative validator test:

```python
def test_validate_community_handoff_workflow_rejects_missing_readiness_command() -> None:
    payload = community_handoff_workflow_payload()
    steps = list(payload["steps"])
    readiness_step = dict(steps[2])
    readiness_step["command"] = "fashion-radar community-handoff-check-dir --strict"
    steps[2] = readiness_step
    payload["steps"] = steps

    with pytest.raises(smoke.SmokeError, match="readiness command missing '--source-name'"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 6: Update first-run smoke command-sequence tests**

In `tests/test_first_run_smoke.py`, update fake stdout for
`community-handoff-workflow` to:

```python
"community-handoff-workflow": json.dumps(community_handoff_workflow_payload()),
```

Update captured-command assertions to expect `--format json` on
`community-handoff-workflow`.

- [ ] **Step 7: Run the focused test group**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_community_handoff_manifest.py tests/test_first_run_smoke.py -q -k "community_handoff or first_run_smoke"
```

Expected: tests pass after implementation.

## Task 4: Update Docs And Docs Drift Tests

**Files:**
- Modify: `tests/test_cli_docs.py`
- Modify: `README.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/first-run.md`
- Modify: `docs/architecture.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update docs drift tests**

In `test_community_handoff_check_dir_docs_are_linked_and_bounded`, replace the
old assertions that `community-handoff-check-dir` is absent from documented and
generated workflow steps with assertions that the embedded workflow includes the
new step:

```python
assert any("review_handoff_readiness" in text for text in documented_step_text)
assert any("community-handoff-check-dir" in text for text in documented_step_text)
assert any("review_handoff_readiness" in text for text in generated_step_text)
assert any("community-handoff-check-dir" in text for text in generated_step_text)
```

In the same test, add required phrases for focused docs:

```python
required_workflow_phrases = (
    "review_handoff_readiness",
    "local-only handoff readiness report",
    "before importing rows",
    "does not execute commands",
)
```

- [ ] **Step 2: Update docs prose**

Update docs to say `community-handoff-workflow` now prints the ordered local
sequence:

1. lint handoff directory
2. preview candidate phrases
3. review local-only handoff readiness
4. dry-run directory import
5. import directory signals
6. print post-import review

Keep boundary language explicit: no platform/source acquisition, scraping,
login, scheduling, monitoring, platform APIs, media download, connector, demand
proof, ranking, coverage verification, entity generation, compliance review,
policy review, authorization review, or safety-review product feature.

- [ ] **Step 3: Update GitHub upload checklist**

In `docs/github-upload-checklist.md`, update the community handoff workflow
checklist expectation to include `review_handoff_readiness`,
`community-handoff-check-dir`, and `step_count == 6` for the community workflow.
Add a short installed-wheel JSON assertion block immediately after the existing
installed-wheel `community-handoff-workflow --format json` command:

```bash
"$tmp_env/venv/bin/fashion-radar" community-handoff-workflow "$tmp_run/missing ? # & %" --input-format csv --pattern "*.csv" --config-dir "$tmp_run/config ? # & %" --data-dir "$tmp_run/data ? # & %" --as-of "2026-06-13T12:00:00Z" --format json > "$tmp_run/community-handoff-workflow.json"
"$tmp_env/venv/bin/python" - "$tmp_run/community-handoff-workflow.json" <<'PY'
import json
import sys
from pathlib import Path

workflow_json = Path(sys.argv[1]).read_text(encoding="utf-8")
payload = json.loads(workflow_json)
assert payload["step_count"] == 6
assert payload["steps"][2]["name"] == "review_handoff_readiness"
assert "community-handoff-check-dir" in payload["steps"][2]["command"]
PY
```

- [ ] **Step 4: Run docs tests**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: all docs drift tests pass.

## Task 5: Review, Full Verification, Commit, Push

**Files:**
- Add: `docs/reviews/opencode-stage-61-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-61-release-review.md`

- [ ] **Step 1: Run targeted verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py -q -k "community_handoff_workflow or community_handoff_check_dir or first_run_smoke or cli_docs"
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/community_handoff_workflow.py tests/test_community_handoff_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/community_handoff_workflow.py tests/test_community_handoff_workflow.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
git diff --check
```

Expected: all pass.

- [ ] **Step 2: Request opencode release review**

Create `docs/reviews/opencode-stage-61-release-review-prompt.md` with:

- Stage 61 objective and non-goals.
- Base commit.
- Current diff target.
- Verification commands and outcomes.
- Request for Critical/Important/Minor findings.

Run:

```bash
NO_COLOR=1 opencode run --dir /home/ubuntu/fashion-radar --model zhipuai-coding-plan/glm-5.2 --variant max "Follow the attached Stage 61 release review prompt exactly. Do not edit files." --file docs/reviews/opencode-stage-61-release-review-prompt.md
```

Expected: `APPROVED FOR STAGE 61 RELEASE`, with no Critical or Important
findings. Fix any Critical/Important findings before continuing.

- [ ] **Step 3: Run full verification**

Run:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv sync --locked --dev --check
env -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
```

Also verify:

```bash
rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --exit-code -- uv.lock pyproject.toml
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

The mirror scan should return no matches.

- [ ] **Step 4: Package smoke**

Build and validate package archives, install the wheel into a temporary venv
using the Tsinghua mirror for dependency resolution, run installed first-run
smoke, and assert installed `community-handoff-workflow --format json` reports
six steps with step 3 `review_handoff_readiness`.

- [ ] **Step 5: Stage, token scan, commit, push, and CI**

Run:

```bash
git add -A
git diff --cached --check
git grep --cached -n -E 'ghp_[A-Za-z0-9_]+'
git commit -m "Add community handoff readiness workflow step"
```

The token scan should return no matches. Push with the saved token using an
HTTP auth header, not by writing the token into `origin`:

```bash
basic_auth="$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 -w0)"
git -c http.version=HTTP/1.1 -c http.extraHeader="AUTHORIZATION: basic $basic_auth" push origin main
```

Verify `origin/main` matches local HEAD and GitHub Actions completes
successfully.
