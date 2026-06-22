## Verdict

**No critical findings.** One **important** finding (test-fixture fidelity) and three **minor** findings. The plan is safe to proceed after addressing the important finding.

---

## Critical
None.

## Important

**I-1: Deterministic `candidate_preview` fixture cannot be produced by the real CLI.**
In `community_handoff_check_dir_payload()` (plan Task 1, Step 1), the `candidate_preview` block contains `directory` and `pattern` keys, but the real `CommunityCandidateDirectoryPreview` model (`src/fashion_radar/community_candidates.py:53`) uses `ConfigDict(extra="forbid")` and has **no** `directory`/`pattern` fields. It also omits required fields `current_window_start`, `baseline_window_start`, `current_days`, `baseline_days`, and `limit`, all of which the real CLI serializes. The same fidelity gap applies to the `community_signal_lint` block, which omits `field_counts`, `source_name_counts`, `platform_counts` that the real `CommunitySignalDirectoryLintResult` (`community_signals.py:87`) always emits.

Why it matters: the whole point of Stage 158 is to assert the real JSON. The validator only reads a subset (so tests pass), but the deterministic test then guards a shape that can never occur in production, so it will not catch nested-schema drift. It is also inconsistent with the sibling helper `community_candidates_payload(directory=True)` (`tests/test_first_run_smoke.py:343`), which correctly includes the window fields and omits `directory`/`pattern`.

Fix: mirror the real model shapes in the helper (drop `directory`/`pattern` from `candidate_preview`; add `current_window_start`, `baseline_window_start`, `current_days`, `baseline_days`, `limit`; add `field_counts`/`source_name_counts`/`platform_counts` to the lint block), or construct the nested objects from the real pydantic models. The real smoke still covers integration, so this is not blocking, but it should be fixed before the fixture ossifies.

## Minor

**M-1: No payload-parity test.** Other helpers have cross-checks like `test_external_tool_workflow_payload_matches_real_rednote_workflow` (`test_first_run_smoke.py:1403`). The new helper has none. `check_community_handoff_directory()` needs a real directory + scoring config, so a parity test is heavier; acceptable to skip given real smoke coverage, but worth noting.

**M-2: Rejection parametrize skips nested-count drift.** `test_validate_community_handoff_check_dir_rejects_top_level_drift` only perturbs top-level scalars. The design explicitly scopes out nested-row internals, but one nested-count rejection case (e.g. `community_signal_lint.row_count = 5`) would confirm the nested assertions actually fire. Low priority.

**M-3: `candidate_preview` null path undocumented.** The real model allows `candidate_preview = None` on preview failure (with `ok=False`). The validator requires it to be a dict, which is correct for the OK first-run contract; just noting for completeness.

---

## Answers to review questions

1. **Right next narrow stage after 157?** Yes. Stage 157 added the direct `community-handoff-check-dir ... --strict` call (`scripts/check_first_run_smoke.py:2581`) and discards stdout; validating the JSON is the natural, minimal next step.
2. **Validator asserts useful guarantees without overfitting?** Yes - the validator reads a stable subset (execution_mode, ok, counts, strict, nested counts) and avoids nested rows/internals, matching CLI unit-test coverage. Its value is undercut by I-1 (fixture fidelity), not by its own scope.
3. **Test strategy sufficient to fail before / pass after?** Yes for RED/GREEN: RED via `AttributeError` (missing validator) + command-sequence mismatch (no `--format json`); GREEN via Task 2. Weaker for real drift detection due to I-1.
4. **Scope preserved?** Yes. No runtime CLI changes, no platform collection, no write-capable import; `--format json` is a read-only output switch and the validator only reads JSON.
5. **Missing release/review-gate steps?** No. Plan covers plan review (this prompt), code review (Task 4 Step 2), full release gate incl. `UV_NO_CONFIG=1 uv lock --check`, `git diff --check`, token/header sweeps (Task 4 Step 3), and records all four `docs/reviews/opencode-stage-158-*` artifacts. Consistent with `AGENTS.md`.

Recommendation: address **I-1** before implementation (it only touches the test fixture text in Task 1 Step 1), then proceed.
