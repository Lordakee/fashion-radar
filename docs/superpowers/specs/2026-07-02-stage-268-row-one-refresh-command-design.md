# Stage 268 ROW ONE Refresh Command Design

## Objective

Add a single `row-one refresh` command that turns the current manual daily chain into one reusable local operation:

1. collect configured sources;
2. match stored items to configured entities;
3. write the dated Markdown/JSON/HTML daily report;
4. rebuild the ROW ONE static site with `--latest-only`;
5. print the generated site, app JSON, manifest, readiness, and fixed local URL.

This is the next operational step toward the ROW ONE local daily site goal. It does not install timers, run a persistent server, add new collectors, add LLM calls, or change the ROW ONE app/site schema.

## Current State

- `fashion-radar run` already performs collect -> match -> report generation in one command.
- `fashion-radar row-one build` already builds the ROW ONE static site from the current local database/report state.
- `fashion-radar row-one schedule` and `row-one local-ops` already print 04:00 cron/systemd examples, but those examples still contain a shell chain instead of a single refresh command.
- `row-one preview` prints `Manifest: <site>/data/manifest.json`, and first-run smoke verifies the generated manifest plus `row-one serve --dry-run`.

## Proposed Shape

Add:

```bash
fashion-radar row-one refresh \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --output-dir reports/row-one/site \
  --as-of 2026-07-02T04:00:00Z \
  --host 127.0.0.1 \
  --port 8787
```

The command should:

- load `sources.yaml`, `entities.yaml`, and `scoring.yaml`;
- call existing workflow functions instead of shelling out to the CLI;
- always rebuild ROW ONE with `latest_only=True`;
- print report paths and ROW ONE readiness in a stable, testable order;
- print the same fixed URL message used by `row-one serve --dry-run`;
- fail clearly on invalid config or workflow errors.

## Non-Goals

- No timer installation or service management.
- No daemon/process supervision.
- No hard "today-only" database pruning.
- No new social platform integrations or collector behavior.
- No schema changes to `row-one-app/v1` or `row-one-manifest/v1`.
- No compliance-review product features.

## Implementation Notes

- Keep the command in `src/fashion_radar/cli.py` near other `row-one` commands.
- Reuse `collect_configured_sources`, `match_stored_items`, `write_daily_report_files`, `_write_row_one_site_from_cli_options`, `build_row_one_readiness`, and `format_row_one_site_access_message`.
- Update `render_row_one_cron_example`, `render_row_one_systemd_service`, and `render_row_one_local_ops_runbook` so generated local ops snippets call `fashion-radar row-one refresh` instead of maintaining a duplicated shell chain.
- Update first-run smoke validators, fake outputs, and deterministic command ordering so schedule/local-ops checks expect the single `row-one refresh` entrypoint.

## Acceptance Evidence

- CLI tests prove `row-one refresh` calls collect, match, report, and ROW ONE build in order.
- CLI tests prove the command prints report paths, site paths, manifest path, readiness counts, and fixed URL.
- Scheduling/local-ops tests prove generated snippets call `row-one refresh`.
- Docs tests prove the refresh command is documented as the single 04:00 automation entrypoint.
- Focused verification passes for CLI, docs, and first-run smoke.
