# Claude Code Stage 307 Plan Rereview Prompt

You are rereviewing the revised Stage 307 implementation plan for `/home/ubuntu/fashion-radar` before implementation.

Required review mode:
- Read-only plan rereview.
- Do not edit files, stage changes, commit, or push.
- Review the revised plan against the current repository state and the prior review findings.

Base SHA: `f774eff`
Plan under review:
- `docs/superpowers/plans/2026-07-05-stage-307-row-one-local-evidence-drilldowns-plan.md`

Prior plan review:
- `docs/reviews/claude-code-stage-307-plan-review.md`

Prior review findings that should now be addressed:
1. Add minimal CSS rules for new `.daily-local-intelligence-actions`, `.daily-local-intelligence-action`, and `.daily-local-intelligence-paragraph-link` classes, or explicitly test the CSS class presence.
2. Simplify `_daily_local_intelligence_paragraph_href()` so it does not re-run `_safe_daily_local_intelligence_href()` on an already validated `detail_href`.
3. Name the exact docs test target for docs drift assertions.
4. Include the existing `test_render_row_one_site_escapes_daily_local_intelligence` regression after the renderer refactor.

Stage 307 objective remains:
- Let ROW ONE homepage Daily Local Intelligence cards link directly to exact saved local article paragraph evidence.
- Keep `row-one-app/v7`, sidecar JSON shapes, local article models, and detail-page rendering unchanged.
- Fix aggregate local-intelligence detail-path/source alignment before rendering exact paragraph links.
- Replace full-card anchors with explicit same-site saved-text and paragraph links so no nested anchors are introduced.
- Expand safe local fragment validation only for generated `#local-article-paragraph-N` anchors.
- Keep scope limited to local article intelligence organization, renderer links, docs/tests, and review artifacts.
- Do not add collectors, platform integrations, LLM/image calls, scheduler/server changes, dependency changes, schema/app contract bumps, sidecar schemas, visual redesign, or compliance-review product features.

Please review for:
- Whether all prior Critical/Important/clear Minor notes are resolved.
- Whether the revised plan is technically feasible against current code.
- Whether any remaining issue must be fixed before implementation.

Return only structured markdown with:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required plan changes before implementation

End with the exact line: REVIEW_COMPLETE
