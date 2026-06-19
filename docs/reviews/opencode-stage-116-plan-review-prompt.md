# Stage 116 Plan Review Prompt

Review the Stage 116 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-19-stage-116-directory-readiness-samples-design.md`
- `docs/superpowers/plans/2026-06-19-stage-116-directory-readiness-samples-plan.md`
- Current `tests/test_community_tool_handoff_directory_examples.py`
- Current `tests/test_cli_docs.py`
- Current `examples/community-tool-handoff-directory.example/README.md`
- Current `docs/community-signal-import.md`
- Current `src/fashion_radar/external_tool_readiness.py`
- Current `src/fashion_radar/external_tool_workflow.py`

## Intended Goal

Connect the checked-in external community tool directory examples to the
existing `external-tool-readiness` and `external-tool-workflow` local preflight
guidance for both CSV and JSON directories. This should prepare for future
user-controlled community/social exports by documenting and testing how the
existing generic adapter accepts directory, format, pattern, and source-name
overrides.

## Scope Constraints

Allowed changes:

- `tests/test_community_tool_handoff_directory_examples.py`
- `tests/test_cli_docs.py`
- `examples/community-tool-handoff-directory.example/README.md`
- `docs/community-signal-import.md`
- Stage 116 review artifacts

Disallowed changes:

- `src/`
- schemas
- dependency manifests or `uv.lock`
- CI workflows
- collectors
- source packs
- entity packs
- dashboard
- import behavior
- scoring
- reports

Do not propose adding source collection, collectors, manual import behavior,
external tool runtime behavior, connectors, source acquisition, platform
coverage, demand proof, ranking, scraping, browser automation, platform APIs,
account/cookie handling, scheduling, monitoring, schema changes, dependency
changes, CI changes, new linter restrictions, or compliance-review product
features.

## Review Questions

1. Does the plan correctly rely on existing readiness/workflow override support
   rather than changing runtime code?
2. Do the proposed tests cover both CSV and JSON checked-in directory examples,
   including the JSON override on `generic_community_export`?
3. Do the docs assertions guard concrete, copyable readiness/workflow snippets
   without becoming brittle for unrelated documentation?
4. Are the focused, adjacent, and full release verification commands
   sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
