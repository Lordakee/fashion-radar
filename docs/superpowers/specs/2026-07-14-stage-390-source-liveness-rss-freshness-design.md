# Stage 390 Source Liveness RSS Freshness Design

## Goal

Make the read-only `source-liveness` diagnostic distinguish a currently active
RSS/RSSHub feed from a reachable feed whose newest dated entry is old, without
changing collection, storage, scoring, matching, reporting, ROW ONE generation,
or source configuration schemas.

## Product Gap

Fashion Radar is a daily fashion intelligence workflow, but the current RSS
liveness probe only proves that a feed can be fetched and contains entries. A
feed with many entries from weeks ago is reported as `live` and `ok`, exactly
like a feed updated today.

This weakens the roadmap requirement to expand curated public-source coverage
using source-liveness evidence. Source expansion should follow evidence that a
feed is both reachable and publishing current material. Stage 390 adds that
evidence before any source-pack expansion or collector filtering is attempted.

## Selected Approach

Use publication timestamps already present in the fetched RSS/RSSHub payload.
The probe will inspect parsed entry timestamps, identify the newest valid value,
measure its age against the existing `checked_at` time, and classify the result
with the current status and severity enums.

This is preferred over the two alternatives:

1. Immediate source-pack expansion would add breadth before the project can
   identify reachable but stale feeds.
2. Collector-side stale-item filtering would directly change daily content and
   could remove valid material from feeds that omit or misstate timestamps.

Stage 390 remains diagnostic-only. Its output can support a later source-pack
refresh or an explicitly designed collector freshness policy.

## Architecture

The change stays inside the existing source-liveness path:

1. The CLI accepts an RSS freshness threshold.
2. `build_source_liveness_report` passes the threshold to RSS/RSSHub probes.
3. `_probe_rss_source` derives timestamp evidence from the already parsed feed.
4. `SourceLivenessResult` exposes additive optional freshness fields.
5. Existing table and JSON output include the evidence.
6. Existing error, strict-mode, network, and no-write behavior is preserved.

GDELT behavior remains unchanged because its probe query is already bounded by
the configured `lookback_hours` through the GDELT `timespan` parameter.

## Technical Stack

- Python 3.11+
- feedparser entry dictionaries and parsed `struct_time` values
- `datetime`, `UTC`, and `timedelta` from the standard library
- Pydantic result models
- Typer CLI options
- pytest
- Ruff
- Existing Markdown documentation contract tests

No dependency or lockfile change is required.

## CLI Contract

Extend `source-liveness` with:

```text
--stale-after-hours INTEGER
```

The default is `72`. The option must accept integers greater than or equal to
one. It applies only to RSS and RSSHub sources. GDELT probes retain their current
query-time lookback behavior.

Examples:

```bash
fashion-radar source-liveness configs/sources.yaml
fashion-radar source-liveness configs/sources.yaml --stale-after-hours 48
fashion-radar source-liveness configs/sources.yaml --strict --stale-after-hours 48
```

Default mode still exits zero for warnings. `--strict` continues to exit nonzero
when any warning is present, including a stale feed warning. Existing errors
continue to exit nonzero in both modes.

## Result Model

Add these optional fields to `SourceLivenessResult` after `records_seen`:

```python
dated_records_seen: int | None = None
latest_entry_at: datetime | None = None
latest_entry_age_hours: int | None = None
```

Field semantics:

- `dated_records_seen` is the number of RSS/RSSHub entries with a valid parsed
  publication or update timestamp.
- `latest_entry_at` is the newest valid entry timestamp normalized to UTC.
- `latest_entry_age_hours` is the nonnegative whole-hour age at probe time.
- RSS/RSSHub probes that successfully parse a feed set `dated_records_seen`,
  including `0` for an empty feed or a feed with no valid entry dates.
- Fetch failures, disabled sources, and GDELT results leave all three fields
  `None`.

The fields are additive within `source-liveness/v1`. This command is a local
alpha diagnostic and the existing contract has already treated additive output
as compatible. No existing field is removed or retyped.

## Timestamp Selection

For each RSS/RSSHub entry:

1. Use `published_parsed` when it is present and valid.
2. Otherwise use `updated_parsed` when it is present and valid.
3. Ignore entries whose selected value cannot be converted to a UTC datetime.
4. Select the maximum valid datetime across all entries.

The conversion follows the existing RSS collector convention and uses the first
six `struct_time` components with `tzinfo=UTC`. Conversion failures are local to
that entry and do not fail the source probe.

Age calculation uses the exact time difference for threshold comparison:

```text
stale when checked_at - latest_entry_at > stale_after_hours
```

The displayed integer age is floored to whole hours. Future-dated entries are
clamped to an age of zero and are not treated as stale in this stage.

## Status Matrix

The existing five status values remain unchanged.

| Feed result | Status | Severity | Code |
| --- | --- | --- | --- |
| Entries and newest dated entry within threshold | `live` | `ok` | `null` |
| Entries and newest dated entry older than threshold | `degraded` | `warning` | `stale_feed` |
| Entries but no valid entry timestamps | `live` | `info` | `freshness_unknown` |
| Entries plus feedparser warning | `degraded` | `warning` | `malformed_feed` |
| No entries, valid feed | `empty` | `warning` | `empty_feed` |
| No entries, malformed feed | `failed` | `error` | `malformed_feed` |
| Fetch or unexpected probe exception | `failed` | `error` | `fetch_failed` |
| Disabled source | `skipped` | `info` | `source_disabled` |

Parser-warning precedence is retained. A bozo feed with entries remains
`malformed_feed` even when timestamp evidence is available. Its freshness fields
can still be populated so operators can inspect them without receiving two
competing status codes.

## Messages

Messages remain concise and report-safe. Representative output:

```text
Feed returned 12 entries; newest dated entry is 5 hours old.
Feed returned 12 entries; newest dated entry is 96 hours old, beyond the 72-hour freshness threshold.
Feed returned 12 entries; no parseable entry timestamps were available.
```

Existing malformed, empty, failed, and skipped messages retain their current
precedence and wording unless a small grammar adjustment is required by the
table layout.

## Table Output

Extend the result table with two compact columns:

```text
Source | Type | Status | Severity | Records | Dated | Latest age | Target | Message
```

Formatting:

- `Dated` is the integer count or `n/a`.
- `Latest age` is `<N>h` when known and `unknown` only for a nonempty,
  successfully parsed RSS/RSSHub feed with no valid dates. It is `n/a` for an
  empty feed and whenever freshness does not apply.
- Existing target and message sanitization remains unchanged.

No top-level `stale_count` is added. Stale feeds are already represented by the
existing `degraded_count` and `warning_count` fields.

## Error Handling

- Invalid CLI threshold values fail before network access through Typer option
  validation.
- Direct Python callers passing a value below one receive `ValueError` before
  config loading or network access.
- Missing, malformed, or partial entry timestamps never produce `failed`.
- One malformed timestamp does not discard valid timestamps from other entries.
- A malformed feed retains the existing parser-warning or parser-error outcome.
- Network clients are closed through the existing `finally` path.

## Documentation

Update these public contracts:

- `README.md`: current roadmap and source-liveness example wording.
- `docs/source-packs.md`: threshold option, freshness fields, and interpretation.
- `docs/source-pack-quality.md`: reachable does not imply fresh; stale evidence
  guides pack maintenance but does not rank sources.
- `docs/cli-reference.md`: document `--stale-after-hours`.
- `docs/architecture.md`: source-liveness now includes RSS timestamp evidence
  without collection or storage.
- `CHANGELOG.md`: add the Stage 390 Unreleased entry.

Documentation must continue to state that freshness evidence is point-in-time,
does not prove demand or platform coverage, and does not alter collection.

## Testing Strategy

### Model and JSON tests

- Extend the exact result JSON key contract with the three additive fields.
- Assert disabled, GDELT, and fetch-failed results serialize them as `null`.
- Assert RSS empty and no-date results set `dated_records_seen` to `0`.

### RSS behavior tests

- Fresh entry within the default threshold returns `live/ok`.
- The newest timestamp is selected across multiple entries.
- `published_parsed` takes precedence over `updated_parsed` per entry.
- An entry with only `updated_parsed` contributes valid freshness evidence.
- A feed older than the threshold returns `degraded/warning/stale_feed`.
- An exactly-on-threshold feed remains fresh; an entry one second beyond it is
  stale.
- A feed with entries but no valid timestamps returns
  `live/info/freshness_unknown`.
- Invalid timestamps are ignored when another entry has a valid timestamp.
- Future timestamps produce age `0` and do not become stale.
- A bozo feed with entries retains `malformed_feed` precedence while exposing
  any valid freshness fields.
- RSSHub follows the same freshness path.

### CLI tests

- Help includes `--stale-after-hours` and its default.
- A custom threshold reaches `build_source_liveness_report`.
- Values below one are rejected before the builder or network is called.
- Default mode exits zero for stale warnings.
- Strict mode exits nonzero for stale warnings.
- JSON and table outputs expose the new evidence.

### Regression tests

- GDELT request parameters remain unchanged.
- Existing source ordering, disabled-source skipping, exception isolation, and
  client-closing tests remain green.
- No source config, SQLite, collector, scoring, ROW ONE app, runtime, manifest,
  or generated-site contract changes.

## Parallel Implementation Boundaries

The implementation can use disjoint workers after the reviewed plan is
accepted:

- Worker A: `src/fashion_radar/source_liveness.py` and
  `tests/test_source_liveness.py`.
- Worker B: `src/fashion_radar/cli.py` and focused CLI tests.
- Worker C: public documentation and documentation contract tests.
- Coordinator: design/plan/review records, integration, changelog, full
  verification, release review, and Git publication.

Worker A and Worker B share the builder signature contract but not writable
files. The coordinator must define the exact signature in the implementation
plan before parallel work begins. No two workers may edit the same test file.

## Non-Goals

- No new source, connector, API, scraper, browser automation, or login flow.
- No source-pack additions or endpoint replacements in Stage 390.
- No collector-side filtering or changes to `published_at`/`collected_at`.
- No SQLite writes, source-health writes, scoring, matching, report, or ROW ONE
  behavior changes.
- No article-page fetches or body extraction.
- No per-source freshness schema field.
- No GDELT behavior or response-field changes.
- No source ranking, demand proof, recommendation, personalization, analytics,
  platform coverage verification, or compliance-review product feature.
- No dependency or `uv.lock` change.

## Acceptance Criteria

Stage 390 is complete when:

1. RSS/RSSHub liveness output exposes dated-entry count, latest timestamp, and
   latest age using only the already fetched feed payload.
2. Stale feeds are `degraded/warning/stale_feed`; no-date feeds are
   `live/info/freshness_unknown`.
3. The default threshold is 72 hours and is configurable through the CLI.
4. Default and strict exit semantics remain consistent with existing warning
   behavior.
5. GDELT and all non-RSS paths retain their current behavior.
6. The source-liveness command remains bounded, network-read-only, and free-first.
7. Focused and full tests, Ruff, release hygiene, package checks, and review
   gates pass without a lockfile change.
