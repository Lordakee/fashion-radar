# Trend Deltas

Trend deltas are read-only comparisons of local observed entity and candidate
signals between two scoring snapshots.

They compare configured sources and imported local signals only. They are not
verified demand, market-wide proof, real-time monitoring, or complete
social-platform coverage.

## CLI Usage

Compare the current local snapshot with the default baseline:

```bash
uv run fashion-radar trends --as-of 2026-06-12T00:00:00Z --config-dir ./configs
```

Compare against an explicit baseline and print JSON:

```bash
uv run fashion-radar trends --as-of 2026-06-12T00:00:00Z --baseline-as-of 2026-06-05T00:00:00Z --format json --limit 30 --include-dropped --config-dir ./configs
```

If `--baseline-as-of` is omitted, it defaults to:

```text
as_of - scoring.current_window_days
```

`--config-dir` loads `scoring.yaml` and optional `entities.yaml`. `--data-dir`
points to the existing local SQLite database. If the database is missing, the
command returns an empty comparison and does not create a database.

## What Is Compared

Entity deltas reuse the same local heat scoring used by reports.

Candidate deltas reuse candidate discovery snapshots. They are thresholded by
configured `candidate_discovery` settings, so they are not a complete raw phrase
inventory.

For trend deltas:

- `current_mentions` is the current comparison snapshot's current-window
  mention count.
- `baseline_mentions` is the baseline comparison snapshot's current-window
  mention count.
- Scoring's internal baseline-window counts are exposed only as
  `current_internal_baseline_mentions` and
  `baseline_internal_baseline_mentions`.

Existing signals are labeled `rising` or `cooling` only when score and mention
movement agree. Mixed-direction movement is `stable`. These statuses are local
observed signals for review, not market-wide rankings.

## Manual Signals

Manual imports participate only after they are imported and matched:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Manual Export"
uv run fashion-radar match
uv run fashion-radar trends --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Imported rows remain local user-provided signals. They do not add platform
coverage or external engagement data.

## Dashboard

The dashboard `Trend Deltas` tab computes the same local observed comparison
from existing SQLite state and the configured scoring window. It loads
`scoring.yaml` from `--config-dir`, uses optional `entities.yaml` when present,
and shows configuration or schema problems as dashboard warnings.

Trend dashboard reads are read-only. They do not initialize schema, migrate a
database, create trend tables, collect sources, run matching, generate reports,
or make network requests.
