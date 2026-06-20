Review the Stage 127 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Make `scripts/check_package_archives.py` reject unexpected direct children in
  the build output directory beyond the selected wheel and sdist.
- Preserve existing missing/duplicate wheel and sdist errors and
  archive-internal validation behavior.

Design:
- `docs/superpowers/specs/2026-06-20-stage-127-build-dir-direct-child-hygiene-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-127-build-dir-direct-child-hygiene-plan.md`

Proposed implementation scope:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 127 review artifacts only

Review focus:
1. Does the design address the gap between the checker help text and current
   behavior without changing archive-internal validation?
2. Are the planned RED tests specific enough to prove direct files,
   directories, and aggregated unexpected direct children are rejected?
3. Does the plan preserve existing missing/duplicate archive selection errors?
4. Does the scope avoid runtime product behavior, dependencies, lockfile,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?
5. Are the verification commands sufficient?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
