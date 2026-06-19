# Stage 122 Plan Review

## Summary

The Stage 122 design and implementation plan are approved. The plan uses a
two-layer release guard: Hatch sdist exclusions omit internal review/planning
artifacts from normal source distributions, and
`scripts/check_package_archives.py` rejects those paths if they appear in a
built archive. The scope stays limited to build configuration, package archive
validation, tests, and Stage 122 review artifacts.

## Focus-area assessment

1. **Packaging gap solved without deleting/rename** - Yes. Repository-local
   `docs/reviews/` and `docs/superpowers/` artifacts remain untouched; only
   release archives omit or reject them. This aligns with the AGENTS.md rule to
   keep existing review records in place.

2. **Hatch exclude patterns correct** - Yes. `/docs/reviews/**` and
   `/docs/superpowers/**` are valid root-anchored recursive globs for
   Hatchling. They target only those two subtrees; the public docs in
   `SDIST_REQUIRED_PATHS` stay required.

3. **Checker rejects exact dir entries and children after normalization** -
   Yes. `normalize_sdist_paths()` strips the archive root prefix and
   `clean_archive_path()` strips trailing slashes, so a directory member ending
   in `/docs/reviews/` normalizes to `docs/reviews`. The planned guard
   `lower_path == prefix or lower_path.startswith(f"{prefix}/")` catches exact
   entries, trailing-slash forms, and child paths.

4. **TDD steps valid** - Yes. Task 1 should fail against current code because
   the checker does not currently reject `docs/reviews/...` or
   `docs/superpowers/...` members. Task 3 should fail because there is no
   current `[tool.hatch.build.targets.sdist]` section in `pyproject.toml`.

5. **Scope clean** - Yes. Pure build configuration, validation script, and
   tests. No runtime, CLI, dependency, connector, scraping, browser automation,
   platform API, monitoring, scheduling, source acquisition, demand proof,
   ranking, coverage verification, or compliance/audit product behavior.

6. **Verification sufficient** - Yes. Task 5 includes a real `uv build`, package
   checker run, and `tar -tzf ... | grep` member scan. Task 7 includes the full
   release gate.

## Critical findings
None.

## Important findings
None.

## Minor findings
- **M1 (readability):** Place the `docs/reviews` and `docs/superpowers`
  prefix rejection adjacent to the existing directory-tree checks. This is
  functionally equivalent to the planned location.
- **M2 (test symmetry):** Add an optional wheel test if the implementation wants
  to make the shared wheel/sdist guard explicit. This is not required because
  wheels do not carry docs today.
- **M3 (brittleness):** The pyproject test uses exact list equality. This is
  acceptable as a strong v0.1.0 release pin, but future sdist excludes will
  require updating the test.
- **M4 (execution note):** The push command must keep using a non-secret
  stand-in in repository files and must not persist the real token in Git
  config.

## Final statement

There are no Critical or Important blockers before implementation.
