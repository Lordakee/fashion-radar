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
- Preserves optional imported `platform` labels as local provenance in SQLite
  and imported-row review output only.
- Lints local community signal CSV/JSON files against the handoff contract
  before import, without fetching URLs or importing rows.
- Prints a local community directory handoff checklist without reading the
  supplied directory or running the generated commands.
- Reviews retained `manual_import` rows already stored in local SQLite without
  importing, collecting, matching, scoring, or writing reports.
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
Stored imported `platform` labels are local provenance metadata only; they are
not scraping, crawling, social connectors, source acquisition, platform
coverage, or demand proof.

Future non-core connectors, if ever added, must be explicit opt-ins with clear
risk labels. They are not required for the core workflow.

## Quickstart

For a source checkout, install dependencies with uv:

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

Package readiness is checked separately before upload by building and smoking a
local wheel from this checkout; that check does not publish to PyPI. See
[docs/github-upload-checklist.md](docs/github-upload-checklist.md).

Create starter config, initialize the repo-local SQLite schema, and check the
same repo-local workspace:

```bash
uv run fashion-radar init --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
uv run fashion-radar migrate-db --data-dir "$PWD/data"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

`doctor` reports database schema status read-only. `migrate-db` only performs
local schema initialization or upgrades; it does not collect, import, match,
score, report, monitor, watch, schedule, or touch external platforms.

### Manual Repo-Local Sample Flow

Use the checked-in community signal example when you want a deterministic
first run that produces local output without live source collection. This
manual flow writes to the repo-local `data/` and `reports/` directories shown
in the commands:

```bash
AS_OF="2026-06-13T12:00:00Z"

uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$AS_OF"
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
test -s reports/fashion-radar-2026-06-13.md
test -s reports/fashion-radar-2026-06-13.json
```

### Automated First-Run Smoke

The automated local sample smoke runs the same path in temporary config, data,
report, and export directories, then verifies generated report artifacts there.
It should not create files under repo `data/` or `reports/`:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

This path does not run live collection, scraping, platform automation,
monitoring, scheduling, or external services. Candidate and trend JSON commands
are execution smoke checks; their local business results depend on the checked
example rows and current starter config.

Run the daily workflow step by step:

```bash
uv run fashion-radar collect --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Optionally import local user-provided signals before matching:

```bash
uv run fashion-radar import-signals ./signals.csv --format csv --source-name "Manual Export" --data-dir "$PWD/data"
```

External community tools can target the local community signal contract:

```bash
AS_OF="2026-06-13T12:00:00Z"
tmp_run="$(mktemp -d)"
mkdir -p "$tmp_run/exports"
cp examples/community-signals.example.csv "$tmp_run/exports/community-signals.csv"
uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar community-handoff-workflow "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar community-signal-lint-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --source-name "Community Tool Export"
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
```

Inspect retained imported rows before matching or downstream review:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data" --format json
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$AS_OF"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$AS_OF" --format json
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF"
uv run fashion-radar imported-candidates --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --phrase "Le Teckel bag"
uv run fashion-radar imported-candidate-evidence --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --phrase "Le Teckel bag" --source-name "Community Tool Export" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --unmatched-only
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --format json
```

`imported-review-workflow` is local and does not execute commands. It prints a
copyable review sequence for existing local commands after manual signal import.

`imported-candidates` is local and read-only. It surfaces observed candidate
phrases from retained `manual_import` rows only. These phrases need review and
are not verified entities, demand proof, or platform coverage.

`imported-candidate-evidence` is local and read-only. It shows retained
`manual_import` rows whose extracted candidate phrases match one requested
phrase. Evidence rows are review aids and are not verified entities, demand
proof, or platform coverage.

`community-candidates` is local and read-only. It previews aggregate candidate
phrase metrics from one supplied community signal CSV/JSON file before import.
It does not store rows, open SQLite, fetch URLs, print the supplied input file
path, or expose row URLs, row titles, summaries, raw text, normalized keys,
candidate contexts, or representative item details. The output is not proof of demand, not platform coverage, and not source ranking.

`community-candidates-dir` is local and read-only. It previews aggregate
candidate phrase metrics from matched regular CSV/JSON handoff files directly
under one supplied directory before import. It does not recurse, import rows,
open SQLite, fetch URLs, print the supplied directory path, expose matched file
paths, expose matched file names, or expose row URLs, row titles, summaries,
raw text, normalized keys, candidate contexts, raw validation findings,
account/private fields, or representative item details. The output is not proof
of demand, not platform coverage, and not source ranking.

`community-handoff-workflow` is local and print-only. It prints the ordered
local sequence `community-signal-lint-dir`, `community-candidates-dir`,
`import-signals-dir --dry-run`, `import-signals-dir`, and
`imported-review-workflow` for a supplied directory. It does not execute
commands, read the supplied directory, validate files, import rows, open or
write SQLite, fetch URLs, log in, download media, automate browsers, scrape,
monitor, watch folders, schedule work, add source/platform connectors, prove
demand, verify platform coverage, rank sources, write reports, update
dashboards, generate configs, or generate entity files. It intentionally prints
the supplied directory/config/data paths inside copyable local commands; this
differs from aggregate candidate preview output, which suppresses paths and row
details.

Review untracked candidate signals from configured sources and imported local
signals:

```bash
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Compare local observed trend deltas without writing to the database:

```bash
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Trend deltas are read-only local comparisons. They do not prove demand outside
your configured source set.

Or run the workflow serially:

```bash
uv run fashion-radar run --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Package local digest artifacts after a report or serial run:

```bash
uv run fashion-radar run --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --digest-latest copy --digest-index --digest-summary
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
uv run fashion-radar dashboard --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --host 127.0.0.1 --port 8501
```

Run the manual repo-local sample flow first when you want the dashboard to open
against a freshly generated sample report in the same `reports` directory.

Mirror install:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --extra dashboard
uv run fashion-radar dashboard
```

The dashboard defaults to `127.0.0.1:8501`, is read-only, and does not collect,
match, or fetch network data on page import or refresh. It shows local
mention-count summaries, reads candidate signals from the latest report JSON,
and can show a `Trend Deltas` tab computed from local SQLite state with the
configured scoring window. This local read does not create trend tables or write
database state. Candidate signals may be stale until a new report is generated.

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
  categories, and trends. Single-word/common aliases may need context terms
  unless explicitly marked safe with a reason; ordinary multi-word aliases can
  match without context under current matcher rules.
- `scoring.example.yaml` defines scoring windows, label thresholds, confidence
  filtering, source diversity bonuses, high-weight source bonuses, and optional
  candidate discovery thresholds.

Optional public-source starter packs live in [configs/source-packs](configs/source-packs).
See [docs/source-packs.md](docs/source-packs.md).

Optional entity watchlist packs live in [configs/entity-packs](configs/entity-packs).
See [docs/entity-packs.md](docs/entity-packs.md).

Check a source pack before copying or editing it:

```bash
uv run fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
```

Check an entity pack before copying or editing it:

```bash
uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
```

Check a community signal handoff file before import:

```bash
uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
```

Check a directory of community signal handoff files before choosing files to dry
run or import:

```bash
AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar community-handoff-workflow ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --source-name "Community Tool Export"
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
```

The linters are local and read-only. They do not collect sources, fetch live
feeds or URLs, run matching/scoring, open SQLite, import rows, or create
config/data/report artifacts.

`import-signals-dir --dry-run` is also local and read-only. It validates matched
regular files directly under one local directory through the same importer model
as `import-signals --dry-run`; it does not recurse, open SQLite, import rows, or
create config/data/report artifacts.

`import-signals-dir` without `--dry-run` imports the same matched local files
only after every matched file validates. Validation failures import nothing and
do not create the data directory or SQLite database.

`community-handoff-workflow` can print the same directory handoff order before
you run any step. It prints copyable commands only; it does not execute them,
read the supplied directory, validate files, import rows, open or write SQLite,
fetch URLs, log in, download media, automate browsers, scrape, monitor, watch
folders, schedule work, add source/platform connectors, prove demand, verify
platform coverage, rank sources, write reports, update dashboards, generate
configs, or generate entity files.

`imported-signals` is local and read-only. It opens an existing SQLite database
in read-only mode and returns retained rows where `source_type` is
`manual_import`, including stored `platform` labels when present; it does not
import rows, fetch URLs, run matching/scoring, generate reports, monitor
folders, infer platform coverage, or create dashboard/report artifacts.

`imported-signals-summary` is local and read-only. It opens an existing SQLite
database in read-only mode and groups retained `manual_import` rows by stored
`source_name` and local `platform` provenance labels where present, showing row
counts and item-level stored match presence without exposing row titles, URLs,
summaries, import file paths, or match details. `source_name` and `platform` are
stored local provenance labels, not statements about anything outside the local
database.

`imported-entity-deltas` is local and read-only. It compares stored matched
entities on retained `manual_import` rows across collected-at windows and
prints aggregate entity counts only.

`imported-candidates` is local and read-only. It opens an existing SQLite
database in read-only mode and computes review-oriented candidate signals from
retained `manual_import` rows only; it does not import rows, fetch URLs, run
entity matching, write scores, generate reports, monitor folders, or create
dashboard/report artifacts.

`imported-candidate-evidence` is local and read-only. It opens an existing
SQLite database in read-only mode and shows phrase-scoped retained
`manual_import` evidence rows. It does not import rows, run entity matching,
write scores, generate reports, monitor folders, or create dashboard/report
artifacts.

## Reports And Storage

The local database defaults to `fashion-radar.sqlite` under the configured data
directory. Use `uv run fashion-radar migrate-db --data-dir "$PWD/data"` when
you want to initialize or upgrade that local SQLite schema explicitly. Reports
are written as:

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
uv run fashion-radar clean-old-data --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30 --dry-run
uv run fashion-radar clean-old-data --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30
```

See [docs/data-retention.md](docs/data-retention.md).

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/cli-reference.md](docs/cli-reference.md)
- [docs/source-boundaries.md](docs/source-boundaries.md)
- [docs/dependency-mirrors.md](docs/dependency-mirrors.md)
- [docs/scoring.md](docs/scoring.md)
- [docs/candidate-discovery.md](docs/candidate-discovery.md)
- [docs/trend-deltas.md](docs/trend-deltas.md)
- [docs/daily-digest.md](docs/daily-digest.md)
- [docs/manual-signal-import.md](docs/manual-signal-import.md)
- [docs/community-signal-import.md](docs/community-signal-import.md)
- [docs/community-signal-quality.md](docs/community-signal-quality.md)
- [docs/entity-packs.md](docs/entity-packs.md)
- [docs/entity-pack-quality.md](docs/entity-pack-quality.md)
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

For PR/release verification, use [CONTRIBUTING.md](CONTRIBUTING.md) or
[docs/github-upload-checklist.md](docs/github-upload-checklist.md); public
lockfile checks should use `UV_NO_CONFIG=1`.

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
