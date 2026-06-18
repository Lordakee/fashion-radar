# Stage 107 Source Boundaries README Requirements Docs Design

## Goal

Add a section-scoped docs drift guard for the `## README Requirements` section in
`docs/source-boundaries.md` so future edits keep the public README boundary
obligations explicit: no full social-platform coverage, user responsibility for
source/robots/API terms, no account-based default collection, manual import as a
local input path, and community handoff check directory reports as local-only
readiness reports.

## Scope

Stage 107 is docs-test-only. It appends one focused pytest test to the existing
`tests/test_source_boundaries_docs.py` module. The test reads
`docs/source-boundaries.md`, extracts the `## README Requirements` section,
normalizes whitespace and case, and asserts stable README-requirements phrases.

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 107 spec, plan, and review artifacts

Out of scope:

- `docs/source-boundaries.md` source text
- `README.md`
- `src/`, `scripts/`, `examples/`, configs, schemas, dependencies, CI,
  `uv.lock`, package metadata, release hygiene, dashboard behavior, report
  generation, CLI behavior, database schema, collector logic, robots/fetching
  behavior, source acquisition, connector behavior, social/platform scraping,
  browser automation, account/session/cookie/proxy handling, scheduling,
  monitoring, coverage verification, ranking behavior, or compliance/audit/
  legal review product features

## Boundary Phrases

The guard should extract only `## README Requirements` and assert these phrases
after whitespace collapse and case-folding:

- `The public README must explain:`
- `The project does not provide full social-platform coverage.`
- `Users are responsible for respecting source terms, robots rules, and API terms.`
- `The default workflow avoids account-based collection and access-control bypasses.`
- `Manual signal import is a local input path, not a platform connector or instructions for obtaining platform exports.`
- `Community handoff check directory reports are local-only handoff readiness reports.`

These phrases pin the compact public-boundary obligations without adding README
parity checks, connector behavior, collection behavior, policy workflow
features, or compliance review functionality.

## Test Shape

Reuse the helpers already present in `tests/test_source_boundaries_docs.py`:

- `_read_source_boundaries_doc()`
- `_normalized()`
- `_section()`

Append one test function with a focused phrase loop. The test must not import
application modules, execute CLI commands, open SQLite, read or write data/report
files, fetch network resources, compare README text, run collectors, or write
files.

## Verification

Focused verification should cover `tests/test_source_boundaries_docs.py` and
adjacent docs/reference tests, then ruff, formatting, and whitespace checks. Full
verification before commit should reuse the repository release gate: release
hygiene, full pytest with proxy vars unset, repo-wide ruff check and format
check, lockfile check, mirror URL scan, `uv.lock`/`pyproject.toml` diff guard,
staged hygiene, and staged secret scan.

## Risks

The `## README Requirements` section is longer than the targeted phrase set and
contains many command-specific bullets already covered elsewhere. Stage 107
deliberately pins only the general public-boundary obligations plus the local
handoff-readiness concept. It does not attempt full README parity and does not
expand runtime behavior or product features.
