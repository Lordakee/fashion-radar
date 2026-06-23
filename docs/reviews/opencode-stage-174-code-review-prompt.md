# Stage 174 Code Review Prompt

Review the Stage 174 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree. If you run verification, limit it to the focused
commands listed below and return one final review body.
Start the response exactly with:

# Stage 174 Code Review

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
- Stage 174 spec, plan, plan-review prompt, and plan-review artifact.

Scope boundaries:

- Docs/test-only.
- No changes to `scripts/check_first_run_smoke.py`.
- No changes to `tests/test_first_run_smoke.py`.
- No changes to runtime CLI commands, external-tool payloads, adapters,
  templates, workflows, readiness builders, install hints, or mirror hints.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, API keys, login, cookies, monitoring, scheduling, demand
  proof, ranking, coverage verification, or compliance-review product feature.

Plan review history:

- `docs/reviews/opencode-stage-174-plan-review.md`
  - No critical findings.
  - No important findings.
  - Minor notes only: small redundancy between first-run and CLI docs tests,
    ensure the identical replacement lands in both README and first-run guide,
    and remember README drift is caught by the shared CLI docs test.

Independent read-only subagent check:

- A Codex explorer reviewed the current uncommitted Stage 174 diff and reported
  no blockers.
- It confirmed the Stage 174 spec names the four validated surfaces, README and
  `docs/first-run.md` mirror them, and the tests pin the four command fragments
  plus local/no-platform boundary fragments without overreach.
- The subagent did not edit files and did not run tests.

RED/GREEN evidence:

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

Review questions:

1. Does the implementation meet the Stage 174 objective?
2. Do the README and detailed first-run guide accurately name all four
   external-tool JSON contract surfaces validated by the smoke?
3. Are the docs/tests narrowly scoped without implying Fashion Radar runs
   upstream external/community tools, calls platform APIs, performs source
   acquisition, manages MCP servers, logs in, stores credentials, or verifies
   platform coverage?
4. Did any out-of-scope runtime, smoke-script, payload, adapter, template,
   workflow, readiness, install-hint, mirror-hint, connector,
   source-acquisition, ranking, or compliance-review behavior change slip in?
5. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
