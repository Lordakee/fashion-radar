# Claude Code Stage 45 Release Review Prompt

You are reviewing the completed Stage 45 package archive and metadata readiness
changes for the `fashion-radar` repository.

Required review mode:

- Think carefully.
- Use maximum effort.
- This is a code, test, CI, and documentation release review.
- Do not edit files.
- Treat Critical and Important findings as blockers.

## Stage Goal

Make the GitHub-ready package surface explicit and testable: public package
metadata should identify the project correctly, both wheel and sdist archives
should be checked for release-critical files, and installed-package smoke checks
should cover both the console script and module entrypoint.

## Implementation Summary

Modified tracked files:

- `pyproject.toml`
  - Added package `keywords`, `classifiers`, and `[project.urls]` for GitHub
    repository, docs, issues, changelog, and security policy.
  - Did not change package name, version, dependencies, script entry point, or
    build backend.
- `.github/workflows/ci.yml`
  - Replaced inline wheel-template zip inspection with
    `UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"`.
  - Changed package build smoke to `UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"`.
  - Added installed module-entrypoint smoke:
    `"$tmp_env/venv/bin/python" -m fashion_radar --help`.
- `docs/github-upload-checklist.md`
  - Uses the same archive inspection script and module-entrypoint smoke as CI.
  - Keeps the broader installed command help loop.
- `README.md`
  - Clarifies source-checkout setup versus local wheel package readiness.
  - States the local wheel smoke does not publish to PyPI.
- `tests/test_cli_docs.py`
  - Guards CI/checklist package smoke command drift, including `UV_NO_CONFIG=1`
    on the build and archive-check commands.
  - Guards README install-mode language.

New files:

- `scripts/check_package_archives.py`
  - Dependency-free archive checker using standard library only.
  - Requires exactly one wheel and one `.tar.gz` sdist.
  - Checks required wheel package files, templates, exactly one top-level
    `.dist-info` directory, `METADATA`, `WHEEL`, `RECORD`, `entry_points.txt`,
    and `licenses/LICENSE`.
  - Validates wheel `METADATA` includes `Name: fashion-radar` and
    `Version: 0.1.0`.
  - Validates `entry_points.txt` includes
    `fashion-radar = fashion_radar.cli:app`.
  - Normalizes sdist root prefixes and checks release-critical public docs,
    configs, examples, schema, source files, and packaged templates.
- `tests/test_package_metadata.py`
  - Guards core package metadata, runtime version parity, script declaration,
    wheel package declaration, keywords, classifiers, and project URLs.
- `tests/test_package_archives.py`
  - Tests archive checker success, missing archives, missing required wheel
    file, missing `RECORD`, nested/multiple/split `.dist-info` layouts,
    missing public sdist doc, missing packaged template config, missing wheel
    metadata name/version, and missing console entry point.
- `docs/superpowers/specs/2026-06-15-stage-45-package-archive-metadata-readiness-design.md`
- `docs/superpowers/plans/2026-06-15-stage-45-package-archive-metadata-readiness-plan.md`
- `docs/reviews/claude-code-stage-45-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-45-plan-review.md`
- This release review prompt. The release review result will be written to
  `docs/reviews/claude-code-stage-45-release-review.md`.

## Review Feedback Already Addressed

Two read-only subagents reviewed the implementation before this release review:

- Spec compliance reviewer:
  - Important: release-review artifacts were missing. This prompt/result pair
    addresses that blocker.
  - Minor: missing single-file wheel/sdist path tests. Added coverage for a
    missing required wheel package file and a missing public-readiness sdist
    doc.
- Code quality reviewer:
  - Important: original wheel `.dist-info` pattern matching was too broad and
    accepted nested, split, or multiple `.dist-info` directories. Fixed by
    deriving exactly one top-level `.dist-info` directory and requiring all
    metadata files in that directory; added regression tests for nested,
    multiple, split, and missing `RECORD`.
  - Minor: package build commands should use `UV_NO_CONFIG=1`. Updated CI,
    checklist, tests, and verification commands accordingly.

## Boundaries

Confirm the change does not add:

- Source connectors, scraping, crawling, browser automation, login/cookie/
  account/proxy/CAPTCHA flows, platform APIs, source acquisition, schedulers,
  watchers, monitors, or external services.
- Compliance-review functionality inside the tool.
- Dependency additions, dependency upgrades, lockfile changes, package version
  bumps, runtime CLI behavior changes, database schema changes, dashboard
  changes, generated reports, or generated local data.
- PyPI publishing, GitHub release creation, artifact upload, or remote
  configuration changes.

## Verification Already Run

Focused tests:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_metadata.py tests/test_package_archives.py tests/test_cli_docs.py -q
```

Result: `18 passed` before the `.dist-info` tightening; after tightening,
package archive tests and CLI package-smoke guard were rerun and passed.

Malformed wheel RED before fix:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py::test_rejects_nested_wheel_dist_info_directory tests/test_package_archives.py::test_rejects_multiple_wheel_dist_info_directories tests/test_package_archives.py::test_rejects_split_wheel_dist_info_files tests/test_package_archives.py::test_rejects_wheel_without_record_file -q
```

Result before fix: `4 failed`, proving the code-quality finding.

Malformed wheel GREEN after fix:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_package_archives.py::test_rejects_nested_wheel_dist_info_directory tests/test_package_archives.py::test_rejects_multiple_wheel_dist_info_directories tests/test_package_archives.py::test_rejects_split_wheel_dist_info_files tests/test_package_archives.py::test_rejects_wheel_without_record_file -q
```

Result after fix: `4 passed`.

Archive and install smoke:

```bash
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/fashion-radar" --help
"$tmp_env/venv/bin/python" -m fashion_radar --help
```

Result: build succeeded, archive script printed
`Package archives contain required files.`, and both help commands exited 0.

Full verification:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
git diff --check
git diff --cached --check
git diff --quiet -- uv.lock
```

Result: all passed; full test suite reported `653 passed`.

## Specific Review Questions

1. Does Stage 45 satisfy the approved package archive and metadata readiness
   scope?
2. Is the archive checker correct enough for wheel/sdist release-critical files,
   including `.dist-info` layout and metadata validation?
3. Are CI and the GitHub upload checklist aligned and appropriately isolated
   from user-level uv mirror config where public release checks matter?
4. Are tests meaningful and not just checking mocks or brittle implementation
   details?
5. Are there any Critical or Important issues that must be fixed before commit
   and push?

## Required Output

Respond with Critical, Important, and Minor findings plus a concise verdict.
If and only if the changes are acceptable to commit and push, include this exact
phrase:

```text
APPROVED FOR STAGE 45 COMMIT AND PUSH
```
