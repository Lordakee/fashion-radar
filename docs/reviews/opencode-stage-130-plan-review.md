# Stage 130 Plan Review

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **Plan-review artifacts have no explicit task step.** The Files section (plan line 26-29) and commit list (plan line 336) reference `docs/reviews/opencode-stage-130-plan-review-prompt.md` and `docs/reviews/opencode-stage-130-plan-review.md`, but no Task creates them. Task 3 explicitly creates only the code-review pair. Since this very review produces the plan-review artifacts, the omission is understandable, but the plan should either add a Task 0/1 step for them or note they are produced out-of-band, so an executing agent does not skip committing them.

2. **Call-site edits for threading are implicit.** Task 2 Step 2 specifies the new signatures for `validate_wheel`, `validate_wheel_metadata`, and `validate_wheel_entry_points`, but does not spell out the two internal call sites in `validate_wheel` (`scripts/check_package_archives.py:225` and `:227`) that must gain the `expected_metadata` argument. A competent agent will infer this, but making it explicit would reduce drift risk.

3. **Loader raises on malformed pyproject.** `load_expected_project_metadata` does `data["project"]`, `project["name"]`, `project["version"]` without guards, so a malformed `[project]` table raises `KeyError` rather than a clean error. This is acceptable for an internal developer tool that always reads the well-formed repo pyproject, and existing `"Traceback" not in result.stderr` assertions only cover archive-validation paths (not pyproject loading). Noting for completeness only; no change recommended for this stage.

## Analysis against review focus

1. **Removes hardcoded values without changing archive behavior — yes.** `PROJECT_NAME`, `PROJECT_VERSION`, and `ENTRY_POINT` (`scripts/check_package_archives.py:13-15`) are replaced by a `tomllib` loader reading the canonical `pyproject.toml`. Error wording (`METADATA is missing Name: …`, `METADATA is missing Version: …`, `entry_points.txt is missing …`) is preserved verbatim with values sourced from loaded metadata. The real-repo derivation produces `fashion-radar` / `0.1.0` / `fashion-radar = fashion_radar.cli:app`, matching the current constants and existing fixtures (verified empirically above).

2. **Loader and metadata threading technically sound — yes.** `tomllib` is stdlib for Python ≥3.11 (matches `requires-python = ">=3.11"`). `PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"` correctly resolves to repo root from `scripts/`. The frozen `ExpectedProjectMetadata` dataclass with `frozenset[str]` script lines is immutable and membership-friendly. Loading once in `validate_build_dir()` and threading through avoids repeated disk reads. Importantly, when loaded via `importlib.util` in tests, `__file__` is still the script path, so the default-argument form genuinely derives from the real repo pyproject.

3. **Tests prove both derivations — yes.** `test_expected_archive_metadata_is_derived_from_pyproject` calls `load_expected_project_metadata()` (default repo pyproject) and asserts the real values. `test_expected_archive_metadata_loader_uses_supplied_pyproject` writes a temp pyproject with distinct values (`example-package`, `9.8.7`, two scripts) and asserts the loader reflects them — proving values are derived rather than hardcoded. The RED-then-GREEN TDD ordering (Task 1 before Task 2) is correct.

4. **Scope avoidance — complete.** No `pyproject.toml`, `uv.lock`, dependency, CI, filename/dist-info path, license (`WHEEL_REQUIRED_DIST_INFO_PATHS` keeps `licenses/LICENSE`), wheel/sdist member, forbidden-member, or required-path list changes. The `entry_points.txt` parser remains a stripped-line membership check (design Risk section explicitly preserves this). No runtime product, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit behavior is introduced. The `sorted()` in the new entry-points check is behavior-equivalent for the single configured script and only adds determinism for a hypothetical future multi-script case — not a regression. Fixture filenames/paths still containing `0.1.0` is a deliberate, documented scope boundary (design line 84-86), not script-side constant drift.

5. **Verification commands sufficient — yes.** Focused verification covers the two new tests, the full archive test file, the combined metadata+archives suite, ruff check + format, and a real `uv build` smoke test feeding the checker (strong end-to-end proof that loaded pyproject metadata matches hatchling output). The release gate adds full pytest, release hygiene, lock check + lockfile diff, whitespace, token-absence, and persistent-auth-header-absence assertions. Adequate for the change surface.

## Final statement

There are **no Critical or Important blockers** before implementation. The Stage 130 design and plan are sound, in-scope, behavior-preserving, and adequately tested; only the three minor findings above (of which only #1, plan-review artifact ownership, is worth resolving before execution) were identified.
