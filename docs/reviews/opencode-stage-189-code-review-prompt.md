# Stage 189 Code Review Prompt

Review the Stage 189 working-tree changes before release-gate verification.
Evaluate uncommitted changes intended for the next commit. Do not treat "not
committed yet" as a blocking finding.

Repository: `/home/ubuntu/fashion-radar`

Primary files:

- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- `docs/reviews/opencode-full-project-review.md`
- `docs/reviews/opencode-stage-188-plan-review.md`
- `docs/reviews/opencode-stage-188-code-review.md`
- `docs/reviews/opencode-stage-188-code-rereview-prompt.md`
- `docs/reviews/opencode-stage-188-code-rereview.md`
- `docs/reviews/opencode-stage-188-release-review.md`
- `docs/reviews/opencode-stage-188-release-rereview-prompt.md`
- `docs/reviews/opencode-stage-188-release-rereview.md`
- `tests/test_workflows.py`
- `docs/REVIEW_PROTOCOL.md`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-24-stage-189-review-capture-hygiene-coverage-design.md`
- `docs/superpowers/plans/2026-06-24-stage-189-review-capture-hygiene-coverage-plan.md`
- `docs/reviews/opencode-stage-189-plan-review.md`
- `docs/reviews/opencode-stage-189-plan-rereview.md`

Questions:

1. Do the new release-hygiene tests prove the prior false negatives for
   non-stage opencode reviews and timeout-stub staged reviews?
2. Is `is_review_capture_artifact_path(...)` narrow enough to preserve Stage
   158 legacy and prompt-file exclusions while scanning non-stage opencode
   review records?
3. Is timeout-stub detection narrow enough to avoid false positives on ordinary
   timeout prose while catching real opencode timeout status stubs?
4. Are the review artifact cleanups and Stage 188 follow-up review records
   coherent, non-misleading, and free of capture noise?
5. Does the workflow test de-duplication preserve the Stage 188 proxy seam
   coverage?
6. Are there any Critical or Important issues that should block release-gate
   verification?

Report findings under:

- Critical
- Important
- Minor

If acceptable, say the Stage 189 changes are approved for release-gate
verification.

Start the response exactly with:

```text
# Stage 189 Code Review
```

Do not include process chatter, command logs, ANSI output, or tool-status lines.
