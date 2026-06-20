Review the Stage 128 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `docs/cli-reference.md` support sentences for
  `external-tool-workflow` and `external-tool-readiness` with actual command
  help.
- Keep the change docs/test-only.

Design and plan:
- `docs/superpowers/specs/2026-06-20-stage-128-external-tool-cli-reference-option-parity-design.md`
- `docs/superpowers/plans/2026-06-20-stage-128-external-tool-cli-reference-option-parity-plan.md`
- `docs/reviews/opencode-stage-128-plan-review.md`

Files changed:
- `docs/cli-reference.md`
- `tests/test_cli_docs.py`
- Stage 128 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 128 design and plan?
2. Does the docs test parse only the relevant CLI reference bullets and
   cross-check option names against Typer help?
3. Does readiness wording remain local read-only and avoid implying directory
   inspection or file validation?
4. Does the stage avoid runtime CLI behavior, dependencies, lockfile,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

Verified locally before review:
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_cli_reference_external_tool_option_parity -q`
- `uv --no-config run --frozen pytest tests/test_cli_docs.py -k "external_tool_option_parity or external_tool_workflow_docs_include_examples_and_steps or external_tool_readiness_upload_checklist_help_loop_and_smoke" -q`
- `uv --no-config run --frozen pytest tests/test_cli.py -k "external_tool_workflow_help_lists_options or external_tool_readiness_help_lists_options or external_tool_workflow_command_applies_overrides or external_tool_readiness_command_applies_overrides" -q`
- `uv --no-config run --frozen ruff check tests/test_cli_docs.py`
- `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py`
- `git diff --check`

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
