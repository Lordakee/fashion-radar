# Stage 130 Code Review

## Critical findings
None.

## Important findings
None.

## Minor findings

1. **`load_expected_project_metadata` still raises on malformed `[project]`.** `data["project"]`, `project["name"]`, and `project["version"]` are unguarded, so a malformed repo `pyproject.toml` surfaces as a bare `KeyError` traceback. The Stage 130 plan review already classified this as acceptable for an internal developer tool that always reads the well-formed repo pyproject (no test exercises a malformed `[project]` table, and existing `"Traceback" not in result.stderr` assertions cover archive-validation paths only, not pyproject loading). No change recommended for this stage; noting for completeness.

2. **Fixture archive filenames still embed `0.1.0`.** `tests/test_package_archives.py` (e.g. lines 29-37, 133, 144, 150) still hardcodes `fashion_radar-0.1.0.dist-info/...` member paths, `fashion_radar-0.1.0-py3-none-any.whl`, and `fashion_radar-0.1.0.tar.gz`. The design (Risk section, line 84-86) explicitly scopes this out: this stage removes script-side metadata duplication, not fixture filename/path duplication. Not a blocker; future stages could derive fixture dist-info paths from the loader if version-bump drift becomes a real risk.

3. **Default `PYPROJECT` evaluated at import time.** `PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"` (line 15) is a pure path expression (no I/O), so module-import-time evaluation is safe and test-friendly. The `test_expected_archive_metadata_is_derived_from_pyproject` test empirically confirms the default resolves to the real repo pyproject when the script is loaded via `importlib.util` (verified: `/home/ubuntu/fashion-radar/pyproject.toml`, values `fashion-radar`/`0.1.0`/`fashion-radar = fashion_radar.cli:app`). No issue; noted for transparency.

## Analysis against review focus

1. **Implementation matches design and plan — yes.** The `ExpectedProjectMetadata` frozen dataclass (lines 18-22), `PYPROJECT` constant (line 15), `load_expected_project_metadata` loader (lines 25-37), single load site in `validate_build_dir()` (line 186), threading into `validate_wheel` (line 202), `validate_wheel_metadata` (line 257), and `validate_wheel_entry_points` (line 261) all match the design's Architecture section verbatim and Task 2's steps exactly. The two internal call sites flagged in the plan review (`scripts/check_package_archives.py:257` and `:261`) correctly gained the `expected_metadata` argument.

2. **Stdlib-only loader — yes.** `import tomllib` (line 8) and `from dataclasses import dataclass` (line 11) are both stdlib in Python ≥3.11, matching `requires-python = ">=3.11"`. No third-party imports added. The loader reads `data["project"]`, `project["name"]`, `project["version"]`, and `project.get("scripts", {})`, then builds lines as `f"{script_name} = {target}"`.

3. **Loaded once per `validate_build_dir()` and threaded through — yes.** Line 186 calls `load_expected_project_metadata()` exactly once, before `select_single_archive`. The result is passed to `validate_wheel(wheel_path, expected_metadata)` and onward to `validate_wheel_metadata`/`validate_wheel_entry_points`. No repeated disk reads per archive member.

4. **Entry point validation checks every configured line via stripped-line membership — yes.** `validate_wheel_entry_points` (lines 307-319) builds `entry_point_lines = {line.strip() for line in entry_points.splitlines()}` (preserving the existing parser style) and emits one error per missing line in `sorted(expected_metadata.console_script_lines)`. The `sorted()` only affects output determinism (one configured script today, so it is behavior-equivalent; multiple future scripts get deterministic error ordering). No ordering or formatting requirement is introduced beyond stripped-line membership, and the existing `entry_points.txt is missing fashion-radar = fashion_radar.cli:app` assertion still passes verbatim.

5. **Tests prove both derivations — yes.** `test_expected_archive_metadata_is_derived_from_pyproject` (lines 82-87) calls the loader with no argument and asserts the real repo values. `test_expected_archive_metadata_loader_uses_supplied_pyproject` (lines 90-115) writes a temp pyproject with distinct values (`example-package`, `9.8.7`, two scripts `example-cli` and `example-admin`) and asserts the loader reflects them — proving values are derived, not hardcoded. Both tests pass (verified, part of 60/60 passing in `tests/test_package_archives.py`).

6. **Scope avoidance — complete.** No `pyproject.toml`, `uv.lock`, dependency, CI, package filename/dist-info path, license path, wheel/sdist member, forbidden-member, or required-path list changes. `WHEEL_REQUIRED_PATHS`, `WHEEL_REQUIRED_DIST_INFO_PATHS`, and `SDIST_REQUIRED_PATHS` are unchanged. The `entry_points.txt` parser remains stripped-line membership. Error wording (`METADATA is missing Name: …`, `METADATA is missing Version: …`, `entry_points.txt is missing …`) is preserved verbatim with values sourced from loaded metadata. No runtime product, connector, scraping, browser automation, platform API, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance/audit behavior is introduced. End-to-end `uv build` smoke test confirms loaded pyproject metadata matches hatchling output (`Package archives contain required files.`). Ruff check + format pass; `git diff --check` clean.

## Verification performed

- `uv --no-config run --frozen pytest tests/test_package_archives.py -q` → 60 passed.
- `uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py` → All checks passed.
- `uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py` → 2 files already formatted.
- `uv --no-config build --out-dir "$tmp"; uv --no-config run --frozen python scripts/check_package_archives.py "$tmp"` → `Package archives contain required files.` (loaded metadata matches real hatchling output).
- `git diff --check` → clean.

## Final statement

There are **no Critical or Important blockers** before release. The Stage 130 implementation matches its design and plan, derives project name/version/console scripts from `pyproject.toml` with stdlib only, loads metadata once per `validate_build_dir()` run, preserves stripped-line membership for entry point validation, is proven by both repo-pyproject and supplied-pyproject tests, and stays within the documented scope boundary. Only the three minor findings above (none of which warrant a code change at this stage) were identified.
