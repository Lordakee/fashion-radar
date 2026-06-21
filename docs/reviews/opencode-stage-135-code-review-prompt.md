Review the Stage 135 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Harden first-run smoke validation for external/community tool workflow
  command shapes by comparing parsed shell argv lists exactly.
- Keep expected path values derived from payload fields so temporary first-run
  smoke directories remain valid.
- Keep this validation-only with no CLI runtime behavior changes.

Files changed:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 135 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 135 design and plan?
2. Do the RED tests prove current substring checks were too weak?
3. Does the helper use `shlex.split()` and exact argv comparison rather than
   direct string equality?
4. Are expected path arguments derived from payload values instead of hardcoded
   `exports`, `configs`, and `data`?
5. Does the stage avoid runtime CLI behavior changes, docs wording changes,
   package/archive checker changes, dependencies, `uv.lock`, connectors,
   scraping, browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, generated command
   execution, PATH lookup behavior changes, import behavior, SQLite behavior,
   file-read behavior, artifact creation behavior, and compliance/audit product
   behavior?

Verification already run:
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_workflow_rejects_extra_readiness_command_flag tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_wrong_workflow_output_format tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_wrong_dry_run_input_format -q`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness or external_tool_adapters"`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q`
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- `git diff --check`

Return:
Start with `# Stage 135 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
