# Stage 183 Package Archive Entry Point Case Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a focused regression test proving package archive validation treats wheel console-script names as case-sensitive.

**Architecture:** Test-only hardening. Reuse the existing wheel/sdist fixture helpers in `tests/test_package_archives.py`, add one case-mismatched `entry_points.txt` test beside the existing console-script tests, and leave `scripts/check_package_archives.py` untouched unless the test exposes a real defect.

**Tech Stack:** Python, pytest, zipfile-backed wheel fixtures, existing package archive checker script, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_package_archives.py`
  - Add `test_rejects_wheel_entry_points_console_script_name_case_mismatch`.
- Add: `docs/superpowers/specs/2026-06-24-stage-183-package-archive-entry-point-case-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-183-package-archive-entry-point-case-plan.md`
- Add: `docs/reviews/opencode-stage-183-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-183-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-183-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-183-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-183-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-183-release-review.md`

## Task 1: Add Console-Script Name Case Guard

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Confirm the new guard does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_package_archives.py::test_rejects_wheel_entry_points_console_script_name_case_mismatch -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Add the case-mismatch test**

Add this test immediately after
`test_rejects_wheel_entry_points_console_script_wrong_target`:

```python
def test_rejects_wheel_entry_points_console_script_name_case_mismatch(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": (
            "[console_scripts]\nFashion-Radar = fashion_radar.cli:app\n"
        )
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        "entry_points.txt is missing console_scripts entry: "
        "fashion-radar = fashion_radar.cli:app"
    ) in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 3: Run the new test**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_package_archives.py::test_rejects_wheel_entry_points_console_script_name_case_mismatch -q
```

Expected: the test passes. If it fails because the checker accepts
`Fashion-Radar`, inspect `scripts/check_package_archives.py::validate_wheel_entry_points`
and only change runtime code if the missing rejection is a real case-sensitivity
defect.

## Task 2: Focused Verification And Code Review

**Files:**

- Modify: `tests/test_package_archives.py`
- Add: `docs/reviews/opencode-stage-183-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-183-code-review.md`

- [ ] **Step 1: Run focused package archive checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check tests/test_package_archives.py
uv --no-config run --frozen ruff format --check tests/test_package_archives.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-183-code-review-prompt.md` requiring the
response to start with:

```text
# Stage 183 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-183-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
awk 'BEGIN{copy=0} /^# Stage 183 Code Review/{copy=1} copy{print}' "$tmp_review" > docs/reviews/opencode-stage-183-code-review.md
if [ ! -s docs/reviews/opencode-stage-183-code-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-183-code-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact if opencode includes process chatter, ANSI output, command logs,
code fences, or multiple drafts.

## Task 3: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-183-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-183-release-review.md`

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

Create `docs/reviews/opencode-stage-183-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 183 Release Review
```

Run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-183-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_package_archives.py \
  docs/superpowers/specs/2026-06-24-stage-183-package-archive-entry-point-case-design.md \
  docs/superpowers/plans/2026-06-24-stage-183-package-archive-entry-point-case-plan.md \
  docs/reviews/opencode-stage-183-plan-review-prompt.md \
  docs/reviews/opencode-stage-183-plan-review.md \
  docs/reviews/opencode-stage-183-code-review-prompt.md \
  docs/reviews/opencode-stage-183-code-review.md \
  docs/reviews/opencode-stage-183-release-review-prompt.md \
  docs/reviews/opencode-stage-183-release-review.md
git commit -m "test: guard console script name case"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the case-sensitivity guard, Task 2 covers focused
  verification and code review, and Task 3 covers release gate, release review,
  commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: package archive runtime behavior, metadata expectations,
  dependency files, lockfiles, source acquisition, ranking, coverage
  verification, and compliance-review product behavior remain out of scope
  unless the new test exposes a real checker defect.
