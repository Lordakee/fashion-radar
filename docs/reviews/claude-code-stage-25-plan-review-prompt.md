# Claude Code Stage 25 Plan Review Prompt

You are reviewing the Fashion Radar Stage 25 plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Read these files:

- `docs/superpowers/specs/2026-06-13-stage-25-imported-candidates-design.md`
- `docs/superpowers/plans/2026-06-13-stage-25-imported-candidates-plan.md`
- Relevant existing candidate discovery code in
  `src/fashion_radar/discovery/candidates.py`
- Relevant existing CLI patterns in `src/fashion_radar/cli.py`
- Relevant imported review helpers in `src/fashion_radar/imported_signals.py`
- Relevant tests if needed

Stage 25 goal:

Add `fashion-radar imported-candidates`, a local read-only command that surfaces
candidate phrases from retained `manual_import` rows only.

Proposed solution:

- Add optional `source_type` and `source_name` filters to
  `discover_candidates()`, defaulting to no filtering so current reports,
  trends, dashboard, and `candidates` command behavior remains unchanged.
- Add `src/fashion_radar/imported_candidates.py` as a small wrapper that opens
  existing SQLite read-only, verifies existing imported-review schema, calls
  filtered candidate discovery with `source_type=manual_import`, and renders
  stable table/JSON output.
- Add a thin Typer command in `src/fashion_radar/cli.py`.
- Add focused tests and local-only docs.

Tech stack:

- Python 3.11+
- Typer
- Pydantic v2
- SQLAlchemy Core
- pytest
- ruff
- uv

Implementation method:

- TDD only: write failing tests first, verify RED, implement minimal code, then
  verify GREEN.
- No new dependencies.
- Use mirrors for install/build commands where practical.
- Do not commit the current unrelated `uv.lock` mirror-url diff.
- Submit implemented code to Claude Code code review before commit/push.

Important scope boundary:

- The feature must only read existing local SQLite state.
- It must not write SQLite, initialize schema, migrate, write reports, write
  dashboard state, run matching, change scoring algorithms, create persistent
  candidate tables, schedule jobs, monitor folders, call platform APIs,
  scrape/crawl, automate accounts, or acquire source files.
- It must not imply verified entities, market-wide demand, platform coverage,
  source quality, source ranking, source coverage, authorization workflows,
  audit workflows, policy workflows, or compliance workflows.

Please review the plan/spec in read-only mode and classify findings as:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: can fix during implementation.

Focus on:

- Whether default candidate discovery behavior is preserved.
- Whether imported-only filtering is scoped correctly.
- Whether the output model avoids leaking internal candidate contexts, match
  internals, import paths, account/private fields, or raw comments.
- Whether missing database and invalid input paths avoid creating artifacts.
- Whether the plan protects read-only SQLite behavior.
- Whether the tests are sufficient for broad-call-site regressions.
- Whether docs wording stays within local-only boundaries.
- Whether the release checks are concrete and mirror-safe without committing
  mirror URLs to `uv.lock`.

Return either:

1. `APPROVED FOR IMPLEMENTATION` if there are no Critical or Important issues,
   followed by any Minor notes; or
2. A findings list with severity, file/section, issue, and concrete fix.

Do not edit files.
