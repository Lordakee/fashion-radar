You are Claude Code performing the required Stage 49 plan review for
/home/ubuntu/fashion-radar.

Use maximum reasoning. Do not browse the network. Do not modify files.

Stage 49 objective:
- Add a tested first-run onboarding guide and tighten public docs so new GitHub
  users can choose between source checkout smoke, installed-wheel smoke,
  manual repo-local sample output, dashboard inspection, and reset.

Proposed files:
- Add: docs/first-run.md
- Modify: README.md
- Modify: docs/cli-reference.md
- Modify: docs/github-upload-checklist.md
- Modify: tests/test_cli_docs.py
- Add: docs/reviews/claude-code-stage-49-release-review-prompt.md
- Add: docs/reviews/claude-code-stage-49-release-review.md

Design and implementation plan to review:
- docs/superpowers/specs/2026-06-16-stage-49-first-run-onboarding-guide-design.md
- docs/superpowers/plans/2026-06-16-stage-49-first-run-onboarding-guide-plan.md

Current baseline:
- Stage 48 commit is pushed on main.
- CI already runs source-checkout first-run smoke and installed-wheel first-run
  smoke.
- Stage 49 should not change runtime behavior or CI behavior.

Boundaries:
- Docs/tests only.
- No runtime code, dependency, lockfile, CI behavior, dashboard behavior,
  source/social connector, scraping/browser/account/session automation,
  external service, or compliance-review feature.
- Keep public uv.lock mirror-free.
- Use mirror only for local install verification where already part of the
  release checks.

Specific review questions:
1. Does the plan give a new GitHub user a clear and accurate first-run path?
2. Are the planned doc-drift tests strong enough without being too brittle?
3. Does the plan preserve the Stage 47/48 smoke contract exactly, including
   source-checkout and installed-wheel commands?
4. Are any planned reset commands risky or too broad for user-facing docs?
5. Does the plan accidentally imply platform/social scraping, account login,
   browser automation, connector work, external services, or compliance-review
   functionality?
6. Is the verification plan sufficient before commit/push?

Please return:
- Critical issues.
- Important issues.
- Minor issues.
- Whether any issue blocks implementation.
- If no Critical or Important issues remain, include exactly:
APPROVED FOR STAGE 49 IMPLEMENTATION
