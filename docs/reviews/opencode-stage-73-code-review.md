I'll review the Stage 73 implementation. Let me start by examining the actual changes and touched files.
Let me see the rest of the script and the test file.
Now let me see the test file and the spec/plan docs in parallel.
Now let me look at the design/plan docs and the runtime registry to verify the pinned expectations match.
Let me cross-check the runtime CLI command for `external-tool-adapters` to verify the `suggested_export_directory` value matches.
Let me verify a potential discrepancy I noticed. The runtime registry uses `DEFAULT_EXPORT_DIRECTORY = "./exports"` but the validator pins to `"exports"`. Let me check whether this would break the actual end-to-end smoke.
Good — `Path("./exports")` normalizes to `"exports"`, so that's consistent. Let me check the CLI tests and run the actual end-to-end smoke to confirm no real-world regression.
The CLI test confirms runtime emits `"exports"` (Path normalizes). Now let me run the actual smoke end-to-end against the real CLI to confirm no regression.
End-to-end smoke passes. Now let me run the focused tests, lint, and confirm no runtime files were touched.
Let me check the diff of the test file to ensure no negative coverage was lost in the refactor.
I have enough to complete the review. Here are my findings.

---

## Stage 73 Code Review

**Stance:** Code-review. **Verdict: No Critical or Important issues. Ready for commit.**

I independently confirmed the pinned values in `EXPECTED_EXTERNAL_TOOL_ADAPTERS` and `EXPECTED_EXTERNAL_TOOL_COMMAND_NAMES` match the runtime registry in `src/fashion_radar/external_tool_adapters.py:108-234` and `_recommended_commands:346-488` (all 7 adapters, all 9 command prefixes). I also ran the real end-to-end smoke (`scripts/check_first_run_smoke.py`) against the live CLI — it passed, not just the monkeypatched unit test.

### Answers to review questions

1. **Validates all seven adapters including later drift?** Yes. `validate_external_tool_adapters` (`scripts/check_first_run_smoke.py:535-642`) loops every adapter and pins per-adapter metadata + readiness flags. Negative tests at `tests/test_first_run_smoke.py:1361-1481` cover later-adapter id drift (`adapters[1]`), reorder, `xiaohongshu_crawler` platform_label drift, `adapters[1]` missing commands, and `adapters[1]` readiness `--input-format` drift.
2. **Fixture registry-like without importing runtime?** Yes. `external_tool_adapters_payload` (`tests/test_first_run_smoke.py:572-621`) is built from the parallel `EXTERNAL_TOOL_ADAPTER_CASES` tuple and uses `shlex.join` via `external_tool_command` (`:84-85`) so multi-word source names and glob patterns quote identically to runtime `_shell_command`. No `from fashion_radar.external_tool_adapters import ...` in the smoke script.
3. **Scope of static smoke checks appropriate?** Yes. Pins contract_version, execution_mode, adapter ids/order, the six public metadata fields, the exact nine `fashion-radar <cmd>` prefixes, single readiness command, and its `--adapter/--directory/--input-format/--pattern/--source-name/--format` values plus non-empty `--config-dir/--data-dir/--as-of`. Intentionally omits `description/upstream_tool_examples/field_mappings/boundaries` — parallel coverage exists in `tests/test_cli.py:536-640`.
4. **Altered sequencing / runtime / platform behavior?** No. `git diff --name-only HEAD` shows only `scripts/check_first_run_smoke.py` + `tests/test_first_run_smoke.py`; no `src/` changes. `run_first_run_flow` is byte-identical; `test_run_first_run_flow_uses_deterministic_local_command_sequence` still pins the same 22-command sequence.
5. **Critical/Important issues?** None.

### Verification re-run (independent)

- `uv pytest tests/test_first_run_smoke.py -q` → 52 passed
- `uv ruff check` + `ruff format --check` on both files → clean
- `python scripts/check_first_run_smoke.py` against real CLI → "First-run sample smoke passed."
- `Path("./exports")` normalizes to `"exports"`, so the smoke's pinned `"exports"` matches the runtime default `DEFAULT_EXPORT_DIRECTORY = "./exports"` (verified empirically).

### Minor notes (non-blocking)

- **M1 (pre-existing pattern):** Unlike `external_tool_template_payload`, `external_tool_workflow_payload`, and `external_tool_readiness_payload`, there is no direct `..._payload_matches_real_registry` test comparing `external_tool_adapters_payload()` to runtime `build_external_tool_adapter_registry(...).model_dump_json()`. Fixture-vs-runtime drift is caught indirectly via `tests/test_cli.py::test_external_tool_adapters_command_prints_json` plus the real smoke run, so it is defended — but a direct comparison test would localize drift faster. Not introduced by this stage; flagging only because this stage expanded the fixture most.
- **M2:** The single `test_validate_external_tool_adapters_requires_print_only_registry_contract` bundles ~15 negative cases sequentially (`tests/test_first_run_smoke.py:1345-1513`). A mid-test failure is slightly harder to localize than `pytest.mark.parametrize` cases, but the style is consistent with the rest of the file.
- **M3:** The validator does not pin adapter-level `description`/`upstream_tool_examples`/`field_mappings`/`boundaries` or registry-level `boundaries`. The fixture's generic `description` and `[source_name]` for `upstream_tool_examples` therefore intentionally diverge from runtime (e.g. runtime uses `["rednote-mcp"]`, fixture uses `["Rednote MCP Export"]`). This matches the design's "public metadata only" scope; just noting in case a future stage expects full fidelity.

### Scope compliance

No scraping, connectors, browser automation, platform APIs, login/cookie/session/token/proxy, CAPTCHA, media download, monitoring/scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review product behavior was introduced. Changes are confined to the static first-run smoke validator and its tests.
