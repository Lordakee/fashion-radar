# Stage 134 Plan Review

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **Helper definition order is callee-before-caller.** Task 2 Step 1 defines
   `validate_wheel_dist_info_dir()` first, then `expected_wheel_dist_info_dir()`
   and `normalize_distribution_name()` below it. Python resolves names at call
   time so this runs correctly, but the rest of `scripts/check_package_archives.py`
   tends to define helpers before their callers (e.g. `select_wheel_dist_info_dir`
   precedes `validate_wheel_dist_info_files`). Reordering to
   `normalize_distribution_name` → `expected_wheel_dist_info_dir` →
   `validate_wheel_dist_info_dir` would match the file's prevailing style. Not
   blocking.

2. **Plan-review artifact creation is implicit.** The Files list and the
   Task 4 commit stage `docs/reviews/opencode-stage-134-plan-review-prompt.md`
   and `docs/reviews/opencode-stage-134-plan-review.md`, but no task step
   creates them. This is consistent with prior stages (the same point was
   noted in the Stage 133 plan review) and matches `docs/REVIEW_PROTOCOL.md`
   handing plan-review creation to the surrounding review workflow. Noted for
   traceability only.

3. **Token scan covers only classic PATs.** The release-gate check
   `rg -n 'ghp_[A-Za-z0-9]+' .` does not cover fine-grained `github_pat_`
   tokens. This is the established project-wide pattern, not a Stage 134
   regression.

## Scope and design checks

1. **Parity gap addressed without filename validation.** Stage 130's design
   (line 40) explicitly left "package filename, dist-info path" validation out
   of scope. Stage 134 closes exactly the `.dist-info` directory-name parity
   gap and the design's Out-of-scope list (lines 43-54) re-affirms no package
   filename validation, no sdist root validation, and no product behavior
   changes. Confirmed against `AGENTS.md` scope boundaries.

2. **RED test specificity is sufficient.** The parametrized cases
   (`wrong_name-0.1.0.dist-info`, `fashion_radar-9.9.9.dist-info`) both
   preserve valid `METADATA` (`Name: fashion-radar`, `Version: 0.1.0`) via the
   `wheel_files_with_dist_info_dir()` helper, which rewrites only the
   directory prefix. This isolates name-only and version-only directory
   mismatches, proving valid `METADATA` alone is insufficient. The assertion
   on the exact mismatch string plus `"Traceback" not in result.stderr`
   anchors behavior precisely. I traced the current checker: with either
   fixture it returns zero errors today, so the test is genuinely RED.

3. **Normalization is appropriate and dependency-free.**
   `re.sub(r"[-_.]+", "_", name).lower()` maps `fashion-radar` →
   `fashion_radar`, matching the wheel binary distribution convention for
   `.dist-info` directory naming (PEP 491 escaped name). It uses only `re`,
   which is already imported at `scripts/check_package_archives.py:5`. No
   new dependencies. Version is compared as-is (no normalization), which is
   correct for the current `0.1.0` project version and the stated release
   hygiene scope.

4. **Layout behavior preserved.** Task 2 Step 2 inserts
   `validate_wheel_dist_info_dir()` inside the existing
   `if dist_info_dir is not None:` block, after `select_wheel_dist_info_dir()`
   returns a single top-level directory. Nested, multiple, and split
   `.dist-info` layouts continue to return `None` from the selector and emit
   the existing broader "exactly one top-level .dist-info directory" error
   (covered by `test_rejects_nested_wheel_dist_info_directory`,
   `test_rejects_multiple_wheel_dist_info_directories`,
   `test_rejects_split_wheel_dist_info_files`). File/metadata/entry-point
   checks remain conditional on file presence, so a mismatched directory
   still reports all relevant errors without traceback.

5. **Scope boundaries honored.** No package filename validation, sdist root
   validation, license-path changes, member validation changes,
   forbidden-member changes, dependency additions, `pyproject.toml` changes,
   `uv.lock` changes, CI changes, or runtime product behavior changes. No
   connectors, scraping, browser automation, platform APIs, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, or compliance/audit product behavior. Confirmed against the
   design Out-of-scope list and the plan's Files/boundary statement.

6. **Verification commands are sufficient.** Focused verification covers the
   new dist-info tests (`-k "dist_info"`), both affected test modules, ruff
   check + format on the two changed files, a live `uv build` archive check
   against the real wheel (which carries `fashion_radar-0.1.0.dist-info/` and
   must still pass), and `git diff --check`. The release gate adds the full
   suite, full lint/format, `UV_NO_CONFIG=1 uv lock --check`, `uv.lock` diff,
   whitespace check, and the token/auth-header scans. This is consistent with
   Stage 130-era verification rigor.

## Final statement

There are **no Critical or Important blockers** before implementation. The
plan may proceed.
