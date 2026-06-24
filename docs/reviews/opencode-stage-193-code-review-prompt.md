Review the Stage 193 implementation for /home/ubuntu/fashion-radar.

Read:
- docs/superpowers/specs/2026-06-24-stage-193-trend-heat-explanation-sidecar-design.md
- docs/superpowers/plans/2026-06-24-stage-193-trend-heat-explanation-sidecar-plan.md
- docs/reviews/opencode-stage-193-plan-review.md
- docs/reviews/opencode-stage-193-plan-rereview.md
- src/fashion_radar/trend_explanations.py
- src/fashion_radar/cli.py
- tests/test_trend_explanations.py
- tests/test_cli.py
- tests/test_cli_docs.py
- README.md
- docs/cli-reference.md
- docs/trend-deltas.md
- docs/architecture.md
- docs/dashboard.md
- docs/github-upload-checklist.md
- CHANGELOG.md
- AGENTS.md
- docs/REVIEW_PROTOCOL.md

Goal:
Review the implemented read-only `trend-explanations` sidecar command and pure
explanation module.

Implementation summary:
- Added `src/fashion_radar/trend_explanations.py`.
- Added pure `TrendExplanationReport` / `TrendExplanationItem` models.
- Added `build_trend_explanations(...)` over existing `TrendComparison`.
- Added `render_trend_explanations_table(...)` with local/no-demand/no-coverage
  boundary language.
- Added `fashion-radar trend-explanations` CLI command.
- Added unit, CLI, and docs tests.
- Updated README, CLI reference, trend-deltas, architecture, dashboard,
  upload checklist, and changelog.

Verification already run:
- `uv --no-config run --frozen pytest tests/test_trend_explanations.py tests/test_cli.py tests/test_cli_docs.py -q`
- `uv --no-config run --frozen ruff check src/fashion_radar/trend_explanations.py src/fashion_radar/cli.py tests/test_trend_explanations.py tests/test_cli.py tests/test_cli_docs.py`
- `uv --no-config run --frozen ruff format --check src/fashion_radar/trend_explanations.py src/fashion_radar/cli.py tests/test_trend_explanations.py tests/test_cli.py tests/test_cli_docs.py`
- `git diff --check`

Review questions:
1. Does the implementation satisfy the approved Stage 193 plan?
2. Does it avoid mutating `TrendDelta`, `TrendComparison`, `HeatMover`,
   `HeatMoversReport`, dashboard row contracts, and existing `trends` /
   `heat-movers` JSON output?
3. Is the CLI read-only, especially when the database is missing or schema
   validation fails?
4. Are rising/cooling explanations accurate for flat score or mention
   dimensions?
5. Are table and JSON outputs deterministic and bounded to configured sources
   and imported local signals, with no demand proof or platform coverage
   verification claim?
6. Are there any Critical or Important issues that must be fixed before
   release verification?

Return:
- Critical
- Important
- Minor
- Verdict

End with one of: approved, approved with non-blocking minors, or not approved.
