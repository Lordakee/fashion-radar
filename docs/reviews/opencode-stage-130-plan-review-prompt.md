Review the Stage 130 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Make `scripts/check_package_archives.py` derive expected project name,
  version, and console script lines from `pyproject.toml`.
- Keep archive validation behavior equivalent except for removing script-side
  metadata hardcoding.

Design:
- `docs/superpowers/specs/2026-06-20-stage-130-package-archive-pyproject-metadata-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-130-package-archive-pyproject-metadata-plan.md`

Proposed implementation scope:
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- Stage 130 review artifacts only

Review focus:
1. Does the design remove script-side hardcoded project name, version, and
   console script values without changing archive behavior?
2. Is the planned loader and metadata threading approach technically sound?
3. Do the planned tests prove derivation from both the repo `pyproject.toml`
   and a supplied temporary `pyproject.toml`?
4. Does the plan avoid package filename/path, license validation, forbidden
   member, dependency, lockfile, CI, runtime product, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit behavior changes?
5. Are the verification commands sufficient?

Return:
Start with `# Stage 130 Plan Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
