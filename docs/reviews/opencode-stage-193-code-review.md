# Stage 193 Code Review

## Critical
None.

## Important
None.

## Minor
1. **Three promised CLI tests were dropped.** The design's testing strategy (design `Testing Strategy`) and the approved plan's Task 2 Step 1 (plan lines 543-559) explicitly listed a dedicated `test_trend_explanations_command_invalid_as_of_writes_nothing`, plus "invalid config fails before data-dir creation" and "incompatible database remains read-only" CLI tests. Only the missing-database / json / table / include-dropped / help / negative-limit tests were implemented. The dropped behaviors are correct — they share the identical read-only flow copied from `trends_command` (`cli.py:1511` vs `cli.py:1584`) — so this is a coverage gap, not a defect. Worth back-filling for parity with `trends`.

2. *(Carryover from rereview, now resolved — not a current issue.)* The rereview's Minor #1 (JSON/table boundary drift) is actually **fixed in implementation**: `render_trend_explanations_table` consumes `*report.boundaries` (`trend_explanations.py:89`) rather than hardcoding strings, so JSON and table boundaries are aligned.

## Review Answers
1. **Satisfies the approved plan?** Yes. Pure module, CLI wiring, docs, changelog, and review artifacts all present and matching the spec. Data model, boundaries, reason codes, headlines, and status clauses all match the design exactly.
2. **Avoids mutating existing contracts?** Yes. `git diff` confirms `models/trend.py`, `heat_movers.py`, `trends.py`, and dashboard code are untouched; `cli.py` diff is purely additive (zero deletions). `build_trend_comparison` is called with `limit=None`, leaving the sidecar to own truncation.
3. **Read-only?** Yes. Missing DB → empty `TrendExplanationReport`, exit 0, no data-dir/DB creation (`test_trend_explanations_command_missing_database_writes_nothing`). Config/schema/parse errors are caught before any write and exit 1. Engine is created read-only and disposed in `finally`.
4. **Rising/cooling accurate for flat dimensions?** Yes. `_status_clause` uses "Score and/or mention movement increased/decreased" wording, verified accurate against the real classifier at `trends.py:246-253` (RISING fires `score_delta>0, mention_delta>=0` and `score_delta==0, mention_delta>0`). The flat-dimension test asserts the clause is present while the per-dimension reason code is correctly absent.
5. **Deterministic and bounded?** Yes. Stable JSON key order (tested), no re-ranking/regrouping — order follows `comparison.deltas` and `limit` truncates in place. Boundary strings ("configured sources and imported local signals", "no demand proof", "no platform coverage verification") are present in both JSON and table; no demand-proof or coverage-verification claims.
6. **Blockers before release?** No Critical or Important issues.

## Verification
- `pytest tests/test_trend_explanations.py tests/test_cli.py tests/test_cli_docs.py -q` → 401 passed.
- `ruff check` + `ruff format --check` → clean.
- `git diff --check` → clean.

## Verdict
**approved with non-blocking minors**
