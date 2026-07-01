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
