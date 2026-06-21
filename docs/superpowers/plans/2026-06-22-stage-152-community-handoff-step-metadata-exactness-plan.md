# Stage 152 Community Handoff Step Metadata Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `community-handoff-workflow` first-run smoke validation reject populated but drifted step guidance and effect metadata.

**Architecture:** Keep runtime community handoff workflow output unchanged. Add RED tests for step `order`, `purpose`, and unchecked `suggested_effect` drift that the current name/command validation accepts, then pin each step's `order`, `name`, `purpose`, and `suggested_effect` in the smoke checker after the current import/post-import effect assertions.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-152-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-152-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-152-plan-review-prompt.md`:

```markdown
# Stage 152 Plan Review Prompt

You are reviewing the Stage 152 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so each step's `order`, `name`, `purpose`, and `suggested_effect` metadata must match the pinned first-run contract exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-152-community-handoff-step-metadata-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-152-community-handoff-step-metadata-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact step metadata equality.
- Whether the pinned metadata matches the runtime builder and first-run fixture.
- Whether existing import/post-import effect tests keep their current more specific failure labels.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-152-plan-review-prompt.md)" > /tmp/opencode-stage-152-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-152-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-152-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-152-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add order drift test**

Add this test after `test_validate_community_handoff_workflow_rejects_unpinned_command_drift()` and before `test_validate_community_handoff_workflow_requires_import_and_review_effects()`:

```python
def test_validate_community_handoff_workflow_rejects_step_order_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[0]["order"] = 99  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 2: Run order RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and order_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts populated order drift.

- [ ] **Step 3: Add purpose drift test**

Add this test after the order drift test:

```python
def test_validate_community_handoff_workflow_rejects_step_purpose_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[2]["purpose"] = "Open a browser and collect fresh platform evidence."  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 4: Run purpose RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and purpose_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts populated purpose drift.

- [ ] **Step 5: Add suggested-effect drift test**

Add this test after the purpose drift test:

```python
def test_validate_community_handoff_workflow_rejects_step_effect_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[1]["suggested_effect"] = "print_only"  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 6: Run suggested-effect RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and effect_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts populated suggested-effect drift for steps 1-4.

### Task 3: Exact Community Handoff Step Metadata Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add expected step metadata constant**

After `EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS`, add:

```python
EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEP_METADATA = [
    {
        "order": 1,
        "name": "lint_handoff_directory",
        "purpose": "Lint local community handoff files before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 2,
        "name": "preview_candidate_phrases",
        "purpose": "Preview aggregate candidate phrases before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 3,
        "name": "review_handoff_readiness",
        "purpose": "Review local handoff readiness before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 4,
        "name": "dry_run_directory_import",
        "purpose": "Validate matched local files through the importer without writing rows.",
        "suggested_effect": "read_only",
    },
    {
        "order": 5,
        "name": "import_directory_signals",
        "purpose": "Import the validated local handoff rows into local SQLite.",
        "suggested_effect": "updates_local_imports",
    },
    {
        "order": 6,
        "name": "print_post_import_review",
        "purpose": "Print the local post-import review checklist.",
        "suggested_effect": "print_only",
    },
]
```

- [ ] **Step 2: Assert exact step metadata**

In `validate_community_handoff_workflow()`, immediately after the existing post-import review effect assertion, add:

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
        EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEP_METADATA,
    )
```

- [ ] **Step 3: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and (order_drift or purpose_drift or effect_drift)"
```

Expected: all three metadata drift tests pass.

- [ ] **Step 4: Run focused community handoff workflow tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow"
```

Expected: all selected community handoff workflow tests pass, including existing command and import/post-review effect tests.

### Task 4: Review, Release Gate, and Commit

**Files:**
- Create: `docs/reviews/opencode-stage-152-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-152-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

- [ ] **Step 2: Run opencode code review**

Create `docs/reviews/opencode-stage-152-code-review-prompt.md`:

```markdown
# Stage 152 Code Review Prompt

You are reviewing Stage 152 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so each step's `order`, `name`, `purpose`, and `suggested_effect` metadata must match the pinned first-run contract exactly.

Review range:
- Base: the commit immediately before the Stage 152 changes
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-152-community-handoff-step-metadata-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-152-community-handoff-step-metadata-exactness-plan.md`
- `docs/reviews/opencode-stage-152-plan-review-prompt.md`
- `docs/reviews/opencode-stage-152-plan-review.md`
- `docs/reviews/opencode-stage-152-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gaps with true RED cases.
- Whether `validate_community_handoff_workflow()` now checks exact step metadata equality.
- Whether existing import/post-import effect tests still fail through their current more specific labels.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

Then run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-152-code-review-prompt.md)" > /tmp/opencode-stage-152-code-review.md
```

- [ ] **Step 3: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-152-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-152-code-review.md`.

- [ ] **Step 4: Run the release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```

- [ ] **Step 5: Commit**

```bash
git add scripts/check_first_run_smoke.py tests/test_first_run_smoke.py \
  docs/reviews/opencode-stage-152-plan-review-prompt.md \
  docs/reviews/opencode-stage-152-plan-review.md \
  docs/reviews/opencode-stage-152-code-review-prompt.md \
  docs/reviews/opencode-stage-152-code-review.md \
  docs/superpowers/specs/2026-06-22-stage-152-community-handoff-step-metadata-exactness-design.md \
  docs/superpowers/plans/2026-06-22-stage-152-community-handoff-step-metadata-exactness-plan.md
git commit -m "feat: pin community handoff step metadata"
```
