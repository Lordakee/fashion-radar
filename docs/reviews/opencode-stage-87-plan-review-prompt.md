# Stage 87 Plan Review Prompt

Review the Stage 87 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-87-roadmap-boundary-test-scope-design.md`
- `docs/superpowers/plans/2026-06-18-stage-87-roadmap-boundary-test-scope-plan.md`
- Current `tests/test_cli_docs.py`
- Current `docs/community-signal-import.md`

## Intended Goal

Tighten `test_community_signal_import_docs_have_external_tool_import_roadmap`
so no-upstream/no-platform boundary terms are asserted inside the extracted
`## External Tool Import Roadmap` section, not against the whole import doc.

## Scope Constraints

Allowed changes:

- one focused test-only change in `tests/test_cli_docs.py`
- Stage 87 review artifacts

Disallowed changes:

- docs content
- `src/`
- schemas
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

1. Does the plan correctly narrow the boundary assertions to the roadmap
   section?
2. Does the current roadmap section already contain the required phrases, so
   docs content can remain unchanged?
3. Is this safely test-only without runtime behavior implications?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
