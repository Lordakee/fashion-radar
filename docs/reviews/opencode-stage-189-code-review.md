# Stage 189 Code Review

I verified the Stage 189 working-tree changes against the committed state, the design/plan, the prior Stage 188 review chain, and the actual test suite. I ran `check_release_hygiene.py` (passed), the full pytest suite, ruff check/format on the changed files, and line-anchored scans of the review archive.

## Critical

**C1 — The `docs/REVIEW_PROTOCOL.md` rewrite breaks `tests/test_review_protocol_docs.py::test_review_protocol_docs_document_capture_hygiene`, so the release gate fails.**

Task 4 Step 1 reworded the timeout paragraph from *"If the review times out, record the timeout honestly instead of presenting partial output as approval."* to *"If a review times out, retry with a narrower prompt or record the failed attempt in a separate scratch location; committed review artifacts must not be timeout stubs or partial output presented as approval."* (`docs/REVIEW_PROTOCOL.md:105-108`).

That removed the exact phrase `"if the review times out, record the timeout honestly"`, which is pinned by `REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES` at `tests/test_review_protocol_docs.py:28` and asserted against the `## Review Capture Hygiene` section (line 170-172). The full suite now reports `1 failed, 1392 passed`; `check_release_hygiene.py` passes but `pytest -q` does not.

Consequences the plan did not surface:
- Plan Task 5 Step 1 only runs `tests/test_release_hygiene.py`, so the gap was not caught there.
- Plan Task 6 Step 1 (`uv --no-config run --frozen pytest -q`) fails, blocking the release gate, which Q6 of this very review asks about.

The new protocol wording is arguably *better* policy (it aligns with the new timeout-stub detector — the old "record the timeout honestly" line would now contradict the detector). But the change was made without coordinating the test's required-phrase contract. Fix: either restore a compatible phrasing (e.g. "If the review times out, record the timeout honestly in a scratch location and retry; committed review artifacts must not be timeout stubs") that keeps the pinned phrase intact, or update `REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES` in tandem with the protocol edit. As committed to the working tree, the gate is red.

## Important

None. The detector logic, path predicate, tests, artifact cleanup, and Stage 188 follow-up records are sound (detailed below).

## Minor

- **M1 — Stale finding inside `docs/reviews/opencode-stage-188-release-rereview.md`.** Its M1 asserts `docs/reviews/opencode-stage-188-plan-review.md:23` "still cites `…opencode-full-project-review.md:219-238`". This same working tree already updated that citation to `:10-27` (`opencode-stage-188-plan-review.md:22-23`). The rereview's M1 is therefore inaccurate for the current state. Non-blocking, but a committed review record should not overstate a defect that is already fixed.
- **M2 — Task 1 heading mislabel (carried).** `test_non_stage_opencode_review_artifact_with_clean_body_passes` is a regression guard, not a RED test; the plan's "Add RED … Tests" heading is slightly imprecise. Plan-doc only.
- **M3 — `opencode-full-project-review.md` describes Stage 189 in future/intent tense** (lines 103-105: "Stage 189 is intended to fix…"). Acceptable for a historical pre-Stage-188 snapshot, but reads slightly oddly once Stage 189 is the active node. Cosmetic.

## Question-by-question

1. **Do the new tests prove the prior false negatives?** Yes. `test_non_stage_opencode_review_artifact_with_capture_noise_fails` proves the non-stage opencode blind spot is closed (fails on process-chatter + ANSI), and `test_stage_159_review_artifact_with_timeout_stub_fails` proves timeout-stub staged records are now rejected. `test_non_stage_opencode_review_artifact_with_clean_body_passes` guards the false-positive direction. All three pass.

2. **Is `is_review_capture_artifact_path(...)` narrow enough?** Yes. The stage branch is evaluated first and returns `False` when `stage < REVIEW_CAPTURE_MIN_STAGE` (159), preserving the Stage 158 legacy exclusion (covered by `test_stage_158_legacy_review_artifact_is_not_rechecked`). The `-prompt.md` early-return at `scripts/check_release_hygiene.py:377-378` sits before the non-stage branch, so both stage and non-stage prompt files are excluded (covered by `test_stage_159_review_artifact_prompt_with_tool_status_example_is_ignored`). The non-stage pattern's `(?!stage-[0-9]+-)` lookahead prevents it from catching legacy stage files. Sound.

3. **Is timeout-stub detection narrow enough?** Yes. `is_review_timeout_stub_line` uses `lower_line.startswith(prefix)` against three exact opencode status prefixes (`scripts/check_release_hygiene.py:90-94,431-433`). I confirmed the verbatim quote at `opencode-stage-188-release-review.md:50` (line starts with a backtick) and the mid-sentence occurrences in the Stage 189 plan-review/rereview records are *not* flagged, while ordinary prose like "the request timeout of 30s is honored" cannot trip it. `check_release_hygiene.py` passes against the full current archive.

4. **Are the cleanups and Stage 188 follow-ups coherent and free of capture noise?** Yes for content. `opencode-full-project-review.md` is a clean 106-line review starting with `# Full Project Review`, retaining the proxy-failure analysis (C1, lines 10-27) and roadmap correction; no ANSI, tool-status, or process-chatter. `opencode-stage-188-code-review.md` is now a 62-line completed review (Q1/Q2/Q3 + Verdict), no longer a timeout stub. The code-rereview and release-rereview records are coherent and self-consistent. Line-anchored scans found no tool-status lines, no ANSI escapes, and no line-starting timeout stubs in any new/cleaned artifact. (M1 above is an in-record accuracy nit, not capture noise.)

5. **Does the workflow test de-duplication preserve the Stage 188 proxy seam?** Yes. `test_collect_configured_sources_uses_injected_collectors` (`tests/test_workflows.py:61-81`) no longer takes `monkeypatch` or pins proxy env — it is the injected-collector baseline. `test_collect_configured_sources_with_injected_collectors_ignores_proxy_env` (`tests/test_workflows.py:84-109`) uniquely owns the proxy-env pin and the seam guard. The two now have a genuine behavioral difference; the proxy-seam coverage is retained in the second test. This resolves the Stage 188 code-review I1.

6. **Critical/Important blockers?** Yes — **C1 above**. The `REVIEW_PROTOCOL.md` edit breaks a pinned docs test and turns the full suite red, so the release gate cannot pass.

## Verdict

**Not approved for release-gate verification as-is.** The release-hygiene detector broadening, timeout-stub rejection, exclusions, tests, and review-archive cleanup are all correct and well-scoped (Q1-Q5 are satisfied). However, **C1** is a hard blocker: the current working tree fails `tests/test_review_protocol_docs.py::test_review_protocol_docs_document_capture_hygiene`, so Plan Task 6 Step 1's full `pytest -q` gate is red. Restore the pinned phrase (or coordinate the test's required-phrase tuple with the protocol edit), re-run the *full* suite to green, and then this stage is acceptable for release-gate verification.
