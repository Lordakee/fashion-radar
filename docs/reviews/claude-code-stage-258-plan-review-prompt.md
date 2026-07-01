Review the Stage 258 plan for /home/ubuntu/fashion-radar.

You are the primary reviewer. Use read-only review. Focus on whether the plan is
technically correct, scoped, and consistent with AGENTS.md and
docs/REVIEW_PROTOCOL.md.

Files to inspect:
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/superpowers/plans/2026-07-01-stage-258-html-report-artifact-hygiene-parity-plan.md
- scripts/check_first_run_smoke.py
- tests/test_first_run_smoke.py
- README.md
- docs/first-run.md
- docs/data-retention.md
- tests/test_cli_docs.py
- tests/test_data_retention_docs.py
- .gitignore
- scripts/check_release_hygiene.py

Plan summary:
- Stage 257 now writes companion `fashion-radar-YYYY-MM-DD.html` reports.
- Stage 258 should make first-run smoke, default-artifact guard tests, cleanup
  docs, data-retention docs, and docs guards include HTML report artifacts
  wherever they already cover Markdown/JSON report artifacts.
- It must not change report rendering, collectors, social/platform connectors,
  scraping, browser automation, platform APIs, demand proof, ranking semantics,
  platform coverage verification, dependencies, `pyproject.toml`, or `uv.lock`.

Please return:
- Verdict: APPROVE, APPROVE_WITH_NITS, REQUEST_CHANGES, or REJECT.
- Critical issues.
- Important issues.
- Minor/nit issues.
- Any missing verification.
