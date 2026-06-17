# Stage 67 External Tool Workflow Readiness Preflight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an early `check_external_tool_readiness` preflight step to `external-tool-workflow` so the printed external tool workflow points users to the existing local read-only readiness command before they prepare sanitized handoff files.

**Architecture:** Keep `external-tool-workflow` print-only and modify only its ordered printed step list. The new step prints a copyable `external-tool-readiness` command using the already-resolved adapter, path, timestamp, format, pattern, and source-name values; all validation and PATH lookup remain inside the separate readiness command when the user runs it manually.

**Tech Stack:** Python 3.11, Typer CLI, Pydantic models, pytest, ruff, uv.

---

## File Map

- Modify `src/fashion_radar/external_tool_workflow.py`
  - Insert one printed readiness preflight step in `_workflow_steps`.
  - Keep model keys and renderer unchanged.
- Modify `tests/test_external_tool_workflow.py`
  - Update stable step names/effects/count.
  - Add command assertions for the readiness preflight step.
- Modify `tests/test_cli.py`
  - Update `external-tool-workflow` CLI JSON/table assertions for the extra step.
- Modify `scripts/check_first_run_smoke.py`
  - Update expected workflow step tuple, effect validation, and readiness-step command validation.
- Modify `tests/test_first_run_smoke.py`
  - Update deterministic `external_tool_workflow_payload` fixture and command indexes.
- Modify docs:
  - `README.md`
  - `docs/cli-reference.md`
  - `docs/community-signal-import.md`
  - `docs/community-signal-quality.md`
  - `docs/source-boundaries.md`
  - `docs/architecture.md`
  - `docs/github-upload-checklist.md`
  - `AGENTS.md`
  - `CHANGELOG.md`
- Modify `tests/test_cli_docs.py` if the existing workflow step-name tuple or phrase assertions need the new step.
- Create review artifacts:
  - `docs/reviews/opencode-stage-67-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-67-plan-review.md`
  - `docs/reviews/opencode-stage-67-code-review-prompt.md`
  - `docs/reviews/opencode-stage-67-code-review.md`

## Task 1: Focused Workflow Tests

**Files:**
- Modify: `tests/test_external_tool_workflow.py`

- [ ] **Step 1: Update stable workflow contract expectations**

In `test_workflow_has_stable_instaloader_contract_and_steps`, change:

```python
assert workflow.step_count == 11
assert [step.name for step in workflow.steps] == [
    "inspect_adapter_registry",
    "print_adapter_template_json",
    "print_signal_profile",
    "print_handoff_manifest",
    "print_handoff_workflow",
    "lint_export_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert [step.suggested_effect for step in workflow.steps] == [
    "print_only",
    "print_only",
    "print_only",
    "print_only",
    "print_only",
    "read_only",
    "read_only",
    "read_only",
    "read_only",
    "updates_local_imports",
    "print_only",
]
```

to:

```python
assert workflow.step_count == 12
assert [step.name for step in workflow.steps] == [
    "inspect_adapter_registry",
    "check_external_tool_readiness",
    "print_adapter_template_json",
    "print_signal_profile",
    "print_handoff_manifest",
    "print_handoff_workflow",
    "lint_export_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert [step.suggested_effect for step in workflow.steps] == [
    "print_only",
    "read_only",
    "print_only",
    "print_only",
    "print_only",
    "print_only",
    "read_only",
    "read_only",
    "read_only",
    "read_only",
    "updates_local_imports",
    "print_only",
]
```

- [ ] **Step 2: Add readiness command assertions to the quoting test**

In `test_workflow_commands_use_adapter_defaults_and_shell_quote_paths`, after
the `inspect_adapter_registry` assertion, add:

```python
assert commands["check_external_tool_readiness"] == (
    "fashion-radar external-tool-readiness --adapter instaloader "
    "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
    "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
    "--input-format json --pattern '*.json' "
    "--source-name 'Instaloader Export' --format table"
)
```

- [ ] **Step 3: Update source-name override step index assertion**

In `test_workflow_defaults_to_generic_adapter_and_accepts_local_overrides`,
replace:

```python
assert "--source-name 'Local Desk Export'" in workflow.steps[3].command
```

with:

```python
assert "--source-name 'Local Desk Export'" in workflow.steps[1].command
assert "--source-name 'Local Desk Export'" in workflow.steps[4].command
```

This ensures the new readiness step and the manifest step both receive the
resolved source-name override.

- [ ] **Step 4: Run focused tests and verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_workflow.py -q
```

Expected: fail because `_workflow_steps` has not inserted
`check_external_tool_readiness` yet.

## Task 2: Implement The Printed Readiness Preflight Step

**Files:**
- Modify: `src/fashion_radar/external_tool_workflow.py`

- [ ] **Step 1: Insert the workflow step**

In `_workflow_steps`, immediately after the `inspect_adapter_registry` step,
insert:

```python
        ExternalToolWorkflowStep(
            order=2,
            name="check_external_tool_readiness",
            purpose=(
                "Print local external tool readiness guidance before preparing "
                "sanitized handoff rows."
            ),
            command=_shell_command(
                "fashion-radar",
                "external-tool-readiness",
                "--adapter",
                adapter_id,
                "--directory",
                directory_text,
                "--config-dir",
                config_text,
                "--data-dir",
                data_text,
                "--as-of",
                as_of_text,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--source-name",
                source_name,
                "--format",
                "table",
            ),
            suggested_effect="read_only",
        ),
```

Then renumber all following `ExternalToolWorkflowStep(order=...)` values so the
final `print_post_import_review` order is `12`.

- [ ] **Step 2: Run focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_workflow.py -q
```

Expected: pass.

## Task 3: CLI And First-Run Smoke Contract Updates

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Update CLI workflow JSON assertions**

In `tests/test_cli.py::test_external_tool_workflow_command_prints_json_with_stable_keys`,
change:

```python
assert payload["step_count"] == 11
assert [step["name"] for step in payload["steps"]] == [
    "inspect_adapter_registry",
    "print_adapter_template_json",
    "print_signal_profile",
    "print_handoff_manifest",
    "print_handoff_workflow",
    "lint_export_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert payload["steps"][9]["suggested_effect"] == "updates_local_imports"
assert f"'{directory}'" in payload["steps"][3]["command"]
```

to:

```python
assert payload["step_count"] == 12
assert [step["name"] for step in payload["steps"]] == [
    "inspect_adapter_registry",
    "check_external_tool_readiness",
    "print_adapter_template_json",
    "print_signal_profile",
    "print_handoff_manifest",
    "print_handoff_workflow",
    "lint_export_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
]
assert payload["steps"][1]["suggested_effect"] == "read_only"
assert "fashion-radar external-tool-readiness" in payload["steps"][1]["command"]
assert payload["steps"][10]["suggested_effect"] == "updates_local_imports"
assert f"'{directory}'" in payload["steps"][4]["command"]
```

Preserve the existing assertion that each workflow step has stable keys:

```python
assert list(payload["steps"][0]) == [
    "order",
    "name",
    "purpose",
    "command",
    "suggested_effect",
]
```

- [ ] **Step 2: Update CLI table assertion**

In `test_external_tool_workflow_command_prints_table_without_artifacts`, add:

```python
assert "check_external_tool_readiness" in result.output
assert "external-tool-readiness" in result.output
```

- [ ] **Step 3: Update smoke expected workflow steps**

In `scripts/check_first_run_smoke.py`, change
`EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS` to:

```python
EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS = (
    "inspect_adapter_registry",
    "check_external_tool_readiness",
    "print_adapter_template_json",
    "print_signal_profile",
    "print_handoff_manifest",
    "print_handoff_workflow",
    "lint_export_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
)
```

- [ ] **Step 4: Update smoke workflow validator**

In `validate_external_tool_workflow`, change:

```python
assert_equal(f"{command_name} step_count", payload.get("step_count"), 11)
```

to:

```python
assert_equal(f"{command_name} step_count", payload.get("step_count"), 12)
```

Change the expected effects list to:

```python
[
    "print_only",
    "read_only",
    "print_only",
    "print_only",
    "print_only",
    "print_only",
    "read_only",
    "read_only",
    "read_only",
    "read_only",
    "updates_local_imports",
    "print_only",
]
```

After validating the registry step, add:

```python
readiness_step = steps[1]
if not isinstance(readiness_step, dict):
    raise SmokeError(f"{command_name} readiness step must be a JSON object")
readiness_command = str(readiness_step.get("command", ""))
for expected in (
    "fashion-radar external-tool-readiness",
    "--adapter",
    "rednote_mcp",
    "--input-format",
    "json",
    "--pattern",
    "*.json",
    "--source-name",
    "--format",
    "table",
):
    if expected not in readiness_command:
        raise SmokeError(f"{command_name} readiness command missing {expected!r}")
```

Then adjust indexed step reads:

```python
template_step = steps[2]
lint_step = steps[6]
import_step = steps[10]
```

- [ ] **Step 5: Update deterministic smoke fixture**

In `tests/test_first_run_smoke.py::external_tool_workflow_payload`, change
`"step_count": 11` to `"step_count": 12`, insert this dict after the registry
step, and increment every following `order` by one:

```python
            {
                "order": 2,
                "name": "check_external_tool_readiness",
                "purpose": (
                    "Print local external tool readiness guidance before preparing "
                    "sanitized handoff rows."
                ),
                "command": (
                    "fashion-radar external-tool-readiness --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
                    "--pattern '*.json' --source-name 'Rednote MCP Export' "
                    "--format table"
                ),
                "suggested_effect": "read_only",
            },
```

- [ ] **Step 6: Update external workflow negative validator test index**

In `tests/test_first_run_smoke.py::test_validate_external_tool_workflow_requires_print_only_workflow_contract`,
the `executable_import` branch currently mutates the import step at the old
index:

```python
import_step = steps[9]
```

Change it to:

```python
import_step = steps[10]
```

This keeps the negative test aimed at `import_directory_signals` after the new
readiness step shifts the workflow from 11 to 12 steps.

- [ ] **Step 7: Run contract tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or run_first_run_flow"
```

Expected: pass.

## Task 4: Documentation And Drift Guards

**Files:**
- Modify: `README.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_cli_docs.py` if step-name constants require it.

- [ ] **Step 1: Update workflow docs wording**

In each public external tool workflow section, add one sentence equivalent to:

```markdown
The printed steps now include `check_external_tool_readiness`, an optional
preflight command that points to `external-tool-readiness` for local command
availability guidance before sanitized handoff rows are prepared.
```

Do this in:

- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`

- [ ] **Step 2: Update explicit step-name lists**

Where docs list `external-tool-workflow` step names, ensure they include:

```text
inspect_adapter_registry
check_external_tool_readiness
print_adapter_template_json
print_signal_profile
print_handoff_manifest
print_handoff_workflow
lint_export_directory
preview_candidate_phrases
review_handoff_readiness
dry_run_directory_import
import_directory_signals
print_post_import_review
```

- [ ] **Step 3: Update CHANGELOG**

Under `[Unreleased]`, add:

```markdown
- Stage 67 `external-tool-workflow` now prints an early
  `check_external_tool_readiness` preflight step pointing to the local
  read-only `external-tool-readiness` command before sanitized CSV/JSON
  external/community handoff rows are prepared. The workflow itself remains
  local and print-only, does not execute generated commands or upstream tools,
  and adds no connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance-review product feature.
```

- [ ] **Step 4: Update docs drift step-name tuple**

In `tests/test_cli_docs.py`, update the existing
`EXTERNAL_TOOL_WORKFLOW_STEP_NAMES` tuple to include
`check_external_tool_readiness` after `inspect_adapter_registry`. The
`test_external_tool_workflow_docs_include_examples_and_steps` test requires
every name in that tuple to appear verbatim in
`docs/community-signal-import.md`, so that document must also include the
literal `check_external_tool_readiness` token.

- [ ] **Step 5: Run docs drift tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "external_tool_workflow or external_tool_readiness or upload_checklist"
```

Expected: pass.

## Task 5: Full Verification, Review, Commit, Push

**Files:**
- Modify or create `docs/reviews/opencode-stage-67-code-review-prompt.md`
- Create `docs/reviews/opencode-stage-67-code-review.md`

- [ ] **Step 1: Run targeted verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_workflow.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
```

Expected: pass.

- [ ] **Step 2: Run lint/format/release hygiene**

Run:

```bash
uv --no-config run --frozen ruff check src/fashion_radar/external_tool_workflow.py tests/test_external_tool_workflow.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/external_tool_workflow.py tests/test_external_tool_workflow.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
```

Expected: pass.

- [ ] **Step 3: Run full test suite**

Run:

```bash
uv --no-config run --frozen pytest
```

Expected: pass.

- [ ] **Step 4: Request local opencode code review**

Create `docs/reviews/opencode-stage-67-code-review-prompt.md` with:

```markdown
Review Stage 67 external-tool-workflow readiness preflight implementation in
/home/ubuntu/fashion-radar.

Scope:
- `external-tool-workflow` should now print one early
  `check_external_tool_readiness` step pointing to `external-tool-readiness`.
- `external-tool-workflow` must remain print-only and must not call readiness,
  inspect directories, read handoff files, open SQLite, or execute generated
  commands.
- `external-tool-readiness` semantics should remain unchanged.
- Tests/docs/smoke should be updated consistently for the 12-step workflow.

Return only Critical or Important findings, plus blocking test gaps.
```

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-67-code-review-prompt.md)" > docs/reviews/opencode-stage-67-code-review.md
```

Expected: no Critical or Important findings. Fix any Critical or Important
findings and rerun the relevant verification/review.

- [ ] **Step 5: Commit**

Run:

```bash
git status --short
test -f docs/reviews/opencode-stage-67-plan-review-prompt.md
test -f docs/reviews/opencode-stage-67-plan-review.md
test -f docs/reviews/opencode-stage-67-plan-rereview-prompt.md
test -f docs/reviews/opencode-stage-67-plan-rereview.md
git add src/fashion_radar/external_tool_workflow.py tests/test_external_tool_workflow.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py README.md docs/cli-reference.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md AGENTS.md CHANGELOG.md docs/superpowers/specs/2026-06-17-stage-67-external-tool-workflow-readiness-preflight-design.md docs/superpowers/plans/2026-06-17-stage-67-external-tool-workflow-readiness-preflight-plan.md docs/reviews/opencode-stage-67-plan-review-prompt.md docs/reviews/opencode-stage-67-plan-review.md docs/reviews/opencode-stage-67-plan-rereview-prompt.md docs/reviews/opencode-stage-67-plan-rereview.md docs/reviews/opencode-stage-67-code-review-prompt.md docs/reviews/opencode-stage-67-code-review.md
git commit -m "Add external workflow readiness preflight"
```

- [ ] **Step 6: Push**

Use the token ephemerally from `/home/ubuntu/.config/fashion-radar/github-token`
without printing it or writing it to git config:

```bash
basic_auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 -w0)
git -c http.version=HTTP/1.1 -c http.extraHeader="AUTHORIZATION: basic $basic_auth" push origin HEAD:main
```

- [ ] **Step 7: Verify remote CI**

Use the existing GitHub API/curl pattern with the token file to confirm the
latest CI run for the pushed SHA succeeds.

## Self-Review Checklist

- Spec coverage: The plan covers workflow code, focused tests, CLI smoke,
  docs, review, commit, push, and CI verification.
- Boundary coverage: The plan keeps `external-tool-workflow` print-only and
  keeps `external-tool-readiness` local read-only.
- Placeholder scan: No TBD/TODO/fill-in placeholders remain.
- Scope check: This is a single small workflow integration, not a new connector
  or new public command.
- Type consistency: Step names, effect values, and command flags match existing
  Typer commands.
