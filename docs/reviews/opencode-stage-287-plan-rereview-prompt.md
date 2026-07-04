# Stage 287 Plan Rereview Prompt (opencode fallback)

You are rereviewing the corrected Stage 287 implementation plan for Fashion Radar / ROW ONE.

## Objective

Stage 287 should add a deterministic ROW ONE `signal_synthesis` layer so app clients and the homepage can show local observed brand, product, designer, and person signals that need review, instead of only showing story links/cards.

## Plan Under Rereview

`docs/superpowers/plans/2026-07-04-stage-287-row-one-signal-synthesis-plan.md`

## Prior Review Context

The prior opencode review found blocking issues around:

1. `boundaries` appearing in the proposed shape but missing from schema/helper/tests.
2. Entity grouping diverging from the shipped `daily_digest.briefing_topics` normalizer.
3. Missing explicit `row-one-app/v5` -> `row-one-app/v6` literal update coverage.
4. Underspecified schema constraints and drift tests.
5. Missing local-observed/review-required wording guards.

The plan has been revised to address those issues. This rereview should focus on whether any Critical or Important blockers remain before implementation starts.

## Constraints

- Read-only review. Do not edit files.
- Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.
- Do not propose collectors, new social-platform integrations, LLM calls, image generation, new dependencies, compliance-review product features, scheduler changes, server/deployment changes, or scoring/ranking/story-ID changes.
- Evaluate whether the corrected plan correctly bumps to `row-one-app/v6` for the new required top-level app field.
- Verify that `signal_synthesis.groups` derives from `briefing_topics_payload(stories)` and therefore shares existing entity/product/designer/person normalization.
- Verify that `boundaries` is included in the shape, helper, schema, and tests.
- Verify local-observed / review-required wording boundaries and no market-demand/platform-coverage claims.

## Output Format

Return exactly these sections:

- Verdict
- Critical Findings
- Important Findings
- Minor Findings
- Recommended Plan Changes

For each Critical or Important finding, include the file/plan section, why it matters, and the smallest fix. If there are no Critical or Important findings, say so explicitly.
