Review the Stage 257 code changes in /home/ubuntu/fashion-radar as fallback
reviewer if Claude Code code review is unavailable.

Read:
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/superpowers/plans/2026-07-01-stage-257-html-recent-news-and-buyer-pack-quality-plan.md
- docs/reviews/claude-code-stage-257-code-review.md
- docs/reviews/opencode-stage-257-plan-review.md
- current git diff

Focus:
- Correctness of HTML recent-news window filtering.
- HTML escaping and unsafe URL behavior.
- CLI/docs consistency for companion HTML reports.
- Buyer brands entity pack lint/matcher quality.
- Package archive guard updates.
- Scope boundaries: no new connectors, scraping, browser automation, platform
  APIs, demand proof, ranking semantics, platform coverage verification,
  dependency changes, or uv.lock changes.

Verification already run:
- Focused pytest command covering CLI/reports/workflows/entity packs/docs/package/first-run smoke: 734 passed.
- Ruff format/check on Python files: passed.
- Release hygiene: passed.
- sdist build/tar inspection: buyer-brands pack included.
- `git diff --check`: passed.

Return:
- Verdict.
- Critical issues.
- Important issues.
- Optional nits.
- Missing verification, if any.
