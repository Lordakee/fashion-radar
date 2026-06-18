# Stage 78 Plan Review Prompt

You are reviewing the Stage 78 implementation plan for `fashion-radar`.

Repository: `/home/ubuntu/fashion-radar`

Use these files as the plan/spec under review:

- `docs/superpowers/specs/2026-06-18-stage-78-adapter-contract-parity-design.md`
- `docs/superpowers/plans/2026-06-18-stage-78-adapter-contract-parity-plan.md`

## Goal

Stage 78 should add a test/docs-only adapter contract parity gate. It should
prove external/community adapter metadata, template model metadata, workflow
commands, and readiness commands stay aligned with
`community-signal-profile` across every built-in adapter.

## Strict Boundaries

- Do not add scraping, crawling, browser automation, platform APIs, login,
  sessions, cookies, tokens, proxies, media downloads, monitoring, scheduling,
  source acquisition, demand proof, ranking, platform coverage verification, or
  compliance-review product features.
- The plan should not require runtime `src/` changes.
- The plan should not stage or modify public dependency manifests or `uv.lock`.
- The existing worktree has a pre-existing local `uv.lock` mirror rewrite. Treat
  it as out-of-scope and verify it is not staged.

## Review Questions

1. Does the plan use public builders and current model shapes correctly?
2. Are the proposed tests deterministic across machines?
3. Are the command parity maps correct for adapter, workflow, and readiness
   shared steps?
4. Does the banned generated-command token test risk false positives against
   legitimate command names or install hints?
5. Are docs/test changes enough to make the guarantee visible without
   over-constraining prose?
6. Are final verification, staging, and GitHub API publication steps safe with
   the dirty `uv.lock` worktree?

Report Critical, Important, and Minor findings with file/line references where
possible. If there are no Critical or Important findings, say so clearly.
