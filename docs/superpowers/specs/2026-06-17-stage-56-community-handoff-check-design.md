# Stage 56 Community Handoff Check Design

## Objective

Add a local-only `community-handoff-check-dir` command that lets a user or
user-controlled external community tool run the existing directory lint,
candidate preview, and import dry-run checks through one read-only report before
importing community signal files.

## Background

Stage 55 added checked-in external community tool export directory examples:

- `examples/community-tool-handoff-directory.example/README.md`
- `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`
- `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`
- `examples/community-tool-handoff-directory.example/json/community-tool-a.json`
- `examples/community-tool-handoff-directory.example/json/community-tool-b.json`

The existing CLI already exposes the three checks an external tool should run:

- `community-signal-lint-dir`
- `community-candidates-dir`
- `import-signals-dir --dry-run`

Those commands are correct, but they require a user or upstream tool to run and
interpret three separate commands. Stage 56 adds one local read-only aggregate
check so the handoff readiness path is easier to automate without changing the
underlying import, preview, or directory matching behavior.

## Technical Stack

- Existing Python 3.11+ package.
- Existing Typer CLI.
- Existing Pydantic result models.
- Existing community signal directory linter.
- Existing community candidate directory preview.
- Existing manual signal directory dry-run importer.
- Existing pytest and docs drift tests.
- No new dependencies.

## Proposed Command

```bash
uv run fashion-radar community-handoff-check-dir ./exports \
  --input-format csv \
  --pattern "*.csv" \
  --config-dir "$PWD/configs" \
  --as-of "2026-06-13T12:00:00Z" \
  --source-name "Community Tool Export" \
  --format json
```

Options:

- `DIRECTORY`: local directory containing matched direct-child handoff files.
- `--config-dir`: existing config directory option used only for candidate
  preview settings and entity aliases.
- `--input-format csv|json`: handoff file format. Default `csv`.
- `--pattern`: non-recursive direct-child filename glob. Default `*.csv`.
- `--as-of`: required UTC timestamp for candidate preview windows.
- `--source-name`: fallback source name. Blank values normalize to
  `Community Tool Export`.
- `--limit`: maximum candidates to include. Default `50`; `0` is allowed.
- `--strict`: make lint warnings fail the aggregate check.
- `--format table|json`: output format.

The command intentionally does not add `--dry-run`, because it is inherently a
read-only check. It intentionally does not add `--output-format`, because
`--format` is available for output when input uses `--input-format`. It
intentionally does not add `--data-dir`, because the direct dry-run helper does
not open SQLite.

## Result Model

Create `src/fashion_radar/community_handoff_check.py` with:

- `CommunityHandoffDirectoryCheckFinding`
- `CommunityHandoffDirectoryCheckResult`
- `check_community_handoff_directory`
- `render_community_handoff_directory_check_table`

Top-level JSON fields:

- `directory`
- `input_format`
- `pattern`
- `as_of`
- `config_dir`
- `source_name`
- `execution_mode`
- `strict`
- `limit`
- `ok`
- `failed_check_count`
- `warning_count`
- `findings`
- `community_signal_lint`
- `candidate_preview`
- `import_dry_run`

`execution_mode` is the literal `local_read_only`.

The nested payloads reuse existing models directly:

- `CommunitySignalDirectoryLintResult`
- `CommunityCandidateDirectoryPreview | None`
- `ManualSignalDirectoryDryRunResult`

The aggregate `ok` value uses logical check status instead of summing nested
finding counts:

- lint fails when `community_signal_lint.error_count > 0`;
- lint also fails when `--strict` is set and
  `community_signal_lint.warning_count > 0`;
- candidate preview fails when it cannot run because the directory cannot be
  read or validated by the existing preview helper;
- import dry-run fails when `import_dry_run.error_count > 0`.

Candidate preview failures are recorded as sanitized high-level findings and
leave `candidate_preview` as `null`; lint and import dry-run diagnostics remain
available in the same output.

## Data Flow

`community-handoff-check-dir` will:

1. parse `--as-of` before reading the directory;
2. load `scoring.yaml` and optional `entities.yaml` before reading the
   directory;
3. normalize `source_name`;
4. call `lint_community_signal_directory`;
5. call `preview_community_candidate_directory`;
6. catch `ManualSignalImportError` from candidate preview and record a
   high-level `candidate_preview` finding without losing lint/dry-run output;
7. call `dry_run_manual_signal_directory`;
8. render table or JSON;
9. exit non-zero when the aggregate result is not ok.

This preserves existing directory matching semantics: matching regular files
directly under the supplied directory only, sorted by path, no recursion.

## Boundaries

Stage 56 does not add:

- source acquisition;
- platform collection;
- scraping or crawling;
- browser automation;
- account login;
- cookies, sessions, tokens, or stored platform credentials;
- platform API clients;
- monitoring, scheduling, watching, or long-running services;
- media download;
- demand proof;
- source ranking;
- platform/community coverage verification;
- entity generation;
- SQLite writes;
- report/dashboard/digest generation;
- profile, workflow, or manifest ordering changes;
- compliance-review, legal-review, approval UI, authorization verifier, or
  policy workflow features.

The command reads only local files and local config supplied by the user. It
does not import rows and does not create config, data, report, dashboard,
digest, or SQLite artifacts.

## Documentation Strategy

Update:

- `README.md`
- `docs/community-signal-import.md`
- `docs/cli-reference.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`

Docs should present the command as a local handoff readiness check/report for
user-controlled external community tools. The docs must not frame it as a
platform connector, platform coverage proof, demand proof, ranking, or
compliance feature.

Do not add the command to `community-signal-profile.recommended_commands`,
`community-handoff-workflow`, or the embedded manifest workflow in Stage 56.
Keeping it independent avoids changing existing producer workflow contracts.

## Testing Strategy

Add:

- `tests/test_community_handoff_check.py` for result model, builder, and table
  rendering behavior.
- `tests/test_cli.py` coverage for command help, JSON output, table output,
  exit status, parser validation, side-effect guardrails, and no-artifact
  behavior.
- `tests/test_cli_docs.py` drift coverage for CLI reference, README/import docs,
  upload checklist, source boundaries, architecture, AGENTS, and changelog.

Targeted commands:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_handoff_check.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_cli.py tests/test_cli_docs.py -q
```

Release verification follows the existing full workflow: full pytest, Ruff,
format check, lock/sync/mirror checks, release hygiene, first-run smoke,
package build/archive check, installed-wheel smoke, local opencode release
review, upload, and GitHub Actions confirmation.
