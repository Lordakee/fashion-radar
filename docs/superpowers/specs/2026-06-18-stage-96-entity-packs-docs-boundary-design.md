# Stage 96 Entity Packs Docs Boundary Design

## Goal

Add a focused docs drift guard for `docs/entity-packs.md` so optional entity
pack documentation keeps its local matching and optional local sample
boundaries.

## Scope

Modify:

- `tests/test_entity_packs_docs.py`
- Stage 96 spec/plan/review artifacts

Do not modify:

- `docs/entity-packs.md`
- `configs/entity-packs/`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime entity-pack tests

## Design

Create a standalone docs-only test file that reads `docs/entity-packs.md`,
normalizes whitespace/case, and asserts stable phrases for:

- entity packs as optional local configuration templates
- not changing runtime behavior
- only changing local entity matching
- not adding sources
- optional sample rows being synthetic local rows
- optional sample flow using local files only

The test should not import application modules, load entity configs, parse YAML,
touch SQLite, or execute CLI commands.

## Tests

Focused checks:

```bash
uv --no-config run --frozen pytest tests/test_entity_packs_docs.py -q
uv --no-config run --frozen pytest tests/test_entity_packs.py tests/test_entity_packs_docs.py -q
uv --no-config run --frozen ruff check tests/test_entity_packs_docs.py
uv --no-config run --frozen ruff format --check tests/test_entity_packs_docs.py
```

## Boundaries

This stage is test-only. It does not add entity-pack behavior, entity config
behavior, runtime matching behavior, source collection, ingestion, source setup,
platform or community ingestion, scraping, social monitoring, current-hotness
detection, ranking semantics, demand proof, platform coverage verification,
schema changes, dependency changes, CI changes, new linter restrictions, or
compliance-review product features.
