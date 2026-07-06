You are reviewing the Stage 309 implementation plan for the `fashion-radar` repo.

Repo: `/home/ubuntu/fashion-radar`
Plan file: `docs/superpowers/plans/2026-07-05-stage-309-row-one-newsroom-digest-polish-plan.md`

Context:
- The project is building ROW ONE, a daily local fashion intelligence static website.
- The current user priority is better content organization: saved local article content should be organized on the site, not just linked out.
- Stage 308 already added generated-site integrity validation.
- Stage 309 should polish the existing Daily Local Intelligence/newsroom digest:
  - cluster duplicate saved local-article cards in `strongest_reads` and `heat_movers`;
  - make paragraph evidence links read like reader-facing evidence/source links;
  - add compact source/extraction/published/count provenance to local article detail pages.
- Do not add compliance-review product features.
- Do not add source collection, browser automation, external API calls, network probes, LLM calls, image generation, or translation services.
- Do not change matching, ranking, scoring, sorting, story IDs, detail routes, paragraph anchors, `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, `data/edition.json`, or JSON schemas.
- Dependencies and lockfile should remain frozen; public `uv.lock` must not be rewritten to local mirror URLs.

Please review the plan for:
1. Feasibility and correctness against the current codebase.
2. Whether the scope is tight enough for one node.
3. Whether the clustering key is too broad, too narrow, unstable, or likely to collapse legitimate distinct stories.
4. Whether aggregate field semantics are correct and compatible with existing `RowOneDailyLocalIntelligenceItem` consumers.
5. Whether template changes preserve escaping, safe URL handling, hrefs, and paragraph anchors.
6. Whether tests are sufficient without becoming brittle against harmless copy/layout changes.
7. Whether docs language correctly describes presentation/sidecar-only polish and no app/schema contract change.
8. Whether generated sample site refresh and verification commands are appropriate.

Return findings in this format:

## Verdict
Approve, Approve with Important fixes, or Reject.

## Critical Findings
- File/step reference, issue, why it matters, concrete fix.

## Important Findings
- File/step reference, issue, why it matters, concrete fix.

## Minor Findings
- File/step reference, issue, why it matters, concrete fix.

## Suggested Plan Adjustments
- Concrete edits to the plan if needed.

Do not modify files.
