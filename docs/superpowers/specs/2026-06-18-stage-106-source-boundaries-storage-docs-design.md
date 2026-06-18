# Stage 106 Source Boundaries Storage Docs Design

## Goal

Add a standalone docs drift guard for the `## Storage Boundaries` section in
`docs/source-boundaries.md` so future edits keep conservative local storage
guidance explicit: store source metadata and local provenance, avoid full article
text/media/comment redistribution by default, preserve source attribution, and
skip known paywalled extraction unless permitted metadata is provided.

## Scope

Stage 106 is docs-test-only. It creates one focused pytest module that reads the
existing source-boundaries documentation, extracts the `## Storage Boundaries`
section, normalizes whitespace and case, and asserts storage-boundary phrases.

Allowed changes:

- `tests/test_source_boundaries_docs.py`
- Stage 106 spec, plan, and review artifacts

Out of scope:

- `docs/source-boundaries.md` source text
- `src/`, `scripts/`, `examples/`, configs, schemas, dependencies, CI,
  `uv.lock`, package metadata, release hygiene, dashboard behavior, report
  generation, CLI behavior, database schema, collector logic, robots/fetching
  behavior, source acquisition, connector behavior, social/platform scraping,
  browser automation, account/session/cookie/proxy handling, scheduling,
  monitoring, coverage verification, ranking behavior, or compliance/audit/
  legal review product features

## Boundary Phrases

The guard should extract only `## Storage Boundaries` and assert these phrases
after whitespace collapse and case-folding:

- `Default storage should be conservative:`
- `` Store source URLs, titles, publication timestamps, source names, optional local `platform` provenance labels for imported rows, short summaries, entity matches, tags, counts, and scores. ``
- `Avoid storing full article text by default.`
- `Avoid storing original images or videos.`
- `Avoid storing user comments as redistributable assets.`
- `Preserve source links so users can read original content on the source site.`
- `Display source attribution beside representative items.`
- `Add attribution footer to generated reports.`
- `Skip extraction for known paywalled domains unless the source itself provides permitted metadata.`

These phrases pin the public explanation of storage limits without expanding
into runtime collection, extraction, storage migrations, source crawling,
platform monitoring, or policy-review features.

## Test Shape

Use the same lightweight pattern as recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `docs/source-boundaries.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a focused phrase loop

The test must not import application modules, execute CLI commands, open
SQLite, read or write data/report files, fetch network resources, run
collectors, inspect robots.txt, or write files.

## Verification

Focused verification should cover the new docs guard and adjacent source
boundary docs tests, then ruff, formatting, and whitespace checks. Full
verification before commit should reuse the repository release gate: release
hygiene, full pytest with proxy vars unset, repo-wide ruff check and format
check, lockfile check, mirror URL scan, `uv.lock`/`pyproject.toml` diff guard,
staged hygiene, and staged secret scan.

## Risks

`docs/source-boundaries.md` also documents source categories, connector
boundaries, robots/fetching, output wording, privacy, and README requirements.
Stage 106 deliberately scopes to `## Storage Boundaries` only so the guard does
not duplicate broader CLI docs tests, architecture source-boundary tests, robots
collector tests, output wording checks, or README requirements wording.

Phrase assertions may need deliberate updates if storage guidance is rewritten.
That is acceptable because the goal is to catch accidental drift from the
conservative local storage boundary.
