# Stage 61 Community Handoff Readiness Workflow Step Design

## Objective

Add the existing local-only `community-handoff-check-dir` command to the
print-only `community-handoff-workflow` so a user-controlled external/community
tool export directory has a copyable readiness report step before rows are
imported into local SQLite.

## Context

`community-handoff-workflow` currently prints five commands:

1. `community-signal-lint-dir`
2. `community-candidates-dir`
3. `import-signals-dir --dry-run`
4. `import-signals-dir`
5. `imported-review-workflow`

`community-handoff-check-dir` already exists. It is local-only and read-only:
it reads matched local regular files and local config, runs the existing lint,
candidate preview, and import dry-run checks, and prints a readiness report. It
does not import rows, write SQLite, create report/dashboard/digest artifacts,
fetch URLs, use platform APIs, run browser automation, schedule monitoring, or
provide demand proof, ranking, coverage verification, entity generation,
compliance review, policy review, authorization review, or safety review.

The current workflow does not surface that consolidated readiness report.

## Selected Approach

Add one workflow step after candidate preview and before the explicit import
dry-run:

1. `lint_handoff_directory`
2. `preview_candidate_phrases`
3. `review_handoff_readiness`
4. `dry_run_directory_import`
5. `import_directory_signals`
6. `print_post_import_review`

The new step remains `read_only` and prints this command shape:

```bash
fashion-radar community-handoff-check-dir <directory> \
  --input-format <format> \
  --pattern <pattern> \
  --config-dir <config_dir> \
  --as-of <as_of> \
  --source-name <source_name> \
  --strict
```

The builder remains print-only. It must only normalize `as_of`, stringify the
provided paths/arguments, and format shell commands. It must not inspect the
directory, read config files, open SQLite, run `community-handoff-check-dir`, run
subprocesses, import rows, write reports, or create artifacts.

## Alternatives Considered

### A. Add the readiness report step before import

This is selected. It preserves the existing granular steps and adds a
local-only read-only readiness report before dry-run/import decisions. Users can
still run the individual commands, and the readiness report gives a single
summary before any write-oriented step is printed later in the sequence.

### B. Keep `community-handoff-check-dir` separate and only improve docs

This avoids changing step count, but it leaves the print-only workflow less
useful for the user who wants one ordered checklist for external community tool
exports.

### C. Replace lint/candidate/dry-run steps with `community-handoff-check-dir`

This would reduce duplication, but it removes explicit commands that are useful
for focused debugging and changes more behavior than this node needs.

## Data Flow

`community-handoff-workflow` receives directory/config/data/as-of/source
arguments from the CLI and returns a Pydantic model with six shell-command
strings. It does not read data. `community-handoff-manifest` embeds the same
workflow model, so its embedded workflow step count also becomes six.

When the user later copies and runs the printed readiness command, that separate
command performs its existing local read-only checks.

## Testing Plan

Use TDD:

- Update `tests/test_community_handoff_workflow.py` first so the expected step
  count, step names, effects, and commands require `review_handoff_readiness`.
- Update CLI JSON/table tests to require `step_count == 6`, the new step name,
  the command shape, and no path artifacts created by the print-only workflow.
- Update manifest tests because `community-handoff-manifest` embeds the
  workflow model.
- Extend first-run smoke validation so `community-handoff-workflow --format
  json` is validated for the six-step shape.
- Update docs drift tests so docs and generated manifest sections expect the
  readiness report step inside the workflow.

## Documentation Plan

Update README, CLI reference, community signal import/quality docs,
architecture, source boundaries, GitHub upload checklist, and changelog to say
the workflow now includes a local-only `community-handoff-check-dir` readiness
report step before import.

Docs must keep the same boundaries: no platform/source acquisition, no scraping,
no login, no scheduling, no monitor/watch behavior, no platform APIs, no media
download, no connector, no demand proof, no ranking, no coverage verification,
no entity generation, and no compliance/policy/authorization/safety-review
product feature.

## Acceptance Criteria

- `community-handoff-workflow --format json` prints `step_count == 6`.
- Step 3 is `review_handoff_readiness`.
- Step 3 is `read_only`.
- Step 3 command uses `community-handoff-check-dir` with `--input-format`,
  `--pattern`, `--config-dir`, `--as-of`, `--source-name`, and `--strict`.
- The dry-run step moves to step 4 and remains `read_only`.
- The actual import step moves to step 5 and remains `updates_local_imports`.
- The post-import review step moves to step 6 and remains `print_only`.
- `community-handoff-manifest` embedded workflow also reports six steps.
- The workflow builder stays print-only and does not read directories, configs,
  SQLite, run subprocesses, import rows, or write artifacts.
- No dependency, schema, connector, scraper, platform API, account/cookie,
  browser automation, scheduler, dashboard/report/digest write, or compliance
  review feature is added.
