# OpenCode Stage 351 Plan Review Prompt

Use model `glm-5.2` to review the Stage 351 Saved Article Organization Jump
Index plan before implementation.

## Scope

Stage 351 adds a generated-site-only section in `articles/index.html`. The
section is a compact navigation index over existing local saved article
surfaces. It must not add new persisted artifacts, routes, schemas, app
contracts, scraping, extraction, ranking, LLM calls, scheduling, deployment,
analytics, personalization, recommendation, or compliance-review product
behavior.

## Review Inputs

- `docs/superpowers/specs/2026-07-08-stage-351-saved-article-organization-jump-index-design.md`
- `docs/superpowers/plans/2026-07-08-stage-351-saved-article-organization-jump-index-plan.md`

## Expected Output

List blocking or non-blocking findings with exact file references. Focus on:

- generated-site-only boundary drift;
- duplicated summary/ranking behavior;
- unsafe or non-existing href anchors;
- accidental use of a non-existent aggregate source-route anchor instead of the
  existing per-source `#saved-article-source-*` anchors;
- missing tests for render placement, escaping, homepage absence, and artifact
  denial;
- documentation boundary gaps.

If the plan is sound, state that it is approved for implementation.
