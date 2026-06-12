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
```

## Behavior

- Defaults to `127.0.0.1:8501`.
- Reads local SQLite/report state.
- Does not collect sources.
- Does not run entity matching.
- Does not generate reports.
- Does not make network requests on import or refresh.
- Reads candidate signals from the latest report JSON when that file is
  available.
- Reflects imported local signals only after those rows have been matched and a
  new report has been generated.

## Security

The dashboard has no authentication layer. It is intended for local use.

Do not bind `--host 0.0.0.0` or any non-local address on an untrusted network
unless you understand that other machines may be able to access it.

## Current Tabs

Dashboard tabs are read-only operational summaries:

- Daily Brief
- Brand Mentions
- Product Mentions
- Celebrity Mentions
- Source Health
- Candidate Signals

The brand/product/celebrity tabs rank mention counts from the local database.
They are not the full heat-score ranking. Use the generated daily report for
heat score, growth ratio, labels, and score components.

The Candidate Signals tab reads the latest generated report JSON. Candidate
signals are observed phrases from configured sources and imported local signals
and need review. If the latest report was generated before the latest
collection, local import, or matching run, the tab may be stale until a new
report is written.
