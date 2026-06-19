# Stage 117 Plan Review Prompt

Review the Stage 117 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-19-stage-117-discoverability-links-design.md`
- `docs/superpowers/plans/2026-06-19-stage-117-discoverability-links-plan.md`
- Current `README.md`
- Current `docs/cli-reference.md`
- Current `docs/first-run.md`
- Current `docs/github-upload-checklist.md`
- Current `tests/test_cli_docs.py`
- Current `docs/community-signal-import.md`
- Current `examples/community-tool-handoff-directory.example/README.md`

## Intended Goal

Add lightweight discoverability pointers in the summary docs so users can find
the already-pinned checked-in directory preflight examples from Stage 116.
This should keep the exact command blocks in the existing Stage 116 docs and add
only summary-level links/pointers in the docs that users are most likely to open
first.

## Scope Constraints

Allowed changes:

- `README.md`
- `docs/cli-reference.md`
- `docs/first-run.md`
- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`
- Stage 117 review artifacts

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

1. Does the plan keep Stage 117 to discoverability pointers rather than
   duplicating the Stage 116 command blocks?
2. Are the proposed docs sections the right high-visibility entry points?
3. Do the tests stay narrow and section-scoped instead of rechecking Stage 116
   command parsing?
4. Are the verification commands sufficient and aligned with project release
   checks?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
