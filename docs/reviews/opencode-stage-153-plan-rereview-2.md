## Findings

### CRITICAL (blocking) — Plan Task 3 Step 4 produces a `dict`, but `stdout_by_command` requires a JSON string

`docs/superpowers/plans/2026-06-22-stage-153-community-handoff-top-level-field-exactness-plan.md:223` wraps the builder output in `json.loads(...)`:

```python
"community-handoff-workflow": json.loads(
    build_community_handoff_workflow(...).model_dump_json()
),
```

This yields a **dict**, while every sibling entry in `stdout_by_command` is a `json.dumps(...)` **string** (`tests/test_first_run_smoke.py:3533-3546`, e.g. line 3536 `"community-handoff-workflow": json.dumps(community_handoff_workflow_payload())`).

Trace of the breakage: `fake_run_cli` assigns that dict to `CompletedProcess.stdout` (`tests/test_first_run_smoke.py:3547-3552`). The un-mocked `run_first_run_flow` then calls `validate_json_output("community-handoff-workflow", run_cli(...).stdout)` (`scripts/check_first_run_smoke.py:2473-2494`). `validate_json_output` does `json.loads(output)` and only catches `JSONDecodeError` (`scripts/check_first_run_smoke.py:492-496`); `json.loads(dict)` raises an **uncaught `TypeError`**. Task 3 Step 5 (`pytest -k deterministic_local_command_sequence`) will error, not pass.

The design doc has the correct form — `.model_dump_json()` directly, i.e. a string (`docs/superpowers/specs/2026-06-22-stage-153-community-handoff-top-level-field-exactness-design.md:123-131`). The plan diverged from the spec. **Fix:** drop the `json.loads(...)` wrapper in the plan and use `.model_dump_json()` verbatim, matching both the spec and the surrounding `json.dumps(...)` entries.

### Non-blocking checks (all pass)

- **RED tests isolate the new assertions correctly.** Each drift test mutates one top-level field *and* rewrites the command fragments via `replace_workflow_command_fragments` (`tests/test_first_run_smoke.py:741-753`) so the payload stays internally consistent. Pre-implementation, the validator derives paths from the payload (`scripts/check_first_run_smoke.py:1119-1123`), so nothing raises → `DID NOT RAISE`. Post-implementation, the new field assertion fires before command synthesis. Match labels line up: `f"{command_name} directory|config_dir|data_dir"` vs. patterns at plan lines 80, 107, 134.
- **Validator signature + `run_smoke(context)` threading is correct.** Keyword-only defaults (`/tmp/export`, `configs`, `data`) match the fixture (`tests/test_first_run_smoke.py:655-660`) and the builder parity test (`tests/test_first_run_smoke.py:1391-1404`). `run_smoke` → `run_first_run_flow(context)` (`scripts/check_first_run_smoke.py:2206-2211, 2226`); the proposed call passes `str(context.exports_dir/config_dir/data_dir)`, identical to the CLI argv at `scripts/check_first_run_smoke.py:2478-2482`.
- **Pinned values match fixture and builder.** Confirmed above; `as_of=smoke.AS_OF` normalizes to `2026-06-13T12:00:00+00:00` via `parse_datetime_utc(...).isoformat()` (`src/fashion_radar/community_handoff_workflow.py:51`), matching `EXPECTED_WORKFLOW_AS_OF`.
- **Existing labels unchanged.** The plan only *adds* three `assert_equal` calls and swaps the command-synthesis inputs from payload-derived locals to the expected params. No existing command/metadata/effect labels are renamed. Existing drift tests (`rejects_coordinated_metadata_command_drift`, `rejects_unpinned_command_drift`, `requires_import_and_review_effects`, etc.) still hit: their mutations leave `directory/config_dir/data_dir` at fixture defaults, so the new field assertions pass and the existing checks fire unchanged.
- **Real `scripts/check_first_run_smoke.py --repo-root .` closes the gap.** The validator now asserts the builder's emitted path fields against caller-supplied expected values rather than reading them back out of the payload; the real flow sources both the CLI args and the expected values from the same `context.*`, so any builder-side path drift is caught. Plan Task 3 Step 8 + Task 4 Step 1 exercise this.
- **Runtime behavior unchanged.** `src/fashion_radar/community_handoff_workflow.py` is not in the modify set; CLI/dashboard/import semantics untouched.

## Verdict

**One blocking issue:** the plan's Task 3 Step 4 snippet (`json.loads(...model_dump_json())`) contradicts the spec and will break the deterministic test with an uncaught `TypeError`. Align the plan with the spec at `docs/superpowers/specs/2026-06-22-stage-153-community-handoff-top-level-field-exactness-design.md:123-131` by using `.model_dump_json()` directly. With that one fix, the plan is sound and ready to execute.
