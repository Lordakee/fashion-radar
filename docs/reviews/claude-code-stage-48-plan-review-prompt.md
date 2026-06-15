You are Claude Code reviewing the Stage 48 plan for /home/ubuntu/fashion-radar.

Use maximum reasoning. Do not modify files. Do not browse the network.

Goal:
- Add an installed-wheel mode to the deterministic first-run smoke so CI and
  release checks prove the built wheel can run the local sample flow.

Files to review:
- docs/superpowers/specs/2026-06-15-stage-48-installed-wheel-first-run-smoke-design.md
- docs/superpowers/plans/2026-06-15-stage-48-installed-wheel-first-run-smoke-plan.md

Key proposed approach:
- Extend scripts/check_first_run_smoke.py with `--installed`.
- Default source mode keeps prepending repo_root/src to PYTHONPATH.
- Installed mode uses the supplied installed Python environment and does not
  prepend repo_root/src.
- Keep cwd at repo root so checked-in example CSV remains available.
- Keep all runtime config/data/reports/exports under tempfile directories.
- Keep default repo data/reports hash guard in both modes.
- Wire installed smoke into the CI build/install step after wheel install.
- Update README and docs/github-upload-checklist.md with the installed-wheel
  smoke command.

Boundaries:
- No scraping, crawling, browser automation, account/cookie/session tooling,
  source acquisition, platform connectors, live collect, dashboard server
  launch, scheduler, monitor, or external services.
- No compliance-review feature.
- No dependency/lockfile/schema/scoring/entity/source config behavior change.

Please review for:
- correctness of installed-vs-source environment handling;
- whether the installed-wheel smoke truly proves the packaged CLI path;
- CI command placement and docs consistency;
- test coverage adequacy;
- release risk or missing verification.

Return Critical, Important, and Minor findings. If there are no Critical or
Important blockers, include exactly:

APPROVED FOR STAGE 48 INSTALLED-WHEEL FIRST-RUN SMOKE
