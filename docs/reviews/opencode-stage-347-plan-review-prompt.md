# OpenCode Stage 347 Plan Review Prompt

Review a planned development node in `/home/ubuntu/fashion-radar` using model
`zhipuai-coding-plan/glm-5.2 --variant max`. Operate read-only. Do not edit
files.

## Goal

Stage 347 adds a generated-site-only Saved Article Source Brief to each source
group in `articles/index.html`, plus a small saved article coverage story-id
parity guard.

## Design And Plan

Review these files:

- `docs/superpowers/specs/2026-07-08-stage-347-saved-article-source-brief-design.md`
- `docs/superpowers/plans/2026-07-08-stage-347-saved-article-source-brief-plan.md`

## Intended Scope

- Reuse existing saved article library/source/content organization data only.
- Render source-level contribution context before each source card grid.
- Keep changes generated-site-only and out of app-facing contracts.
- Avoid new JSON artifacts, schemas, routes, fetchers, extraction behavior,
  ranking, LLM summaries, scheduling, deployment, or compliance-review product
  features.

## Review Questions

1. Is the plan technically reasonable for the current codebase?
2. Are planned tests enough to catch unsafe links, escaping failures, duplicate
   source bullets, overlong excerpts, empty shells, story-id mismatches, and
   contract drift?
3. Does the plan accidentally introduce ranking/source-quality/product scope?
4. Should anything be corrected before implementation?

Return a concise severity-labeled review. If no Critical or Important issues
exist, approve implementation.
