# Stage 115 Plan Rereview Prompt

You are rereviewing the Stage 115 plan after prior opencode findings were
addressed.

Repository: `/home/ubuntu/fashion-radar`

Review target:

- Design: `docs/superpowers/specs/2026-06-19-stage-115-xpoz-adapter-metadata-design.md`
- Plan: `docs/superpowers/plans/2026-06-19-stage-115-xpoz-adapter-metadata-plan.md`

Prior blocking findings to verify:

1. `tests/test_external_tool_templates.py::test_template_collection_table_renderer_includes_each_full_template`
   must be explicitly covered for `Templates: 8`, `Adapter 8:`, and final
   `generic_community_export`.
2. `tests/test_first_run_smoke.py::EXTERNAL_TOOL_ADAPTER_CASES` must be
   explicitly covered with an `xpoz_mcp` tuple.
3. README, `docs/first-run.md`, and `tests/test_cli_docs.py` must update the
   "all seven adapters" phrase to "all eight adapters".
4. `tests/test_cli.py::test_external_tool_template_command_prints_all_adapters_when_unfiltered`
   must be explicitly covered for the unfiltered template item count `14 -> 16`
   and included in focused RED/GREEN selections.

Please only answer:

- Whether the above four blockers are now covered.
- Whether any new Critical or Important blockers remain before implementation.
- Minor notes only if they materially reduce implementation risk.

Scope reminder:

- `platform_label="community"` is intentional for this stage.
- `command=None` / `not_applicable` readiness is intentional.
- Do not ask for scraper, connector, MCP execution, API client, schema, dependency,
  lockfile, compliance/audit/legal-review, dashboard, importer, scoring, or report changes.
