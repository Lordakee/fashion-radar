# Data Retention

Fashion Radar stores local runtime state in SQLite. The default database path is:

```text
<data-dir>/fashion-radar.sqlite
```

Generated databases and SQLite sidecars are ignored by git when stored under the
project `data/` directory.

## Cleanup Command

Use `clean-old-data` to prune old collected items:

```bash
fashion-radar clean-old-data --data-dir ./data --as-of 2026-06-11T12:00:00Z --retention-days 30 --dry-run
fashion-radar clean-old-data --data-dir ./data --as-of 2026-06-11T12:00:00Z --retention-days 30
```

The cutoff is:

```text
as_of - retention_days
```

Rows in `items` with `collected_at` older than that cutoff are pruned.

`clean-old-data` remains the standalone/manual cleanup command. For ROW ONE,
`row-one refresh` runs the same SQLite cleanup semantics after the current ROW
ONE site and reports are generated, using default 1-day SQLite item retention
for the ROW ONE daily test-site path. Pass `--retention-days N` to
`row-one refresh` for a longer local history, or pass `--skip-data-retention` to
opt out for one refresh. A non-skipped SQLite retention failure returns a
nonzero exit status after report and site output is written. Report and site
artifacts generated before the retention failure remain available for inspection.

The 1-day retention is disk-friendly for test deployments, but it reduces
multi-day item history available to future scoring-window and heat-score
comparisons. Keep a longer `--retention-days` window when scoring-window and
heat-score comparisons need more than the current day of local item history.

ROW ONE report artifact pruning remains separate from this SQLite cleanup path:
`row-one refresh` may remove stale generated dated report files, while SQLite
retention prunes only eligible `items` rows and their related `item_entities`
rows.
The ROW ONE SQLite retention step does not prune `collector_runs`, does not
prune `source_health`, does not prune `entity_first_seen`, does not prune config
files, and does not prune generated ROW ONE site files.

## Matcher Rows

The cleanup path explicitly deletes related `item_entities` rows before deleting
`items`. It does not rely on SQLite foreign-key cascade behavior.

`--dry-run` reports how many item and item/entity rows would be deleted without
deleting them.

## What Is Not Pruned In v0.1.0

The cleanup command does not prune:

- `collector_runs`
- `source_health`
- `entity_first_seen`
- generated Markdown, JSON, or HTML report files
- generated ROW ONE site files
- config files

`collector_runs` and `source_health` remain available for source diagnostics.
Generated reports are filesystem artifacts and can be deleted manually when no
longer needed.

## `entity_first_seen`

`entity_first_seen` is intentionally retained across item pruning. It stores the
first and last accepted match timestamp for each `(entity_name, entity_type)`.

This prevents an old entity from being labeled `new` just because its old item
history was pruned.

Because item rows can be deleted later, `last_seen_at` may refer to item history
that is no longer retained in `items`. Treat it as stable entity-history
metadata, not as a guaranteed pointer to retained rows.

## Practical Guidance

- Start with `--dry-run`.
- Keep a longer retention period while tuning sources and aliases.
- Keep generated reports if you need a human-readable archive before pruning
  raw item history.
- Back up the SQLite database before aggressive cleanup.

For ROW ONE, use `row-one refresh --retention-days N` when you need longer local
history for scoring-window and heat-score comparisons. Use
`row-one refresh --skip-data-retention` only when the refresh should leave
SQLite item history untouched.
