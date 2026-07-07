# Stage 330 ROW ONE Refresh Data Retention Design

## Goal

Wire local SQLite data retention into `row-one refresh` so the daily ROW ONE
website path does not keep accumulating old collected item rows after the
current edition has been generated.

## Product Gap Closed

The user asked for a local daily ROW ONE site that saves today's content locally
and removes the previous records after the next update so the test deployment
does not consume disk unnecessarily.

ROW ONE already performs two presentation-layer cleanup steps:

- `row-one refresh` rebuilds the generated ROW ONE site with `latest_only=True`.
- `row-one refresh` prunes stale dated Markdown/JSON/HTML report artifacts.

The remaining gap is SQLite retention: collected `items` and related
`item_entities` matcher rows remain in the local database until the standalone
`clean-old-data` command is run. Stage 330 makes the daily ROW ONE refresh path
run that existing retention primitive after a successful site/report refresh.

## Scope

- Add ROW ONE refresh data retention after successful collection, matching,
  report generation, site generation, and report artifact pruning.
- Reuse the existing `clean_old_data()` workflow primitive.
- Default ROW ONE refresh retention to `1` day to match the user's test-site
  request for near-daily cleanup.
- Add `--retention-days` to `row-one refresh` so the operator can keep a longer
  local history when needed.
- Add `--skip-data-retention` to `row-one refresh` for explicit opt-out.
- Print SQLite retention counts in `row-one refresh` output.
- Keep `clean-old-data` as the standalone/manual retention command.
- Update local ops, install/schedule docs, and tests to describe that scheduled
  ROW ONE refresh includes default SQLite retention.

## Non-Goals

- Do not change the scoring algorithm, entity matching, candidate discovery,
  source collection, article extraction, LLM behavior, connectors, or generated
  site routes.
- Do not delete `collector_runs`, `source_health`, `entity_first_seen`, config
  files, generated ROW ONE site files, generated report artifacts outside the
  existing report-artifact retention path, or any non-SQLite data.
- Do not add systemd enablement checks, call `systemctl`, start/stop servers, or
  mutate user systemd units.
- Do not change `row-one-app/v7`, `row-one-manifest/v1`,
  `row-one-runtime/v1`, schemas, detail routes, paragraph anchors, market
  grouping, domestic/international classification, or compliance-review
  behavior.
- Do not add dependencies.

## Behavior

`row-one refresh` should:

1. Load configs.
2. Collect configured sources.
3. Match stored items.
4. Write daily report files.
5. Build the ROW ONE generated site with `latest_only=True`.
6. Prune stale dated report artifacts.
7. Unless `--skip-data-retention` is passed, call:

```python
clean_old_data(data_dir=data_dir, as_of=as_of, retention_days=retention_days)
```

The cleanup happens after the current site/report has been generated, so the
current refresh can still use the data it just collected. The retained SQLite
window controls future local history and disk use.

CLI output should include:

```text
SQLite retention: pruned <N> old items and <M> item/entity matches; retention window <D> days
```

When skipped:

```text
SQLite retention: skipped
```

If SQLite retention fails after the current report and site have been generated,
the command should print a warning such as:

```text
SQLite retention: failed: <reason>
```

and still exit successfully for the completed refresh. The warning makes the
cleanup failure visible without hiding that today's generated site/report work
finished.

## Defaults

- `row-one refresh --retention-days` defaults to `1`.
- The standalone `clean-old-data` command keeps its existing default retention
  window.

This intentionally makes the ROW ONE daily test-site workflow more aggressive
than the general Fashion Radar retention command.

Operators who need multi-day heat/scoring history should increase
`--retention-days`. A 1-day SQLite retention window is disk-friendly for the
test-site workflow, but it also limits the local item history available to
future heat scores and scoring-window comparisons.

## Testing

Use TDD:

- CLI pipeline test proves `clean_old_data` runs after report artifact pruning.
- CLI output test proves item and matcher prune counts are displayed.
- CLI opt-out test proves `--skip-data-retention` skips cleanup.
- CLI help test proves `--retention-days` and `--skip-data-retention` are
  discoverable.
- A real SQLite integration test proves `row-one refresh` prunes old `items`
  and `item_entities` while keeping current rows.
- Docs tests prove ROW ONE refresh retention is documented and old docs no
  longer say ROW ONE leaves SQLite retention entirely to `clean-old-data`.
