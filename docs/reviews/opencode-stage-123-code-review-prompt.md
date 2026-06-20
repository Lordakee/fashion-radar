Review the Stage 123 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align CI, contributor, PR-template, and GitHub upload verification commands
  with `uv --no-config run --frozen ...`.
- Preserve ordinary local workflow examples and mirror install examples.
- Preserve explicit isolated lock/sync commands such as
  `UV_NO_CONFIG=1 uv lock --check`.

Files changed:
- `.github/workflows/ci.yml`
- `README.md`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- `docs/github-upload-checklist.md`
- `docs/first-run.md`
- `tests/test_cli_docs.py`
- Stage 123 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 123 design and plan?
2. Do release/agent/CI verification commands use no-config/frozen command
   forms consistently?
3. Are explicit isolated lock/sync commands preserved where they existed?
4. Are ordinary local workflow examples such as `uv run fashion-radar ...`
   preserved?
5. Are mirror install examples preserved only as local install aids?
6. Does the stage avoid runtime, CLI, dependency, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
