# Stage 159 Release Review Prompt

Review the Stage 159 final working tree for Fashion Radar before GitHub upload.

Scope:

- Review artifact hygiene scanner in `scripts/check_release_hygiene.py`.
- Tests in `tests/test_release_hygiene.py`.
- Stage 159 spec, plan, plan review, plan rereview, code review, code rereview,
  and this release-review prompt.

Verification already run:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q` -> 1317 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .` -> First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .` -> Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .` -> passed.
- `uv --no-config run --frozen ruff format --check .` -> 142 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check` -> resolved successfully.
- `git diff --check` -> passed.
- `rg -n 'ghp_[A-Za-z0-9]+' .` -> no matches.
- `git config --get-all http.https://github.com/.extraheader` -> no output.

Review questions:

1. Are there any critical or important issues in the Stage 159 code, tests, or
   review artifacts?
2. Are the review artifacts clean completed review bodies with no live-capture
   stubs, tool-status lines, ANSI output, duplicated/truncated output, or empty
   output?
3. Is the change still process-only with no product/runtime/social collection,
   scraping, platform API, scheduling, monitoring, or compliance-review product
   behavior?
4. Is the full release gate evidence sufficient to commit and push?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
