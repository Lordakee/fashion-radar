# Stage 125 Issue Template Verification Command Parity Design

## Objective

Align the GitHub bug report issue template's verification examples with the
project's current no-config/frozen agent verification command practice.

## Problem

Stage 123 aligned CI, README, CONTRIBUTING, the pull request template, the
GitHub upload checklist, and first-run docs with
`uv --no-config run --frozen ...`. The public bug report issue template still
shows stale verification placeholder commands:

- `uv run pytest`
- `uv run ruff check .`
- `uv run ruff format --check .`

That form can read user-level uv configuration and can rewrite `uv.lock` when a
mirror is configured locally. The issue template is user-facing and should not
teach a different verification style from the other GitHub-facing surfaces.

## Scope

In scope:

- Add `.github/ISSUE_TEMPLATE/bug_report.yml` to the docs drift guard for
  ruff/pytest verification command examples.
- Replace the bug report placeholder's ruff/pytest lines with
  `uv --no-config run --frozen ...`.
- Preserve `uv run fashion-radar doctor` as an ordinary local CLI example.
- Preserve `UV_NO_CONFIG=1 uv lock --check` in the bug report placeholder.

Out of scope:

- No runtime product behavior changes.
- No CLI behavior changes.
- No dependency changes.
- No `uv.lock` changes.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.
- No issue-template restructuring beyond the verification placeholder lines.

## Architecture

This is a documentation drift node:

1. `tests/test_cli_docs.py` gets a `BUG_REPORT_TEMPLATE` path constant.
2. `test_github_verification_surfaces_use_no_config_frozen_uv_run` reads the bug
   report template alongside the other GitHub-facing verification surfaces.
3. The test requires the no-config/frozen ruff and pytest command forms in the
   bug report template.
4. The stale verification command ban also scans the bug report template.
5. The test explicitly preserves the local `uv run fashion-radar doctor`
   example and `UV_NO_CONFIG=1 uv lock --check`.

## Expected Behavior

After implementation:

- `.github/ISSUE_TEMPLATE/bug_report.yml` shows:
  - `uv --no-config run --frozen pytest`
  - `uv --no-config run --frozen ruff check .`
  - `uv --no-config run --frozen ruff format --check .`
- `.github/ISSUE_TEMPLATE/bug_report.yml` still shows:
  - `uv run fashion-radar doctor`
  - `UV_NO_CONFIG=1 uv lock --check`
- `tests/test_cli_docs.py` fails if any scanned GitHub-facing verification
  surface reintroduces `uv run pytest`, `uv run ruff check .`, or
  `uv run ruff format --check .`.

## Risks

- The stale command scan is intentionally exact-string based so it does not
  reject ordinary local CLI examples such as `uv run fashion-radar doctor`.
- The issue template is YAML text. This stage should keep indentation and
  multi-line placeholder formatting unchanged.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
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
```
