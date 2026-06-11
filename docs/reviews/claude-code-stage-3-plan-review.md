# Claude Code Stage 3 Plan Review

Date: 2026-06-11

Reviewed file:
`docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

## Critical Findings

1. Stage 3 adds collector status/unhealthy-source persistence but did not define
   how the Stage 2 schema version guard should evolve from version `1`.
2. The GDELT request/query contract was undefined: endpoint, source of query
   terms, time window, and deduplication path were missing.

## Important Findings

1. robots.txt fetch-failure policy was unspecified.
2. RSS/article HTTP politeness was not specified.
3. `collectors/base.py` and `utils/http.py` lacked explicit contracts.
4. New configuration fields did not have an owning YAML/Pydantic model.
5. Unhealthy-source reset lifecycle was underspecified before Stage 5 CLI.

## Recommendation

Approved after fixes.

## Resolution

- Added an explicit Stage 3 schema version bump from `1` to `2` with a
  lightweight tested migration path.
- Defined the GDELT Doc API endpoint, source-query ownership, default lookback,
  max-records setting, and shared `ItemRepository` upsert path.
- Set safe robots.txt failure behavior to skip article extraction when robots
  cannot be fetched or parsed.
- Added shared HTTP timeout, retry, User-Agent, and per-domain politeness
  contracts.
- Defined the base collector interface as returning normalized items and run
  status without direct SQLite writes.
- Assigned Stage 3 settings to `sources.yaml` and Pydantic source models.
- Deferred manual source-health reset to Stage 5 CLI and kept retention expiry
  or direct DB state as the Stage 3 reset path.

## Claude Code Re-Review

Critical findings: None.

Important findings: None blocking.

Recommendation: Approved.

Claude Code confirmed that the schema version `1` to `2` policy, GDELT query
contract, robots.txt failure policy, RSS/article politeness, collector/http
interfaces, config ownership, and source-health lifecycle are resolved at plan
level. A minor consistency note about `gdelt.rate_limit_per_second` was fixed in
the plan.
