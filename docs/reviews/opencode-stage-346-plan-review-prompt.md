# OpenCode Stage 346 Plan Review Prompt

Review a planned development node in `/home/ubuntu/fashion-radar` using model
`zhipuai-coding-plan/glm-5.2 --variant max`. Operate read-only. Do not edit
files.

## Goal

Stage 346 will add a generated-site-only Saved Article Body Guide inside saved
article cards on `articles/index.html`.

## Design And Plan

Review these files:

- `docs/superpowers/specs/2026-07-08-stage-346-saved-article-body-guide-design.md`
- `docs/superpowers/plans/2026-07-08-stage-346-saved-article-body-guide-plan.md`

## Intended Scope

- Use existing saved article library and content-organization data only.
- Render concise per-card body-guide bullets with safe local paragraph links.
- Keep changes generated-site-only and out of app-facing contracts.
- Avoid new JSON artifacts, schemas, routes, fetchers, extraction behavior,
  ranking, LLM summaries, scheduling, deployment, or compliance-review product
  features.
- Avoid duplicating existing top-level modules.

## Review Questions

1. Is the implementation plan technically reasonable for the current codebase?
2. Are the planned tests enough to catch unsafe links, escaping failures,
   duplicate guide content, overlong excerpts, empty shells, and contract drift?
3. Does the plan accidentally introduce new data/product scope?
4. Should anything be corrected before implementation?

Return a concise severity-labeled review. If no Critical or Important issues
exist, approve implementation.
