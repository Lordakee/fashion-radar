# Claude Code Stage 44 Plan Rereview Prompt

You are rereviewing the Stage 44 README quickstart path smoke plan after fixes
to the first plan review blockers.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan rereview only; do not edit files.
- Treat Critical and Important findings as blockers.

## Previous Findings

The first review found:

- Critical: the RED smoke test could execute current bare README `init`/`doctor`
  commands against platform default paths.
- Important: the spec/plan wording incorrectly implied `migrate-db` uses
  `$PWD/configs` and `$PWD/reports`, even though it only accepts `--data-dir`.
- Important: the commit task repeated a Claude Code co-author trailer concern
  without the Stage 43 context that Claude Code is a read-only reviewer and Codex
  performs the commit.
- Minor: design/plan output assertions and import instructions needed cleanup.

## Fixes Applied

- The RED phase now runs only the static guard. The plan explicitly says not to
  run the smoke test during RED because current README setup commands are unsafe
  platform-default invocations.
- `_quickstart_cli_args()` now asserts expected `$PWD` path flags before invoking
  any parsed README command.
- The spec, plan, and review prompt now say “applicable repo-local path flags”:
  `init` and `doctor` use `$PWD/configs`, `$PWD/data`, and `$PWD/reports`;
  `migrate-db` uses `$PWD/data`.
- The smoke test now asserts `doctor` output reports the temporary
  config/data/report directories.
- The plan now says to leave the existing `from fashion_radar.cli import app`
  import unchanged.
- Task 4 states that Claude Code is a read-only reviewer and Codex performs the
  commit, so no Claude Code co-author trailer should be added unless user or repo
  instructions explicitly require one.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-44-readme-quickstart-path-smoke-design.md`
- `docs/superpowers/plans/2026-06-15-stage-44-readme-quickstart-path-smoke-plan.md`
- `docs/reviews/claude-code-stage-44-plan-review.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 44 README QUICKSTART PATH SMOKE
```
