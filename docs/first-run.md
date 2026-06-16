# First Run

Use this guide when you want a deterministic first run from a source checkout.
The sample path uses the checked-in community signal example and local
directories under the checkout.

Run first-run commands from the repository root after `cd /path/to/fashion-radar`.

## Choose Your First Run

Choose the manual repo-local sample when you want to inspect the generated
`data/` and `reports/` artifacts yourself. This path writes local sample output
under the checkout.

Choose the automated first-run smoke when you want a disposable verification
path. The smoke uses temporary config, data, report, and export directories,
then verifies generated report artifacts there. It should not create files under
repo `data/` or `reports/`.

Use the installed-wheel smoke when you need to verify the packaged wheel instead
of the source checkout. It builds a local wheel, installs it into a temporary
virtual environment, and runs the same sample path with `--installed`.

Use the reset path when you want to start over after a repo-local experiment.
It deletes selected generated runtime files and keeps the placeholder
`README.md` files under `data/` and `reports/`.

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
```

Expected sample artifacts are:

- `data/fashion-radar.sqlite`
- `reports/fashion-radar-2026-06-13.md`
- `reports/fashion-radar-2026-06-13.json`

The deterministic sample is expected to produce matched report and trend
signals for `The Row`, `The Row Margaux`, and `Ballet Flats`.

The community handoff commands are also available for local directory-based
handoffs: `community-handoff-workflow`, `community-signal-lint-dir`,
`community-candidates-dir`, `community-handoff-check-dir`, and
`import-signals-dir`. The print-only workflow includes
`review_handoff_readiness`, a `community-handoff-check-dir` local-only handoff
readiness report before importing rows, and does not execute commands.

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

## Automated First-Run Smoke

In a source checkout, the automated local sample smoke uses temporary config,
data, report, and export directories, then verifies generated report artifacts
there. It should not create files under repo `data/` or `reports/`:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Source checkout mode prepends the checkout `src/` directory so it exercises the
working tree. A successful run prints:

```text
First-run sample smoke passed.
```

## Installed-Wheel Smoke

Use this path when you need to verify the built package instead of the source
checkout. The installed wheel smoke builds and installs the local wheel, then
runs the same sample path with the wheel Python environment and `--installed`:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Both automated smoke paths verify temporary dated reports, should not create
files under repo `data/` or `reports/`, and print
`First-run sample smoke passed.` on success.
The automated smoke validates that sample rows import as community signals,
match the starter entities `The Row`, `The Row Margaux`, and `Ballet Flats`,
appear in the dated report, produce matching entity trend deltas, and keep
untracked candidates empty under starter config.

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
}
```

This keeps `data/README.md` and `reports/README.md`.

## Boundary

The first-run sample does not run live collection. The automated smoke does not
run `collect`, `run`, or `dashboard`, and it should not create files under repo
`data/` or `reports/`.

The sample does not perform browser automation, account login, cookies/sessions,
source/platform connectors, scraping, platform automation, monitoring,
scheduling, or external services. Candidate and trend outputs are local sample
content checks from the checked-in example; they are not proof of demand, not
platform coverage, and not source ranking.
