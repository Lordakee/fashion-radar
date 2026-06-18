# Stage 114 Plan Review Prompt

Review the Stage 114 plan in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Expand the optional watchlist community-signal sample so it exercises existing
entity-pack entries for Tory Burch, Tory Burch Pierced Mule, East-West Bags, and
Office Siren.

## Files To Review

- `docs/superpowers/specs/2026-06-19-stage-114-watchlist-sample-parity-design.md`
- `docs/superpowers/plans/2026-06-19-stage-114-watchlist-sample-parity-plan.md`
- `examples/community-signals.watchlist.example.csv`
- `configs/entity-packs/fashion-watchlist.example.yaml`
- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_entity_packs.py`
- `tests/test_watchlist_sample_workflow.py`
- `docs/entity-packs.md`
- `docs/first-run.md`

## Planned Change

Add these three rows before the final `Boho Revival` row:

```csv
https://example.com/community-watchlist/tory-burch-pierced-mule,Tory Burch Pierced Mule footwear watchlist note,2026-06-12T14:15:00Z,Sanitized local note about Tory Burch Pierced Mule shoe styling and Tory Burch footwear interest,Community Watchlist Sample,community,1.1,2026-06-12T14:35:00Z
https://example.com/community-watchlist/east-west-bags,East-West Bags local watchlist note,2026-06-12T14:30:00Z,Sanitized local note about east-west bags and east west tote handbag styling,Community Watchlist Sample,community,1.0,2026-06-12T14:50:00Z
https://example.com/community-watchlist/office-siren,Office Siren styling watchlist note,2026-06-12T14:45:00Z,Sanitized local note about office siren styling signals and fashion aesthetics,Community Watchlist Sample,community,1.0,2026-06-12T14:55:00Z
```

Update row-count tests from 8 to 11 and extend expected matched/report/trend
entities with:

- `Tory Burch`
- `Tory Burch Pierced Mule`
- `East-West Bags`
- `Office Siren`

## Scope Constraints

Allowed changes:

- `examples/community-signals.watchlist.example.csv`
- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_entity_packs.py`
- `tests/test_watchlist_sample_workflow.py`
- Stage 114 review artifacts

Disallowed changes:

- `configs/entity-packs/fashion-watchlist.example.yaml`
- docs unless review identifies a concrete failing docs contract
- runtime importer, matcher, report, trend, dashboard, CLI, schema, source, or
  scheduling behavior
- source packs, external-tool adapters, connectors, scraping, platform search,
  browser automation, account/session/cookie/proxy behavior
- compliance/audit/legal review product features
- dependency manifests, `uv.lock`, package metadata, CI workflows, or default
  packaged config

## Review Questions

1. Do the planned rows exercise existing entities without requiring alias/YAML
   changes?
2. Is inserting before the final `Boho Revival` row sufficient to preserve
   existing first/last-row assertions?
3. Are row-count and expected-entity test updates complete?
4. Can docs safely remain unchanged because their match examples are
   non-exhaustive?
5. Are the focused verification commands sufficient?

## Review Constraints

- Review the plan and referenced files only.
- Do not run full workflow simulations, temporary CSV generation, or broad
  empirical experiments unless a critical blocker cannot be assessed from the
  plan and existing source/tests.
- Prefer static review of file contracts and existing assertions.

Return findings first, ordered by severity. If there are no Critical or
Important blockers, say that explicitly.
