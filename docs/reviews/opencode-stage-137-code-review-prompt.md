Review the Stage 137 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Harden `external-tool-workflow` first-run smoke payload validation by exact
  argv-checking the eight workflow step commands that were previously not
  covered.
- Reuse existing `validate_expected_external_tool_command()` and its
  `shlex.split()` exact argv comparison.
- Keep the change validation-only with no CLI runtime behavior changes.

Files changed:
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- Stage 137 design/plan/review artifacts

Review focus:
1. Do the new tests prove the previous validator accepted command drift for
   `print_signal_profile`, `print_handoff_manifest`,
   `print_handoff_workflow`, `preview_candidate_phrases`,
   `review_handoff_readiness`, `dry_run_directory_import`,
   `import_directory_signals`, and `print_post_import_review`?
2. Does `validate_external_tool_workflow()` now exact argv-check all eight
   previously unguarded step commands?
3. Are the new expected argv values derived from payload fields (`directory`,
   `input_format`, `pattern`, `config_dir`, `data_dir`, `as_of`,
   `source_name`) instead of hardcoded first-run paths?
4. Are existing registry, readiness, template, lint, step-count, step-name,
   import-effect, step-effect, and boundary checks preserved?
5. Does the stage avoid CLI runtime behavior changes, generated command
   execution, PATH lookup changes, directory inspection, handoff file reads,
   import behavior changes, SQLite behavior changes, artifact creation,
   dependency changes, `uv.lock`, connectors, scraping, browser automation,
   platform APIs, account/session/cookie/token behavior, media downloads,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Verification already run:
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift -q`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow or external_tool_readiness or external_tool_adapters"`
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q`
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- `git diff --check`

Return:
Start with `# Stage 137 Code Review`, then include:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
