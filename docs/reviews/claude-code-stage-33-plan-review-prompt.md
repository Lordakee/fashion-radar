# Claude Code Stage 33 Plan Review Prompt

You are reviewing the Stage 33 CI fresh runner sync fix plan for the
`fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a plan review only; do not edit files.
- Treat Critical and Important findings as blockers.

## Goal

Fix the GitHub Actions CI failure on commit
`ad2116df6763cb1b2bab3e7e1c34d9c046c6bac0` without changing runtime code or
dependencies.

## Root Cause Evidence

GitHub Actions run `27481885536` failed in job `81230982347`, step
`Public lockfile check`.

The job log shows:

```text
UV_NO_CONFIG=1 uv sync --locked --dev --check
Would create project environment at: .venv
The environment is outdated; run `uv sync` to update the environment
Process completed with exit code 1.
```

Local Stage 32 verification passed because the local repository already had a
synchronized `.venv`; the GitHub runner is fresh and has no `.venv`.

## Proposed Technical Approach

- Keep pre-install public lockfile validation as
  `UV_NO_CONFIG=1 uv lock --check`.
- Keep the pre-install mirror-marker scan of `uv.lock`.
- Move `UV_NO_CONFIG=1 uv sync --locked --dev --check` to after
  `UV_NO_CONFIG=1 uv sync --locked --dev` in the install step.
- Update contributor, PR, agent, mirror, and upload checklist docs so fresh
  environments run locked sync before the optional sync check.
- Do not edit `uv.lock`, dependencies, runtime code, source connectors,
  scraping/crawling/platform automation, watchers, schedulers, source
  acquisition, source ranking, demand proof, platform coverage verification, or
  social-platform functionality.
- After push, query the GitHub Actions result for the new commit and debug
  again if it still fails.

## Files To Review

- `docs/superpowers/specs/2026-06-14-stage-33-ci-fresh-runner-sync-design.md`
- `docs/superpowers/plans/2026-06-14-stage-33-ci-fresh-runner-sync-plan.md`

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the plan is acceptable to execute, include this exact phrase:

```text
APPROVED FOR STAGE 33 CI FRESH RUNNER FIX
```
