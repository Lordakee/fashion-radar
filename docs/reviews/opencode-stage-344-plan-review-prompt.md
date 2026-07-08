# opencode Stage 344 Plan Review Prompt

Review `/home/ubuntu/fashion-radar` read-only using model
`zhipuai-coding-plan/glm-5.2` with max reasoning.

## Files

- `docs/superpowers/specs/2026-07-08-stage-344-saved-article-organization-coverage-matrix-design.md`
- `docs/superpowers/plans/2026-07-08-stage-344-saved-article-organization-coverage-matrix-plan.md`

## Objective

Stage 344 adds a generated-site-only Saved Article Organization Coverage Matrix
inside `articles/index.html`, built only from existing saved article content
organization groups/cards. It must not add new schemas, JSON artifacts, route
families, source collection, scraping, ranking, recommendation, deployment, or
compliance-review behavior.

## Requested Review

Assess plan feasibility, technical correctness, likely implementation conflicts,
test adequacy, and whether the next project direction is reasonable. Return
severity-labeled findings only. If acceptable, say the plan is ready for
implementation.
