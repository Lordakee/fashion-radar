# Stage 185 First-Run Trends Delta Shape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject malformed non-object entries in first-run smoke `trends.deltas` with a precise `SmokeError`.

**Architecture:** Add a small structural validation loop to `scripts/check_first_run_smoke.py::validate_trends(...)` and a focused regression test in `tests/test_first_run_smoke.py`. Keep downstream trend content assertions unchanged and keep the change limited to smoke validation.

**Tech Stack:** Python, pytest, existing first-run smoke script, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `scripts/check_first_run_smoke.py`
  - Add explicit per-entry object validation for `trends.deltas`.
- Modify: `tests/test_first_run_smoke.py`
  - Add `test_validate_trends_rejects_non_object_delta_entries`.
- Add: `docs/superpowers/specs/2026-06-24-stage-185-first-run-trends-delta-shape-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-185-first-run-trends-delta-shape-plan.md`
- Add: `docs/reviews/opencode-stage-185-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-185-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-185-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-185-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-185-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-185-release-review.md`

## Task 1: Add Trends Delta Shape Guard

**Files:**

- Modify: `tests/test_first_run_smoke.py`
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Confirm the new guard does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_validate_trends_rejects_non_object_delta_entries -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Add the failing regression test**

Add this test immediately after
`test_validate_candidates_and_trends_pin_expected_first_run_state`:

```python
def test_validate_trends_rejects_non_object_delta_entries() -> None:
    payload = trends_payload()
    deltas = payload["deltas"]
    assert isinstance(deltas, list)
    deltas.append("not-a-delta")

    with pytest.raises(smoke.SmokeError, match="trends delta 4 must be a JSON object"):
        smoke.validate_trends("trends", payload)
```

- [ ] **Step 3: Run the new test and verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_validate_trends_rejects_non_object_delta_entries -q
```

Expected after adding only the test: the test fails because
`validate_trends(...)` silently skips the string entry instead of raising
`SmokeError`.

- [ ] **Step 4: Add minimal runtime validation**

In `scripts/check_first_run_smoke.py::validate_trends(...)`, replace:

```python
deltas_by_name = {str(delta.get("name")): delta for delta in deltas if isinstance(delta, dict)}
```

with:

```python
delta_rows: list[Mapping[str, Any]] = []
for index, delta in enumerate(deltas, start=1):
    if not isinstance(delta, dict):
        raise SmokeError(f"{command_name} delta {index} must be a JSON object")
    delta_rows.append(delta)
delta_rows_by_name = {str(delta.get("name")): delta for delta in delta_rows}
```

Then update downstream references from `deltas_by_name` to
`delta_rows_by_name`:

```python
list(delta_rows_by_name)
delta = delta_rows_by_name[name]
```

- [ ] **Step 5: Run the new test and verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_validate_trends_rejects_non_object_delta_entries -q
```

Expected: the test passes.

## Task 2: Focused Verification And Code Review

**Files:**

- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Add: `docs/reviews/opencode-stage-185-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-185-code-review.md`

- [ ] **Step 1: Run focused first-run smoke tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "trends or candidates"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-185-code-review-prompt.md` requiring the
response body to start with:

```text
# Stage 185 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-185-code-review-prompt.md)" > "$tmp_review" 2>&1
awk 'BEGIN{copy=0} /^# Stage 185 Code Review/{copy=1} copy{print}' "$tmp_review" > docs/reviews/opencode-stage-185-code-review.md
if [ ! -s docs/reviews/opencode-stage-185-code-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-185-code-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no Critical or Important findings. Clean
the artifact if opencode includes process chatter, ANSI output, command logs,
code fences, or duplicated drafts.

## Task 3: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-185-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-185-release-review.md`

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

Create `docs/reviews/opencode-stage-185-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 185 Release Review
```

Run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-185-release-review.md`.

Expected: completed review output with no Critical or Important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  scripts/check_first_run_smoke.py \
  tests/test_first_run_smoke.py \
  docs/superpowers/specs/2026-06-24-stage-185-first-run-trends-delta-shape-design.md \
  docs/superpowers/plans/2026-06-24-stage-185-first-run-trends-delta-shape-plan.md \
  docs/reviews/opencode-stage-185-plan-review-prompt.md \
  docs/reviews/opencode-stage-185-plan-review.md \
  docs/reviews/opencode-stage-185-code-review-prompt.md \
  docs/reviews/opencode-stage-185-code-review.md \
  docs/reviews/opencode-stage-185-release-review-prompt.md \
  docs/reviews/opencode-stage-185-release-review.md
git commit -m "test: reject malformed trends deltas"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the structural delta guard, Task 2 covers focused
  verification and code review, and Task 3 covers release gate, release review,
  commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: CLI trend generation, scoring, models, heat movers, dashboard,
  package archives, dependencies, source acquisition, ranking, monitoring,
  scraping, and compliance-review product behavior remain out of scope.
