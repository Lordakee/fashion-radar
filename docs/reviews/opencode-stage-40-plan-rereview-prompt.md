# Opencode Stage 40 Plan Rereview Prompt

You are rereviewing the Stage 40 opencode review workflow documentation plan
for the `fashion-radar` repository after the first opencode plan review found
verification-hardening issues.

Required review mode:

- Think carefully.
- This is a plan rereview only; do not edit files.
- Treat Critical and Important findings as blockers.
- The review model must be GLM 5.2 via local opencode.

## Fixes Applied Since First Review

- Removed the Markdown `ruff format --check` command because ruff does not
  meaningfully lint Markdown prose.
- Added history guards so Stage 40 fails if it modifies historical
  `docs/reviews/claude-code-*` files or unrelated historical plan files.
- Corrected `opencode run` command examples so the prompt argument appears
  before repeated `--file` attachments, matching the local opencode CLI syntax
  verified during this node.
- Added a pre-flight cleanliness check.
- Clarified that this documentation-only stage uses documentation checks and
  release verification, not Python tests as the primary behavior proof.

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
