# Stage 124 Package Archive Member Path Safety Design

## Objective

Make the package archive checker fail closed when a wheel or sdist contains an
unsafe archive member path before the checker performs normal required-file and
forbidden-member validation.

## Problem

`scripts/check_package_archives.py` normalizes archive member names by replacing
backslashes with slashes, stripping trailing slashes, and removing leading `./`.
It does not currently reject member names containing parent-directory
components, absolute paths, Windows drive paths, or UNC-style paths.

That leaves a narrow release-gate blind spot: a malformed archive can pass the
normal missing/forbidden-member checks even when one member path would be unsafe
to extract. For sdists, root-prefix stripping can also turn a raw member such as
`fashion_radar-0.1.0/../outside.txt` into `../outside.txt` after the checker has
already decided which root to remove.

## Scope

In scope:

- Add focused package archive tests for unsafe wheel member paths.
- Add focused package archive tests for unsafe sdist member paths.
- Reject archive member names that normalize to:
  - any path with a `..` component,
  - any slash-normalized absolute POSIX path,
  - any slash-normalized Windows drive path such as `C:/outside.txt` or
    `C:outside.txt`,
  - any slash-normalized UNC-style path such as `//server/share/file.txt`.
- Run the unsafe-member check on raw wheel and sdist member names before sdist
  root-prefix stripping.
- Preserve existing required-file, metadata, entry-point, and forbidden-release
  member validation behavior.

Out of scope:

- No runtime package behavior changes.
- No CLI behavior changes except the existing archive checker returning clearer
  errors for malformed archives.
- No dependency changes.
- No `uv.lock` changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.
- No new release publishing, upload, or PyPI automation.

## Architecture

The archive checker keeps the existing normalization helpers and adds one small
guard layer:

1. `unsafe_archive_member_errors(paths, archive_label)` converts raw archive
   member names through the existing `clean_archive_path` helper.
2. `is_unsafe_archive_path(path)` applies path-shape checks to the normalized
   string.
3. `validate_wheel()` reads raw zip member names once, records unsafe-member
   errors, then continues with the existing clean-path validations so users can
   see all relevant archive problems in one run.
4. `validate_sdist()` reads raw tar member names once, records unsafe-member
   errors, then continues with existing sdist root normalization and required
   file checks.

The helper is deliberately string-based. The archive member names are not local
filesystem paths, and using host `Path` semantics would make behavior depend on
the operating system running the checker.

## Expected Behavior

After implementation:

- A wheel containing `../outside.txt` fails with
  `wheel archive contains unsafe archive member path: ../outside.txt`.
- A wheel containing `/absolute.txt` fails with
  `wheel archive contains unsafe archive member path: /absolute.txt`.
- A wheel containing `C:/outside.txt` fails with
  `wheel archive contains unsafe archive member path: C:/outside.txt`.
- A wheel containing `fashion_radar\..\outside.txt` fails after slash
  normalization with
  `wheel archive contains unsafe archive member path: fashion_radar/../outside.txt`.
- A sdist containing `fashion_radar-0.1.0/../outside.txt` fails before root
  prefix stripping with
  `sdist archive contains unsafe archive member path: fashion_radar-0.1.0/../outside.txt`.
- Existing valid archive fixtures continue to pass.
- Existing forbidden-member tests continue to pass.

## Risks

- The checker may report both unsafe-member and missing-required-file errors
  for the same malformed archive. That is acceptable and matches the current
  style of collecting multiple validation errors.
- Directory entries such as `./` already normalize to an empty path and remain
  ignored. This stage does not change that behavior.
- The guard should not try to resolve or simplify paths; it should only reject
  clearly unsafe member-name shapes.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "unsafe_archive_member"
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
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
```
