Review the updated Stage 136 design and implementation plan before code
changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Reject wheel/sdist archive files whose outer filenames or sdist root
  directory do not match the project distribution name and version derived from
  `pyproject.toml`.
- Keep existing archive required-file and forbidden-member checks unchanged.
- Keep this release-hygiene-only with no runtime product behavior changes.

Design:
- `docs/superpowers/specs/2026-06-21-stage-136-package-archive-filename-parity-design.md`

Plan:
- `docs/superpowers/plans/2026-06-21-stage-136-package-archive-filename-parity-plan.md`

Proposed implementation scope:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 136 review artifacts only

Review focus:
1. Does the design address package archive outer filename parity and the sdist
   root-normalization masking gap left after Stage 134 without broadening into
   wheel tag parsing?
2. Are the planned RED tests specific enough to prove valid archive contents
   are not enough when the outer wheel filename, outer sdist filename, or sdist
   root directory is wrong?
3. Does the plan derive expected filenames and sdist root from
   `ExpectedProjectMetadata` and the existing normalized distribution name
   helper?
4. Does the plan preserve existing missing/multiple archive behavior by
   validating filenames only after one wheel and one sdist are selected?
5. Does the plan validate sdist root names from raw member names before
   `normalize_sdist_paths()` strips the root?
6. Does the plan avoid wheel tag parsing, `.dist-info` changes, dependency
   changes, `pyproject.toml`, `uv.lock`, CI, runtime product behavior,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?
7. Are the verification commands sufficient?

Return:
Start with `# Stage 136 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
