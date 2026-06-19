Review the Stage 122 design and implementation plan before any code changes.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Exclude internal review and superpowers planning artifacts from source
  distributions.
- Make package archive validation fail if those internal artifact paths appear
  in any release archive.

Design:
- `docs/superpowers/specs/2026-06-20-stage-122-sdist-internal-artifact-exclusion-design.md`

Plan:
- `docs/superpowers/plans/2026-06-20-stage-122-sdist-internal-artifact-exclusion-plan.md`

Proposed implementation scope:
- `pyproject.toml`
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `tests/test_package_metadata.py`
- Stage 122 review artifacts only

Review focus:
1. Does the design solve the proven packaging gap without deleting or renaming
   repository-local review/plan artifacts?
2. Are the Hatch sdist exclude patterns correct for omitting
   `docs/reviews/**` and `docs/superpowers/**` from a real sdist?
3. Does the checker plan reject both exact directory entries and child paths
   after archive path normalization?
4. Are the TDD steps valid, with RED tests that fail against the current
   implementation and GREEN changes that should pass?
5. Does the scope avoid runtime, CLI, dependency, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?
6. Are the verification commands sufficient, including a real build and sdist
   member scan?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before implementation.
