# Stage 142 Readiness Install Hint Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `external-tool-readiness` first-run smoke validation reject install-hint shell-text drift instead of accepting any string containing the old required fragments.

**Architecture:** Add one expected install-hint constant in `scripts/check_first_run_smoke.py`, add a RED drift test in `tests/test_first_run_smoke.py`, and replace substring validation with `assert_equal()`.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-142-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-142-plan-review.md`

- [x] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-142-plan-review-prompt.md`:

```markdown
# Stage 142 Plan Review Prompt

You are reviewing the Stage 142 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-readiness` first-run smoke validation so the Rednote MCP `install_hint` must match the exact expected string.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-142-readiness-install-hint-exact-design.md`
- `docs/superpowers/plans/2026-06-21-stage-142-readiness-install-hint-exact-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_readiness.py`

Please review:
- Whether the exact expected install hint matches runtime builder output.
- Whether the RED test would fail before implementation and pass after exact equality.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [x] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-142-plan-review-prompt.md)" > /tmp/opencode-stage-142-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-142-plan-review.md`.

- [x] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-142-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-142-plan-review.md`.

### Task 2: RED Test

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [x] **Step 1: Add install-hint drift test**

Add near the existing external-tool-readiness contract tests:

```python
def test_validate_external_tool_readiness_rejects_install_hint_extra_shell_text() -> None:
    payload = external_tool_readiness_payload()
    checks = payload["checks"]
    assert isinstance(checks, list)
    checks[0]["install_hint"] = (
        "npm install -g rednote-mcp using registry.npmmirror.com; "
        "do not set the npm registry first"
    )

    with pytest.raises(smoke.SmokeError, match="install_hint"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)
```

- [x] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "install_hint_extra_shell_text"
```

Expected: test fails because the current validator accepts the drifted hint.

### Task 3: Exact Install Hint Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [x] **Step 1: Add expected install-hint constant**

Add near the other expected external-tool constants:

```python
EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT = (
    "npm config set registry https://registry.npmmirror.com && npm install -g rednote-mcp"
)
```

- [x] **Step 2: Replace substring loop**

Replace:

```python
for expected in ("registry.npmmirror.com", "npm install -g rednote-mcp"):
    if expected not in install_hint:
        raise SmokeError(f"{command_name} check install_hint missing {expected!r}")
```

with:

```python
assert_equal(
    f"{command_name} check install_hint",
    install_hint,
    EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT,
)
```

- [x] **Step 3: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "install_hint_extra_shell_text"
```

Expected: test passes.

### Task 4: Focused Verification and Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-142-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-142-code-review.md`

- [x] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Expected: all commands exit 0.

- [x] **Step 2: Write code review prompt**

Create `docs/reviews/opencode-stage-142-code-review-prompt.md`:

```markdown
# Stage 142 Code Review Prompt

You are reviewing Stage 142 changes in `/home/ubuntu/fashion-radar`.

Base commit: `894af43aff3770f42642a506a433cfae93d4aecb`

Review scope:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 142 plan and review docs

Requirements:
- `external-tool-readiness` smoke validation must reject Rednote MCP install-hint shell-text drift.
- Runtime builder/output behavior must not change.
- RED/GREEN should prove the old substring check accepted drift and exact equality rejects it.

Please report findings first with severity and file/line references. If there are no blocking findings, say that explicitly.
```

- [x] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-142-code-review-prompt.md)" > /tmp/opencode-stage-142-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-142-code-review.md`.

- [x] **Step 4: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-142-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-142-code-review.md`.

### Task 5: Release Gate, Commit, Push, CI

**Files:**
- Commit all Stage 142 files after verification and review.

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

- [ ] **Step 2: Commit Stage 142**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-21-stage-142-readiness-install-hint-exact-design.md docs/superpowers/plans/2026-06-21-stage-142-readiness-install-hint-exact-plan.md docs/reviews/opencode-stage-142-plan-review-prompt.md docs/reviews/opencode-stage-142-plan-review.md docs/reviews/opencode-stage-142-code-review-prompt.md docs/reviews/opencode-stage-142-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Tighten readiness install hint validation"
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
