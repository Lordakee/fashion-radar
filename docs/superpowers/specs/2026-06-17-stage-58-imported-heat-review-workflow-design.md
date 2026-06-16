# Stage 58 Imported Heat Review Workflow Design

## Objective

Extend the existing print-only `imported-review-workflow` so imported
community/external tool signals have a clear local path into heat review after
they are imported and matched.

The workflow should add one final read-only step:

```bash
fashion-radar heat-movers --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of>
```

This keeps the external/community handoff chain local:

```text
community handoff files -> import-signals-dir -> imported-review-workflow -> match -> heat-movers
```

## Current Context

The repository already has the local handoff pieces needed for external tools:

- `community-signal-profile` prints producer contract fields and examples.
- `community-handoff-manifest` prints a producer-facing directory manifest.
- `community-handoff-workflow` prints the pre-import directory sequence.
- `community-handoff-check-dir` validates a local directory without importing.
- `import-signals-dir` imports sanitized local CSV/JSON files only when run
  without `--dry-run`.
- `imported-review-workflow` currently prints four post-import steps:
  imported source summary, `match`, imported entity deltas, and unmatched
  imported rows.
- `heat-movers` already provides local observed heat movement over existing
  local SQLite/config state.

The missing link is that `imported-review-workflow` does not point users toward
`heat-movers` after refreshing matches.

## Scope

In scope:

- Add a fifth `ImportedReviewWorkflowStep` named `review_local_heat_movers`.
- Keep the step `suggested_effect` as `read_only`.
- Use the same `config_dir`, `data_dir`, and normalized `as_of` values already
  used by the workflow.
- Keep command quoting through the existing `_shell_command()` helper.
- Update direct workflow tests, CLI workflow tests, docs drift tests, docs, and
  upload checklist wording.
- Preserve the current public `imported-review-workflow` flags; no new CLI
  options are needed.

Out of scope:

- New commands.
- New output formats.
- Daily report or digest integration.
- Dashboard persistence or dashboard writes.
- Database schema or migration changes.
- Dependency or lockfile changes.
- Platform/social connectors, scraping, crawling, platform API clients,
  browser automation, account/cookie/session handling, monitoring, scheduling,
  source acquisition, ranking, demand proof, platform coverage verification, or
  compliance/legal/authorization/safety-review features.
- Changes to `community-signal-profile`, `community-handoff-manifest`,
  `community-handoff-workflow`, or `community-handoff-check-dir` behavior.

## Architecture

The only production behavior change is inside
`src/fashion_radar/imported_review_workflow.py`.

`build_imported_review_workflow()` will append a fifth step after
`review_unmatched_imported_rows`:

- `name`: `review_local_heat_movers`
- `purpose`: `Review local observed heat movement after imported rows are
  matched.`
- `command`: `fashion-radar heat-movers --config-dir <config_dir> --data-dir
  <data_dir> --as-of <as_of>`
- `suggested_effect`: `read_only`

The CLI command remains a thin wrapper over `build_imported_review_workflow()`.
The JSON and table renderers do not need special cases because they already
render every workflow step.

## Data Flow

1. User imports sanitized external/community rows through `import-signals-dir`.
2. User runs `imported-review-workflow`.
3. The workflow prints:
   - summary of retained imported source labels
   - `match` to refresh local entity matches
   - imported entity delta comparison
   - unmatched imported row review
   - local heat-movers review
4. The workflow itself does not execute any command.

## Error Handling

Existing error handling remains unchanged:

- `imported-review-workflow` validates `--as-of`.
- `lookback_days`, `current_days`, and `baseline_days` must be at least 1.
- Any workflow construction error is reported as
  `Could not build imported review workflow`.

The new step does not add IO, database access, or validation paths.

## Testing

Add or update tests to prove:

- Direct workflow builder now returns five deterministic steps.
- The fifth step is named `review_local_heat_movers`.
- The fifth step has `suggested_effect == "read_only"`.
- The fifth command is exactly shell-quoted with `--config-dir`, `--data-dir`,
  and `--as-of`.
- Source-name filtering remains limited to the imported entity/unmatched-row
  steps; `heat-movers` does not receive `--source-name`.
- CLI JSON/table output includes the fifth step without creating data/config
  artifacts.
- Docs mention the post-import heat review handoff and keep local-only/no
  demand-proof/no platform-coverage wording.

## Documentation

Update:

- README post-import workflow description.
- `docs/community-signal-import.md` Review After Import section.
- `docs/cli-reference.md` `imported-review-workflow` entry.
- `docs/architecture.md` imported/community workflow narrative.
- `docs/source-boundaries.md` imported-review boundary.
- `docs/github-upload-checklist.md` Stage 58 docs check.
- `CHANGELOG.md`.

Docs must avoid implying that Fashion Radar collects social/platform data,
proves demand, verifies platform coverage, or performs compliance review.

## Release Checks

Before commit:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run ruff format --check src/fashion_radar/imported_review_workflow.py tests/test_imported_review_workflow.py tests/test_cli.py tests/test_cli_docs.py
git diff --check
```

Then run the standard full release gate and installed-wheel smoke for
`imported-review-workflow`.
