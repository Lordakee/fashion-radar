Review the Stage 125 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `.github/ISSUE_TEMPLATE/bug_report.yml` verification examples with
  no-config/frozen uv run commands.
- Preserve ordinary local CLI examples in the issue template.

Design:
- `docs/superpowers/specs/2026-06-20-stage-125-issue-template-verification-command-parity-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-125-issue-template-verification-command-parity-plan.md`

Proposed implementation scope:
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `tests/test_cli_docs.py`
- Stage 125 review artifacts only

Review focus:
1. Does the design address the issue-template command drift without changing
   ordinary local CLI examples?
2. Are the planned docs tests specific enough to catch stale `uv run pytest`
   and `uv run ruff ...` verification forms in the bug report template?
3. Does the plan preserve `uv run fashion-radar doctor` and
   `UV_NO_CONFIG=1 uv lock --check`?
4. Does the scope avoid runtime, CLI, dependency, connector, scraping, browser
   automation, platform API, monitoring, scheduling, source acquisition, demand
   proof, ranking, coverage verification, and compliance/audit product
   behavior?
5. Are the verification commands sufficient?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
