Review the Stage 257 code changes in /home/ubuntu/fashion-radar.

You are the primary reviewer. Use read-only review. Focus on correctness,
test coverage, scope boundaries, and release readiness.

Context:
- Claude Code plan review was unavailable; opencode fallback approved the plan
  with required changes, now incorporated.
- Stage 257 fixes obvious issues in uncommitted work:
  - HTML reports now include a `Latest Collected News` section populated from
    local SQLite recent items.
  - The recent-item query is scoped to the report window:
    `as_of - scoring.current_window_days < collected_at <= as_of`.
  - CLI output and docs expose the companion HTML report path without changing
    `write_daily_report_files()` return shape.
  - Adds optional `configs/entity-packs/buyer-brands.example.yaml` as a local
    entity matching template, with lint/tests/docs/package guards.

Files to inspect:
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/superpowers/plans/2026-07-01-stage-257-html-recent-news-and-buyer-pack-quality-plan.md
- docs/reviews/opencode-stage-257-plan-review.md
- README.md
- docs/architecture.md
- docs/cli-reference.md
- docs/entity-packs.md
- docs/first-run.md
- scripts/check_package_archives.py
- configs/entity-packs/buyer-brands.example.yaml
- src/fashion_radar/cli.py
- src/fashion_radar/html_report.py
- src/fashion_radar/workflows.py
- tests/test_cli.py
- tests/test_reports.py
- tests/test_workflows.py
- tests/test_entity_packs.py
- tests/test_entity_pack_lint.py
- tests/test_entity_packs_docs.py
- tests/test_package_archives.py

Verification already run:
- `uv --no-config run --frozen pytest tests/test_cli.py tests/test_reports.py tests/test_workflows.py tests/test_entity_packs.py tests/test_entity_pack_lint.py tests/test_entity_packs_docs.py tests/test_package_archives.py tests/test_cli_docs.py tests/test_first_run_smoke.py -q`
  -> 734 passed.
- `uv --no-config run --frozen ruff format --check scripts/check_package_archives.py src/fashion_radar/cli.py src/fashion_radar/html_report.py src/fashion_radar/workflows.py tests/test_cli.py tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_entity_packs_docs.py tests/test_package_archives.py tests/test_reports.py tests/test_workflows.py`
  -> 11 files already formatted.
- `uv --no-config run --frozen ruff check scripts/check_package_archives.py src/fashion_radar/cli.py src/fashion_radar/html_report.py src/fashion_radar/workflows.py tests/test_cli.py tests/test_entity_pack_lint.py tests/test_entity_packs.py tests/test_entity_packs_docs.py tests/test_package_archives.py tests/test_reports.py tests/test_workflows.py`
  -> All checks passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  -> Release hygiene checks passed.
- `uv --no-config build --sdist --out-dir /tmp/fashion-radar-stage257-dist`
  plus tar inspection confirmed
  `configs/entity-packs/buyer-brands.example.yaml` is in the sdist.
- `git diff --check`
  -> no whitespace errors.

Please return:
- Verdict: APPROVE, APPROVE_WITH_NITS, REQUEST_CHANGES, or REJECT.
- Critical issues.
- Important issues.
- Minor/nit issues.
- Any missing verification.
