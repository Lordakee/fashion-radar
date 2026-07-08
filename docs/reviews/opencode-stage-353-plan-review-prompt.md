# OpenCode Stage 353 Plan Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review the Stage 353 Saved Article Read Next Clusters plan before
implementation.

## Scope

Stage 353 adds a generated-site-only read-next cluster section in
`articles/index.html`. The clusters must reuse existing saved article library
entries, content organization cards, local leads, references, and safe local
article/detail anchors. It must not add new persisted artifacts, routes,
schemas, app contracts, scraping, extraction, ranking, LLM calls, scheduling,
deployment, analytics, personalization, recommendation, or compliance-review
product behavior.

## Review Inputs

- `docs/superpowers/specs/2026-07-08-stage-353-saved-article-read-next-clusters-design.md`
- `docs/superpowers/plans/2026-07-08-stage-353-saved-article-read-next-clusters-plan.md`

## Expected Output

List blocking or non-blocking findings with exact file references. Focus on:

- generated-site-only boundary drift;
- unsafe href handling;
- accidental ranking/recommendation behavior;
- overlap with reading queue, reading paths, theme digest, signal facets, or
  evidence board;
- missing tests for caps, order, dedupe, render placement, escaping,
  homepage/detail absence, and artifact denial.

If the plan is sound, state that it is approved for implementation.
