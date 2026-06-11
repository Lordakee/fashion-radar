# Claude Code Stage 6 Plan Rereview Prompt

You are Claude Code rereviewing the Stage 6 plan for Fashion Radar after fixing
the Important findings from `docs/reviews/claude-code-stage-6-plan-review.md`.

Repository: `/home/ubuntu/fashion-radar`

Current base:

- `3d97313 feat: add stage 5 cli and dashboard workflow`
- plus uncommitted Stage 6 plan-review records and plan updates only

Please review only whether the Stage 6 plan is now ready to implement. The
implementation should not begin until this is approved.

Fixes applied to the Stage 6 plan:

- Added a reference to the Stage 6 plan review and required Critical/Important
  plan findings to be fixed before Stage 6 docs/package changes.
- CI/package contract now explicitly requires installed-wheel verification of
  `fashion_radar.templates/daily_report.md`, either via report smoke or
  `importlib.resources`.
- CI/package contract now explicitly requires resolving/installing the optional
  `dashboard` extra and importing `fashion_radar.dashboard.app` and
  `fashion_radar.dashboard.queries` without launching Streamlit.
- Planned files now reuse existing `docs/REVIEW_PROTOCOL.md` and
  `docs/dependency-mirrors.md` rather than creating conflicting duplicate docs.
- Tasks now say update README/source-boundaries/review workflow where docs
  already exist.
- Hygiene task now includes `AGENTS.md`, `.mcp.json`,
  `.claude/settings.json`, and `.codegraph/.gitignore`.
- Scoring known limits now include omitted zero-current entities and the
  redundant stable fallback.

Please answer:

1. Are the previous Important findings fixed in the plan?
2. Are there any remaining blockers before Stage 6 implementation?
3. Is the plan still safely scoped to docs/CI/GitHub readiness and not social
   scraping implementation?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 6 implementation
- Approved after fixes
- Do not proceed
