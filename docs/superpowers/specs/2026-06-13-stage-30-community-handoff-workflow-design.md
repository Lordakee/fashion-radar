# Stage 30 Community Handoff Workflow Design

## Goal

Add a local `fashion-radar community-handoff-workflow DIRECTORY` command that
prints a copyable, ordered command checklist for the local community signal
directory handoff path.

## User Value

External community tools can already produce sanitized local CSV/JSON handoff
files. The current command surface is accurate but long:

1. lint the directory;
2. preview candidate phrases;
3. dry-run import;
4. import;
5. run post-import review commands.

The new command turns that sequence into deterministic table or JSON output so
users can copy the next steps without remembering every flag.

## Scope

In scope:

- Directory-batch workflow only.
- Print-only command generation.
- Table and JSON output.
- Shell-quoted commands for paths, source names, patterns, and timestamps.
- CLI tests and module tests.
- Stage 30 process review artifacts under `docs/reviews/`.
- Docs updates for README, architecture, community signal docs, source
  boundaries, changelog, and GitHub upload checklist.

Out of scope:

- Single-file handoff workflow.
- Executing generated commands.
- Reading the supplied directory.
- Validating matched files.
- Importing rows.
- Opening or writing SQLite.
- Fetching URLs.
- Logging in, downloading media, browser automation, source acquisition,
  scraping, monitoring, watchers, schedulers, platform connectors, reports,
  dashboards, config generation, or entity generation.

## Command Shape

```bash
fashion-radar community-handoff-workflow ./exports \
  --input-format csv \
  --pattern "*.csv" \
  --config-dir ./configs \
  --data-dir ./data \
  --as-of 2026-06-13T12:00:00Z \
  --source-name "Community Tool Export"
```

JSON output uses `--format json`.

## Output Model

`CommunityHandoffWorkflow` contains:

- `directory`
- `input_format`
- `pattern`
- `as_of`
- `config_dir`
- `data_dir`
- `source_name`
- `execution_mode = "print_only"`
- `step_count`
- `steps`

Each step contains:

- `order`
- `name`
- `purpose`
- `command`
- `suggested_effect`

Allowed `suggested_effect` values:

- `read_only`
- `updates_local_imports`
- `print_only`

The command intentionally prints the supplied directory/config/data paths inside
copyable commands. This differs from aggregate candidate preview commands, which
suppress paths and row details.

## Generated Steps

1. `lint_handoff_directory`
   - Command: `fashion-radar community-signal-lint-dir ... --strict`
   - Effect: `read_only`

2. `preview_candidate_phrases`
   - Command: `fashion-radar community-candidates-dir ...`
   - Effect: `read_only`

3. `dry_run_directory_import`
   - Command: `fashion-radar import-signals-dir ... --dry-run`
   - Effect: `read_only`

4. `import_directory_signals`
   - Command: `fashion-radar import-signals-dir ...`
   - Effect: `updates_local_imports`

5. `print_post_import_review`
   - Command: `fashion-radar imported-review-workflow ...`
   - Effect: `print_only`

The workflow builder does not execute these commands.

## Implementation

Create `src/fashion_radar/community_handoff_workflow.py`, mirroring the existing
`imported_review_workflow` pattern:

- Pydantic models with `extra="forbid"`.
- `build_community_handoff_workflow(...)`.
- `render_community_handoff_workflow_table(...)`.
- private `_shell_command(...)` using `shlex.join`.
- private `_table_cell(...)` that removes table separators and newlines.

Add a thin Typer command in `src/fashion_radar/cli.py`:

- accept the positional `DIRECTORY` as a string so Typer does not inspect
  directory metadata for this print-only command;
- parse `--as-of` before building the workflow;
- return clean errors for invalid timestamps;
- print model JSON when `--format json`;
- otherwise print table lines.

## Tests

Module tests:

- deterministic five-step workflow;
- shell quoting for directory/config/data/source/pattern values;
- blank source name falls back to `Community Tool Export`;
- table renderer sanitizes pipe and newline characters;
- invalid timestamp raises from the builder parser.

CLI tests:

- help lists options;
- invalid timestamp returns a clean CLI error;
- JSON output has stable top-level keys, stable step keys, and five steps;
- table output is print-only, contains copyable commands, and intentionally
  echoes supplied directory/config/data paths;
- command succeeds for a missing directory and does not create artifacts;
- command does not call directory metadata/traversal APIs, SQLite creation,
  manual import loading/storing, subprocess execution, report generation,
  digest packaging, dashboard code, or source collection.

## Verification

Use mirror-aware install checks when dependency checks are needed:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
```

Required final checks:

```bash
.venv/bin/python -m pytest tests/test_community_handoff_workflow.py tests/test_cli.py -q
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
```

Final boundary scans should include variants for fetch/URL handling, login,
downloads, browser automation, scraping, monitoring, watchers, schedulers,
source acquisition, platform coverage, demand proof, source ranking, report
generation, dashboard generation, config generation, and entity generation.

Build and installed-wheel smoke:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv build --out-dir /tmp/fashion-radar-dist-stage30
```

Install the wheel into a temporary venv and run:

```bash
fashion-radar community-handoff-workflow --help
fashion-radar community-handoff-workflow ./missing --input-format csv --pattern "*.csv" --config-dir ./configs --data-dir ./data --as-of 2026-06-13T12:00:00Z --format json
```

The missing-directory smoke should exit `0` because this command does not read
the directory.
