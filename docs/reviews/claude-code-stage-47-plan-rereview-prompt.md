# Claude Code Stage 47 Plan Rereview Prompt

Plan rereview only. Do not edit files. Review only the text below and the
listed revised plan/spec files if needed. Use maximum effort.

## Previous Important Findings

1. Runtime isolation was underspecified and could touch repo/user state.
2. Exact command arguments were not specified enough for deterministic output.
3. `doctor` was included without proving it is local/offline in this mode.
4. Temp `exports/` directory contract was ambiguous.

## Revisions Made

- The spec now requires every command to run with `cwd=repo_root`,
  `PYTHONPATH` prepending `repo_root/src`, and explicit temp path flags whenever
  supported.
- The spec/plan require fixed `AS_OF="2026-06-13T12:00:00Z"` and
  `SOURCE_NAME="Community Tool Export"` on all relevant commands.
- The spec requires asserting no generated default-path runtime artifacts land
  under repo `data/` or `reports/`.
- The spec records that `doctor` is local-only for this mode: local paths,
  config loading, and SQLite schema status for supplied `--data-dir`; no URL
  fetching, live service checks, account validation, or external credentials.
- The temp exports contract is explicit: create exactly
  `$tmp/exports/community-signals.csv` by copying the checked-in CSV before
  directory commands; `community-handoff-workflow` is print-only and does not
  create files.

## Files

- `docs/superpowers/specs/2026-06-15-stage-47-first-run-sample-smoke-design.md`
- `docs/superpowers/plans/2026-06-15-stage-47-first-run-sample-smoke-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If the revised plan is acceptable, include exactly:

```text
APPROVED FOR STAGE 47 FIRST RUN SAMPLE SMOKE
```
