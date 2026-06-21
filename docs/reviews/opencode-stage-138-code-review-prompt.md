Review the Stage 138 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Harden `external-tool-readiness` first-run smoke payload validation by exact
  argv-checking the five readiness step commands that were previously not
  covered.
- Reuse existing `validate_expected_external_tool_command()` and its
  `shlex.split()` exact argv comparison.
- Keep the change validation-only with no CLI runtime behavior changes.

Files changed:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 138 design/plan/review artifacts

Review focus:
1. Do the new tests prove the previous validator accepted command drift for
   `inspect_adapter_registry`, `print_adapter_template_json`,
   `print_signal_profile`, `lint_export_directory`, and
   `review_handoff_readiness`?
2. Does `validate_external_tool_readiness()` now exact argv-check all five
   previously unguarded step commands?
3. Are the new expected argv values derived from payload fields (`adapter_id`,
   `directory`, `config_dir`, `data_dir`, `as_of`, `input_format`, `pattern`,
   `source_name`) instead of hardcoded first-run paths?
4. Are existing workflow and dry-run exact checks plus step-count, step-name,
   step-effect, checks, boundary, install-hint, and forbidden-scope validation
   preserved?
5. Does the stage avoid CLI runtime behavior changes, generated command
   execution, PATH lookup changes, directory inspection, handoff file reads,
   import behavior changes, SQLite behavior changes, artifact creation,
   dependency changes, `uv.lock`, connectors, scraping, browser automation,
   platform APIs, account/session/cookie/token behavior, media downloads,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Verification already run:
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_readiness_rejects_remaining_step_command_argv_drift -q`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness or external_tool_workflow or external_tool_adapters"`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q`
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- `git diff --check`

Return:
Start with `# Stage 138 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
