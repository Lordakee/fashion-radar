# Stage 90 Code Review Prompt

Review the Stage 90 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 90 adds `tests/test_daily_digest_docs.py`, a standalone docs drift guard
for `docs/daily-digest.md`. It asserts local-file-only digest packaging,
manual `.eml` review boundaries, and local observed source-set review language.

## Files To Review

- `tests/test_daily_digest_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-90-daily-digest-docs-boundary-design.md`
- `docs/superpowers/plans/2026-06-18-stage-90-daily-digest-docs-boundary-plan.md`
- `docs/reviews/opencode-stage-90-plan-review-prompt.md`
- `docs/reviews/opencode-stage-90-plan-review.md`

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

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_daily_digest_docs.py -q
uv --no-config run --frozen pytest tests/test_digests.py tests/test_daily_digest_docs.py -q
uv --no-config run --frozen ruff check tests/test_daily_digest_docs.py
uv --no-config run --frozen ruff format --check tests/test_daily_digest_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 90 plan and scope?
2. Are the docs assertions present, stable enough, and limited to local digest
   boundaries?
3. Is the new standalone test independent from runtime digest behavior tests
   and broad CLI docs tests?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
