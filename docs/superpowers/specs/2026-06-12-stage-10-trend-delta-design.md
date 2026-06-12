# Stage 10 Trend Delta Design

## Goal

Add a local, read-only trend delta view that answers: which tracked fashion
brands, designers, celebrities, products, categories, trends, and candidate
phrases are rising, new in the current comparison snapshot, stable, or cooling
in the local Fashion Radar database.

This stage uses only data that already exists locally, including items imported
through the Stage 9 manual signal importer and items collected by configured
RSS/RSSHub/GDELT sources. It does not add platform collection.

## Non-Goals

Stage 10 does not implement:

- Social platform search, scraping, crawling, browser automation, or account
  automation.
- Instagram, TikTok, X/Twitter, Xiaohongshu, or other platform APIs.
- Login cookies, account/session files, browser profiles, tokens, credentials,
  proxies, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass.
- Private data collection, comments, DMs, account IDs, follower lists, raw
  engagement counts, images, videos, or media downloading.
- Market-wide or real-time trend claims.
- LLM scoring, embeddings, vector databases, image recognition, or paid
  services.
- Schema migrations, persistent trend tables, writable trend indexes, or any
  database writes. Trend deltas are computed on demand from existing local
  tables.

All trend language must stay framed as local observed signals that need human
review.

The "no external services" boundary applies to Fashion Radar runtime behavior.
Development verification may still use existing project tooling such as `uv`
sync checks, package-index mirrors, and Claude Code review gates.

## Recommended Approach

Add a read-only `fashion-radar trends` command and a dashboard trend tab.

The command compares two scoring snapshots:

```bash
fashion-radar trends --as-of 2026-06-12T00:00:00Z --config-dir ./configs
fashion-radar trends --as-of 2026-06-12T00:00:00Z --baseline-as-of 2026-06-05T00:00:00Z --config-dir ./configs
fashion-radar trends --as-of 2026-06-12T00:00:00Z --format json --limit 30 --config-dir ./configs
```

If `--baseline-as-of` is omitted, the baseline defaults to
`as_of - scoring.current_window_days`. This default gives a simple week-over-week
comparison with the repository's current default scoring configuration.

The command must be read-only:

- If the database file is missing, print an empty trend result and do not create
  `data_dir` or a SQLite database.
- If config is missing or invalid, or dates are invalid, exit non-zero before
  opening the database and do not create `data_dir`.
- Reject `baseline_as_of >= as_of` with a concise non-zero error before opening
  the database.
- If the database exists, open it in SQLite read-only URI mode.
- Verify the schema version before reading in both CLI and dashboard paths,
  including tables needed by entity scoring such as `entity_first_seen`.
- Never call `initialize_schema()` from the trends command.
- Never initialize, migrate, or mutate an incompatible existing database.

## Data Flow

```text
config/scoring.yaml + optional config/entities.yaml
  -> read-only SQLite database
  -> score_entities(as_of=current)
  -> score_entities(as_of=baseline)
  -> discover_candidates(as_of=current)
  -> discover_candidates(as_of=baseline)
  -> compare metrics by stable normalized keys
  -> print table/json and show dashboard tab
```

The comparison operates on metrics already computed by existing scoring and
candidate discovery code. Stage 10 should not invent a new heat formula.

## Trend Delta Model

Create small Pydantic models for trend output:

- `TrendSignalKind`: `entity` or `candidate`.
- `TrendStatus`: `new`, `rising`, `cooling`, `stable`, or `dropped`.
- `TrendDelta`: one comparable signal.
- `TrendComparison`: metadata plus a list of deltas.

Each `TrendDelta` should include:

- `signal_kind`
- `comparison_key`
- `name`
- `signal_type`
- `status`
- `current_label`
- `baseline_label`
- `current_score`
- `baseline_score`
- `score_delta`
- `current_mentions`
- `baseline_mentions`
- `mention_delta`
- `current_internal_baseline_mentions`
- `baseline_internal_baseline_mentions`
- `current_growth_ratio`
- `baseline_growth_ratio`
- `current_distinct_sources`
- `baseline_distinct_sources`
- `distinct_source_delta`
- `first_seen_at`

For trend deltas, `current_mentions` means the current comparison snapshot's
current-window mention count. `baseline_mentions` means the baseline comparison
snapshot's current-window mention count. Therefore:

```text
mention_delta = current_snapshot.current_mentions - baseline_snapshot.current_mentions
```

Existing metric fields also named `baseline_mentions` are internal
baseline-window counts used by scoring. If Stage 10 exposes those counts, it
must use explicit names: `current_internal_baseline_mentions` and
`baseline_internal_baseline_mentions`.

The output intentionally excludes raw post text, comments, author/account
metadata, media, and platform internals.

## Comparison Rules

Entity key:

```text
entity:<entity_type>:<normalized entity name>
```

Candidate key:

```text
candidate:<candidate_type>:<normalized phrase>
```

Entity and candidate comparison keys must use the repository's existing
normalization behavior, specifically `normalize_alias_key()`. Do not use ad hoc
lowercasing or punctuation stripping.

Each output delta should include the normalized `comparison_key` used for
matching and deterministic sorting. This key is derived from local entity or
candidate names only; it must not include raw post text, URLs, account metadata,
or platform internals.

Status rules:

- `new`: present in the current comparison snapshot and absent from the
  baseline comparison snapshot. This does not necessarily mean first observed
  locally.
- `dropped`: absent from current snapshot and present in baseline, only when
  `--include-dropped` is set.
- `rising`: present in both snapshots with `score_delta > 0` and
  `mention_delta >= 0`, or `score_delta == 0` and `mention_delta > 0`.
- `cooling`: present in both snapshots with `score_delta < 0` and
  `mention_delta <= 0`, or `score_delta == 0` and `mention_delta < 0`.
- `stable`: present in both snapshots with no movement, or with mixed-direction
  movement such as `score_delta > 0` and `mention_delta < 0`, or
  `score_delta < 0` and `mention_delta > 0`.

Score and mention movement must agree before Stage 10 labels an existing signal
as rising or cooling. Mixed-direction changes are `stable` because the local
evidence is not directionally clear enough for a stronger status label.

Candidate deltas are based on candidates discoverable under existing
candidate-discovery thresholds. They are not a complete raw phrase inventory.

Sorting:

1. `new`
2. `rising`
3. `cooling`
4. `stable`
5. `dropped`

Within each status, sort by descending absolute score delta, descending current
score, descending current mentions, name, signal kind, signal type, and
normalized comparison key. The final tie-breakers avoid relying on dict or input
iteration order when same-name signals exist across kinds or types.

The table output should favor scanability: status, kind, type, name, current
score, score delta, mention delta, current label, and baseline label.

## CLI Behavior

New command:

```bash
fashion-radar trends [OPTIONS]
```

Options:

- `--config-dir PATH`
- `--data-dir PATH`
- `--as-of TEXT`
- `--baseline-as-of TEXT`
- `--limit INTEGER`
- `--format table|json`
- `--include-dropped / --no-include-dropped`

Invalid config or invalid dates should print concise errors and exit non-zero.
If `baseline_as_of >= as_of`, the command should print a concise non-zero error.

No database should be created for missing DB, invalid config, or invalid dates.

## Dashboard Behavior

Add a local trend tab to the Streamlit dashboard:

- Read the existing local database only.
- Use the same config directory as the CLI. Stage 10 should add a dashboard
  `--config-dir` argument and pass it through the `fashion-radar dashboard`
  launcher so scoring windows, candidate settings, and tracked entities stay
  consistent between CLI and dashboard trend views.
- If config is missing or invalid, show a concise dashboard error without
  creating the data directory or database.
- Use the latest local `collected_at` timestamp as the default dashboard
  `as_of` when any local items exist. Fall back to current UTC only when the
  database exists but contains no items.
- Compare dashboard `as_of` to `as_of - current_window_days` using the loaded
  scoring settings.
- Verify schema version before reading with the same read-only schema guard as
  the CLI, and do not initialize or migrate schema.
- Show local observed signal deltas with status badges and score/mention deltas.
- If no database or no entity/candidate deltas exist, show an empty state.
- Do not claim platform-wide or market-wide popularity.
- If an incompatible existing database makes global dashboard summary queries
  fail, the dashboard should still surface a concise read-only schema error
  instead of initializing or migrating the database.

The dashboard copy should say "local observed signals" or equivalent wording.

## Documentation

Document:

- The command is read-only.
- It compares local observed signals only.
- Manual imports can participate after users run `import-signals` and `match`.
- The output is a prioritization aid, not verified demand.
- Missing social platform support is intentional and remains out of scope for
  the local/free core.

## Verification

Before code review:

- Focused trend model/comparator tests, including mixed movement and equality
  status cases, same-name ordering, internal baseline counts, and normalization
  behavior.
- Focused CLI tests for missing DB, invalid dates, invalid config,
  incompatible existing DBs, JSON output, `--include-dropped`, `--limit`,
  default baseline, help output, and read-only behavior.
- Direct integration tests proving trend comparison composes existing
  deterministic entity scoring and candidate discovery.
- Dashboard helper and render/copy tests, including config loading,
  incompatible database behavior, dashboard default `as_of` selection, invalid
  config no-creation behavior, and visible local-observed wording.
- Full `pytest`.
- `ruff check .`.
- `ruff format --check .`.
- `uv lock --check`.
- `uv sync --locked --dev --check`.
- `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`.
- Wheel build and installed CLI smoke for `fashion-radar trends --help`.
- CodeGraph status.
- Claude Code code review with `--effort max`.
