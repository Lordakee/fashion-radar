# Stage 144 Imported Review Command Argv Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `imported-review-workflow` first-run smoke validation reject command drift for every workflow step.

**Architecture:** Keep runtime workflow builders unchanged. Add one expected-command helper to the smoke checker, extend the existing RED command drift test with the four currently unpinned imported-review commands, then replace the one-off exact command checks with an exact argv loop for all seven steps.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-144-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-144-plan-review.md`

- [x] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-144-plan-review-prompt.md`:

```markdown
# Stage 144 Plan Review Prompt

You are reviewing the Stage 144 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `imported-review-workflow` first-run smoke validation so all seven workflow step commands must match exact argv.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-144-imported-review-command-argv-design.md`
- `docs/superpowers/plans/2026-06-21-stage-144-imported-review-command-argv-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`

Please review:
- Whether the expected argv parts match `build_imported_review_workflow()`.
- Whether the RED test would fail before implementation and pass after exact argv validation.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [x] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-144-plan-review-prompt.md)" > /tmp/opencode-stage-144-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-144-plan-review.md`.

- [x] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-144-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-144-plan-review.md`.

### Task 2: RED Test

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [x] **Step 1: Extend imported review command drift cases**

Add these four cases to `test_validate_imported_review_workflow_rejects_command_argv_drift()` before the existing entity-evidence/candidate/final-heat cases:

```python
        (
            "summarize_imported_sources",
            "fashion-radar imported-signals-summary --data-dir other-data",
            "summary command",
        ),
        (
            "refresh_stored_matches",
            "fashion-radar match --config-dir configs",
            "match refresh command",
        ),
        (
            "compare_imported_entities",
            (
                "fashion-radar imported-entity-deltas --data-dir data "
                "--as-of 2026-06-13T12:00:00+00:00 "
                "--current-days 14 --baseline-days 7 "
                "--source-name 'Community Tool Export'"
            ),
            "entity delta command",
        ),
        (
            "review_unmatched_imported_rows",
            (
                "fashion-radar imported-signals --data-dir data "
                "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 7 "
                "--source-name 'Community Tool Export'"
            ),
            "unmatched rows command",
        ),
```

- [x] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and command_argv_drift"
```

Expected: the new cases fail with `DID NOT RAISE` because the current validator accepts the four mutated unpinned commands. The three existing cases should still pass.

### Task 3: Exact Command Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [x] **Step 1: Add expected-command helper**

Add near the other workflow command helpers:

```python
def expected_imported_review_workflow_command_parts(
    *,
    config_dir: str,
    data_dir: str,
    as_of: str,
    source_name: str,
    lookback_days: str,
    current_days: str,
    baseline_days: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    source_args = ("--source-name", source_name) if source_name else ()
    return (
        ("summary", ("imported-signals-summary", "--data-dir", data_dir)),
        ("match refresh", ("match", "--config-dir", config_dir, "--data-dir", data_dir)),
        (
            "entity delta",
            (
                "imported-entity-deltas",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--current-days",
                current_days,
                "--baseline-days",
                baseline_days,
                *source_args,
            ),
        ),
        (
            "entity evidence",
            (
                "imported-entity-evidence",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--entity-name",
                "The Row",
                "--entity-type",
                "brand",
                "--current-days",
                current_days,
                "--baseline-days",
                baseline_days,
                *source_args,
            ),
        ),
        (
            "candidate",
            (
                "imported-candidates",
                "--config-dir",
                config_dir,
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                *source_args,
            ),
        ),
        (
            "unmatched rows",
            (
                "imported-signals",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--lookback-days",
                lookback_days,
                "--unmatched-only",
                *source_args,
            ),
        ),
        ("final heat", ("heat-movers", "--config-dir", config_dir, "--data-dir", data_dir, "--as-of", as_of)),
    )
```

- [x] **Step 2: Extract `lookback_days` and replace one-off checks**

In `validate_imported_review_workflow()`, add:

```python
    lookback_days = str(payload.get("lookback_days", ""))
```

Then replace the three one-off exact command checks with:

```python
    expected_commands = expected_imported_review_workflow_command_parts(
        config_dir=config_dir,
        data_dir=data_dir,
        as_of=as_of,
        source_name=source_name,
        lookback_days=lookback_days,
        current_days=current_days,
        baseline_days=baseline_days,
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

    heat_step = steps[-1]
    if not isinstance(heat_step, dict):
        raise SmokeError(f"{command_name} heat step must be a JSON object")
    assert_equal(f"{command_name} final step", heat_step.get("name"), "review_local_heat_movers")
```

Keep the final step assertion so the existing heat-position guard remains explicit.

- [x] **Step 3: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow and command_argv_drift"
```

Expected: all seven command drift cases pass.

### Task 4: Focused Verification and Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-144-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-144-code-review.md`

- [x] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Expected: all commands exit 0.

- [x] **Step 2: Write code review prompt**

Create `docs/reviews/opencode-stage-144-code-review-prompt.md`:

```markdown
# Stage 144 Code Review Prompt

You are reviewing Stage 144 changes in `/home/ubuntu/fashion-radar`.

Base commit: `22deb60`

Review scope:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 144 plan and review docs

Requirements:
- `imported-review-workflow` smoke validation must reject command drift for every workflow step.
- Runtime builder/output behavior must not change.
- RED/GREEN should prove the old validator accepted unpinned command drift and exact argv validation rejects it.

Please report findings first with severity and file/line references. If there are no blocking findings, say that explicitly.
```

- [x] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-144-code-review-prompt.md)" > /tmp/opencode-stage-144-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-144-code-review.md`.

- [x] **Step 4: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-144-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-144-code-review.md`.

### Task 5: Release Gate, Commit, Push, CI

**Files:**
- Commit all Stage 144 files after verification and review.

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

- [ ] **Step 2: Commit Stage 144**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-21-stage-144-imported-review-command-argv-design.md docs/superpowers/plans/2026-06-21-stage-144-imported-review-command-argv-plan.md docs/reviews/opencode-stage-144-plan-review-prompt.md docs/reviews/opencode-stage-144-plan-review.md docs/reviews/opencode-stage-144-code-review-prompt.md docs/reviews/opencode-stage-144-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Harden imported review workflow commands"
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
