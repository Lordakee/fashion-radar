# Stage 270 Plan Review Prompt

You are reviewing the Stage 270 ROW ONE Runtime Readiness plan for the Fashion Radar repo.

Repo: /home/ubuntu/fashion-radar

Primary artifacts to review:
- docs/superpowers/specs/2026-07-03-stage-270-row-one-runtime-readiness-design.md
- docs/superpowers/plans/2026-07-03-stage-270-row-one-runtime-readiness-plan.md

Relevant existing files:
- src/fashion_radar/cli.py
- src/fashion_radar/row_one/render.py
- src/fashion_radar/row_one/server.py
- src/fashion_radar/scheduling.py
- src/fashion_radar/row_one/ops.py
- tests/test_row_one_cli.py
- tests/test_row_one_app_contract.py
- tests/test_package_archives.py
- tests/test_row_one_docs.py
- scripts/check_first_run_smoke.py
- docs/row-one.md
- docs/cli-reference.md
- docs/first-run.md

Review questions:
1. Does the plan build on existing `row-one refresh`, `row-one schedule`, `row-one local-ops`, `row-one preview`, and `row-one serve` surfaces instead of duplicating or replacing them?
2. Does the plan preserve print-only scheduling and avoid installing cron/systemd timers, daemons, background workers, or cloud deployment behavior?
3. Does the plan correctly preserve the retention boundary: ROW ONE site output may be cleaned via `latest_only=True`, but dated reports outside the site directory are not silently deleted?
4. Does the plan avoid OpenDesign calls, image generation, new collectors, social-platform automation, account/cookie/browser automation, and compliance-review product features?
5. Is the proposed additive `row-one-runtime/v1` contract technically reasonable, internally consistent, and compatible with the existing `row-one-app/v1` and `row-one-manifest/v1` contracts?
6. Is `row-one status` scoped correctly as a validation/status command, and are text and JSON outputs testable without making the CLI brittle?
7. Is the subprocess serve smoke feasible and not likely to be flaky or leave a long-running process behind?
8. Are package archive, docs, first-run smoke, focused tests, and full gate coverage sufficient for this stage?
9. Are there implementation-plan issues such as missing imports, wrong file ownership, missing required files, untestable assertions, schema mismatch, or commands that cannot work as written?

Return format:
- Verdict: APPROVED or NOT APPROVED
- Critical findings: blockers that must be fixed before coding
- Important findings: issues that should be fixed before coding
- Minor findings: optional cleanup
- Suggested plan changes, with exact file/path references

Do not edit files. This is a read-only plan review.
