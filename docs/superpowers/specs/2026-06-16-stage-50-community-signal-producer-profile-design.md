# Stage 50 Community Signal Producer Profile Design

## Objective

Add a local, print-only Community Signal Producer Profile so external
user-controlled tools can discover the exact Fashion Radar handoff contract
before writing sanitized CSV/JSON files.

The profile is a contract description, not a source acquisition feature. It
must not add scraping, crawling, browser automation, account/session handling,
cookies, platform APIs, monitoring, watch folders, scheduler behavior, database
writes, report writes, dashboard state, or any compliance-review workflow.

## Context

Fashion Radar already supports local community signal handoffs:

- `examples/community-signals.example.csv`
- `examples/community-signals.example.json`
- `schemas/community-signals.schema.json`
- `community-signal-lint`
- `community-signal-lint-dir`
- `community-candidates`
- `community-candidates-dir`
- `import-signals-dir --dry-run`
- `import-signals-dir`
- `imported-review-workflow`

This is enough for a user to validate and import files after another tool has
created them. The missing piece is a machine-readable profile that a separate
tool can read or copy before it generates the files. That profile should expose
the existing strict contract in one stable command without adding another input
format or platform connector.

## Recommended Approach

Use a small Pydantic model and one Typer command:

- `src/fashion_radar/community_signal_profile.py` builds the profile and renders
  a compact table.
- `fashion-radar community-signal-profile --format table|json` prints the
  profile and exits.
- `examples/community-signal-profile.example.json` stores an example JSON
  payload generated from the same shape.

The profile will reuse existing constants from
`src/fashion_radar/community_signals.py`:

- `ALLOWED_COMMUNITY_SIGNAL_FIELDS`
- `PROHIBITED_COMMUNITY_SIGNAL_FIELDS`

Tests will lock the profile to the checked-in CSV header and JSON schema so
future changes do not silently drift across docs, schema, examples, and CLI
output.

## Profile Shape

The JSON output should have stable top-level keys:

```json
{
  "contract_version": "community-signals/v1",
  "execution_mode": "print_only",
  "schema_path": "schemas/community-signals.schema.json",
  "example_paths": [
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json"
  ],
  "supported_input_formats": ["csv", "json"],
  "csv_header": [
    "url",
    "title",
    "published_at",
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at"
  ],
  "required_fields": ["url", "title", "published_at"],
  "optional_fields": [
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at"
  ],
  "allowed_fields": [
    "url",
    "title",
    "published_at",
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at"
  ],
  "prohibited_fields": [
    "account_id",
    "author_handle",
    "cookie",
    "direct_message",
    "follower_count",
    "full_post_body",
    "image_url",
    "profile_url",
    "raw_comment",
    "session",
    "token",
    "video_url"
  ],
  "json_envelopes": [
    "top_level_array",
    "object_with_items_only"
  ],
  "field_notes": {
    "url": "Source URL or stable reference URL for the observed item.",
    "title": "Short observed text, headline, or normalized signal phrase.",
    "published_at": "ISO 8601-compatible publication or observation timestamp.",
    "summary": "Short sanitized note for local review.",
    "source_name": "Display name for the external tool or local export; import commands can supply a fallback when omitted.",
    "platform": "Short local provenance label; not platform coverage, source acquisition, demand proof, or source ranking.",
    "source_weight": "Local score weight accepted in the range (0, 5]; importer default is 1.0 when omitted or blank.",
    "collected_at": "Timestamp for when the external tool produced the row; importer may use the import timestamp when omitted."
  },
  "field_rules": {
    "source_weight": {
      "exclusive_minimum": 0,
      "maximum": 5,
      "default": 1.0
    }
  },
  "unsupported_capabilities": [
    "scraping",
    "browser_automation",
    "account_login",
    "cookies_sessions",
    "platform_api",
    "compliance_review",
    "source_acquisition",
    "media_download",
    "watching_monitoring",
    "scheduling"
  ],
  "recommended_commands": [
    "fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern \"*.csv\" --source-name \"Community Tool Export\" --strict",
    "fashion-radar community-candidates-dir ./exports --input-format csv --pattern \"*.csv\" --config-dir \"$PWD/configs\" --as-of \"$AS_OF\" --source-name \"Community Tool Export\"",
    "fashion-radar import-signals-dir ./exports --format csv --pattern \"*.csv\" --source-name \"Community Tool Export\" --data-dir \"$PWD/data\" --dry-run",
    "fashion-radar import-signals-dir ./exports --format csv --pattern \"*.csv\" --source-name \"Community Tool Export\" --imported-at \"$AS_OF\" --data-dir \"$PWD/data\"",
    "fashion-radar imported-review-workflow --data-dir \"$PWD/data\" --config-dir \"$PWD/configs\" --as-of \"$AS_OF\" --source-name \"Community Tool Export\""
  ],
  "boundaries": [
    "Prints the local handoff contract only.",
    "Does not read handoff files or directories.",
    "Does not create config, data, report, dashboard, or SQLite artifacts.",
    "Does not fetch URLs, search platforms, log in, store cookies, automate browsers, call platform APIs, monitor communities, rank sources, or verify platform coverage.",
    "Does not provide a compliance-review workflow."
  ]
}
```

The exact ordering matters because the profile is meant to be copyable by other
tools. `csv_header` and `allowed_fields` should keep the same canonical order.
`schema_path` and `example_paths` must point to the existing import contract,
not to a new import schema. `prohibited_fields` should be sorted for
deterministic output. `unsupported_capabilities` should be structured so tests
can assert boundaries without banning words such as `cookie` and `session`,
which are valid prohibited-field values.

## CLI Behavior

Command:

```bash
fashion-radar community-signal-profile --format table
fashion-radar community-signal-profile --format json
```

Behavior:

- No required path arguments.
- No config/data/reports options.
- No filesystem reads except normal package/module import.
- No filesystem writes.
- No network calls.
- `--format table` prints a compact human-readable profile.
- `--format json` prints the full profile with stable keys.
- Typer handles invalid `--format` values before the command body runs.

## Tests

Add tests that prove:

- The profile object matches the JSON schema required fields and property names.
- The profile points to `schemas/community-signals.schema.json`,
  `examples/community-signals.example.csv`, and
  `examples/community-signals.example.json` as the import contract anchors.
- The profile `csv_header` matches
  `examples/community-signals.example.csv`.
- `allowed_fields` matches `ALLOWED_COMMUNITY_SIGNAL_FIELDS`.
- `prohibited_fields` matches `PROHIBITED_COMMUNITY_SIGNAL_FIELDS`.
- Prohibited fields are disjoint from allowed row fields.
- `field_rules.source_weight` mirrors the schema and `ManualSignalRow` bounds:
  greater than `0`, maximum `5`, default `1.0`.
- The Pydantic model forbids extra top-level fields, requires required model
  fields, and emits JSON Schema with `additionalProperties: false`.
- The profile JSON is not shaped like a community signal import file and is
  rejected by `lint_community_signal_file(..., input_format="json")` as
  `invalid_file`.
- The checked-in profile example matches the generated profile exactly.
- The checked-in profile example text is byte-for-byte deterministic with
  `model_dump_json(indent=2) + "\n"`.
- The table renderer includes the contract version, supported formats, CSV
  header, required fields, optional fields, prohibited fields, JSON envelope
  forms, source-weight bounds, unsupported capabilities, recommended commands,
  and local boundary lines.
- The CLI help documents `--format`.
- The CLI help does not expose path/config/data/report/import/platform controls
  such as `--config-dir`, `--data-dir`, `--reports-dir`, `--pattern`,
  `--input-format`, `--source-name`, `--imported-at`, or `--dry-run`.
- The CLI JSON output parses and has stable key order.
- The CLI table output includes the expected contract markers.
- The CLI JSON output is deterministic across different cwd and environment
  path variables.
- The CLI command body does not inspect handoff paths, read directories, open
  SQLite, run subprocesses, or call collection/import/report helpers when those
  functions are monkeypatched to fail.
- The real CLI process does not create config/data/report directories, SQLite
  files, reports, digests, dashboard state, or collection workflow artifacts
  when run from a temporary directory with environment path variables set.
- Invalid `--format yaml` exits non-zero without creating artifacts.
- CLI docs and GitHub upload checklist stay in sync with the new public
  command.
- The new profile example is required in the sdist archive.

## Documentation

Update:

- `README.md`: mention the profile command in the external community handoff
  path.
- `docs/community-signal-import.md`: add a producer profile section before
  preflight lint. The section must explicitly mention
  `examples/community-signal-profile.example.json`.
- `docs/community-signal-quality.md`: tell producers to print the profile before
  linting.
- `docs/cli-reference.md`: list `community-signal-profile`.
- `docs/source-boundaries.md`: describe the command as print-only local
  contract introspection.
- `docs/architecture.md`: include it in the local import/community signal
  component.
- `docs/github-upload-checklist.md`: include the command in the installed-wheel
  help loop.
- `CHANGELOG.md`: add an Unreleased entry.

## Release And Packaging

Add `examples/community-signal-profile.example.json` to
`scripts/check_package_archives.py` and the matching test fixture in
`tests/test_package_archives.py` so the sdist includes the profile example.

No dependency changes are required. `uv.lock` should remain unchanged.

## Out Of Scope

This stage does not:

- Add adapters for Instagram, TikTok, X, Xiaohongshu, Reddit, Discord, WeChat,
  or any other community/social platform.
- Add scraping, crawler development, browser automation, login/session/cookie
  handling, proxies, CAPTCHA handling, source acquisition, or platform API
  calls.
- Add metadata sidecars or platform-specific export importers.
- Change the existing import parser semantics.
- Change scoring, matching, dashboard, report, scheduling, collection, or
  retention behavior.
- Add any compliance-review feature.

## Verification

Focused verification should include:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py tests/test_community_signal_import_contract.py tests/test_cli.py::test_community_signal_profile_help_lists_format tests/test_cli.py::test_community_signal_profile_prints_table tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_signal_profile_does_not_create_project_artifacts tests/test_cli_docs.py::test_cli_reference_lists_every_public_command tests/test_cli_docs.py::test_upload_checklist_help_loop_matches_public_commands tests/test_package_archives.py -q
```

Release verification should include the project-standard full test, lint,
format, lock, sync, package archive, first-run smoke, release hygiene, diff
whitespace, Claude Code release review, commit, push, and GitHub Actions checks.
