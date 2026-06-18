# Stage 87 Roadmap Boundary Test Scope Design

## Goal

Tighten the external tool import roadmap docs drift test so boundary phrases are
required inside the `## External Tool Import Roadmap` section itself, not merely
somewhere in `docs/community-signal-import.md`.

## Scope

Modify:

- `tests/test_cli_docs.py`
- Stage 87 spec/plan/review artifacts

Do not modify:

- docs content
- `src/`
- schemas
- community signal lint/import behavior
- external adapter/template/workflow/readiness behavior
- dependency manifests or `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

## Design

The existing test already extracts the roadmap section into `roadmap` and checks
table/phase terms there. It also computes a normalized full-document string and
checks no-upstream/no-platform boundary terms against the full document.

Replace that full-document boundary check with `normalized_roadmap =
_normalized_text(roadmap).casefold()` and assert the same boundary terms against
`normalized_roadmap`.

## Tests

Run the narrowed test and full docs test module:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_import_docs_have_external_tool_import_roadmap -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

The focused test should pass without docs changes because the roadmap section
already contains the required boundary phrases.

## Boundaries

This stage is test-only. It does not add new platform collection, scraping,
connectors, browser automation, platform APIs, account/session/cookie/token
behavior, media downloads, monitoring, scheduling, source acquisition, demand
proof, ranking, coverage verification, schema enums, new linter restrictions,
or compliance-review product features.
