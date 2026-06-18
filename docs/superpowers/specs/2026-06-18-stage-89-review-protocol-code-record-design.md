# Stage 89 Review Protocol Code Record Design

## Goal

Update the active review protocol and guard test so the documented review record
naming convention includes implementation code reviews and code rereviews, not
only plan and release reviews.

## Scope

Modify:

- `docs/REVIEW_PROTOCOL.md`
- `tests/test_review_protocol_docs.py`
- Stage 89 spec/plan/review artifacts

Do not modify:

- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- product docs outside the review protocol
- community signal/import/adapter behavior
- `AGENTS.md`
- `docs/github-upload-checklist.md`

## Design

The current protocol already requires local Claude Code review of newly added
code during each implementation stage. The record naming section should name the
corresponding artifacts:

- `docs/reviews/claude-code-stage-N-code-review.md`
- `docs/reviews/claude-code-stage-N-code-rereview.md`

Add these names between plan and release records in the normal review block and
the follow-up rereview block.

Update `tests/test_review_protocol_docs.py` to assert all six active record
names:

- plan review
- code review
- release review
- plan rereview
- code rereview
- release rereview

Stage 89 itself continues to use `opencode-stage-89-*` plan/code review
artifacts because the current user-directed review runner for this development
thread is local opencode. This stage does not resolve the active-review-runner
drift between current execution practice and the checked-in Claude Code review
protocol. Treat that as an explicit carry-forward item, not an attempt to label
opencode output as Claude Code output.

## Tests

Use red/green focused verification:

```bash
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py::test_active_review_protocol_documents_claude_code_gate -q
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q
```

The first run should fail after adding the test assertions and before updating
`docs/REVIEW_PROTOCOL.md`.

## Boundaries

This stage is docs/test-only review-process maintenance. It does not add new
platform collection, scraping, connectors, browser automation, platform APIs,
account/session/cookie/token behavior, media downloads, monitoring, scheduling,
source acquisition, demand proof, ranking, coverage verification, schema enums,
new linter restrictions, or compliance-review product features.
