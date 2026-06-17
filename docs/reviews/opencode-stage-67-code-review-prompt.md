Review Stage 67 external-tool-workflow readiness preflight implementation in
/home/ubuntu/fashion-radar.

Scope:
- `external-tool-workflow` now prints one early `check_external_tool_readiness`
  step pointing to `external-tool-readiness`.
- `external-tool-workflow` must remain print-only and must not call readiness,
  inspect directories, read handoff files, open SQLite, or execute generated
  commands.
- `external-tool-readiness` semantics should remain unchanged.
- Tests/docs/smoke should be updated consistently for the 12-step workflow.

Review changed files:
- src/fashion_radar/external_tool_workflow.py
- tests/test_external_tool_workflow.py
- tests/test_cli.py
- scripts/check_first_run_smoke.py
- tests/test_first_run_smoke.py
- tests/test_cli_docs.py
- README.md
- docs/cli-reference.md
- docs/community-signal-import.md
- docs/community-signal-quality.md
- docs/source-boundaries.md
- docs/architecture.md
- docs/github-upload-checklist.md
- AGENTS.md
- CHANGELOG.md
- docs/superpowers/specs/2026-06-17-stage-67-external-tool-workflow-readiness-preflight-design.md
- docs/superpowers/plans/2026-06-17-stage-67-external-tool-workflow-readiness-preflight-plan.md

Verification already run before this review:
- `uv --no-config run --frozen pytest tests/test_external_tool_workflow.py tests/test_external_tool_readiness.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q` -> 420 passed
- `uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "external_tool_workflow or external_tool_readiness or upload_checklist"` -> 9 passed
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or run_first_run_flow"` -> 3 passed
- `uv --no-config run --frozen ruff check src/fashion_radar/external_tool_workflow.py tests/test_external_tool_workflow.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py` -> passed
- `uv --no-config run --frozen ruff format --check src/fashion_radar/external_tool_workflow.py tests/test_external_tool_workflow.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py` -> passed
- `uv --no-config run --frozen python scripts/check_release_hygiene.py` -> passed
- `uv --no-config run --frozen pytest` -> 1098 passed
- `git diff --check` -> passed

Return only Critical or Important findings, plus blocking test gaps.
