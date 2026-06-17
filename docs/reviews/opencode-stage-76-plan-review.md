I'll examine the current state of the code to verify the plan's assumptions align with reality.
Let me read the rest of the test file and verify the runtime registry code.
Let me examine the runtime registry code and check remaining test sections.
Let me verify how the CLI uses these env vars and what defaults it uses.
Let me verify the env var impact and repo structure.
I have enough context to produce the review. Let me write it to stdout.

# Stage 76 Plan Review

## Scope Verdict

The design and plan are well-scoped, internally consistent, and correctly target the remaining first-run smoke validator gap. The static expected constants are aligned with the current runtime registry contract in `src/fashion_radar/external_tool_adapters.py`, and the negative-test matrix covers every newly-added check. No Critical or Important issues block implementation.

## Critical

None.

## Important

None.

## Minor

1. **Env-var blast radius is wider than the target command, but safe and actually beneficial.** Setting `FASHION_RADAR_CONFIG_DIR=configs` / `FASHION_RADAR_DATA_DIR=data` in `command_environment(...)` affects every subprocess in `run_first_run_flow()`, not only `external-tool-adapters`. At least four commands do not pass explicit `--config-dir` and/or `--data-dir`:
   - `external-tool-adapters` (intended target; renders paths into printed commands).
   - `external-tool-template` (`scripts/check_first_run_smoke.py:1180`) — only passes `--adapter`/`--format`; its validated JSON payload (`items`) does not render config/data paths, so no validator impact.
   - `community-signal-lint` (`scripts/check_first_run_smoke.py:1232`) — read-only file linter, does not consume `data_dir`/`config_dir`.
   - `community-candidates` (`scripts/check_first_run_smoke.py:1243`) — passes `--config-dir` but not `--data-dir`, so it will resolve `data_dir` to `repo_root/data/`. Today (pre-Stage-76) the same command resolves `data_dir` via platformdirs to a path outside the repo that also lacks a DB, and the smoke passes, so this command clearly tolerates a missing DB. Stage 76 only changes *which* missing path is consulted, and moves it *inside* the repo so the existing `assert_default_artifacts_unchanged` guard (`scripts/check_first_run_smoke.py:1045`) now also catches any accidental write. Net effect: more deterministic, better guarded. The spec/plan would benefit from a one-line note documenting this blast-radius analysis so future maintainers don't unintentionally introduce a command that writes to `repo_root/configs/` (which is **not** covered by the artifact guard).

2. **Smoke helper duplicates the fixture helper (~130 lines).** `scripts/check_first_run_smoke.py::expected_external_tool_adapter_commands` will reproduce `tests/test_first_run_smoke.py::external_tool_adapter_commands` verbatim. This is an accepted trade-off (keeps the smoke independent of `fashion_radar.external_tool_adapters`), and the helper-parity test makes drift visible. Worth a one-line comment in the smoke helper pointing at the parity test so the duplication is deliberate and maintained in lockstep.

3. **Helper-parity test covers 2 of 7 adapters.** `test_expected_external_tool_adapter_commands_match_fixture_helper` parameterizes only `rednote_mcp` (JSON) and `xiaohongshu_crawler` (CSV). This is sufficient because `validate_external_tool_adapters` iterates all seven adapters and the full-smoke run exercises the remaining five, but the two chosen cases do exercise both `input_format` branches, which is the right axis.

4. **No negative test for an extra registry boundary.** The matrix covers `remove_external_tool_registry_boundary` (shrinking) and `add_external_tool_registry_extra_key` (top-level key drift), but not appending an extra entry to `payload["boundaries"]`. The `boundaries` equality check catches both directions, so this is symmetry-only.

5. **`remove_external_tool_adapter_key` pops `description`, which is also covered by the dedicated description-drift case.** The keys-order check is the intended trigger here, and since the mutation removes a key (rather than just changing its value), the label `"rednote_mcp keys"` is correct and the test is well-formed. No action needed; noting for clarity.

## Review Questions

1. **Coverage of remaining gap** — Yes. Stages 73-75 left the full static JSON surface (top-level/adapter key order, descriptions, upstream examples, field mappings, full command strings, adapter/registry boundaries) unvalidated by the smoke itself; Stage 76 closes exactly that gap while leaving Stage 73 diagnostic precedence intact.

2. **Constant alignment with runtime** — Verified against `src/fashion_radar/external_tool_adapters.py`: `EXPECTED_EXTERNAL_TOOL_ADAPTER_KEYS` matches the `ExternalToolAdapter` field declaration order (lines 59-73); `EXPECTED_EXTERNAL_TOOL_REGISTRY_KEYS` matches `ExternalToolAdapterRegistry` (lines 76-82); `EXPECTED_EXTERNAL_TOOL_ADAPTER_DETAILS`, `EXPECTED_EXTERNAL_TOOL_FIELD_MAPPINGS`, `EXPECTED_EXTERNAL_TOOL_ADAPTER_BOUNDARIES`, and `EXPECTED_EXTERNAL_TOOL_REGISTRY_BOUNDARIES` match the runtime `_adapter(...)`, `FIELD_NOTES`/`_field_mappings(...)`, `ADAPTER_BOUNDARIES`, and `EXTERNAL_TOOL_ADAPTER_REGISTRY_BOUNDARIES` literals. The CLI `external-tool-adapters` command honors `FASHION_RADAR_CONFIG_DIR`/`FASHION_RADAR_DATA_DIR` via `CONFIG_DIR_OPTION`/`DATA_DIR_OPTION` (`src/fashion_radar/cli.py:186-192, 686-687`), and `directory` defaults to `DEFAULT_EXPORT_DIRECTORY = "./exports"` which `Path("./exports")` normalizes to `"exports"`, matching the fixture's hardcoded value.

3. **Negative-test strength** — Adequate and well-scoped. Eleven mutations cover every newly-added check without bloating the existing Stage 73 test. Each mutation targets exactly one contract family and asserts a specific label that the new validator emits. The split into a dedicated parameterized test is the right structural choice.

4. **Avoiding docs/CHANGELOG** — Correct. This is internal smoke/test hardening with no user-facing or API surface change. The public adapter matrix was already documented in Stage 75.

5. **Avoidance of runtime/external-platform behavior changes** — Yes. Runtime code is untouched; the smoke script's only behavioral change is two `env[...] = ...` assignments plus new static validators. Generated recommended commands remain print-only and are never executed; no new platform behavior is introduced.

6. **Critical/Important before implementation** — None. Implement as planned.
