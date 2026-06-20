# Stage 123 Verification Command Parity Design

## Objective

Align CI, contributor, pull request, and GitHub upload verification commands
with the project practice that agent-run verification should use
`uv --no-config run --frozen ...`.

## Problem

The repository already documents the verification practice in `AGENTS.md` and
the upload checklist, but several GitHub-facing command blocks still use plain
`uv run` for tests and lint:

- `.github/workflows/ci.yml`
- `README.md`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- `docs/github-upload-checklist.md`
- `docs/first-run.md`

Plain `uv run` can read user-level uv config and can rewrite `uv.lock` when
mirror configuration is present. That already caused a local `uv.lock` rewrite
during Stage 122 worker verification and had to be restored before commit.

## Scope

In scope:

- Replace release/agent/CI verification commands with
  `uv --no-config run --frozen ...`.
- Use `uv --no-config build` for release build commands in CI/upload docs.
- Update README and first-run automated smoke examples that are pinned by docs
  tests.
- Preserve `UV_NO_CONFIG=1 uv lock --check` and locked sync commands where they
  are already explicit environment isolation commands.
- Add tests that pin the command parity in CI, contributor docs, the pull
  request template, and the upload checklist.

Out of scope:

- No dependency changes.
- No `uv.lock` changes.
- No runtime, CLI, collector, dashboard, report, source acquisition, connector,
  scraping, browser automation, platform API, monitoring, scheduling, demand
  proof, ranking, coverage verification, or compliance/audit product behavior.
- No removal of mirror install examples. Mirror-backed installs remain local
  install aids only.
- No replacement of ordinary local workflow examples such as
  `uv run fashion-radar ...`.

## Architecture

This is a documentation and CI-command parity node:

1. A docs test in `tests/test_cli_docs.py` extracts the verification surfaces
   and checks the release/test/lint command forms.
2. `.github/workflows/ci.yml` switches test, lint, smoke, archive-check, and
   release-hygiene commands to no-config/frozen command forms.
3. `CONTRIBUTING.md`, `.github/pull_request_template.md`, and
   `docs/github-upload-checklist.md` use the same verification commands.

The test intentionally does not reject `uv run fashion-radar ...` examples
because those are normal local workflow examples, not release verification
commands.

## Tech Stack

- Python 3.11
- pytest text-based documentation tests
- GitHub Actions YAML edited as plain text
- uv command-line options

## Files

- Modify `.github/workflows/ci.yml`
- Modify `README.md`
- Modify `CONTRIBUTING.md`
- Modify `.github/pull_request_template.md`
- Modify `docs/github-upload-checklist.md`
- Modify `docs/first-run.md`
- Modify `tests/test_cli_docs.py`

## Expected Behavior

After implementation:

- CI release hygiene command uses
  `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`.
- CI first-run sample smoke command uses
  `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`.
- CI lint, format, and tests use `uv --no-config run --frozen ...`.
- CI package archive checker uses
  `uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"`.
- CI and upload checklist release builds use `uv --no-config build`.
- README and first-run automated source smoke examples use
  `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`.
- README Development verification commands use no-config/frozen command forms.
- Contributor and PR verification command blocks use no-config/frozen commands
  for ruff and pytest.
- Ordinary local usage examples continue to use `uv run fashion-radar ...`.

## Risks

- Some docs tests already assert `UV_NO_CONFIG=1 uv run ...` for first-run and
  package archive commands. Those tests must be updated in the same stage.
- Changing local workflow examples would make normal usage noisier. The test
  should target verification sections rather than every `uv run` occurrence.
- GitHub Actions already runs after a locked sync, so `uv --no-config run
  --frozen` should be compatible. The stage must verify locally and then rely
  on pushed CI for the workflow file.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "no_config or first_run_smoke or package_archive"
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
