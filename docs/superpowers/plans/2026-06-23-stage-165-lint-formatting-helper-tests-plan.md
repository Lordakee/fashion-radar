# Stage 165 Lint Formatting Helper Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add direct unit coverage for the shared lint finding-count formatting helper.

**Architecture:** Create one focused pytest module for `fashion_radar.lint_formatting`. Keep the helper implementation, caller renderers, CLI behavior, JSON output, docs output, and lint semantics unchanged unless the tests expose a real mismatch.

**Tech Stack:** Python standard library, pytest, existing `src` layout, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Create: `tests/test_lint_formatting.py`
  - Add direct tests for `format_count_label(...)`.
  - Add direct tests for `format_finding_counts(...)`.
- Add: `docs/superpowers/specs/2026-06-23-stage-165-lint-formatting-helper-tests-design.md`
- Add: `docs/superpowers/plans/2026-06-23-stage-165-lint-formatting-helper-tests-plan.md`
- Add: `docs/reviews/opencode-stage-165-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-165-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-165-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-165-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-165-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-165-release-review.md`

## Task 1: Add Direct Helper Characterization Tests

**Files:**

- Create: `tests/test_lint_formatting.py`

- [ ] **Step 1: Add the test file**

Create `tests/test_lint_formatting.py` with exactly this content:

```python
import pytest

from fashion_radar.lint_formatting import format_count_label, format_finding_counts


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (0, "0 errors"),
        (1, "1 error"),
        (2, "2 errors"),
    ],
)
def test_format_count_label_uses_singular_only_for_one(count: int, expected: str) -> None:
    assert format_count_label(count, "error", "errors") == expected


def test_format_finding_counts_formats_zero_counts() -> None:
    assert format_finding_counts(0, 0, 0) == "0 errors, 0 warnings, 0 info"


def test_format_finding_counts_formats_singular_counts() -> None:
    assert format_finding_counts(1, 1, 1) == "1 error, 1 warning, 1 info"


def test_format_finding_counts_formats_plural_counts() -> None:
    assert format_finding_counts(2, 2, 2) == "2 errors, 2 warnings, 2 info"


def test_format_finding_counts_formats_mixed_counts() -> None:
    assert format_finding_counts(1, 0, 2) == "1 error, 0 warnings, 2 info"
```

This is a characterization-test step for existing behavior. Do not edit
`src/fashion_radar/lint_formatting.py` first, and do not temporarily break the
helper just to manufacture a RED run.

- [ ] **Step 2: Run focused helper tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_lint_formatting.py -q
```

Expected: all tests pass against the existing helper.

- [ ] **Step 3: Run dependent renderer regression tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_source_packs.py \
  tests/test_entity_pack_lint.py \
  tests/test_community_signal_lint.py \
  -q -k "render_"
```

Expected: all selected renderer tests pass.

- [ ] **Step 4: Run focused lint and format checks**

Run:

```bash
uv --no-config run --frozen ruff check tests/test_lint_formatting.py
uv --no-config run --frozen ruff format --check tests/test_lint_formatting.py
```

Expected: both commands pass.

## Task 2: Run Stage 165 Review And Release Gate

**Files:**

- Add: `docs/reviews/opencode-stage-165-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-165-code-review.md`
- Add: `docs/reviews/opencode-stage-165-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-165-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-165-code-review-prompt.md` with a prompt
that asks local opencode to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-165-lint-formatting-helper-tests-design.md`
- `docs/superpowers/plans/2026-06-23-stage-165-lint-formatting-helper-tests-plan.md`
- `src/fashion_radar/lint_formatting.py`
- `tests/test_lint_formatting.py`

The prompt must require the response to start with:

```text
# Stage 165 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-165-code-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-165-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Fix
any critical or important findings before continuing.

- [ ] **Step 3: Run release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected:

- Full pytest suite passes.
- First-run smoke passes.
- Release hygiene passes.
- Ruff check and format checks pass.
- Lockfile check passes.
- `git diff --check` exits 0.
- Token scan prints no matches.
- GitHub extraheader check prints no token-bearing header.

- [ ] **Step 4: Create release review prompt**

Create `docs/reviews/opencode-stage-165-release-review-prompt.md` with a prompt
that asks local opencode to review the Stage 165 changes and release readiness.
The prompt must require the response to start with:

```text
# Stage 165 Release Review
```

- [ ] **Step 5: Run release review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-165-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-165-release-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Fix
any critical or important findings before committing.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short
git add \
  docs/superpowers/specs/2026-06-23-stage-165-lint-formatting-helper-tests-design.md \
  docs/superpowers/plans/2026-06-23-stage-165-lint-formatting-helper-tests-plan.md \
  docs/reviews/opencode-stage-165-plan-review-prompt.md \
  docs/reviews/opencode-stage-165-plan-review.md \
  docs/reviews/opencode-stage-165-code-review-prompt.md \
  docs/reviews/opencode-stage-165-code-review.md \
  docs/reviews/opencode-stage-165-release-review-prompt.md \
  docs/reviews/opencode-stage-165-release-review.md \
  tests/test_lint_formatting.py
git commit -m "test: cover lint finding formatting helper"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.
