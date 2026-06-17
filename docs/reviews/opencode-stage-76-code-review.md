I'll review the Stage 76 implementation. Let me start by examining the repository state and the changed files.
Let me examine the actual changes in the two modified files and the design artifacts.
Now let me examine the test changes and the existing validator context.
Let me read the full validator function and the test fixture helper to verify the parity claims.
Let me look at the start of the validator function and the test fixture helper to verify parity claims.
Let me read the fixture helper to verify parity, and check the runtime registry source.
Let me verify the runtime registry matches the pinned static expectations and check the CLI envvar semantics.
Let me verify the envvar-to-Path conversion in the CLI defaults and confirm the runtime registry parity test reference.
Let me check the path defaults and confirm the full test suite count and the runtime parity test.
Verification complete. All scope boundaries hold (no `src/`, public docs, manifest, or lockfile changes), the runtime registry matches the pinned static values, the new validator checks sit strictly after the Stage 73 diagnostics, and the smoke helper is byte-identical to the fixture helper. Here is the final review.

# Stage 76 Code Review — Adapter Smoke Full Contract

**Verdict: APPROVE.** No Critical or Important findings. Stage 76 is safe to commit.

## Summary

The change hardens `validate_external_tool_adapters` in `scripts/check_first_run_smoke.py` to assert the complete static JSON surface of `external-tool-adapters --format json`, and pins a smoke-local `FASHION_RADAR_CONFIG_DIR=configs` / `FASHION_RADAR_DATA_DIR=data` environment so the print-only registry emits deterministic handoff paths in both source and installed smoke modes. Runtime code is untouched.

## Critical Findings

None.

## Important Findings

None.

## Minor Notes

1. **Two sources of truth, mitigated by parity tests.** `EXPECTED_EXTERNAL_TOOL_ADAPTER_DETAILS`, `EXPECTED_EXTERNAL_TOOL_FIELD_MAPPINGS`, `EXPECTED_EXTERNAL_TOOL_ADAPTER_BOUNDARIES`, and `EXPECTED_EXTERNAL_TOOL_REGISTRY_BOUNDARIES` duplicate values that also live in `src/fashion_radar/external_tool_adapters.py`. This is intentional and correct (the smoke must not import the code under test), and drift is caught by `test_external_tool_adapters_payload_matches_real_registry` plus the new `test_expected_external_tool_adapter_commands_match_fixture_helper`. The pairing is sound; no action needed, but future editors must update both sites together.

2. **`remove_external_tool_adapter_key` is representative, not exhaustive.** It only removes `description`. Removing other keys (`field_mappings`, `recommended_commands`, etc.) is caught by the same `list(adapter)` assertion, while some keys would additionally trip earlier Stage 73 checks. The single case adequately proves the key-order guard; expanding it is not warranted.

3. **`command_environment` unconditionally overwrites the two env vars.** Even when a caller passes `base_env`, `FASHION_RADAR_CONFIG_DIR`/`FASHION_RADAR_DATA_DIR` are force-set to `configs`/`data`. This is deliberate for determinism and is locked by `test_command_environment_sets_deterministic_adapter_registry_dirs`; flagging only so a future caller who wants to inject custom dirs via `base_env` is aware.

4. **Relative-path CWD assumption is benign.** The env vars are relative (`configs`, `data`). The print-only registry never inspects them (registry boundary: "Does not inspect the supplied directory"), and the smoke already runs from the repo root where those directories exist, so the relative values are both deterministic for rendering and harmless for any smoke command that does read them. The full smoke and release-hygiene runs confirm this.

## Review Questions

1. **Full static contract coverage?** Yes. The validator now asserts top-level key order (`contract_version`, `execution_mode`, `adapters`, `boundaries`), per-adapter key order (all 12 fields), each adapter's `description`, `upstream_tool_examples`, shared `field_mappings`, full `recommended_commands` strings (via the new `shlex.join`-based helper), adapter `boundaries`, and registry `boundaries`. Every value was cross-checked against `src/fashion_radar/external_tool_adapters.py` and matches exactly.

2. **Stage 73 diagnostic labels preserved?** Yes. The new per-adapter assertions are inserted strictly after the existing readiness output-format assertion inside the loop (`scripts/check_first_run_smoke.py:914`), and the top-level key/boundary assertions run after the adapter loop (`:951`). Payload-type, `contract_version`, `execution_mode`, adapter-id order, core metadata, command-prefix, shell-parseability, readiness-count, and readiness-flag diagnostics all retain precedence. `test_validate_external_tool_adapters_requires_print_only_registry_contract` continues to pass.

3. **Env var change deterministic without altering runtime CLI?** Yes. The vars are set only inside the smoke subprocess environment produced by `command_environment`. Runtime CLI behavior is unchanged: `CONFIG_DIR_OPTION`/`DATA_DIR_OPTION` still bind `envvar=FASHION_RADAR_CONFIG_DIR/DATA_DIR` with the same `default_config_dir`/`default_data_dir` factories, and Typer does not `.resolve()` envvar-derived `Path` values, so `str(Path("configs")) == "configs"`. The explicit `run_first_run_flow()` command sequence is unchanged and `test_run_first_run_flow_uses_deterministic_local_command_sequence` passes.

4. **New tests strong and localized?** Yes. `test_validate_external_tool_adapters_rejects_full_static_contract_drift` is a focused parameterized table covering 11 drift families (extra/missing registry key, registry-boundary drift, extra/missing adapter key, description drift, upstream-example drift, two field-mapping drift axes, adapter-boundary drift, non-readiness command drift, readiness extra-flag drift), each asserting a specific `SmokeError` label. The helper-parity test covers one JSON and one CSV adapter. The env-var test covers both source and installed modes. No unrelated behavior is exercised.

5. **Runtime, dependencies, public docs, external-platform behavior unchanged?** Yes. `git diff` touches only `scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py`; new untracked files are Stage 76 review/spec/plan artifacts under `docs/reviews` and `docs/superpowers`. No changes under `src/`, `pyproject.toml`, `uv.lock`, or public docs. No connectors, scraping, browser automation, platform APIs, auth/cookie/session/token/proxy behavior, CAPTCHA handling, media download, monitoring/scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review behavior introduced.

6. **Critical/Important issues before commit?** None. The implementation matches the design and plan, all claimed verification reproduces the stated results, and the scope stays within smoke/test hardening.

## Recommendation

Commit as planned with the Stage 76 spec, plan, and review artifacts. No changes required.
