Review this Stage 257 plan for /home/ubuntu/fashion-radar.

You are the primary reviewer. Use read-only review. Focus on whether the plan is
technically correct, scoped, and consistent with AGENTS.md and
docs/REVIEW_PROTOCOL.md.

Files to inspect:
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/superpowers/plans/2026-07-01-stage-257-html-recent-news-and-buyer-pack-quality-plan.md
- current git diff for src/fashion_radar/html_report.py
- current git diff for src/fashion_radar/workflows.py
- configs/entity-packs/buyer-brands.example.yaml
- tests/test_reports.py
- tests/test_workflows.py
- tests/test_entity_packs.py
- tests/test_package_archives.py

Plan summary:
- Fix the uncommitted HTML report recent-news behavior by adding tests and
  scoping recent DB items to the current report window:
  `as_of - scoring.current_window_days < collected_at <= as_of`.
- Keep the untracked buyer brand entity pack only with minimal tests, docs, and
  package/archive guard updates.
- Do not add connectors, scraping, browser automation, demand proof, ranking
  semantics, platform coverage verification, dependency changes, or uv.lock
  changes.

Please return:
- Verdict: APPROVE, APPROVE_WITH_NITS, REQUEST_CHANGES, or REJECT.
- Critical issues.
- Important issues.
- Minor/nit issues.
- Any missing verification commands.
