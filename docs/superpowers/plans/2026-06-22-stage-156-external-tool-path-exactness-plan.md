# Stage 156 External Tool Path Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `external-tool-workflow` and `external-tool-readiness` first-run
smoke validators reject coordinated drift in top-level `directory`, `config_dir`,
and `data_dir` fields.

**Architecture:** Keep runtime builders unchanged. Add RED tests for coordinated
path drift and explicit runtime-path acceptance, then add keyword-only expected
path parameters to both smoke validators and thread `SmokeContext` paths from the
real first-run flow. Update deterministic smoke-flow fake stdout to use
context-specific external-tool payloads.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-156-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-156-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-156-plan-review-prompt.md` asking opencode
to review this plan and the design.

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-156-plan-review-prompt.md)" > /tmp/opencode-stage-156-plan-review.md
```

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-156-plan-review.md`. Strip live narration before the
review heading if present. Save the body to
`docs/reviews/opencode-stage-156-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add external-tool path rewrite helper**

Add `rewrite_external_tool_payload_paths(...)` near the existing workflow payload
helpers. It must use `shlex.split()` / `shlex.join()` and replace only complete
argv tokens `exports`, `configs`, and `data`.

- [ ] **Step 2: Add coordinated drift RED test**

Add a parametrized test over:

- `external_tool_workflow_payload` / `smoke.validate_external_tool_workflow`
- `external_tool_readiness_payload` / `smoke.validate_external_tool_readiness`
- `directory`, `config_dir`, and `data_dir`

The test mutates the top-level path and rewrites nested command argv
consistently. It expects `SmokeError` matching the drifted field.

- [ ] **Step 3: Add explicit runtime path acceptance RED test**

Add a parametrized test proving each validator accepts kwargs:

```python
expected_directory=...
expected_config_dir=...
expected_data_dir=...
```

Expected before implementation: `TypeError` because the validators do not yet
accept these kwargs.

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_surfaces_reject_coordinated_top_level_path_drift or external_tool_surfaces_accept_explicit_runtime_paths"
```

Expected before implementation: failures proving the gap.

### Task 3: Validator Exactness

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Update `validate_external_tool_workflow()` signature**

Add keyword-only defaults:

```python
expected_directory: str = "exports"
expected_config_dir: str = "configs"
expected_data_dir: str = "data"
```

- [ ] **Step 2: Assert external workflow top-level path fields**

Replace non-empty-only path checks with exact `assert_equal(...)` checks against
the expected path kwargs. Synthesize nested expected command argv from these
expected values, not from payload values.

- [ ] **Step 3: Update `validate_external_tool_readiness()` signature**

Apply the same keyword-only defaults.

- [ ] **Step 4: Assert external readiness top-level path fields**

Apply the same exact `assert_equal(...)` pattern and expected-value command
synthesis.

- [ ] **Step 5: Thread runtime paths through `run_first_run_flow()`**

Pass `str(context.exports_dir)`, `str(context.config_dir)`, and
`str(context.data_dir)` into both validators.

- [ ] **Step 6: Update deterministic flow fake stdout**

Add helper functions that return `external_tool_workflow_payload()` and
`external_tool_readiness_payload()` rewritten to the test `context` paths. Use
those helpers in `test_run_first_run_flow_uses_deterministic_local_command_sequence()`.

- [ ] **Step 7: Run focused GREEN verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_surfaces_reject_coordinated_top_level_path_drift or external_tool_surfaces_accept_explicit_runtime_paths"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness or first_run_flow"
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: all pass.

### Task 4: Review, Release Gate, and Commit

**Files:**
- Create: `docs/reviews/opencode-stage-156-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-156-code-review.md`

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

Create `docs/reviews/opencode-stage-156-code-review-prompt.md`, then run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-156-code-review-prompt.md)" > /tmp/opencode-stage-156-code-review.md
```

- [ ] **Step 3: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-156-code-review.md`. Strip live narration before the
review heading if present. Save the body to
`docs/reviews/opencode-stage-156-code-review.md`.

- [ ] **Step 4: Run release gate**

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
  docs/reviews/opencode-stage-156-plan-review-prompt.md \
  docs/reviews/opencode-stage-156-plan-review.md \
  docs/reviews/opencode-stage-156-code-review-prompt.md \
  docs/reviews/opencode-stage-156-code-review.md \
  docs/superpowers/specs/2026-06-22-stage-156-external-tool-path-exactness-design.md \
  docs/superpowers/plans/2026-06-22-stage-156-external-tool-path-exactness-plan.md
git commit -m "feat: pin external tool workflow paths"
```
