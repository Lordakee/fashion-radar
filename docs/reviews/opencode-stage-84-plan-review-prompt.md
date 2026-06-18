# Stage 84 Plan Review Prompt

Review the Stage 84 design and implementation plan in
`/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Files To Review

- `docs/superpowers/specs/2026-06-18-stage-84-readiness-installed-smoke-design.md`
- `docs/superpowers/plans/2026-06-18-stage-84-readiness-installed-smoke-plan.md`
- Current `docs/github-upload-checklist.md`
- Current `tests/test_cli_docs.py`
- Current `docs/cli-reference.md`

## Intended Goal

The upload checklist readiness docs already claim the CLI reference and
installed-wheel smoke include both:

- `fashion-radar external-tool-readiness --adapter instaloader --format table`
- `fashion-radar external-tool-readiness --adapter instaloader --format json`

The installed-wheel smoke block currently has only the JSON `instaloader`
command. Stage 84 should add the exact installed-path table smoke command and
tighten the docs drift test to assert both exact installed-path table and JSON
commands.

## Scope Constraints

This node must stay docs/test-only:

- Allowed: `docs/github-upload-checklist.md`, `tests/test_cli_docs.py`, and
  Stage 84 spec/plan/review artifacts.
- Disallowed: runtime code under `src/`, dependency manifests, `uv.lock`, CI,
  `AGENTS.md`, and `docs/REVIEW_PROTOCOL.md`.
- Do not propose adding scraping, connectors, browser automation, platform
  APIs, login/cookie/session/token behavior, media downloads, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage
  verification, or compliance-review product features.

## Review Questions

1. Does the plan close the documented smoke coverage gap without changing
   runtime behavior?
2. Is the insertion point in the upload checklist correct?
3. Does the proposed test pin both exact installed-path table and JSON
   readiness commands without weakening existing assertions?
4. Are the verification commands sufficient for a docs/test-only node?
5. Are there any Critical or Important blockers before implementation?

Return findings first, ordered by severity, with file/line references. If
there are no Critical or Important blockers, say that explicitly.
