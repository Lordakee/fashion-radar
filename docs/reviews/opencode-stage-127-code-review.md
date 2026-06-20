# Stage 127 Code Review

I reviewed the Stage 127 implementation against the revised design, plan, and both rereviews, and independently re-ran the focused tests, full file tests, ruff check/format, package build smoke, and `git diff --check`.

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **`.gitignore` allowance is by name with no type guard.** A direct child *directory* named exactly `.gitignore` would also be allowed (`scripts/check_package_archives.py:186`). uv 0.11.7 writes a 1-byte file, and the build dir is a fresh `mktemp -d`, so this is theoretical only. The design explicitly accepts name-based matching (`design.md:99-101`), so this is consistent with intent. Non-blocking.

2. **Carried-forward minor gaps, acknowledged in prior reviews.** No symlink direct-child test (plan-review Minor 3) and the test writes `*\n` while the real marker is 1-byte `*` (rereview Minor 3). Both are moot under by-name matching, and the live `uv build` smoke confirms real-world correctness. Non-blocking.

3. **Design verification line drift.** `design.md:108` now uses the corrected `-k "... or gitignore"` filter, so rereview-2 Minor 1 is already resolved in the current tree. No action needed; noted for traceability.

## Focus-area verification

1. **Matches revised design and plan?** Yes. `ALLOWED_BUILD_DIR_DIRECT_CHILD_NAMES` (`scripts/check_package_archives.py:130`), `unexpected_build_dir_child_errors` (`:179-188`), and the `validate_build_dir` integration (`:172-176`) match plan Task 2 Steps 1-3 verbatim. Direct-child errors are returned before archive-internal errors per design Architecture bullet 4.

2. **Rejects extra files/directories while accepting wheel+sdist+`.gitignore`?** Yes. Five new tests cover acceptance, direct file, direct directory, aggregated ordering, and the combined case (58/58 pass). The real `uv build` smoke produced wheel+sdist+`.gitignore` and the checker returned exit 0.

3. **`.gitignore` allowance does not hide other children?** Yes. `test_allowed_gitignore_marker_does_not_hide_unexpected_direct_child` asserts `.gitignore` is absent from stderr while `build.log` is present; the `and path.name not in ALLOWED_BUILD_DIR_DIRECT_CHILD_NAMES` clause is name-scoped to exactly `.gitignore`.

4. **Preserves existing missing/duplicate and archive-internal behavior?** Yes. `select_single_archive` still runs first with its early-return (`scripts/check_package_archives.py:165-167`), so missing/duplicate messages fire unchanged. `validate_wheel`/`validate_sdist` are untouched. Existing `test_rejects_build_directory_without_wheel/sdist` and all archive-internal tests still pass. Path equality between `glob()` and `iterdir()` confirmed (equal `PosixPath` objects, equal hashes), so `expected_paths` membership is reliable without `resolve()`.

5. **Scope clean of prohibited categories?** Yes. Only `scripts/check_package_archives.py` (release-time guardrail), its tests, and review/design/plan artifacts. No runtime product code, dependencies, `uv.lock` changes, connectors, scraping, browser automation, platform APIs, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit product behavior.

## Verification reproduced locally
- Focused tests: `7 passed, 51 deselected`
- Full file: `58 passed`
- `ruff check`: `All checks passed!`
- `ruff format --check`: `2 files already formatted`
- `uv build` + checker on temp dir: `Package archives contain required files.` exit 0
- `git diff --check`: clean

## Final statement
**There are no Critical or Important blockers before release.** The implementation may proceed to the full release gate and commit.
