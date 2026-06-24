Review the Stage 193 plan for /home/ubuntu/fashion-radar.

Read:
- docs/superpowers/specs/2026-06-24-stage-193-trend-heat-explanation-sidecar-design.md
- docs/superpowers/plans/2026-06-24-stage-193-trend-heat-explanation-sidecar-plan.md
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- src/fashion_radar/trends.py
- src/fashion_radar/heat_movers.py
- src/fashion_radar/models/trend.py
- src/fashion_radar/cli.py
- tests/test_trends.py
- tests/test_heat_movers.py

Goal:
Add a new read-only `trend-explanations` sidecar command that explains why
local trend deltas moved without changing the existing `trends` or
`heat-movers` contracts.

Architecture and technical constraints:
- Pure explanation module over `TrendComparison`.
- Separate sidecar contract; do not mutate `TrendDelta`, `TrendComparison`,
  `HeatMover`, or `HeatMoversReport`.
- Reuse existing read-only trend loading flow and date/config validation.
- No new network access, source acquisition, connector work, demand proof,
  coverage verification, compliance-review feature, or LLM summarization.

Review questions:
1. Is a separate `trend-explanations` command the right contract-safe approach?
2. Does the plan avoid mutating existing trend/heat JSON contracts?
3. Are the RED tests likely to fail for the intended reasons?
4. Are the proposed models and summaries deterministic enough?
5. Are there any Critical or Important issues in the spec/plan as written?

Return:
- Critical
- Important
- Minor
- Verdict

End with one of: approved, approved with non-blocking minors, or not approved.
