# Stage 105 Code Review Prompt

Review the Stage 105 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 105 adds `tests/test_trend_deltas_docs.py`, a standalone docs drift guard
for the `## What Is Compared` section in `docs/trend-deltas.md`. It asserts that
trend-delta comparison guidance keeps explicit wording about entity deltas
reusing local heat scoring, candidate deltas reusing candidate discovery
snapshots and configured thresholds, mention fields comparing current-window
counts across snapshots, internal baseline-window counts remaining separate,
and statuses being local observed review signals rather than market-wide
rankings.

## Files To Review

- `tests/test_trend_deltas_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-105-trend-deltas-what-compared-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-105-trend-deltas-what-compared-docs-plan.md`
- `docs/reviews/opencode-stage-105-plan-review-prompt.md`
- `docs/reviews/opencode-stage-105-plan-review.md`

## Scope Constraints

Allowed changes:

- `tests/test_trend_deltas_docs.py`
- Stage 105 review artifacts

Disallowed changes:

- `docs/trend-deltas.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- package metadata, archive tests, release-hygiene behavior, or `.gitignore`
- `tests/test_cli_docs.py`
- scoring, candidate discovery, heat movers, dashboard, report, database, or
  CLI runtime behavior
- source acquisition, connectors, scraping, browser automation, platform APIs,
  monitoring, scheduling, ranking, demand proof, coverage verification,
  account/cookie/session/proxy/CAPTCHA/paywall behavior, or compliance/audit/
  legal review product features

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_trend_deltas_docs.py -q
uv --no-config run --frozen pytest tests/test_trend_deltas_docs.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_trend_deltas_docs.py
uv --no-config run --frozen ruff format --check tests/test_trend_deltas_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 105 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/trend-deltas.md` `## What Is Compared` section?
3. Is the new standalone test independent from CLI usage, manual signal,
   dashboard, scoring implementation, and candidate discovery runtime behavior?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
