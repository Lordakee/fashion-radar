# Stage 79 Plan Review Prompt

You are reviewing the Stage 79 implementation plan for `fashion-radar`.

Repository: `/home/ubuntu/fashion-radar`

This is a read-only plan review. Do not edit files, stage changes, commit, or
run networked source-collection commands.

Use these files as the plan/spec under review:

- `docs/superpowers/specs/2026-06-18-stage-79-onboarding-roadmap-design.md`
- `docs/superpowers/plans/2026-06-18-stage-79-onboarding-roadmap-plan.md`

## Goal

Stage 79 should improve first-time GitHub onboarding docs with a README start
path, first-run chooser table, CLI beginner roadmap, and clearer optional
entity-pack sequence. It must be docs/test-only.

## Strict Boundaries

- No runtime CLI behavior changes.
- No new commands, flags, collectors, adapters, connectors, scraping, browser
  automation, platform APIs, login/session/cookie/token/proxy behavior, media
  downloads, monitoring, scheduling, source acquisition, demand proof, ranking,
  platform coverage verification, or compliance-review product features.
- Do not stage or modify public dependency manifests or `uv.lock`.
- The current worktree has a pre-existing local `uv.lock` mirror rewrite. Treat
  it as out-of-scope and verify it is not staged.
- Per the latest user instruction, this stage uses stage-local opencode review
  artifacts. Do not propose or require edits to `AGENTS.md`,
  `docs/REVIEW_PROTOCOL.md`, or `docs/github-upload-checklist.md` for Stage 79.

## Review Questions

1. Are the proposed docs tests satisfiable by the planned prose?
2. Do the docs additions improve orientation without duplicating too much command
   detail or changing product scope?
3. Are the section insertion points safe relative to existing docs tests?
4. Does the entity-pack wording keep packs optional and local-only?
5. Are final verification, staging, and GitHub API publication steps safe with
   the dirty out-of-stage `uv.lock`?

Report Critical, Important, and Minor findings with file/line references where
possible. If there are no Critical or Important findings, say so clearly.
