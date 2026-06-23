# Stage 163 Package Archive Invalid UTF-8 Design

## Objective

Make the package archive checker report deterministic validation errors when
wheel `.dist-info/METADATA` or `.dist-info/entry_points.txt` is present but not
valid UTF-8.

## Current Gap

`scripts/check_package_archives.py` reads both wheel text members through
`read_zip_text(...)`:

```python
def read_zip_text(archive: zipfile.ZipFile, path: str) -> str:
    return archive.read(path).decode("utf-8")
```

That path is used by:

- `validate_wheel_metadata(...)` for `{dist_info_dir}/METADATA`
- `validate_wheel_entry_points(...)` for `{dist_info_dir}/entry_points.txt`

If either member contains invalid UTF-8 bytes, `UnicodeDecodeError` escapes the
validator and the CLI prints a Python traceback instead of a checker error.
Stage 160 already noted this as a deferred edge case for entry points; the same
decode path also affects `METADATA`.

## Scope

In scope:

- Add regression tests for invalid UTF-8 in wheel `METADATA`.
- Add regression tests for invalid UTF-8 in wheel `entry_points.txt`.
- Return stable checker error lines:
  - `METADATA is not valid UTF-8`
  - `entry_points.txt is not valid UTF-8`
- Preserve no-traceback behavior.
- Keep all changes inside package archive validation and its tests.

Out of scope:

- No changes to package build configuration.
- No changes to archive filename, required-member, forbidden-member, dist-info
  directory, metadata name/version, or console-script validation semantics.
- No sdist text decoding work.
- No runtime CLI product behavior changes.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

## Architecture

Keep the decode helper simple and keep user-facing validation messages at the
validator level:

1. `validate_wheel_metadata(...)` catches `UnicodeDecodeError` around
   `read_zip_text(...)` and returns `["METADATA is not valid UTF-8"]`.
2. `validate_wheel_entry_points(...)` catches `UnicodeDecodeError` around
   `read_zip_text(...)` and returns `["entry_points.txt is not valid UTF-8"]`.
3. The existing `read_zip_text(...)` helper remains strict UTF-8 and continues
   to return a `str` for valid members.

This keeps the fix narrow and avoids changing the helper into a result object
or broadening its contract for paths that are not part of this stage.

## Tech Stack

- Python standard library: `zipfile`, existing strict UTF-8 decoding.
- Existing archive checker script `scripts/check_package_archives.py`.
- Existing pytest module `tests/test_package_archives.py`.
- Local opencode plan/code/release review with
  `zhipuai-coding-plan/glm-5.2 --variant max`.
- `uv --no-config run --frozen` for tests and lint.

## Implementation Method

Use test-first changes:

1. Broaden the test-only `write_wheel(...)` helper type to accept `str | bytes`
   values, because invalid UTF-8 fixtures need raw bytes.
2. Add a RED subprocess test where wheel `METADATA` contains invalid UTF-8
   bytes and assert:
   - exit code is 1;
   - stderr includes `METADATA is not valid UTF-8`;
   - stderr does not include `Traceback`;
   - stderr does not include `UnicodeDecodeError`.
3. Add a RED subprocess test where wheel `entry_points.txt` contains invalid
   UTF-8 bytes and assert:
   - exit code is 1;
   - stderr includes `entry_points.txt is not valid UTF-8`;
   - stderr does not include `Traceback`;
   - stderr does not include `UnicodeDecodeError`.
4. Add minimal `UnicodeDecodeError` handling in the two validators.
5. Run focused package archive tests, package archive smoke, opencode code
   review, full release gate, release review, commit, and push.

## Expected Behavior

Invalid `METADATA` bytes:

```python
{f"{EXPECTED_WHEEL_DIST_INFO_DIR}/METADATA": b"\xff\xfe\xfa"}
```

Expected stderr contains:

```text
METADATA is not valid UTF-8
```

Invalid `entry_points.txt` bytes:

```python
{f"{EXPECTED_WHEEL_DIST_INFO_DIR}/entry_points.txt": b"\xff\xfe\xfa"}
```

Expected stderr contains:

```text
entry_points.txt is not valid UTF-8
```

In both cases stderr must not contain:

```text
Traceback
UnicodeDecodeError
```

## Risks

- Catching too broadly could hide archive corruption or parser bugs. Catch only
  `UnicodeDecodeError` in the two text-member validators.
- Including the raw Python exception message would be deterministic but noisy
  and less stable across Python versions. Use stable checker-owned messages.
- Extending the low-level helper to return `(text, errors)` would add more
  churn than this narrow edge case needs.

## Verification

Focused:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "invalid_utf8 or metadata or entry_points"
uv --no-config run --frozen pytest tests/test_package_archives.py -q
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
rm -rf "$tmp_build"
```

Release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```
