# Stage 89 Code Review Prompt

Review the Stage 89 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 89 updates the active review protocol to document
`claude-code-stage-N-code-review.md` and
`claude-code-stage-N-code-rereview.md` record names. It also updates the review
protocol docs test to assert plan/code/release review and rereview names inside
the `## Review Record Naming` section, including ordering.

## Files To Review

- `docs/REVIEW_PROTOCOL.md`
- `tests/test_review_protocol_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-89-review-protocol-code-record-design.md`
- `docs/superpowers/plans/2026-06-18-stage-89-review-protocol-code-record-plan.md`
- `docs/reviews/opencode-stage-89-plan-review-prompt.md`
- `docs/reviews/opencode-stage-89-plan-review.md`
- `docs/reviews/opencode-stage-89-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-89-plan-rereview.md`

## Scope Constraints

Allowed changes:

- `docs/REVIEW_PROTOCOL.md`
- `tests/test_review_protocol_docs.py`
- Stage 89 review artifacts

Disallowed changes:

- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- product docs outside the review protocol
- community signal/import/adapter behavior
- `AGENTS.md`
- `docs/github-upload-checklist.md`

Current user-directed review runner is local opencode, so Stage 89 review
artifacts use `opencode-stage-89-*` names. Do not request renaming them to
`claude-code-stage-89-*`; the design/plan document this as carry-forward drift.

Do not propose adding scraping, connectors, browser automation, platform APIs,
login/cookie/session/token behavior, media downloads, monitoring, scheduling,
source acquisition, demand proof, ranking, coverage verification, schema enums,
new linter restrictions, or compliance-review product features.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py::test_active_review_protocol_documents_claude_code_gate -q
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q
uv --no-config run --frozen ruff check tests/test_review_protocol_docs.py
uv --no-config run --frozen ruff format --check tests/test_review_protocol_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 89 plan and scope?
2. Does the test correctly scope record-name ordering to the Review Record
   Naming section despite the During Development cross-reference?
3. Is the opencode artifact naming drift documented as carry-forward without
   weakening the active Claude Code protocol docs guard?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
