# Stage 88 Code Review Prompt

Review the Stage 88 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 88 adds test-only assertions proving `suggested_platform_labels` remains
advisory producer/profile metadata. The tests now assert it is not a row field,
not a schema property, not a JSON Schema enum/const for `platform`, not emitted
in external tool template JSON/CSV rows, and still described as advisory for the
optional handoff `platform` field.

## Files To Review

- `tests/test_community_signal_profile.py`
- `tests/test_external_tool_contract_parity.py`
- `tests/test_cli_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-88-suggested-platform-label-boundary-tests-design.md`
- `docs/superpowers/plans/2026-06-18-stage-88-suggested-platform-label-boundary-tests-plan.md`
- `docs/reviews/opencode-stage-88-plan-review-prompt.md`
- `docs/reviews/opencode-stage-88-plan-review.md`

## Scope Constraints

Allowed changes:

- focused tests in `tests/test_community_signal_profile.py`
- focused tests in `tests/test_external_tool_contract_parity.py`
- focused docs test in `tests/test_cli_docs.py`
- Stage 88 review artifacts

Disallowed changes:

- `src/`
- schemas
- docs content
- lint/import behavior
- adapter/template/workflow/readiness behavior
- dependency manifests or `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

Do not propose adding scraping, connectors, browser automation, platform APIs,
login/cookie/session/token behavior, media downloads, monitoring, scheduling,
source acquisition, demand proof, ranking, coverage verification, schema enums,
new linter restrictions, or compliance-review product features.

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_community_signal_profile.py::test_profile_contract_matches_schema_csv_header_and_constants tests/test_external_tool_contract_parity.py::test_every_template_json_and_csv_output_lints_cleanly tests/test_cli_docs.py::test_community_signal_import_platform_field_keeps_suggested_labels_advisory -q
uv --no-config run --frozen pytest tests/test_community_signal_profile.py tests/test_external_tool_contract_parity.py tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_community_signal_profile.py tests/test_external_tool_contract_parity.py tests/test_cli_docs.py
```

## Review Questions

1. Does the implementation match the Stage 88 plan and scope?
2. Are the new assertions correct for existing schema/profile/template/docs
   behavior?
3. Do the assertions avoid over-constraining future advisory label additions?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
