# Stage 189 Plan Rereview

I re-verified the revised plan against the committed state: the real
`docs/reviews/` archive, the actual dirty artifacts, the current
`scripts/check_release_hygiene.py`, the full test file, and a line-anchored
scan of the proposed timeout prefixes across every tracked review record.

## Prior blockers

**C1 — Resolved.** The revised `is_review_timeout_stub_line` (Task 2 Step 3)
uses `lower_line.startswith(prefix)` against three exact opencode-status
prefixes (`opencode plan review timed out`, `opencode code review timed out`,
`opencode release review timed out`) instead of substring matching. I
verified behavior against the two files at issue:

- `docs/reviews/opencode-stage-188-code-review.md:5` — the real stub line,
  after `.strip()`, starts with `opencode code review timed out` → correctly
  flagged. Confirmed by `rg '^(opencode (plan|code|release) review timed out)'`
  returning exactly one match repo-wide: this line.
- `docs/reviews/opencode-stage-188-release-review.md:50` — the verbatim
  quote line, after `.strip()`, starts with a backtick
  (`` `docs/reviews/opencode-stage-188-code-review.md:5-6` reads: … ``) →
  `startswith` is False → not flagged. C1's false-positive is gone.

The line-anchored scan also confirms no other tracked review record has a
line beginning with one of the three prefixes, so the release gate will not
trip on any existing committed artifact once Task 3 cleans the three known
dirty files.

**I1 — Resolved.** The `startswith`-anchored matcher is strictly narrower
than the prior review's suggestion (anchoring to status/opening region).
Ordinary prose such as "the request timeout of 30s is honored" or "the
review timed out" cannot trip it because no legitimate prose line begins
with the literal `opencode <kind> review timed out` status string. The
stub-specific signal is preserved while the broad false-positive surface is
eliminated.

## Scope verification

1. **Stage 158 legacy exclusion preserved.**
   `is_review_capture_artifact_path` (Task 2 Step 2) checks
   `REVIEW_CAPTURE_ARTIFACT_PATTERN` first and returns False when
   `stage < REVIEW_CAPTURE_MIN_STAGE` (159). `opencode-stage-158-*` returns
   False before the non-stage branch is reached. `REVIEW_CAPTURE_MIN_STAGE`
   is untouched. Existing test
   `test_stage_158_legacy_review_artifact_is_not_rechecked` is in the Task 2
   Step 4 GREEN subset.

2. **Prompt-file exclusion preserved.** Stage prompt files
   (`opencode-stage-N-...-prompt.md`) do not match `REVIEW_CAPTURE_ARTIFACT_PATTERN`
   (which requires `review.md` / `rereview.md` terminally) and then hit the
   `lower_path.endswith("-prompt.md")` early-return. Non-stage prompt files
   hit the same early-return. Existing test
   `test_stage_159_review_artifact_prompt_with_tool_status_example_is_ignored`
   is in the Task 2 Step 4 GREEN subset.

3. **Cleanup covers all dirty artifacts the new detector would catch.**
   - `docs/reviews/opencode-full-project-review.md` is the only tracked
     non-stage `opencode-*.md` review record (verified via `git ls-files
     docs/reviews`); Task 3 Step 1 rewrites it.
   - `docs/reviews/opencode-stage-188-code-review.md:5` is the only
     timeout-stub line in the archive (verified via line-anchored `rg`);
     Task 3 Step 4 replaces the file via a scoped opencode re-run.
   - `docs/reviews/opencode-stage-188-release-review.md:50` is defensively
     paraphrased in Task 3 Step 2; even without the paraphrase it would not
     trip the revised detector, but the edit is correct hygiene and removes
     any future ambiguity.
   - The full-repo current-state test
     (`test_current_repository_tracked_review_artifacts_have_no_capture_findings`,
     `tests/test_release_hygiene.py:554`) will return `[]` after Task 3.

4. **Prerequisite maintenance node + product redirect.** The spec
   (`...design.md:31-34`) and plan (`...plan.md:13-19`) both state this is a
   prerequisite review-gate maintenance node and explicitly route the next
   product node to source-liveness / feed-health diagnostics. No `src/`
   runtime, collector, social-connector, or handoff-surface changes are in
   the modify list (Task 6 Step 3 `git add` confirms only `scripts/`,
   `tests/`, and `docs/`).

## Critical

None.

## Important

None.

## Minor

- **M1 — Task 1 heading still says "RED" for a non-RED test (carried
  forward).** `test_non_stage_opencode_review_artifact_with_clean_body_passes`
  (Task 1 Step 3) is a regression guard that passes both before and after
  the change; Task 1 Step 4 explicitly acknowledges this. The Task 1
  heading "Add RED Release-Hygiene Coverage Tests" is therefore slightly
  inaccurate. Cosmetic; does not affect correctness.

- **M2 — `claude-code-*` review records remain uncovered (carried forward,
  deliberate).** The broadened predicate matches only `opencode-*`.
  `docs/REVIEW_PROTOCOL.md:107-127` describes claude-code as an active
  optional route, and those artifacts can hold the same capture noise. This
  is a defensible scope decision for this node; note as a future scope
  expansion.

- **M3 — Paraphrase of the 188 release-review quote is now defensive rather
  than required.** With the `startswith`-anchored detector, line 50 of
  `opencode-stage-188-release-review.md` would not trip even unchanged.
  Task 3 Step 2's paraphrase is still correct hygiene (removes verbatim
  stub-text repetition from a review record) and is consistent with the
  rule's intent; no change needed, recorded for clarity.

- **M4 — Task 3 Step 4 and Step 6 lack the empty-output fallback that Task 5
    Step 3 and Task 6 Step 2 include.** Task 5/6 use
    `if [ ! -s <file> ]; then cp "$tmp_review" <file>; fi` after the `sed`
    extract, while Task 3 Step 4/Step 6 use only `test -s <file>` (which
    fails the step on empty output). Failing loudly on an empty opencode
    run is arguably the safer behavior for the Stage 188 refresh (it forces
    a retry rather than committing a stale capture), so this is acceptable;
    noting the inconsistency for awareness.

## Verdict

**Approved for implementation.** C1 and I1 are resolved by the
line-anchored `startswith` matcher, Stage 158 and prompt-file exclusions
are preserved, the cleanup scope covers every artifact the new detector
would otherwise fail on, and the plan correctly remains a prerequisite
review-gate maintenance node that redirects the next product node to
source-liveness diagnostics. The remaining findings are minor and
non-blocking.
