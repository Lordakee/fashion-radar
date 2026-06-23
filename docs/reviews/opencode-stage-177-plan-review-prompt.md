# Stage 177 Plan Review Prompt

Review the Stage 177 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
Start the response exactly with:

# Stage 177 Plan Review

Objective:

Keep `docs/github-upload-checklist.md` aligned with README and
`docs/first-run.md` by naming every local external-tool JSON contract surface
that the automated first-run smoke already validates.

Files to review:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-24-stage-177-upload-checklist-external-tool-smoke-parity-design.md`
- `docs/superpowers/plans/2026-06-24-stage-177-upload-checklist-external-tool-smoke-parity-plan.md`
- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/first-run.md`
- `scripts/check_first_run_smoke.py`

Scope boundaries:

- Docs/test-only.
- Keep runtime smoke logic, first-run smoke fixture behavior, CLI behavior,
  payload shapes, external-tool adapter/template/workflow/readiness behavior,
  install hints, mirror hints, dependency manifests, and `uv.lock` unchanged.
- Clarify only the GitHub upload checklist package smoke section.
- No source acquisition, connectors, scraping, browser automation, platform
  APIs, MCP execution, login, cookies, monitoring, scheduling, demand proof,
  ranking, coverage verification, or compliance-review product feature.

Planned implementation:

1. Extend `test_upload_checklist_documents_first_run_smoke_boundary` so it
   requires every phrase in `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES`.
2. Run the focused test before docs updates and confirm it fails because the
   upload checklist currently omits the external-tool JSON contract smoke claim.
3. Add one concise paragraph in `docs/github-upload-checklist.md` saying the
   automated first-run smoke validates `external-tool-adapters --format json`
   across all eight adapters plus the `rednote_mcp` `external-tool-template`,
   `external-tool-workflow`, and `external-tool-readiness` JSON outputs.
4. Keep the wording explicit that these checks are local command-output
   contract checks only and do not run adapters or upstream
   external/community tools, call platform APIs, or perform source acquisition.
5. Run focused tests/lint, code review, full release gate, release review,
   commit, and push.

Review questions:

1. Is this stage appropriately scoped and safe?
2. Does the plan satisfy the project boundary rules in `AGENTS.md`?
3. Is reusing `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` the right test design?
4. Does the proposed checklist wording accurately match the first-run smoke
   script and avoid implying live collection or platform coverage?
5. Did any out-of-scope runtime, smoke-script, payload, adapter, source
   acquisition, ranking, coverage-verification, install-hint, mirror-hint,
   dependency, lockfile, or compliance-review behavior slip into the plan?
6. Are there any critical or important planning findings before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Plan Assessment
- Verdict
