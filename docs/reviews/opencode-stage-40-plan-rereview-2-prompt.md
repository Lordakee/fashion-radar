# Opencode Stage 40 Plan Rereview 2 Prompt

You are rereviewing the Stage 40 opencode review workflow documentation plan
after the previous rereview withheld approval for five Important blockers.

Required review mode:

- Think carefully.
- This is a plan rereview only; do not edit files.
- Treat Critical and Important findings as blockers.
- The review model must be GLM 5.2 via local opencode.

## Fixes Applied Since Previous Rereview

- Converted the active Claude Code phrase check into a failing guard.
- Extended Task 1 to update the Review Record Naming section to
  `opencode-stage-N-*` for new records while preserving old Claude Code records
  as historical legacy artifacts.
- Enumerated every active `docs/REVIEW_PROTOCOL.md` section that must change:
  Before Coding, During Development, Before GitHub Upload, and Review Record
  Naming.
- Added `AGENTS.md` to scope so active project instructions also use local
  opencode with GLM 5.2.
- Added plan rereview prompt/result artifacts to the in-scope file manifest.
- Changed history guards to use `git diff HEAD --name-only`.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-40-opencode-review-workflow-design.md`
- `docs/superpowers/plans/2026-06-14-stage-40-opencode-review-workflow-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the revised plan is acceptable to execute, include this exact
phrase:

```text
APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW
```
