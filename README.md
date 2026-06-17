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
- Documents sanitized CSV/JSON local file handoff templates for
  user-controlled external/community tools.
- Prints the `external-tool-adapters` external social/community tool adapter
  registry as a local producer-discovery registry for mapping
  user-controlled external/community tools to the sanitized CSV/JSON local file
  handoff contract.
- Prints `external-tool-template` adapter-specific template rows for
  user-controlled external/community tools that need sanitized CSV/JSON local
  file handoff examples.
- Prints `external-tool-workflow` workflow metadata for user-controlled
  external/community tools that need a producer-facing wrapper around existing
  local commands before writing sanitized CSV/JSON local file handoff rows.
  JSON output is workflow metadata, not importable handoff rows.
- Checks `external-tool-readiness` local command availability for known free
  external/community tools and prints readiness guidance, mirror-friendly
  install hints, and Fashion Radar next-step handoff commands without
  installing dependencies or running upstream tools.
- Prints the community signal producer contract for user-controlled local tools
  without reading handoff files, acquiring sources, monitoring platforms, or
  performing compliance review.
- Prints a local community directory handoff checklist with a
  `review_handoff_readiness` step for the `community-handoff-check-dir`
  local-only handoff readiness report before importing rows; it does not
  execute commands, read the supplied directory, or run the generated commands.
- Prints a local-only community directory handoff readiness report without
  importing rows or writing SQLite.
- Reviews retained `manual_import` rows already stored in local SQLite without
  importing, collecting, matching, scoring, or writing reports.
- Reviews privacy-safe imported-only entity evidence for one matched entity
  from retained local rows without scraping, browser automation, platform APIs,
  or account or cookie behavior.
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

The external tool handoff templates are sanitized CSV/JSON local file handoff
templates for user-controlled external/community tools:
[examples/community-tool-handoff.example.csv](examples/community-tool-handoff.example.csv)
and
[examples/community-tool-handoff.example.json](examples/community-tool-handoff.example.json).
This is not platform collection and does not add connectors, scraping, browser
automation, platform APIs, monitoring, scheduling, source acquisition, demand
proof, ranking, or coverage verification.

The external community tool export directory examples are sanitized CSV/JSON
local export directory examples for user-controlled external/community tools:
[examples/community-tool-handoff-directory.example/README.md](examples/community-tool-handoff-directory.example/README.md),
[examples/community-tool-handoff-directory.example/csv/community-tool-a.csv](examples/community-tool-handoff-directory.example/csv/community-tool-a.csv),
[examples/community-tool-handoff-directory.example/csv/community-tool-b.csv](examples/community-tool-handoff-directory.example/csv/community-tool-b.csv),
[examples/community-tool-handoff-directory.example/json/community-tool-a.json](examples/community-tool-handoff-directory.example/json/community-tool-a.json),
and
[examples/community-tool-handoff-directory.example/json/community-tool-b.json](examples/community-tool-handoff-directory.example/json/community-tool-b.json).
`community-signal-profile --format json` and
`community-handoff-manifest --format json` expose these same checked-in
directory layout pointers as `directory_example_paths` for local/external tool
discovery, while `example_paths` stays limited to single-file examples.
The checked-in `csv/` and `json/` directories are separate non-recursive
examples for one input format and one matched filename pattern per run. They
are not platform collection and do not add connectors, scraping, browser
automation, platform APIs, monitoring, scheduling, source acquisition, demand
proof, ranking, or coverage verification.

`external-tool-adapters` is a local, print-only external social/community tool
adapter registry and local producer-discovery registry for user-controlled
external/community tools that need sanitized CSV/JSON local file handoff
targets. It prints metadata and copyable local handoff commands only. It is not
platform collection and has no connectors, no scraping, no browser automation,
no platform APIs, no monitoring, no scheduling, no source acquisition, no
demand proof, no ranking, and no coverage verification.

`external-tool-template` is a local, print-only command that prints
adapter-specific template rows for user-controlled external/community tools
that need sanitized CSV/JSON local file handoff examples. JSON and CSV output
contain importable community handoff rows only; table output may include local
metadata, field mappings, and copyable commands. It is not platform collection
and has no connectors, no scraping, no browser automation, no platform APIs,
no monitoring, no scheduling, no source acquisition, no demand proof, no
ranking, and no coverage verification.

`external-tool-workflow` is a local, print-only command that prints workflow
metadata for user-controlled external/community tools that need a
producer-facing wrapper around existing local commands before writing sanitized
CSV/JSON local file handoff rows. JSON output is workflow metadata, not
importable handoff rows; table output may include local metadata and copyable
commands. The printed steps include `check_external_tool_readiness`, an
optional preflight command that points to `external-tool-readiness` for local
command availability guidance before sanitized handoff rows are prepared. It
does not inspect directories, read handoff files, import rows, open SQLite, or
create artifacts. It is not platform collection and has no connectors, no
scraping, no browser automation, no platform APIs, no monitoring, no
scheduling, no source acquisition, no demand proof, no ranking, and no
coverage verification.

```bash
uv run fashion-radar external-tool-workflow --adapter instaloader --format table
uv run fashion-radar external-tool-workflow --adapter instaloader --format json
```

`external-tool-readiness` provides external tool readiness guidance and is local
read-only, not print-only, because it checks command availability only with
local PATH lookup (`shutil.which`) for known free external/community tools such
as Rednote MCP, Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp, and
X/search exports. It prints readiness guidance, mirror-friendly install hints,
and Fashion Radar next-step handoff commands for user-controlled
external/community tools producing sanitized CSV/JSON local file handoff rows.
It does not install dependencies automatically, does not run
adapters, does not run upstream tools, does not inspect directories, does not
read handoff files, import rows, open or write SQLite, or create
config/data/report/dashboard/workflow/handoff artifacts. It is not a
scraper/connector and has no scraping, no browser automation, no platform APIs,
no account/session/cookie/token behavior, no monitoring, no scheduling, no
source acquisition, no demand proof, no ranking, no coverage verification, and
no compliance-review product feature.

```bash
uv run fashion-radar external-tool-readiness --adapter instaloader
uv run fashion-radar external-tool-readiness --adapter rednote_mcp --format json
```

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

For first-run onboarding, see [docs/first-run.md](docs/first-run.md). Choose
the path that matches what you need:

- Source checkout smoke: verify the working tree with temporary paths.
- Manual repo-local sample output/dashboard: create local sample configs,
  SQLite state, and dated reports you can inspect in the dashboard.
- Installed-wheel release smoke: build a local wheel and smoke the installed
  package path before upload; this does not publish to PyPI.
- Reset repo-local sample output: remove generated sample runtime files after
  reviewing any local config edits.

Run Quickstart commands from the repository root after `cd /path/to/fashion-radar`.

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
in the commands. Run the prerequisite `init`, `migrate-db`, and `doctor` block
above first so the same repo-local paths are initialized and checked.

```bash
AS_OF="2026-06-13T12:00:00Z"

uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data" --format json
uv run fashion-radar imported-signals --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar report --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --as-of "$AS_OF"
uv run fashion-radar candidates --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
uv run fashion-radar trends --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --format json
test -s reports/fashion-radar-2026-06-13.md
test -s reports/fashion-radar-2026-06-13.json
```

Expected repo-local artifacts include `configs/sources.yaml`,
`configs/entities.yaml`, `configs/scoring.yaml`,
`data/fashion-radar.sqlite`, `reports/fashion-radar-2026-06-13.md`, and
`reports/fashion-radar-2026-06-13.json`. The deterministic sample is expected
to produce matched report and trend signals for `The Row`, `The Row Margaux`,
and `Ballet Flats`. To inspect the generated sample report, run the dashboard
with the same path flags and open
`http://127.0.0.1:8501`.

### Automated First-Run Smoke

In a source checkout, the automated local sample smoke uses temporary config, data,
report, and export directories, then verifies generated report artifacts there.
It should not create files under repo `data/` or `reports/`:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Source checkout mode prepends the checkout `src/` directory so it exercises the
working tree. Use it to check local source edits. The installed wheel smoke
builds and installs the local wheel, then runs the same sample path with the
wheel Python environment and `--installed`; use it to check release packaging:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Both modes print `First-run sample smoke passed.` on success and create
temporary dated reports such as `fashion-radar-2026-06-13.md` and
`fashion-radar-2026-06-13.json` inside their temporary report directories.
The automated smoke validates that sample rows import as community signals,
match the starter entities `The Row`, `The Row Margaux`, and `Ballet Flats`,
appear in the dated report, produce matching entity trend deltas, and keep
untracked candidates empty under starter config.
Temporary smokes do not leave dashboard-inspectable repo-local reports; use the
manual repo-local sample flow when you want dashboard output under
`reports/`.

This path does not run live collection, scraping, platform automation,
monitoring, scheduling, or external services. Candidate and trend JSON outputs
are local sample content checks from the checked example rows and current
starter config.

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

The external tool handoff template examples are sanitized CSV/JSON local file
handoff templates for user-controlled external/community tools, not platform
collection. Use
[examples/community-tool-handoff.example.csv](examples/community-tool-handoff.example.csv)
or
[examples/community-tool-handoff.example.json](examples/community-tool-handoff.example.json)
as local template shapes before running the same lint, preview,
`review_handoff_readiness`, dry-run, import, and review commands below.

```bash
AS_OF="2026-06-13T12:00:00Z"
tmp_run="$(mktemp -d)"
mkdir -p "$tmp_run/exports"
cp examples/community-signals.example.csv "$tmp_run/exports/community-signals.csv"
uv run fashion-radar community-signal-profile --format json
uv run fashion-radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar community-handoff-manifest "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar community-handoff-workflow "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-handoff-check-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar external-tool-adapters --format table
uv run fashion-radar external-tool-adapters --format json
uv run fashion-radar external-tool-template --adapter instaloader --format table
uv run fashion-radar external-tool-template --adapter instaloader --format json
uv run fashion-radar external-tool-template --adapter instaloader --format csv
uv run fashion-radar external-tool-workflow --adapter instaloader --format table
uv run fashion-radar external-tool-workflow --adapter instaloader --format json
uv run fashion-radar external-tool-readiness --adapter instaloader
uv run fashion-radar external-tool-readiness --adapter rednote_mcp --format json
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar community-signal-lint-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --source-name "Community Tool Export"
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
uv run fashion-radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
```

Inspect retained imported rows and matched-entity evidence after import:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF"
uv run fashion-radar imported-review-workflow --data-dir "$PWD/data" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data"
uv run fashion-radar imported-signals-summary --data-dir "$PWD/data" --format json
uv run fashion-radar match --config-dir "$PWD/configs" --data-dir "$PWD/data"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$AS_OF"
uv run fashion-radar imported-entity-deltas --data-dir "$PWD/data" --as-of "$AS_OF" --format json
uv run fashion-radar imported-entity-evidence --data-dir "$PWD/data" --as-of "$AS_OF" --entity-name "The Row" --entity-type brand
uv run fashion-radar imported-entity-evidence --data-dir "$PWD/data" --as-of "$AS_OF" --entity-name "The Row" --entity-type brand --source-name "Community Tool Export" --format json
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
copyable review sequence for existing local commands after manual signal
import. The workflow includes `review_imported_entity_evidence` after entity
deltas, then a read-only imported-candidates step for candidate phrase review,
and still ends with the final read-only heat-movers step for local observed
heat movement from configured sources and imported local signals. Those review
outputs need review and provide no demand proof and no platform coverage
verification.

`imported-entity-evidence` is local read-only and imported-only. It opens an
existing SQLite database in read-only mode and shows retained local rows whose
`manual_import` stored matched entity equals the requested entity. Output is a
privacy-safe drilldown: it includes only review metadata plus `window`, `id`,
`source_name`, `title`, `url`, `published_at`, and `collected_at`; it omits
summaries, candidate contexts, match internals, import file paths, normalized
keys, and platform labels. It does no scraping, no browser automation, no
platform APIs, and no account or cookie work.

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

`community-handoff-manifest` is local and print-only. It prints a
producer-facing manifest for a supplied directory without reading it. The
manifest describes the directory, matched file pattern, suggested handoff
filename, `community-signal-profile`/schema/example pointers,
`directory_example_paths`, embedded producer profile fields and rules, a
storage note, and the local workflow commands used by
`community-handoff-workflow`. If an external tool saves the manifest, keep it
outside the matched export directory or use a filename excluded by the handoff
`--pattern`, especially for JSON export directories using `--pattern "*.json"`.

`community-handoff-workflow` is local and print-only. It prints the ordered
local sequence `lint_handoff_directory`, `preview_candidate_phrases`,
`review_handoff_readiness`, `dry_run_directory_import`,
`import_directory_signals`, and `print_post_import_review` for a supplied
directory. The `review_handoff_readiness` step prints the
`community-handoff-check-dir` local-only handoff readiness report before
importing rows. The workflow does not execute commands, read the supplied
directory, validate files, import rows, open or write SQLite, fetch URLs, log
in, download media, automate browsers, scrape, monitor, watch folders, schedule
work, add source/platform connectors, prove demand, verify platform coverage,
rank sources, write reports, update dashboards, generate configs, or generate
entity files. It intentionally prints the supplied directory/config/data paths
inside copyable local commands; this differs from aggregate candidate preview
output, which suppresses paths and row details.

`community-handoff-check-dir` is a local-only handoff readiness report for
user-controlled community signal directories. It reads only matched local
regular files and local config. It does not import rows, uses no SQLite,
creates no config/data/report/dashboard/digest artifacts, and has no fetch URLs/login/platform
APIs/download media/browser automation/scrape/crawl/monitor/watch/schedule/connectors/source
acquisition/demand proof/ranking/coverage verification/entity generation/compliance/policy/
authorization/safety-review features.

`external-tool-adapters` is local and print-only. It prints the external
social/community tool adapter registry as a local producer-discovery registry
for user-controlled external/community tools that want sanitized CSV/JSON local
file handoff rows. It can print table or JSON metadata and copyable local
handoff commands, but it does not run adapters, inspect directories, read
handoff files, validate files, import rows, open SQLite, create artifacts, or
perform platform collection. It has no connectors, no scraping, no browser
automation, no platform APIs, no monitoring, no scheduling, no source
acquisition, no demand proof, no ranking, and no coverage verification.

`external-tool-template` is local and print-only. It prints adapter-specific
template rows for user-controlled external/community tools that want sanitized
CSV/JSON local file handoff examples. It can print importable JSON, importable
CSV, or a table with local metadata and copyable local commands, but it does
not write files, run adapters, inspect directories, read handoff files,
validate files, import rows, open SQLite, create artifacts, or perform
platform collection. It has no connectors, no scraping, no browser automation,
no platform APIs, no monitoring, no scheduling, no source acquisition, no
demand proof, no ranking, and no coverage verification.

`external-tool-readiness` provides external tool readiness guidance as local
read-only command availability only. It uses local PATH lookup (`shutil.which`)
to report whether the known command for a free external/community tool appears
available, then prints mirror-friendly install guidance and next-step Fashion
Radar handoff commands for sanitized CSV/JSON local file handoff rows. It does
not install dependencies, run
adapters, run upstream tools, inspect directories, read handoff files, import
rows, open or write SQLite, or create config/data/report/dashboard/workflow/
handoff artifacts. It is not platform collection and has no connectors, no
scraping, no browser automation, no platform APIs, no account/session/cookie/
token behavior, no monitoring, no scheduling, no source acquisition, no demand
proof, no ranking, no coverage verification, and no compliance-review product
feature.

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

### Heat Movers

The `heat-movers` command is a local observed heat movement view over one
configured source set. It reviews configured sources and imported local
signals, and the output needs review. It is local observed heat movement only,
with no demand proof and no platform coverage verification.

```bash
uv run fashion-radar heat-movers --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

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
uv run fashion-radar community-handoff-manifest ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar community-handoff-workflow ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-handoff-check-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
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

`community-handoff-manifest` can print a directory producer manifest before
workflow or directory validation. It is local and print-only; it describes the
target directory, file pattern, suggested filename, producer contract/profile
pointers, `directory_example_paths`, storage note, and workflow commands
without reading the supplied directory or creating artifacts.

`community-handoff-workflow` can print the same directory handoff order before
you run any step: `lint_handoff_directory`, `preview_candidate_phrases`,
`review_handoff_readiness`, `dry_run_directory_import`,
`import_directory_signals`, and `print_post_import_review`. The
`review_handoff_readiness` step prints the `community-handoff-check-dir`
local-only handoff readiness report before importing rows. It prints copyable
commands only; it does not execute commands, read the supplied directory,
validate files, import rows, open or write SQLite, fetch URLs, log in, download
media, automate browsers, scrape, monitor, watch folders, schedule work, add
source/platform connectors, prove demand, verify platform coverage, rank
sources, write reports, update dashboards, generate configs, or generate entity
files.

`community-handoff-check-dir` can print one local-only handoff readiness report
before import. It reads only matched local regular files and local config. It
does not import rows, uses no SQLite, creates no config/data/report/dashboard/digest artifacts,
and has no fetch URLs/login/platform APIs/download media/browser automation/scrape/crawl/
monitor/watch/schedule/connectors/source acquisition/demand proof/ranking/coverage verification/
entity generation/compliance/policy/authorization/safety-review features.

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

`imported-entity-evidence` is local read-only and imported-only. It opens an
existing SQLite database in read-only mode and shows retained local rows whose
`manual_import` stored matched entity equals the requested entity. Output is a
privacy-safe drilldown with review metadata plus `window`, `id`, `source_name`,
`title`, `url`, `published_at`, and `collected_at`; it omits summaries,
candidate contexts, match internals, import file paths, normalized keys, and
platform labels. It does not import rows, fetch URLs, run entity matching,
write scores, generate reports, monitor folders, scrape, automate browsers, use
platform APIs, or perform account or cookie work.

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

To reset the deterministic repo-local sample, see
[docs/first-run.md#reset-the-repo-local-sample](docs/first-run.md#reset-the-repo-local-sample).
`clean-old-data` is retention pruning for old collected items and matcher rows;
it is not a full reset of generated configs, reports, or the sample database.

```bash
uv run fashion-radar clean-old-data --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30 --dry-run
uv run fashion-radar clean-old-data --data-dir "$PWD/data" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --retention-days 30
```

See [docs/data-retention.md](docs/data-retention.md).

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/first-run.md](docs/first-run.md)
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
