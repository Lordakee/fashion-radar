I'll review the Stage 72 plan. Let me start by reading the spec, plan, and current implementation in parallel.
Now let me examine the current implementation to verify the plan's expected values against actual code.
Let me verify the CLI defaults and check ruff rules (B023) and how `--directory` and `--as-of` are normalized.
Let me verify two subtle points: the Path normalization of `./exports` → `exports`, and the `ManualSignalFormat` JSON serialization, plus confirm no other tests touch this contract.
Let me check the existing `test_external_tool_adapters.py` to understand what's already covered at the model level, which affects scope redundancy.
## Stage 72 Plan Review

I verified the plan against `src/fashion_radar/external_tool_adapters.py`, the current `tests/test_cli.py:536-580`, the CLI defaults at `cli.py:678-712`, and the ruff config. All expected values were cross-checked at runtime (see verification below).

### Critical
None.

### Important
None.

### Minor

1. **Step 3 doesn't explicitly retire the old first-adapter readiness block.** Step 3 says "Replace the single first-adapter field mapping assertion" but the existing test (`tests/test_cli.py:557-580`) also contains a first-adapter readiness command block that becomes redundant once Step 5's per-adapter loop runs. The plan should state plainly: delete lines 557-580 when adding the loop, otherwise the implementer leaves a dead single-adapter block above the new loop.

2. **Overlap with existing model-level coverage is worth noting.** `tests/test_external_tool_adapters.py:46` already pins instaloader's full readiness flag contract via `model_dump`, and `:109` already loops all adapters for field-mapping consistency. The Stage 72 test's marginal value is CLI-invocation + `model_dump_json` serialization coverage, not the model contract. The plan/spec don't mention this; a one-line note would set reviewer expectations correctly.

3. **`--config-dir` / `--data-dir` only truthiness-checked.** Plan Step 5 mirrors the existing test's `assert flag_value(readiness_parts, "--config-dir")` without pinning values. Since all adapters share the same CLI defaults, you could cheaply strengthen with `== adapters[0]`'s readiness values to catch cross-adapter drift on those two flags too. Optional, not blocking.

4. **Tuple unpacking is positional-only.** `platform_label, source_name, input_format, pattern = expected_adapters[adapter_id]` silently misaligns if a tuple is reordered. A `NamedTuple` or inline comment would be more robust, but acceptable for a local test fixture.

### Review Question Answers

1. **Test-only and appropriately scoped?** Yes. Runtime changes are explicitly out-of-scope unless drift is revealed. No out-of-bounds additions (no scraping, connectors, etc.). Scope is tightly limited to one test function.

2. **Expected adapter values and command sequence consistent with current implementation?** Yes, all seven match `external_tool_adapters.py:109-233` exactly. Verified at runtime:
   - `Path("./exports")` → `"exports"` (matches plan's `--directory == "exports"`).
   - `"2026-06-13T12:00:00Z"` → `"2026-06-13T12:00:00+00:00"` via `parse_datetime_utc().isoformat()` (matches plan's `--as-of` assertion).
   - JSON key order from `model_dump_json` matches `expected_adapter_keys` exactly.
   - `recommended_input_format` serializes as a plain string (`"json"`/`"csv"`), matching the tuple comparison.
   - Command sequence (9 entries, with `import-signals-dir` appearing twice) matches `_recommended_commands` at `external_tool_adapters.py:357-488`.

3. **Is the nested `flag_value` helper valid, or should it be refactored?** It **must** be refactored, and the plan already does this correctly. B023 is enabled via `select = ["B"]` in `pyproject.toml`. A closure defined inside the loop body capturing loop-local `readiness_parts` would trigger B023. The plan's `flag_value(parts: list[str], flag: str)` defined **before** the loop and called as `flag_value(readiness_parts, "--adapter")` avoids the closure entirely. This is the correct fix; the spec note at design lines 71-73 is accurate.

4. **Critical or Important issues to fix before implementation?** No. Only the Minor items above, of which only #1 (explicitly deleting the old readiness block) is worth addressing to avoid implementer confusion; the rest are optional polish.

**Verdict:** Plan is approvable as-is for implementation. Recommend addressing Minor #1 in the plan text for clarity before handing off.
