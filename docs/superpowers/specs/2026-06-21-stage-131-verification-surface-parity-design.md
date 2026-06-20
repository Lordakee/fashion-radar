# Stage 131 Verification Surface Parity Design

## Objective

Align contributor-facing verification surfaces so `CONTRIBUTING.md` and the
pull request template both require the local release hygiene gate and the
source-checkout first-run smoke gate that CI and the upload checklist already
treat as standard verification.

## Problem

CI and the upload checklist already require:

- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`

But `CONTRIBUTING.md` and `.github/pull_request_template.md` omit these commands
from their main `Verification` sections. `tests/test_cli_docs.py` also scopes
the two commands to CI/checklist (and README/first-run docs for first-run
smoke), which lets the contributor-facing drift persist.

## Scope

In scope:

- Update `CONTRIBUTING.md` `Verification` commands to include:
  - `check_release_hygiene.py --repo-root .`
  - `check_first_run_smoke.py --repo-root .`
- Update `.github/pull_request_template.md` `Verification` checklist to include
  the same two commands before conditional packaging/dashboard bullets.
- Extend docs tests so `CONTRIBUTING.md` and the PR template are required
  verification surfaces for these commands.
- Keep installed-wheel/package-smoke detail where it already belongs in the
  upload checklist and first-run docs.

Out of scope:

- No runtime product behavior changes.
- No CI behavior changes.
- No dependency changes.
- No `uv.lock` changes.
- No package archive checker behavior changes.
- No README development-block expansion.
- No connector, scraping, browser automation, platform API, monitoring,
  scheduling, source acquisition, demand proof, ranking, coverage verification,
  or compliance/audit product behavior.

## Architecture

This is a docs/test parity node:

1. Add a focused docs test that extracts the `Verification` sections from
   `CONTRIBUTING.md` and the PR template and asserts both contain:
   - `check_release_hygiene.py --repo-root .`
   - `check_first_run_smoke.py --repo-root .`
2. Update `test_github_verification_surfaces_use_no_config_frozen_uv_run` so
   the release hygiene command includes `contributing` and
   `pull_request_template`, and the source-checkout `check_first_run_smoke.py`
   command includes `contributing` and `pull_request_template` in addition to
   existing surfaces.
3. Update the two Markdown documents with concise command lines only; do not
   duplicate installed-wheel smoke walkthroughs from the upload checklist.

## Expected Behavior

After implementation:

- `CONTRIBUTING.md` and `.github/pull_request_template.md` both list the local
  release hygiene command and the source-checkout first-run smoke command in
  their `Verification` sections.
- The docs parity tests fail if either contributor-facing surface drops one of
  those commands.
- Existing CI/checklist/README/first-run smoke expectations remain unchanged.

## Risks

- The contributor-facing verification sections must stay concise. This stage
  should add only the two missing standard gates and keep packaging/dashboard
  detail delegated to existing conditional bullets and the upload checklist.
- README should remain a lighter development surface. This stage should not pull
  these commands into the README development block.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_contributing_and_pr_template_include_release_hygiene_and_source_smoke tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "contributing or github_verification_surfaces"
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
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
