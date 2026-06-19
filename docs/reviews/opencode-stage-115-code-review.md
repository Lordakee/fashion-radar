I'll review the Stage 115 changes. Let me start by examining the diff and relevant files.
Let me read the source files and tests in full context.
Now let me check the design/plan docs and tests in parallel.
Now let me look at the test and docs diffs in parallel.
Let me look at the prior plan rereview and full test files for context.
Let me look at the readiness test context and the contract parity test in full.
Let me look at the templates test and the full first-run smoke test in detail.
Let me check for any other places that might have drift — counts of adapters, command names, or other places referencing "seven", and inspect the smoke script.
Let me check the other parts of `test_first_run_smoke.py` that pin adapter lists/counts.
Let me verify the static fixture generator is data-driven from `EXTERNAL_TOOL_ADAPTER_CASES`.
Now let me run the verification commands from the prompt to confirm correctness, and inspect the actual XPOZ JSON output.
Let me verify the remaining CLI outputs (template, readiness, workflow) and the ruff checks.
Let me check the existing review artifacts and verify there's nothing missed in scope.
## Stage 115 Code Review

I reviewed the uncommitted diff against the design (`docs/superpowers/specs/2026-06-19-stage-115-xpoz-adapter-metadata-design.md`), the plan, the plan rereview, and the AGENTS.md scope boundaries. I also re-ran the verification commands.

### Verification re-run (all green)
- `pytest` focused suite: **174 passed**
- `external-tool-adapters --adapter xpoz_mcp --format json`: 9 standard commands, correct metadata
- `external-tool-template --adapter xpoz_mcp --format json`: 2 rows, `source_name="XPOZ MCP Export"`, `platform="community"`
- `external-tool-readiness --adapter xpoz_mcp --format json`: `checks[0].status=="not_applicable"`, `command==null`, `shutil.which` not invoked
- `external-tool-workflow --adapter xpoz_mcp --format json`: 12 steps, local handoff only
- `ruff check` / `ruff format --check`: clean; `git diff --check`: clean

### Correctness checks (all pass)
- **Registry order** at `external_tool_adapters.py:108-252` matches the required order exactly (`xpoz_mcp` between `x_search_export` and `generic_community_export`).
- **xpoz_mcp metadata** (`external_tool_adapters.py:216-233`) matches the design field-for-field: display/source name, platform label, format/pattern, upstream examples, description.
- **Readiness spec** at `external_tool_readiness.py:87-93` uses `command=None`, producing `not_applicable` without calling `which`, consistent with `x_search_export`/`tiktok_api`/`generic_community_export`.
- **Drift surfaces are all updated**:
  - `EXPECTED_ADAPTER_IDS` in `test_external_tool_adapters.py` + `test_external_tool_contract_parity.py`
  - `len == 8` adapter count + `len(items) == 16` template count (`test_external_tool_templates.py:146`, `test_cli.py:745`)
  - `"Templates: 8"` / `"Adapter 8:"` (`test_external_tool_templates.py:233,245`)
  - `EXPECTED_EXTERNAL_TOOL_ADAPTERS` + `EXPECTED_EXTERNAL_TOOL_ADAPTER_DETAILS` in `scripts/check_first_run_smoke.py:114,190-196`
  - `EXTERNAL_TOOL_ADAPTER_CASES` tuple in `test_first_run_smoke.py:127-138` (correctly uses a tuple, not a list — addresses the rereview's minor stylistic note)
  - CLI expected-map + docs matrix rows in `test_cli.py:563` and `test_cli_docs.py:283`
  - "seven" → "eight" prose in `README.md:345`, `docs/first-run.md:155`, and `FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE`
- **Auto-covering parity tests** iterate `registry.adapters`, so `xpoz_mcp` is automatically covered for: platform-label membership in `profile.suggested_platform_labels` (`"community"` already valid via `generic_community_export`), template ↔ adapter command parity, workflow/readiness command reuse, and the `BANNED_COMMAND_TOKENS` scan (no `api`/`mcp`/etc. tokens leak into the 9 standard handoff commands — they only appear in description/install_hint text).
- **Fixture fidelity** is enforced bidirectionally: `test_external_tool_adapters_payload_matches_real_registry` (`test_first_run_smoke.py:1226`) compares the static `external_tool_adapters_payload()` (data-driven from `EXTERNAL_TOOL_ADAPTER_CASES`) against the live registry `model_dump_json`, so any future drift in the new adapter's fields, command shape, or order will fail this test.
- **AGENTS.md scope boundaries** are respected: no connectors, scraping, MCP execution, API clients, schema/lockfile/dependency changes; the adapter inherits the standard print-only 9-command list with `external-tool-readiness` as the optional preflight at index 1.

### Findings

**Critical:** None.

**Important:** None.

**Minor (optional cleanup, non-blocking):**
1. `test_xpoz_mcp_adapter_has_expected_mapping_and_commands` omits the `list(adapter.model_dump(mode="json"))` key-order assertion that the neighboring `test_instaloader_adapter_has_expected_mapping_and_commands` includes. Not a real gap (model keys are shared across all adapters and the contract is implicitly covered by the registry-level test at `test_external_tool_adapters.py:39`), but adding it would keep the per-adapter tests uniform.
2. Line 147 uses `("XPOZ MCP Export")` parenthesized single-string form purely to mirror the instaloader test's multi-line `("...")` style. Cosmetic only; `ruff format` is happy either way.

The Stage 115 changes are correct, internally consistent, and free of drift risks in scope. Approved to commit.
