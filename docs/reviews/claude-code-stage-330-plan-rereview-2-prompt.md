Re-review the Stage 330 plan after fixing the previous Critical blocker.

Files:
- docs/superpowers/specs/2026-07-07-stage-330-row-one-refresh-data-retention-design.md
- docs/superpowers/plans/2026-07-07-stage-330-row-one-refresh-data-retention-plan.md
- docs/reviews/claude-code-stage-330-plan-rereview.md

Verify:
- The real SQLite integration test now actually monkeypatches collect/match/report/site helpers while leaving `clean_old_data` real.
- The skip flag plan avoids the `--no-skip-data-retention` double-negative.
- The plan requires adding/updating cli-reference coverage for `row-one refresh`.
- No new Critical or Important blocker remains.

Return concise complete sections: Critical, Important, Medium, Minor, Verdict.
If there are no findings for a severity, write `None`.
Do not edit files.
