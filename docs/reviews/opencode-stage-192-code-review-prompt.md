Review Stage 192 code changes in /home/ubuntu/fashion-radar.

Scope:
- Daily Brief source caveat error fragments are capped with the existing
  report-safe snippet policy.
- Daily Brief source-caveats de-duplicate failed recent-run caveats when a
  source-health caveat already represents the same source.
- Per-section empty Markdown fallback is clearer while the global all-empty
  fallback remains unchanged.
- docs/reviews/opencode-full-project-review.md follow-up status is updated to
  reflect completed Stages 188-191.

Files expected in scope:
- src/fashion_radar/reports.py
- tests/test_reports.py
- tests/test_review_protocol_docs.py
- docs/reviews/opencode-full-project-review.md
- CHANGELOG.md
- docs/superpowers/specs/2026-06-24-stage-192-daily-brief-caveat-polish-review-status-design.md
- docs/superpowers/plans/2026-06-24-stage-192-daily-brief-caveat-polish-review-status-plan.md
- docs/reviews/opencode-stage-192-plan-review.md
- docs/reviews/opencode-stage-192-plan-rereview.md

Verify:
1. No public report model shape changes.
2. No new CLI command, source acquisition, platform/social connector,
   monitoring, scheduling, demand proof, coverage verification, compliance
   review feature, LLM summarization, or trend/heat/dashboard contract change.
3. Tests cover the old failure modes and the intended new behavior.
4. Review artifacts are clean and coherent.
5. The implementation follows the Stage 192 spec/plan and does not overbuild.

Return:
- Critical
- Important
- Minor
- Verdict
