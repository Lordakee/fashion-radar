Review the Stage 125 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `.github/ISSUE_TEMPLATE/bug_report.yml` verification examples with
  no-config/frozen uv run commands.
- Preserve ordinary local CLI examples in the issue template.

Files changed:
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `tests/test_cli_docs.py`
- Stage 125 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 125 design and plan?
2. Does the bug report template use no-config/frozen ruff and pytest
   verification commands?
3. Does the test reject stale `uv run pytest` and `uv run ruff ...` examples in
   the bug report template without rejecting `uv run fashion-radar doctor`?
4. Does the stage avoid runtime, CLI, dependency, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
