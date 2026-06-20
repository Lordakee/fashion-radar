# Stage 127 Build Directory Direct-Child Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the package archive checker reject any unexpected direct child in the build output directory beyond the selected wheel, selected sdist, and uv's generated `.gitignore` marker.

**Architecture:** Preserve existing wheel/sdist selection and archive-internal validation, then add a direct-child scan after successful archive selection. The scan is deterministic, direct-child-only, allows uv's direct `.gitignore` marker, and reports every extra file, directory, or symlink by name.

**Tech Stack:** Python 3.11, pytest, standard-library pathlib/tarfile/zipfile.

---

## Files

- Modify `tests/test_package_archives.py`
  - Add a RED test that accepts uv's `.gitignore` build-output marker.
  - Add a RED test proving `.gitignore` does not hide another unexpected direct
    child.
  - Add RED tests for unexpected direct files, directories, and aggregated
    direct children in the build output directory.
- Modify `scripts/check_package_archives.py`
  - Add `ALLOWED_BUILD_DIR_DIRECT_CHILD_NAMES`.
  - Add `unexpected_build_dir_child_errors`.
  - Call it from `validate_build_dir()` after wheel/sdist selection succeeds.
- Create `docs/reviews/opencode-stage-127-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-127-plan-review.md`.
- Create `docs/reviews/opencode-stage-127-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-127-code-review.md`.

The plan-review prompt and plan-review artifact are created by the required
pre-implementation opencode review gate before Task 1 starts.

No runtime product code, CLI behavior, dependencies, lockfile, connectors,
scraping, platform APIs, browser automation, scheduling, source acquisition,
demand proof, ranking, coverage verification, or compliance/audit product
behavior is part of this stage.

Implementation note: direct-child rejection tests and the initial helper were
added before the uv `.gitignore` smoke failure was discovered. Continue from the
current working tree by adding the marker-specific tests and amending the
existing helper; do not duplicate the existing rejection tests, helper, or
`validate_build_dir()` call.

## Task 1: Add RED build-directory direct-child tests

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add uv `.gitignore` marker acceptance test**

After `test_accepts_archives_with_required_files_and_metadata`, add:

```python
def test_accepts_uv_build_gitignore_marker(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / ".gitignore").write_text("*\n", encoding="utf-8")

    result = run_checker(build_dir)

    assert result.returncode == 0
    assert result.stdout == "Package archives contain required files.\n"
    assert result.stderr == ""
```

This test is RED once the direct-child helper exists but before it allows the
uv marker. It exists because `uv --no-config build --out-dir <tmp>` with uv
0.11.7 writes `.gitignore` containing `*`.

- [ ] **Step 2: Add unexpected direct file test**

If not already present, after the uv marker test, add:

```python
def test_rejects_build_directory_with_unexpected_direct_file(tmp_path: Path) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / "build.log").write_text("local build output\n", encoding="utf-8")

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "build directory contains unexpected direct child: build.log" in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 3: Add unexpected direct directory test**

If not already present, after the direct file test, add:

```python
def test_rejects_build_directory_with_unexpected_direct_directory(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / "metadata").mkdir()

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "build directory contains unexpected direct child: metadata" in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 4: Add aggregated direct-child reporting test**

If not already present, after the direct directory test, add:

```python
def test_reports_all_unexpected_build_directory_direct_children(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / "build.log").write_text("local build output\n", encoding="utf-8")
    (build_dir / "metadata").mkdir()

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "build directory contains unexpected direct child: build.log" in result.stderr
    assert "build directory contains unexpected direct child: metadata" in result.stderr
    assert result.stderr.index("build.log") < result.stderr.index("metadata")
    assert "Traceback" not in result.stderr
```

- [ ] **Step 5: Add combined allowed-marker plus unexpected-child test**

After the aggregated reporting test, add:

```python
def test_allowed_gitignore_marker_does_not_hide_unexpected_direct_child(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir)
    (build_dir / ".gitignore").write_text("*\n", encoding="utf-8")
    (build_dir / "build.log").write_text("local build output\n", encoding="utf-8")

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "build directory contains unexpected direct child: .gitignore" not in result.stderr
    assert "build directory contains unexpected direct child: build.log" in result.stderr
    assert "Traceback" not in result.stderr
```

- [ ] **Step 6: Run the RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -k "unexpected_direct or build_directory or gitignore" -q
```

Expected result: before the helper is added, the unexpected direct-child tests
fail because the checker ignores unrelated direct children. If the helper exists
but does not yet allow uv's `.gitignore`, the uv marker test fails.

## Task 2: Reject unexpected direct children in the checker while allowing uv's marker

**Files:**

- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Add allowed marker constant**

Near the release member constants, add:

```python
ALLOWED_BUILD_DIR_DIRECT_CHILD_NAMES = frozenset({".gitignore"})
```

- [ ] **Step 2: Amend or add direct-child helper**

If the helper is already present in the working tree, amend its `if` condition.
Otherwise, after `validate_build_dir`, add:

```python
def unexpected_build_dir_child_errors(
    build_dir: Path,
    *,
    expected_paths: set[Path],
) -> list[str]:
    errors: list[str] = []
    for path in sorted(build_dir.iterdir(), key=lambda item: item.name):
        if path not in expected_paths and path.name not in ALLOWED_BUILD_DIR_DIRECT_CHILD_NAMES:
            errors.append(f"build directory contains unexpected direct child: {path.name}")
    return errors
```

- [ ] **Step 3: Keep helper call after archive selection**

If the helper call is already present in the working tree, keep it. Otherwise,
in `validate_build_dir()`, replace:

```python
    return validate_wheel(wheel_path) + validate_sdist(sdist_path)
```

with:

```python
    build_dir_errors = unexpected_build_dir_child_errors(
        build_dir,
        expected_paths={wheel_path, sdist_path},
    )
    return build_dir_errors + validate_wheel(wheel_path) + validate_sdist(sdist_path)
```

This keeps existing missing and duplicate archive messages before direct-child
checks because `select_single_archive()` still runs first.

- [ ] **Step 4: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -k "unexpected_direct or build_directory or gitignore" -q
```

Expected result: all selected tests pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-127-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-127-code-review.md`

- [ ] **Step 1: Run focused tests, lint, and package smoke**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
git diff --check
```

Expected result: tests, lint, format, package smoke, and whitespace checks pass.

- [ ] **Step 2: Write Stage 127 code review prompt**

Create `docs/reviews/opencode-stage-127-code-review-prompt.md` with:

```markdown
Review the Stage 127 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Make `scripts/check_package_archives.py` reject unexpected direct children in
  the build output directory beyond the selected wheel, selected sdist, and
  uv's generated `.gitignore` marker.
- Preserve existing missing/duplicate wheel and sdist errors and
  archive-internal validation behavior.

Files changed:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 127 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 127 design and plan?
2. Does the checker reject extra direct files and directories while still
   accepting exactly one valid wheel, one valid sdist, and uv's `.gitignore`
   marker?
3. Does it preserve existing missing/duplicate archive selection messages?
4. Does the stage avoid runtime product behavior, dependencies, lockfile,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
```

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-127-code-review-prompt.md)" > "$tmp_review"
sed -n '1,240p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-127-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 127 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-127-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Full release gate, commit, push, and CI

**Files:**

- No new implementation files beyond Task 3.

- [ ] **Step 1: Run the full release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: release hygiene, full pytest, ruff, format, lock check,
lockfile diff, whitespace check, token scan, and git auth-header scan all pass.

- [ ] **Step 2: Commit Stage 127**

Run:

```bash
git status --short --untracked-files=all
git add scripts/check_package_archives.py tests/test_package_archives.py docs/superpowers/specs/2026-06-20-stage-127-build-dir-direct-child-hygiene-design.md docs/superpowers/plans/2026-06-20-stage-127-build-dir-direct-child-hygiene-plan.md docs/reviews/opencode-stage-127-plan-review-prompt.md docs/reviews/opencode-stage-127-plan-review.md docs/reviews/opencode-stage-127-code-review-prompt.md docs/reviews/opencode-stage-127-code-review.md
git commit -m "Reject unexpected build directory artifacts"
```

Expected result: one commit containing only Stage 127 checker/test/review
artifacts.

- [ ] **Step 3: Push with temporary auth header**

Run the established temporary-header push pattern without storing credentials in
git config or files:

```bash
AUTH_HEADER="$(printf 'x-access-token:%s' "$GITHUB_TOKEN_FOR_PUSH" | base64 -w0)"
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
unset AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub auth header remains.

- [ ] **Step 4: Verify remote and CI**

Run:

```bash
git ls-remote origin refs/heads/main
```

Then poll the latest GitHub Actions run for the pushed SHA until it reaches a
terminal state.

Expected result: remote `main` points at the Stage 127 commit and CI completes
successfully.
