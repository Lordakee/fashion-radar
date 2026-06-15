# Claude Code Stage 42 Plan Rereview Prompt

You are rereviewing the Stage 42 CLI docs drift guards plan for the
`fashion-radar` repository after fixes to the first plan review.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan rereview only; do not edit files.
- Treat Critical and Important findings as blockers.

## Previous Blocking Findings

The first Stage 42 plan review in
`docs/reviews/claude-code-stage-42-plan-review.md` withheld approval because:

1. The planned public command helper used `sorted(click_app.commands)` without
   filtering hidden commands.
2. The design required cleanup `--data-dir` guards, but the planned test code
   did not include `clean-old-data`.

## Fixes Made

- Updated the Stage 42 spec and plan to filter commands with
  `if not getattr(command, "hidden", False)`.
- Added `clean-old-data` to the required path-flag map with `--data-dir`.
- Added `docs/data-retention.md` to the path-consistency docs list.
- Replaced the narrow command-name extraction with a regex that recognizes
  direct, `uv run`, and quoted/path-qualified `fashion-radar` invocations.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-42-cli-docs-drift-guards-design.md`
- `docs/superpowers/plans/2026-06-15-stage-42-cli-docs-drift-guards-plan.md`
- `docs/reviews/claude-code-stage-42-plan-review.md`

## Required Output

Respond with:

- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A concise verdict.

If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 42 CLI DOCS DRIFT GUARDS
```
