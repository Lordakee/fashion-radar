## Findings

**Critical:** None

**Important:** None

**Minor:** None

## Verified Areas

**AGENTS.md Codex Runtime Rule (AGENTS.md:57-59)**

The AGENTS.md file correctly states "Every Codex subagent spawned for this project must explicitly use model `gpt-5.6-sol` with reasoning effort `max`." This satisfies review requirement #9 and properly overrides all earlier Codex model rules.

**Published Recovery No-Backup Matrix Parametrization**

The valid and invalid published/no-backup recovery cases are properly parametrized over all four combinations of `had_live_output` (False, True) and `owner_present` (False, True) as required by the design spec section on published recovery and the plan rereview. Both test functions use `@pytest.mark.parametrize` for both dimensions, generating 4 test cases each (8 total for the no-backup published matrix).

- Valid case parametrization: `tests/test_row_one_publish.py:3644-3647`
- Invalid case parametrization: `tests/test_row_one_publish.py:3716-3719`

**First-Run Debris Validation Coverage**

The first-run smoke check at `scripts/check_first_run_smoke.py:3682` calls `assert_row_one_publish_artifacts_clean(row_one_output_dir)` after the serve smoke test. The helper at lines 3898-3927 correctly denies canonical journal, stage, backup, temporary journals, and the private owner file while explicitly allowing the stable lock file. This matches the design requirement that "the stable lock file is allowed to remain after a successful publish."

**Capability Detector Call Count and Test Coverage**

The pure `_safe_directory_operations_supported()` helper is called exactly once at module import (line 55) to initialize `_SAFE_DIRECTORY_OPERATIONS_SUPPORTED`. The public gate `_require_safe_directory_operations()` reads only this constant (lines 122-124) and never calls the detector again.

Test `test_public_publish_gate_uses_import_time_capability_before_any_side_effect` at line 2352 monkeypatches the detector to raise and patches the constant to `False`, proving the gate never redetects. Test `test_safe_directory_operations_supported_requires_all_directory_fd_operations` at line 2310 and `test_safe_directory_operations_supported_requires_each_open_flag` at line 2331 independently remove each of the four `os.supports_dir_fd` memberships and each flag, confirming the six-part predicate.

**Mutation-Free Canonical Journal Boundary**

`_read_canonical_journal` (lines 1043-1062) validates and reads only the deterministic canonical journal. It never calls `_recover_temporary_journals` and performs no writes, promotions, renames, or deletions. `_load_journal` (lines 1065-1067) is the sole recovery-capable entry that calls `_recover_temporary_journals` before delegating to `_read_canonical_journal`.

All cleanup and rollback preflight callers use `_read_canonical_journal`:
- `_cleanup_after_handled_failure:2414`
- `_preflight_cleanup_artifacts:2288`
- `_preflight_rollback_artifacts:2331`
- `_cleanup_after_rollback_restore:1787`
- `_remove_matching_temporary_journals:2366`
- `_remove_owned_backup_if_present:2381`
- `_remove_canonical_journal:2392`

None of these paths call `_load_journal` or `_recover_temporary_journals`, preventing mutation before the complete preflight validates all artifacts.

**Live Owner Binding Contract**

`_read_owner_token_if_present` (lines 809-836) binds the managed live root and `data/` child with descriptor-relative operations. It returns `None` only for a missing final owner file. For a present owner, it parses both token and `physical_output`, then returns the token only after exact equality: `if physical_output != directory` raises ambiguous state (line 832). This differs from stage ownership, which validates the `(token, physical_output)` tuple against the transaction without requiring exact directory equality.

All live owner consumers pass `transaction.target.physical_output` as the directory argument:
- `_validate_published_row_one_site:846`
- `_is_owned_live:888`
- `_published_live_owner_preflight:1920`

**Live Root Metadata Timing**

`_apply_live_root_metadata` (lines 569-576) calls `shutil.copystat(live, stage, follow_symlinks=False)` only when `transaction.had_live_output` is true (first-publish no-op is explicit). The single production call site is in `publish_latest_row_one_site:2509`, placed after `_validate_staged_row_one_site` and immediately before `_replace_phase(transaction, RowOnePublishPhase.READY)` at line 2510.

This timing is after staged rendering and validation but before the `ready` journal write or any live rename, matching the plan amendment specification. The `copystat` reads the still-live root's mode and timestamp at that exact snapshot point under the local single-user/non-concurrent-external-mutation model.

**KeyboardInterrupt Identity Preservation**

Four test cases parametrize `KeyboardInterrupt` and `SystemExit` to verify they are re-raised unchanged:
- `test_first_publish_journal_write_failure_before_rollback_cleanup_raises_control_unchanged:3385`
- `test_first_publish_journal_write_failure_after_rollback_cleanup_raises_control_unchanged:3420`
- `test_existing_publish_journal_write_failure_before_rollback_raises_control_unchanged:4267`
- `test_existing_publish_journal_write_failure_after_rollback_raises_control_unchanged:4290`

In `_commit_first_publish` (lines 1670-1706), line 1702 re-raises `KeyboardInterrupt` and `SystemExit` unchanged after successful rollback. In `_commit_existing_publish` (lines 1709-1751), line 1719 re-raises them unchanged for the live-move failure path. `_rollback_existing_publish` at line 1839 re-raises them after rollback completes. The orchestrator at line 2521 catches them separately and performs cleanup only if `not commit_started`.

A `KeyboardInterrupt` during the first live rename leaves a `live_moving` journal for recovery and does not attempt a phase rollback that could demote the control-flow exception.

**Windows Test Skip Strategy**

The implementation defines `_REQUIRES_SAFE_DIRECTORY_OPERATIONS = pytest.mark.skipif(...)` at line 2091 but this decorator is applied to capability-requiring tests. Platform-neutral tests for FIFO and socket fixtures use explicit `hasattr(os, "mkfifo")` and `hasattr(socket, "AF_UNIX")` skip conditions.

Windows will fail the capability gate before the publisher creates artifacts. The test suite includes explicit unsupported-capability tests that monkeypatch the constant to `False` and verify the mutation-free failure. Non-latest rendering bypasses the gate entirely (verified in `test_non_latest_renderer_bypasses_publish_capability_gate:2381`).

## Questions And Assumptions

The implementation satisfies all design requirements with no open questions. Key verification methods included direct source inspection and comprehensive test coverage across all journal phases, recovery scenarios, and boundary conditions.

## Residual Risks

**R1: Power-Loss Durability Non-Goal**

The design explicitly states "It does not claim complete durability through sudden power loss on every filesystem" and "The design targets process-crash recovery." This is an accepted non-goal per the specification section on atomic journal writes and non-goals.

**R2: Two-Rename Live-Path Gap**

The existing-publish path has a short interval between `live -> backup` and `stage -> live` when the physical live pathname is absent. The design states "There is a short interval between the two directory renames when the physical live pathname is absent. Eliminating that interval requires the deferred versioned-symlink architecture and is not a Stage 391 promise." This is documented in README.md, docs/row-one.md, and CHANGELOG.md.

**R3: Concurrent External Mutation Out of Scope**

The design's local single-user model excludes "concurrent edits to unrelated output files by non-publisher processes" and "Concurrent hostile replacement of an already resolved ancestor above that transaction root is outside this local, single-user publisher's threat model." Preservation of unrelated file content and paths is promised; inode identity and concurrent external writes are not.

**R4: Windows Native-Handle Backend Deferred**

Windows lacks safe directory-relative operations in standard Python. The design states "A future Windows native-handle publisher may remove the capability restriction" but this remains a follow-up. The current implementation fails cleanly and mutation-free on Windows for latest-only paths.

## Verification Evidence

- Targeted 14-file integration: 1463 passed
- Unsupported-capability simulation: 19 passed, 16 skipped
- Full sanitized public_uv suite: 3244 passed
- Ruff check and format check passed
- git diff --check and release hygiene passed
- uv.lock SHA-256 unchanged at 09c2236c8fe3821b6982c1abe3f447ddcc4c6a3fd9392d1c054f4522a85947c9
- Task 4 post-fix spec rereview: SPEC COMPLIANT
- Task 4 post-fix quality rereview: APPROVED with no remaining findings

Implementation statistics:
- Core publisher: 2,534 lines (`src/fashion_radar/row_one/publish.py`)
- Publisher tests: 5,602 lines (`tests/test_row_one_publish.py`, 194 test functions)
- Total change: 23 files, +2849 lines, -151 lines
- No dependency changes, no schema changes, no uv.lock changes

The Stage 391 implementation is spec-compliant, test-complete, and production-ready. All acceptance criteria are satisfied including capability gate correctness, descriptor-bound operations, atomic journals, stage creation and validation, commit and rollback ordering, recovery for every journal phase, ambiguity-free failure behavior, renderer integration, first-run debris validation, wheel/sdist membership, public documentation, AGENTS.md Codex runtime rule, and release hygiene.

APPROVED
