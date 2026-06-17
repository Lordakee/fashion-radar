# Stage 63 External Tool Template Design

## Objective

Add a local, print-only `fashion-radar external-tool-template` command that
prints adapter-specific sanitized CSV/JSON community handoff template rows for
user-controlled external/community tools.

This stage helps upstream tools such as Rednote/Xiaohongshu exporters,
Instaloader, TikTok-Api, yt-dlp metadata exporters, X/search exports, and
generic community exports understand the exact local row shape they should
produce before the existing lint, manifest, readiness, dry-run, import, and
review commands run.

## Architecture

Stage 62 added `external-tool-adapters` as a print-only adapter registry. Stage
63 adds a focused template layer on top of that registry:

- `src/fashion_radar/external_tool_templates.py` builds deterministic Pydantic
  models for one adapter template and one template collection.
- The template builder reuses
  `build_external_tool_adapter_registry(...).adapter_by_id(...)` so adapter ids,
  source names, input formats, patterns, platform labels, directory defaults,
  and field mappings stay aligned with the registry.
- The CLI prints one of three stdout formats:
  - `table`: human-readable adapter metadata, field mapping, rows, and
    boundaries.
  - `json`: importable community handoff JSON in the schema-supported
    `{"items": [...]}` shape, with no metadata keys outside `items`.
  - `csv`: importable community handoff CSV with the community signal header
    plus example rows.

The command is stdout-only and print-only. It does not write files, read
directories, inspect handoff files, validate rows, import rows, open SQLite,
install upstream tools, fetch URLs, log in, store cookies, automate browsers,
call platform APIs, download media, monitor communities, schedule work, acquire
sources, prove demand, rank sources, verify platform coverage, or provide a
compliance-review workflow.

## Data Contract

The internal template model uses this contract version for table rendering and
unit-level stability checks:

```text
external-tool-template/v1
```

The internal model has this stable key order:

```text
contract_version
execution_mode
adapter_id
display_name
platform_label
source_name
recommended_input_format
recommended_pattern
suggested_export_directory
csv_header
items
field_mappings
recommended_commands
boundaries
```

`execution_mode` is always `print_only`.

The CLI `--format json` output is intentionally different from the internal
metadata model: it prints only a community-signal handoff object with one
allowed top-level key:

```json
{
  "items": []
}
```

That keeps JSON output directly compatible with
`schemas/community-signals.schema.json` and the existing import/lint path. The
CLI `--format csv` output is likewise directly compatible with the CSV handoff
contract. Metadata such as `contract_version`, `adapter_id`, field mappings,
and boundaries appears only in table output and in internal model tests.

`csv_header` must equal the community signal profile allowed field order:

```text
url,title,published_at,summary,source_name,platform,source_weight,collected_at
```

`items` contains deterministic synthetic example rows. They are valid community
signal rows and intentionally use `example.com` URLs. They contain short
sanitized observations only, not raw comments, full post bodies, account ids,
cookies, sessions, tokens, profile URLs, media URLs, follower counts, or direct
messages.

For every item:

- `source_name` equals the adapter's `suggested_source_name`.
- `platform` equals the adapter's `platform_label`.
- `source_weight` stays in the existing community signal range `(0, 5]`.
- `published_at` and `collected_at` are deterministic UTC timestamps derived
  from `--as-of`, not the current clock.

## CLI

Add:

```bash
fashion-radar external-tool-template --adapter instaloader --format table
fashion-radar external-tool-template --adapter instaloader --format json
fashion-radar external-tool-template --adapter instaloader --format csv
```

Options:

- `--adapter`: optional adapter id. When omitted, the command prints one
  template with two synthetic example rows per known adapter. When supplied, it
  prints rows for that adapter only.
- `--directory`: optional suggested export directory, defaults to the same
  `DEFAULT_EXPORT_DIRECTORY` used by `external-tool-adapters`; table metadata
  and recommended commands only.
- `--config-dir`: existing shared config-dir option, printed in table
  recommended commands only.
- `--data-dir`: existing shared data-dir option, printed in table recommended
  commands only.
- `--as-of`: deterministic UTC timestamp, defaults to
  `DEFAULT_ADAPTER_AS_OF`.
- `--format table|json|csv`: output format, default `table`.

Unknown adapter ids exit with status `1` and a clear stderr message.

Invalid `--as-of` values exit with status `1` through the same build error
path.

## Implementation Method

1. Add tests first for the template builder and renderers.
2. Implement the new module with small Pydantic models, deterministic row
   generation, importable JSON rendering, CSV rendering via Python's `csv`
   module, table sanitization, and adapter filtering through the Stage 62
   registry.
3. Wire the CLI command with Typer using existing option style.
4. Add CLI tests for JSON, CSV, table, omitted adapter, path quoting in table
   recommended commands, unknown adapter errors, and invalid timestamp errors.
5. Add first-run smoke coverage for the JSON output.
6. Update docs and docs-drift tests so README, CLI reference, source
   boundaries, community signal docs, upload checklist, AGENTS, and CHANGELOG
   all describe the command and preserve the local print-only boundary.
7. Add package archive coverage only if a checked-in example file is introduced.
   This design does not introduce checked-in example files, so package archive
   contents are unchanged.
8. Run focused tests, full tests, lint, format check, lock check, release
   hygiene, first-run smoke, build/package archive checks, installed-wheel
   smoke, opencode release review, commit, push, and GitHub Actions polling.

## Files

Create:

- `src/fashion_radar/external_tool_templates.py`
- `tests/test_external_tool_templates.py`
- `docs/reviews/opencode-stage-63-plan-review-prompt.md`
- `docs/reviews/opencode-stage-63-plan-review.md`
- `docs/reviews/opencode-stage-63-release-review-prompt.md`
- `docs/reviews/opencode-stage-63-release-review.md`

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
uv --no-config run --frozen pytest tests/test_external_tool_templates.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
```

Quality gates:

```bash
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config lock --check
git diff --check
uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
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
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format json | "$tmp_env/venv/bin/python" -m json.tool >/dev/null
"$tmp_env/venv/bin/fashion-radar" external-tool-template --adapter instaloader --format csv >/dev/null
```

## Scope Boundaries

This stage is local and print-only. It prints adapter-specific template rows
for sanitized CSV/JSON local file handoff by user-controlled
external/community tools. It is not platform collection and has no connectors,
no scraping, no browser automation, no platform APIs, no monitoring, no
scheduling, no source acquisition, no demand proof, no ranking, and no coverage
verification.

It does not add a compliance-review product feature.

## Self Review

- Placeholder scan: no `TBD`, `TODO`, or unspecified implementation details.
- Scope check: focused on one print-only command and one module.
- Consistency check: command name, model name, contract version, and docs terms
  use `external-tool-template` / `external-tool-template/v1` consistently.
- Boundary check: explicitly excludes platform collection, connectors,
  scraping, browser automation, APIs, sessions/cookies, media downloads,
  scheduling, demand proof, ranking, coverage verification, and compliance
  review features.
