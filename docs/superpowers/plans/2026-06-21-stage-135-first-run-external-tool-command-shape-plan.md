# Stage 135 First-Run External Tool Command Shape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make first-run smoke reject malformed external/community tool workflow commands by comparing parsed command argv lists exactly.

**Architecture:** Add RED tests that mutate existing external-tool workflow/readiness payload commands while preserving current substring anchors, then add one `shlex.split()` helper in `scripts/check_first_run_smoke.py` and use it for the command checks already present in the two validators. Expected path values come from the payload, not hardcoded fixture directories.

**Tech Stack:** Python 3.11 stdlib `shlex`, pytest, uv frozen command runner, ruff.

---

## Files

- Modify `tests/test_first_run_smoke.py`
  - Add three focused negative tests near existing external-tool workflow and
    readiness validator tests.
- Modify `scripts/check_first_run_smoke.py`
  - Add an exact argv validation helper near `expected_external_tool_command()`.
  - Replace weak substring checks in `validate_external_tool_workflow()`.
  - Replace weak substring checks in `validate_external_tool_readiness()`.
- Create `docs/reviews/opencode-stage-135-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-135-plan-review.md`.
- Create `docs/reviews/opencode-stage-135-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-135-code-review.md`.

No CLI runtime behavior changes, docs wording changes, package/archive checker
changes, dependency changes, `uv.lock` changes, new connectors, scraping,
browser automation, platform APIs, monitoring, scheduling, source acquisition,
demand proof, ranking, coverage verification, compliance/audit product
behavior, generated command execution, PATH lookup behavior changes, import
behavior, SQLite behavior, file-read behavior, or artifact creation behavior
are part of this stage.

## Task 1: Add RED external-tool command-shape tests

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add three negative tests**

Add after `test_validate_external_tool_workflow_requires_print_only_workflow_contract`:

```python
def test_validate_external_tool_workflow_rejects_extra_readiness_command_flag() -> None:
    payload = external_tool_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    readiness_step = steps[1]
    assert isinstance(readiness_step, dict)
    readiness_step["command"] = str(readiness_step["command"]) + " --verbose"

    with pytest.raises(smoke.SmokeError, match="readiness command"):
        smoke.validate_external_tool_workflow("external-tool-workflow", payload)


def test_validate_external_tool_readiness_rejects_wrong_workflow_output_format() -> None:
    payload = external_tool_readiness_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    workflow_step = steps[2]
    assert isinstance(workflow_step, dict)
    workflow_step["command"] = external_tool_command(
        "external-tool-workflow",
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
        "--input-format",
        "json",
        "--pattern",
        "*.json",
        "--source-name",
        "Rednote MCP Export",
        "--format",
        "json",
    )

    with pytest.raises(smoke.SmokeError, match="workflow command"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)


def test_validate_external_tool_readiness_rejects_wrong_dry_run_input_format() -> None:
    payload = external_tool_readiness_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    dry_run_step = steps[-1]
    assert isinstance(dry_run_step, dict)
    dry_run_step["command"] = external_tool_command(
        "import-signals-dir",
        "exports",
        "--format",
        "csv",
        "--pattern",
        "*.json",
        "--source-name",
        "Rednote MCP Export",
        "--data-dir",
        "data",
        "--imported-at",
        "2026-06-13T12:00:00+00:00",
        "--dry-run",
    )

    with pytest.raises(smoke.SmokeError, match="dry-run command"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)
```

- [ ] **Step 2: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_workflow_rejects_extra_readiness_command_flag tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_wrong_workflow_output_format tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_wrong_dry_run_input_format -q
```

Expected result: fail because current validators use substring checks and do
not reject these malformed but substring-preserving commands.

## Task 2: Add exact command argv validation helper

**Files:**

- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add helper near `expected_external_tool_command()`**

Add after `expected_external_tool_command()`:

```python
def validate_expected_external_tool_command(
    command_name: str,
    label: str,
    command: object,
    *parts: str,
) -> None:
    try:
        actual_parts = shlex.split(str(command))
    except ValueError as exc:
        raise SmokeError(
            f"{command_name} {label} command is not shell-parseable: {exc}"
        ) from exc
    assert_equal(
        f"{command_name} {label} command",
        actual_parts,
        ["fashion-radar", *parts],
    )
```

- [ ] **Step 2: Run currently RED tests to confirm still failing before call sites**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_workflow_rejects_extra_readiness_command_flag tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_wrong_workflow_output_format tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_wrong_dry_run_input_format -q
```

Expected result: still fail because the helper is not wired into validators
yet.

## Task 3: Wire exact checks into external-tool validators

**Files:**

- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Replace workflow substring checks**

In `validate_external_tool_workflow()`, after the populated-field checks, keep
payload-derived local values:

```python
    adapter_id = str(payload["adapter_id"])
    directory = str(payload["directory"])
    config_dir = str(payload["config_dir"])
    data_dir = str(payload["data_dir"])
    as_of = str(payload["as_of"])
    input_format = str(payload["input_format"])
    pattern = str(payload["pattern"])
    source_name = str(payload["source_name"])
```

Replace registry, readiness, template, and lint command substring loops with:

```python
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
```

```python
    validate_expected_external_tool_command(
        command_name,
        "readiness",
        readiness_step.get("command", ""),
        "external-tool-readiness",
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
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--format",
        "table",
    )
```

```python
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

```python
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
```

- [ ] **Step 2: Replace readiness substring checks**

In `validate_external_tool_readiness()`, after the populated-field checks, keep
payload-derived local values:

```python
    adapter_id = str(payload["adapter_id"])
    directory = str(payload["directory"])
    config_dir = str(payload["config_dir"])
    data_dir = str(payload["data_dir"])
    as_of = str(payload["as_of"])
    input_format = str(payload["input_format"])
    pattern = str(payload["pattern"])
    source_name = str(payload["source_name"])
```

Replace workflow and dry-run command substring loops with:

```python
    validate_expected_external_tool_command(
        command_name,
        "workflow",
        workflow_step.get("command", ""),
        "external-tool-workflow",
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
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--format",
        "table",
    )
```

```python
    validate_expected_external_tool_command(
        command_name,
        "dry-run",
        dry_run_step.get("command", ""),
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
```

- [ ] **Step 3: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_workflow_rejects_extra_readiness_command_flag tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_wrong_workflow_output_format tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_wrong_dry_run_input_format -q
```

Expected result: pass.

## Task 4: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-135-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-135-code-review.md`

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

Expected result: focused tests, contract parity tests, lint, format, live
first-run smoke, and whitespace checks pass.

- [ ] **Step 2: Write Stage 135 code review prompt**

Create `docs/reviews/opencode-stage-135-code-review-prompt.md` with:

```markdown
Review the Stage 135 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Harden first-run smoke validation for external/community tool workflow
  command shapes by comparing parsed shell argv lists exactly.
- Keep expected path values derived from payload fields so temporary first-run
  smoke directories remain valid.
- Keep this validation-only with no CLI runtime behavior changes.

Files changed:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 135 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 135 design and plan?
2. Do the RED tests prove current substring checks were too weak?
3. Does the helper use `shlex.split()` and exact argv comparison rather than
   direct string equality?
4. Are expected path arguments derived from payload values instead of hardcoded
   `exports`, `configs`, and `data`?
5. Does the stage avoid runtime CLI behavior changes, docs wording changes,
   package/archive checker changes, dependencies, `uv.lock`, connectors,
   scraping, browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, generated command
   execution, PATH lookup behavior changes, import behavior, SQLite behavior,
   file-read behavior, artifact creation behavior, and compliance/audit product
   behavior?

Return:
Start with `# Stage 135 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
```

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-135-code-review-prompt.md)" > "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-135-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 135 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-135-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 5: Release gate, commit, push, and CI

**Files:**

- Stage all Stage 135 files only.

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

Expected result: all commands pass.

- [ ] **Step 2: Commit Stage 135**

Run:

```bash
git status --short --untracked-files=all
git add scripts/check_first_run_smoke.py tests/test_first_run_smoke.py docs/superpowers/specs/2026-06-21-stage-135-first-run-external-tool-command-shape-design.md docs/superpowers/plans/2026-06-21-stage-135-first-run-external-tool-command-shape-plan.md docs/reviews/opencode-stage-135-plan-review-prompt.md docs/reviews/opencode-stage-135-plan-review.md docs/reviews/opencode-stage-135-code-review-prompt.md docs/reviews/opencode-stage-135-code-review.md
git commit -m "Harden external tool command shape smoke checks"
```

Expected result: one commit containing only Stage 135 first-run smoke checker,
tests, design, plan, and review artifacts.

- [ ] **Step 3: Push with ephemeral credentials**

Use the established one-shot push pattern from the operator shell, deriving the
credential header only in process memory and passing it through `git -c` for
that single command. Do not write the token, derived header, or push command
containing credentials into files, git config, shell profile, or review
artifacts. Clear the temporary shell variable immediately after the push, then
verify no persistent GitHub credential header remains:

```bash
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub credential header
remains.

- [ ] **Step 4: Verify remote and CI**

Run:

```bash
git ls-remote origin refs/heads/main
```

Expected result: remote `main` points to the new commit. Poll GitHub Actions for
that SHA until CI completes.

## Self-Review

- Spec coverage: the plan covers RED tests, helper implementation, validator
  wiring, focused verification, opencode code review, release gate, commit,
  push, and CI check.
- Placeholder scan: no placeholder implementation steps are present.
- Type consistency: helper names, validator labels, payload fields, and test
  names are consistent across tasks.
