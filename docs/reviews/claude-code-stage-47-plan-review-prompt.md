# Claude Code Stage 47 Plan Review Prompt

You are reviewing the Stage 47 first-run sample smoke plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Make the GitHub first-run experience deterministic and testable: a new user
should be able to clone the repository, run a local-only sample workflow from
checked-in examples, generate a report, and inspect candidate/trend outputs
without live collection or external platform access.

## Proposed Technical Approach

- Add `scripts/check_first_run_smoke.py`, a dependency-free standard-library
  script that creates a temporary runtime workspace and runs
  `python -m fashion_radar` local commands.
- Use deterministic `AS_OF="2026-06-13T12:00:00Z"` and
  `examples/community-signals.example.csv`.
- Run `init`, `migrate-db`, `doctor`, community lint/candidate preview,
  import dry-run, import, imported summary/signals, `match`, `report`,
  `candidates`, and `trends`.
- Assert generated SQLite and report artifacts exist and JSON-producing
  commands parse as JSON.
- Add a temp directory handoff smoke by copying the checked-in CSV example into
  a temp `exports/` directory.
- Wire the smoke script into CI and `docs/github-upload-checklist.md`.
- Update README and `docs/community-signal-import.md` so the first-run path uses
  checked-in examples and does not rely on nonexistent `./signals.csv`,
  `./community-signals.csv`, or unexplained `./exports`.
- Add pytest guards for the smoke script and docs/CI drift.
- Preserve current boundaries: no live `collect`, RSS/GDELT fetches, scraping,
  crawling, browser automation, login/cookie/session tooling, platform
  connectors, external services, product compliance-review functionality,
  dependency changes, lockfile changes, scoring changes, schema changes, or
  committed generated runtime artifacts.

## Files To Review

- `docs/superpowers/specs/2026-06-15-stage-47-first-run-sample-smoke-design.md`
- `docs/superpowers/plans/2026-06-15-stage-47-first-run-sample-smoke-plan.md`
- `docs/reviews/claude-code-stage-47-plan-review-prompt.md`
- Current context files likely affected by the plan:
  - `README.md`
  - `docs/community-signal-import.md`
  - `docs/github-upload-checklist.md`
  - `.github/workflows/ci.yml`
  - `tests/test_cli_docs.py`
  - `src/fashion_radar/cli.py`
  - `examples/community-signals.example.csv`

## Specific Questions

1. Is Stage 47 the right next node after release hygiene/package readiness?
2. Is the first-run smoke workflow useful and deterministic for a GitHub user?
3. Are the planned commands safe and fully local/offline?
4. Are the assertions strong enough without requiring non-empty candidate/trend
   business results that the current examples may not guarantee?
5. Is the TDD sequence credible?
6. Does the plan avoid scraping/crawling/platform automation, account/cookie/
   session tooling, product compliance-review functionality, dependency
   changes, and committed generated artifacts?
7. Are there any Critical or Important issues that must be fixed before
   implementation?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 47 FIRST RUN SAMPLE SMOKE
```
