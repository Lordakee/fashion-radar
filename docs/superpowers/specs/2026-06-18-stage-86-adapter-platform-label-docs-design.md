# Stage 86 Adapter Platform Label Docs Design

## Goal

Clarify the `Platform label` column in the README and CLI reference adapter
registry tables as advisory `suggested_platform_labels` guidance for the
optional handoff `platform` field.

## Scope

Modify:

- `README.md`
- `docs/cli-reference.md`
- `tests/test_cli_docs.py`
- Stage 86 spec/plan/review artifacts

Do not modify:

- `src/`
- `schemas/`
- community signal lint/import behavior
- external adapter/template/workflow/readiness behavior
- dependency manifests or `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

## Design

Add one short explanatory paragraph immediately after the existing
Display/source name note beneath each `Known adapter ids:` table.

The paragraph must state that the `Platform label` column reflects
`suggested_platform_labels` as advisory local provenance label guidance for the
optional handoff `platform` field. It must also state that these labels are not
a schema enum, not a linter restriction, not platform coverage, and not demand
proof.

Keep the existing table header and row values unchanged.

## Tests

Add one focused docs drift test in `tests/test_cli_docs.py` near
`test_external_tool_adapter_registry_docs_are_linked_and_bounded`.

The test should inspect the README `## What It Does Not Do` section and the CLI
reference `## Local Import And Community Handoff` section. It should require:

- `Known adapter ids:`
- `Platform label column`
- `suggested_platform_labels`
- `advisory local provenance label guidance`
- `optional handoff \`platform\` field`
- `not a schema enum`
- `not a linter restriction`
- `not platform coverage`
- `not demand proof`

## Boundaries

This stage is docs/test-only. It does not add new platform collection, scraping,
connectors, browser automation, platform APIs, account/session/cookie/token
behavior, media downloads, monitoring, scheduling, source acquisition, demand
proof, ranking, coverage verification, schema enums, new linter restrictions,
or compliance-review product features.
