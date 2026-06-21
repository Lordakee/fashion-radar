# Stage 134 Wheel Dist-Info Metadata Parity Design

## Objective

Make the package archive checker reject wheels whose single top-level
`.dist-info` directory does not match the expected project distribution name
and version derived from `pyproject.toml`.

## Problem

Stage 130 made wheel `METADATA` and `entry_points.txt` expectations derive from
`pyproject.toml`, but explicitly left package filename and `.dist-info` path
validation out of scope. The current checker only requires exactly one
top-level `.dist-info` directory, then validates metadata files under whatever
directory it found.

That means a wheel can currently pass with a directory such as
`wrong_name-9.9.9.dist-info/` as long as its `METADATA` still says:

- `Name: fashion-radar`
- `Version: 0.1.0`

This creates a release hygiene gap: the archive metadata content and the wheel
directory naming convention can disagree without the release gate noticing.

## Scope

In scope:

- Derive the expected wheel `.dist-info` directory name from
  `ExpectedProjectMetadata`.
- Normalize the project distribution name using the standard wheel directory
  convention for this project: collapse runs of `-`, `_`, and `.` to `_`, then
  lowercase.
- Require the selected top-level `.dist-info` directory to equal
  `<normalized-name>-<version>.dist-info`.
- Add RED tests for both name mismatch and version mismatch while keeping
  `METADATA` content valid.
- Keep the existing exact-one-top-level `.dist-info` directory check and
  missing-file checks.

Out of scope:

- No package filename validation.
- No sdist root directory validation.
- No license-path, wheel/sdist member, or forbidden-member validation changes.
- No dependency changes.
- No `pyproject.toml` changes.
- No `uv.lock` changes.
- No CI behavior changes.
- No runtime product behavior changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.

## Architecture

1. Keep `ExpectedProjectMetadata` as the canonical project metadata object
   loaded from `pyproject.toml`.
2. Add a small stdlib-only helper:
   - `normalize_distribution_name(name: str) -> str`
   - implementation: `re.sub(r"[-_.]+", "_", name).lower()`
3. Add `expected_wheel_dist_info_dir(expected_metadata)` returning
   `f"{normalized_name}-{expected_metadata.version}.dist-info"`.
4. Add `validate_wheel_dist_info_dir(dist_info_dir, expected_metadata)` that
   returns:
   - `[]` when the selected directory matches the expected value;
   - one deterministic error when it does not.
5. In `validate_wheel()`, after `select_wheel_dist_info_dir(paths)` succeeds
   and before validating files under that directory, append the mismatch error.
6. Keep metadata and entry point validation conditional on files existing, so a
   mismatched directory can still report all relevant directory-level and
   metadata-level errors without a traceback.

## Expected Behavior

After implementation:

- A valid wheel containing `fashion_radar-0.1.0.dist-info/` still passes.
- A wheel containing `wrong_name-0.1.0.dist-info/` and valid `METADATA` fails
  with:
  `wheel archive dist-info directory mismatch: expected fashion_radar-0.1.0.dist-info, found wrong_name-0.1.0.dist-info`
- A wheel containing `fashion_radar-9.9.9.dist-info/` and valid `METADATA`
  fails with:
  `wheel archive dist-info directory mismatch: expected fashion_radar-0.1.0.dist-info, found fashion_radar-9.9.9.dist-info`
- Existing tests for missing `METADATA`, missing `entry_points.txt`, nested
  `.dist-info`, multiple `.dist-info`, split `.dist-info`, and invalid metadata
  remain meaningful and continue to pass after the checker is tightened.

## Risks

- The normalization rule must match wheel directory naming for the current
  project without adding packaging dependencies. The project only needs the
  PEP 503-style separator collapse for `fashion-radar` to `fashion_radar`, so
  a local stdlib helper is sufficient.
- Running the mismatch check only after exact-one-top-level selection is
  important. Nested, split, or multiple `.dist-info` layouts should continue to
  use the existing broader layout error rather than a misleading mismatch
  message.
- This stage intentionally does not validate the wheel archive filename. That
  should remain a later, separately tested stage if needed.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "dist_info"
uv --no-config run --frozen pytest tests/test_package_archives.py tests/test_package_metadata.py -q
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
