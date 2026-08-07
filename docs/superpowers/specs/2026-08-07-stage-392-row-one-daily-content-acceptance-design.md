# ROW ONE Daily Content Acceptance Gate Design

## Goal

Prevent an unattended `fashion-radar row-one refresh` run from replacing a
usable existing ROW ONE site with a semantically empty or stale edition when
the current collection run did not produce enough current publishable signals.

## Problem

The current refresh path collects configured sources, matches stored items,
writes the dated report files, publishes the latest-only site, removes older
dated reports, and applies SQLite retention. Collector failures are represented
as `CollectorResult` values rather than necessarily raising an exception. A
run where every source fails, no source yields items, or all current-run items
are too old can therefore render successfully and replace the live site.

The Stage 391 publisher protects a valid live site from filesystem and process
failures. It correctly treats a structurally valid empty render as a successful
publication, because it has no semantic knowledge of daily content quality.
This stage adds that missing semantic gate before the publisher is reached.

## Decision

Add a pure, local evaluator named `evaluate_daily_content_acceptance`. It reads
only the `CollectorResult` values from the current refresh invocation, a
`DailyContentAcceptanceSettings` value, and the refresh `as_of` timestamp. It
returns a typed verdict with accepted/rejected status, observed counts, echoed
thresholds, and deterministic rejection reasons.

The gate runs immediately after collection and before entity matching. A normal
rejected refresh exits with code 1 before it writes daily report files, renders
or publishes ROW ONE, prunes dated report files, or starts SQLite retention.
The existing live site and existing generated report files remain untouched.

Collection itself is intentionally not rolled back. Collection writes collector
run metadata and any successfully collected items before the gate can inspect
the current results. A rejected run leaves those collection writes available for
diagnosis, but skips matching as well as every later report, site, and cleanup
write.

## Acceptance Inputs

The settings live in a dedicated top-level `daily_content_acceptance` section
of `ScoringConfig`, not in the scoring formula settings. This keeps publication
admission separate from heat-score configuration while retaining
`version: 1` and backward-compatible defaults.

```yaml
daily_content_acceptance:
  min_successful_collectors: 1
  min_fresh_items: 1
  max_fresh_item_age_hours: 48
```

All three values are positive integers. The default says that an automated run
needs at least one successful collector and at least one fresh item returned by
successful collectors in the current invocation. `failed` and `skipped`
collector results do not count as successful collectors.

An item is fresh when its normalized `published_at` is not in the future and is
no more than `max_fresh_item_age_hours` old relative to the supplied `as_of`.
The current item model always has `published_at`: several collectors synthesize
it from collection time when a source omits a date. Such dateless items count
as fresh under this stage because no source-date provenance field exists. This
stage still rejects explicit stale timestamps, zero usable items, and failed or
skipped-only collection.

## CLI Behavior

`row-one refresh` adds a one-shot `--allow-unaccepted-content` flag. The flag
does not alter settings, environment state, report behavior, or future scheduled
runs. When a rejected verdict is overridden, the command emits an explicit
warning before continuing. This supports deliberate manual empty-edition or
stale-edition rendering without silently weakening scheduled safety.

Without the flag, rejection prints a stable, greppable message beginning with
`ROW ONE refresh rejected:` followed by the deterministic reasons and a clear
statement that the live site and generated reports were preserved. It then exits
with status 1. A systemd timer or cron task therefore records the run as failed
and lets the operator inspect source conditions rather than treating an empty
edition as a successful daily update.

The ordinary `report`, `run`, `row-one build`, and `row-one preview` commands
remain permissive. This gate applies only to the unattended-oriented
`row-one refresh` workflow.

## Flow

```text
load config
  -> collect configured sources (collector run and collected-item writes)
  -> evaluate current-run content acceptance
      -> rejected: print diagnostics and exit 1
      -> accepted or explicit override: continue
  -> match stored items
  -> write dated report files
  -> recoverably publish latest ROW ONE site
  -> prune older dated reports
  -> apply optional SQLite retention
```

The gate has no filesystem, database, network, clock, or CLI dependency. The
CLI supplies the parsed UTC `as_of`, which makes the evaluator deterministic.

## Verification

Unit tests cover accepted fresh input and each rejection reason: empty results,
all failed, skipped-only, successful collection with zero items, stale-only
items, and future-dated items. Configuration tests cover defaults, invalid
thresholds, and the tracked example configuration.

CLI tests patch the shared refresh harness to return a fresh successful
`CollectorResult` for normal-path tests. Dedicated rejection tests prove that
the matcher, report writer, site publisher, report retention, and SQLite
retention are not invoked after rejection, and that a preexisting live site and
dated reports remain byte-for-byte present. Override tests prove that a rejected
verdict can continue only with the explicit flag and emits a warning.

Documentation and documentation tests describe the settings, fresh-date rule,
intentional exit-1 behavior, preserved site/report contract, and the fact that
collection writes are not rolled back.

## Non-Goals

This stage does not add new source acquisition, scraping, browser automation,
social connectors, paid services, proxies, remote workers, deployment, LLMs,
translation, image generation, new report or ROW ONE JSON schemas, URL changes,
scoring/ranking formula changes, rolling edition archives, zero-downtime
serving, or strict `ops-check` behavior. Those remain independent future nodes.
