## Findings

### Critical

None.

### Important

None.

### Minor

None.

## Verified Release Evidence

**Commit Scope and Hygiene**

Commit 3eabf38fc7b8508572daa8f48c0ed9745140acff contains exactly 28 changed paths as specified. No pyproject.toml, uv.lock, dependencies, schemas, credentials, generated artifacts, or unrelated work are present. The commit adds:
- Core publisher: `src/fashion_radar/row_one/publish.py` (2,534 lines)
- Publisher tests: `tests/test_row_one_publish.py` (5,602 lines, 194 test functions)
- Renderer integration: `src/fashion_radar/row_one/render.py:157-186,403-413`
- CLI integration: `src/fashion_radar/cli.py` (12-line diff adding `latest_only` help text)
- Package archive validators: `scripts/check_package_archives.py:33-34,tests/test_package_archives.py:36`
- First-run smoke: `scripts/check_first_run_smoke.py:3682,3898-3927`
- Boundary tests: 8 test files with 1,463 new assertions
- Documentation: CHANGELOG.md, README.md, docs/architecture.md, docs/cli-reference.md, docs/first-run.md, docs/row-one.md
- Plan/design/review records: 3 files under docs/reviews/ and 2 under docs/superpowers/

**Code Review Gate**

`docs/reviews/claude-code-stage-391-code-review.md:1-121` contains a coherent approved review with no Critical or Important findings. The review verifies AGENTS.md Codex runtime rule (lines 11-13), published recovery parametrization (lines 15-22), first-run debris validation (lines 24-31), capability detector (lines 33-43), mutation-free canonical journal boundary (lines 45-61), live owner binding (lines 63-78), live root metadata timing (lines 80-92), KeyboardInterrupt identity (lines 94-107), and Windows test skip strategy (lines 109-117). Verdict: APPROVED (line 121).

**Plan Review Gates**

`docs/reviews/claude-code-stage-391-plan-rereview.md:1-94` approved the mutation-free canonical journal preflight split, live owner binding contract, six-part capability detector, live root metadata timing, and published/no-backup matrix. `docs/reviews/opencode-stage-391-plan-rereview-2.md:1-30` applied the Important clarification and three Nits, then re-approved.

**Publisher Capability and Safety**

Lines `src/fashion_radar/row_one/publish.py:41-55` define a pure six-part capability detector covering four `os.supports_dir_fd` memberships plus `O_DIRECTORY` and `O_NOFOLLOW`. The module-level constant `_SAFE_DIRECTORY_OPERATIONS_SUPPORTED` is initialized once at line 55. The public gate at lines 122-126 reads only the constant and raises `RowOnePublishError` with the exact message `"ROW ONE safe directory handles are unsupported on this platform"` before any mutation. The gate is called at lines 2489, 810, 844, 865, and 901, covering all latest-only entry points. Non-latest rendering bypasses the gate entirely (verified by renderer integration at `src/fashion_radar/row_one/render.py:160-162`).

**Descriptor-Bound Operations and Lock/Journal/Owner Binding**

`src/fashion_radar/row_one/publish.py:127-245` implement descriptor-bound `_open_path_relative_to_directory_fd`, `_stat_nofollow_relative_to_directory_fd`, `_mkdir_relative_to_directory_fd`, and `_unlink_relative_to_directory_fd` using `os.open` with `O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`, then `os.open/os.stat/os.mkdir/os.unlink` with `dir_fd`. Live owner binding at lines 809-836 parses both `token` and `physical_output`, returning the token only after exact equality `if physical_output != directory` raises `RowOnePublishAmbiguousStateError`. All live owner consumers pass `transaction.target.physical_output` as the directory argument (lines 846, 888, 1920).

**Staging, Validation, Commit, Rollback, Recovery**

Stage creation: lines 1452-1481. Staged validation: line 2507 calls `_validate_staged_row_one_site`. Live metadata timing: line 2508 calls `_apply_live_root_metadata` after staged validation, before `ready` journal write. Commit phases: `staging` (line 1454), `ready` (line 2510), `live_moving` (line 1717), `live_backed_up` (line 1729), `published` (line 1744). Rollback: `_rollback_existing_publish` (lines 1754-1841). Recovery: `_recover_interrupted_publish` (lines 2117-2207) handles all five journal phases. Cleanup: `_cleanup_after_handled_failure` (lines 2400-2449) and `_finish_published_recovery` (lines 2019-2101) implement bounded cleanup contracts.

**Mutation-Free Canonical Journal Boundary**

`_read_canonical_journal` (lines 1043-1062) reads only the deterministic canonical journal without recovery side effects. `_load_journal` (line 1065-1067) is the sole recovery-capable entry calling `_recover_temporary_journals` before delegating. All cleanup and rollback preflight callers use `_read_canonical_journal` (lines 1787, 2288, 2331, 2366, 2381, 2392, 2414), never `_load_journal`.

**Ambiguity, Exception Identity, Renderer/CLI Integration**

Seven exception types are defined: `RowOnePublishError`, `RowOnePublishBusyError`, `RowOnePublishAmbiguousStateError`, `RowOnePublishRollbackError`, `RowOnePublishCleanupPendingError`, `RowOnePublishPreservedError`, `RowOnePublishRestoredError` (lines 57-84). KeyboardInterrupt preservation: lines 1702, 1719, 1839, 2521. Renderer integration: `render_row_one_site` at lines 157-181 routes `latest_only=True` through `publish_latest_row_one_site`. CLI integration: `src/fashion_radar/cli.py` adds `latest_only` option to `row-one build`, `row-one preview`, and makes `row-one refresh` latest-only (lines 15-25 of the diff).

**Package Archive Validators**

`scripts/check_package_archives.py:33-34` adds `"fashion_radar/row_one/publish.py"` to `WHEEL_REQUIRED_PATHS` and `"src/fashion_radar/row_one/publish.py"` to `SDIST_REQUIRED_PATHS`. `tests/test_package_archives.py:36` tests wheel membership.

**Public Documentation**

README.md:15-50 documents failure-safe recoverable publish, staging before live changes, stable lock, preserved unrelated children, unchanged paths/URLs, platform capability requirements, mutation-free failure on unsupported platforms, feature-level boundary, ordinary non-latest availability, short live-path gap, non-atomic publication, no power-loss durability claim, and Stage 391 non-goals. CHANGELOG.md:1-28 states the same. docs/architecture.md:48-72 repeats capability limits and boundaries. docs/row-one.md contains comprehensive publication section. docs/cli-reference.md and docs/first-run.md document commands and workflows.

**Test Coverage and Platform Skips**

194 test functions in `tests/test_row_one_publish.py`. Published/no-backup recovery matrix: lines 3644-3750 parametrize both valid and invalid cases over `had_live_output` (False, True) and `owner_present` (False, True), producing 4 test cases each (8 total). First-run debris validation: `scripts/check_first_run_smoke.py:3898-3927` denies canonical journal, stage, backup, temporary journals, and owner file while explicitly allowing the stable lock. Windows platform skip: capability-requiring tests use `_REQUIRES_SAFE_DIRECTORY_OPERATIONS` decorator at line 2091; FIFO/socket tests use explicit `hasattr` skip conditions.

**Validation Evidence**

User-supplied validation evidence states:
- Public UV/PIP config unset, UV_NO_CONFIG=1
- uv lock --check passed with fail-closed mirror scan
- uv sync --locked --dev and --check passed
- Full pytest: 3244 passed
- Full Ruff check and format check passed
- Release hygiene and git diff --check passed
- Source first-run smoke passed
- uv build produced exactly fashion_radar-0.1.0.tar.gz and fashion_radar-0.1.0-py3-none-any.whl
- scripts/check_package_archives.py passed
- Wheel installed into isolated Python 3.13 venv
- Installed fashion-radar and python -m fashion_radar help passed
- Installed row-one commands help passed
- Installed first-run build/preview/refresh/status/serve smoke passed
- Installed package resource lookup passed
- row-one install-local generated systemd units; systemd-analyze --user verify passed
- wheel[dashboard] installed; imports passed
- All temporary build/env/dashboard/unit directories trap-cleaned
- Final worktree clean guard passed
- uv.lock remained committed public SHA-256 09c2236c8fe3821b6982c1abe3f447ddcc4c6a3fd9392d1c054f4522a85947c9

## Questions And Assumptions

No open questions. The implementation satisfies all specified requirements with coherent design/plan/code-review gates, complete test coverage, accurate public documentation, and successful end-to-end validation.

## Residual Risks

**R1: Power-Loss Durability Non-Goal**

The design explicitly excludes "complete durability through sudden power loss on every filesystem" and targets "process-crash recovery." This is documented in the design spec non-goals section and public docs.

**R2: Two-Rename Live-Path Gap**

The existing-publish path has a short interval between `live -> backup` and `stage -> live` when the physical live pathname is absent. The design states "Eliminating that interval requires the deferred versioned-symlink architecture and is not a Stage 391 promise." This is documented in README.md, docs/row-one.md, docs/architecture.md, and CHANGELOG.md.

**R3: Concurrent External Mutation Out of Scope**

The design's local single-user model excludes "concurrent edits to unrelated output files by non-publisher processes." Preservation of unrelated file content and paths is promised; inode identity and concurrent external writes are not.

**R4: Windows Native-Handle Backend Deferred**

Windows lacks safe directory-relative operations in standard Python. The design states "A future Windows native-handle publisher may remove the capability restriction." The current implementation fails cleanly and mutation-free on Windows for latest-only paths, while ordinary non-latest rendering remains available.

APPROVED
