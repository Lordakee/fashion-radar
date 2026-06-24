# Stage 186 Readiness Skip Mark Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Broaden the readiness parity meta guard so a future bare `pytest.mark.skip` cannot silently disable the first-run external-tool readiness parity test.

**Architecture:** Test-only hardening in `tests/test_first_run_smoke.py`. Add a small helper that detects blocking readiness parity skip marks, prove it catches both `skipif` and `skip` with synthetic marks, then update the existing meta test to use that helper.

**Tech Stack:** Python, pytest marks, existing first-run smoke tests, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_first_run_smoke.py`
  - Add `BLOCKING_READINESS_PARITY_SKIP_MARKS`.
  - Add `has_blocking_readiness_parity_skip_mark(...)`.
  - Add `test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks`.
  - Update `test_external_tool_readiness_payload_parity_is_not_conditionally_skipped`.
- Add: `docs/superpowers/specs/2026-06-24-stage-186-readiness-skip-mark-guard-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-186-readiness-skip-mark-guard-plan.md`
- Add: `docs/reviews/opencode-stage-186-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-186-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-186-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-186-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-186-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-186-release-review.md`

## Task 1: Add Broad Readiness Skip-Mark Guard

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Confirm the new helper guard test does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Add the failing helper-focused test**

Add this test immediately after
`test_external_tool_readiness_payload_parity_is_not_conditionally_skipped`:

```python
@pytest.mark.parametrize(
    ("mark_decorator", "mark_name"),
    [
        (pytest.mark.skipif(True, reason="synthetic skipif"), "skipif"),
        (pytest.mark.skip(reason="synthetic skip"), "skip"),
    ],
)
def test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks(
    mark_decorator: pytest.MarkDecorator,
    mark_name: str,
) -> None:
    def fake_parity_test() -> None:
        return None

    fake_parity_test.pytestmark = [mark_decorator.mark]  # type: ignore[attr-defined]

    assert has_blocking_readiness_parity_skip_mark(fake_parity_test), mark_name
```

- [ ] **Step 3: Run the new test and verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks -q
```

Expected after adding only the test: the test fails with `NameError` because
`has_blocking_readiness_parity_skip_mark` does not exist yet.

- [ ] **Step 4: Add the helper and update the existing meta test**

Add this helper near the external-tool parity tests, before
`test_external_tool_readiness_payload_parity_is_not_conditionally_skipped`:

```python
BLOCKING_READINESS_PARITY_SKIP_MARKS = frozenset({"skipif", "skip"})


def has_blocking_readiness_parity_skip_mark(test_func: Callable[..., object]) -> bool:
    marks = getattr(test_func, "pytestmark", [])
    return any(mark.name in BLOCKING_READINESS_PARITY_SKIP_MARKS for mark in marks)
```

Replace the body of
`test_external_tool_readiness_payload_parity_is_not_conditionally_skipped` with:

```python
def test_external_tool_readiness_payload_parity_is_not_conditionally_skipped() -> None:
    assert not has_blocking_readiness_parity_skip_mark(
        test_external_tool_readiness_payload_matches_real_rednote_readiness
    )
```

- [ ] **Step 5: Run the helper test and existing meta test**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_skip_guard_rejects_skip_marks \
  tests/test_first_run_smoke.py::test_external_tool_readiness_payload_parity_is_not_conditionally_skipped -q
```

Expected: both tests pass.

## Task 2: Focused Verification And Code Review

**Files:**

- Modify: `tests/test_first_run_smoke.py`
- Add: `docs/reviews/opencode-stage-186-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-186-code-review.md`

- [ ] **Step 1: Run focused first-run smoke checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "readiness_payload_parity or skip_guard"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-186-code-review-prompt.md` requiring the
response body to start with:

```text
# Stage 186 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-186-code-review-prompt.md)" > "$tmp_review" 2>&1
awk 'BEGIN{copy=0} /^# Stage 186 Code Review/{copy=1} copy{print}' "$tmp_review" > docs/reviews/opencode-stage-186-code-review.md
if [ ! -s docs/reviews/opencode-stage-186-code-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-186-code-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no Critical or Important findings. Clean
the artifact if opencode includes process chatter, ANSI output, command logs,
code fences, or duplicated drafts.

## Task 3: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-186-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-186-release-review.md`

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

Create `docs/reviews/opencode-stage-186-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 186 Release Review
```

Run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-186-release-review.md`.

Expected: completed review output with no Critical or Important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_first_run_smoke.py \
  docs/superpowers/specs/2026-06-24-stage-186-readiness-skip-mark-guard-design.md \
  docs/superpowers/plans/2026-06-24-stage-186-readiness-skip-mark-guard-plan.md \
  docs/reviews/opencode-stage-186-plan-review-prompt.md \
  docs/reviews/opencode-stage-186-plan-review.md \
  docs/reviews/opencode-stage-186-code-review-prompt.md \
  docs/reviews/opencode-stage-186-code-review.md \
  docs/reviews/opencode-stage-186-release-review-prompt.md \
  docs/reviews/opencode-stage-186-release-review.md
git commit -m "test: guard readiness parity skip marks"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 broadens the readiness parity skip mark guard, Task 2
  covers focused verification and code review, and Task 3 covers release gate,
  release review, commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: runtime source, smoke script behavior, payloads, command
  order, adapter metadata, readiness boundaries, dependencies, source
  acquisition, ranking, monitoring, scraping, and compliance-review product
  behavior remain out of scope.
