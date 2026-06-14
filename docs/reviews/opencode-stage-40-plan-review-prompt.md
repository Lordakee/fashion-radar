# Opencode Stage 40 Plan Review Prompt

You are reviewing the Stage 40 opencode review workflow documentation plan for
the `fashion-radar` repository.

Required review mode:

- Think carefully.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.
- The review model must be GLM 5.2 via local opencode.

## Goal

Update the active repository review workflow docs so future audit gates use
local `opencode` with the GLM 5.2 model.

## Proposed Technical Approach

- Update `docs/REVIEW_PROTOCOL.md` to replace active Claude Code review gates
  with local opencode review gates.
- Use this local model ID in examples:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "review prompt..."
```

- Update `docs/github-upload-checklist.md` final review language to require
  local opencode with GLM 5.2 before upload.
- Keep historical Claude Code records and old staged plans untouched.
- Keep the change documentation-only.
- Do not change product code, tests, dependencies, lockfiles, CI, database
  schema, commands, scraping/crawling/platform automation, source acquisition,
  schedulers, watchers, or monitors.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md`
- `docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW
```
