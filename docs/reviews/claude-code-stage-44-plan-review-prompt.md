# Claude Code Stage 44 Plan Review Prompt

You are reviewing the Stage 44 README quickstart path smoke plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Make the README quickstart use one consistent repo-local workspace from setup
through report generation, and add a guard so setup commands cannot drift back
to platform default paths.

## Proposed Technical Approach

- Update README quickstart setup commands so `init`, `migrate-db`, and `doctor`
  use applicable repo-local path flags. `init` and `doctor` should use
  `$PWD/configs`, `$PWD/data`, and `$PWD/reports`; `migrate-db` should use
  `$PWD/data`.
- Put `doctor` after `migrate-db` so it verifies the repo-local database that was
  just initialized.
- Extend `tests/test_cli_docs.py`, reusing its existing Markdown bash parsing
  helpers and README constant.
- Add a static README quickstart guard for repo-local setup path flags.
- Add a no-network `CliRunner` smoke test that parses the README setup commands,
  substitutes `$PWD` with a temporary directory, runs `init`, `migrate-db`, and
  `doctor`, and asserts the generated config/database artifacts live under that
  temporary repo-local workspace. The smoke helper must reject commands missing
  `$PWD` path flags before invoking anything, so RED does not mutate platform
  default directories.
- Add `.gitignore` entries only for generated `configs/sources.yaml`,
  `configs/entities.yaml`, and `configs/scoring.yaml`, preserving tracked
  `*.example.yaml` templates.
- Keep the node out of runtime behavior, source acquisition, scraping/crawling,
  platform automation, schedulers, watchers, monitors, external services,
  package metadata, lockfiles, CI workflow behavior, dashboards, and database
  schema changes.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-44-readme-quickstart-path-smoke-design.md`
- `docs/superpowers/plans/2026-06-15-stage-44-readme-quickstart-path-smoke-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 44 README QUICKSTART PATH SMOKE
```
