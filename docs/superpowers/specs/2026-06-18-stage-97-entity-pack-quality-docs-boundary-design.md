# Stage 97 Entity-Pack Quality Docs Boundary Design

## Goal

Add a focused docs drift guard for `docs/entity-pack-quality.md` so
`entity-pack-lint` documentation keeps its local, read-only, non-matching, and
non-claim boundaries.

## Scope

Modify:

- `tests/test_entity_pack_quality_docs.py`
- Stage 97 spec/plan/review artifacts

Do not modify:

- `docs/entity-pack-quality.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime entity-pack lint tests

## Design

Create a standalone docs-only test file that reads
`docs/entity-pack-quality.md`, normalizes whitespace/case, and asserts stable
phrases for:

- `entity-pack-lint` checking one local YAML file
- linting being local and read-only
- no item matching, entity scoring, SQLite inspection, source collection,
  social-platform search, page fetching, or generated artifacts
- not being a hot-list, ranking, platform-wide signal, market-wide proof,
  compliance review, audit workflow, or legal review
- clean lint results being local configuration quality signals, not demand or
  platform/social/search/audit claims

The test should not import application modules, load entity configs, parse YAML,
touch SQLite, or execute CLI commands.

## Tests

Focused checks:

```bash
uv --no-config run --frozen pytest tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen pytest tests/test_entity_pack_lint.py tests/test_entity_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_entity_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_entity_pack_quality_docs.py
```

## Boundaries

This stage is test-only. It does not add entity-pack lint behavior, entity config
behavior, runtime matching behavior, source collection, source acquisition,
social-platform search, page fetching, SQLite inspection, report/digest/workflow
artifacts, ranking semantics, demand proof, market/platform-wide claims,
schema changes, dependency changes, CI changes, new linter restrictions, or
compliance-review product features.
