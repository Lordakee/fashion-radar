# Stage 86 Plan Review Prompt

Review the Stage 86 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-86-adapter-platform-label-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-86-adapter-platform-label-docs-plan.md`
- Current `README.md`
- Current `docs/cli-reference.md`
- Current `tests/test_cli_docs.py`

## Intended Goal

Clarify the adapter registry table `Platform label` column in README and CLI
reference as advisory local provenance label guidance from
`suggested_platform_labels` for the optional handoff `platform` field.

## Scope Constraints

Allowed changes:

- README adapter registry prose
- CLI reference adapter registry prose
- focused docs drift test in `tests/test_cli_docs.py`
- Stage 86 review artifacts

Disallowed changes:

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

1. Does the plan clarify `Platform label` semantics without implying platform
   support, coverage, schema validation, or demand proof?
2. Are the README and CLI reference insertion points correct?
3. Is the proposed docs drift test scoped tightly enough to the adapter table
   sections?
4. Are the verification commands sufficient?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
