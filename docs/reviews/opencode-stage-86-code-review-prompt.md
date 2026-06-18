# Stage 86 Code Review Prompt

Review the Stage 86 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 86 clarifies the adapter registry table `Platform label` column in
README and CLI reference. It describes the column as
`suggested_platform_labels` advisory local provenance label guidance for the
optional handoff `platform` field and explicitly says these labels are not a
schema enum, not a linter restriction, not platform coverage, and not demand
proof.

## Files To Review

- `README.md`
- `docs/cli-reference.md`
- `tests/test_cli_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-86-adapter-platform-label-docs-design.md`
- `docs/superpowers/plans/2026-06-18-stage-86-adapter-platform-label-docs-plan.md`
- `docs/reviews/opencode-stage-86-plan-review-prompt.md`
- `docs/reviews/opencode-stage-86-plan-review.md`

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

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_platform_label_docs_are_advisory -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

## Review Questions

1. Does the implementation match the Stage 86 plan and scope?
2. Does the wording preserve the advisory-only meaning of
   `suggested_platform_labels`?
3. Is the docs drift test scoped tightly enough and unlikely to pass from
   unrelated text?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
