# Stage 54 External Tool Handoff Templates Design

## Objective

Add first-class external tool handoff templates for future user-controlled
community/social tools while preserving Fashion Radar's local sanitized
CSV/JSON import boundary.

## Background

Fashion Radar already has the runtime primitives external producers need:

- `community-signal-profile` prints the field-level producer contract.
- `community-handoff-manifest` prints a directory manifest and workflow.
- `community-handoff-workflow` prints the local lint, preview, dry-run import,
  import, and review sequence.
- The importer, linter, candidate preview, and retained-row review commands work
  on local files only.

The missing piece is a clearer template package for external tools the user may
bring later. Those tools should have importable example CSV/JSON files they can
copy, inspect, and validate without changing Fashion Radar's schema or adding a
platform connector.

## Technical Stack

- Existing Python 3.11+ codebase.
- Existing strict `schemas/community-signals.schema.json`.
- Existing community signal profile and manifest builders.
- Existing pytest, Typer CLI tests, package archive checks, and docs drift
  tests.
- No new runtime or development dependencies.

## Scope

Stage 54 will add:

- `examples/community-tool-handoff.example.csv`
- `examples/community-tool-handoff.example.json`
- Profile/manifest discoverability by adding those paths to
  `COMMUNITY_SIGNAL_EXAMPLE_PATHS` and regenerating
  `examples/community-signal-profile.example.json`.
- Lint, dry-run, schema-field, profile, manifest, CLI JSON, docs, and package
  archive tests.
- README, community import docs, source boundaries, architecture, upload
  checklist, AGENTS, and changelog wording that describes the external tool
  handoff template.

## Behavior

No new command will be added.

The templates are static, sanitized, synthetic examples. They use only the
existing allowed community signal fields:

- `url`
- `title`
- `published_at`
- `summary`
- `source_name`
- `platform`
- `source_weight`
- `collected_at`

The JSON template will use the existing accepted envelope:

```json
{
  "items": [
    {
      "url": "https://example.com/community-tool/observed-bag",
      "title": "Observed bag signal",
      "published_at": "2026-06-12T10:00:00Z"
    }
  ]
}
```

It will not add top-level metadata, contract version, tool-specific fields, raw
source fields, account fields, media URLs, cookies, sessions, or tokens.

## Boundaries

Stage 54 does not add:

- scraping or crawling;
- browser automation;
- account login or account automation;
- cookies, sessions, tokens, or stored platform credentials;
- platform API clients;
- source acquisition;
- monitoring, watching, or scheduling;
- media download;
- platform/community coverage verification;
- demand proof;
- source ranking;
- compliance review, legal review, approval UI, or policy workflow;
- a new CLI command.

The external producer remains outside Fashion Radar. Fashion Radar only
documents and validates the local file contract.

## Implementation Plan

1. Add the new CSV/JSON templates under `examples/`.
2. Add the template paths to `COMMUNITY_SIGNAL_EXAMPLE_PATHS` and regenerate the
   checked-in producer profile example JSON.
3. Update tests that freeze profile and manifest `example_paths`.
4. Add lint/import/schema guardrail tests for all importable community handoff
   examples.
5. Add package archive requirements and package archive tests for the new
   templates.
6. Update docs and docs drift tests.
7. Run targeted tests, full verification, local opencode release review for
   this node, commit, upload, and GitHub Actions confirmation.

## Testing Strategy

Targeted tests:

```bash
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_lint.py tests/test_community_signal_import_contract.py -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_cli.py::test_community_signal_profile_prints_json tests/test_cli.py::test_community_handoff_manifest_command_prints_json_with_stable_keys -q
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py tests/test_cli_docs.py -q
```

Release verification follows the existing hardened workflow: full pytest, Ruff,
format check, lock checks, mirror sync check, release hygiene, source first-run
smoke, package archive check, installed-wheel smoke, local opencode release
review for this node, commit, GitHub upload, and Actions confirmation.
