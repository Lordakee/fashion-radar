# Stage 137 External Tool Workflow Step Argv Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject command-shape drift in every `external-tool-workflow` payload step by exact parsed argv comparison.

**Architecture:** Extend the existing first-run smoke validator only. Add RED tests for the eight workflow step commands that are not currently exact-checked, then reuse `validate_expected_external_tool_command()` inside `validate_external_tool_workflow()` for those same steps. Keep expected args derived from workflow payload values so temporary first-run smoke paths remain valid.

**Tech Stack:** Python 3.11 stdlib (`shlex` already used by the checker and tests), pytest, uv frozen command runner, ruff.

---

## Files

- Modify `tests/test_first_run_smoke.py`
  - Add one parametrized RED test for the eight currently unchecked
    `external-tool-workflow` step commands.
- Modify `scripts/check_first_run_smoke.py`
  - Add exact `validate_expected_external_tool_command()` checks for:
    `print_signal_profile`, `print_handoff_manifest`,
    `print_handoff_workflow`, `preview_candidate_phrases`,
    `review_handoff_readiness`, `dry_run_directory_import`,
    `import_directory_signals`, and `print_post_import_review`.
- Create `docs/reviews/opencode-stage-137-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-137-plan-review.md`.
- Create `docs/reviews/opencode-stage-137-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-137-code-review.md`.

No CLI runtime behavior changes, generated command execution, PATH lookup
changes, directory inspection, handoff file reads, import behavior changes,
SQLite behavior changes, artifact creation, dependency changes, `uv.lock`
changes, connectors, scraping, browser automation, platform APIs,
account/session/cookie/token behavior, media downloads, monitoring,
scheduling, source acquisition, demand proof, ranking, coverage verification,
or compliance/audit product behavior are part of this stage.

## Task 1: Add RED workflow step command argv drift tests

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add the parametrized RED test**

Add after
`test_validate_external_tool_workflow_rejects_extra_readiness_command_flag`:

```python
@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_error"),
    [
        (
            "print_signal_profile",
            external_tool_command("community-signal-profile", "--format", "table"),
            "signal profile command",
        ),
        (
            "print_handoff_manifest",
            external_tool_command(
                "community-handoff-manifest",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Rednote MCP Export",
                "--format",
                "table",
            ),
            "handoff manifest command",
        ),
        (
            "print_handoff_workflow",
            external_tool_command(
                "community-handoff-workflow",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Rednote MCP Export",
                "--format",
                "json",
            ),
            "handoff workflow command",
        ),
        (
            "preview_candidate_phrases",
            external_tool_command(
                "community-candidates-dir",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Wrong Source",
            ),
            "candidate preview command",
        ),
        (
            "review_handoff_readiness",
            external_tool_command(
                "community-handoff-check-dir",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Rednote MCP Export",
            ),
            "handoff readiness command",
        ),
        (
            "dry_run_directory_import",
            external_tool_command(
                "import-signals-dir",
                "exports",
                "--format",
                "json",
                "--pattern",
                "*.json",
                "--source-name",
                "Rednote MCP Export",
                "--data-dir",
                "data",
                "--imported-at",
                "2026-06-13T12:00:00+00:00",
            ),
            "dry-run command",
        ),
        (
            "import_directory_signals",
            external_tool_command(
                "import-signals-dir",
                "exports",
                "--format",
                "json",
                "--pattern",
                "*.json",
                "--source-name",
                "Rednote MCP Export",
                "--data-dir",
                "data",
                "--imported-at",
                "2026-06-13T12:00:00+00:00",
                "--dry-run",
            ),
            "import command",
        ),
        (
            "print_post_import_review",
            external_tool_command(
                "imported-review-workflow",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Wrong Source",
            ),
            "post-import review command",
        ),
    ],
)
def test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift(
    step_name: str,
    replacement_command: str,
    expected_error: str,
) -> None:
    payload = external_tool_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    matching_steps = [
        step for step in steps if isinstance(step, dict) and step.get("name") == step_name
    ]
    assert len(matching_steps) == 1
    matching_steps[0]["command"] = replacement_command

    with pytest.raises(smoke.SmokeError, match=expected_error):
        smoke.validate_external_tool_workflow("external-tool-workflow", payload)
```

- [ ] **Step 2: Run the RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift -q
```

Expected result: fail because the current checker accepts all eight mutated
commands.

## Task 2: Add exact argv checks for remaining workflow steps

**Files:**

- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add exact checks for steps 3-5 after the template command check**

Inside `validate_external_tool_workflow()`, after the existing
`template_step` validation block and before the existing `lint_step` block,
add:

```python
    signal_profile_step = steps[3]
    if not isinstance(signal_profile_step, dict):
        raise SmokeError(f"{command_name} signal profile step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "signal profile",
        signal_profile_step.get("command", ""),
        "community-signal-profile",
        "--format",
        "json",
    )

    handoff_manifest_step = steps[4]
    if not isinstance(handoff_manifest_step, dict):
        raise SmokeError(f"{command_name} handoff manifest step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "handoff manifest",
        handoff_manifest_step.get("command", ""),
        "community-handoff-manifest",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
        "--format",
        "json",
    )

    handoff_workflow_step = steps[5]
    if not isinstance(handoff_workflow_step, dict):
        raise SmokeError(f"{command_name} handoff workflow step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "handoff workflow",
        handoff_workflow_step.get("command", ""),
        "community-handoff-workflow",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
    )
```

- [ ] **Step 2: Add exact checks for steps 7-11 after the lint command check**

Inside `validate_external_tool_workflow()`, after the existing `lint_step`
validation block and before the `boundaries = payload.get("boundaries")`
block, add:

```python
    candidate_preview_step = steps[7]
    if not isinstance(candidate_preview_step, dict):
        raise SmokeError(f"{command_name} candidate preview step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "candidate preview",
        candidate_preview_step.get("command", ""),
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
    )

    handoff_readiness_step = steps[8]
    if not isinstance(handoff_readiness_step, dict):
        raise SmokeError(f"{command_name} handoff readiness step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "handoff readiness",
        handoff_readiness_step.get("command", ""),
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

    dry_run_import_step = steps[9]
    if not isinstance(dry_run_import_step, dict):
        raise SmokeError(f"{command_name} dry-run step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "dry-run",
        dry_run_import_step.get("command", ""),
        "import-signals-dir",
        directory,
        "--format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--data-dir",
        data_dir,
        "--imported-at",
        as_of,
        "--dry-run",
    )

    import_signals_step = steps[10]
    if not isinstance(import_signals_step, dict):
        raise SmokeError(f"{command_name} import step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "import",
        import_signals_step.get("command", ""),
        "import-signals-dir",
        directory,
        "--format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--data-dir",
        data_dir,
        "--imported-at",
        as_of,
    )

    post_import_review_step = steps[11]
    if not isinstance(post_import_review_step, dict):
        raise SmokeError(f"{command_name} post-import review step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "post-import review",
        post_import_review_step.get("command", ""),
        "imported-review-workflow",
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
    )
```

- [ ] **Step 3: Run the GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift -q
```

Expected result: 8 passed.

## Task 3: Focused verification and review

**Files:**

- Create: `docs/reviews/opencode-stage-137-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-137-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness or external_tool_adapters"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

Expected result: all commands exit 0.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-137-code-review-prompt.md` asking local
opencode to review:

- whether all eight previously unchecked workflow step commands are now exact
  argv-checked;
- whether the expected argv values are derived from payload fields;
- whether existing exact checks remain intact;
- whether the stage is validation-only and within AGENTS.md boundaries;
- whether the RED test proved the previous gap.

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-137-code-review-prompt.md)" > docs/reviews/opencode-stage-137-code-review.md
```

Expected result: review file starts with `# Stage 137 Code Review` and reports
no Critical or Important blockers. If opencode emits live narration before the
heading, remove only that preamble from the review artifact before commit.

## Task 4: Release gate, commit, push, and CI

**Files:**

- Stage all Stage 137 code/test/review artifacts.

- [ ] **Step 1: Run release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if [ -n "$(git config --get-all http.https://github.com/.extraheader || true)" ]; then echo 'Persistent GitHub auth header found' >&2; exit 1; fi
```

Expected result: all commands exit 0.

- [ ] **Step 2: Commit**

Run:

```bash
git add scripts/check_first_run_smoke.py tests/test_first_run_smoke.py \
  docs/superpowers/specs/2026-06-21-stage-137-external-tool-workflow-step-argv-design.md \
  docs/superpowers/plans/2026-06-21-stage-137-external-tool-workflow-step-argv-plan.md \
  docs/reviews/opencode-stage-137-plan-review-prompt.md \
  docs/reviews/opencode-stage-137-plan-review.md \
  docs/reviews/opencode-stage-137-code-review-prompt.md \
  docs/reviews/opencode-stage-137-code-review.md
git commit -m "Harden external tool workflow step commands"
```

- [ ] **Step 3: Push with ephemeral GitHub auth header**

Run with the user-provided token only in process environment; do not persist it:

```bash
GH_TOKEN="..."
AUTH_HEADER="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
git -c http.https://github.com/.extraheader="$AUTH_HEADER" push origin main
unset GH_TOKEN AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and the final config command prints nothing.

- [ ] **Step 4: Poll CI**

Poll the GitHub Actions run for the pushed SHA and require conclusion
`success`.

- [ ] **Step 5: Handoff summary**

Write a concise Handoff Summary with repo status, verified commands,
uncommitted files, and next step.
