# Stage 24 Imported Review Workflow Design

## Goal

Add `fashion-radar imported-review-workflow`, a local command that prints a
deterministic post-import review checklist for existing Fashion Radar commands.

The command is an operator aid. It does not execute the printed commands, open
SQLite, create directories, read configs, import rows, refresh matches, compare
entities, generate reports, schedule jobs, monitor folders, or integrate with
external platforms.

## Why This Stage

The project now has several useful local post-import commands:

- `imported-signals-summary`
- `match`
- `imported-entity-deltas`
- `imported-signals --unmatched-only`

Users and external community tools need a stable, copyable sequence after local
signal import. Stage 24 makes that sequence explicit without adding automation
or new data access.

## Non-Goals

- No command execution, subprocess calls, shell scripts, schedulers, watch
  folders, source acquisition, or external integrations.
- No SQLite access, schema checks, migrations, imports, matching, scoring,
  report/dashboard writes, or artifact creation by this command.
- No claims about external coverage, source quality, source ranking, verified
  demand, or real-time monitoring.
- No new dependencies.

## Command

```bash
fashion-radar imported-review-workflow \
  --config-dir ./configs \
  --data-dir ./data \
  --as-of 2026-06-13T12:00:00Z
```

Options:

- `--config-dir PATH`: used only to print the suggested `match` command.
- `--data-dir PATH`: used only to print suggested commands.
- `--as-of TEXT`: required UTC timestamp included in review commands.
- `--source-name TEXT`: optional exact stored source-name label included in
  row/entity review commands that support it.
- `--lookback-days INTEGER`: imported row review window, default `7`, minimum
  `1`.
- `--current-days INTEGER`: entity delta current window, default `7`, minimum
  `1`.
- `--baseline-days INTEGER`: entity delta baseline window, default `7`,
  minimum `1`.
- `--format [table|json]`: output format, default `table`.

`--as-of` is parsed with `parse_datetime_utc()` and normalized in output.
Blank `--source-name` is treated as no source-name filter.

## Output Model

Top-level JSON fields, in order:

```text
as_of
config_dir
data_dir
source_name
lookback_days
current_days
baseline_days
execution_mode
step_count
steps
```

Step fields, in order:

```text
order
name
purpose
command
suggested_effect
```

`execution_mode` is always `print_only`, because this command only prints the
suggested sequence and does not execute it.

`suggested_effect` values describe what the printed command would do if the
operator later copied and ran it:

- `read_only`: suggested command reads local state only.
- `updates_local_matches`: suggested command refreshes stored local matches.

The workflow always prints four steps:

1. `summarize_imported_sources`
   - Command: `fashion-radar imported-signals-summary --data-dir <data_dir>`
   - Effect: `read_only`
2. `refresh_stored_matches`
   - Command: `fashion-radar match --config-dir <config_dir> --data-dir <data_dir>`
   - Effect: `updates_local_matches`
3. `compare_imported_entities`
   - Command: `fashion-radar imported-entity-deltas --data-dir <data_dir>
     --as-of <as_of> --current-days <current_days> --baseline-days
     <baseline_days> [--source-name <source_name>]`
   - Effect: `read_only`
4. `review_unmatched_imported_rows`
   - Command: `fashion-radar imported-signals --data-dir <data_dir> --as-of
     <as_of> --lookback-days <lookback_days> --unmatched-only
     [--source-name <source_name>]`
   - Effect: `read_only`

Paths and option values in printed commands are built from argument tokens and
shell-quoted with `shlex.join()` so spaces and shell metacharacters in
paths/source labels are represented copyably.

## Table Output

Table output starts with:

```text
Imported manual signal review workflow.
Execution mode: print_only
Commands were not executed.
As of: 2026-06-13T12:00:00+00:00
Data dir: ./data
Config dir: ./configs
Source name: none
Lookback days: 7
Current days: 7
Baseline days: 7
Steps: 4
```

Then one row per step:

```text
Order | Step | Suggested Effect | Purpose | Command
1 | summarize_imported_sources | read_only | Summarize retained imported source-name labels. | fashion-radar imported-signals-summary --data-dir ./data
```

Cells are sanitized for pipes/newlines/carriage returns, using the same table
cell behavior as imported-signal renderers.

## Errors

- Invalid `--as-of` prints `Could not build imported review workflow: invalid
  --as-of: ...` and exits `1`.
- Invalid numeric options are rejected by Typer before workflow construction.
- Invalid `--format` is rejected by Typer before workflow construction.

## Tests

Add focused tests for:

- helper builds four deterministic steps and normalized `as_of`;
- blank source-name becomes `None` and omits source-name flags;
- source-name with spaces/metacharacters is shell-quoted and included only in
  commands that support it;
- paths with spaces/metacharacters are shell-quoted;
- table rendering sanitizes cells;
- CLI help lists options;
- CLI JSON has stable key order;
- invalid `--as-of`, invalid numeric options, and invalid format avoid helper
  execution;
- command creates no config/data/report artifacts.

## Documentation

Document the command near imported signal review examples as a copyable local
post-import checklist. Wording must say it prints suggested commands and does
not execute them.
