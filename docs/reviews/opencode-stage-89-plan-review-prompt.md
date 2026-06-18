# Stage 89 Plan Review Prompt

Review the Stage 89 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-89-review-protocol-code-record-design.md`
- `docs/superpowers/plans/2026-06-18-stage-89-review-protocol-code-record-plan.md`
- Current `docs/REVIEW_PROTOCOL.md`
- Current `tests/test_review_protocol_docs.py`

## Intended Goal

Document and test active review record names for implementation code reviews
and code rereviews, aligning the naming convention with the existing protocol
requirement that each implementation stage includes local Claude Code review of
newly added code.

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

Do not propose adding scraping, connectors, browser automation, platform APIs,
login/cookie/session/token behavior, media downloads, monitoring, scheduling,
source acquisition, demand proof, ranking, coverage verification, schema enums,
new linter restrictions, or compliance-review product features.

## Current Review Runner Constraint

The current user-directed review runner for this development thread is local
opencode, so Stage 89 review artifacts use `opencode-stage-89-*` names. Do not
recommend renaming opencode-generated artifacts to `claude-code-stage-89-*`.
Instead, review whether the plan clearly documents this as carry-forward drift
while still updating the checked-in Claude Code protocol naming convention.

## Review Questions

1. Does the plan correctly align the record naming section with the existing
   code-review requirement?
2. Does the test assertion shape cover both review and rereview names without
   overreaching into historical `opencode-*` records?
3. Is the scope safely docs/test-only?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
