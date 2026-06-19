Review the Stage 120 design and implementation plan before coding.

Repository: `/home/ubuntu/fashion-radar`

Files to review:
- `docs/superpowers/specs/2026-06-20-stage-120-opencode-review-capture-hygiene-design.md`
- `docs/superpowers/plans/2026-06-20-stage-120-opencode-review-capture-hygiene-plan.md`
- Current targets:
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `docs/github-upload-checklist.md`
  - `tests/test_review_protocol_docs.py`
- Relevant prior evidence:
  - `docs/reviews/opencode-stage-40-release-review.md`
  - `docs/reviews/opencode-stage-40-release-rereview.md`
  - `docs/reviews/opencode-stage-74-code-review.md`
  - `docs/reviews/opencode-stage-84-code-review.md`
  - `docs/reviews/opencode-stage-119-code-review.md`

Review focus:
1. Does the plan address the recurring opencode live-capture / telemetry
   contamination problem without rewriting historical review artifacts?
2. Does the planned test fail before docs changes and pass after the exact
   planned docs text is added?
3. Do the updated command examples avoid direct final-file redirection into
   `docs/reviews/opencode-stage-N-...` paths?
4. Does the stage remain docs/tests-only, with no runtime, dependency,
   `uv.lock`, CI, connector, scraping, scheduling, monitoring, source
   acquisition, ranking, coverage verification, or compliance/audit product
   behavior?
5. Are the verification commands sufficient for this stage?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
