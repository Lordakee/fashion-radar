# Claude Code Plan Review Request — Stage 321 ROW ONE Editorial Brief

Please review the Stage 321 spec and implementation plan before implementation.

## Files

- `docs/superpowers/specs/2026-07-07-stage-321-row-one-editorial-brief-design.md`
- `docs/superpowers/plans/2026-07-07-stage-321-row-one-editorial-brief-plan.md`

## Goal

Add a generated-site-only ROW ONE homepage `Editorial Brief / 编辑正文` section that organizes existing saved local article and story data into short bilingual editorial paragraphs. The goal is to improve local information organization on the generated website, not to change app payloads or collect/fetch new data.

## Required Boundaries

- HTML-only generated-site feature.
- No `data/edition.json` field additions.
- No change to `row-one-app/v7`, `row-one-manifest/v1`, or `row-one-runtime/v1`.
- No schema changes.
- No new JSON artifact.
- No source collection, fetching, extraction, scoring, LLM, connector, image generation, deployment, or compliance-review behavior changes.
- Use existing saved local article sidecars, story text, detail routes, and paragraph anchors.

## Review Questions

1. Is the feature scope appropriate for Stage 321 and aligned with the user goal of “整理信息，而不是只是链接”?
2. Is the plan technically feasible in the current codebase?
3. Are the file boundaries correct, especially the generated-site-only JSON contract boundary?
4. Are tests sufficient to catch rendering, omission, escaping, safe href, ordering, workflow JSON, docs, and CSS regressions?
5. Does the plan contain any ambiguity, placeholder work, or risky overreach?

Please return:

- Critical findings
- Important findings
- Minor findings
- Final recommendation: approve / approve with changes / reject
