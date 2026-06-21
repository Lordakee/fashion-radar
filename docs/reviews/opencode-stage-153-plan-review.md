## Stage 153 Plan Review — Findings

### CRITICAL (blocking)

**C1. Pinning `directory`/`config_dir`/`data_dir` to fixture literals breaks the real first-run smoke flow.**

The design pins `EXPECTED_COMMUNITY_HANDOFF_DIRECTORY = "/tmp/export"`, `..._CONFIG_DIR = "configs"`, `..._DATA_DIR = "data"` (design:56-58), matching the *test fixture* `community_handoff_workflow_payload()` (tests/test_first_run_smoke.py:655-660). But the **real** smoke flow invokes the CLI with temp-derived paths, not those literals:

- `scripts/check_first_run_smoke.py:2476-2484` calls `run_cli(context, "community-handoff-workflow", str(context.exports_dir), "--config-dir", str(context.config_dir), "--data-dir", str(context.data_dir), ...)`.
- `context.exports_dir = runtime_dir / "exports"`, `context.config_dir = runtime_dir / "config"`, `context.data_dir = runtime_dir / "data"` (scripts/check_first_run_smoke.py:2646-2649), where `runtime_dir` is a `TemporaryDirectory` prefix `fashion-radar-first-run-` (line 2659).
- The builder echoes them verbatim: `directory=str(directory)` etc. (src/fashion_radar/community_handoff_workflow.py:53-55,181-188).

So the real payload's `directory` is e.g. `/tmp/fashion-radar-first-run-XYZ/exports`, **not** `/tmp/export`. The new `assert_equal("... directory", payload.get("directory"), "/tmp/export")` (plan:155-169) would raise `SmokeError` and fail the smoke run. CI runs this script directly (`.github/workflows/ci.yml:28` and `:50`), so the release would fail in CI.

The fixture parity test `test_community_handoff_workflow_payload_matches_real_builder` (tests/test_first_run_smoke.py:1391-1404) only proves the fixture matches the builder **for the hardcoded inputs** `Path("/tmp/export")`/`Path("configs")`/`Path("data")`; it does **not** prove the fixture matches the real smoke flow, which uses temp paths. The design's premise ("the runtime builder and smoke fixture already agree on the current values", design:28-30) conflates these two.

This is exactly why the existing `validate_external_tool_workflow` and `validate_external_tool_readiness` only assert these fields are *populated strings*, never pinned to literals (scripts/check_first_run_smoke.py:1460-1463 and 1821-1824). The plan deviates from that established pattern.

**C2. The verification commands would not catch C1 locally.**

Neither the focused verification (plan:212-221) nor the release gate (plan:235-247) runs `scripts/check_first_run_smoke.py`. The only end-to-style test, `test_run_first_run_flow_uses_deterministic_local_command_sequence` (tests/test_first_run_smoke.py:3470-3561), monkeypatches `run_cli` to return the fixture payloads (with `/tmp/export`), so it would **not** catch the breakage. Comparable prior stages (135 at plan:370 of its plan; 65 at its plan:1404) explicitly ran `python scripts/check_first_run_smoke.py --repo-root .` in verification. Stage 153 omits it, so the failure surfaces only in CI.

### IMPORTANT

**I1. The directory-drift RED test is a false RED and won't guard the new behavior.**

`test_validate_community_handoff_workflow_rejects_directory_drift` uses `match="directory"` (design:111, plan:75). Today, mutating `payload["directory"]` makes the synthesized expected commands (built from the payload's `directory`, scripts/check_first_run_smoke.py:1119-1135) diverge from the unchanged step commands, so the validator already raises at the first step with label `"community-handoff-workflow lint_handoff_directory command"` (label tuple at scripts/check_first_run_smoke.py:619; error path via assert_equal at 499-501 and validate_expected_external_tool_command at 508-522). "directory" is a substring of "lint_handoff_directory", so `re.search("directory", ...)` matches and the test **passes before implementation**. It is not a RED, and reverting the implementation later would still pass it. Use a distinguishing pattern, e.g. `match="directory expected"` or `match=r"community-handoff-workflow directory "`.

**I2. The stated RED rationale ("DID NOT RAISE") is incorrect for all three tests.**

The plan (lines 87, 110, 133) says each RED fails "with `DID NOT RAISE` because the current validator accepts the payload path drift." The current validator does **not** accept the drift — it raises a command-mismatch `SmokeError` (the synthesized commands use the mutated value while step commands keep the original). For `config_dir`/`data_dir` the tests fail due to regex mismatch (the command labels `preview_candidate_phrases`/`dry_run_directory_import` and the `--config-dir`/`--data-dir` reprs contain hyphens, not underscores), not `DID NOT RAISE`. This misstates observable behavior and will confuse the implementer.

### Non-issues (verified OK)

- New assertions are placed after `source_name` and before `expected_community_handoff_workflow_command_parts(...)` (matches plan:150-184; current code at scripts/check_first_run_smoke.py:1118-1135). ✓
- Existing command-specific labels (e.g. `"lint_handoff_directory command"`) and effect-specific labels (`"import step effect"`, `"post-review step effect"`) are preserved. ✓
- Runtime builder/CLI/dashboard/import semantics are untouched (only the smoke checker and tests change). ✓

### Recommendation

Do not proceed as written. Options to unblock:
1. Drop the exact-pinning approach for these three fields (they are inherently temp-derived in the real smoke flow) and instead keep the populated-string check — i.e., follow the pattern already used by `validate_external_tool_workflow`/`validate_external_tool_readiness`. The smoke checker cannot pin values it never receives as literals.
2. If exact field pinning is genuinely desired, the expected values must be threaded into the validator from `SmokeContext` (a larger change than this stage's scope), and the verification must run `scripts/check_first_run_smoke.py --repo-root .`.
3. At minimum, add `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .` to both focused and release-gate verification, and fix the directory-drift test's `match` pattern and the RED rationale.

There are blocking issues — the plan should not be implemented as written.
