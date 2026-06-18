# Stage 103 Code Review Prompt

Review the Stage 103 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 103 adds `tests/test_project_brief_docs.py`, a standalone docs drift guard
for the `## Non-Goals For MVP` section in `docs/PROJECT_BRIEF.md`. It asserts
that the MVP remains documented as having no paid API requirement, no account or
proxy pool, no high-frequency scraping, no automated posting, no private user
data collection, no full-platform social coverage claim, no required LLM in the
first core pipeline, and no default connector that needs login cookies, proxy
pools, CAPTCHA bypass, or paywall bypass.

## Files To Review

- `tests/test_project_brief_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-103-project-brief-non-goals-design.md`
- `docs/superpowers/plans/2026-06-18-stage-103-project-brief-non-goals-plan.md`
- `docs/reviews/opencode-stage-103-plan-review-prompt.md`
- `docs/reviews/opencode-stage-103-plan-review.md`

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

Do not propose connector behavior, platform search, social monitoring, scraping
automation, browser/account/proxy/CAPTCHA/paywall flows, generated data, scoring
algorithm changes, dashboard/report behavior, compliance/audit/legal review
product features, or runtime validation.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_project_brief_docs.py -q
uv --no-config run --frozen pytest tests/test_project_brief_docs.py tests/test_scoring_docs.py tests/test_architecture_boundary_docs.py tests/test_source_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_project_brief_docs.py
uv --no-config run --frozen ruff format --check tests/test_project_brief_docs.py
git diff --check
```

## Review Questions

1. Does the implementation match the Stage 103 plan and scope?
2. Are the docs assertions present, stable enough, and limited to the
   `docs/PROJECT_BRIEF.md` `## Non-Goals For MVP` section?
3. Is the new standalone test independent from broad CLI docs tests, source
   boundary tests, and runtime source/connector/scoring behavior?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If there
are no Critical or Important blockers, say that explicitly.
