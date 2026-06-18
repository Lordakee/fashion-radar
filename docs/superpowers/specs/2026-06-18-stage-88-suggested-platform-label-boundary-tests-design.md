# Stage 88 Suggested Platform Label Boundary Tests Design

## Goal

Harden tests around `suggested_platform_labels` so the advisory label list stays
producer/profile metadata only, not importable row data, not a schema property,
and not a JSON Schema enum or const for the optional `platform` field.

## Scope

Modify:

- `tests/test_community_signal_profile.py`
- `tests/test_external_tool_contract_parity.py`
- `tests/test_cli_docs.py`
- Stage 88 spec/plan/review artifacts

Do not modify:

- `src/`
- `schemas/`
- docs content
- community signal lint/import behavior
- external adapter/template/workflow/readiness behavior
- dependency manifests or `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

## Design

Add test-only assertions that:

- `suggested_platform_labels` is absent from required, optional, allowed,
  prohibited, CSV, and schema row fields.
- The schema `platform` field remains a string and does not gain `enum` or
  `const`.
- External tool template JSON items and CSV headers do not emit
  `suggested_platform_labels`.
- The community import Optional Fields docs continue to say the optional
  `platform` field is not platform coverage, source acquisition, demand proof,
  or complete platform/community visibility, and that
  `suggested_platform_labels` are advisory metadata only and do not make
  `platform` required.

Use structured CSV parsing for the template CSV header check.

## Tests

Focused tests:

```bash
uv --no-config run --frozen pytest \
  tests/test_community_signal_profile.py::test_profile_contract_matches_schema_csv_header_and_constants \
  tests/test_external_tool_contract_parity.py::test_every_template_json_and_csv_output_lints_cleanly \
  tests/test_cli_docs.py::test_community_signal_import_platform_field_keeps_suggested_labels_advisory \
  -q
```

Relevant module tests:

```bash
uv --no-config run --frozen pytest \
  tests/test_community_signal_profile.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli_docs.py \
  -q
```

## Boundaries

This stage is test-only. It does not add new platform collection, scraping,
connectors, browser automation, platform APIs, account/session/cookie/token
behavior, media downloads, monitoring, scheduling, source acquisition, demand
proof, ranking, coverage verification, schema enums, new linter restrictions,
or compliance-review product features.
