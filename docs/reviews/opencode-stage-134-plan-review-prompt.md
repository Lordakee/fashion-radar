Review the Stage 134 design and implementation plan before code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject wheels whose single top-level `.dist-info` directory does not match
  the expected project distribution name and version derived from
  `pyproject.toml`.
- Preserve existing exact-one-top-level `.dist-info`, missing dist-info file,
  metadata, entry point, and forbidden-member behavior.
- Keep this release-hygiene-only with no runtime product behavior changes.

Design:
- `docs/superpowers/specs/2026-06-21-stage-134-wheel-dist-info-metadata-parity-design.md`

Plan:
- `docs/superpowers/plans/2026-06-21-stage-134-wheel-dist-info-metadata-parity-plan.md`

Proposed implementation scope:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 134 review artifacts only

Review focus:
1. Does the design address the wheel `.dist-info` directory parity gap left out
   of Stage 130 without expanding into package filename validation?
2. Is the planned RED test specific enough to prove valid `METADATA` is not
   enough when the wheel `.dist-info` directory name or version is wrong?
3. Is the planned distribution-name normalization appropriate for deriving
   `fashion_radar-0.1.0.dist-info` from `fashion-radar` and `0.1.0` without
   adding dependencies?
4. Does the plan preserve nested/multiple/split `.dist-info` layout behavior by
   validating the exact directory name only after one top-level `.dist-info`
   directory is selected?
5. Does the plan avoid package filename validation, sdist root validation,
   dependency changes, `pyproject.toml`, `uv.lock`, CI changes, runtime product
   behavior changes, connectors, scraping, browser automation, platform API,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?
6. Are the verification commands sufficient?

Return:
Start with `# Stage 134 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
