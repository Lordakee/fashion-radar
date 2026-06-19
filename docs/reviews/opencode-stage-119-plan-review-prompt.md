Review the Stage 119 design and implementation plan before coding.

Repository: `/home/ubuntu/fashion-radar`

Files to review:
- `docs/superpowers/specs/2026-06-20-stage-119-review-protocol-opencode-alignment-design.md`
- `docs/superpowers/plans/2026-06-20-stage-119-review-protocol-opencode-alignment-plan.md`
- Current targets:
  - `AGENTS.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `docs/github-upload-checklist.md`
  - `tests/test_review_protocol_docs.py`
- Relevant prior review findings:
  - `docs/reviews/opencode-stage-117-plan-review.md`
  - `docs/reviews/opencode-stage-117-code-review.md`
  - `docs/reviews/opencode-stage-118-plan-review.md`
  - `docs/reviews/opencode-stage-118-plan-rereview.md`
  - `docs/reviews/opencode-stage-118-code-review.md`

Review focus:
1. Does the plan correctly align the active staged review workflow with local
   opencode using `zhipuai-coding-plan/glm-5.2 --variant max`?
2. Does the plan preserve Claude Code `--effort max` as an optional alternate
   route without contradicting the active opencode route?
3. Is the planned test internally consistent with the exact planned doc text and
   existing helpers in `tests/test_review_protocol_docs.py`?
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
