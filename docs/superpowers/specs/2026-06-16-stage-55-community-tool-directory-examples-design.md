# Stage 55 Community Tool Directory Examples Design

## Objective

Add checked-in external community tool export directory examples so a future
user-controlled social/community tool can copy a complete local directory
layout, write sanitized CSV or JSON files there, and run the existing directory
lint, dry-run import, manifest, and workflow commands.

## Background

Stage 54 added importable single-file external tool handoff templates:

- `examples/community-tool-handoff.example.csv`
- `examples/community-tool-handoff.example.json`

Fashion Radar already has the runtime commands needed for directory handoff:

- `community-signal-lint-dir`
- `community-candidates-dir`
- `import-signals-dir --dry-run`
- `import-signals-dir`
- `community-handoff-manifest`
- `community-handoff-workflow`

The remaining gap is practical producer onboarding. External tools have
single-file templates, but not a checked-in directory shape they can mirror.
The community import docs also contain a manifest JSON excerpt whose
`example_paths` can drift from the actual profile/manifest output.

## Technical Stack

- Existing Python 3.11+ package.
- Existing community signal schema and manual-signal importer.
- Existing Typer CLI directory handoff commands.
- Existing pytest, docs drift tests, and package archive checker.
- Markdown examples and docs only for producer-facing instructions.
- No new dependencies.

## Scope

Stage 55 will add:

- `examples/community-tool-handoff-directory.example/README.md`
- `examples/community-tool-handoff-directory.example/csv/community-tool-a.csv`
- `examples/community-tool-handoff-directory.example/csv/community-tool-b.csv`
- `examples/community-tool-handoff-directory.example/json/community-tool-a.json`
- `examples/community-tool-handoff-directory.example/json/community-tool-b.json`
- Focused tests proving the checked-in CSV and JSON directories:
  - contain two matched handoff files each;
  - lint cleanly;
  - load through the existing manual importer;
  - pass `community-signal-lint-dir`;
  - pass `import-signals-dir --dry-run`;
  - do not create config/data/report/SQLite artifacts during dry-run checks.
- Package archive requirements for the new directory example files.
- Docs updates that point external tools to the checked-in `csv/` and `json/`
  sample directories.
- Docs drift coverage that keeps the manifest example's `example_paths` aligned
  with the current four profile example paths.

## Directory Layout

The new checked-in example layout will be:

```text
examples/community-tool-handoff-directory.example/
  README.md
  csv/
    community-tool-a.csv
    community-tool-b.csv
  json/
    community-tool-a.json
    community-tool-b.json
```

The `csv/` and `json/` directories are separate because the directory commands
take one `--input-format` and one `--pattern` per run. They intentionally do
not include generated manifests inside the matched directories. A saved manifest
must live outside the matched export directory, or use an excluded filename or
pattern.

## Data Contract

The sample CSV and JSON files will use only existing community signal fields:

- `url`
- `title`
- `published_at`
- `summary`
- `source_name`
- `platform`
- `source_weight`
- `collected_at`

All URLs will use `https://example.com/...`, `source_name` will be
`External Community Tool`, and `platform` will be `community`. The rows are
synthetic and short; they do not include raw comments, handles, account IDs,
profile URLs, media URLs, cookies, sessions, tokens, full post bodies, or
private material.

## Boundaries

Stage 55 does not add:

- new CLI commands;
- schema changes;
- dependency or lockfile changes;
- source acquisition;
- scraping or crawling;
- browser automation;
- account login or account automation;
- cookies, sessions, tokens, or stored platform credentials;
- platform API clients;
- monitoring, scheduling, watching, or long-running services;
- media download;
- demand proof;
- platform/community coverage verification;
- source ranking;
- compliance-review, legal-review, approval UI, or policy workflow features.

The feature remains a local file/directory handoff example for external tools
the user controls.

## Documentation Strategy

Update:

- `README.md` near the external community tools section.
- `docs/community-signal-import.md` in the external template and directory
  workflow sections.
- `docs/github-upload-checklist.md` package/readiness checks.
- `docs/source-boundaries.md`, `docs/architecture.md`, and `AGENTS.md` with
  compact maintainer guardrails for directory examples.
- `CHANGELOG.md` under Unreleased.

Docs should use stable product wording such as "external community tool export
directory examples" rather than exposing stage labels to users.

## Testing Strategy

Targeted tests:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_tool_handoff_directory_examples.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py tests/test_cli_docs.py -q
```

Release verification follows the existing hardened workflow:

- full pytest;
- Ruff check;
- Ruff format check;
- lock and mirror-free checks;
- release hygiene;
- first-run smoke;
- package build and archive check;
- installed-wheel smoke;
- local opencode release review;
- commit/upload;
- GitHub Actions confirmation.
