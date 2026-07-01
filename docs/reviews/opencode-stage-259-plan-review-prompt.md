Review and revise the Stage 259 release-finalization docs plan after Claude
Code's plan review.

Repository: /home/ubuntu/fashion-radar

Read:
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/superpowers/plans/2026-07-01-stage-259-release-finalization-docs-plan.md
- docs/reviews/claude-code-stage-259-plan-review.md
- current git diff

Context:
- Stage 258 is already pushed and the repo is clean at
  `076db8c Stage 258: align HTML report artifact hygiene`.
- The user asked to continue with release finalization.
- This plan should stay docs/test/review only and should not add runtime
  behavior, collectors, scraping, platform APIs, dependencies, or tag creation.

Task:
- Confirm whether the plan is acceptable after Claude Code review.
- Incorporate any valid Critical or Important Claude Code concerns.
- Flag any additional Critical or Important planning issues.
- Keep scope limited to release-facing docs consistency, changelog freshness,
  docs guards, and release gate/review artifacts.

Return:
- Verdict.
- Required plan changes before implementation, if any.
- Optional nits.
