# Stage 174 Release Review Prompt

Review the Stage 174 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to confirming the
evidence below and return one final review body.
Start the response exactly with:

# Stage 174 Release Review

Objective:

Make first-run documentation accurately describe every external-tool JSON
contract surface that the automated first-run smoke already validates.

Changed files:

- `tests/test_first_run_docs.py`
  - Adds `test_first_run_docs_name_external_tool_smoke_contracts`.
  - Pins the detailed first-run guide's "Installed-Wheel Smoke" section to the
    four external-tool JSON contract surfaces already validated by the smoke.
- `tests/test_cli_docs.py`
  - Replaces the old single adapter-registry smoke phrase with
    `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES`.
  - Applies the fragments to both README and detailed first-run guide docs
    guards.
- `README.md`
  - Expands the automated first-run smoke claim to name the adapter registry,
    rednote template, rednote workflow, and rednote readiness JSON contract
    checks.
  - Keeps the command-output-only / no-upstream-tool / no-platform-API /
    no-source-acquisition boundary.
- `docs/first-run.md`
  - Mirrors the README smoke claim in the "Installed-Wheel Smoke" section.
- Stage 174 spec, plan, plan-review prompt, plan-review artifact, code review
  prompt, and code review artifact.

Scope boundaries:

- Docs/test-only.
- No changes to `scripts/check_first_run_smoke.py`.
- No changes to `tests/test_first_run_smoke.py`.
- No changes to runtime CLI commands, external-tool payloads, adapters,
  templates, workflows, readiness builders, install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, API keys, login, cookies, monitoring, scheduling, demand
  proof, ranking, coverage verification, or compliance-review product feature.

Review history:

- `docs/reviews/opencode-stage-174-plan-review.md`
  - No critical findings.
  - No important findings.
  - Minor notes only: small redundancy between first-run and CLI docs tests,
    ensure the identical replacement lands in both README and first-run guide,
    and remember README drift is caught by the shared CLI docs test.
- `docs/reviews/opencode-stage-174-code-review.md`
  - No critical findings.
  - No important findings.
  - Minor notes only: overlap between the two docs tests, README parity relying
    on the shared CLI docs guard, and casing differences between phrase sets.
- A read-only Codex explorer reviewed the current uncommitted Stage 174 diff and
  reported no blockers. It confirmed the Stage 174 spec names the four
  validated surfaces, README and `docs/first-run.md` mirror them, and the tests
  pin the four command fragments plus local/no-platform boundary fragments
  without overreach.

Focused verification evidence:

- RED:
  - `uv --no-config run --frozen pytest tests/test_first_run_docs.py::test_first_run_docs_name_external_tool_smoke_contracts -q`
  - Result before docs updates: 1 failed because old docs lacked
    `automated first-run smoke also validates local external-tool json contracts`.
- RED:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q`
  - Result before docs updates: failed because README and first-run docs lacked
    the new external-tool smoke fragments.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_first_run_docs.py::test_first_run_docs_name_external_tool_smoke_contracts -q`
  - Result: 1 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_first_run_docs.py -q`
  - Result: 2 passed.
- GREEN:
  - `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_documents_manual_sample_flow_and_automated_smoke_boundary tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries -q`
  - Result: 2 passed.
- Related first-run smoke coverage:
  - `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -k "external_tool or deterministic_local_command_sequence" -q`
  - Result: 58 passed, 104 deselected.
- Installed smoke script:
  - `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- Focused lint:
  - `uv --no-config run --frozen ruff check tests/test_first_run_docs.py tests/test_cli_docs.py`
  - Result: All checks passed.
- Focused format:
  - `uv --no-config run --frozen ruff format --check tests/test_first_run_docs.py tests/test_cli_docs.py`
  - Result: 2 files already formatted.

Release gate evidence:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  - Result: 1370 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  - Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  - Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
  - Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
  - Result: 144 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  - Result: Resolved 84 packages in 7ms.
- `git diff --check`
  - Result: no output, exit 0.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
  - Result: no matches, exit 1.
- `git config --get-all http.https://github.com/.extraheader`
  - Result: no configured GitHub extraheader, exit 1.

Release review questions:

1. Is Stage 174 in scope and ready to commit?
2. Are the plan/code review artifacts clean and consistent with
   `docs/REVIEW_PROTOCOL.md`?
3. Is the release verification evidence sufficient for this docs/test-only
   stage?
4. Did any out-of-scope runtime, smoke-script, payload, adapter, template,
   workflow, readiness, install-hint, mirror-hint, connector,
   source-acquisition, ranking, or compliance-review behavior change slip in?
5. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
