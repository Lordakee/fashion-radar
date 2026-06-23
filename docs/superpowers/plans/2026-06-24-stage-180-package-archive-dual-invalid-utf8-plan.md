# Stage 180 Package Archive Dual Invalid UTF-8 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a focused regression test proving the package archive checker aggregates invalid UTF-8 errors from both wheel `METADATA` and `entry_points.txt`.

**Architecture:** Test-only hardening. Reuse the existing wheel/sdist fixture helpers in `tests/test_package_archives.py`, add one combined invalid-UTF-8 case beside the existing single-member cases, and leave `scripts/check_package_archives.py` untouched unless the test exposes a real aggregation defect.

**Tech Stack:** Python, pytest, zipfile-backed test fixtures, existing package archive checker script, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_package_archives.py`
  - Add `test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback`.
- Add: `docs/superpowers/specs/2026-06-24-stage-180-package-archive-dual-invalid-utf8-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-180-package-archive-dual-invalid-utf8-plan.md`
- Add: `docs/reviews/opencode-stage-180-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-180-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-180-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-180-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-180-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-180-release-review.md`

## Task 1: Add Dual Invalid UTF-8 Wheel Guard

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Confirm the dual invalid UTF-8 guard does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_package_archives.py::test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Add the dual invalid UTF-8 aggregation test**

Immediately after
`test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback`, add:

```python
def test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA": b"\xff\xfe\xfa",
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": b"\xff\xfe\xfa",
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    stderr_lines = result.stderr.splitlines()
    assert "METADATA is not valid UTF-8" in stderr_lines
    assert "entry_points.txt is not valid UTF-8" in stderr_lines
    assert "Traceback" not in result.stderr
    assert "UnicodeDecodeError" not in result.stderr
```

- [ ] **Step 3: Run the new dual invalid UTF-8 test**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_package_archives.py::test_rejects_wheel_metadata_and_entry_points_with_invalid_utf8_without_traceback -q
```

Expected: the test passes. If it fails because one stable error is missing,
inspect `scripts/check_package_archives.py::validate_wheel` and only change the
checker if the missing message is a real aggregation defect.

## Task 2: Focused Verification And Code Review

**Files:**

- Modify: `tests/test_package_archives.py`
- Add: `docs/reviews/opencode-stage-180-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-180-code-review.md`

- [ ] **Step 1: Run focused package archive checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check tests/test_package_archives.py
uv --no-config run --frozen ruff format --check tests/test_package_archives.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-180-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 180 implementation. The prompt
must require the response to start with:

```text
# Stage 180 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-180-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-180-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact so it contains only one final review body if opencode includes
process chatter, ANSI output, command logs, or multiple drafts.

## Task 3: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-180-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-180-release-review.md`

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

Create `docs/reviews/opencode-stage-180-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 180 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-180-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_package_archives.py \
  docs/superpowers/specs/2026-06-24-stage-180-package-archive-dual-invalid-utf8-design.md \
  docs/superpowers/plans/2026-06-24-stage-180-package-archive-dual-invalid-utf8-plan.md \
  docs/reviews/opencode-stage-180-plan-review-prompt.md \
  docs/reviews/opencode-stage-180-plan-review.md \
  docs/reviews/opencode-stage-180-code-review-prompt.md \
  docs/reviews/opencode-stage-180-code-review.md \
  docs/reviews/opencode-stage-180-release-review-prompt.md \
  docs/reviews/opencode-stage-180-release-review.md
git commit -m "test: cover package archive dual utf8 errors"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the dual invalid UTF-8 aggregation guard, Task 2
  covers focused verification and code review, and Task 3 covers release gate,
  release review, commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: package archive checker runtime behavior, archive metadata
  expectations, sdist behavior, dependencies, lockfiles, source acquisition,
  ranking, coverage verification features, and compliance-review product
  features remain out of scope unless the new test exposes a real aggregation
  defect.
