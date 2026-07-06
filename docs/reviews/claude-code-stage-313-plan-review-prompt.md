# Claude Code Stage 313 Plan Review Prompt

You are the primary local Claude Code reviewer for Fashion Radar Stage 313.
Use maximum reasoning. Review the Stage 313 design and implementation plan
before coding begins.

## Files To Review

- `docs/superpowers/specs/2026-07-06-stage-313-row-one-saved-article-briefs-design.md`
- `docs/superpowers/plans/2026-07-06-stage-313-row-one-saved-article-briefs-plan.md`
- Relevant current context:
  - `src/fashion_radar/row_one/models.py`
  - `src/fashion_radar/row_one/render.py`
  - `src/fashion_radar/row_one/templates.py`
  - `src/fashion_radar/row_one/local_intelligence.py`
  - `src/fashion_radar/row_one/saved_article_coverage.py`
  - `tests/test_row_one_render.py`
  - `tests/test_row_one_docs.py`

## Stage Goal

Add a generated-site-only ROW ONE homepage `Saved Article Briefs / 保存正文简报`
section that surfaces readable takeaways and reference chips from
current-edition saved local article sidecars.

## Required Boundaries

- Use existing `data/articles/<story-id>.json` sidecars only.
- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not write a new JSON artifact.
- Do not change schemas, story IDs, detail routes, or paragraph anchors.
- Do not add source collection, scraping, scoring, LLM calls, scheduling,
  platform/social/community connectors, or compliance-review product features.

## Requested Review

Check the plan for:

- feasibility against current code;
- missing tests or weak tests;
- contract/schema/runtime/manifest drift risk;
- unsafe href or escaping risk;
- duplicated work with Daily Local Intelligence or Saved Article Coverage;
- overreach beyond the stage boundaries;
- implementation details that are likely to fail ruff, pytest, or existing
  Pydantic model constraints.

Return findings first, ordered by severity:

- Critical: plan would break required contracts, schemas, routes, artifacts, or
  user-visible correctness.
- Important: likely implementation bugs, missing required tests, unclear steps,
  or plan details that should be fixed before coding.
- Minor: polish or low-risk improvements.

For each finding, include exact file and line references. If no Critical or
Important findings exist, say that clearly and mention residual risks.
