Review the Stage 30 plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Objective:

Add `fashion-radar community-handoff-workflow DIRECTORY`, a local print-only
command that emits a copyable command checklist for the community signal
directory handoff path:

1. `community-signal-lint-dir`
2. `community-candidates-dir`
3. `import-signals-dir --dry-run`
4. `import-signals-dir`
5. `imported-review-workflow`

Design and plan to review:

- `docs/superpowers/specs/2026-06-13-stage-30-community-handoff-workflow-design.md`
- `docs/superpowers/plans/2026-06-13-stage-30-community-handoff-workflow-plan.md`

Technology and approach:

- Python 3.11.
- Typer CLI.
- Pydantic v2 models with `extra="forbid"`.
- `shlex.join` for copyable command generation.
- pytest and ruff.
- Existing `imported_review_workflow` pattern.
- No new dependencies.

Hard boundaries:

- The workflow command itself must be print-only.
- It must not execute generated commands.
- It must not read the supplied directory.
- It must not validate files.
- It must not import rows.
- It must not open or write SQLite.
- It must not fetch URLs, log in, download media, run browser automation,
  scrape platforms, monitor platforms, watch folders, schedule work, add source
  or platform connectors, prove demand, verify platform coverage, rank sources,
  write reports, update dashboards, generate config files, or generate entity
  files.
- It may intentionally print supplied directory/config/data paths inside
  copyable local commands; this path echo must be documented as different from
  aggregate candidate preview output.
- `uv.lock` must remain excluded.

Please review for:

1. Scope correctness and whether the command name/options are coherent.
2. Whether the planned output model and generated steps are stable and
   sufficient.
3. Whether planned tests prove print-only behavior, no directory read, no
   SQLite/report/dashboard/config/entity artifacts, no subprocess execution,
   shell quoting, stable JSON keys, and intentional path echo.
4. Whether docs updates avoid implying source acquisition, scraping, monitoring,
   scheduling, platform coverage, or demand proof.
5. Whether the plan is implementable without ambiguous placeholders.
6. Whether any Critical or Important issue should block implementation.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block implementation.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 30 IMPLEMENTATION`.
