# Stage 90 Plan Review Prompt

Review the Stage 90 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-90-daily-digest-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-90-daily-digest-docs-boundary-plan.md`
- Current `docs/daily-digest.md`
- Current `tests/test_digests.py`

## Intended Goal

Add a standalone docs drift guard for `docs/daily-digest.md` that locks its
local file-only packaging, manual `.eml` review, and local observed source-set
boundary language without changing docs or runtime behavior.

## Scope Constraints

Allowed changes:

- `tests/test_daily_digest_docs.py`
- Stage 90 review artifacts

Disallowed changes:

- `docs/daily-digest.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- `tests/test_digests.py`
- review protocol docs/tests

Do not propose adding digest behavior, network behavior, email sending,
webhooks, browser automation, scheduling, source acquisition, platform
coverage, demand proof, ranking, scraping, connectors, platform APIs, schema
enums, new linter restrictions, or compliance-review product features.

## Review Questions

1. Are the proposed docs assertions present in current `docs/daily-digest.md`?
2. Are the phrases stable enough and not overly broad?
3. Is the scope safely test-only and independent from Stages 89, 91, and 92?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
