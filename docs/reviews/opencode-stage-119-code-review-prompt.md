Review the Stage 119 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Make local opencode with `zhipuai-coding-plan/glm-5.2 --variant max` the
  documented active review route.
- Preserve Claude Code `--effort max` as an explicit optional alternate route.
- Keep the node docs/tests-only.

Files changed:
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/github-upload-checklist.md`
- `tests/test_review_protocol_docs.py`
- `docs/superpowers/specs/2026-06-20-stage-119-review-protocol-opencode-alignment-design.md`
- `docs/superpowers/plans/2026-06-20-stage-119-review-protocol-opencode-alignment-plan.md`
- `docs/reviews/opencode-stage-119-plan-review-prompt.md`
- `docs/reviews/opencode-stage-119-plan-review.md`
- `docs/reviews/opencode-stage-119-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-119-plan-rereview.md`

Plan review artifacts:
- `docs/reviews/opencode-stage-119-plan-review.md`
- `docs/reviews/opencode-stage-119-plan-rereview.md`

Verification already run:
- RED: `env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q`
  failed as expected against old docs.
- GREEN: `env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q`
  passed with `2 passed`.
- Adjacent docs tests: `env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py tests/test_cli_docs.py -q`
  passed with `63 passed`.

Review focus:
1. Does the implementation match the reviewed Stage 119 design and plan?
2. Do `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, and
   `docs/github-upload-checklist.md` consistently document local opencode as the
   active review route?
3. Does `docs/REVIEW_PROTOCOL.md` preserve Claude Code `--effort max` only as an
   optional alternate route and keep its `claude-code-stage-N-...` artifact names?
4. Are the tests in `tests/test_review_protocol_docs.py` focused, meaningful,
   and aligned with the docs text?
5. Does the implementation remain docs/tests-only, with no runtime, dependency,
   `uv.lock`, CI, connector, scraping, scheduling, monitoring, source
   acquisition, ranking, coverage verification, or compliance/audit product
   behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
