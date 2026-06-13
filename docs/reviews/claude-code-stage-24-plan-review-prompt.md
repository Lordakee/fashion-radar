# Claude Code Stage 24 Plan Review Prompt

You are reviewing the Fashion Radar Stage 24 plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Read these files:

- `docs/superpowers/specs/2026-06-13-stage-24-imported-review-workflow-design.md`
- `docs/superpowers/plans/2026-06-13-stage-24-imported-review-workflow-plan.md`
- Relevant existing command patterns in `src/fashion_radar/cli.py`
- Relevant existing imported command modules/tests if needed

Stage 24 goal:

Add `fashion-radar imported-review-workflow`, a local command that prints a
deterministic post-import review checklist for existing Fashion Radar commands.

Planned technical approach:

- Python 3.11+, Typer, Pydantic v2, `shlex`, pytest, ruff, uv.
- New pure module `src/fashion_radar/imported_review_workflow.py`.
- Thin Typer command in `src/fashion_radar/cli.py`.
- TDD implementation with builder tests, renderer tests, CLI tests, docs, and
  release verification.

Important scope boundary:

- The new command must only print suggested commands.
- It must not execute subprocesses or shell commands.
- It must not open SQLite, create directories, read configs, import rows, match
  rows, score entities, generate reports, schedule jobs, monitor folders, call
  platform APIs, crawl/scrape anything, or integrate externally.
- It must not add source acquisition, source ranking, source quality, coverage,
  approval, audit, policy, or compliance workflows.
- The printed `match` step may update stored local matches if the operator later
  copies and runs it, so the Stage 24 output must clearly distinguish
  `execution_mode: print_only` from each printed command's `suggested_effect`.

Please review the plan/spec in read-only mode and classify findings as:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: can fix during implementation.

Focus on:

- Whether the plan/spec fully enforce print-only behavior.
- Whether any step would accidentally read SQLite/configs, create artifacts, or
  execute commands.
- Whether JSON/table fields are stable and not misleading.
- Whether `shlex.join()` command rendering is sufficient and deterministic.
- Whether invalid CLI inputs avoid builder execution where appropriate.
- Whether docs wording avoids automation, source acquisition, external platform,
  ranking, coverage, source quality, audit, policy, or compliance claims.
- Whether the TDD steps are coherent and sufficient for this scope.

Return either:

1. `APPROVED FOR IMPLEMENTATION` if there are no Critical or Important issues,
   followed by any Minor notes; or
2. A findings list with severity, file/section, issue, and concrete fix.

Do not edit files.
