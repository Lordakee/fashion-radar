# Stage 134 Code Review

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **Plan-review ordering note was honored.** The plan-review's Minor #1
   suggested defining helpers in dependency order
   (`normalize_distribution_name` → `expected_wheel_dist_info_dir` →
   `validate_wheel_dist_info_dir`). The implementation at
   `scripts/check_package_archives.py:283-302` follows exactly that order,
   matching the file's prevailing style.

2. **`wheel_files_with_dist_info_dir` relies on prefix-stripping assumption.**
   `tests/test_package_archives.py:486` uses `path.split('/', 1)[1]` for any
   path starting with `fashion_radar-0.1.0.dist-info/`. This is safe given
   `WHEEL_FILES` always pairs the prefix with a filename, but it would
   `IndexError` on a hypothetical prefix-only key. Not worth changing.

## Review focus answers

1. **Design/plan match — yes.** Helpers, validator, error message text
   (`"wheel archive dist-info directory mismatch: expected ... found ..."`),
   and insertion point inside `if dist_info_dir is not None:` at
   `scripts/check_package_archives.py:253-254` match the design (lines 60-73)
   and plan (Task 2 Step 1-2) verbatim. Verified expected message strings at
   `tests/test_package_archives.py:513-516` against
   `scripts/check_package_archives.py:299-302`.

2. **RED test proves METADATA alone is insufficient — yes.**
   `wheel_files_with_dist_info_dir()` rewrites only the `.dist-info/` prefix
   on every key, so `METADATA` content stays `Name: fashion-radar` /
   `Version: 0.1.0` (from `WHEEL_FILES` line 29-31). Both parametrized cases
   (`wrong_name-0.1.0.dist-info`, `fashion_radar-9.9.9.dist-info`) isolate
   name-only and version-only directory mismatches. Tracing the pre-change
   checker: with valid METADATA it returned 0 errors, so the test was
   genuinely RED. After the fix, both cases pass (verified:
   `2 passed in 0.16s`).

3. **Normalization is dependency-free and correct — yes.**
   `re.sub(r"[-_.]+", "_", name).lower()` at line 284 maps `fashion-radar` →
   `fashion_radar`, producing expected dir `fashion_radar-0.1.0.dist-info`.
   Only uses `re`, already imported at line 5. No new dependencies. Live
   `uv build` confirmed the real wheel directory is
   `fashion_radar-0.1.0.dist-info/` and the checker accepted it (exit 0).

4. **Mismatch check runs only after exact-one selection — yes.** The
   `errors.extend(validate_wheel_dist_info_dir(...))` call at line 254 sits
   inside `if dist_info_dir is not None:` (line 253), which only triggers
   when `select_wheel_dist_info_dir()` returns a single top-level directory.
   `test_rejects_nested_wheel_dist_info_directory`,
   `test_rejects_multiple_wheel_dist_info_directories`, and
   `test_rejects_split_wheel_dist_info_files` (lines 426, 444, 461) all
   still assert the broader "exactly one top-level .dist-info directory"
   error and pass. Full module: `66 passed in 4.03s`.

5. **Scope boundaries honored — yes.** `git diff --name-only` shows only
   `scripts/check_package_archives.py` and `tests/test_package_archives.py`.
   No `pyproject.toml`, `uv.lock`, or `.github/` changes. No package
   filename validation, sdist root validation, license/member validation
   changes, dependency additions, CI changes, or runtime product behavior
   changes. No connectors, scraping, browser automation, platform APIs,
   monitoring, scheduling, source acquisition, demand proof, ranking,
   coverage verification, or compliance/audit product behavior. Confirmed
   against `AGENTS.md` scope boundaries and the design Out-of-scope list
   (lines 43-54). `ruff check` + `ruff format --check` clean on both files;
   `git diff --check` clean.

## Verification re-run

- `pytest tests/test_package_archives.py::test_rejects_wheel_with_mismatched_dist_info_directory` → `2 passed`
- `pytest tests/test_package_archives.py tests/test_package_metadata.py -q` → `66 passed`
- `ruff check` + `ruff format --check` → clean
- Live `uv build` + checker → exit 0
- `git diff --check` → clean

## Final statement

There are **no Critical or Important blockers** before release.
