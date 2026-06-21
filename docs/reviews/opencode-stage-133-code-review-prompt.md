Review the Stage 133 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Route PR authors from `.github/pull_request_template.md` to the canonical
  `docs/github-upload-checklist.md` for conditional smoke/upload verification.
- Keep the PR template concise and avoid duplicating the full upload checklist.
- Keep the change docs/test-only.

Files changed:
- `.github/pull_request_template.md`
- `tests/test_cli_docs.py`
- Stage 133 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 133 design and plan?
2. Does the PR template `Verification` section link to
   `docs/github-upload-checklist.md` for the GitHub upload or package smoke
   gate?
3. Does the test use `_assert_markdown_link_to_path()` instead of overfitting a
   single link path spelling?
4. Does the PR template avoid duplicating the full upload checklist?
5. Does the stage avoid CI changes, upload checklist content changes, package
   checker behavior changes, runtime product behavior changes, dependencies,
   `uv.lock`, README/CONTRIBUTING changes, release hygiene changes, connectors,
   scraping, browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Verification already completed:
- `test_pull_request_template_routes_conditional_smokes_to_upload_checklist`
  failed before the PR template link was added.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_pull_request_template_routes_conditional_smokes_to_upload_checklist tests/test_cli_docs.py::test_pull_request_template_package_smoke_uses_temp_build_archive_checker tests/test_cli_docs.py::test_contributing_and_pr_template_include_release_hygiene_and_source_smoke -q` passed.
- `uv --no-config run --frozen ruff check tests/test_cli_docs.py` passed.
- `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py` passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .` passed.
- `git diff --check` passed.

Return:
Start with `# Stage 133 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
