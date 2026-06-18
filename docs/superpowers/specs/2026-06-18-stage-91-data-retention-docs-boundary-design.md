# Stage 91 Data Retention Docs Boundary Design

## Goal

Add a focused docs drift guard for `docs/data-retention.md` so cleanup and
retention documentation keeps its current pruning boundaries.

## Scope

Modify:

- `tests/test_data_retention_docs.py`
- Stage 91 spec/plan/review artifacts

Do not modify:

- `docs/data-retention.md`
- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- `tests/test_cli_docs.py`
- runtime cleanup tests

## Design

Create a standalone docs-only test file that reads `docs/data-retention.md` and
asserts stable phrases for:

- `clean-old-data` pruning old collected `items`
- cutoff calculation as `as_of - retention_days`
- explicit `item_entities` deletion before deleting `items`
- dry-run count reporting without deletion
- non-pruned `collector_runs`, `source_health`, `entity_first_seen`, generated
  reports, and config files
- `entity_first_seen` retention across item pruning
- practical dry-run and backup guidance

The test should not import application modules or inspect SQLite state.

## Tests

Focused checks:

```bash
uv --no-config run --frozen pytest tests/test_data_retention_docs.py -q
uv --no-config run --frozen pytest tests/test_workflows.py::test_clean_old_data_prunes_by_collected_at tests/test_cli.py::test_clean_old_data_command_prunes_old_items tests/test_data_retention_docs.py -q
uv --no-config run --frozen ruff check tests/test_data_retention_docs.py
uv --no-config run --frozen ruff format --check tests/test_data_retention_docs.py
```

## Boundaries

This stage is test-only. It does not add cleanup behavior, retention behavior,
schema changes, source acquisition, platform coverage, demand proof, ranking,
scraping, connectors, platform APIs, scheduling, new linter restrictions, or
compliance-review product features.
