# Stage 150 Display Name Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `external-tool-workflow` and `external-tool-readiness` first-run smoke validation reject populated but drifted `display_name` values.

**Architecture:** Keep runtime workflow/readiness output unchanged. Add a RED parametrized test proving both validators currently accept display-name drift, then pin the shared expected display name in the smoke checker.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-150-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-150-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-150-plan-review-prompt.md`:

```markdown
# Stage 150 Plan Review Prompt

You are reviewing the Stage 150 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-workflow` and `external-tool-readiness` first-run smoke validation so top-level `display_name` must match the pinned first-run contract exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-150-display-name-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-150-display-name-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_workflow.py`
- `src/fashion_radar/external_tool_readiness.py`

Please review:
- Whether the RED test would fail before implementation and pass after exact display-name equality.
- Whether the pinned display name matches the runtime builders and first-run fixtures.
- Whether existing targeted metadata errors remain intact.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-150-plan-review-prompt.md)" > /tmp/opencode-stage-150-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-150-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-150-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-150-plan-review.md`.

### Task 2: RED Test

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add display-name drift test**

Add this test near the external workflow/readiness validator tests, before `test_validate_external_tool_workflow_requires_print_only_workflow_contract()`:

```python
@pytest.mark.parametrize(
    ("payload_fn", "validator", "command_name"),
    [
        (
            external_tool_workflow_payload,
            smoke.validate_external_tool_workflow,
            "external-tool-workflow",
        ),
        (
            external_tool_readiness_payload,
            smoke.validate_external_tool_readiness,
            "external-tool-readiness",
        ),
    ],
)
def test_validate_external_tool_surfaces_reject_display_name_drift(
    payload_fn: Callable[[], dict[str, object]],
    validator: Callable[[str, object], None],
    command_name: str,
) -> None:
    payload = payload_fn()
    payload["display_name"] = "Unexpected Export Label"

    with pytest.raises(smoke.SmokeError, match="display_name"):
        validator(command_name, payload)
```

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "display_name_drift"
```

Expected: both cases fail with `DID NOT RAISE`, because the current validators only require `display_name` to appear in the key order.

### Task 3: Exact Display Name Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add shared expected display-name constant**

Near the external-tool metadata constants, add:

```python
EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME = "Rednote MCP Export"
```

- [ ] **Step 2: Assert exact workflow display name**

In `validate_external_tool_workflow()`, after the existing adapter/platform assertions and before input format assertions, add:

```python
    assert_equal(
        f"{command_name} display_name",
        payload.get("display_name"),
        EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME,
    )
```

- [ ] **Step 3: Assert exact readiness display name**

In `validate_external_tool_readiness()`, after the existing adapter/platform assertions and before input format assertions, add the same assertion:

```python
    assert_equal(
        f"{command_name} display_name",
        payload.get("display_name"),
        EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME,
    )
```

- [ ] **Step 4: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "display_name_drift"
```

Expected: both display-name drift cases pass.

- [ ] **Step 5: Run focused workflow/readiness tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness"
```

Expected: all selected external workflow and readiness tests pass.

### Task 4: Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-150-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-150-code-review.md`

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

Create `docs/reviews/opencode-stage-150-code-review-prompt.md`:

```markdown
# Stage 150 Code Review Prompt

You are reviewing Stage 150 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-workflow` and `external-tool-readiness` first-run smoke validation so top-level `display_name` must match the pinned first-run contract exactly.

Review range:
- Base: `e4a59d0f8da372e5f2b4d8a22275d1ea7c48f50a`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-150-display-name-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-150-display-name-exactness-plan.md`
- `docs/reviews/opencode-stage-150-plan-review-prompt.md`
- `docs/reviews/opencode-stage-150-plan-review.md`
- `docs/reviews/opencode-stage-150-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new test proves the prior gap with true RED cases for both validators.
- Whether both validators now check exact display-name equality.
- Whether existing targeted metadata error messages remain intact.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-150-code-review-prompt.md)" > /tmp/opencode-stage-150-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-150-code-review.md`.

- [ ] **Step 4: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-150-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-150-code-review.md`.

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
git add docs/superpowers/specs/2026-06-22-stage-150-display-name-exactness-design.md docs/superpowers/plans/2026-06-22-stage-150-display-name-exactness-plan.md docs/reviews/opencode-stage-150-plan-review-prompt.md docs/reviews/opencode-stage-150-plan-review.md docs/reviews/opencode-stage-150-code-review-prompt.md docs/reviews/opencode-stage-150-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Pin external tool display names"
```

Push with the existing ephemeral auth-header pattern only; do not persist credentials in git config or files.

- [ ] **Step 7: Poll CI**

Poll the GitHub Actions run for the pushed commit until it completes.

Expected: workflow conclusion is `success`.
