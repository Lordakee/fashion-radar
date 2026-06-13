# Claude Code Stage 23 Code Review Prompt

You are reviewing Stage 23 for `/home/ubuntu/fashion-radar` in read-only mode.
Do not edit files. Use maximum reasoning.

## Goal

Stage 23 adds `fashion-radar imported-entity-deltas`, a local read-only command
that compares current stored `item_entities` matches on retained
`manual_import` rows across adjacent collected-at windows.

## Current Working Tree

Review the current working tree, including untracked Stage 23 process docs.
Useful commands:

```bash
git status --short
git diff -- src/fashion_radar/imported_entity_deltas.py src/fashion_radar/cli.py tests/test_imported_entity_deltas.py tests/test_cli.py README.md docs CHANGELOG.md
```

## Scope Guard

Keep review recommendations inside the local SQLite imported-entity-deltas
boundary. Do not propose new ingestion paths, browser automation, platform APIs,
account automation, background workflows, source-name quality/ranking,
scoring/trend machinery, candidate discovery, report/dashboard writes,
migrations, dependencies, or compliance/audit features.

## Review Focus

Check:

1. The command reads only existing local SQLite `items` and `item_entities`,
   filters to `manual_import`, and never initializes, migrates, imports,
   matches, scores, reports, collects, or writes artifacts.
2. Missing DB, invalid format, invalid numeric options, and invalid `--as-of`
   avoid query/database access and do not create data/config/report artifacts.
3. Existing DBs are opened through `create_readonly_sqlite_engine()`, schema is
   verified with the existing imported-signals verifier, and only SELECTs are
   used.
4. Counts are item-level per stored `(item_id, entity_name, entity_type)`;
   duplicate match rows on one item do not inflate counts or source counts.
5. Window classification uses `parse_datetime_utc()` in Python with:
   `baseline_start < collected_at <= current_start` and
   `current_start < collected_at <= as_of`.
6. `current_matched_item_count` and `baseline_matched_item_count` reflect the
   same source-name/entity-type filters as entity rows.
7. `current_source_count`, `baseline_source_count`, and `source_count_delta`
   refer only to stored local `source_name` labels.
8. Change labels and ordering are deterministic and do not imply external
   ranking.
9. Table/JSON outputs hide item titles, URLs, summaries, ids, match reasons,
   context terms, aliases, confidence values, raw rows, and imported file paths.
10. Docs remain bounded to retained local rows, stored matches,
    collected-at windows, and stored entity/source-name labels.

Recent local checks already run:

```bash
.venv/bin/python -m pytest tests/test_imported_entity_deltas.py tests/test_cli.py tests/test_db.py -q -k "imported_entity_deltas or imported_signals or readonly"
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Return findings by severity:

- Critical: must fix before release.
- Important: should fix before release.
- Minor: optional polish.

End with one of:

- `Approved for Stage 23 release checks`
- `Not approved`
