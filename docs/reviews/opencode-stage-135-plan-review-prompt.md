Review the Stage 135 design and implementation plan before code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Harden first-run smoke validation for external/community tool workflow
  command shapes by comparing parsed shell argv lists exactly.
- Keep expected path values derived from payload fields so temporary first-run
  smoke directories remain valid.
- Keep this validation-only with no CLI runtime behavior changes.

Design:
- `docs/superpowers/specs/2026-06-21-stage-135-first-run-external-tool-command-shape-design.md`

Plan:
- `docs/superpowers/plans/2026-06-21-stage-135-first-run-external-tool-command-shape-plan.md`

Proposed implementation scope:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 135 review artifacts only

Review focus:
1. Does the design address weak substring validation in
   `validate_external_tool_workflow()` and `validate_external_tool_readiness()`
   without broadening into runtime CLI behavior?
2. Are the planned RED tests specific enough to prove current substring checks
   accept malformed commands?
3. Does the plan use `shlex.split()` and exact argv comparison rather than
   direct string equality, so shell quoting remains flexible?
4. Does the plan derive directory/config/data path arguments from payload
   fields rather than hardcoding fixture paths?
5. Does the plan avoid runtime CLI behavior changes, docs wording changes,
   package/archive checker changes, dependencies, `uv.lock`, connectors,
   scraping, browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, generated command
   execution, PATH lookup behavior changes, import behavior, SQLite behavior,
   file-read behavior, artifact creation behavior, and compliance/audit product
   behavior?
6. Are the verification commands sufficient?

Return:
Start with `# Stage 135 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
