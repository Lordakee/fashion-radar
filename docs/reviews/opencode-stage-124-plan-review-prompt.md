Review the Stage 124 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject unsafe wheel and sdist archive member paths in
  `scripts/check_package_archives.py`.
- Preserve existing required-file, metadata, entry-point, and forbidden-member
  package archive validation behavior.

Design:
- `docs/superpowers/specs/2026-06-20-stage-124-package-archive-member-path-safety-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-124-package-archive-member-path-safety-plan.md`

Proposed implementation scope:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 124 review artifacts only

Review focus:
1. Does the design address the archive member path blind spot without changing
   runtime product behavior?
2. Are the planned RED tests specific enough to fail against the current
   checker for wheel and sdist unsafe paths?
3. Does the implementation plan reject unsafe paths before sdist root-prefix
   stripping?
4. Does the plan preserve existing required-file, metadata, entry-point, and
   forbidden-member package archive validation behavior?
5. Does the scope avoid dependency, lockfile, connector, scraping, browser
   automation, platform API, monitoring, scheduling, source acquisition, demand
   proof, ranking, coverage verification, and compliance/audit product
   behavior?
6. Are the verification commands sufficient?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
