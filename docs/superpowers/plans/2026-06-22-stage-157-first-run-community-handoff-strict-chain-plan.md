# Stage 157 First-Run Community Handoff Strict Chain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the first-run smoke flow directly execute the stricter local community handoff directory checks already declared by `community-handoff-workflow`.

**Architecture:** Keep the first-run smoke script as the single orchestration surface and the deterministic command-sequence test as the regression guard. Tighten only command arguments and sequence around the existing local community handoff directory commands.

**Tech Stack:** Python, pytest, Typer CLI entrypoints, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `scripts/check_first_run_smoke.py`
  - Add `--strict` to the direct `community-signal-lint-dir` call.
  - Add a direct `community-handoff-check-dir ... --strict` call.
  - Add `--imported-at AS_OF` to the direct `import-signals-dir ... --dry-run` call.
- Modify: `tests/test_first_run_smoke.py`
  - Update `expected_first_run_flow_commands()` to require the stricter command sequence.
- Add: `docs/reviews/opencode-stage-157-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-157-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-157-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-157-code-review.md`

## Task 1: Prove The Current First-Run Sequence Is Too Loose

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Update `expected_first_run_flow_commands()` for `community-signal-lint-dir`**

Change the existing tuple for `community-signal-lint-dir` so it ends with `--strict`:

```python
        (
            "community-signal-lint-dir",
            str(context.exports_dir),
            "--input-format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--source-name",
            smoke.SOURCE_NAME,
            "--strict",
        ),
```

- [ ] **Step 2: Add the expected `community-handoff-check-dir` command**

Insert this tuple after `community-candidates-dir` and before `import-signals-dir`:

```python
        (
            "community-handoff-check-dir",
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
            "--strict",
        ),
```

- [ ] **Step 3: Update the expected `import-signals-dir` dry-run command**

Change the existing tuple so `--imported-at smoke.AS_OF` appears before
`--dry-run`:

```python
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
            "--imported-at",
            smoke.AS_OF,
            "--dry-run",
        ),
```

- [ ] **Step 4: Run the focused RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
```

Expected: FAIL. The captured command sequence should differ because the
implementation still omits `--strict`, does not run `community-handoff-check-dir`,
and omits `--imported-at`.

## Task 2: Implement The Stricter First-Run Command Chain

**Files:**

- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add `--strict` to the direct directory lint call**

Update the `run_cli(context, "community-signal-lint-dir", ...)` call after
`validate_community_handoff_workflow(...)`:

```python
    run_cli(
        context,
        "community-signal-lint-dir",
        str(context.exports_dir),
        "--input-format",
        "csv",
        "--pattern",
        DIR_PATTERN,
        "--source-name",
        SOURCE_NAME,
        "--strict",
    )
```

- [ ] **Step 2: Add the direct handoff readiness check**

Insert this call after `validate_community_candidates(...)` returns for the
existing `community-candidates-dir` JSON payload and before the
`import-signals-dir` dry-run:

```python
    run_cli(
        context,
        "community-handoff-check-dir",
        str(context.exports_dir),
        "--config-dir",
        str(context.config_dir),
        "--input-format",
        "csv",
        "--pattern",
        DIR_PATTERN,
        "--as-of",
        AS_OF,
        "--source-name",
        SOURCE_NAME,
        "--strict",
    )
```

- [ ] **Step 3: Add `--imported-at AS_OF` to the dry-run directory import**

Update the existing `import-signals-dir` dry-run call to include:

```python
            "--imported-at",
            AS_OF,
            "--dry-run",
```

Keep `--dry-run` present. Do not add the write-capable `import-signals-dir`
workflow command without `--dry-run`.

- [ ] **Step 4: Run the focused GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
```

Expected: PASS.

## Task 3: Verify Focused Smoke Coverage

**Files:**

- No code changes expected.

- [ ] **Step 1: Run first-run smoke focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "community_handoff or first_run_flow or import_signals_dir"
```

Expected: all selected tests pass.

- [ ] **Step 2: Run the real first-run smoke script**

Run:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected:

```text
First-run sample smoke passed.
```

- [ ] **Step 3: Run the full first-run smoke test module**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
```

Expected: all tests in `tests/test_first_run_smoke.py` pass.

## Task 4: Code Review And Release Gate

**Files:**

- Add: `docs/reviews/opencode-stage-157-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-157-code-review.md`

- [ ] **Step 1: Create the code review prompt**

Write `docs/reviews/opencode-stage-157-code-review-prompt.md` with this review
scope:

```text
Review Stage 157. Confirm that run_first_run_flow directly executes the stricter
community handoff directory chain without adding platform collection or
write-capable directory import behavior. Check tests prove the strict command
sequence, and check verification evidence.
```

- [ ] **Step 2: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-157-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-157-code-review.md
rm -f "$tmp_review"
```

Expected: no critical or important findings. Fix any critical or important
findings before continuing.

- [ ] **Step 3: Run the release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected:

- Full pytest passes.
- First-run smoke prints `First-run sample smoke passed.`
- Ruff check passes.
- Ruff format check passes.
- Lock check passes.
- `git diff --check` prints nothing.
- Token and persistent header checks find nothing.

## Task 5: Commit And Push

**Files:**

- Stage only Stage 157 implementation, tests, plan, and review artifacts.

- [ ] **Step 1: Inspect status**

Run:

```bash
git status --short --branch
git diff --stat
```

- [ ] **Step 2: Stage exact files**

Run:

```bash
git add \
  scripts/check_first_run_smoke.py \
  tests/test_first_run_smoke.py \
  docs/superpowers/specs/2026-06-22-stage-157-first-run-community-handoff-strict-chain-design.md \
  docs/superpowers/plans/2026-06-22-stage-157-first-run-community-handoff-strict-chain-plan.md \
  docs/reviews/opencode-stage-157-plan-review-prompt.md \
  docs/reviews/opencode-stage-157-plan-review.md \
  docs/reviews/opencode-stage-157-code-review-prompt.md \
  docs/reviews/opencode-stage-157-code-review.md
```

- [ ] **Step 3: Commit**

Run:

```bash
git commit -m "test: run strict community handoff smoke chain"
```

- [ ] **Step 4: Push with one-shot auth header**

Run:

```bash
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 | tr -d '\n') && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" push origin main
```

- [ ] **Step 5: Confirm sync and clean state**

Run:

```bash
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected: local branch clean and local HEAD matches remote `refs/heads/main`.

## Self-Review

- Spec coverage: The plan covers strict lint, direct handoff check, imported-at
  dry-run, focused tests, real smoke, code review, release gate, and push.
- Placeholder scan: No TBD/TODO placeholders remain.
- Type consistency: Command names, constants, and paths match the existing smoke
  script and tests.
