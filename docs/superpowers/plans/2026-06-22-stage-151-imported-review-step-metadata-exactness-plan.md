# Stage 151 Imported Review Step Metadata Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `imported-review-workflow` first-run smoke validation reject populated but drifted step guidance/effect metadata.

**Architecture:** Keep runtime imported-review workflow output unchanged. Add RED tests for step `purpose` and `suggested_effect` drift that the current name/command validation accepts, then pin each step's `order`, `name`, `purpose`, and `suggested_effect` in the smoke checker.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-151-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-151-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-151-plan-review-prompt.md`:

```markdown
# Stage 151 Plan Review Prompt

You are reviewing the Stage 151 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `imported-review-workflow` first-run smoke validation so each step's `order`, `name`, `purpose`, and `suggested_effect` metadata must match the pinned first-run contract exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-151-imported-review-step-metadata-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-151-imported-review-step-metadata-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact step metadata equality.
- Whether the pinned metadata matches the runtime builder and first-run fixture.
- Whether existing command-argv drift tests still fail through command-specific labels.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-151-plan-review-prompt.md)" > /tmp/opencode-stage-151-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-151-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-151-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-151-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add order drift test**

Add this test after `test_validate_imported_review_workflow_rejects_heat_movers_not_final()`:

```python
def test_validate_imported_review_workflow_rejects_step_order_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[0]["order"] = 99

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

- [ ] **Step 2: Run order RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and order_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts populated order drift.

- [ ] **Step 3: Add purpose drift test**

Add this test after the order drift test:

```python
def test_validate_imported_review_workflow_rejects_step_purpose_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[3]["purpose"] = "Open a browser and collect fresh platform evidence."

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

- [ ] **Step 4: Run purpose RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and purpose_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts populated purpose drift.

- [ ] **Step 5: Add suggested-effect drift test**

Add this test after the purpose drift test:

```python
def test_validate_imported_review_workflow_rejects_step_effect_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[1]["suggested_effect"] = "read_only"

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

- [ ] **Step 6: Run suggested-effect RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and effect_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts populated suggested-effect drift.

### Task 3: Exact Imported-Review Step Metadata Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add expected step metadata constant**

After `EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEPS`, add:

```python
EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEP_METADATA = [
    {
        "order": 1,
        "name": "summarize_imported_sources",
        "purpose": "Summarize retained imported source-name labels.",
        "suggested_effect": "read_only",
    },
    {
        "order": 2,
        "name": "refresh_stored_matches",
        "purpose": "Refresh stored local matches using configured entities.",
        "suggested_effect": "updates_local_matches",
    },
    {
        "order": 3,
        "name": "compare_imported_entities",
        "purpose": "Compare stored matched imported entities across collected-at windows.",
        "suggested_effect": "read_only",
    },
    {
        "order": 4,
        "name": "review_imported_entity_evidence",
        "purpose": "Review retained imported rows behind one selected matched entity.",
        "suggested_effect": "read_only",
    },
    {
        "order": 5,
        "name": "review_imported_candidate_phrases",
        "purpose": (
            "Review observed candidate phrases from retained imported rows after stored "
            "matches are refreshed."
        ),
        "suggested_effect": "read_only",
    },
    {
        "order": 6,
        "name": "review_unmatched_imported_rows",
        "purpose": "Review retained imported rows without stored matches.",
        "suggested_effect": "read_only",
    },
    {
        "order": 7,
        "name": "review_local_heat_movers",
        "purpose": "Review local observed heat movement after imported rows are matched.",
        "suggested_effect": "read_only",
    },
]
```

- [ ] **Step 2: Assert exact step metadata**

In `validate_imported_review_workflow()`, immediately after the existing step-name assertion, add:

```python
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} step {index} must be a JSON object")
    step_metadata = [
        {
            "order": step.get("order"),
            "name": step.get("name"),
            "purpose": step.get("purpose"),
            "suggested_effect": step.get("suggested_effect"),
        }
        for step in steps
    ]
    assert_equal(
        f"{command_name} step metadata",
        step_metadata,
        EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEP_METADATA,
    )
```

- [ ] **Step 3: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and (order_drift or purpose_drift or effect_drift)"
```

Expected: all three metadata drift tests pass.

- [ ] **Step 4: Run focused imported-review workflow tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow"
```

Expected: all selected imported-review workflow tests pass, including existing command drift tests.

### Task 4: Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-151-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-151-code-review.md`

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

Create `docs/reviews/opencode-stage-151-code-review-prompt.md`:

```markdown
# Stage 151 Code Review Prompt

You are reviewing Stage 151 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `imported-review-workflow` first-run smoke validation so each step's `order`, `name`, `purpose`, and `suggested_effect` metadata must match the pinned first-run contract exactly.

Review range:
- Base: `c42f764d9f775ec3cf9ecd75beb4954e7b6f8c7b`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-151-imported-review-step-metadata-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-151-imported-review-step-metadata-exactness-plan.md`
- `docs/reviews/opencode-stage-151-plan-review-prompt.md`
- `docs/reviews/opencode-stage-151-plan-review.md`
- `docs/reviews/opencode-stage-151-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gaps with true RED cases.
- Whether `validate_imported_review_workflow()` now checks exact step metadata equality.
- Whether existing command drift tests still fail through command-specific labels.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-151-code-review-prompt.md)" > /tmp/opencode-stage-151-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-151-code-review.md`.

- [ ] **Step 4: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-151-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-151-code-review.md`.

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
git add docs/superpowers/specs/2026-06-22-stage-151-imported-review-step-metadata-exactness-design.md docs/superpowers/plans/2026-06-22-stage-151-imported-review-step-metadata-exactness-plan.md docs/reviews/opencode-stage-151-plan-review-prompt.md docs/reviews/opencode-stage-151-plan-review.md docs/reviews/opencode-stage-151-code-review-prompt.md docs/reviews/opencode-stage-151-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Pin imported review step metadata"
```

Push with the existing ephemeral auth-header pattern only; do not persist credentials in git config or files.

- [ ] **Step 7: Poll CI**

Poll the GitHub Actions run for the pushed commit until it completes.

Expected: workflow conclusion is `success`.
