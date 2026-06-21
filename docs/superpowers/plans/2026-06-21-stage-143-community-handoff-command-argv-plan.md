# Stage 143 Community Handoff Command Argv Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `community-handoff-workflow` first-run smoke validation reject command drift for every workflow step.

**Architecture:** Keep runtime workflow builders unchanged. Add one expected-command helper to the smoke checker, add a RED parametrized drift test for the five currently unpinned commands, then replace the one-off readiness command validation with an exact argv loop for all six steps.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-143-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-143-plan-review.md`

- [x] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-143-plan-review-prompt.md`:

```markdown
# Stage 143 Plan Review Prompt

You are reviewing the Stage 143 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `community-handoff-workflow` first-run smoke validation so all six workflow step commands must match exact argv, not only the readiness step.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-143-community-handoff-command-argv-design.md`
- `docs/superpowers/plans/2026-06-21-stage-143-community-handoff-command-argv-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the expected argv parts match `build_community_handoff_workflow()`.
- Whether the RED test would fail before implementation and pass after exact argv validation.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [x] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-143-plan-review-prompt.md)" > /tmp/opencode-stage-143-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-143-plan-review.md`.

- [x] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-143-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-143-plan-review.md`.

### Task 2: RED Test

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [x] **Step 1: Add unpinned community handoff command drift test**

Add near the existing `community_handoff_workflow` validator tests:

```python
@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_message"),
    [
        (
            "lint_handoff_directory",
            (
                "fashion-radar community-signal-lint-dir /tmp/export "
                "--input-format csv --pattern '*.csv' "
                "--source-name 'Community Tool Export'"
            ),
            "lint_handoff_directory command",
        ),
        (
            "preview_candidate_phrases",
            (
                "fashion-radar community-candidates-dir-extra /tmp/export "
                "--input-format csv --pattern '*.csv' --config-dir configs "
                "--as-of 2026-06-13T12:00:00+00:00 "
                "--source-name 'Community Tool Export'"
            ),
            "preview_candidate_phrases command",
        ),
        (
            "dry_run_directory_import",
            (
                "fashion-radar import-signals-dir /tmp/export --format csv "
                "--pattern '*.csv' --data-dir data "
                "--source-name 'Community Tool Export' "
                "--imported-at 2026-06-13T12:00:00+00:00"
            ),
            "dry_run_directory_import command",
        ),
        (
            "import_directory_signals",
            (
                "fashion-radar import-signals-dir-extra /tmp/export --format csv "
                "--pattern '*.csv' --data-dir data "
                "--source-name 'Community Tool Export' "
                "--imported-at 2026-06-13T12:00:00+00:00"
            ),
            "import_directory_signals command",
        ),
        (
            "print_post_import_review",
            (
                "fashion-radar imported-review-workflow-extra --config-dir configs "
                "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                "--source-name 'Community Tool Export'"
            ),
            "print_post_import_review command",
        ),
    ],
)
def test_validate_community_handoff_workflow_rejects_unpinned_command_drift(
    step_name: str,
    replacement_command: str,
    expected_message: str,
) -> None:
    payload = community_handoff_workflow_payload()
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
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)
```

- [x] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "unpinned_command_drift"
```

Expected: test fails because the current validator accepts at least one mutated non-readiness command.

### Task 3: Exact Command Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [x] **Step 1: Add expected-command helper**

Add after `validate_expected_external_tool_command()`:

```python
def expected_community_handoff_workflow_command_parts(
    *,
    directory: str,
    input_format: str,
    pattern: str,
    config_dir: str,
    data_dir: str,
    as_of: str,
    source_name: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return (
        (
            "lint_handoff_directory",
            (
                "community-signal-lint-dir",
                directory,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--source-name",
                source_name,
                "--strict",
            ),
        ),
        (
            "preview_candidate_phrases",
            (
                "community-candidates-dir",
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
            ),
        ),
        (
            "review_handoff_readiness",
            (
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
            ),
        ),
        (
            "dry_run_directory_import",
            (
                "import-signals-dir",
                directory,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--data-dir",
                data_dir,
                "--source-name",
                source_name,
                "--imported-at",
                as_of,
                "--dry-run",
            ),
        ),
        (
            "import_directory_signals",
            (
                "import-signals-dir",
                directory,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--data-dir",
                data_dir,
                "--source-name",
                source_name,
                "--imported-at",
                as_of,
            ),
        ),
        (
            "print_post_import_review",
            (
                "imported-review-workflow",
                "--config-dir",
                config_dir,
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--source-name",
                source_name,
            ),
        ),
    )
```

- [x] **Step 2: Extract `data_dir` and replace one-off readiness command validation**

Add `data_dir` next to the existing command input extraction:

```python
    data_dir = str(payload.get("data_dir", ""))
```

Then replace the `readiness_step = steps[2]` block in `validate_community_handoff_workflow()` with:

```python
    expected_commands = expected_community_handoff_workflow_command_parts(
        directory=directory,
        input_format=input_format,
        pattern=pattern,
        config_dir=config_dir,
        data_dir=data_dir,
        as_of=as_of,
        source_name=source_name,
    )
    for index, (label, expected_parts) in enumerate(expected_commands):
        step = steps[index]
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} {label} step must be a JSON object")
        validate_expected_external_tool_command(
            command_name,
            label,
            step.get("command", ""),
            *expected_parts,
        )
```

Keep the existing import and post-review effect checks after this loop.

- [x] **Step 3: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "unpinned_command_drift"
```

Expected: test passes.

### Task 4: Focused Verification and Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-143-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-143-code-review.md`

- [x] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Expected: all commands exit 0.

- [x] **Step 2: Write code review prompt**

Create `docs/reviews/opencode-stage-143-code-review-prompt.md`:

```markdown
# Stage 143 Code Review Prompt

You are reviewing Stage 143 changes in `/home/ubuntu/fashion-radar`.

Base commit: `9b8cd5e`

Review scope:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 143 plan and review docs

Requirements:
- `community-handoff-workflow` smoke validation must reject command drift for every workflow step.
- Runtime builder/output behavior must not change.
- RED/GREEN should prove the old validator accepted non-readiness command drift and exact argv validation rejects it.

Please report findings first with severity and file/line references. If there are no blocking findings, say that explicitly.
```

- [x] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-143-code-review-prompt.md)" > /tmp/opencode-stage-143-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-143-code-review.md`.

- [x] **Step 4: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-143-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-143-code-review.md`.

### Task 5: Release Gate, Commit, Push, CI

**Files:**
- Commit all Stage 143 files after verification and review.

- [x] **Step 1: Run release gate**

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

Expected: all commands exit 0.

- [ ] **Step 2: Commit Stage 143**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-21-stage-143-community-handoff-command-argv-design.md docs/superpowers/plans/2026-06-21-stage-143-community-handoff-command-argv-plan.md docs/reviews/opencode-stage-143-plan-review-prompt.md docs/reviews/opencode-stage-143-plan-review.md docs/reviews/opencode-stage-143-code-review-prompt.md docs/reviews/opencode-stage-143-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Harden community handoff workflow commands"
```

Expected: commit succeeds.

- [ ] **Step 3: Push with ephemeral auth**

Use an ephemeral HTTP extraheader only for this push.

Run:

```bash
git -c http.https://github.com/.extraheader="$AUTH_HEADER" push origin main
git config --get-all http.https://github.com/.extraheader || true
```

Expected: push succeeds and no persistent auth header is printed.

- [ ] **Step 4: Poll CI**

Use GitHub Actions API to poll the new run until completion.

- [ ] **Step 5: Handoff Summary**

Write:

```markdown
**Handoff Summary**

- Repo status:
- Verified commands:
- CI:
- Uncommitted files:
- Next step:
```
