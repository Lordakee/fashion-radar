# Stage 103 Plan Review Prompt

Review the Stage 103 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Add a standalone docs drift guard for `docs/PROJECT_BRIEF.md`, scoped only to
the `## Non-Goals For MVP` section, so the MVP remains documented as free-first,
local-first, deterministic, and not dependent on paid APIs, account/proxy pools,
high-frequency scraping, private data, full-platform social coverage claims, LLM
dependency, or default connectors requiring login cookies, CAPTCHA bypass, or
paywall bypass.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-103-project-brief-non-goals-design.md`
- `docs/superpowers/plans/2026-06-18-stage-103-project-brief-non-goals-plan.md`
- `docs/PROJECT_BRIEF.md`

## Planned Test

The implementation will add `tests/test_project_brief_docs.py` with one
docs-only test that extracts `## Non-Goals For MVP` and asserts:

- `No paid API requirement.`
- `No account pool.`
- `No proxy pool.`
- `No high-frequency scraping.`
- `No automated posting.`
- `No private user data collection.`
- `No claim that the tool provides full-platform Instagram, TikTok, X, or Xiaohongshu coverage.`
- `No LLM dependency in the first core pipeline. The first version should work with deterministic extraction and scoring. Optional LLM summarization can be added later.`
- `No default connector that needs login cookies, proxy pools, CAPTCHA bypass, or paywall bypass.`

## Scope Constraints

Allowed changes:

- `tests/test_project_brief_docs.py`
- Stage 103 review artifacts

Disallowed changes:

- `docs/PROJECT_BRIEF.md`
- `src/`
- `scripts/`
- `examples/`
- configs
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime source acquisition, connector, scraping, browser automation, account,
  cookie, session, proxy, CAPTCHA, paywall, social platform, scoring, dashboard,
  report, or CLI tests
- scoring, first-run, source-pack, entity-pack, scheduling, dashboard,
  manual-import, candidate-discovery, community-signal, trend-delta, or security
  docs guards

Do not expand this stage into connector behavior, platform search, social
monitoring, scraping automation, browser/account/proxy/CAPTCHA/paywall flows,
generated data, scoring algorithm changes, dashboard/report behavior,
compliance/audit/legal review product features, or runtime validation.

This guard must not claim that future opt-in social/community/external-tool
integrations are prohibited; it only pins MVP non-goals.

## Review Questions

1. Does the plan protect a real `docs/PROJECT_BRIEF.md` MVP non-goals boundary
   without changing product behavior?
2. Are the planned phrases present in `docs/PROJECT_BRIEF.md` and scoped
   narrowly enough to `## Non-Goals For MVP`?
3. Does the plan avoid over-pinning `## Free-First Boundary`,
   `## Recommended First Public Version`, current connector docs, and future
   opt-in social/community/external-tool expansion?
4. Are the verification commands sufficient for a docs-only guard?

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
