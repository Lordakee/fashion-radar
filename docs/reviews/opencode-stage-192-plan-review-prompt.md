Review the Stage 192 plan for /home/ubuntu/fashion-radar.

Files to read:
- docs/superpowers/specs/2026-06-24-stage-192-daily-brief-caveat-polish-review-status-design.md
- docs/superpowers/plans/2026-06-24-stage-192-daily-brief-caveat-polish-review-status-plan.md
- docs/reviews/opencode-stage-191-code-review.md
- docs/reviews/opencode-stage-191-release-review.md
- docs/reviews/opencode-full-project-review.md
- AGENTS.md
- docs/REVIEW_PROTOCOL.md

Goal:
Stage 192 should resolve only the actionable Stage 191 Minor polish and stale
full-project review follow-up status before starting the next product node.

Architecture and tech stack:
- Python 3.11 report-layer changes in src/fashion_radar/reports.py.
- Existing Pydantic report models only; no public model-shape change.
- Existing report_safe_snippet policy for Daily Brief source-caveat error
  fragments.
- pytest TDD for report output and review-status docs.
- opencode review gate with zhipuai-coding-plan/glm-5.2 --variant max.

Implementation method:
- Write RED tests first for source-caveat error capping, duplicate recent-run
  suppression, per-section Markdown fallback, and full-project review follow-up
  status.
- Implement the smallest report-layer and docs/status changes.
- Run focused and broad verification.
- Request code and release reviews before commit/push.

Review questions:
1. Does this plan correctly interpret the Stage 191 code-review Minor findings?
2. Is the scope small enough, and does it avoid new product surfaces?
3. Are the RED tests meaningful and likely to fail on current code for the
   intended reasons?
4. Is using report_safe_snippet for Daily Brief caveat errors technically
   consistent with existing report safety behavior?
5. Is source-caveat de-duplication by casefolded `(source_name, source_type)`
   reasonable and deterministic?
6. Is updating only the `Current Follow-Up Status` section of the historical
   full-project review acceptable?
7. Are any Critical or Important issues blocking implementation?

Return:
- Critical
- Important
- Minor
- Verdict

End with one of: approved, approved with non-blocking minors, or not approved.
