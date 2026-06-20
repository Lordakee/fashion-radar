# Stage 129 PR Template Package Smoke Parity Design

## Objective

Align the pull request template's packaging verification guidance with the
current CI and GitHub upload checklist package smoke path.

## Problem

CI and the upload checklist build into a temporary directory, run the package
archive checker against that directory, then install the built wheel for smoke
tests:

```bash
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
```

The pull request template still has a compressed packaging checkbox that says
`uv --no-config build` plus installed-wheel smoke, but it does not mention the
temporary output directory or `scripts/check_package_archives.py`. That makes PR
review guidance weaker than CI and the upload checklist.

## Scope

In scope:

- Update `.github/pull_request_template.md` packaging verification guidance to
  include `tmp_build`, `uv --no-config build --out-dir "$tmp_build"`, and the
  archive checker command.
- Add a focused docs test that proves the PR template contains the temp-build,
  archive-checker, and installed-wheel `"$tmp_build"/*.whl` guidance.
- Update the canonical GitHub verification surface test so the PR template is
  included for the package archive checker and temp build commands.

Out of scope:

- No CI behavior changes.
- No package checker behavior changes.
- No runtime product behavior changes.
- No dependency changes.
- No `uv.lock` changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.

## Architecture

This is a documentation parity node:

1. `test_pull_request_template_package_smoke_uses_temp_build_archive_checker`
   extracts the PR template `Verification` section and asserts it contains the
   temp-build, archive-checker, and `"$tmp_build"/*.whl` installed-wheel
   guidance.
2. `test_github_verification_surfaces_use_no_config_frozen_uv_run` treats the
   PR template as a package verification surface for
   `scripts/check_package_archives.py "$tmp_build"` and
   `uv --no-config build --out-dir "$tmp_build"`.
3. The PR template checkbox is expanded into a small sub-list so the exact
   commands are easy for contributors to run.

## Expected Behavior

After implementation:

- The PR template contains:
  - `tmp_build="$(mktemp -d)"`
  - `uv --no-config build --out-dir "$tmp_build"`
  - `uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"`
- The PR template still points contributors to installed-wheel smoke for
  `fashion-radar --help`, `init`, `doctor`, and the packaged daily report
  template.
- Tests fail if the PR template drifts back to a generic `uv --no-config build`
  packaging note without the archive checker.
- Tests fail if the canonical GitHub verification surface matrix stops
  enforcing the PR template package build/archive-check commands.

## Risks

- The PR template should remain concise. A nested checklist under the existing
  packaging checkbox is enough; it should not duplicate the full upload
  checklist.
- The stage should not add package behavior or CI behavior. CI and the upload
  checklist already use the stronger path.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_pull_request_template_package_smoke_uses_temp_build_archive_checker tests/test_cli_docs.py::test_package_archive_smoke_command_is_documented_and_in_ci tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
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
