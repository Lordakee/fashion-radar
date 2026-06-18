# Stage 109 Code Review Prompt

Review the Stage 109 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 109 appends a docs drift guard to `tests/test_source_boundaries_docs.py`,
scoped to the `## Quality Boundaries` section in `docs/source-boundaries.md`. It
asserts that quality-boundary guidance remains explicit about heat scores being
local metrics, candidate signals needing review rather than validation, and the
dashboard showing a small set of local diagnostic fields.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-109-source-boundaries-quality-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-109-source-boundaries-quality-docs-plan.md`
- `docs/reviews/opencode-stage-109-plan-review-prompt.md`
- `docs/reviews/opencode-stage-109-plan-review.md`
- `docs/reviews/opencode-stage-109-code-review-prompt.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 109 review artifacts

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
- `tests/test_cli_docs.py`
- dashboard, report, collector, source acquisition, storage schema, database, or
  CLI runtime behavior
- connectors, scraping, browser automation, platform APIs, monitoring,
  scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py tests/test_dashboard_docs.py tests/test_reports.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 109 plan and remain scoped to a
   docs-only drift guard?
2. Are the asserted phrases appropriate for the `## Quality Boundaries`
   section, given existing overlap with scoring, candidate discovery, dashboard,
   and report tests?
3. Does the implementation fit the existing `tests/test_source_boundaries_docs.py`
   pattern cleanly?
4. Are there any Critical or Important issues to fix before commit?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
