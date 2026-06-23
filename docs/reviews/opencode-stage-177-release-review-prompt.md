# Stage 177 Release Review Prompt

Review the Stage 177 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming the
evidence below and return one final review body.
Start the response exactly with:

# Stage 177 Release Review

Objective:

Keep `docs/github-upload-checklist.md` aligned with README and
`docs/first-run.md` by naming every local external-tool JSON contract surface
that the automated first-run smoke already validates.

Changed files:

- `tests/test_cli_docs.py`
  - Extends `test_upload_checklist_documents_first_run_smoke_boundary` to assert
    every phrase in `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES`.
- `docs/github-upload-checklist.md`
  - Adds the external-tool JSON contract smoke paragraph in the package smoke
    section.
- Stage 177 spec, plan, plan-review prompt, plan-review artifact, code review
  prompt, and code review artifact.

Scope boundaries:

- Docs/test-only.
- No changes to `README.md` or `docs/first-run.md`.
- No changes to `scripts/check_first_run_smoke.py`.
- No changes to `tests/test_first_run_smoke.py`.
- No changes to runtime CLI commands, external-tool payloads, adapters,
  templates, workflows, readiness builders, install hints, mirror hints,
  dependency manifests, or `uv.lock`.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, login, cookies, monitoring, scheduling, demand proof,
  ranking, coverage verification, or compliance-review product feature.

Review history:

- `docs/reviews/opencode-stage-177-plan-review.md`
  - No critical or important findings.
  - Minor notes only: phrase tuple guards normalized substrings rather than full
    sentence order, and ensure generated review artifacts exist before commit.
- `docs/reviews/opencode-stage-177-code-review.md`
  - No critical or important findings.
  - Minor notes only: same normalized-substring tradeoff and review artifact
    filing reminder.

Focused verification evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_upload_checklist_documents_first_run_smoke_boundary -q`
  - Result before docs update: failed because the upload checklist lacked
    `The automated first-run smoke also validates local external-tool JSON contracts`.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_upload_checklist_documents_first_run_smoke_boundary -q`
  - Result after docs update: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "upload_checklist or first_run_smoke"`
  - Result: 10 passed, 59 deselected.
- GREEN:
  - `uv --no-config run --frozen ruff check tests/test_cli_docs.py`
  - Result: All checks passed.
- GREEN:
  - `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py`
  - Result: 1 file already formatted.

Release gate evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1374 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - Result: 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Result: Resolved 84 packages.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches, exit 1.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no configured GitHub extraheader, exit 1.

Release review questions:

1. Is Stage 177 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this docs/test-only
   stage?
4. Did any out-of-scope runtime, smoke-script, payload, adapter, source
   acquisition, ranking, coverage-verification, install-hint, mirror-hint,
   dependency, or lockfile behavior slip in?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
