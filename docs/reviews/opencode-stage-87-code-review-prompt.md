# Stage 87 Code Review Prompt

Review the Stage 87 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Change Summary

Stage 87 narrows `test_community_signal_import_docs_have_external_tool_import_roadmap`
so the no-upstream/no-platform boundary terms are asserted against the extracted
`## External Tool Import Roadmap` section instead of the whole
`docs/community-signal-import.md` document.

## Files To Review

- `tests/test_cli_docs.py`
- `docs/superpowers/specs/2026-06-18-stage-87-roadmap-boundary-test-scope-design.md`
- `docs/superpowers/plans/2026-06-18-stage-87-roadmap-boundary-test-scope-plan.md`
- `docs/reviews/opencode-stage-87-plan-review-prompt.md`
- `docs/reviews/opencode-stage-87-plan-review.md`

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

## Verification Already Run

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_import_docs_have_external_tool_import_roadmap -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

## Review Questions

1. Does the implementation match the Stage 87 plan and scope?
2. Does it correctly require the boundary phrases inside the roadmap section?
3. Is there any risk that this weakens docs drift coverage?
4. Are there any Critical or Important issues that must be fixed before final
   verification, commit, and push?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
