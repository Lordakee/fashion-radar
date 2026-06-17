# Stage 64 External Tool Workflow Design

## Objective

Add a local, print-only `fashion-radar external-tool-workflow` command that
prints a copyable workflow for user-controlled external/community tools before
their sanitized CSV/JSON exports enter the existing community signal handoff
path.

This stage connects the Stage 62 adapter registry and Stage 63 template rows to
the local profile, manifest, workflow, lint, readiness, dry-run, import, and
post-import review commands. It is meant for future Xiaohongshu/Rednote,
Instagram, TikTok, X/search, media metadata, and generic community handoff
tools without adding platform collection to Fashion Radar itself.

## Architecture

Create a new `src/fashion_radar/external_tool_workflow.py` module with a
Pydantic workflow model and a table renderer. The builder reuses the static
external tool adapter registry for adapter metadata, then emits named workflow
steps as shell-quoted command strings. The CLI exposes table and JSON output.

The command remains stdout-only and print-only. It does not run the generated
commands. It does not read the supplied directory, validate files, import rows,
open SQLite, write artifacts, call upstream tools, launch browser automation,
call platform APIs, schedule monitoring, acquire sources, prove demand, rank
sources, verify platform coverage, or add any compliance-review product
feature.

## Data Contract

The workflow model uses this contract version:

```text
external-tool-workflow/v1
```

The stable top-level key order is:

```text
contract_version
execution_mode
adapter_id
display_name
platform_label
directory
input_format
pattern
as_of
config_dir
data_dir
source_name
step_count
steps
boundaries
```

`execution_mode` is always `print_only`.

`adapter_id` defaults to `generic_community_export` when the CLI caller does
not provide `--adapter`. For a known adapter, the builder uses the adapter's
recommended input format, pattern, source name, platform label, display name,
and directory. The caller may override `--input-format`, `--pattern`, and
`--source-name` for local handoff variations. Unknown adapter ids raise
`ValueError("Unknown external tool adapter: <id>")`.

`steps` is a list of objects with this key order:

```text
order
name
purpose
command
suggested_effect
```

The workflow has eleven deterministic steps:

1. `inspect_adapter_registry` (`print_only`)
2. `print_adapter_template_json` (`print_only`)
3. `print_signal_profile` (`print_only`)
4. `print_handoff_manifest` (`print_only`)
5. `print_handoff_workflow` (`print_only`)
6. `lint_export_directory` (`read_only`)
7. `preview_candidate_phrases` (`read_only`)
8. `review_handoff_readiness` (`read_only`)
9. `dry_run_directory_import` (`read_only`)
10. `import_directory_signals` (`updates_local_imports`)
11. `print_post_import_review` (`print_only`)

The command strings are built with `shlex.join` only. Paths are converted with
`str(Path(...))` and are not resolved, created, inspected, globbed, statted, or
read.

## CLI

Add:

```bash
fashion-radar external-tool-workflow --adapter instaloader --format table
fashion-radar external-tool-workflow --adapter instaloader --format json
```

Options:

- `--adapter`: known adapter id, default `generic_community_export`.
- `--directory`: external tool export directory printed into generated local
  commands, default `./exports`.
- `--config-dir`: local config directory printed into generated local commands.
- `--data-dir`: local data directory printed into generated local commands.
- `--as-of`: deterministic UTC timestamp, default `2026-06-13T12:00:00Z`.
- `--input-format`: optional `csv|json` override. When omitted, use adapter
  metadata.
- `--pattern`: optional glob pattern override. When omitted, use adapter
  metadata.
- `--source-name`: optional source-name override. Blank or omitted values fall
  back to adapter metadata.
- `--format table|json`: output format, default `table`.

Invalid `--as-of` values exit with status `1` before the builder runs, matching
the existing workflow command guard pattern. Invalid `--format` values are
rejected by Typer before the builder runs.

## Output Semantics

Table output contains metadata, a clear "Commands were not executed." line, the
workflow steps, and boundaries. Table cells replace `|`, carriage returns, and
newlines before printing.

JSON output is the full workflow metadata model. Unlike
`external-tool-template --format json`, it is not importable handoff row JSON.
It is a workflow contract for local orchestration and documentation.

## Implementation Method

1. Write failing unit tests for the workflow model, exact steps, adapter
   defaults, override behavior, table sanitization, unknown adapter handling,
   invalid timestamp handling, and model extra-field rejection.
2. Implement `external_tool_workflow.py` with Pydantic models, constants,
   builder, `shlex.join` command construction, and table rendering.
3. Write failing CLI tests for help text, JSON output, table output, unknown
   adapter errors, invalid `--as-of`, invalid `--format`, no directory/SQLite
   artifacts, and no side-effect calls.
4. Wire the Typer command near `external-tool-adapters` and
   `external-tool-template`.
5. Add first-run smoke JSON validation for the workflow contract.
6. Update docs and docs-drift tests so README, CLI reference, import guide,
   quality guide, source boundaries, architecture, upload checklist, AGENTS,
   and CHANGELOG mention the command and preserve local print-only boundaries.
7. Run focused tests, full tests, lint, format check, release hygiene,
   first-run smoke, package/installed-wheel checks, opencode release review,
   commit, push, and GitHub Actions polling.

## Files

Create:

- `src/fashion_radar/external_tool_workflow.py`
- `tests/test_external_tool_workflow.py`
- `docs/reviews/opencode-stage-64-plan-review-prompt.md`
- `docs/reviews/opencode-stage-64-plan-review.md`
- `docs/reviews/opencode-stage-64-release-review-prompt.md`
- `docs/reviews/opencode-stage-64-release-review.md`

Modify:

- `src/fashion_radar/cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_cli.py`
- `tests/test_first_run_smoke.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/cli-reference.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`

## Testing Strategy

Focused tests:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_workflow.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
```

Quality gates:

```bash
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config lock --check
git diff --check
uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Packaging gates:

```bash
tmp_build="$(mktemp -d)"
tmp_env="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
python3 scripts/check_package_archives.py "$tmp_build"
uv --no-config venv "$tmp_env/venv"
uv --no-config pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" external-tool-workflow --adapter instaloader --format json | "$tmp_env/venv/bin/python" -m json.tool >/dev/null
"$tmp_env/venv/bin/fashion-radar" external-tool-workflow --adapter instaloader --format table >/dev/null
```

## Scope Boundaries

In scope:

- Static local workflow metadata.
- Shell-quoted command strings for existing local Fashion Radar commands.
- Adapter-specific defaults and explicit local overrides.
- Table and JSON rendering.
- Tests and docs proving print-only behavior.

Out of scope:

- Platform connectors.
- Scraping.
- Browser automation.
- Platform APIs.
- Account/session/cookie/token behavior.
- Media downloads.
- Reading external tool output files.
- Writing generated files.
- Running upstream tools.
- Running generated commands.
- SQLite access from this command.
- Monitoring or scheduling.
- Source acquisition.
- Demand proof.
- Ranking.
- Coverage verification.
- Compliance-review product features.

## Self-Review

- No placeholder requirements remain.
- The command is focused enough for one implementation plan.
- JSON output is intentionally workflow metadata, not importable handoff rows;
  importable example rows remain the responsibility of `external-tool-template`.
- The design keeps future social/community source support as a local handoff
  workflow and does not add built-in platform collection.
