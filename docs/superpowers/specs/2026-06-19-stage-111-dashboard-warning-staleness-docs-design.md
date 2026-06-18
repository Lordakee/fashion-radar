# Stage 111 Dashboard Warning Staleness Docs Design

## Goal

Add a docs drift guard for dashboard warning, empty-state, and stale report
wording in `docs/dashboard.md` so future edits keep user-facing dashboard
expectations explicit: invalid trend config warns without creating local state,
Daily Brief empty states do not create local state, and Candidate Signals reads
the latest report JSON and may be stale until a new report is written.

## Scope

Stage 111 is docs-test-only. It appends one focused pytest test to
`tests/test_dashboard_docs.py`. The test reads `docs/dashboard.md`, normalizes
whitespace and case, and asserts stable warning/staleness phrases already
present in the document.

Allowed changes:

- `tests/test_dashboard_docs.py`
- Stage 111 spec, plan, and review artifacts

Out of scope:

- `docs/dashboard.md` source text
- dashboard runtime behavior, Streamlit rendering, SQLite queries, report
  loading, candidate extraction, scoring, source collection, dashboard tab
  routing, CLI behavior, source acquisition, connector behavior, social/platform
  scraping, browser automation, account/session/cookie/proxy handling,
  monitoring, scheduling, coverage verification, ranking behavior,
  compliance/audit/legal review product features, `src/`, `scripts/`,
  `examples/`, configs, schemas, dependencies, CI, `uv.lock`, package metadata,
  release hygiene behavior, README, or project brief text

## Boundary Phrases

The guard should assert these phrases after whitespace collapse and
case-folding:

- `Invalid or missing trend config shows a concise dashboard warning without creating the data directory or database.`
- `If the local database has not been initialized or has no retained items, the tab shows an empty-state message without creating the data directory or database.`
- `Reads candidate signals from the latest report JSON when that file is available.`
- `The Candidate Signals tab reads the latest generated report JSON.`
- `If the latest report was generated before the latest collection, local import, or matching run, the tab may be stale until a new report is written.`

These phrases pin dashboard docs that explain local-state warnings and report
staleness without changing dashboard runtime behavior.

## Test Shape

Reuse the helpers already present in `tests/test_dashboard_docs.py`:

- `_read_dashboard_doc()`
- `_normalized()`

Append one test function with a focused phrase loop. The test should follow the
existing whole-document normalized assertion pattern and avoid adding a section
helper unless the plan review identifies a real ambiguity. The test must not
import application modules, execute CLI commands, open SQLite, read or write
data/report/dashboard files, fetch network resources, render Streamlit, or write
files.

## Verification

Focused verification should cover `tests/test_dashboard_docs.py`. Adjacent
verification should include dashboard runtime tests and docs that overlap with
candidate report staleness and scoring limits. Full verification before commit
should reuse the repository release gate: release hygiene, full pytest with
proxy vars unset, repo-wide ruff check and format check, lockfile check, mirror
URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and staged
secret scan.

## Risks

Candidate report JSON wording overlaps conceptually with `docs/scoring.md` and
`docs/candidate-discovery.md`. Stage 111 deliberately pins only dashboard docs
wording and does not change candidate discovery, scoring, report generation, or
dashboard runtime behavior.
