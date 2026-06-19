Review the Stage 118 design and implementation plan before coding.

Repository: `/home/ubuntu/fashion-radar`

Files to review:
- `docs/superpowers/specs/2026-06-20-stage-118-agent-uv-run-hygiene-design.md`
- `docs/superpowers/plans/2026-06-20-stage-118-agent-uv-run-hygiene-plan.md`
- Current targets:
  - `AGENTS.md`
  - `README.md`
  - `docs/dependency-mirrors.md`
  - `docs/github-upload-checklist.md`
  - `tests/test_cli_docs.py`

Review focus:
1. Does the plan correctly separate mirror-backed frozen local installs from
   no-config frozen agent-run verification?
2. Is the planned test section-scoped and internally consistent with the exact
   planned doc text?
3. Are the target headings and helper functions in `tests/test_cli_docs.py`
   appropriate for `AGENTS.md`, `README.md`, `docs/dependency-mirrors.md`, and
   `docs/github-upload-checklist.md`?
4. Does the stage remain docs/tests-only, with no runtime, dependency,
   `uv.lock`, CI, connector, scraping, scheduling, monitoring, source
   acquisition, ranking, coverage verification, or compliance/audit product
   behavior?
5. Are the verification commands sufficient for this stage?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
