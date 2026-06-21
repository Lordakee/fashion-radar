# Stage 154 Imported Review Top-Level Field Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `imported-review-workflow` first-run smoke validation reject drift in the top-level `config_dir` and `data_dir` fields.

**Architecture:** Keep runtime imported review workflow output unchanged. Add RED tests for path-field drift that the current command-synthesis logic accepts, then add exact top-level path assertions to the smoke checker and thread expected runtime paths in from `run_smoke(context)` while keeping unit tests fixture-based.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-154-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-154-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-154-plan-review-prompt.md`:

```markdown
# Stage 154 Plan Review Prompt

You are reviewing the Stage 154 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `imported-review-workflow` first-run smoke validation so the top-level `config_dir` and `data_dir` fields are pinned exactly, while the real smoke flow passes its runtime temp paths into the validator explicitly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-154-imported-review-top-level-field-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-154-imported-review-top-level-field-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`

Please review:
- Whether the RED tests isolate the top-level field assertions after command rewrites.
- Whether the validator signature and `run_smoke(context)` call thread expected runtime paths correctly.
- Whether the deterministic smoke-flow test uses temp-path payloads for `imported-review-workflow`.
- Whether existing command-specific and metadata-specific labels remain unchanged.
- Whether direct `python scripts/check_first_run_smoke.py --repo-root .` verification is included.
- Whether runtime behavior remains unchanged.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-154-plan-review-prompt.md)" > /tmp/opencode-stage-154-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-154-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-154-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-154-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add config-dir drift test**

Add this test near the existing imported-review workflow drift tests:

```python
def test_validate_imported_review_workflow_rejects_config_dir_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["config_dir"] = "other-configs"
    replace_workflow_command_fragments(
        payload,
        {"--config-dir configs": "--config-dir other-configs"},
    )

    with pytest.raises(smoke.SmokeError, match="imported-review-workflow config_dir"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

- [ ] **Step 2: Run config-dir RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and config_dir_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator still synthesizes expected commands from the payload path fields.

- [ ] **Step 3: Add data-dir drift test**

Add this test after the config-dir drift test:

```python
def test_validate_imported_review_workflow_rejects_data_dir_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["data_dir"] = "other-data"
    replace_workflow_command_fragments(
        payload,
        {"--data-dir data": "--data-dir other-data"},
    )

    with pytest.raises(smoke.SmokeError, match="imported-review-workflow data_dir"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)
```

- [ ] **Step 4: Run data-dir RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and data_dir_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator still synthesizes expected commands from the payload path fields.

### Task 3: Exact Imported Review Top-Level Field Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add expected path parameters to the validator**

Change `validate_imported_review_workflow()` to:

```python
def validate_imported_review_workflow(
    command_name: str,
    payload: Any,
    *,
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
```

- [ ] **Step 2: Assert exact top-level path fields**

Immediately after the existing `baseline_days` assertion and before command synthesis, add:

```python
    assert_equal(
        f"{command_name} config_dir",
        payload.get("config_dir"),
        expected_config_dir,
    )
    assert_equal(
        f"{command_name} data_dir",
        payload.get("data_dir"),
        expected_data_dir,
    )
```

Then pass `expected_config_dir` and `expected_data_dir` into
`expected_imported_review_workflow_command_parts(...)`.

Remove the now-redundant payload-derived
`config_dir = str(payload.get("config_dir", ""))` and
`data_dir = str(payload.get("data_dir", ""))` locals from the validator so the
expected command synthesis uses only the explicit expected path arguments.

- [ ] **Step 3: Thread runtime paths into the real smoke flow**

In `run_first_run_flow()`, update the imported-review validator call:

```python
    validate_imported_review_workflow(
        "imported-review-workflow",
        imported_review_workflow,
        expected_config_dir=str(context.config_dir),
        expected_data_dir=str(context.data_dir),
    )
```

- [ ] **Step 4: Update the deterministic smoke-flow test payload**

In `test_run_first_run_flow_uses_deterministic_local_command_sequence()`, make the `imported-review-workflow` entry in `stdout_by_command` come from `build_imported_review_workflow(...)` using that test's temp `context` paths:

```python
"imported-review-workflow": build_imported_review_workflow(
    config_dir=context.config_dir,
    data_dir=context.data_dir,
    as_of=smoke.AS_OF,
    source_name=smoke.SOURCE_NAME,
).model_dump_json(),
```

- [ ] **Step 5: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and (config_dir_drift or data_dir_drift)"
```

Expected: both path drift tests pass.

- [ ] **Step 6: Run focused imported-review workflow tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow"
```

Expected: all selected imported-review workflow tests pass.

- [ ] **Step 7: Run deterministic smoke-flow and real smoke script**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "deterministic_local_command_sequence"
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: both pass.

### Task 4: Review, Release Gate, and Commit

**Files:**
- Create: `docs/reviews/opencode-stage-154-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-154-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

- [ ] **Step 2: Run opencode code review**

Create `docs/reviews/opencode-stage-154-code-review-prompt.md` with the same review structure as the plan review prompt, but ask for a code review of the new smoke checker and test changes. Then run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-154-code-review-prompt.md)" > /tmp/opencode-stage-154-code-review.md
```

- [ ] **Step 3: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-154-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-154-code-review.md`.

- [ ] **Step 4: Run the release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
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
  docs/reviews/opencode-stage-154-plan-review-prompt.md \
  docs/reviews/opencode-stage-154-plan-review.md \
  docs/reviews/opencode-stage-154-code-review-prompt.md \
  docs/reviews/opencode-stage-154-code-review.md \
  docs/superpowers/specs/2026-06-22-stage-154-imported-review-top-level-field-exactness-design.md \
  docs/superpowers/plans/2026-06-22-stage-154-imported-review-top-level-field-exactness-plan.md
git commit -m "feat: pin imported review top-level fields"
```
