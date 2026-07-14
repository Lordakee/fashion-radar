# OpenCode Stage 391 Plan Rereview (Formal Fallback)

**Reviewer:** opencode (`zhipuai-coding-plan/glm-5.2 --variant max`)
**Scope:** Rereview of the Stage 391 design and plan after incorporation of the seven Minor findings from `/tmp/opencode-stage-391-plan-review.out`.

## Verification Of Incorporated Amendments

- **M1 (`live_moving` / live-present / no-backup recovery):** Design line 385 adds the matrix row "`live_moving`, old live present, no backup | The live-to-backup rename did not complete; keep and validate old live, then remove token-owned stage and journal." Plan line 1289 names `test_recovery_keeps_old_live_when_live_moving_rename_failed`, and plan lines 1302-1305 specify the exact seed (old live in place, no backup, owned stage, `live_moving` journal) and expected cleanup scope. Incorporated.
- **M2 (owner-marker write cleanup in `_begin_staging`):** Plan lines 1346-1364 wrap `_write_owner_file` in `try/except BaseException`; on failure it attempts `_remove_publish_path(stage)` and raises `RowOnePublishCleanupPendingError` only if that removal also fails. Task 3 Step 2 RED test (plan lines 1056-1061) asserts both the cleaned-stage happy path and the cleanup-pending failure case. Incorporated.
- **M3 (internal staged-result path semantics and public renderer rebasing):** Design lines 432-445 document that internal staging paths are not returned. Plan docstring (lines 138-143) states `output_dir`/`index_path` identify staging paths and that the public renderer must rebase. Plan lines 1647-1653 rebase to `RowOneRenderResult(output_dir=output_dir, index_path=output_dir / "index.html", ...)`. Incorporated.
- **M4 (`_remove_publish_path` special-file fail-fast):** Plan lines 1033-1041 add `elif path.exists(): raise RowOnePublishAmbiguousStateError(...)`. A FIFO/socket/device now raises instead of silently returning. Incorporated.
- **M5 (public `clean_row_one_site_children` docstring):** Plan lines 1656-1660 direct the renderer integration to retain the mutating function with a docstring stating it remains a public explicit-cleanup utility not invoked by the staged publisher, and that it delegates to the shared read-only marker safety helper. Incorporated.
- **M6 (`RowOnePublishPreservedError` cleanup and bypass):** Plan lines 1195-1197 raise the dedicated `RowOnePublishPreservedError` after the READY rollback and handled cleanup succeed; plan lines 1493-1500 add it to the outer-handler bypass tuple. The dedicated sanitized message survives unwrapped, while the original `OSError` is retained as `__cause__`. Incorporated.
- **M7 (KeyboardInterrupt/SystemExit before vs during commit):** Plan lines 1182-1184 in `_commit_existing_publish` re-raise `KeyboardInterrupt`/`SystemExit` immediately when the live→backup rename fails, before any READY-phase journal rollback. Plan lines 1104-1106 add the RED test asserting the `live_moving` journal survives for recovery. The public function (plan lines 1501-1504) gates pre-commit cleanup on `not commit_started`, leaving commit-time control-flow exceptions to the commit handlers. Incorporated.

## Verification That Amendments Did Not Weaken Required Surfaces

- **All-artifact cleanup preflight:** Plan lines 1377-1394 retain the single read-only preflight over canonical journal, phase, owner, stage, backup, complete temporary-journal set, and extra sibling rejection. The M2 amendment's `_remove_publish_path(stage)` call happens only after the journal exists and is preflight-checked; an unsafe stage object still raises ambiguous and deletes nothing. Plan lines 1099-1103 retain the unsafe-temporary-journal and unsafe-backup cleanup tests. Unchanged in strength.
- **Ordinary error sanitization:** Plan lines 1493-1510 still wrap ordinary `BaseException` from copy/render/validation as `RowOnePublishError("ROW ONE staged publish failed before commit; the live site was preserved")`, while the path-bearing recovery errors (Ambiguous, Rollback, CleanupPending, Preserved, Restored) bypass wrapping. Plan lines 1685-1692 retain the CLI sanitization test that injects tokenized stage paths, tokens, and physical targets and asserts they do not leak while `Rollback`/`Ambiguous` retained paths remain visible. The M6 `RowOnePublishPreservedError` is correctly on the bypass list, so its sanitized message survives without being collapsed into the generic wrapper. Unchanged in strength.
- **Immutable release sequence:** Plan lines 2068-2070 capture `implementation_head` at the implementation commit; lines 2184-2187 require HEAD equality and clean snapshot before/after validation; lines 2102-2182 run the complete public-uv validation; lines 2271-2304 allowlist only review records plus plan/spec in the release-record delta; lines 2321-2339 verify authorized remote URL, ancestry, and post-push SHA. No amendment touches these controls. Unchanged in strength.

## Critical Findings

None.

## Important Findings

None.

## Verdict

**APPROVED.** All seven Minor findings are incorporated with both implementation and RED-test coverage, and the amendments do not weaken the all-artifact cleanup preflight, ordinary error sanitization, or the immutable release sequence. Implementation may begin.
