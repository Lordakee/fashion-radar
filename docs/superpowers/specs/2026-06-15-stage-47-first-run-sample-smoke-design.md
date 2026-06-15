# Stage 47 First-Run Sample Smoke Design

## Goal

Make the GitHub first-run experience deterministic and testable: a new user
should be able to clone the repository, run a local-only sample workflow from
checked-in examples, generate a report, and then inspect candidate/trend outputs
without using live collection, social platforms, browser automation, or network
source acquisition.

## Scope

In scope:

- Add a dependency-free `scripts/check_first_run_smoke.py` script that runs the
  local sample workflow in a temporary directory through the installed source
  checkout CLI.
- Use only checked-in examples and packaged starter config templates:
  `examples/community-signals.example.csv`, `fashion-radar init`,
  `migrate-db`, `doctor`, `community-signal-lint`, `community-candidates`,
  `import-signals --dry-run`, `import-signals`, `imported-signals-summary`,
  `imported-signals`, `match`, `report`, `candidates`, and `trends`.
- Assert visible local output: generated SQLite database, generated Markdown
  report, generated JSON report, imported rows, and JSON-producing candidate
  and trend commands that execute successfully.
- Optionally include a directory handoff smoke by copying the checked-in CSV
  example into a temporary `exports/` directory and running local directory
  commands against that temp directory.
- Update README and `docs/community-signal-import.md` so the first-run path uses
  checked-in examples instead of nonexistent `./signals.csv`,
  `./community-signals.csv`, or an unexplained `./exports` directory.
- Update `docs/github-upload-checklist.md` and CI to run the first-run smoke
  script after package/archive checks.
- Add pytest coverage for the smoke script and docs/CI drift.
- Record Stage 47 Claude Code plan and release review artifacts.

Out of scope:

- Live `collect`, RSS/GDELT fetches, source acquisition, web scraping, crawling,
  browser automation, login/cookie/session handling, account automation,
  anti-bot workarounds, platform connectors, media download, monitoring,
  watching, scheduling, push notifications, or external services.
- Product compliance-review functionality.
- Dashboard server launch tests. The stage may document launching the dashboard
  after the sample report is generated, but CI should not start a long-running
  Streamlit server.
- Dependency additions, dependency upgrades, lockfile changes, package version
  changes, database schema changes, scoring algorithm changes, entity alias
  changes, or generated data/report files committed to git.

## Design

Create `scripts/check_first_run_smoke.py` using only Python standard library
modules. The script should accept:

- `--repo-root`, defaulting to the current directory.
- `--python`, defaulting to `sys.executable`, for running
  `python -m fashion_radar ...`.

The script should create a temporary runtime directory, then run the CLI through
`python -m fashion_radar` so it exercises the source checkout entrypoint without
requiring an installed console script. Every command must run with:

- `cwd` set to `--repo-root`;
- `PYTHONPATH` preserving the active environment and prepending
  `<repo-root>/src`;
- explicit temp `--config-dir`, `--data-dir`, and/or `--reports-dir` whenever a
  command accepts those flags;
- deterministic `AS_OF = "2026-06-13T12:00:00Z"` whenever a command accepts
  `--as-of`;
- deterministic source name `"Community Tool Export"` whenever a command
  accepts `--source-name`.

After the script finishes, it should assert that no generated
`fashion-radar.sqlite`, `fashion-radar-2026-06-13.md`, or
`fashion-radar-2026-06-13.json` landed under the repository's `data/` or
`reports/` directories. This guards against accidental default-path writes.

The source-checkout workflow should run:

```bash
python -m fashion_radar init --config-dir "$tmp/configs" --data-dir "$tmp/data" --reports-dir "$tmp/reports"
python -m fashion_radar migrate-db --data-dir "$tmp/data"
python -m fashion_radar doctor --config-dir "$tmp/configs" --data-dir "$tmp/data" --reports-dir "$tmp/reports"
python -m fashion_radar community-signal-lint examples/community-signals.example.csv --input-format csv --source-name "Community Tool Export"
python -m fashion_radar community-candidates examples/community-signals.example.csv --input-format csv --config-dir "$tmp/configs" --as-of "2026-06-13T12:00:00Z" --source-name "Community Tool Export" --format json
python -m fashion_radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --data-dir "$tmp/data" --dry-run
python -m fashion_radar import-signals examples/community-signals.example.csv --format csv --source-name "Community Tool Export" --imported-at "2026-06-13T12:00:00Z" --data-dir "$tmp/data"
python -m fashion_radar imported-signals-summary --data-dir "$tmp/data" --format json
python -m fashion_radar imported-signals --data-dir "$tmp/data" --as-of "2026-06-13T12:00:00Z" --source-name "Community Tool Export" --format json
python -m fashion_radar match --config-dir "$tmp/configs" --data-dir "$tmp/data"
python -m fashion_radar report --config-dir "$tmp/configs" --data-dir "$tmp/data" --reports-dir "$tmp/reports" --as-of "2026-06-13T12:00:00Z"
python -m fashion_radar candidates --config-dir "$tmp/configs" --data-dir "$tmp/data" --as-of "2026-06-13T12:00:00Z" --format json
python -m fashion_radar trends --config-dir "$tmp/configs" --data-dir "$tmp/data" --as-of "2026-06-13T12:00:00Z" --format json
```

`doctor` is safe for this stage because the current command implementation
checks only local paths, required config file loading, and local SQLite schema
status for the provided `--data-dir`; it does not fetch URLs, probe live
services, validate accounts, or inspect external credentials.

The script should assert:

- `examples/community-signals.example.csv` exists.
- `configs`, `data`, and `reports` temp directories are created.
- `data/fashion-radar.sqlite` exists after import.
- `reports/fashion-radar-2026-06-13.md` and
  `reports/fashion-radar-2026-06-13.json` exist and are non-empty.
- `imported-signals-summary --format json` parses as JSON and reports at least
  one imported item.
- `imported-signals --format json`, `community-candidates --format json`,
  `candidates --format json`, and `trends --format json` parse as JSON.

For directory handoff smoke, create exactly one temp file by copying
`examples/community-signals.example.csv` into
`$tmp/exports/community-signals.csv`. `community-handoff-workflow` is
print-only and does not create that file; the script creates it before running
any directory commands. All directory commands use `--pattern "*.csv"` and
should see only that one direct-child CSV file.

```bash
python -m fashion_radar community-handoff-workflow "$tmp/exports" --input-format csv --pattern "*.csv" --config-dir "$tmp/configs" --data-dir "$tmp/data" --as-of "2026-06-13T12:00:00Z" --source-name "Community Tool Export"
python -m fashion_radar community-signal-lint-dir "$tmp/exports" --input-format csv --pattern "*.csv" --source-name "Community Tool Export"
python -m fashion_radar community-candidates-dir "$tmp/exports" --input-format csv --pattern "*.csv" --config-dir "$tmp/configs" --as-of "2026-06-13T12:00:00Z" --source-name "Community Tool Export" --format json
python -m fashion_radar import-signals-dir "$tmp/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$tmp/data" --dry-run
```

Do not run `collect` or dashboard server startup in this script.

Update CI with:

```bash
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

after release hygiene and before package build. Update upload checklist to use
the same command. Add docs drift tests so README, CI, and upload checklist all
name `scripts/check_first_run_smoke.py`.

## Verification

Focused checks:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Release checks:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```
