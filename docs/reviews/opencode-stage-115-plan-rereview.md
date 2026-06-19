Let me verify the four blockers against the actual test file structures to confirm the snippets match.
Let me verify the existing test snippets match the plan's assumptions to ensure no implementation risk.
I found a potential critical issue. Let me check how `EXTERNAL_TOOL_ADAPTER_CASES` tuples are consumed — the existing tuples use a tuple for `upstream_tool_examples`, but the plan's XPOZ snippet uses a list.
Let me verify the `scripts/check_first_run_smoke.py` structure to confirm the plan's Step 7 snippet matches the existing `EXPECTED_EXTERNAL_TOOL_ADAPTERS` shape.
Let me verify the `test_external_tool_adapters_command_prints_json` expected-map shape and the `test_external_tool_contract_parity.py` shape to rule out implementation risk.
Let me check `test_external_tool_templates.py` for any other adapter-id or count pins the plan might miss, and check the existing collection test that the plan's Step 4 modifies.
Let me check `test_first_run_smoke.py` for any separate pinned adapter-id list the plan's Step 8 "catch-all" must cover.
Let me check the two other adapter-id/tuple lists in `test_first_run_smoke.py` (around lines 840 and 1230) to ensure the plan's Step 8 catch-all is sufficient.
I verified the plan against the actual test/source files. Here is the rereview.

## Prior blockers — all four covered

1. **`test_template_collection_table_renderer_includes_each_full_template`** — ✅ Covered by Task 1, Step 4b (plan:140-153). Explicitly asserts `"Templates: 8"`, `"Adapter 8:"`, and `"Adapter: generic_community_export"`, correctly replacing the current `"Templates: 7"`/`"Adapter 7:"` at `tests/test_external_tool_templates.py:232,244`.

2. **`EXTERNAL_TOOL_ADAPTER_CASES` xpoz_mcp tuple** — ✅ Covered by Task 1, Step 8 (plan:206-226). Adds the tuple before `generic_community_export`; `external_tool_adapters_payload()` derives its adapter list directly from this tuple (`test_first_run_smoke.py:706-714`), so no separate id list needs editing. I checked the two other `rednote_mcp`/tuple spots (lines 840, 1228-1232): they are a single-adapter drift probe and an intentionally 2-branch helper-parity parametrization — correctly left alone.

3. **"all seven adapters" → "all eight adapters"** — ✅ Covered in all three locations: README + `docs/first-run.md` (Task 3 Step 3, plan:334-348) and `tests/test_cli_docs.py::FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE` (Task 1 Step 9, plan:236-237; current phrase at `test_cli_docs.py:283-287`).

4. **Unfiltered template count `14 -> 16`** — ✅ Covered by Task 1 Step 6b (plan:170-183; current `len(payload["items"]) == 14` at `test_cli.py:744`), and the test is listed in both the RED selection (Task 1 Step 10, plan:250) and GREEN selection (Task 2 Step 3, plan:312).

## New Critical / Important blockers

None. Cross-checked the at-risk seams:
- `test_external_tool_contract_parity.py:99` requires `platform_label in profile.suggested_platform_labels` — `"community"` is already valid (`generic_community_export` uses it).
- `test_cli.py:619` unpacks `(platform_label, source_name, input_format, pattern)` — the plan's `("community", "XPOZ MCP Export", "json", "*.json")` matches.
- `test_external_tool_contract_parity.py:202` BANNED_COMMAND_TOKENS scan only inspects command strings; "API"/"MCP" appear only in description/install_hint text, never in the standard 9 handoff commands.
- Parity/readiness/workflow/template-iterating tests loop over `registry.adapters`, so they auto-cover xpoz once the registry entry is inserted in the correct slot (after `x_search_export`, before `generic_community_export`), as Task 2 Step 1 specifies.

## Minor (non-blocking, optional)

In Task 1 Step 8, the XPOZ tuple's last element is a list `["XPOZ MCP", "XPOZ Social Data API"]`, whereas all 7 existing tuples use a trailing tuple `(...)`. It is functionally identical because the consumer wraps it with `list(...)` at `test_first_run_smoke.py:694`, so this carries no implementation risk — aligning to a tuple would just keep the fixture stylistically uniform. Does not block implementation.

The plan is approved to proceed to implementation.
