Let me verify the current state of the affected files to ensure the plan accurately reflects reality.
Let me verify the registry defaults and path rendering to confirm the smoke validator assertions will hold.
Let me verify the test fixture payload to ensure the valid case passes the stricter new validator.
## Stage 70 Plan Review

Reviewed both artifacts against the required constraints and the current source. The constraints (no runtime changes, `shlex.split` parsing, no hard-coded user config/data paths, required coverage, local-first boundaries) are all respected. However, there is one blocking test-conflict the plan does not account for.

### Critical

**1. The existing `missing_token` negative case breaks under the new validator and the plan never updates it.**

`tests/test_first_run_smoke.py:1170-1177` keeps this case unchanged:
```python
adapters[0]["recommended_commands"] = [
    "fashion-radar external-tool-readiness --adapter rednote_mcp --format table"
]
with pytest.raises(smoke.SmokeError, match="readiness command missing '--input-format'"):
```

The plan's Task 2, Step 4 validator checks `--directory` *before* `--input-format` (`plan.md:170-174` asserts `required_readiness_value("--directory")` then `--input-format` at `plan.md:178-182`). For that command, `required_readiness_value("--directory")` raises `... readiness command missing '--directory'`, which does **not** match the expected `--input-format` regex, so `pytest.raises(match=...)` fails.

Consequence: Task 2, Step 5's "Expected: both pass" (`plan.md:200-209`) will actually fail for `test_validate_external_tool_adapters_requires_print_only_registry_contract`. The spec's helper design (`design.md:74-90`) does not mandate this ordering — the conflict is introduced by the plan's chosen check order.

Fix options for the plan: (a) change the existing case's `match` to `'--directory'`, or (b) keep the `--input-format` intent by constructing a command that supplies `--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of` but omits only `--input-format`. The Task 2 Step 2 diff should explicitly edit this case rather than only appending after it.

### Minor

**2. Task 2 Step 3 rationale is imprecise about the pre-hardening failure.** `plan.md:123-125` says the old substring checks "do not specifically validate the missing `--format` structure." The old validator (`check_first_run_smoke.py:495-497`) *does* catch a missing `--format` (it is in the substring token list), so the `missing_format` case actually passes pre-hardening. Only the `malformed_readiness` case (expecting `is not shell-parseable`) drives the Step 3 failure. The step still fails as predicted; the explanation just over-attributes the cause.

### Notes / verification done

- Confirmed `DEFAULT_EXPORT_DIRECTORY = "./exports"` and `str(Path("./exports")) == "exports"`, so the smoke validator's `assert_equal("--directory", ..., "exports")` (`plan.md:170-174`) is safe even though the smoke run calls `external-tool-adapters` with no `--directory` (`check_first_run_smoke.py:1030-1034`).
- Confirmed `default_config_dir`/`default_data_dir` are `platformdirs` user dirs (`utils/paths.py:10-15`), so the plan correctly uses **presence-only** checks for `--config-dir`/`--data-dir` (`plan.md:175-176`) — no hard-coded user paths. Good.
- The Task 1 unit assertions (`--config-dir == "configs"`, `--data-dir == "data"`) are also safe: the test constructs the registry with `config_dir=Path("./configs")`, `data_dir=Path("./data")` (`test_external_tool_adapters.py:48-51`), so this checks rendering fidelity of explicitly-supplied paths, not environment defaults.
- No connectors/scraping/platform APIs/scheduling/etc. introduced; scope is test + smoke-validator only. Boundary constraints satisfied.

**No other Critical or Important issues.** The single Critical item above should be resolved in the plan before implementation begins, since it will otherwise halt the plan at Task 2, Step 5.
