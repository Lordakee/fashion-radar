# Stage 153 Community Handoff Top-Level Field Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `community-handoff-workflow` first-run smoke validation reject drift in the top-level `directory`, `config_dir`, and `data_dir` fields.

**Architecture:** Keep runtime community handoff workflow output unchanged. Add RED tests for top-level path-field drift that the current command-synthesis logic accepts, then add exact top-level path assertions to the smoke checker and thread the expected runtime paths in from `run_smoke(context)` while keeping the unit tests fixture-based.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-153-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-153-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-153-plan-review-prompt.md`:

```markdown
# Stage 153 Plan Review Prompt

You are reviewing the Stage 153 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so the top-level `directory`, `config_dir`, and `data_dir` fields are pinned exactly, while the real smoke flow passes its runtime temp paths into the validator explicitly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-153-community-handoff-top-level-field-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-153-community-handoff-top-level-field-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact field assertions are added.
- Whether the pinned field values match the runtime builder and first-run fixture.
- Whether the validator receives the real runtime paths from `run_smoke(context)`.
- Whether existing command-specific and effect-specific labels remain unchanged.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-153-plan-review-prompt.md)" > /tmp/opencode-stage-153-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-153-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-153-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-153-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add directory drift test**

Add this test after `test_validate_community_handoff_workflow_rejects_coordinated_metadata_command_drift()` and before `test_validate_community_handoff_workflow_rejects_unpinned_command_drift()`:

```python
def test_validate_community_handoff_workflow_rejects_directory_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["directory"] = "/tmp/other-export"
    replace_workflow_command_fragments(
        payload,
        {"/tmp/export": "/tmp/other-export"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow directory"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 2: Run directory RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and directory_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator still synthesizes expected commands from the payload path fields.

- [ ] **Step 3: Add config-dir drift test**

Add this test after the directory drift test:

```python
def test_validate_community_handoff_workflow_rejects_config_dir_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["config_dir"] = "other-configs"
    replace_workflow_command_fragments(
        payload,
        {"--config-dir configs": "--config-dir other-configs"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow config_dir"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 4: Run config-dir RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and config_dir_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator still synthesizes expected commands from the payload path fields.

- [ ] **Step 5: Add data-dir drift test**

Add this test after the config-dir drift test:

```python
def test_validate_community_handoff_workflow_rejects_data_dir_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["data_dir"] = "other-data"
    replace_workflow_command_fragments(
        payload,
        {"--data-dir data": "--data-dir other-data"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow data_dir"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [ ] **Step 6: Run data-dir RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and data_dir_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator still synthesizes expected commands from the payload path fields.

### Task 3: Exact Community Handoff Top-Level Field Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add expected path parameters to the validator**

Change the `validate_community_handoff_workflow()` signature to accept fixture defaults for unit tests and caller-supplied runtime paths for the real smoke flow:

```python
def validate_community_handoff_workflow(
    command_name: str,
    payload: Any,
    *,
    expected_directory: str = "/tmp/export",
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
```

- [ ] **Step 2: Assert exact top-level path fields**

In `validate_community_handoff_workflow()`, immediately after the existing `source_name` assertion and before `expected_community_handoff_workflow_command_parts(...)`, add:

```python
    assert_equal(
        f"{command_name} directory",
        payload.get("directory"),
        expected_directory,
    )
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

Then replace the payload-derived path inputs in `expected_community_handoff_workflow_command_parts(...)` with the expected path parameters:

```python
    expected_commands = expected_community_handoff_workflow_command_parts(
        directory=expected_directory,
        input_format=input_format,
        pattern=pattern,
        config_dir=expected_config_dir,
        data_dir=expected_data_dir,
        as_of=as_of,
        source_name=source_name,
    )
```

- [ ] **Step 3: Thread runtime paths into the real smoke flow**

In `run_first_run_flow()`, update the `validate_community_handoff_workflow(...)` call to pass the actual temporary smoke paths:

```python
    validate_community_handoff_workflow(
        "community-handoff-workflow",
        community_handoff_workflow,
        expected_directory=str(context.exports_dir),
        expected_config_dir=str(context.config_dir),
        expected_data_dir=str(context.data_dir),
    )
```

- [ ] **Step 4: Update the deterministic smoke-flow test payload**

In `test_run_first_run_flow_uses_deterministic_local_command_sequence()`, make the `community-handoff-workflow` entry in `stdout_by_command` come from `build_community_handoff_workflow(...)` using that test's temp `context` paths instead of the fixed `community_handoff_workflow_payload()` fixture. Keep the other command payloads unchanged.

```python
"community-handoff-workflow": build_community_handoff_workflow(
    directory=context.exports_dir,
    config_dir=context.config_dir,
    data_dir=context.data_dir,
    input_format="csv",
    pattern=smoke.DIR_PATTERN,
    as_of=smoke.AS_OF,
    source_name=smoke.SOURCE_NAME,
).model_dump_json(),
```

- [ ] **Step 5: Run the deterministic smoke-flow test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "deterministic_local_command_sequence"
```

Expected: pass with the updated temp-path payload.

- [ ] **Step 6: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow and (directory_drift or config_dir_drift or data_dir_drift)"
```

Expected: all three path drift tests pass.

- [ ] **Step 7: Run focused community handoff workflow tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow"
```

Expected: all selected community handoff workflow tests pass, including existing command, metadata, and effect tests.

- [ ] **Step 8: Run the real first-run smoke script**

Run:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: exits 0 with `First-run sample smoke passed.`

### Task 4: Review, Release Gate, and Commit

**Files:**
- Create: `docs/reviews/opencode-stage-153-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-153-code-review.md`

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

Create `docs/reviews/opencode-stage-153-code-review-prompt.md` with the same review structure as the plan review prompt, but ask for a code review of the new smoke checker and test changes. Then run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-153-code-review-prompt.md)" > /tmp/opencode-stage-153-code-review.md
```

- [ ] **Step 3: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-153-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-153-code-review.md`.

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
  docs/reviews/opencode-stage-153-plan-review-prompt.md \
  docs/reviews/opencode-stage-153-plan-review.md \
  docs/reviews/opencode-stage-153-code-review-prompt.md \
  docs/reviews/opencode-stage-153-code-review.md \
  docs/superpowers/specs/2026-06-22-stage-153-community-handoff-top-level-field-exactness-design.md \
  docs/superpowers/plans/2026-06-22-stage-153-community-handoff-top-level-field-exactness-plan.md
git commit -m "feat: pin community handoff top-level fields"
```
