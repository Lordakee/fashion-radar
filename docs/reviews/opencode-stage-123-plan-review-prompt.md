Review the Stage 123 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align CI, contributor, PR-template, and GitHub upload verification commands
  with `uv --no-config run --frozen ...`.
- Preserve ordinary local workflow examples and mirror install examples.

Design:
- `docs/superpowers/specs/2026-06-20-stage-123-verification-command-parity-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-123-verification-command-parity-plan.md`

Proposed implementation scope:
- `.github/workflows/ci.yml`
- `README.md`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- `docs/github-upload-checklist.md`
- `docs/first-run.md`
- `tests/test_cli_docs.py`
- Stage 123 review artifacts only

Review focus:
1. Does the design address the verification-command drift without changing
   ordinary local workflow examples?
2. Are the planned docs tests specific enough to catch stale release/agent/CI
   verification command forms without rejecting `uv run fashion-radar ...`
   examples?
3. Are mirror-backed install examples preserved as local install aids?
4. Are the TDD steps valid, with RED tests that fail against the current docs
   and GREEN changes that should pass?
5. Does the scope avoid runtime, CLI, dependency, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?
6. Are the verification commands sufficient?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
