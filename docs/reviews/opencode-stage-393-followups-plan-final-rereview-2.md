# Stage 393 Review Follow-ups — Plan Rereview (Final Conditions)

Scope: revised plan at `docs/superpowers/plans/2026-08-07-stage-393-review-followups-plan.md`, read against `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, and `docs/reviews/opencode-stage-393-followups-plan-final-rereview.md`. The three prior conditions (Task 1 allowlist-tightening framing, Worker D file-level ownership with changelog-helper intent, empty-string regression required) were each verified against the current plan text. No files were edited.

## Critical

None.

All three prior conditions are satisfied in the plan body:

- **Task 1 is a deliberate allowlist tightening, not only a TypeError guard.** The Architecture section states that "at the aggregation boundary this deliberately tightens the healthy allowlist to `ready` and `not_applicable`, rather than merely swallowing a TypeError; current producers already use those canonical healthy values." Task 1 Step 3's helper contract reiterates that it "accepts only string `ready` and `not_applicable`." This satisfies the prior Important finding #2.
- **Worker D exact file-level ownership with changelog-helper-only intent.** The Parallel Assignment Table row now lists Worker D / Halley's exact writable globs as **ONLY** `tests/test_scheduling.py`, `CHANGELOG.md`, and `tests/test_row_one_docs.py` (changelog-helper additions only), and reiterates the three files are exactly one coupled write set with no edits to `src/fashion_radar/scheduling.py`. This satisfies the prior Minor finding.
- **Empty-string regression remains required before implementation closes.** Task 1 Step 1 mandates that each of `"degraded"`, `None`, `""`, `[]`, `{}` be supplied to both `local_article_routes` and `local_article_content`, asserting `_overall_status(...)` returns exactly `"attention"` and does not raise. The `""` case is no longer left implicit. This satisfies the prior Important finding #1.

Hard constraints still hold:
- No new connectors, scraping, browser automation, platform APIs, scheduling behavior, source acquisition, demand proof, ranking, coverage verification, compliance review, Git metadata, commit, push, branch, or extra worktree.
- The override `--allow-unaccepted-content` stays smoke-only and is excluded from scheduling renderers and documentation snippets.
- Plan gate, finding-fix -> fresh-verification -> rereview loop, and honest timeout/fallback handling remain intact.

## Important

None.

The two prior Important findings and the prior Minor ownership-wording finding are all represented in the plan. No new Important issue was introduced by the revisions.

## Minor

1. **Residual Task 3 body wording vs. ownership table.** The Parallel Assignment Table now uses the requested "`tests/test_row_one_docs.py` (changelog-helper additions only)" wording, but Task 3 Step 1 and Step 4 body text still refer to "the Stage 393 changelog contract portion of `tests/test_row_one_docs.py`." Both phrases describe the same restriction, but "changelog-helper additions only" is the glob-level claim language AGENTS.md uses. Consider aligning the Task 3 body sentences to the table wording so a future code reviewer does not flag an apparent discrepancy. Non-blocking; the table is the authoritative ownership record.

2. **Worker B "pre-applied, reconcile only" status is implied, not stated.** The prior rereview's Minor note that both Worker B files already contain the candidate change is handled via the plan's "already-dirty baseline" language, but Task 2 still reads as fresh implementation. A one-line "Worker B work appears pre-applied; reconcile and fresh-run only" would reduce confusion. Non-blocking; Task 2 Step 2 and Step 5 already require a fresh integrated run.

3. **Smoke success-path over-specification carried forward unchanged.** The exact reasons substrings asserted against the fake handler stderr remain marginally more brittle than the plan's "stable substring" intent, but they assert against the fake, not the real CLI, so the real run is unaffected. Acceptable as-is.

## Verification

- **Condition 1 (allowlist tightening framing):** Present in Architecture and Task 1 Step 3. Verified at plan lines 12-15 and 225-226.
- **Condition 2 (Worker D file-level ownership + changelog-helper intent):** Ownership table lists exactly `tests/test_scheduling.py`, `CHANGELOG.md`, `tests/test_row_one_docs.py` (changelog-helper additions only) as one coupled write set; Worker D is barred from editing production scheduling files. Verified at plan line 104 and Task 3 header.
- **Condition 3 (empty-string regression required):** Task 1 Step 1 explicitly includes `""` in the five-value set for both local-article fields, with the top-level `"attention"` assertion. Verified at plan lines 182-195.
- **No new scope or dependency:** Worker B, Worker C, Worker D, and Coordinator claims are unchanged in scope from the previously reviewed revision; Prerequisites and Dependency Order (plan lines 115-148) introduce no new path, worker, external service, or sequencing coupling. No new tests, source files, review-record paths, or commands beyond what the prior rereview already audited.
- **Scope-boundary compliance:** Plan Scope And Non-Goals (lines 32-55) and Task list remain within ROW ONE diagnostic hardening, smoke override localization, documentation/changelog contract, and the parallel-execution repository test. No Phase 2-5 platform collection, scheduling policy, payload-key, default-exit, or compliance-review behavior is added.
- **Review-capture hygiene:** Plan continues to require one coherent captured body per review record, honest timeout handling, no stub/duplicate/truncated/tool-status capture, and rereview records rather than appended verdicts.

## Verdict

**Approve.** All three prior conditions are fixed in the plan body: Task 1 is explicitly framed as a deliberate `ready`/`not_applicable` allowlist tightening rather than only a TypeError guard; Worker D / Halley's ownership is recorded as exact file-level claims over `tests/test_scheduling.py`, `CHANGELOG.md`, and `tests/test_row_one_docs.py` with changelog-helper-additions-only intent; and the empty-string regression case is explicitly required in Task 1 Step 1 before implementation closes. No new scope, dependency, worker, path, or external coupling was introduced. The remaining items are Minor wording-consistency notes that can be resolved during implementation without re-review. The plan gate may proceed; Worker D / Halley's three-file write set may start once the completed primary plan review (or honest fallback) is recorded.
