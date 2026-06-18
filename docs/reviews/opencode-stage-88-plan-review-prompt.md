# Stage 88 Plan Review Prompt

Review the Stage 88 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-88-suggested-platform-label-boundary-tests-design.md`
- `docs/superpowers/plans/2026-06-18-stage-88-suggested-platform-label-boundary-tests-plan.md`
- Current `tests/test_community_signal_profile.py`
- Current `tests/test_external_tool_contract_parity.py`
- Current `tests/test_cli_docs.py`
- Current `schemas/community-signals.schema.json`
- Current `docs/community-signal-import.md`

## Intended Goal

Add test-only assertions proving `suggested_platform_labels` remains advisory
producer/profile metadata, not required/optional/prohibited row data, not a
schema property, not a JSON Schema enum/const for `platform`, and not emitted
in external tool template JSON/CSV handoff rows.

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

## Review Questions

1. Does the plan keep the stage test-only and avoid behavior/schema/docs
   changes?
2. Are the schema/profile/template/docs assertions technically correct for the
   current codebase?
3. Do the assertions avoid over-constraining the advisory label list to exact
   adapter equality?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
