# Stage 110 Code Review Prompt

Review the Stage 110 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 110 appends a docs drift guard to `tests/test_source_boundaries_docs.py`,
scoped to the `## Robots And Fetching` section in `docs/source-boundaries.md`.
It asserts that robots/fetching guidance remains explicit about robots.txt
checks before article extraction, skipped URL reasons, source-specific rate
limits, and GDELT metadata/link storage and backoff boundaries.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-110-source-boundaries-robots-fetching-docs-plan.md`
- `docs/reviews/opencode-stage-110-plan-review-prompt.md`
- `docs/reviews/opencode-stage-110-plan-review.md`
- `docs/reviews/opencode-stage-110-code-review-prompt.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 110 review artifacts

Disallowed changes:

- `docs/source-boundaries.md`
- `README.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_collectors_robots.py`
- `tests/test_cli_docs.py`
- dashboard, report, collector, source acquisition, storage schema, database, or
  CLI runtime behavior
- HTTP client behavior, robots parser behavior, article extraction behavior,
  GDELT runtime behavior, connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_collectors_robots.py tests/test_collectors_article.py tests/test_collectors_runner.py tests/test_project_brief_docs.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 110 plan and remain scoped to a
   docs-only drift guard?
2. Are the asserted phrases appropriate for the `## Robots And Fetching`
   section, given existing overlap with collector runtime and HTTP/robots tests?
3. Does the implementation fit the existing `tests/test_source_boundaries_docs.py`
   pattern cleanly?
4. Are there any Critical or Important issues to fix before commit?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
