# Stage 174 Plan Review Prompt

Review the Stage 174 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 174 Plan Review

Objective:

Make first-run documentation accurately describe every external-tool JSON
contract surface that the automated first-run smoke already validates.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-174-first-run-external-tool-smoke-claim-parity-design.md`
- `docs/superpowers/plans/2026-06-23-stage-174-first-run-external-tool-smoke-claim-parity-plan.md`
- `README.md`
- `docs/first-run.md`
- `tests/test_first_run_docs.py`
- `tests/test_cli_docs.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Scope boundaries:

- Docs/test-only.
- Keep runtime smoke logic, first-run smoke fixture behavior, CLI behavior,
  payload shapes, external-tool adapter/template/workflow/readiness behavior,
  install hints, and mirror hints unchanged.
- Clarify only the first-run documentation's automated smoke claim in README
  and the detailed first-run guide.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, API keys, login, cookies, monitoring, scheduling, demand
  proof, ranking, coverage verification, or compliance-review product feature.

Planned implementation:

1. Add a RED docs test in `tests/test_first_run_docs.py`:
   `test_first_run_docs_name_external_tool_smoke_contracts`.
2. Update the shared first-run docs assertion in `tests/test_cli_docs.py` so the
   README and detailed first-run guide must both name the external-tool
   surfaces and boundary terms.
3. Run those tests before docs updates and confirm they fail because README and
   the detailed first-run guide currently name only the adapter registry JSON
   contract.
4. Update `README.md` and `docs/first-run.md` to say the automated first-run
   smoke validates `external-tool-adapters --format json` across all eight
   adapters plus the `rednote_mcp` `external-tool-template`,
   `external-tool-workflow`, and `external-tool-readiness` JSON outputs.
5. Keep the wording explicit that these checks are local command-output
   contract checks only and do not run adapters or upstream
   external/community tools, call platform APIs, or perform source acquisition.
6. Run focused docs/smoke checks, code review, full release gate, release
   review, commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Is the docs parity test useful without being too broad or brittle?
4. Does the proposed wording accurately match the first-run smoke script and
   avoid implying live collection or platform coverage?
5. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
