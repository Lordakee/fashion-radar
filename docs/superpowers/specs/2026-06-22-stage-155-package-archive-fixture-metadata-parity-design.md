# Stage 155 Package Archive Fixture Metadata Parity Design

## Goal

Remove package name/version drift from `tests/test_package_archives.py` fixtures by
deriving archive filenames, wheel `dist-info` paths, sdist root paths, and
expected metadata strings from `scripts/check_package_archives.py` helper
functions instead of hard-coding `fashion_radar-0.1.0` in fixture construction.

## Background

`scripts/check_package_archives.py` already derives expected package archive names
from `pyproject.toml` through `load_expected_project_metadata()`,
`expected_archive_base_name()`, `expected_wheel_archive_name()`,
`expected_sdist_archive_name()`, `expected_sdist_root_dir()`, and
`expected_wheel_dist_info_dir()`.

The test module still embeds the current normalized distribution name and version
in many fixture paths and expected messages. That means a future version bump or
package-name normalization change could require broad manual test edits even when
the checker itself remains correct.

## Scope

Modify only:

- `tests/test_package_archives.py`
- Stage 155 plan/review artifacts

Do not change:

- `scripts/check_package_archives.py`
- `pyproject.toml`
- runtime package metadata
- archive validation behavior
- lockfiles

## Design

Add module-level helper constants in `tests/test_package_archives.py` immediately
after `spec.loader.exec_module(check_package_archives)`:

```python
EXPECTED_METADATA = check_package_archives.load_expected_project_metadata()
EXPECTED_ARCHIVE_BASE_NAME = check_package_archives.expected_archive_base_name(
    EXPECTED_METADATA,
)
EXPECTED_WHEEL_ARCHIVE_NAME = check_package_archives.expected_wheel_archive_name(
    EXPECTED_METADATA,
)
EXPECTED_SDIST_ARCHIVE_NAME = check_package_archives.expected_sdist_archive_name(
    EXPECTED_METADATA,
)
EXPECTED_SDIST_ROOT_DIR = check_package_archives.expected_sdist_root_dir(
    EXPECTED_METADATA,
)
EXPECTED_WHEEL_DIST_INFO_DIR = check_package_archives.expected_wheel_dist_info_dir(
    EXPECTED_METADATA,
)
```

Then update fixture builders and expected strings to use these constants:

- `WHEEL_FILES` uses `EXPECTED_WHEEL_DIST_INFO_DIR` for all `.dist-info` paths.
- `WHEEL_FILES["METADATA"]` uses `EXPECTED_METADATA.name` and
  `EXPECTED_METADATA.version`.
- Override keys in tests that intentionally replace the positive wheel
  `METADATA` or `entry_points.txt` members use `EXPECTED_WHEEL_DIST_INFO_DIR`.
- `wheel_files_with_dist_info_dir()` detects positive dist-info members using
  `EXPECTED_WHEEL_DIST_INFO_DIR`.
- `write_wheel()` defaults to `EXPECTED_WHEEL_ARCHIVE_NAME`.
- `write_sdist()` defaults to `EXPECTED_SDIST_ARCHIVE_NAME` and
  `EXPECTED_SDIST_ROOT_DIR`.
- `write_sdist_with_raw_member()` uses `EXPECTED_SDIST_ARCHIVE_NAME` and
  `EXPECTED_SDIST_ROOT_DIR` directly inside the function body.
- positive and negative fixture paths/error-message assertions that represent
  the expected package name/version use the constants instead of duplicated
  literals.
- assertion messages for missing `Name`, missing `Version`, and missing console
  scripts use `EXPECTED_METADATA.name`, `EXPECTED_METADATA.version`, and
  `EXPECTED_METADATA.console_script_lines`.

Keep intentionally wrong fixture values readable and explicit where their purpose
is to simulate a wrong archive:

- `wrong_name-0.1.0-py3-none-any.whl`
- `fashion_radar-9.9.9-py3-none-any.whl`
- `wrong_name-0.1.0.tar.gz`
- `fashion_radar-9.9.9.tar.gz`
- `other-0.1.0.dist-info/...`
- unsafe archive-member path strings such as
  `fashion_radar-0.1.0/../outside.txt`

Those values are negative fixtures, not expected project metadata.

## Test Strategy

Add a focused guard test near `test_expected_archive_metadata_is_derived_from_pyproject()`:

```python
def test_package_archive_fixture_names_are_derived_from_expected_metadata() -> None:
    assert EXPECTED_WHEEL_ARCHIVE_NAME == "fashion_radar-0.1.0-py3-none-any.whl"
    assert EXPECTED_SDIST_ARCHIVE_NAME == "fashion_radar-0.1.0.tar.gz"
    assert EXPECTED_SDIST_ROOT_DIR == "fashion_radar-0.1.0"
    assert EXPECTED_WHEEL_DIST_INFO_DIR == "fashion_radar-0.1.0.dist-info"
    assert f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA" in WHEEL_FILES
```

This test intentionally keeps the current public package metadata visible and
verifies the derived dist-info key is present in `WHEEL_FILES`. The end-to-end
positive archive test proves those derived defaults still line up with checker
expectations.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check tests/test_package_archives.py
uv --no-config run --frozen ruff format --check tests/test_package_archives.py
git diff --check
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```
