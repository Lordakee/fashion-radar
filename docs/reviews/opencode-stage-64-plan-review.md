I'll review the Stage 64 plan. Let me start by reading the design and plan documents along with key reference files.
Now let me read the plan and key reference files in parallel.
Now let me read the remaining reference files including the CLI, smoke script, and key test files.
Let me examine the CLI to verify the wiring patterns and the symbols referenced in tests.
Let me read the relevant CLI sections to verify the test monkeypatch symbols and option aliases exist.
Let me read the existing external-tool-template command and the community-handoff-workflow command to verify the as_of guard pattern and structure.
Let me verify the test_cli.py patterns: the `cli_module` alias and existing external-tool tests.
Let me search specifically within test_cli.py for the relevant patterns.
Let me read the existing no-side-effect test for community-handoff-workflow to compare patterns with the plan's proposed guard test.
Let me read the existing external-tool-template print-only test to compare approaches.
Let me check the existing Stage 62/63 docs-drift test to compare the boundary-term stringency, and verify the smoke script's helper function names.
The smoke helper mismatch is confirmed. Let me read the existing Stage 62/63 docs-drift tests to confirm the precedent for the new test's stringency.
Let me read the existing external-tool-adapters CLI test (line 558) to check how it asserts quoted tmp_path-based paths.
I need to verify the plan against existing repo patterns. Let me investigate key dependencies.
I found a likely bug. Let me verify the smoke test fake-command pattern and other details.
I have enough to assess. Let me cross-check the smoke-test positional index concern one more time.
## Verdict: CHANGES REQUIRED

## Critical
- None.

## Important
1. **Smoke validator test/impl signature mismatch (Task 3 Step 1 vs Step 3).** The Step 1 test calls `check_first_run_smoke.validate_external_tool_workflow(json.dumps(payload), label="external-tool-workflow")`, but the Step 3 implementation signature is `def validate_external_tool_workflow(command_name: str, payload: Any) -> None:` and the body calls `payload.get(...)`, `list(payload)`, etc. The test as written (a) passes a JSON *string* where a dict is required, (b) supplies an unknown `label=` kwarg (TypeError), and (c) omits the positional `command_name`. The test cannot pass against the specified function — the existing validators (`validate_external_tool_adapters`, `validate_external_tool_template`) confirm the canonical shape is `("name", payload_dict)`. Fix the test call to `validate_external_tool_workflow("external-tool-workflow", payload)`.

2. **Fake-command positional index shift is unaddressed (Task 3).** The new `run_cli("external-tool-workflow", ...)` invocation is to be inserted near the adapter/template calls (between `captured[4]` and the current `captured[5]`). Existing assertions at `tests/test_first_run_smoke.py:1390,1392,1400,1403,1404,1405` use hard-coded indices (`captured[3]`, `captured[4]`, `captured[16]`..`captured[19]`) that will all shift by +1 once the new command is captured. The plan's Task 3 Step 1 only drops a list of arg strings without specifying the new captured index or acknowledging that downstream `captured[N]` assertions and the `first_run_flow` "no `collect/run/dashboard`" guard set must be renumbered/updated.

## Minor
- The builder re-implements the `adapter_by_id` + `KeyError → ValueError("Unknown external tool adapter: ...")` lookup that already lives in `filter_external_tool_adapter_registry` (`src/fashion_radar/external_tool_adapters.py:243`). Reusing it would keep behavior identical for free.
- Design says `--config-dir`/`--data-dir` carry help text, but the plan wires them via the shared option objects which have no `help=`. Cosmetic doc drift only.
- Builder's `pattern_text = (pattern or adapter.recommended_pattern).strip() or adapter.recommended_pattern` is more defensive than the design needs (the CLI never sends blank `--pattern`), but harmless.

## Rationale
Scope, boundaries, contract version, key order, step list, adapter defaults (`instaloader`, `rednote_mcp`, `x_search_export`, `generic_community_export`), shell-quoting via `shlex.join`, `parse_datetime_utc` error path, all referenced CLI symbols (`CONFIG_DIR_OPTION`, `DATA_DIR_OPTION`, `ManualSignalInputFormat`, `DEFAULT_ADAPTER_AS_OF`, `DEFAULT_EXPORT_DIRECTORY`), all `cli_module.*` side-effect targets, and the smoke-script helpers (`SmokeError`, `assert_equal`, `validate_json_output`, `run_cli`, `AS_OF`) all check out against the repo. JSON is explicitly workflow metadata, not importable handoff rows, preserving the `external-tool-template` responsibility split required by AGENTS.md. No platform-collection / side-effect gap was found in the design.

However, two instruction-level defects in Task 3 (the validator test signature bug and the unhandled `captured[N]` renumbering) each force the implementer to deviate from the plan as written in order to get a green verification step. Per the review criteria ("a test or implementation instruction that is clearly impossible against existing repo patterns"), these must be corrected in the plan before coding begins.
Let me verify the plan's assumptions against the actual repo patterns.
Let me verify the `smoke` import alias used in the test file matches what the plan references.
Both blockers verified against the current plan and existing test scaffolding.

- **Blocker 1 (validator signature):** Fixed. Plan line 1016 calls `smoke.validate_external_tool_workflow("external-tool-workflow", payload)` — `(command_name, payload)` positional order, no `json.dumps`, no `label=` kwarg. Matches validator signature at plan line 1034 `validate_external_tool_workflow(command_name: str, payload: Any)`. The `smoke` alias is already the established import in `tests/test_first_run_smoke.py`.
- **Blocker 2 (fake payload / captured indices):** Fixed.
  - `external_tool_workflow_payload()` fixture added at plan lines 1108–1243; `stdout_by_command["external-tool-workflow"] = json.dumps(external_tool_workflow_payload())` at plan lines 1275–1276.
  - Captured command-name insertion after `external-tool-template` specified at lines 1277–1278; current file has `external-tool-adapters`/`external-tool-template` at `captured[3]`/`captured[4]`, so `captured[5]` is correct (plan lines 1285–1300).
  - Current file shifts 4 directory checks from `captured[16..19]` → `captured[17..20]` (plan lines 1307–1312), matching the one-slot insert.
  - Both the first-run invocation (plan lines 1255–1262) and the `captured[5]` assertion (plan lines 1290–1294) use `context.exports_dir`/`context.config_dir`/`context.data_dir`.

No new Critical/Important regressions introduced. Both the validator-test payload (lines 961–989) and the fake-stdout payload (lines 1108–1243) independently satisfy the validator's contract-version, step-name, suggested-effect, command-token, and boundary checks.

---

- **Verdict:** APPROVED FOR STAGE 64 IMPLEMENTATION
- **Critical:** None
- **Important:** None
- **Minor:** None
- **Rationale:** Both previously identified Important blockers are fully resolved and consistent with the existing `tests/test_first_run_smoke.py` structure (captured indices, `stdout_by_command` shape, `smoke.` validator-call convention). The fixes do not introduce any new Critical or Important issue.
