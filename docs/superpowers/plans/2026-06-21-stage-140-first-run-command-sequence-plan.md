# Stage 140 First-Run Command Sequence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace loose first-run command-capture assertions with an exact expected argv sequence for every local command emitted by `run_first_run_flow()`.

**Architecture:** Keep all changes in `tests/test_first_run_smoke.py`. Add a reusable expected-command helper and a helper-negative test, then have the deterministic first-run flow test compare the full captured command list to that expected list.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke test fixtures.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-140-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-140-plan-review.md`

- [ ] **Step 1: Write the opencode plan review prompt**

Create `docs/reviews/opencode-stage-140-plan-review-prompt.md` with:

```markdown
# Stage 140 Plan Review Prompt

You are reviewing the Stage 140 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Tighten the first-run smoke flow command capture test so every emitted command is compared as an exact argv tuple.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-140-first-run-command-sequence-design.md`
- `docs/superpowers/plans/2026-06-21-stage-140-first-run-command-sequence-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the expected command sequence exactly matches `run_first_run_flow()`.
- Whether the proposed helper-negative RED test catches drift the old membership checks missed.
- Whether the plan avoids runtime behavior changes.
- Whether focused verification is sufficient before release gate.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-140-plan-review-prompt.md)" > /tmp/opencode-stage-140-plan-review.md
```

Expected: exit code 0 and a review file in `/tmp/opencode-stage-140-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-140-plan-review.md`. Strip live narration before the actual review heading if present. Save the reviewed body to `docs/reviews/opencode-stage-140-plan-review.md`.

### Task 2: RED Test

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add helper-negative test before helpers exist**

Add this test above `test_run_first_run_flow_uses_deterministic_local_command_sequence()`:

```python
def test_assert_first_run_flow_commands_rejects_tail_command_extra_args(
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    example_csv = tmp_path / smoke.EXAMPLE_CSV
    captured = expected_first_run_flow_commands(context, example_csv)
    drifted = list(captured)
    handoff_index = next(
        index
        for index, command in enumerate(drifted)
        if command[0] == "community-handoff-workflow"
    )
    drifted[handoff_index] = (*drifted[handoff_index], "--extra")

    with pytest.raises(AssertionError):
        assert_first_run_flow_commands(drifted, context, example_csv)
```

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "first_run_flow_commands"
```

Expected: fail because `expected_first_run_flow_commands` is not defined.

### Task 3: Exact Command Helper and Replacement

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add exact expected command helper**

Add this helper after `test_constants_pin_first_run_sample_inputs()` and before `test_cli_command_runs_fashion_radar_module()`:

```python
def expected_first_run_flow_commands(
    context: smoke.SmokeContext,
    example_csv: Path,
) -> list[tuple[str, ...]]:
    return [
        (
            "init",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--reports-dir",
            str(context.reports_dir),
        ),
        ("migrate-db", "--data-dir", str(context.data_dir)),
        (
            "doctor",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--reports-dir",
            str(context.reports_dir),
        ),
        ("external-tool-adapters", "--format", "json"),
        ("external-tool-template", "--adapter", "rednote_mcp", "--format", "json"),
        (
            "external-tool-workflow",
            "--adapter",
            "rednote_mcp",
            "--directory",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--format",
            "json",
        ),
        (
            "external-tool-readiness",
            "--adapter",
            "rednote_mcp",
            "--directory",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--format",
            "json",
        ),
        (
            "community-signal-lint",
            str(example_csv),
            "--input-format",
            "csv",
            "--source-name",
            smoke.SOURCE_NAME,
        ),
        (
            "community-candidates",
            str(example_csv),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        (
            "import-signals",
            str(example_csv),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--source-name",
            smoke.SOURCE_NAME,
            "--dry-run",
        ),
        (
            "import-signals",
            str(example_csv),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--source-name",
            smoke.SOURCE_NAME,
            "--imported-at",
            smoke.AS_OF,
        ),
        ("match", "--config-dir", str(context.config_dir), "--data-dir", str(context.data_dir)),
        (
            "imported-review-workflow",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        ("imported-signals-summary", "--data-dir", str(context.data_dir), "--format", "json"),
        (
            "imported-signals",
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        (
            "report",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--reports-dir",
            str(context.reports_dir),
            "--as-of",
            smoke.AS_OF,
        ),
        (
            "candidates",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--format",
            "json",
        ),
        (
            "trends",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--format",
            "json",
        ),
        (
            "community-handoff-workflow",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--input-format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        (
            "community-signal-lint-dir",
            str(context.exports_dir),
            "--input-format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--source-name",
            smoke.SOURCE_NAME,
        ),
        (
            "community-candidates-dir",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        (
            "import-signals-dir",
            str(context.exports_dir),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--source-name",
            smoke.SOURCE_NAME,
            "--dry-run",
        ),
    ]


def assert_first_run_flow_commands(
    captured: list[tuple[str, ...]],
    context: smoke.SmokeContext,
    example_csv: Path,
) -> None:
    assert captured == expected_first_run_flow_commands(context, example_csv)
```

- [ ] **Step 2: Replace loose assertions**

In `test_run_first_run_flow_uses_deterministic_local_command_sequence()`, after:

```python
smoke.run_first_run_flow(context)
```

replace the command-name list assertion, `commands_named()`, `single_command()`, the membership loop, and exact partial command assertions with:

```python
assert_first_run_flow_commands(captured, context, example_csv)
```

Keep the final exported CSV content assertion.

- [ ] **Step 3: Run GREEN focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "first_run_flow_commands or deterministic_local_command_sequence"
```

Expected: helper-negative test and deterministic command sequence test pass.

### Task 4: Focused Verification and Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-140-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-140-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Write code review prompt**

Create `docs/reviews/opencode-stage-140-code-review-prompt.md` with:

```markdown
# Stage 140 Code Review Prompt

You are reviewing Stage 140 changes in `/home/ubuntu/fashion-radar`.

Base commit: `4ad41b45d89d5c872a7b0d8d1c1a2b6162073837`

Review scope:
- `tests/test_first_run_smoke.py`
- Stage 140 plan and review docs

Requirements:
- The deterministic first-run flow test must compare the full captured command sequence as exact argv tuples.
- Runtime smoke behavior must not change.
- The helper-negative test must prove exact comparison rejects command drift that old membership checks missed.

Please report findings first with severity and file/line references. If there are no blocking findings, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-140-code-review-prompt.md)" > /tmp/opencode-stage-140-code-review.md
```

Expected: exit code 0 and a review file in `/tmp/opencode-stage-140-code-review.md`.

- [ ] **Step 4: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-140-code-review.md`. Strip live narration before the actual review heading if present. Save the reviewed body to `docs/reviews/opencode-stage-140-code-review.md`.

### Task 5: Release Gate, Commit, Push, CI

**Files:**
- Commit all Stage 140 files after verification and review.

- [ ] **Step 1: Run release gate**

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

- [ ] **Step 2: Commit Stage 140**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-21-stage-140-first-run-command-sequence-design.md docs/superpowers/plans/2026-06-21-stage-140-first-run-command-sequence-plan.md docs/reviews/opencode-stage-140-plan-review-prompt.md docs/reviews/opencode-stage-140-plan-review.md docs/reviews/opencode-stage-140-code-review-prompt.md docs/reviews/opencode-stage-140-code-review.md tests/test_first_run_smoke.py
git commit -m "Pin first-run command sequence assertions"
```

Expected: commit succeeds.

- [ ] **Step 3: Push with ephemeral auth**

Use an ephemeral HTTP extraheader only for this push. Do not persist the token or auth header.

Run:

```bash
git -c http.https://github.com/.extraheader="$AUTH_HEADER" push origin main
git config --get-all http.https://github.com/.extraheader || true
```

Expected: push succeeds, and the second command prints nothing.

- [ ] **Step 4: Poll CI**

Use the GitHub Actions API because `gh` is not installed:

```bash
uv --no-config run --frozen python - <<'PY'
import json
import time
import urllib.request

run_id = "<new-run-id>"
url = f"https://api.github.com/repos/Lordakee/fashion-radar/actions/runs/{run_id}"
for attempt in range(40):
    with urllib.request.urlopen(url, timeout=30) as response:
        run = json.load(response)
    status = run.get("status")
    conclusion = run.get("conclusion")
    print(f"attempt={attempt + 1} status={status} conclusion={conclusion} url={run.get('html_url')}")
    if status == "completed":
        raise SystemExit(0 if conclusion == "success" else 1)
    time.sleep(15)
raise SystemExit("CI run did not complete within polling window")
PY
```

Expected: CI conclusion is `success`.

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
