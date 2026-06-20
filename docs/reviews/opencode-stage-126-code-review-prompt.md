Review the Stage 126 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align user-facing community handoff command sequences with the canonical
  local order: lint directory, preview candidates, readiness check, dry-run
  import, import, and imported review.
- Keep the change docs/test-only.

Design and plan:
- `docs/superpowers/specs/2026-06-20-stage-126-community-handoff-order-docs-design.md`
- `docs/superpowers/plans/2026-06-20-stage-126-community-handoff-order-docs-plan.md`
- `docs/reviews/opencode-stage-126-plan-review.md`
- `docs/reviews/opencode-stage-126-plan-rereview.md`

Files changed:
- `README.md`
- `docs/community-signal-quality.md`
- `docs/architecture.md`
- `tests/test_cli_docs.py`
- Stage 126 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 126 design and plan?
2. Do the named user docs show `community-handoff-check-dir` after
   `community-candidates-dir` and before `import-signals-dir`?
3. Is the regression test targeted to named sections instead of a brittle
   global command order?
4. Does the stage avoid runtime, CLI, dependency, connector, scraping, browser
   automation, platform API, monitoring, scheduling, source acquisition, demand
   proof, ranking, coverage verification, and compliance/audit product
   behavior?

Verified locally before review:
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_user_docs_keep_community_handoff_readiness_after_preview_before_import -q`
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_user_docs_keep_community_handoff_readiness_after_preview_before_import tests/test_cli_docs.py::test_community_handoff_check_dir_docs_are_linked_and_bounded tests/test_cli_docs.py::test_community_signal_import_doc_keeps_profile_recommended_command_order tests/test_community_handoff_workflow.py::test_build_community_handoff_workflow_returns_deterministic_steps tests/test_community_signal_profile.py::test_profile_recommended_commands_keep_directory_handoff_sequence tests/test_external_tool_adapters.py tests/test_external_tool_contract_parity.py -q`
- `uv --no-config run --frozen ruff check tests/test_cli_docs.py`
- `uv --no-config run --frozen ruff format --check tests/test_cli_docs.py`
- `git diff --check`

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
