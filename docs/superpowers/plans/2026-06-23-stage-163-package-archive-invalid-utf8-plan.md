# Stage 163 Package Archive Invalid UTF-8 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the package archive checker return deterministic checker errors, not tracebacks, when wheel `METADATA` or `entry_points.txt` is not valid UTF-8.

**Architecture:** Keep strict UTF-8 decoding in the existing `read_zip_text(...)` helper. Catch `UnicodeDecodeError` only in the two validators that know the user-facing member labels, returning stable errors for `METADATA` and `entry_points.txt`.

**Tech Stack:** Python standard library, pytest, existing package archive fixture helpers, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_package_archives.py`
  - Broaden the test helper `write_wheel(...)` so fixture values can be `str | bytes`.
  - Add RED test for invalid UTF-8 wheel `METADATA`.
  - Add RED test for invalid UTF-8 wheel `entry_points.txt`.
- Modify: `scripts/check_package_archives.py`
  - Catch `UnicodeDecodeError` in `validate_wheel_metadata(...)`.
  - Catch `UnicodeDecodeError` in `validate_wheel_entry_points(...)`.
- Add: `docs/reviews/opencode-stage-163-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-163-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-163-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-163-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-163-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-163-release-review.md`

## Task 1: Add RED Tests For Invalid UTF-8 Wheel Text Members

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Broaden the `write_wheel(...)` fixture helper type**

Change:

```python
def write_wheel(
    build_dir: Path,
    *,
    files: dict[str, str] | None = None,
    filename: str = EXPECTED_WHEEL_ARCHIVE_NAME,
) -> Path:
```

to:

```python
def write_wheel(
    build_dir: Path,
    *,
    files: dict[str, str | bytes] | None = None,
    filename: str = EXPECTED_WHEEL_ARCHIVE_NAME,
) -> Path:
```

Do not change the function body. `zipfile.ZipFile.writestr(...)` accepts both
`str` and `bytes`, and existing string fixtures continue to work unchanged.

- [ ] **Step 2: Add invalid UTF-8 `METADATA` test**

Add after `test_rejects_wheel_metadata_without_project_version(...)`:

```python
def test_rejects_wheel_metadata_with_invalid_utf8_without_traceback(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA": b"\xff\xfe\xfa"
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "METADATA is not valid UTF-8" in result.stderr
    assert "Traceback" not in result.stderr
    assert "UnicodeDecodeError" not in result.stderr
```

Expected before implementation: the subprocess exits nonzero with a Python
traceback containing `UnicodeDecodeError`, so the stable error assertion fails.

- [ ] **Step 3: Add invalid UTF-8 `entry_points.txt` test**

Add after `test_rejects_wheel_entry_points_malformed_without_traceback(...)`:

```python
def test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback(
    tmp_path: Path,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    wheel_files = WHEEL_FILES | {
        f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": b"\xff\xfe\xfa"
    }
    write_wheel(build_dir, files=wheel_files)
    write_sdist(build_dir)

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert "entry_points.txt is not valid UTF-8" in result.stderr
    assert "Traceback" not in result.stderr
    assert "UnicodeDecodeError" not in result.stderr
```

Expected before implementation: the subprocess exits nonzero with a Python
traceback containing `UnicodeDecodeError`, so the stable error assertion fails.

- [ ] **Step 4: Run focused RED tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_package_archives.py::test_rejects_wheel_metadata_with_invalid_utf8_without_traceback \
  tests/test_package_archives.py::test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback \
  -q
```

Expected before implementation: both tests fail because stderr contains a
traceback and does not contain the new stable checker messages.

## Task 2: Return Stable Checker Errors For Invalid UTF-8

**Files:**

- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Catch invalid UTF-8 in `validate_wheel_metadata(...)`**

Change:

```python
def validate_wheel_metadata(
    archive: zipfile.ZipFile,
    dist_info_dir: str,
    expected_metadata: ExpectedProjectMetadata,
) -> list[str]:
    metadata_path = f"{dist_info_dir}/METADATA"
    metadata = read_zip_text(archive, metadata_path)
    parsed_metadata = Parser().parsestr(metadata)
```

to:

```python
def validate_wheel_metadata(
    archive: zipfile.ZipFile,
    dist_info_dir: str,
    expected_metadata: ExpectedProjectMetadata,
) -> list[str]:
    metadata_path = f"{dist_info_dir}/METADATA"
    try:
        metadata = read_zip_text(archive, metadata_path)
    except UnicodeDecodeError:
        return ["METADATA is not valid UTF-8"]
    parsed_metadata = Parser().parsestr(metadata)
```

- [ ] **Step 2: Catch invalid UTF-8 in `validate_wheel_entry_points(...)`**

Change:

```python
def validate_wheel_entry_points(
    archive: zipfile.ZipFile,
    dist_info_dir: str,
    expected_metadata: ExpectedProjectMetadata,
) -> list[str]:
    entry_points_path = f"{dist_info_dir}/entry_points.txt"
    entry_points = read_zip_text(archive, entry_points_path)
    parser = configparser.ConfigParser(interpolation=None)
```

to:

```python
def validate_wheel_entry_points(
    archive: zipfile.ZipFile,
    dist_info_dir: str,
    expected_metadata: ExpectedProjectMetadata,
) -> list[str]:
    entry_points_path = f"{dist_info_dir}/entry_points.txt"
    try:
        entry_points = read_zip_text(archive, entry_points_path)
    except UnicodeDecodeError:
        return ["entry_points.txt is not valid UTF-8"]
    parser = configparser.ConfigParser(interpolation=None)
```

Do not catch `Exception`, `ValueError`, or `configparser.Error` here. Keep the
existing `configparser.Error` catch around `parser.read_string(...)`.

- [ ] **Step 3: Run focused GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_package_archives.py::test_rejects_wheel_metadata_with_invalid_utf8_without_traceback \
  tests/test_package_archives.py::test_rejects_wheel_entry_points_with_invalid_utf8_without_traceback \
  -q
```

Expected after implementation: both tests pass.

- [ ] **Step 4: Run broader package archive checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "invalid_utf8 or metadata or entry_points"
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
```

Expected after implementation:

- The selected invalid-UTF8/metadata/entry-points subset passes.
- The full package archive test module passes.
- Ruff check and format check pass.

## Task 3: Build Smoke, Code Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-163-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-163-code-review.md`
- Add: `docs/reviews/opencode-stage-163-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-163-release-review.md`

- [ ] **Step 1: Run package archive smoke against a real build**

Run:

```bash
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
rm -rf "$tmp_build"
```

Expected: archive checker prints `Package archives contain required files.`

- [ ] **Step 2: Create and run code review**

Create `docs/reviews/opencode-stage-163-code-review-prompt.md` summarizing:

- Objective.
- Changed files.
- RED failure evidence.
- GREEN verification evidence.
- Scope boundaries.
- Review questions about deterministic errors, no traceback behavior, and
  whether the fix is too broad.

Run:

```bash
raw_review="$(mktemp)"
clean_review="$(mktemp)"
opencode run --format json --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-163-code-review-prompt.md)" > "$raw_review"
jq -r 'select(.type == "text") | .part.text' "$raw_review" \
  | sed -n '/^# Stage 163 Code Review$/,$p' > "$clean_review"
cp "$clean_review" docs/reviews/opencode-stage-163-code-review.md
rm -f "$raw_review" "$clean_review"
```

Fix any critical or important findings before continuing.

- [ ] **Step 3: Run full release gate**

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

Expected: all checks pass; token scan and extraheader commands produce no
configured secret/header output.

- [ ] **Step 4: Create and run release review**

Create `docs/reviews/opencode-stage-163-release-review-prompt.md` summarizing:

- Objective.
- Changed files.
- RED/GREEN/code-review evidence.
- Full release gate evidence.
- Scope boundaries.

Run:

```bash
raw_review="$(mktemp)"
clean_review="$(mktemp)"
opencode run --format json --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-163-release-review-prompt.md)" > "$raw_review"
jq -r 'select(.type == "text") | .part.text' "$raw_review" \
  | sed -n '/^# Stage 163 Release Review$/,$p' > "$clean_review"
cp "$clean_review" docs/reviews/opencode-stage-163-release-review.md
rm -f "$raw_review" "$clean_review"
```

Fix any critical or important findings before continuing.

- [ ] **Step 5: Run final hygiene checks**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: release hygiene and diff checks pass; token scan and extraheader
commands produce no configured secret/header output.

- [ ] **Step 6: Commit and push**

Run:

```bash
git add scripts/check_package_archives.py tests/test_package_archives.py \
  docs/superpowers/specs/2026-06-23-stage-163-package-archive-invalid-utf8-design.md \
  docs/superpowers/plans/2026-06-23-stage-163-package-archive-invalid-utf8-plan.md \
  docs/reviews/opencode-stage-163-plan-review-prompt.md \
  docs/reviews/opencode-stage-163-plan-review.md \
  docs/reviews/opencode-stage-163-code-review-prompt.md \
  docs/reviews/opencode-stage-163-code-review.md \
  docs/reviews/opencode-stage-163-release-review-prompt.md \
  docs/reviews/opencode-stage-163-release-review.md
git commit -m "fix: report invalid wheel text-member UTF-8"
auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 | tr -d '\n') && \
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic $auth" push origin main
```

- [ ] **Step 7: Run post-push checks**

Run:

```bash
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git config --get-all http.https://github.com/.extraheader
```

Expected:

- Local `main` and `origin/main` point at the same commit.
- Worktree is clean.
- No persistent GitHub extraheader is configured.
