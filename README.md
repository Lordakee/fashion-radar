# Fashion Radar

Fashion Radar is a free-first, local-first fashion intelligence tool for daily
tracking of fashion signals across allowed public sources. It collects RSS or
RSSHub-compatible feeds and GDELT metadata, matches configurable brands,
designers, celebrities, products, categories, and trends, then writes local
Markdown/JSON reports and a read-only dashboard. It can also surface candidate
signals as observed phrases from configured sources and imported local signals
that need review before being tracked.

The MVP is built for personal research and editorial monitoring. It is not a
full social-listening service, and its heat scores are local metrics based only
on the sources you configure and local signals you import.

## What It Does

- Collects public RSS/Atom, RSSHub-compatible, and GDELT Doc API signals.
- Imports local user-provided CSV/JSON signal files that you are authorized to
  process.
- Stores conservative metadata in a local SQLite database.
- Matches entities with deterministic alias and context rules.
- Computes transparent heat scores over current and baseline windows.
- Surfaces untracked candidate signals as observed phrases from configured
  sources and imported local signals that need review.
- Compares local observed entity and candidate signal deltas between scoring
  snapshots.
- Generates daily Markdown and JSON reports with source attribution.
- Can package optional local digest artifacts such as latest report copies, a
  report index, and a local `.eml` handoff file.
- Provides an optional local Streamlit dashboard for read-only inspection.

## What It Does Not Do

Fashion Radar v0.1.0 does not include broad platform collection, account-based
source access, access-control bypasses, private data collection, or hidden
platform workarounds. Google News is not part of the default source set.
Manual signal import is a local input path, not a platform connector or source
acquisition guide.

Future non-core connectors, if ever added, must be explicit opt-ins with clear
risk labels. They are not required for the core workflow.

## Quickstart

Install dependencies with uv:

```bash
uv sync --locked --dev
```

For users in mainland China or slower networks, use a mirror only as a local
install aid:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
```

Do not regenerate or commit `uv.lock` from a mirror-backed lock operation. The
public lockfile should remain usable from the default PyPI registry. See
[docs/dependency-mirrors.md](docs/dependency-mirrors.md).

Create starter config, data, and report directories:

```bash
uv run fashion-radar init
uv run fashion-radar doctor
```

Run the daily workflow step by step:

```bash
uv run fashion-radar collect
uv run fashion-radar match
uv run fashion-radar report --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Optionally import local user-provided signals before matching:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export"
```

External community tools can target the local community signal contract:

```bash
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --dry-run
```

Review untracked candidate signals from configured sources and imported local
signals:

```bash
uv run fashion-radar candidates --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Compare local observed trend deltas without writing to the database:

```bash
uv run fashion-radar trends --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --config-dir "$PWD/configs"
```

Trend deltas are read-only local comparisons. They do not prove demand outside
your configured source set.

Or run the workflow serially:

```bash
uv run fashion-radar run --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Package local digest artifacts after a report or serial run:

```bash
uv run fashion-radar run --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --digest-latest copy --digest-index --digest-summary
```

Digest artifacts are local files only. Fashion Radar does not send email,
webhooks, or push notifications.

Print a daily scheduling example:

```bash
uv run fashion-radar schedule-example --mode cron --project-dir "$PWD"
```

By default, config/data/report directories use platform-specific user
directories. To keep everything inside a local workspace while experimenting:

```bash
export FASHION_RADAR_CONFIG_DIR="$PWD/configs"
export FASHION_RADAR_DATA_DIR="$PWD/data"
export FASHION_RADAR_REPORTS_DIR="$PWD/reports"
```

Generated SQLite databases and reports are ignored by git.

## Dashboard

The dashboard is optional:

```bash
uv sync --locked --dev --extra dashboard
uv run fashion-radar dashboard --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

Mirror install:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --extra dashboard
uv run fashion-radar dashboard
```

The dashboard defaults to `127.0.0.1:8501`, is read-only, and does not collect,
match, or fetch network data on page import or refresh. It shows local
mention-count summaries, reads candidate signals from the latest report JSON,
and can show a `Trend Deltas` tab computed from local SQLite state with the
configured scoring window. Candidate signals may be stale until a new report is
generated.

There is no authentication layer. Do not bind `--host 0.0.0.0` or any non-local
address on an untrusted network unless you understand that the dashboard may be
reachable by other machines.

See [docs/dashboard.md](docs/dashboard.md).

## Configuration

Starter files live in [configs](configs) and are also packaged for
`fashion-radar init`:

- `sources.example.yaml` defines enabled RSS/RSSHub/GDELT sources, source
  weights, HTTP settings, article extraction settings, and source-health
  circuit-breaker behavior.
- `entities.example.yaml` defines brands, designers, celebrities, products,
  categories, and trends. Broad aliases need context terms unless explicitly
  marked safe.
- `scoring.example.yaml` defines scoring windows, label thresholds, confidence
  filtering, source diversity bonuses, high-weight source bonuses, and optional
  candidate discovery thresholds.

Optional public-source starter packs live in [configs/source-packs](configs/source-packs).
See [docs/source-packs.md](docs/source-packs.md).

Check a source pack before copying or editing it:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml
```

The linter is local and read-only. It does not collect sources, fetch live
feeds, open SQLite, or create config/data/report artifacts.

## Reports And Storage

The local database defaults to `fashion-radar.sqlite` under the configured data
directory. Reports are written as:

```text
fashion-radar-YYYY-MM-DD.md
fashion-radar-YYYY-MM-DD.json
```

Reports contain source attribution, links, snippets/metadata, matched entities,
candidate signals from configured sources and imported local signals, and score
components. They should be reviewed before being shared publicly.

Optional local digest artifacts can make daily output easier to find:

```text
latest.md
latest.json
report-index.json
fashion-radar-YYYY-MM-DD.eml
```

See [docs/daily-digest.md](docs/daily-digest.md).

Use cleanup when you want to prune old collected items:

```bash
uv run fashion-radar clean-old-data --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30 --dry-run
uv run fashion-radar clean-old-data --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30
```

See [docs/data-retention.md](docs/data-retention.md).

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/source-boundaries.md](docs/source-boundaries.md)
- [docs/scoring.md](docs/scoring.md)
- [docs/candidate-discovery.md](docs/candidate-discovery.md)
- [docs/trend-deltas.md](docs/trend-deltas.md)
- [docs/daily-digest.md](docs/daily-digest.md)
- [docs/manual-signal-import.md](docs/manual-signal-import.md)
- [docs/community-signal-import.md](docs/community-signal-import.md)
- [docs/data-retention.md](docs/data-retention.md)
- [docs/dashboard.md](docs/dashboard.md)
- [docs/scheduling.md](docs/scheduling.md)
- [docs/source-packs.md](docs/source-packs.md)
- [docs/source-pack-quality.md](docs/source-pack-quality.md)
- [docs/github-upload-checklist.md](docs/github-upload-checklist.md)
- [docs/REVIEW_PROTOCOL.md](docs/REVIEW_PROTOCOL.md)

## Development

```bash
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Optional article text extraction uses the `article` extra:

```bash
uv sync --locked --dev --extra article
```

The core RSS/GDELT workflow does not require this extra. If `trafilatura` is not
installed, article extraction returns a conservative skipped result instead of
attempting a fallback page collector.

## GitHub Publishing Boundary

This repository can be prepared for GitHub locally, but the user controls remote
creation, pushing, PyPI publishing, and artifact uploads. Do not upload local
SQLite databases, generated reports, browser state, account/session artifacts,
secrets, build artifacts, or CodeGraph database files.
