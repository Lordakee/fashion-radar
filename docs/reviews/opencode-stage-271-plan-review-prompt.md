# Stage 271 Plan Review Request

Please review the Stage 271 design and implementation plan in `/home/ubuntu/fashion-radar`.

## Files To Review
- `docs/superpowers/specs/2026-07-03-stage-271-row-one-app-content-organization-design.md`
- `docs/superpowers/plans/2026-07-03-stage-271-row-one-app-content-organization-plan.md`

## Goal
Stage 271 should make ROW ONE app-facing content easier to render by adding structured content organization to `data/edition.json`: `content_sections`, story `detail_sections`, and story `evidence_summary`.

## Constraints
- Do not add new source collection, scraping, platform APIs, translation services, LLM calls, image generation, deployment, or timer installation.
- Keep the manifest contract `row-one-manifest/v1` stable and do not add `runtime_path` to manifest.
- The plan proposes bumping `row-one-app/v1` to `row-one-app/v2` while preserving `data/edition.json` and `schemas/row-one-app.schema.json` paths.
- This stage should address the product requirement that the tool organize information instead of only exposing links.

## Please Evaluate
1. Is the app contract strategy reasonable: version bump to `row-one-app/v2` vs sidecar file?
2. Are `content_sections`, cards, `detail_sections`, and `evidence_summary` sufficient and coherent for the app use case?
3. Are the implementation tasks specific enough and scoped to the right files?
4. Are there missing schema/test/doc requirements?
5. Are there any blockers before implementation?

Return:
- APPROVED or NOT APPROVED
- Findings ordered by severity with file/line references
- Required fixes before implementation
- Optional follow-ups
