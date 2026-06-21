# Stage 145 Community Handoff Step Shape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `community-handoff-workflow` first-run smoke validation reject extra or non-object workflow steps.

**Architecture:** Keep runtime workflow builders unchanged. Add one RED smoke-validator test for an appended command-like non-object tail step, then add exact `steps` list length and all-object validation before names or commands are evaluated.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-145-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-145-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-145-plan-review-prompt.md`:

```markdown
# Stage 145 Plan Review Prompt

You are reviewing the Stage 145 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so the actual `steps` list must contain exactly the six expected JSON object steps, with no ignored extra tail entries.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-145-community-handoff-step-shape-design.md`
- `docs/superpowers/plans/2026-06-21-stage-145-community-handoff-step-shape-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the RED test would fail before implementation and pass after exact list-shape validation.
- Whether the implementation should validate actual `len(steps)` and every step object before deriving step names.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-145-plan-review-prompt.md)" > /tmp/opencode-stage-145-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-145-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-145-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-145-plan-review.md`.

### Task 2: RED Test

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add appended tail-step regression test**

Add this test after `test_validate_community_handoff_workflow_rejects_wrong_readiness_command_argv()`:

```python
def test_validate_community_handoff_workflow_rejects_extra_command_like_tail_step() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps.append("fashion-radar live-collect --platform rednote")

    with pytest.raises(smoke.SmokeError, match="step_count|step 7|JSON object"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "extra_command_like_tail_step"
```

Expected: fail with `DID NOT RAISE` because the current validator ignores the extra non-object tail step.

### Task 3: Strict Step Shape Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add exact length and all-object guards**

In `validate_community_handoff_workflow()`, immediately after:

```python
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
```

add:

```python
    if len(steps) != len(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS):
        raise SmokeError(
            f"{command_name} step_count expected "
            f"{len(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS)!r}, got {len(steps)!r}"
        )
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} step {index} must be a JSON object")
```

Then replace:

```python
    names = [step.get("name") for step in steps if isinstance(step, dict)]
```

with:

```python
    names = [step.get("name") for step in steps]
```

- [ ] **Step 2: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "extra_command_like_tail_step"
```

Expected: pass.

- [ ] **Step 3: Run focused workflow tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow"
```

Expected: all selected community handoff workflow tests pass.

### Task 4: Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-145-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-145-code-review.md`

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

Create `docs/reviews/opencode-stage-145-code-review-prompt.md`:

```markdown
# Stage 145 Code Review Prompt

You are reviewing Stage 145 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so the actual `steps` list must contain exactly the six expected JSON object steps, with no ignored extra tail entries.

Review range:
- Base: `d98d81245929cf871049341ce79a04779929183c`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-21-stage-145-community-handoff-step-shape-design.md`
- `docs/superpowers/plans/2026-06-21-stage-145-community-handoff-step-shape-plan.md`
- `docs/reviews/opencode-stage-145-plan-review-prompt.md`
- `docs/reviews/opencode-stage-145-plan-review.md`
- `docs/reviews/opencode-stage-145-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new test proves the prior gap with a true RED case.
- Whether `validate_community_handoff_workflow()` validates actual step list length and non-object entries before names and commands.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-145-code-review-prompt.md)" > /tmp/opencode-stage-145-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-145-code-review.md`.

- [ ] **Step 4: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-145-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-145-code-review.md`.

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
git add docs/superpowers/specs/2026-06-21-stage-145-community-handoff-step-shape-design.md docs/superpowers/plans/2026-06-21-stage-145-community-handoff-step-shape-plan.md docs/reviews/opencode-stage-145-plan-review-prompt.md docs/reviews/opencode-stage-145-plan-review.md docs/reviews/opencode-stage-145-code-review-prompt.md docs/reviews/opencode-stage-145-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Harden community handoff step shape validation"
```

Push with the existing ephemeral auth-header pattern only; do not persist credentials in git config or files.

- [ ] **Step 7: Poll CI**

Poll the GitHub Actions run for the pushed commit until it completes.

Expected: workflow conclusion is `success`.
