# Stage 138 External Tool Readiness Step Argv Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject command-shape drift in every `external-tool-readiness` payload step by exact parsed argv comparison.

**Architecture:** Extend the existing first-run smoke validator only. Add RED tests for the five readiness step commands that are not currently exact-checked, then reuse `validate_expected_external_tool_command()` inside `validate_external_tool_readiness()` for those same steps. Keep expected args derived from readiness payload values so temporary first-run smoke paths remain valid.

**Tech Stack:** Python 3.11 stdlib (`shlex` already used by the checker and tests), pytest, uv frozen command runner, ruff.

---

## Files

- Modify `tests/test_first_run_smoke.py`
  - Add one parametrized RED test for the five currently unchecked
    `external-tool-readiness` step commands.
- Modify `scripts/check_first_run_smoke.py`
  - Add exact `validate_expected_external_tool_command()` checks for:
    `inspect_adapter_registry`, `print_adapter_template_json`,
    `print_signal_profile`, `lint_export_directory`, and
    `review_handoff_readiness`.
- Create `docs/reviews/opencode-stage-138-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-138-plan-review.md`.
- Create `docs/reviews/opencode-stage-138-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-138-code-review.md`.

No CLI runtime behavior changes, generated command execution, PATH lookup
changes, directory inspection, handoff file reads, import behavior changes,
SQLite behavior changes, artifact creation, dependency changes, `uv.lock`
changes, connectors, scraping, browser automation, platform APIs,
account/session/cookie/token behavior, media downloads, monitoring,
scheduling, source acquisition, demand proof, ranking, coverage verification,
or compliance/audit product behavior are part of this stage.

## Task 1: Add RED readiness step command argv drift tests

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add the parametrized RED test**

Add after
`test_validate_external_tool_readiness_rejects_wrong_dry_run_input_format`:

```python
@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_error"),
    [
        (
            "inspect_adapter_registry",
            external_tool_command(
                "external-tool-adapters",
                "--adapter",
                "rednote_mcp",
                "--directory",
                "exports",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--format",
                "json",
            ),
            "registry command",
        ),
        (
            "print_adapter_template_json",
            external_tool_command(
                "external-tool-template",
                "--adapter",
                "rednote_mcp",
                "--directory",
                "exports",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--format",
                "table",
            ),
            "template command",
        ),
        (
            "print_signal_profile",
            external_tool_command("community-signal-profile", "--format", "table"),
            "signal profile command",
        ),
        (
            "lint_export_directory",
            external_tool_command(
                "community-signal-lint-dir",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--source-name",
                "Rednote MCP Export",
            ),
            "lint command",
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
    ],
)
def test_validate_external_tool_readiness_rejects_remaining_step_command_argv_drift(
    step_name: str,
    replacement_command: str,
    expected_error: str,
) -> None:
    payload = external_tool_readiness_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    matching_steps = [
        step for step in steps if isinstance(step, dict) and step.get("name") == step_name
    ]
    assert len(matching_steps) == 1
    matching_steps[0]["command"] = replacement_command

    with pytest.raises(smoke.SmokeError, match=expected_error):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)
```

- [ ] **Step 2: Run the RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_remaining_step_command_argv_drift -q
```

Expected result: fail because the current checker accepts all five mutated
commands.

## Task 2: Add exact argv checks for remaining readiness steps

**Files:**

- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add exact checks for steps 0-1 before the workflow command check**

Inside `validate_external_tool_readiness()`, after the existing step effects
assertion and before `workflow_step = steps[2]`, add:

```python
    registry_step = steps[0]
    if not isinstance(registry_step, dict):
        raise SmokeError(f"{command_name} registry step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "registry",
        registry_step.get("command", ""),
        "external-tool-adapters",
        "--adapter",
        adapter_id,
        "--directory",
        directory,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--format",
        "table",
    )

    template_step = steps[1]
    if not isinstance(template_step, dict):
        raise SmokeError(f"{command_name} template step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "template",
        template_step.get("command", ""),
        "external-tool-template",
        "--adapter",
        adapter_id,
        "--directory",
        directory,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--format",
        "json",
    )
```

- [ ] **Step 2: Add exact checks for steps 3-5 after the workflow command check**

Inside `validate_external_tool_readiness()`, after the existing
`workflow_step` validation block and before `dry_run_step = steps[-1]`, add:

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

    lint_step = steps[4]
    if not isinstance(lint_step, dict):
        raise SmokeError(f"{command_name} lint step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "lint",
        lint_step.get("command", ""),
        "community-signal-lint-dir",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--strict",
    )

    handoff_readiness_step = steps[5]
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
```

- [ ] **Step 3: Run the GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_remaining_step_command_argv_drift -q
```

Expected result: 5 passed.

## Task 3: Focused verification and review

**Files:**

- Create: `docs/reviews/opencode-stage-138-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-138-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness or external_tool_workflow or external_tool_adapters"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

Expected result: all commands exit 0.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-138-code-review-prompt.md` asking local
opencode to review:

- whether all five previously unchecked readiness step commands are now exact
  argv-checked;
- whether the expected argv values are derived from payload fields;
- whether existing workflow and dry-run exact checks remain intact;
- whether the stage is validation-only and within AGENTS.md boundaries;
- whether the RED test proved the previous gap.

- [ ] **Step 3: Run local opencode code review**

Run capture outside the reviewed artifact first, then copy only the formal
review body into the repo artifact:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-138-code-review-prompt.md)" > /tmp/opencode-stage-138-code-review.md
```

Expected result: formal review body starts with `# Stage 138 Code Review` and
reports no Critical or Important blockers. If opencode emits live narration
before the heading, remove only that preamble before saving
`docs/reviews/opencode-stage-138-code-review.md`.

## Task 4: Release gate, commit, push, and CI

**Files:**

- Stage all Stage 138 code/test/review artifacts.

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
  docs/superpowers/specs/2026-06-21-stage-138-external-tool-readiness-step-argv-design.md \
  docs/superpowers/plans/2026-06-21-stage-138-external-tool-readiness-step-argv-plan.md \
  docs/reviews/opencode-stage-138-plan-review-prompt.md \
  docs/reviews/opencode-stage-138-plan-review.md \
  docs/reviews/opencode-stage-138-code-review-prompt.md \
  docs/reviews/opencode-stage-138-code-review.md
git commit -m "Harden external tool readiness step commands"
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
