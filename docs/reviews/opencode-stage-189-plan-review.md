# Stage 189 Plan Review

I verified the plan against the actual committed state (the real Stage 188 review chain, all `docs/reviews/` files, and a substring scan of the proposed timeout phrases across the archive).

## Question-by-question

1. **Real gaps identified?** Yes. `docs/reviews/opencode-full-project-review.md` is full of ANSI escapes, `→ Read`/`build ·`/`$` tool UI markers, and `I'll…`/`Let me…` process chatter and currently passes hygiene because the predicate ignores it. `docs/reviews/opencode-stage-188-code-review.md:5-6` is a genuine timeout stub that currently passes. Both gaps are real.
2. **RED tests behave as predicted?** The two intended RED tests do fail-before/pass-after *in isolation*. But the plan's GREEN claim for the full file is false — see C1.
3. **Stage 158 + prompt exclusions preserved?** Yes. The ordering in the new `is_review_capture_artifact_path` (stage match → `-prompt.md` early-return → non-stage pattern) is correct, and `REVIEW_CAPTURE_MIN_STAGE = 159` is untouched.
4. **Sufficient and scoped?** No — see C1. The omission of `opencode-stage-188-release-review.md` breaks the plan's own gate.
5. **Reasonable prerequisite node?** Yes. A guard that currently false-passes undermines every future review gate; fixing it before the next product node is sound, and the plan correctly redirects the next node to source-liveness/feed-health.
6. **Avoids product/collector/social/handoff expansion?** Yes. Only `scripts/`, `tests/`, and docs are touched; no `src/` runtime, no new collectors, no social connectors, and the Stage 188 follow-up is review-record cleanup, not handoff surface.

## Critical

**C1 — The new timeout-stub detector fails the plan's own release gate on an existing committed file, and the plan never addresses it.**
`docs/reviews/opencode-stage-188-release-review.md:50` legitimately *quotes* the Stage 188 stub verbatim as evidence in its Important finding I1: *"…reads: 'opencode code review timed out after 600 seconds. No partial output was captured as approval.'"*. The proposed `is_review_timeout_stub_line` does substring matching (`"timed out"`, `"timeout"`, `"no partial output"`, `"captured as approval"`) on every line, so it flags line 50 of that file. That file is **not** in the plan's modify list (Task 3 only rewrites `opencode-stage-188-code-review.md` and adds `opencode-stage-188-release-rereview.md`). Consequences, all uncaught by the plan:
- `tests/test_release_hygiene.py:554` (`test_current_repository_tracked_review_artifacts_have_no_capture_findings`) runs the new logic over every tracked review file and will now return a non-empty list → assertion fails.
- Task 3 Step 6 (`check_release_hygiene.py … → "Release hygiene checks passed."`) fails.
- Task 5 Step 1 (full `tests/test_release_hygiene.py`) and Task 6 Step 1 release gate both fail.

Task 2 Step 4 only runs a 5-test selected subset and so would not surface this; the breakage only appears at the full-file/release-gate steps, where the plan asserts GREEN.

## Important

**I1 — The timeout-stub detector is over-broad and will generate recurring false positives on legitimate review prose.**
Matching the bare substrings `"timeout"`/`"timed out"` on any line is too aggressive for a repository whose core is HTTP collectors, robots.txt gating, and scheduling — all of which have legitimate timeouts. A future code review of `src/fashion_radar/collectors/` that says "the request timeout of 30s is honored" would fail release hygiene. This is the same root cause as C1. The detector should target stub-*status* signal specifically (e.g., patterns like `review … timed out … seconds`, the exact phrase `no partial output was captured as approval`, or anchoring to the file's status/opening region) rather than any occurrence of "timeout"; and the existing 188 release-review quote must be neutralized (paraphrase the quoted stub, or drop the verbatim quote) so the gate passes without weakening the detector's real target.

## Minor

- **M1 — Test 3 is mislabeled as RED.** Task 1 is headed "Add RED Release-Hygiene Coverage Tests," but `test_non_stage_opencode_review_artifact_with_clean_body_passes` is explicitly acknowledged in Step 4 as passing both before and after. It is a regression guard, not a RED test; the heading/Step-4 note should say so.
- **M2 — `claude-code-*` review records remain uncovered by design.** The broadened predicate only matches `opencode-*`. That is consistent with the stated objective, but `docs/REVIEW_PROTOCOL.md` describes claude-code as an active optional route and those artifacts can hold the same capture noise. Note as a deliberate scope decision for a future node, not this one.
- **M3 — Hand-sanitizing `opencode-full-project-review.md` vs re-running.** Keeping the substantive findings and stripping capture noise is defensible (and consistent with the hygiene rule's intent), but it is a manual edit of a review record; confirm the cleaned body retains no `"timeout"` substring since that would now also trip I1's detector.

## Verdict

**Not approved for implementation as written.** C1 must be resolved first: tighten `is_review_timeout_stub_line` so it does not substring-match `"timeout"`/`"timed out"` on arbitrary lines, and neutralize the verbatim stub quote at `docs/reviews/opencode-stage-188-release-review.md:50` (or otherwise bring that file within the cleanup scope). Once C1/I1 are addressed and the plan's Task 3 Step 6, Task 5 Step 1, and Task 6 Step 1 genuinely pass, the remainder of the plan is sound and can proceed.
