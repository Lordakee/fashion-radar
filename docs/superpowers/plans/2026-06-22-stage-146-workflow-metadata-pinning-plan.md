# Stage 146 Workflow Metadata Pinning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make imported-review and community-handoff workflow smoke validators reject coordinated drift between top-level metadata and step command strings.

**Architecture:** Keep runtime workflow builders unchanged. Add RED tests that mutate metadata and matching command strings together, then pin first-run smoke semantic metadata in `scripts/check_first_run_smoke.py` before exact argv validation.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-146-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-146-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-146-plan-review-prompt.md`:

```markdown
# Stage 146 Plan Review Prompt

You are reviewing the Stage 146 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden first-run workflow smoke validators so coordinated drift between top-level semantic metadata and step command strings is rejected.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-146-workflow-metadata-pinning-design.md`
- `docs/superpowers/plans/2026-06-22-stage-146-workflow-metadata-pinning-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the two RED tests would fail before implementation and pass after metadata pinning.
- Whether the implementation should keep path fields (`directory`, `config_dir`, `data_dir`) payload-derived.
- Whether the proposed pinned constants match the first-run smoke fixtures and runtime default workflows.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-146-plan-review-prompt.md)" > /tmp/opencode-stage-146-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-146-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-146-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-146-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add command rewrite helper**

Add this helper near the workflow payload helpers:

```python
def replace_workflow_command_fragments(
    payload: dict[str, object],
    replacements: dict[str, str],
) -> None:
    steps = payload["steps"]
    assert isinstance(steps, list)
    for step in steps:
        assert isinstance(step, dict)
        command = step.get("command")
        assert isinstance(command, str)
        for old, new in replacements.items():
            command = command.replace(old, new)
        step["command"] = command
```

- [ ] **Step 2: Add imported review coordinated drift test**

Add this test after `test_validate_imported_review_workflow_rejects_command_argv_drift()`:

```python
def test_validate_imported_review_workflow_rejects_coordinated_metadata_command_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["source_name"] = "Other Source"
    payload["as_of"] = "2026-06-14T12:00:00+00:00"
    payload["lookback_days"] = 14
    payload["current_days"] = 14
    payload["baseline_days"] = 21
    replace_workflow_command_fragments(
        payload,
        {
            "2026-06-13T12:00:00+00:00": "2026-06-14T12:00:00+00:00",
            "'Community Tool Export'": "'Other Source'",
            "--lookback-days 7": "--lookback-days 14",
            "--current-days 7": "--current-days 14",
            "--baseline-days 7": "--baseline-days 21",
        },
    )

    with pytest.raises(
        smoke.SmokeError,
        match="source_name|as_of|lookback_days|current_days|baseline_days",
    ):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

- [ ] **Step 3: Add community handoff coordinated drift test**

Add this test after `test_validate_community_handoff_workflow_rejects_extra_command_like_tail_step()`:

```python
def test_validate_community_handoff_workflow_rejects_coordinated_metadata_command_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["source_name"] = "Other Source"
    payload["as_of"] = "2026-06-14T12:00:00+00:00"
    payload["input_format"] = "json"
    payload["pattern"] = "*.json"
    replace_workflow_command_fragments(
        payload,
        {
            "2026-06-13T12:00:00+00:00": "2026-06-14T12:00:00+00:00",
            "'Community Tool Export'": "'Other Source'",
            "--input-format csv": "--input-format json",
            "--format csv": "--format json",
            "'*.csv'": "'*.json'",
        },
    )

    with pytest.raises(
        smoke.SmokeError,
        match="source_name|as_of|input_format|pattern",
    ):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "coordinated_metadata_command_drift"
```

Expected: both tests fail with `DID NOT RAISE` because the current validators accept internally consistent metadata and command drift.

### Task 3: Pin Workflow Metadata

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add pinned metadata constants**

Near the existing constants, add:

```python
EXPECTED_WORKFLOW_AS_OF = "2026-06-13T12:00:00+00:00"
EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT = "csv"
EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS = 7
EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS = 7
EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS = 7
```

- [ ] **Step 2: Pin imported review workflow semantic metadata**

In `validate_imported_review_workflow()`, after the step names assertion and before command expectations are built, add:

```python
    assert_equal(f"{command_name} as_of", payload.get("as_of"), EXPECTED_WORKFLOW_AS_OF)
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    assert_equal(
        f"{command_name} lookback_days",
        payload.get("lookback_days"),
        EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS,
    )
    assert_equal(
        f"{command_name} current_days",
        payload.get("current_days"),
        EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS,
    )
    assert_equal(
        f"{command_name} baseline_days",
        payload.get("baseline_days"),
        EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS,
    )
```

Then replace:

```python
    as_of = str(payload.get("as_of", ""))
    source_name = str(payload.get("source_name", "") or "")
    lookback_days = str(payload.get("lookback_days", ""))
    current_days = str(payload.get("current_days", ""))
    baseline_days = str(payload.get("baseline_days", ""))
```

with:

```python
    as_of = EXPECTED_WORKFLOW_AS_OF
    source_name = SOURCE_NAME
    lookback_days = str(EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS)
    current_days = str(EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS)
    baseline_days = str(EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS)
```

- [ ] **Step 3: Pin community handoff workflow semantic metadata**

In `validate_community_handoff_workflow()`, after the step names assertion and before command expectations are built, add:

```python
    assert_equal(
        f"{command_name} input_format",
        payload.get("input_format"),
        EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT,
    )
    assert_equal(f"{command_name} pattern", payload.get("pattern"), DIR_PATTERN)
    assert_equal(f"{command_name} as_of", payload.get("as_of"), EXPECTED_WORKFLOW_AS_OF)
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
```

Then replace the semantic assignments while keeping `directory`, `config_dir`, and `data_dir` payload-derived. The source currently interleaves semantic and path assignments, so make this as two small edits or reorder the assignment block.

Replace:

```python
    input_format = str(payload.get("input_format", ""))
    pattern = str(payload.get("pattern", ""))
```

with:

```python
    input_format = EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT
    pattern = DIR_PATTERN
```

Then replace:

```python
    as_of = str(payload.get("as_of", ""))
    source_name = str(payload.get("source_name", ""))
```

with:

```python
    as_of = EXPECTED_WORKFLOW_AS_OF
    source_name = SOURCE_NAME
```

- [ ] **Step 4: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "coordinated_metadata_command_drift"
```

Expected: both tests pass.

- [ ] **Step 5: Run focused workflow tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow or community_handoff_workflow"
```

Expected: all selected imported-review and community-handoff workflow tests pass.

### Task 4: Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-146-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-146-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Write opencode code review prompt**

Create `docs/reviews/opencode-stage-146-code-review-prompt.md`:

```markdown
# Stage 146 Code Review Prompt

You are reviewing Stage 146 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden first-run workflow smoke validators so coordinated drift between top-level semantic metadata and step command strings is rejected.

Review range:
- Base: `3b7960e1e845251b207c3d8bbf3899517bd2ecad`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-146-workflow-metadata-pinning-design.md`
- `docs/superpowers/plans/2026-06-22-stage-146-workflow-metadata-pinning-plan.md`
- `docs/reviews/opencode-stage-146-plan-review-prompt.md`
- `docs/reviews/opencode-stage-146-plan-review.md`
- `docs/reviews/opencode-stage-146-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gap with true RED cases.
- Whether the validators pin semantic metadata but keep path fields payload-derived.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-146-code-review-prompt.md)" > /tmp/opencode-stage-146-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-146-code-review.md`.

- [ ] **Step 4: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-146-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-146-code-review.md`.

- [ ] **Step 5: Run release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```

Expected: all commands exit 0 and token/auth checks print no secret findings.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-22-stage-146-workflow-metadata-pinning-design.md docs/superpowers/plans/2026-06-22-stage-146-workflow-metadata-pinning-plan.md docs/reviews/opencode-stage-146-plan-review-prompt.md docs/reviews/opencode-stage-146-plan-review.md docs/reviews/opencode-stage-146-code-review-prompt.md docs/reviews/opencode-stage-146-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Pin workflow smoke metadata validation"
```

Push with the existing ephemeral auth-header pattern only; do not persist credentials in git config or files.

- [ ] **Step 7: Poll CI**

Poll the GitHub Actions run for the pushed commit until it completes.

Expected: workflow conclusion is `success`.
