# Stage 109 Source Boundaries Quality Docs Design

## Goal

Add a section-scoped docs drift guard for the `## Quality Boundaries` section in
`docs/source-boundaries.md` so future edits keep quality-boundary guidance
explicit: heat scores are local metrics, candidate signals need review, and the
dashboard should surface a small set of local diagnostic fields.

## Scope

Stage 109 is docs-test-only. It appends one focused pytest test to the existing
`tests/test_source_boundaries_docs.py` module. The test reads
`docs/source-boundaries.md`, extracts the `## Quality Boundaries` section,
normalizes whitespace and case, and asserts stable quality-boundary phrases.

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 109 spec, plan, and review artifacts

Out of scope:

- `docs/source-boundaries.md` source text
- `README.md`
- dashboard/report behavior or UI
- `src/`, `scripts/`, `examples/`, configs, schemas, dependencies, CI,
  `uv.lock`, package metadata, release hygiene, CLI behavior, database schema,
  collector logic, source acquisition, connector behavior, social/platform
  scraping, browser automation, account/session/cookie/proxy handling,
  scheduling, monitoring, coverage verification, ranking behavior, or
  compliance/audit/legal review product features

## Boundary Phrases

The guard should extract only `## Quality Boundaries` and assert these phrases
after whitespace collapse and case-folding:

- `Heat scores are local metrics based on configured sources and imported local signals.`
- `They are not rankings outside that local source set.`
- `Candidate signals are observed phrases from configured sources and imported local signals and need review.`
- `They should not be presented as validated entities.`
- `The dashboard should show:`
- `Source count.`
- `Representative links.`
- `Time window.`
- `Failed source runs.`
- `Missing data warnings.`
- `Whether a source is core, opt-in, or experimental.`

These phrases pin the public quality-boundary wording without adding runtime
scoring checks, candidate validation behavior, dashboard rendering logic, or
policy-review features.

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
adjacent docs/reference tests that already touch scoring, candidate discovery,
dashboard docs, reports, and CLI docs, then ruff, formatting, and whitespace
checks. Full verification before commit should reuse the repository release
gate: release hygiene, full pytest with proxy vars unset, repo-wide ruff check
and format check, lockfile check, mirror URL scan, `uv.lock`/
`pyproject.toml` diff guard, staged hygiene, and staged secret scan.

## Risks

The `## Quality Boundaries` section overlaps conceptually with scoring,
candidate discovery, dashboard, and reporting. Stage 109 deliberately pins only
the source-boundaries section wording and does not change runtime scoring,
dashboard content, report content, or candidate processing behavior.
