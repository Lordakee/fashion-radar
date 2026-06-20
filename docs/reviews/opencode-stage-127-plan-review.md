I'll review the Stage 127 design and plan. Let me start by reading the relevant files.
Let me read the existing test file to verify the test helpers referenced in the plan.
I've reviewed the design, plan, current checker (`scripts/check_package_archives.py:157-170`), and the existing test conventions. Here are my findings.

## Review Findings

### Critical findings
None.

### Important findings
None.

### Minor findings

1. **Plan-review artifacts have no creation task.** The plan's Files section (lines 21-24) lists `docs/reviews/opencode-stage-127-plan-review-prompt.md` and `docs/reviews/opencode-stage-127-plan-review.md`, and Task 4 Step 2 `git add`s them (line 290), but no task step creates either file. A worker following the plan literally will reach the commit with two uncreated paths and the `git add` will fail. Consider adding a Task 0 (or a note) stating these are produced by the pre-stage review gate per `docs/REVIEW_PROTOCOL.md:6-23`, before Task 1 begins.

2. **RED-run description is slightly imprecise.** The `-k "unexpected_direct or build_directory"` filter (plan line 106) also matches the existing `test_rejects_build_directory_without_wheel` and `test_rejects_build_directory_without_sdist`. This is beneficial (regression coverage during RED→GREEN), but Task 1 Step 4's "Expected result: the new direct-child tests fail" (line 109) should note the two existing tests still pass at RED. Not blocking.

3. **No symlink direct-child test.** The design's Risks section (`docs/superpowers/specs/...design.md:80-81`) explicitly calls out avoiding `resolve()` so the helper does not follow symlinks. The helper's by-name comparison inherently satisfies this, but a single test asserting a symlinked direct child is rejected by name (not followed) would lock in that guarantee. Optional.

### Focus-area verification

1. **Design addresses the help-text gap without changing archive-internal validation?** Yes. `validate_build_dir` currently globs only `*.whl`/`*.tar.gz` and ignores everything else; the help text (`scripts/check_package_archives.py:138`) promises "exactly one wheel and one sdist archive." The new direct-child scan closes that gap, and `validate_wheel`/`validate_sdist` are untouched.
2. **RED tests specific enough?** Yes. They cover a direct file (`build.log`), a direct directory (`metadata/`), and aggregated reporting with deterministic ordering (`build.log` before `metadata`, asserted via `index` comparison).
3. **Existing missing/duplicate errors preserved?** Yes. `select_single_archive()` still runs first and the early-return-on-errors path (`scripts/check_package_archives.py:163-165`) fires before the new helper is reached. The helper is only appended to the final return after successful selection.
4. **Scope clean of all prohibited categories?** Yes. Only `scripts/check_package_archives.py`, its tests, and review artifacts. No runtime product code, dependencies, lockfile edits, connectors, scraping, platform APIs, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit behavior.
5. **Verification commands sufficient?** Yes. Focused tests, full tests, ruff check + format, package build smoke against a temp `dist/`, full release gate with `UV_NO_CONFIG=1 uv lock --check` and `git diff --exit-code -- uv.lock`, plus token and auth-header scans. Matches `AGENTS.md` mirror/lock discipline.

### Implementation correctness spot-checks
- Path equality for the `expected_paths` set works: `select_single_archive` returns `build_dir.glob(...)` results and `iterdir()` yields the same `build_dir / name` Path objects, so `path not in expected_paths` filters correctly without `resolve()`.
- Determinism: helper sorts by `item.name`; the aggregated test's `index("build.log") < index("metadata")` aligns with lexical order.
- Happy path preserved: existing `test_accepts_archives_with_required_files_and_metadata` still passes since the helper yields no errors when only the wheel and sdist are present.

### Final statement
**There are no Critical or Important blockers.** Implementation may proceed after addressing the minor plan-review artifact workflow gap (Minor 1) to avoid a failed `git add` at commit time.
