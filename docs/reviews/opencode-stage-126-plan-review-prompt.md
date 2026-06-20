Review the Stage 126 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align user-facing community handoff command sequences with the canonical
  local order: lint directory, preview candidates, readiness check, dry-run
  import, import, and imported review.
- Keep the change docs/test-only.

Design:
- `docs/superpowers/specs/2026-06-20-stage-126-community-handoff-order-docs-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-126-community-handoff-order-docs-plan.md`

Proposed implementation scope:
- `README.md`
- `docs/community-signal-quality.md`
- `docs/architecture.md`
- `tests/test_cli_docs.py`
- Stage 126 review artifacts only

Review focus:
1. Does the design address the community handoff command-order drift without
   changing runtime workflow behavior?
2. Is the planned regression test targeted enough to catch the affected user
   docs while avoiding brittle global command-order assertions?
3. Does the plan keep `community-handoff-workflow` as print-only overview and
   place the standalone `community-handoff-check-dir` after preview and before
   importer dry-run/import?
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
