# Claude Code Stage 307 Plan Review Prompt

You are reviewing the Stage 307 implementation plan for `/home/ubuntu/fashion-radar` before implementation.

Required review mode:
- Read-only plan review.
- Do not edit files, stage changes, commit, or push.
- Review the plan against the current repository state.

Base SHA: `f774eff`
Current branch: `main`
Plan under review:
- `docs/superpowers/plans/2026-07-05-stage-307-row-one-local-evidence-drilldowns-plan.md`

Stage 307 objective:
- Let ROW ONE homepage Daily Local Intelligence cards link directly to exact saved local article paragraph evidence.
- Keep `row-one-app/v7`, sidecar JSON shapes, local article models, and detail-page rendering unchanged.
- Fix aggregate local-intelligence detail-path/source alignment before rendering exact paragraph links.
- Replace full-card anchors with explicit same-site saved-text and paragraph links so no nested anchors are introduced.
- Expand safe local fragment validation only for generated `#local-article-paragraph-N` anchors.
- Keep scope limited to local article intelligence organization, renderer links, docs/tests, and review artifacts.
- Do not add collectors, platform integrations, LLM/image calls, scheduler/server changes, dependency changes, schema/app contract bumps, sidecar schemas, visual redesign, or compliance-review product features.

Known audit inputs that informed the plan:
- Homepage Daily Local Intelligence currently links cards only to `#local-article`, not exact paragraph evidence.
- `_render_daily_local_intelligence_item` currently wraps the whole card in an anchor, so paragraph links require markup restructuring.
- Reference aggregates can upgrade body/segments/paragraph indices from a later article while leaving `detail_path` pinned to the first aggregate story.
- `data/local-intelligence.json` is written when populated but is under-documented.
- Public `uv.lock` must not be rewritten to mirror registry URLs.

Please review for:
1. Whether the plan is technically feasible against current code.
2. Whether the red/green tests are specific enough and likely to fail/pass for the intended behavior.
3. Whether any proposed helper/API shape is incompatible with current renderer/local-intelligence code.
4. Whether the plan preserves app contract/schema boundaries and avoids out-of-scope functionality.
5. Whether implementation order is safe and minimizes nested-anchor, unsafe-fragment, or wrong-article-link regressions.
6. Whether verification is sufficient before commit/push.

Return only structured markdown with:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required plan changes before implementation

End with the exact line: REVIEW_COMPLETE
