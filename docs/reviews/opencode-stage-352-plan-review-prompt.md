# OpenCode Stage 352 Plan Review Prompt

Use model `glm-5.2` to review the Stage 352 Saved Article Reading Queue plan
before implementation.

## Scope

Stage 352 adds a generated-site-only reading queue in `articles/index.html`.
The queue must reuse existing saved article library entries and safe local
article/detail anchors. It must not add new persisted artifacts, routes,
schemas, app contracts, scraping, extraction, ranking, LLM calls, scheduling,
deployment, analytics, personalization, recommendation, or compliance-review
product behavior.

## Review Inputs

- `docs/superpowers/specs/2026-07-08-stage-352-saved-article-reading-queue-design.md`
- `docs/superpowers/plans/2026-07-08-stage-352-saved-article-reading-queue-plan.md`

## Expected Output

List blocking or non-blocking findings with exact file references. Focus on:

- generated-site-only boundary drift;
- unsafe href handling;
- accidental ranking/recommendation behavior;
- overlap with prior reading-path/reading-improvement features;
- missing tests for render placement, escaping, homepage/detail absence, and
  artifact denial.

If the plan is sound, state that it is approved for implementation.
