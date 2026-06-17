# Stage 66 External Tool Readiness Design

## Goal

Add a local read-only `external-tool-readiness` CLI command that helps users
check whether a selected free external/community tool handoff path is ready on
their machine before they create sanitized CSV/JSON local export rows.

This stage moves Fashion Radar closer to the original social/community workflow:
the project can name known free-first upstream tools such as Rednote MCP,
Xiaohongshu crawler, Instaloader, TikTok-Api, yt-dlp, and X search exports, then
print local readiness guidance and copyable next-step commands. It still does
not become a platform scraper or connector.

## Scope

In scope:

- Add a new `external-tool-readiness` command.
- Resolve the same adapter metadata used by `external-tool-adapters`,
  `external-tool-template`, and `external-tool-workflow`.
- Print deterministic readiness metadata for one adapter, defaulting to
  `generic_community_export`.
- Check only local command availability with `shutil.which` for known upstream
  command names where a command name is safely representable.
- Never execute upstream tools.
- Print recommended mirror-friendly install hints where useful, for example:
  `python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ...` or
  `npm config set registry https://registry.npmmirror.com`.
- Print next-step Fashion Radar handoff commands:
  `external-tool-adapters`, `external-tool-template`,
  `external-tool-workflow`, `community-signal-profile`, and local directory
  handoff commands.
- Provide table and JSON output.
- Keep paths as printed metadata only; do not inspect directories or files.
- Update README, CLI reference, source-boundary docs, architecture docs,
  quality/import docs, upload checklist, AGENTS, CHANGELOG, and docs drift
  tests.
- Add installed-wheel help smoke coverage.

Out of scope:

- No scraping, browser automation, platform API calls, account/cookie/session
  behavior, login flows, proxy pools, media download, monitoring, scheduling,
  source acquisition, demand proof, ranking, coverage verification, or
  compliance-review product feature.
- No running `rednote-mcp`, Xiaohongshu crawler, Instaloader, TikTok-Api,
  yt-dlp, snscrape, AnySearch, or other upstream tools.
- No installing dependencies automatically.
- No writing config, data, report, dashboard, workflow, or handoff artifacts.
- No directory reads, file validation, row import, SQLite open/write, matching,
  scoring, or report generation.
- No dashboard changes.

## User Flow

Example:

```bash
uv run fashion-radar external-tool-readiness \
  --adapter instaloader \
  --directory "$PWD/exports" \
  --config-dir "$PWD/configs" \
  --data-dir "$PWD/data"

uv run fashion-radar external-tool-readiness \
  --adapter rednote_mcp \
  --format json
```

The command tells the user:

- which adapter was selected;
- which upstream command name is expected, if any;
- whether that local command is currently found on `PATH`;
- which mirror-friendly install command can be run manually;
- which Fashion Radar commands should be run next after the user creates
  sanitized export files.

The command does not prove the upstream tool can access any platform. It only
reports local command availability and handoff readiness guidance.

## Data Model

Create `src/fashion_radar/external_tool_readiness.py`.

Constants:

- `EXTERNAL_TOOL_READINESS_CONTRACT_VERSION = "external-tool-readiness/v1"`
- `EXTERNAL_TOOL_READINESS_EXECUTION_MODE = "local_read_only"`
- `DEFAULT_EXTERNAL_TOOL_READINESS_ADAPTER_ID = "generic_community_export"`

Models:

- `ExternalToolReadinessCheck`
  - `name: str`
  - `status: Literal["found", "missing", "not_applicable"]`
  - `command: str | None`
  - `path: str | None`
  - `detail: str`
  - `install_hint: str | None`
- `ExternalToolReadinessStep`
  - `order: int`
  - `name: str`
  - `purpose: str`
  - `command: str`
  - `suggested_effect: Literal["print_only", "read_only", "updates_local_imports"]`
- `ExternalToolReadiness`
  - `contract_version: str`
  - `execution_mode: Literal["local_read_only"]`
  - `adapter_id: str`
  - `display_name: str`
  - `platform_label: str`
  - `directory: str`
  - `input_format: ManualSignalFormat`
  - `pattern: str`
  - `as_of: str`
  - `config_dir: str`
  - `data_dir: str`
  - `source_name: str`
  - `checks: list[ExternalToolReadinessCheck]`
  - `step_count: int`
  - `steps: list[ExternalToolReadinessStep]`
  - `boundaries: list[str]`

JSON key order must be stable and tested.

## Adapter Command Mapping

Readiness checks use a small static mapping keyed by adapter id:

- `rednote_mcp`: command `rednote-mcp`; install hint
  `npm config set registry https://registry.npmmirror.com && npm install -g rednote-mcp`
- `xiaohongshu_crawler`: command `xiaohongshu-crawler`; install hint points to
  the upstream project docs and suggests using Python/pip mirrors if the tool is
  installed as a Python package.
- `instaloader`: command `instaloader`; install hint
  `python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple instaloader`
- `tiktok_api`: no reliable CLI command; status `not_applicable`; install hint
  `python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple TikTokApi`
- `yt_dlp`: command `yt-dlp`; install hint
  `python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple yt-dlp`
- `x_search_export`: no single required command; status `not_applicable`;
  detail says this adapter covers user-controlled X/search exports such as
  AnySearch or snscrape-derived sanitized files.
- `generic_community_export`: no upstream command; status `not_applicable`.

The command checks only `shutil.which(command)`. It must not spawn processes or
import upstream packages.

## Builder Semantics

`build_external_tool_readiness(adapter_id, directory, config_dir, data_dir,
as_of, input_format=None, pattern=None, source_name=None)`:

- Default `adapter_id` to `generic_community_export`.
- Parse `as_of` with `parse_datetime_utc`.
- Build the existing external tool adapter registry and resolve the selected
  adapter.
- Reject unknown adapters with `ValueError("Unknown external tool adapter: ...")`.
- Use adapter defaults for `input_format`, `pattern`, `source_name`, and
  directory when overrides are blank or missing.
- Build one check for local upstream command availability.
- Build copyable deterministic next steps:
  1. `external-tool-adapters`
  2. `external-tool-template`
  3. `external-tool-workflow`
  4. `community-signal-profile`
  5. `community-signal-lint-dir`
  6. `community-handoff-check-dir`
  7. `import-signals-dir --imported-at <as_of> --dry-run`
- Quote paths and values with `shlex.quote`/`shlex.join`.
- Accept an optional `which` callable for tests, but resolve the default lazily
  from `shutil.which` inside the builder so monkeypatching the module-level
  `shutil.which` remains reliable.
- Do not inspect `directory`, `config_dir`, or `data_dir`.

## Rendering

Table output:

- Starts with `External tool readiness.`
- Prints contract version, execution mode, `Commands were not executed.`, adapter
  metadata, local settings, checks, next steps, and boundaries.
- Sanitizes table cells by replacing pipes and line breaks, matching existing
  external tool renderers.

JSON output:

- Emits `ExternalToolReadiness.model_dump_json(indent=2)`.
- Includes readiness metadata and command strings only.
- Does not include environment variables, cookies, sessions, private file
  contents, or platform data.

## CLI

Add `fashion-radar external-tool-readiness`.

Options:

- `--adapter`: adapter id, default `generic_community_export`.
- `--directory`: suggested local export directory used in printed commands only.
- `--config-dir`: existing shared config directory option.
- `--data-dir`: existing shared data directory option.
- `--as-of`: UTC timestamp used in printed commands only.
- `--input-format`: optional `csv|json` override for later handoff commands.
- `--pattern`: optional file pattern override for later handoff commands.
- `--source-name`: optional source name override.
- `--format`: `table|json`, default `table`.

Error messages:

- Invalid date: `Could not build external tool readiness: invalid --as-of: ...`
- Unknown adapter: `Could not build external tool readiness: Unknown external tool adapter: missing`
- Invalid output format should be rejected by Typer before the builder is called.

## Tests

Add focused tests:

- `tests/test_external_tool_readiness.py`
  - stable contract/key order;
  - command found/missing/not-applicable behavior through monkeypatching
    `shutil.which`;
  - adapter defaults and overrides;
  - unknown adapter and invalid `as_of`;
  - command quoting;
  - table sanitization;
  - no-scope boundary terms.
- `tests/test_cli.py`
  - help lists options;
  - JSON output has stable keys;
  - table output prints boundaries and creates no artifacts;
  - unknown adapter error;
  - invalid `--as-of` does not call builder;
  - invalid `--format` does not call builder;
  - no side effects: guard Path inspection, subprocess, SQLite, importer, lint,
    collection, reporting, and package helpers.
- `tests/test_cli_docs.py`
  - docs mention `external-tool-readiness`;
  - upload checklist help loop includes it;
  - docs include boundary phrases.
- `scripts/check_first_run_smoke.py` / `tests/test_first_run_smoke.py`
  - installed help smoke includes `external-tool-readiness`;
  - `run_first_run_flow` explicitly executes
    `external-tool-readiness --adapter rednote_mcp --format json`;
  - validator ensures JSON shape is local read-only and not executable.

## Documentation

Update:

- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`

Required language:

- local read-only;
- command availability only;
- user-controlled external/community tools;
- sanitized CSV/JSON local file handoff;
- no adapters/upstream tools are run;
- no directory inspection, file reads, row import, SQLite open/write, or
  artifacts;
- no scraping, browser automation, platform APIs, account/cookie/session/token
  behavior, monitoring, scheduling, source acquisition, demand proof, ranking,
  or coverage verification;
- no compliance-review product feature.

## Verification

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_readiness.py -q
uv --no-config run --frozen pytest tests/test_cli.py -q -k "external_tool_readiness"
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check src/fashion_radar/external_tool_readiness.py src/fashion_radar/cli.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
uv --no-config run --frozen ruff format --check src/fashion_radar/external_tool_readiness.py src/fashion_radar/cli.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_cli_docs.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py
uv --no-config run --frozen pytest
uv --no-config run --frozen python scripts/check_release_hygiene.py
```

Before commit, run local `opencode` code review with
`zhipuai-coding-plan/glm-5.2 --variant max`.
