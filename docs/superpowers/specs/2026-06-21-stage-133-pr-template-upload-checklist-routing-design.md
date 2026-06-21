# Stage 133 PR Template Upload Checklist Routing Design

## Objective

Route pull request authors from the PR template to the canonical GitHub upload
checklist for conditional smoke and upload verification.

## Problem

The pull request template already lists the common local verification commands
and includes focused conditional checks for packaging/templates and
dashboard/dependency changes. It does not point contributors to the full
`docs/github-upload-checklist.md` gate.

`CONTRIBUTING.md` already routes conditional packaging, template, dashboard, and
optional dependency smoke checks to the upload checklist. The PR template should
do the same without duplicating that checklist.

## Scope

In scope:

- Add a short PR template `Verification` checklist line that links to
  `docs/github-upload-checklist.md` for the full upload/package smoke gate.
- Add a focused docs test proving the PR template `Verification` section routes
  conditional smoke/upload verification to the upload checklist.
- Keep the PR template concise and preserve the existing package and dashboard
  checkboxes.

Out of scope:

- No CI changes.
- No upload checklist content changes.
- No package archive checker changes.
- No runtime product behavior changes.
- No dependencies or `uv.lock` changes.
- No README, CONTRIBUTING, release hygiene, connector, scraping, browser
  automation, platform API, monitoring, scheduling, source acquisition, demand
  proof, ranking, coverage verification, or compliance/audit product behavior
  changes.

## Architecture

This is a docs parity node:

1. `tests/test_cli_docs.py` gets one test near the existing PR template tests.
   It extracts the PR template `Verification` section, uses the existing
   `_assert_markdown_link_to_path()` helper to allow either
   `docs/github-upload-checklist.md` or `../docs/github-upload-checklist.md`,
   and asserts the surrounding text ties the link to the full upload/package
   smoke gate.
2. `.github/pull_request_template.md` gets one concise checklist item after the
   conditional packaging and dashboard bullets:
   `If preparing a GitHub upload or package smoke gate, follow
   [docs/github-upload-checklist.md](../docs/github-upload-checklist.md).`
3. Stage 133 review artifacts record the plan and code review without including
   credentials or copy-pasteable auth headers.

## Expected Behavior

After implementation:

- PR authors see the usual local verification commands in the PR template.
- PR authors also get a direct link to the full GitHub upload checklist when
  preparing an upload or package smoke gate.
- Tests fail if the PR template loses the upload checklist routing.
- The PR template does not duplicate the full upload checklist.

## Risks

- Link path form can be brittle because the template lives under `.github/`.
  The test should use `_assert_markdown_link_to_path()` instead of asserting a
  single path spelling.
- The PR template should stay concise. This stage adds a pointer, not another
  long command block.
- Stage review artifacts are now scanned by release hygiene while untracked, so
  prompts and reviews must not contain credential-shaped strings or auth-header
  examples.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_pull_request_template_routes_conditional_smokes_to_upload_checklist -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "pull_request_template_routes_conditional_smokes_to_upload_checklist or pull_request_template_package_smoke_uses_temp_build_archive_checker or contributing_and_pr_template_include_release_hygiene_and_source_smoke"
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
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
