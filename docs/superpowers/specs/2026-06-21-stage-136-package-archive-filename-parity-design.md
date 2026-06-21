# Stage 136 Package Archive Filename And Sdist Root Parity Design

## Objective

Make the package archive checker reject wheel/sdist archives whose outer
filenames or sdist root directory do not match the project distribution name
and version derived from `pyproject.toml`.

## Problem

Stage 134 tightened wheel internals by validating the single top-level
`.dist-info` directory against project metadata. The release checker still has
two related naming gaps:

1. It selects archives only by glob:
   - `*.whl`
   - `*.tar.gz`
2. It normalizes sdist member paths by stripping any single common root
   directory, regardless of whether that root matches the expected project
   distribution name and version.

That means a build directory can pass with:

- `wrong_name-0.1.0-py3-none-any.whl` containing otherwise valid wheel
  contents;
- `wrong_name-0.1.0.tar.gz` containing otherwise valid sdist contents;
- `fashion_radar-0.1.0.tar.gz` whose members all live under
  `wrong_name-0.1.0/`, because `normalize_sdist_paths()` strips the wrong root
  before required-file validation.

This creates a release hygiene gap: the artifacts uploaded to GitHub can
disagree with `pyproject.toml` even when their internal required files are
present.

## Scope

In scope:

- Derive expected wheel and sdist archive filenames from
  `ExpectedProjectMetadata`.
- Derive the expected sdist root directory from `ExpectedProjectMetadata`.
- Reuse the existing stdlib-only distribution-name normalization:
  `fashion-radar` -> `fashion_radar`.
- Require the selected wheel filename to equal
  `<normalized-name>-<version>-py3-none-any.whl`.
- Require the selected sdist filename to equal
  `<normalized-name>-<version>.tar.gz`.
- Require the raw sdist member tree to contain exactly one common root and for
  that root to equal `<normalized-name>-<version>`.
- Add RED tests proving wheel filename drift, sdist filename drift, and sdist
  root drift are rejected while archive contents remain otherwise valid.

Out of scope:

- No wheel tag parsing or support for platform-specific wheel filenames.
- No wheel `.dist-info` path changes.
- No wheel/sdist required-member, license-path, or forbidden-member validation
  changes.
- No build backend or CI behavior changes.
- No dependency changes.
- No `pyproject.toml` changes.
- No `uv.lock` changes.
- No runtime product behavior changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.

## Architecture

1. Keep `ExpectedProjectMetadata` as the canonical package metadata loaded from
   `pyproject.toml`.
2. Reuse `normalize_distribution_name()` from Stage 134.
3. Add:
   - `expected_archive_base_name(expected_metadata) -> str`
   - `expected_wheel_archive_name(expected_metadata) -> str`
   - `expected_sdist_archive_name(expected_metadata) -> str`
   - `expected_sdist_root_dir(expected_metadata) -> str`
   - `validate_archive_filename(path, archive_label, expected_name) -> list[str]`
   - `validate_sdist_root_dir(raw_paths, expected_metadata) -> list[str]`
4. In `validate_build_dir()`, after selecting exactly one wheel and one sdist,
   validate both selected filenames before content validation.
5. Thread `expected_metadata` into `validate_sdist()`.
6. In `validate_sdist()`, inspect raw archive members before
   `normalize_sdist_paths()` strips the root:
   - clean raw paths with existing `clean_archive_path()`;
   - ignore empty cleaned paths;
   - derive roots from paths containing `/`;
   - emit one deterministic root mismatch error if there is not exactly one
     common root or if that root does not equal the expected root.
7. Keep `normalize_sdist_paths()` behavior unchanged for required-file checks
   after the root has been validated.

## Expected Behavior

After implementation:

- A normal `uv build` output containing:
  - `fashion_radar-0.1.0-py3-none-any.whl`
  - `fashion_radar-0.1.0.tar.gz`
  - sdist members under `fashion_radar-0.1.0/`
  continues to pass.
- A build directory containing only `wrong_name-0.1.0-py3-none-any.whl` plus a
  valid sdist fails with:
  `wheel archive filename mismatch: expected fashion_radar-0.1.0-py3-none-any.whl, found wrong_name-0.1.0-py3-none-any.whl`
- A build directory containing a valid wheel plus only `wrong_name-0.1.0.tar.gz`
  fails with:
  `sdist archive filename mismatch: expected fashion_radar-0.1.0.tar.gz, found wrong_name-0.1.0.tar.gz`
- An sdist named `fashion_radar-0.1.0.tar.gz` whose required files are under
  `wrong_name-0.1.0/` fails with:
  `sdist archive root directory mismatch: expected fashion_radar-0.1.0, found wrong_name-0.1.0`
- Existing missing archive, multiple archive, unexpected build-dir child,
  `.dist-info`, metadata, entry point, and forbidden-member tests continue to
  pass.

## Risks

- The project currently builds pure Python `py3-none-any` wheels. This stage
  intentionally pins that filename because broad wheel tag parsing would add
  complexity not needed by the current package.
- The checker should validate selected filenames only after existing
  exactly-one archive selection succeeds. Missing or multiple archive errors
  should keep their current messages.
- Sdist root validation must happen before `normalize_sdist_paths()` strips the
  root; validating after normalization would preserve the masking bug.
- Sdist root validation should not replace required-file checks. Wrong root
  with otherwise valid members should report root mismatch without noisy
  missing-file errors.
- Test helpers need optional filename/root overrides without disrupting the
  many existing callers that rely on current default names.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "filename or sdist_root or dist_info"
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
