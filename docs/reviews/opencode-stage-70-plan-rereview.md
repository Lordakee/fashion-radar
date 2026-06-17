I'll review the three artifacts in parallel.
Let me verify the current state of the affected source/test files to confirm the plan's assertions will hold.
Let me verify the CLI tests, the registry output, and the adapter unit test to confirm the plan's assertions match reality.
Let me verify the default `--as-of` value rendered by the CLI and the `_shell_command` quoting helper, since the plan hard-codes an `--as-of` assertion in the default CLI JSON test.
Let me verify the test fixture payload so the valid case passes the stricter validator, and confirm `parse_datetime_utc` normalization.
Let me confirm `shlex` is already imported in the smoke validator script (the plan uses `shlex.split` there but doesn't mention adding an import).
## Stage 70 Plan Rereview

Reviewed the spec, the revised plan, and the prior review against the current source (`tests/test_first_run_smoke.py`, `tests/test_cli.py`, `tests/test_external_tool_adapters.py`, `scripts/check_first_run_smoke.py`, `src/fashion_radar/external_tool_adapters.py`, `src/fashion_radar/cli.py`, `src/fashion_radar/utils/dates.py`).

### Critical

**None.** The prior Critical conflict is resolved.

The revised `missing_token` case (`plan.md:184-192`) now supplies `--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`, `--pattern`, `--source-name`, `--format` and omits only `--input-format`. Traced against the new validator check order (`plan.md:270-302`): the validator passes `--adapter` → `--directory` → `--config-dir` → `--data-dir` → `--as-of`, then raises `... readiness command missing '--input-format'`, which matches the unchanged `pytest.raises(..., match="readiness command missing '--input-format'")` at `tests/test_first_run_smoke.py:1176`. The Task 3 Step 5 "both pass" expectation now holds.

### Important

**None.**

### Minor

**1. CLI test `flag_value` helper is slightly looser than the validator it mirrors.** `plan.md:105-108` defines:
```python
def flag_value(flag: str) -> str:
    value = readiness_parts[readiness_parts.index(flag) + 1]
    assert value
    return value
```
Unlike the smoke validator's `required_readiness_value` (`plan.md:259-268`), it has no `value.startswith("--")` guard and no bounds check on `index + 1`. So a regressed registry emitting `--config-dir --data-dir` (missing value) would let `flag_value("--config-dir")` return `"--data-dir"` and pass `assert value`. Since this stage's stated goal is hardening the readiness-command assertions, mirroring the `startswith("--")` / bounds guard would let the CLI test independently catch that regression instead of relying on the smoke validator. Non-blocking — the smoke validator enforces the rule, and real registry output is correct.

### Verified

- Valid fixture passes the stricter validator: `tests/test_first_run_smoke.py:416-421` contains every required flag with the exact stable values the new checks require (`--adapter rednote_mcp`, `--directory exports`, `--input-format json`, `--pattern *.json`, `--source-name 'Rednote MCP Export'`, `--format table`), with `--config-dir`/`--data-dir`/`--as-of` present and non-empty.
- `missing_format` and `malformed_readiness` cases (`plan.md:197-219`) trace correctly to their respective `match=` strings; only the malformed case drives the Task 3 Step 3 pre-hardening failure (the plan's wording at `plan.md:229-230` now states this correctly, resolving prior Minor #2).
- Task 2 Step 2 default-CLI assertions match live output: `DEFAULT_ADAPTER_AS_OF = "2026-06-13T12:00:00Z"` (`external_tool_adapters.py:15`) normalizes via `parse_datetime_utc(...).isoformat()` → `"2026-06-13T12:00:00+00:00"` (`dates.py:8-17`); `DEFAULT_EXPORT_DIRECTORY` renders as `"exports"`; `rednote_mcp` source name / pattern / format match `cli.py:611` table row.
- No hard-coded user config/data defaults: the CLI test uses presence-only checks for `--config-dir`/`--data-dir` (`plan.md:113-114`); the only hard-coded `configs`/`data` are in the unit test where the test itself supplies those paths (`test_external_tool_adapters.py` constructs the registry explicitly) and in the smoke negative-case fixtures.
- `shlex` already imported in both `scripts/check_first_run_smoke.py:9` and `tests/test_cli.py:3`; `_shell_command` uses `shlex.join` (`external_tool_adapters.py:491-492`), so `shlex.split` round-trips the quoted-path test values exactly as asserted in `plan.md:137-141`.
- Scope is test + smoke-validator only; no runtime/registry/CLI behavior changes, no boundary-violating capabilities added.

**No Critical or Important issues.** The plan is ready for implementation.
