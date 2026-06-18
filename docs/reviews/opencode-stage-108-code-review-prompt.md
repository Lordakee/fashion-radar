# Stage 108 Code Review Prompt

Review the Stage 108 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 108 appends a docs drift guard to `tests/test_source_boundaries_docs.py`,
scoped to the `## Output Boundaries` section in `docs/source-boundaries.md`. It
asserts that output wording guidance remains explicit about describing signals
rather than certainty, section-specific safe wording examples, and avoiding
explicit demand-proof or celebrity-causation claims.

## Files To Review

- `tests/test_source_boundaries_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-108-source-boundaries-output-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-108-source-boundaries-output-docs-plan.md`
- `docs/reviews/opencode-stage-108-plan-review-prompt.md`
- `docs/reviews/opencode-stage-108-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 108 review artifacts

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
- dashboard, report, collector, robots/fetching, storage schema, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py -q
uv --no-config run --frozen pytest tests/test_source_boundaries_docs.py tests/test_cli_docs.py tests/test_trend_deltas_docs.py tests/test_scoring_docs.py tests/test_candidate_discovery_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_boundaries_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_boundaries_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 108 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/source-boundaries.md` `## Output Boundaries` section?
3. Is appending to `tests/test_source_boundaries_docs.py` clean and consistent
   with the existing helper pattern?
4. Is the new guard independent from full negative-claim scanning, heat movers,
   trend deltas, scoring, candidate discovery, dashboard/report behavior,
   package archive checks, and runtime code?
5. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
