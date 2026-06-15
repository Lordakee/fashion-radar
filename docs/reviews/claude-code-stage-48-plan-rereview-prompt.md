You are Claude Code rereviewing the Stage 48 plan for /home/ubuntu/fashion-radar.

Use maximum reasoning. Do not modify files. Do not browse the network.

Files to review:
- docs/superpowers/specs/2026-06-15-stage-48-installed-wheel-first-run-smoke-design.md
- docs/superpowers/plans/2026-06-15-stage-48-installed-wheel-first-run-smoke-plan.md
- docs/reviews/claude-code-stage-48-plan-review.md

Prior Important finding to verify:
- Installed mode could still be source-contaminated via inherited PYTHONPATH.
  The plan previously preserved unrelated PYTHONPATH and did not explicitly
  remove/fail on repo_root/src or preflight import origin.

Plan changes made:
- Spec now requires installed mode to remove inherited repo_root/src from
  PYTHONPATH before running commands.
- Spec now requires an installed-mode import-origin preflight using the target
  Python and failing if `fashion_radar.__file__` resolves inside repo_root/src.
- Plan now adds tests for removing repo src from PYTHONPATH in installed mode.
- Plan now adds `remove_pythonpath_entry()`.
- Plan now adds `assert_installed_import_origin()` and `installed_import_origin()`.
- Plan now calls the import-origin preflight before `run_smoke(context)` in
  installed mode.
- Plan updates run_cli tests to cover source-contamination removal.

Please verify whether the prior Important finding is resolved and whether any
new Critical or Important blockers remain. If the plan is ready, include exactly:

APPROVED FOR STAGE 48 INSTALLED-WHEEL FIRST-RUN SMOKE
