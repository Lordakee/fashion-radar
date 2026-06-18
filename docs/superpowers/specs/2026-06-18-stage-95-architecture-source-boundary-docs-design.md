# Stage 95 Architecture Source Boundary Docs Design

## Goal

Add a focused docs drift guard for the `## Source Boundary` section in
`docs/architecture.md` so the architecture documentation keeps its core-source
scope and manual-import limits.

## Scope

Modify:

- `tests/test_architecture_boundary_docs.py`
- Stage 95 spec/plan/review artifacts

Do not modify:

- `docs/architecture.md`
- `docs/source-boundaries.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime tests

## Design

Create a standalone docs-only test file that reads `docs/architecture.md`,
extracts only the `## Source Boundary` section, normalizes whitespace/case, and
asserts stable phrases for:

- the core collector set being RSS, RSSHub-compatible feeds, and GDELT
- manual signal import being a local input path
- user-provided CSV/JSON files
- manual import not being a connector or platform collector
- non-core platform collection not being part of the current release boundary
- the source boundary section linking to `source-boundaries.md`

The test should not import application modules, parse configs, inspect source
packs, touch SQLite, or execute CLI commands.

## Tests

Focused checks:

```bash
uv --no-config run --frozen pytest tests/test_architecture_boundary_docs.py -q
uv --no-config run --frozen ruff check tests/test_architecture_boundary_docs.py
uv --no-config run --frozen ruff format --check tests/test_architecture_boundary_docs.py
```

## Boundaries

This stage is test-only. It does not add source collection, collectors, manual
import behavior, external tool behavior, connectors, source acquisition,
platform coverage, demand proof, ranking, scraping, browser automation,
platform APIs, account/cookie handling, scheduling, monitoring, schema changes,
dependency changes, CI changes, new linter restrictions, or compliance-review
product features.
