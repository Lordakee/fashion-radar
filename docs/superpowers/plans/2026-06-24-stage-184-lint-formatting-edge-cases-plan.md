# Stage 184 Lint Formatting Edge Cases Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add direct tests proving `format_count_label(...)` uses caller-supplied singular/plural labels and singularizes only count `1`.

**Architecture:** Test-only hardening. Add one parametrized test to `tests/test_lint_formatting.py`, leave `src/fashion_radar/lint_formatting.py` untouched unless the test exposes a real defect, and keep existing `format_finding_counts(...)` tests unchanged.

**Tech Stack:** Python, pytest parametrization, existing lint formatting helper, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_lint_formatting.py`
  - Replace `test_format_count_label_uses_singular_only_for_one` with
    `test_format_count_label_uses_supplied_label_for_count`.
- Add: `docs/superpowers/specs/2026-06-24-stage-184-lint-formatting-edge-cases-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-184-lint-formatting-edge-cases-plan.md`
- Add: `docs/reviews/opencode-stage-184-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-184-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-184-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-184-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-184-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-184-release-review.md`

## Task 1: Broaden Count Label Edge-Case Guard

**Files:**

- Modify: `tests/test_lint_formatting.py`

- [ ] **Step 1: Confirm the broader guard does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_lint_formatting.py::test_format_count_label_uses_supplied_label_for_count -q
```

Expected before replacing the existing test: pytest reports the test name is not
found or no matching test is collected.

- [ ] **Step 2: Replace the narrow parametrized test**

Replace `test_format_count_label_uses_singular_only_for_one` with:

```python
@pytest.mark.parametrize(
    ("count", "singular", "plural", "expected"),
    [
        (0, "error", "errors", "0 errors"),
        (1, "error", "errors", "1 error"),
        (2, "error", "errors", "2 errors"),
        (1, "import-ready row", "import-ready rows", "1 import-ready row"),
        (2, "import-ready row", "import-ready rows", "2 import-ready rows"),
        (0, "valid file", "valid files", "0 valid files"),
        (2, "info", "info", "2 info"),
        (2, "analysis", "analyses", "2 analyses"),
    ],
)
def test_format_count_label_uses_supplied_label_for_count(
    count: int,
    singular: str,
    plural: str,
    expected: str,
) -> None:
    assert format_count_label(count, singular, plural) == expected
```

- [ ] **Step 3: Run the new test**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_lint_formatting.py::test_format_count_label_uses_supplied_label_for_count -q
```

Expected: the test passes. If it fails, inspect
`src/fashion_radar/lint_formatting.py::format_count_label` and only change the
helper if the failure exposes a real count-label defect.

## Task 2: Focused Verification And Code Review

**Files:**

- Modify: `tests/test_lint_formatting.py`
- Add: `docs/reviews/opencode-stage-184-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-184-code-review.md`

- [ ] **Step 1: Run focused lint formatting checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_lint_formatting.py -q
uv --no-config run --frozen ruff check tests/test_lint_formatting.py
uv --no-config run --frozen ruff format --check tests/test_lint_formatting.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-184-code-review-prompt.md` requiring the
response to start with:

```text
# Stage 184 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-184-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
awk 'BEGIN{copy=0} /^# Stage 184 Code Review/{copy=1} copy{print}' "$tmp_review" > docs/reviews/opencode-stage-184-code-review.md
if [ ! -s docs/reviews/opencode-stage-184-code-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-184-code-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact if opencode includes process chatter, ANSI output, command logs,
code fences, or multiple drafts.

## Task 3: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-184-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-184-release-review.md`

- [ ] **Step 1: Run release gate**

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

Expected: all commands pass; token and extraheader checks report no persisted
secrets. For the two absence checks, exit 1 with no output is the expected clean
result.

- [ ] **Step 2: Create and run release review**

Create `docs/reviews/opencode-stage-184-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 184 Release Review
```

Run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-184-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_lint_formatting.py \
  docs/superpowers/specs/2026-06-24-stage-184-lint-formatting-edge-cases-design.md \
  docs/superpowers/plans/2026-06-24-stage-184-lint-formatting-edge-cases-plan.md \
  docs/reviews/opencode-stage-184-plan-review-prompt.md \
  docs/reviews/opencode-stage-184-plan-review.md \
  docs/reviews/opencode-stage-184-code-review-prompt.md \
  docs/reviews/opencode-stage-184-code-review.md \
  docs/reviews/opencode-stage-184-release-review-prompt.md \
  docs/reviews/opencode-stage-184-release-review.md
git commit -m "test: cover lint count label edge cases"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the edge-case guard, Task 2 covers focused
  verification and code review, and Task 3 covers release gate, release review,
  commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: helper runtime behavior, renderers, package archive tests,
  smoke scripts, dependencies, lockfiles, source acquisition, ranking, coverage
  verification, and compliance-review product behavior remain out of scope
  unless the new test exposes a real defect.
