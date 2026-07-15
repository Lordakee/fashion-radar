# Stage 391 Readiness Plan Rereview

The diff spans both the plan and design docs. All five points are reviewable
without additional file reads; the pseudocode, helper table, and matrix are
self-contained within the diff.

## Point 1: Mutation-Free Canonical Journal Preflight

The split is clean and fully specified. The pseudocode gives exact
implementations:

- `_read_canonical_journal` reads `target.journal_path` without recovery side
  effects.
- `_load_journal` calls `_recover_temporary_journals`, then delegates to
  `_read_canonical_journal`.

Every preflight caller (`_preflight_cleanup_artifacts`, rollback,
`_remove_owned_backup_if_present`, and `_cleanup_after_handled_failure`) is
updated to use `_read_canonical_journal`. The prohibition on calling
`_load_journal` or `_recover_temporary_journals` from those paths is stated in
both the plan and design. The helper table adds `_read_canonical_journal` at
Task 3 Step 4 consistently with the first Step 4 implementation action. No
ambiguity forces a guess.

## Point 2: Live Owner Binding

The contract is coherent. `_read_owner_token_if_present` must parse both fields
and return the token only after `physical_output == directory` using an exact
comparison with no normalization. This applies to live-root published
validation, `_is_owned_live`, `_remove_owner_file_from_managed_root`, and all
rollback or cleanup preflights that inspect a present live owner. Stage
ownership retains its existing token-and-physical-output tuple check against
the transaction object. That deliberate distinction is documented in both
files.

Removing the redundant inline stage-owner check in
`_cleanup_after_handled_failure` is correct because the complete preflight now
covers it.

## Point 3: Capability Detector

The refactor is sound. The pure `_safe_directory_operations_supported()`
helper covers all six conditions: four `os.supports_dir_fd` memberships plus
`O_DIRECTORY` and `O_NOFOLLOW`. `_SAFE_DIRECTORY_OPERATIONS_SUPPORTED` is
initialized exactly once at module level, and the public gate reads only that
constant.

The test strategy separates concerns cleanly: pure-helper tests call the
function directly with a synthetic baseline; public-gate tests monkeypatch the
constant and also make the detector raise, proving the gate never redetects.
The helper table and checklist are consistent.

## Point 4: Live Root Metadata

The timing is unambiguous in both documents. `_apply_live_root_metadata` calls
`shutil.copystat(live, stage, follow_symlinks=False)` after rendering and staged
validation, before the `ready` journal write or any live rename. There is no
captured-before-render field or transaction snapshot. The local single-user,
non-concurrent-external-mutation model is explicit. The staged-render sequence
and checklist agree.

## Point 5: Published Without Backup

The matrix is complete. The valid/no-backup case covers all four combinations
of `had_live_output` and owner presence, keeps live, and finishes bounded
cleanup. The invalid/no-backup case covers the same combinations, raises
`RowOnePublishAmbiguousStateError` before cleanup deletion, and preserves all
seeded artifacts. The fixture explicitly contains no temporary journal, so
`_load_journal` recovery is a no-op and the preservation claim holds end to
end. The design matrix and `_finish_published_recovery` prose are consistent.

## Verdict: APPROVED

## Critical

None.

## Important

`_cleanup_after_handled_failure` assigns `canonical` only for a missing-journal
guard, while `_preflight_cleanup_artifacts` deliberately performs a second
canonical read and full equality check. The behavior is unambiguous, but the
pseudocode should include a short comment explaining the missing-journal guard
versus full-preflight separation.

## Nits

- Link the direct `_read_canonical_journal` tests in the earlier fault-injection
  step to the Step 4 extraction instruction so their location is intentional.
- In the staged-render sequence, mention that `_apply_live_root_metadata` is a
  no-op when `had_live_output` is false.
- Clarify that the valid owner-present/no-backup recovery state is accepted
  regardless of how it arose; it is a conservative idempotent superset of the
  states emitted by the chosen cleanup order.
