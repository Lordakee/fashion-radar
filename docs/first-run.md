# First Run

Use this guide when you want a deterministic first run from a source checkout.
The sample path uses the checked-in community signal example and local
directories under the checkout.

Run first-run commands from the repository root after `cd /path/to/fashion-radar`.

## Choose Your First Run

| Path | Use When | Writes To | Start Here |
| --- | --- | --- | --- |
| Manual repo-local sample | Recommended first-time path when you want inspectable output, local SQLite state, dated reports, and dashboard data. | `data/` and `reports/` under this checkout. | [Manual Repo-Local Sample Flow](#manual-repo-local-sample-flow) |
| Automated source-checkout smoke | Disposable verification for the current source checkout. | temporary config/data/report/export directories. | [Automated First-Run Smoke](#automated-first-run-smoke) |
| Installed-wheel smoke | Package verification when you need to test the built wheel. | Temporary build directory and temporary virtual environment. | [Installed-Wheel Smoke](#installed-wheel-smoke) |
| Reset repo-local sample | Cleanup after local experiments. | Removes generated repo-local sample files and keeps placeholder READMEs. | [Reset The Repo-Local Sample](#reset-the-repo-local-sample) |

Choose the manual repo-local sample when you want inspectable output from the
generated `data/` and `reports/` artifacts yourself. This path writes local
sample output under the checkout and is the recommended first-time path when
you also want dashboard data.

Choose the automated source-checkout smoke when you want disposable verification
of the working tree. The smoke uses temporary config/data/report/export
directories, then verifies generated report artifacts there. It should not
create files under repo `data/` or `reports/`.

Use the installed-wheel smoke when you need package verification instead of the
source checkout. It builds a local wheel, installs it into a temporary virtual
environment, and runs the same sample path with `--installed`.

Use the reset repo-local sample after local experiments when you want to start
over. It deletes selected generated runtime files and keeps the placeholder
`README.md` files under `data/` and `reports/`.

These first-run paths use checked-in examples and local files. The sample does
not run live collection.

## Prepare A Source Checkout

Create starter config, initialize the repo-local SQLite schema, and check the
same repo-local workspace:

```bash
uv run fashion-radar init --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
uv run fashion-radar migrate-db --data-dir "$PWD/data"
uv run fashion-radar doctor --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports"
```

Expected local setup artifacts are:

- `configs/sources.yaml`
- `configs/entities.yaml`
- `configs/scoring.yaml`
- `data/fashion-radar.sqlite`

Review generated config files before changing or deleting them. The manual
sample below depends on the repo-local `configs/`, `data/`, and `reports/`
paths shown in the commands.

## Manual Repo-Local Sample Flow

Use the checked-in community signal example when you want a deterministic first
run that produces local output without live source collection. This manual flow
writes to the repo-local `data/` and `reports/` directories shown in the
commands:

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
test -s reports/fashion-radar-2026-06-13.html
```

Expected sample artifacts are:

- `data/fashion-radar.sqlite`
- `reports/fashion-radar-2026-06-13.md`
- `reports/fashion-radar-2026-06-13.json`
- `reports/fashion-radar-2026-06-13.html`

The deterministic sample is expected to produce matched report and trend
signals for `The Row`, `The Row Margaux`, and `Ballet Flats`.

The community handoff commands are also available for local directory-based
handoffs: `community-handoff-workflow`, `community-signal-lint-dir`,
`community-candidates-dir`, `community-handoff-check-dir`, and
`import-signals-dir`. The print-only workflow includes
`review_handoff_readiness`, a `community-handoff-check-dir` local-only handoff
readiness report before importing rows, and does not execute commands.

The checked-in `generic_community_export` CSV/JSON directory preflight examples live in
[examples/community-tool-handoff-directory.example/README.md](../examples/community-tool-handoff-directory.example/README.md)
and the concrete `external-tool-readiness` / `external-tool-workflow` command
pairs for `External Community Tool` are documented in
[community-signal-import.md#external-tool-export-directory-examples](community-signal-import.md#external-tool-export-directory-examples).

## Inspect The Sample In The Dashboard

Install the dashboard extra and start the read-only local dashboard against the
same repo-local directories:

```bash
uv sync --locked --dev --extra dashboard
uv run fashion-radar dashboard --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --host 127.0.0.1 --port 8501
```

Open `http://127.0.0.1:8501` after the server starts. Run the manual repo-local
sample flow first when you want the dashboard to open against the generated
sample report in `reports/`.

## Inspect The Sample In ROW ONE

Use the same repo-local sample data to build the ROW ONE local static site:

```bash
AS_OF="2026-06-13T12:00:00Z"
uv run fashion-radar row-one refresh --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --output-dir reports/row-one/site --as-of "$AS_OF"
uv run fashion-radar row-one preview --config-dir "$PWD/configs" --data-dir "$PWD/data" --reports-dir "$PWD/reports" --output-dir reports/row-one/site --as-of "$AS_OF" --latest-only --dry-run-serve-url
uv run fashion-radar row-one status --site-dir reports/row-one/site
uv run fashion-radar row-one serve --site-dir reports/row-one/site --host 127.0.0.1 --port 8787
```

`row-one refresh` is the single local daily refresh command for ROW ONE. It
refreshes the daily report data and generated site in one local command.
ROW ONE local ops use a daily `04:00` refresh boundary and fixed local
IP:port `127.0.0.1:8787`; use `0.0.0.0:8787` only for explicit LAN serving.
The generated site includes `data/runtime.json` runtime metadata alongside
`data/edition.json` and `data/manifest.json`, and `row-one status` reads that
runtime metadata without rebuilding or serving the site. The status command is
a lightweight runtime contract check for the generated site marker, the three
JSON objects, fixed runtime paths, `04:00` refresh metadata, `127.0.0.1:8787`
serve metadata, readiness, counts, and generated timestamps.

Open `http://127.0.0.1:8787` locally. The generated ROW ONE site under
`reports/row-one/site` is a local artifact and should not be committed.

## Automated First-Run Smoke

In a source checkout, the automated local sample smoke uses temporary config,
data, report, and export directories, then verifies generated report artifacts
there. It should not create files under repo `data/` or `reports/`:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Source checkout mode prepends the checkout `src/` directory so it exercises the
working tree. A successful run prints:

```text
First-run sample smoke passed.
```

The source-checkout smoke also validates the ROW ONE manifest output, runtime
status output, and local serve readiness path. It checks that ROW ONE writes the
Manifest: `data/manifest.json` app discovery file and `data/runtime.json`
runtime metadata file, runs `row-one status` against the generated temporary
site as a lightweight runtime contract and cross-file consistency check, then runs
`row-one serve --dry-run` against the same site so the dry-run URL path is
covered without starting a long-running server.

## Installed-Wheel Smoke

Use this path when you need to verify the built package instead of the source
checkout. The installed wheel smoke builds and installs the local wheel, then
runs the same sample path with the wheel Python environment and `--installed`:

```bash
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Both automated smoke paths verify temporary dated reports, generated ROW ONE
runtime metadata, status output, and local serve readiness. They should not
create files under repo `data/` or `reports/`, and print
`First-run sample smoke passed.` on success.
The automated smoke validates that sample rows import as community signals,
match the starter entities `The Row`, `The Row Margaux`, and `Ballet Flats`,
appear in the dated report, produce matching entity trend deltas, and keep
untracked candidates empty under starter config.
The automated first-run smoke also validates local external-tool JSON
contracts: `external-tool-adapters --format json` across all eight adapters,
plus the `external-tool-template --adapter rednote_mcp --format json`,
`external-tool-workflow --adapter rednote_mcp --format json`, and
`external-tool-readiness --adapter rednote_mcp --format json` outputs generated
with the `rednote_mcp` adapter. These are command-output contract checks only;
they do not run adapters or upstream external/community tools, do not call
platform APIs, and do not perform source acquisition.

## Optional Expanded Watchlist Sample

Use this optional local sample when you want to see the broader
`fashion-watchlist` entity pack match designer brands, named products,
categories, designers, celebrity style, and trend terms against checked-in
synthetic local rows. It is separate from the deterministic first-run sample
and does not change generated starter configs.

```bash
tmp_watchlist="$(mktemp -d)"
AS_OF="2026-06-13T12:00:00Z"
mkdir -p "$tmp_watchlist/configs" "$tmp_watchlist/data" "$tmp_watchlist/reports"
cp configs/entity-packs/fashion-watchlist.example.yaml "$tmp_watchlist/configs/entities.yaml"
cp configs/scoring.example.yaml "$tmp_watchlist/configs/scoring.yaml"

uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml
uv run fashion-radar community-signal-lint examples/community-signals.watchlist.example.csv --input-format csv --source-name "Community Watchlist Sample"
uv run fashion-radar import-signals examples/community-signals.watchlist.example.csv --format csv --source-name "Community Watchlist Sample" --imported-at "$AS_OF" --data-dir "$tmp_watchlist/data"
uv run fashion-radar match --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data"
uv run fashion-radar report --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --reports-dir "$tmp_watchlist/reports" --as-of "$AS_OF"
uv run fashion-radar trends --config-dir "$tmp_watchlist/configs" --data-dir "$tmp_watchlist/data" --as-of "$AS_OF" --format json
```

Expected local matches include `Khaite`, `Khaite Lotus Bag`, `Loewe`,
`Loewe Puzzle Bag`, `Jonathan Anderson`, `Bella Hadid`, `Alaia Le Teckel`,
`Miu Miu Arcadie`, `Mary Jane Shoes`, and `Boho Revival`.

The optional local sample does not fetch URLs, does not collect platform data,
does not prove demand, does not rank brands, does not verify platform coverage,
and does not add connectors.

## Reset The Repo-Local Sample

Review or copy edits to generated config files before deleting them. The setup
command can regenerate starter config files, but local edits to
`configs/sources.yaml`, `configs/entities.yaml`, or `configs/scoring.yaml` are
not preserved by deletion.

This deletes local experiment state. Use narrow `rm -f` commands for the
generated sample files:

Before reset, confirm you are at the repository root:

```bash
test -f pyproject.toml && test -d examples && { \
  rm -f configs/sources.yaml; \
  rm -f configs/entities.yaml; \
  rm -f configs/scoring.yaml; \
  rm -f data/fashion-radar.sqlite; \
  rm -f data/fashion-radar.sqlite-wal; \
  rm -f data/fashion-radar.sqlite-shm; \
  rm -f reports/fashion-radar-2026-06-13.md; \
  rm -f reports/fashion-radar-2026-06-13.json; \
  rm -f reports/fashion-radar-2026-06-13.html; \
}
```

This keeps `data/README.md` and `reports/README.md`. ROW ONE latest-only site
cleanup removes generated site output, including `data/runtime.json` inside the
site directory, but it does not delete dated Fashion Radar reports such as
`reports/fashion-radar-YYYY-MM-DD.md`, `.json`, or `.html`.

## Boundary

The first-run sample does not run live collection. The automated smoke does not
run `collect`, `run`, or `dashboard`, and it should not create files under repo
`data/` or `reports/`.

The sample does not perform browser automation, account login, cookies/sessions,
source/platform connectors, scraping, platform automation, monitoring,
scheduling, or external services. Candidate and trend outputs are local sample
content checks from the checked-in example; they are not proof of demand, not
platform coverage, and not source ranking.
