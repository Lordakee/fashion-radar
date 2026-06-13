Review Stage 30 before implementation. Read only these files unless absolutely
needed:

- `docs/superpowers/specs/2026-06-13-stage-30-community-handoff-workflow-design.md`
- `docs/superpowers/plans/2026-06-13-stage-30-community-handoff-workflow-plan.md`

Stage 30 goal:

Add `fashion-radar community-handoff-workflow DIRECTORY`, a local print-only
command that prints copyable commands for this directory handoff path:

`community-signal-lint-dir -> community-candidates-dir -> import-signals-dir --dry-run -> import-signals-dir -> imported-review-workflow`

Tech stack:

Python 3.11, Typer, Pydantic v2, `shlex.join`, pytest, ruff. No new
dependencies.

Hard boundaries:

- The new workflow command itself must not execute commands, read the supplied
  directory, validate files, import rows, open/write SQLite, fetch URLs, log in,
  download media, run browser automation, scrape, monitor, watch folders,
  schedule work, add source/platform connectors, prove demand, verify platform
  coverage, rank sources, write reports, update dashboards, generate configs,
  or generate entity files.
- It may intentionally print supplied directory/config/data paths as part of
  copyable local commands; docs/tests must make this distinction clear.
- `uv.lock` must remain excluded.

Review focus:

1. Is the plan implementable without ambiguity?
2. Do tests sufficiently prove print-only behavior, no directory read, no
   SQLite/artifacts/subprocess execution, shell quoting, stable JSON keys, and
   intentional path echo?
3. Do docs avoid unsafe implications around scraping/source acquisition/platform
   monitoring/scheduling/demand proof?
4. Should any Critical or Important issue block implementation?

Output:

- Critical findings.
- Important findings.
- Minor findings.
- If no Critical or Important issue remains, include exactly:
  `APPROVED FOR STAGE 30 IMPLEMENTATION`
