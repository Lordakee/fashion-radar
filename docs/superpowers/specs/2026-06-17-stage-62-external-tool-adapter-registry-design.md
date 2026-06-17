# Stage 62 External Tool Adapter Registry Design

## Objective

Add a local, print-only external social/community tool adapter registry that
helps user-controlled tools map their sanitized exports into the existing
community signal handoff contract.

The registry is for producer discovery and handoff planning only. It must not
run adapters, install tools, fetch URLs, log in, store cookies, call platform
APIs, automate browsers, monitor communities, schedule work, acquire sources,
prove demand, rank sources, verify platform coverage, or perform compliance
review.

## Context

Fashion Radar already has a local CSV/JSON handoff path for community signals:

- `community-signal-profile` prints the producer contract.
- `community-handoff-manifest` prints a directory manifest.
- `community-handoff-workflow` prints the lint, preview, readiness, dry-run,
  import, and review command sequence.
- `community-handoff-check-dir` validates a local handoff directory before
  import.

The gap is discoverability for future upstream tools. Users have named tools
and ecosystems such as Rednote/Xiaohongshu tools, Instaloader, TikTok-Api,
yt-dlp, X tooling, and other community exports. Fashion Radar should give those
tools a stable local target shape without turning them into core collectors.

## Recommended Approach

Create a focused `external_tool_adapters` module that returns deterministic
Pydantic models:

- `ExternalToolAdapterRegistry`
- `ExternalToolAdapter`
- `ExternalToolAdapterFieldMapping`

The registry will contain a small built-in list of known producer categories:

- `rednote_mcp`
- `xiaohongshu_crawler`
- `instaloader`
- `tiktok_api`
- `yt_dlp`
- `x_search_export`
- `generic_community_export`

Each adapter entry will describe:

- a stable adapter id;
- display name;
- platform label to write into the existing `platform` field;
- suggested `source_name`;
- input format recommendation (`csv` or `json`);
- suggested export directory and filename pattern;
- required output fields from the existing community signal contract;
- optional output fields from the existing community signal contract;
- source notes that explain what an upstream tool should map into `url`,
  `title`, `published_at`, `summary`, `source_name`, `platform`,
  `source_weight`, and `collected_at`;
- copyable local commands for profile, manifest, workflow, lint, readiness,
  dry-run import, import, and review.

The command recommendations reuse the existing community handoff commands and
quote all dynamic pieces with `shlex.join`.

## Public CLI

Add:

```bash
fashion-radar external-tool-adapters --format table
fashion-radar external-tool-adapters --format json
```

Optional filters:

```bash
fashion-radar external-tool-adapters --adapter instaloader --format json
fashion-radar external-tool-adapters --adapter rednote_mcp --as-of 2026-06-13T12:00:00Z --format table
```

Options:

- `--adapter`: optional adapter id. When omitted, print all adapters.
- `--format`: `table` or `json`, default `table`.
- `--directory`: export directory used only for generated command strings,
  default `./exports`.
- `--config-dir`: config directory used only for generated command strings,
  default existing config dir option.
- `--data-dir`: data directory used only for generated command strings,
  default existing data dir option.
- `--as-of`: timestamp used only for generated command strings, default
  `2026-06-13T12:00:00Z` for deterministic output.

The CLI must not inspect the supplied directory, read configs, open SQLite, run
subprocesses, import rows, create files, or contact networks.

Unknown adapter ids should exit non-zero with a clear message and should not
print a partial registry.

## Data Model

The registry should expose stable JSON keys in this order:

```text
contract_version
execution_mode
adapters
boundaries
```

Each adapter should expose stable JSON keys in this order:

```text
id
display_name
platform_label
suggested_source_name
recommended_input_format
recommended_pattern
suggested_export_directory
description
upstream_tool_examples
field_mappings
recommended_commands
boundaries
```

Each field mapping should expose:

```text
field
required
note
```

The registry must use only fields already accepted by the existing community
signal contract. It must not change `schemas/community-signals.schema.json`,
`ManualSignalRow`, the importer, SQLite schema, source config, collectors,
reports, dashboard, scheduling, or candidate scoring.

## Documentation

Update public docs to describe the registry as a local producer-discovery
registry:

- `README.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/cli-reference.md`
- `docs/github-upload-checklist.md`
- `CHANGELOG.md`

Docs must use the repository's existing boundary vocabulary:

- local;
- print-only;
- sanitized CSV/JSON local file handoff;
- user-controlled external/community tools;
- local provenance label;
- not platform collection;
- no connectors, scraping, browser automation, platform APIs, monitoring,
  scheduling, source acquisition, demand proof, ranking, or coverage
  verification.

## Testing

Add focused unit tests for:

- stable registry JSON shape;
- expected adapter ids and platform/source labels;
- adapter filtering;
- unknown adapter errors;
- generated command quoting;
- table rendering sanitizes cells;
- all adapter field mappings use allowed community signal fields only;
- CLI JSON and table output;
- docs-drift coverage for CLI reference, upload checklist, source boundaries,
  and changelog.

Extend first-run smoke only enough to validate that the installed CLI can print
the registry JSON and that it remains print-only. Do not add live collection or
external tool execution to first-run smoke.

## Out Of Scope

- No connector implementation.
- No scraper, crawler, browser automation, or platform API integration.
- No account login, cookies, sessions, tokens, or proxy guidance.
- No media downloads.
- No new dependency.
- No schema, migration, collector, scheduler, dashboard, report, digest, entity
  pack, or source pack change.
- No compliance-review product feature.
- No claims about platform coverage, demand proof, ranking, or market-wide
  trend authority.

## Self-Review

- Placeholder scan: no TBD/TODO placeholders remain.
- Internal consistency: CLI, model, docs, and tests all keep the registry
  print-only and local.
- Scope check: this is one implementation node. It adds a registry surface and
  documentation without changing the import contract or core collection.
- Ambiguity check: external tools are examples of upstream producers only; the
  command never runs them.
