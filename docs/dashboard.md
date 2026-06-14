# Dashboard

The dashboard is an optional Streamlit app for inspecting local Fashion Radar
state.

Install the extra:

```bash
uv sync --locked --dev --extra dashboard
```

Mirror install:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --extra dashboard
```

Run:

```bash
uv run fashion-radar dashboard
uv run fashion-radar dashboard --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

## Behavior

- Defaults to `127.0.0.1:8501`.
- Reads local SQLite/report state.
- Accepts the same config directory as the CLI through `--config-dir`.
- Does not collect sources.
- Does not run entity matching.
- Does not generate reports.
- Does not make network requests on import or refresh.
- Shows recent local signals in Daily Brief from retained SQLite rows, capped to
  report-safe snippets.
- Reads candidate signals from the latest report JSON when that file is
  available.
- Computes the Trend Deltas tab from existing local SQLite state and local
  scoring config, not from external services.
- Trend windows default to current UTC and use
  `as_of - scoring.current_window_days` for the baseline snapshot.
- Trend reads verify schema read-only and do not initialize, migrate, or write
  trend tables.
- Invalid or missing trend config shows a concise dashboard warning without
  creating the data directory or database.
- Daily Brief can show retained imported local rows as recent signals after
  import. Candidate Signals still require a newly generated report, and entity
  mention tabs require matching before imported rows appear as entity mentions.
- `imported-signals` can inspect retained imported rows from local SQLite before
  matching or report/dashboard review; it does not add a dashboard tab.

## Security

The dashboard has no authentication layer. It is intended for local use.

Do not bind `--host 0.0.0.0` or any non-local address on an untrusted network
unless you understand that other machines may be able to access it.

## Current Tabs

Dashboard tabs are read-only operational summaries:

- Daily Brief
- Candidate Signals
- Trend Deltas
- Brand Mentions
- Designer Mentions
- Celebrity Mentions
- Product Mentions
- Category Mentions
- Trend Mentions
- Source Health

Daily Brief shows local item and entity-match counts, the latest collection
timestamp, and recent local signals from SQLite. If the local database has not
been initialized or has no retained items, the tab shows an empty-state message
without creating the data directory or database.

The entity mention tabs are generated for every configured entity type
(`brand`, `designer`, `celebrity`, `product`, `category`, and `trend`) and rank
mention counts from the local database. They are not the full heat-score
ranking. Use the generated daily report for heat score, growth ratio, labels,
representative items, and score components.

The Candidate Signals tab reads the latest generated report JSON. Candidate
signals are observed phrases from configured sources and imported local signals
and need review. If the latest report was generated before the latest
collection, local import, or matching run, the tab may be stale until a new
report is written.

The Trend Deltas tab compares local observed entity and candidate signals
between two scoring snapshots. These directional signals need review and should
not be read as platform-wide popularity or market-wide demand.
