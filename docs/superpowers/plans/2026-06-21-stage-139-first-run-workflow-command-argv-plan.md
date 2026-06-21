# Stage 139 First-Run Workflow Command Argv Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the remaining substring-based first-run workflow command checks with exact argv validation for imported-review and community-handoff workflows.

**Architecture:** Reuse the existing `validate_expected_external_tool_command()` helper in `scripts/check_first_run_smoke.py`. Pull expected argument values from workflow payload top-level metadata instead of hardcoded fixture values so the real smoke run continues to support temporary paths.

**Tech Stack:** Python 3.12, pytest, ruff, uv, `shlex.split()`, existing Fashion Radar first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-139-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-139-plan-review.md`

- [ ] **Step 1: Write the opencode plan review prompt**

Create `docs/reviews/opencode-stage-139-plan-review-prompt.md` with:

```markdown
# Stage 139 Plan Review Prompt

You are reviewing the Stage 139 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Tighten remaining first-run smoke workflow command validators from substring checks to exact argv checks.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-139-first-run-workflow-command-argv-design.md`
- `docs/superpowers/plans/2026-06-21-stage-139-first-run-workflow-command-argv-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the plan preserves runtime CLI behavior.
- Whether expected argv lists match the workflow builders.
- Whether fixture metadata additions mirror real Pydantic payloads.
- Whether the proposed RED tests would fail before implementation and pass after exact validation.

Return a concise review with findings first. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-139-plan-review-prompt.md)" > /tmp/opencode-stage-139-plan-review.md
```

Expected: exit code 0 and a review file in `/tmp/opencode-stage-139-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-139-plan-review.md`. If it contains live narration before the actual review heading, strip that narration. Save the reviewed body to `docs/reviews/opencode-stage-139-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add imported review fixture metadata**

In `imported_review_workflow_payload()`, add the runtime payload fields before `execution_mode`:

```python
"as_of": "2026-06-13T12:00:00+00:00",
"config_dir": "configs",
"data_dir": "data",
"source_name": "Community Tool Export",
"lookback_days": 7,
"current_days": 7,
"baseline_days": 7,
```

Update the imported entity deltas fixture command to include:

```python
"--current-days 7 --baseline-days 7 "
```

Update the imported entity evidence fixture command to include:

```python
"--current-days 7 --baseline-days 7 "
```

- [ ] **Step 2: Add imported-review command drift tests**

Add these tests after `test_validate_imported_review_workflow_rejects_heat_movers_not_final()`:

```python
@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_message"),
    [
        (
            "review_imported_entity_evidence",
            (
                "fashion-radar imported-entity-evidence --data-dir data "
                "--as-of 2026-06-13T12:00:00+00:00 --entity-name 'The Row' "
                "--entity-type brand --current-days 14 --baseline-days 7 "
                "--source-name 'Community Tool Export'"
            ),
            "entity evidence command",
        ),
        (
            "review_imported_candidate_phrases",
            (
                "fashion-radar imported-candidates --config-dir configsets "
                "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                "--source-name 'Community Tool Export'"
            ),
            "candidate command",
        ),
        (
            "review_local_heat_movers",
            (
                "fashion-radar heat-movers-extra --config-dir configs --data-dir data "
                "--as-of 2026-06-13T12:00:00+00:00"
            ),
            "final heat command",
        ),
    ],
)
def test_validate_imported_review_workflow_rejects_command_argv_drift(
    step_name: str,
    replacement_command: str,
    expected_message: str,
) -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    for step in steps:
        assert isinstance(step, dict)
        if step.get("name") == step_name:
            step["command"] = replacement_command
            break
    else:
        pytest.fail(f"missing step {step_name}")

    with pytest.raises(smoke.SmokeError, match=expected_message):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

- [ ] **Step 3: Add community handoff readiness drift test**

Add this test after `test_validate_community_handoff_workflow_rejects_incomplete_readiness_command()`:

```python
def test_validate_community_handoff_workflow_rejects_wrong_readiness_command_argv() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    readiness_step = steps[2]
    assert isinstance(readiness_step, dict)
    readiness_step["command"] = (
        "fashion-radar community-handoff-check-dir-extra /tmp/export "
        "--input-format csv --pattern '*.csv' --config-dir configs "
        "--as-of 2026-06-13T12:00:00+00:00 "
        "--source-name 'Community Tool Export' --strict"
    )

    with pytest.raises(smoke.SmokeError, match="readiness command"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow or community_handoff_workflow"
```

Expected: the newly added drift tests fail because old substring validators accept invalid argv.

### Task 3: Exact Argv Implementation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add local source-name argv construction**

Inside `validate_imported_review_workflow()`, after the step-name assertion, define:

```python
config_dir = str(payload.get("config_dir", ""))
data_dir = str(payload.get("data_dir", ""))
as_of = str(payload.get("as_of", ""))
source_name = str(payload.get("source_name", "") or "")
current_days = str(payload.get("current_days", ""))
baseline_days = str(payload.get("baseline_days", ""))
source_args = ["--source-name", source_name] if source_name else []
```

- [ ] **Step 2: Replace imported entity evidence substring loop**

Replace the `evidence_command` loop with:

```python
validate_expected_external_tool_command(
    command_name,
    "entity evidence",
    evidence_step.get("command", ""),
    "imported-entity-evidence",
    "--data-dir",
    data_dir,
    "--as-of",
    as_of,
    "--entity-name",
    "The Row",
    "--entity-type",
    "brand",
    "--current-days",
    current_days,
    "--baseline-days",
    baseline_days,
    *source_args,
)
```

- [ ] **Step 3: Replace imported candidates substring loop**

Replace the `candidate_command` loop with:

```python
validate_expected_external_tool_command(
    command_name,
    "candidate",
    candidate_step.get("command", ""),
    "imported-candidates",
    "--config-dir",
    config_dir,
    "--data-dir",
    data_dir,
    "--as-of",
    as_of,
    *source_args,
)
```

- [ ] **Step 4: Replace final heat substring checks**

Replace the `heat_command` checks with:

```python
validate_expected_external_tool_command(
    command_name,
    "final heat",
    heat_step.get("command", ""),
    "heat-movers",
    "--config-dir",
    config_dir,
    "--data-dir",
    data_dir,
    "--as-of",
    as_of,
)
```

- [ ] **Step 5: Replace community readiness substring loop**

Inside `validate_community_handoff_workflow()`, after the step-name assertion, define:

```python
directory = str(payload.get("directory", ""))
input_format = str(payload.get("input_format", ""))
pattern = str(payload.get("pattern", ""))
config_dir = str(payload.get("config_dir", ""))
as_of = str(payload.get("as_of", ""))
source_name = str(payload.get("source_name", ""))
```

Replace the readiness substring loop with:

```python
validate_expected_external_tool_command(
    command_name,
    "readiness",
    readiness_step.get("command", ""),
    "community-handoff-check-dir",
    directory,
    "--input-format",
    input_format,
    "--pattern",
    pattern,
    "--config-dir",
    config_dir,
    "--as-of",
    as_of,
    "--source-name",
    source_name,
    "--strict",
)
```

- [ ] **Step 6: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow or community_handoff_workflow"
```

Expected: all selected tests pass.

### Task 4: Focused Verification and Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-139-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-139-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Write code review prompt**

Create `docs/reviews/opencode-stage-139-code-review-prompt.md` with:

```markdown
# Stage 139 Code Review Prompt

You are reviewing Stage 139 changes in `/home/ubuntu/fashion-radar`.

Base commit: `969a0b9c8f6e77c43e42a8d1cbaa8f9ec61f5793`

Review scope:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 139 plan and review docs

Requirements:
- First-run smoke imported-review and community-handoff validators must reject command argv drift, not just missing substrings.
- Runtime CLI builders must not be changed.
- Fixture metadata should mirror real workflow JSON.
- Tests should prove failures that old substring validators missed.

Please report findings first with severity and file/line references. If there are no blocking findings, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-139-code-review-prompt.md)" > /tmp/opencode-stage-139-code-review.md
```

Expected: exit code 0 and a review file in `/tmp/opencode-stage-139-code-review.md`.

- [ ] **Step 4: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-139-code-review.md`. If it contains live narration before the actual review heading, strip that narration. Save the reviewed body to `docs/reviews/opencode-stage-139-code-review.md`.

### Task 5: Release Gate, Commit, Push, CI

**Files:**
- Commit all Stage 139 files after verification and review.

- [ ] **Step 1: Run release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```

Expected: all commands exit 0, token scan finds no token, and persistent auth scan prints nothing before exiting 0.

- [ ] **Step 2: Commit Stage 139**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-21-stage-139-first-run-workflow-command-argv-design.md docs/superpowers/plans/2026-06-21-stage-139-first-run-workflow-command-argv-plan.md docs/reviews/opencode-stage-139-plan-review-prompt.md docs/reviews/opencode-stage-139-plan-review.md docs/reviews/opencode-stage-139-code-review-prompt.md docs/reviews/opencode-stage-139-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Harden remaining workflow command validators"
```

Expected: commit succeeds.

- [ ] **Step 3: Push with ephemeral auth**

Use an ephemeral HTTP extraheader only for the push. Do not save the token or auth header in git config.

Run:

```bash
git -c http.https://github.com/.extraheader="$AUTH_HEADER" push origin main
git config --get-all http.https://github.com/.extraheader || true
```

Expected: push succeeds, and the second command prints nothing.

- [ ] **Step 4: Poll CI**

Run:

```bash
gh run list --repo Lordakee/fashion-radar --branch main --limit 5
```

Poll the new run until it completes. Expected conclusion: `success`.

- [ ] **Step 5: Handoff Summary**

Write a concise handoff with:

```markdown
**Handoff Summary**

- Repo status:
- Verified commands:
- Uncommitted files:
- Next step:
```
