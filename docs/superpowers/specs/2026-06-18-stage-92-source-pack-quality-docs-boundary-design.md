# Stage 92 Source-Pack Quality Docs Boundary Design

## Goal

Add a focused docs drift guard for `docs/source-pack-quality.md` so the
source-pack lint documentation keeps its local, read-only, non-fetching, and
non-guarantee boundaries.

## Scope

Modify:

- `tests/test_source_pack_quality_docs.py`
- Stage 92 spec/plan/review artifacts

Do not modify:

- `docs/source-pack-quality.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime source-pack lint tests

## Design

Create a standalone docs-only test file that reads
`docs/source-pack-quality.md`, normalizes whitespace/case, and asserts stable
phrases for:

- `source-pack-lint` as local and read-only
- no source fetching, live-feed availability checks, item collection, SQLite
  access, or generated config/data/report/workflow artifacts
- not being a compliance, audit, policy, or source-terms review workflow
- JSON output excluding fetched data, collected items, database state, source
  contents, and account data
- article-page fetching remaining outside lint behavior
- retail/resale source signals not being proof of demand outside the configured
  source set
- clean lint results being local configuration quality signals, not source
  availability guarantees

The test should not import application modules, inspect YAML files, touch
SQLite, or execute `source-pack-lint`.

## Tests

Focused checks:

```bash
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py
```

## Boundaries

This stage is test-only. It does not add lint behavior, source-pack behavior,
source acquisition, source availability checks, source fetching, collection,
SQLite access, generated artifacts, schema changes, platform coverage, demand
proof, ranking, scraping, connectors, platform APIs, scheduling, new linter
restrictions, or compliance-review product features.
