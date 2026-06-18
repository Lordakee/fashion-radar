# Stage 108 Source Boundaries Output Docs Design

## Goal

Add a section-scoped docs drift guard for the `## Output Boundaries` section in
`docs/source-boundaries.md` so future edits keep report/dashboard wording
guidance explicit: outputs describe local signals rather than certainty, include
safe local-observed wording examples, and avoid market-wide or verified-demand
claims.

## Scope

Stage 108 is docs-test-only. It appends one focused pytest test to the existing
`tests/test_source_boundaries_docs.py` module. The test reads
`docs/source-boundaries.md`, extracts the `## Output Boundaries` section,
normalizes whitespace and case, and asserts stable output-boundary phrases.

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 108 spec, plan, and review artifacts

Out of scope:

- `docs/source-boundaries.md` source text
- `README.md`
- dashboard/report rendering behavior
- `src/`, `scripts/`, `examples/`, configs, schemas, dependencies, CI,
  `uv.lock`, package metadata, release hygiene, CLI behavior, database schema,
  collector logic, robots/fetching behavior, source acquisition, connector
  behavior, social/platform scraping, browser automation, account/session/
  cookie/proxy handling, scheduling, monitoring, coverage verification, ranking
  behavior, or compliance/audit/legal review product features

## Boundary Phrases

The guard should extract only `## Output Boundaries` and assert these phrases
after whitespace collapse and case-folding:

- `Reports and dashboards should describe signals, not assert certainty.`
- `Preferred wording:`
- `Mention count increased in this configured source set`
- `Needs human review`
- `Signal changed within this configured local source set`
- `Imported row platform provenance label`
- `Stored local provenance label, not platform coverage`
- `Avoid wording that implies complete market truth:`
- `This source-set signal proves external demand`
- `This celebrity caused the trend`

These phrases pin output wording guidance without adding runtime string filters,
dashboard/report behavior, market-ranking behavior, or policy-review features.

## Test Shape

Reuse the helpers already present in `tests/test_source_boundaries_docs.py`:

- `_read_source_boundaries_doc()`
- `_normalized()`
- `_section()`

Append one test function with a focused phrase loop. The test must not import
application modules, execute CLI commands, open SQLite, read or write data/report
files, fetch network resources, render dashboards/reports, run collectors, or
write files.

## Verification

Focused verification should cover `tests/test_source_boundaries_docs.py` and
adjacent docs/reference tests that already touch heat, trend, scoring, candidate,
dashboard, and CLI docs, then ruff, formatting, and whitespace checks. Full
verification before commit should reuse the repository release gate: release
hygiene, full pytest with proxy vars unset, repo-wide ruff check and format
check, lockfile check, mirror URL scan, `uv.lock`/`pyproject.toml` diff guard,
staged hygiene, and staged secret scan.

## Risks

The `## Output Boundaries` section overlaps conceptually with heat movers, trend
deltas, scoring, candidate discovery, dashboard, and report wording. Stage 108
deliberately pins only the more section-specific source-boundaries text and
avoids duplicating heat-mover, trend-delta, scoring, and candidate guard
phrases that are already asserted elsewhere. It does not change runtime wording,
CLI docs, report content, dashboard content, or full negative-claim scanning.
