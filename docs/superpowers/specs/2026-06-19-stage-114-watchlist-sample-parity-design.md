# Stage 114 Watchlist Sample Parity Design

## Goal

Expand the optional watchlist community-signal sample so the checked-in sample
exercises more of the existing fashion watchlist entity pack: Tory Burch,
Tory Burch Pierced Mule, East-West Bags, and Office Siren.

## Scope

Stage 114 is a small sample-data and test-parity stage. It does not add new
entities or aliases. The existing optional entity pack already contains these
watchlist entries; the sample CSV simply does not exercise them.

Allowed changes:

- `examples/community-signals.watchlist.example.csv`
- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_import_contract.py`
- `tests/test_entity_packs.py`
- `tests/test_watchlist_sample_workflow.py`
- Stage 114 spec, plan, and review artifacts

Out of scope:

- `configs/entity-packs/fashion-watchlist.example.yaml`
- default packaged entity config
- source packs
- docs unless plan review identifies a concrete failing docs contract
- runtime importer, matcher, report, trend, dashboard, CLI, or schema behavior
- external-tool adapters, connectors, scraping, platform search, scheduling, or
  browser automation
- compliance, audit, or legal review product features
- dependency manifests, `uv.lock`, package metadata, or CI changes

## Design

Add three synthetic rows to
`examples/community-signals.watchlist.example.csv`, inserted before the current
final `Boho Revival` row so the existing "last row is Boho Revival" contract can
remain unchanged:

- `Tory Burch Pierced Mule footwear watchlist note`
- `East-West Bags local watchlist note`
- `Office Siren styling watchlist note`

The rows should use conservative local-note language, `Community Watchlist
Sample` as `source_name`, `community` as `platform`, and stable collected
timestamps on `2026-06-12`. They should avoid account names, usernames, raw
comments, private data, or platform-specific scraping claims.

Update the tests that intentionally pin sample row count and matched entity
coverage:

- row count: `8 -> 11`
- expected matched names: add `Tory Burch`, `Tory Burch Pierced Mule`,
  `East-West Bags`, and `Office Siren`
- workflow output strings: `Validated 8`, `Imported 8`, `Processed 8` become
  `Validated 11`, `Imported 11`, `Processed 11`

## Risks

- Do not widen aliases in YAML. The risk is false-positive matching, and this
  stage does not need alias changes.
- Do not add sample rows after `Boho Revival`; existing import-contract tests
  assert the final row title.
- Do not make docs exhaustive unless a docs test requires it. Current docs are
  phrased as examples of expected local matches, not a complete sample row list.
