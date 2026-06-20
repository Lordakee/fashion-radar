# Stage 130 Package Archive Pyproject Metadata Design

## Objective

Make the package archive checker derive expected wheel metadata from
`pyproject.toml` instead of duplicating package name, version, and console
script values as script constants.

## Problem

`scripts/check_package_archives.py` currently hardcodes:

- `PROJECT_NAME = "fashion-radar"`
- `PROJECT_VERSION = "0.1.0"`
- `ENTRY_POINT = "fashion-radar = fashion_radar.cli:app"`

Those values are canonical in `pyproject.toml`. A version bump or console-script
change could update package metadata while leaving the archive checker stale.

## Scope

In scope:

- Add a small stdlib `tomllib` loader for `[project]` metadata and
  `[project.scripts]`.
- Validate wheel `METADATA` name/version against loaded project metadata.
- Validate every configured console script line from `[project.scripts]` in
  wheel `entry_points.txt`.
- Add tests proving the loader derives values from both the repo
  `pyproject.toml` and a temporary supplied `pyproject.toml`.
- Keep existing archive behavior and error wording equivalent, with values
  coming from loaded metadata.

Out of scope:

- No dependency changes.
- No `pyproject.toml` changes.
- No `uv.lock` changes.
- No CI behavior changes.
- No package filename, dist-info path, license-path, wheel/sdist member, or
  forbidden-member validation changes.
- No runtime product behavior changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.

## Architecture

1. Add `ExpectedProjectMetadata` as a frozen dataclass with:
   - `name: str`
   - `version: str`
   - `console_script_lines: frozenset[str]`
2. Add `PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"`.
3. Add `load_expected_project_metadata(pyproject_path: Path = PYPROJECT)`:
   - read TOML with stdlib `tomllib`;
   - read `project.name`, `project.version`, and `project.scripts`;
   - build script lines as `"{script_name} = {target}"`.
4. Load metadata once in `validate_build_dir()`.
5. Thread metadata into `validate_wheel()`, `validate_wheel_metadata()`, and
   `validate_wheel_entry_points()`.
6. Require all configured script lines to exist in `entry_points.txt`, while
   keeping the current stripped-line membership style.

## Expected Behavior

After implementation:

- `load_expected_project_metadata()` returns `fashion-radar`, `0.1.0`, and
  `fashion-radar = fashion_radar.cli:app` from the repo `pyproject.toml`.
- The loader uses a supplied pyproject path in tests, proving values are
  derived rather than hardcoded.
- Existing valid wheel/sdist fixtures still pass.
- Existing invalid metadata and invalid entry point tests still fail with the
  same user-facing messages.
- A future additional `[project.scripts]` entry would be validated without
  adding another checker constant.

## Risks

- Importing the script module in tests must avoid executing `main()`. This is
  safe because `main()` is guarded by `if __name__ == "__main__"`.
- The current `entry_points.txt` parser is a stripped-line membership check,
  not an INI parser. This stage should not change that behavior.
- Test fixture archive filenames and `.dist-info` paths still contain `0.1.0`.
  That is intentional because this stage removes script-side metadata
  duplication, not fixture filename/path duplication.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_expected_archive_metadata_is_derived_from_pyproject tests/test_package_archives.py::test_expected_archive_metadata_loader_uses_supplied_pyproject -q
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen pytest tests/test_package_metadata.py tests/test_package_archives.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build="$(mktemp -d)"; uv --no-config build --out-dir "$tmp_build"; uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"; rm -rf "$tmp_build"
git diff --check
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if [ -n "$(git config --get-all http.https://github.com/.extraheader || true)" ]; then echo 'Persistent GitHub auth header found' >&2; exit 1; fi
```
