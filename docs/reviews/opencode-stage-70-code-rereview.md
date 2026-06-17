I'll rereview the Stage 70 workspace. Let me start by examining the current state of the uncommitted changes.
Let me read the relevant files in full context to verify the changes.
Let me verify the imports and the helper payload that the positive tests rely on.
Let me check the helper payload that the positive test relies on, and run the full verification suite.
Let me run the exact three verification commands listed in the rereview prompt to confirm they pass as claimed.
## Stage 70 Code Rereview

**No Critical or Important issues.** The prior Minor test-coverage gaps are resolved and all Stage 70 constraints hold.

### Prior Minor Findings — Resolved

All three previously-uncovered negative paths now have explicit tests in `tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract`:

| Prior gap | Test | Validator path |
|---|---|---|
| non-table `--format` | `invalid_format` (test_first_run_smoke.py:1198-1210, `--format json`) | `check_first_run_smoke.py:544-548` |
| value replaced by next flag | `missing_value` (test_first_run_smoke.py:1212-1224, `--source-name --format table`) | `check_first_run_smoke.py:505-514` (`value.startswith("--")`) |
| trailing flag with no value | `trailing_flag` (test_first_run_smoke.py:1226-1236, ends at `--as-of`) | `check_first_run_smoke.py:509-510` (`index + 1 >= len`) |

Two extra negative paths were also added: malformed shell quoting (`malformed_readiness`, :1238-1245, unterminated quote → `shlex.split` `ValueError` at :497-498) and missing required flag (`missing_format` for `--format`, :1184-1196; plus the pre-existing `missing_token` for `--input-format`, :1170-1182).

### Stage 70 Constraints — Verified

- **No app runtime changes:** `git diff --stat -- src/` is empty; only `scripts/check_first_run_smoke.py` + 3 test files changed.
- **Adapter registry output unchanged:** no edit to `src/fashion_radar/external_tool_adapters.py`; the new `test_cli.py` assertions (:558-580, :615-618) parse the *existing* emitted command and pass, proving the output already contained `--directory/--config-dir/--data-dir/--as-of/--pattern/--source-name`.
- **CLI tests use `shlex.split` without hard-coding config/data defaults:** `test_cli.py:574-575` asserts only truthiness of `--config-dir`/`--data-dir` values; :617-618 assert against test-supplied special-char inputs, not defaults. Smoke validator mirrors this — it requires *presence* of `--config-dir`/`--data-dir`/`--as-of` (check_first_run_smoke.py:526-528) without value-checking them.
- **Smoke validation parses via `shlex.split`:** check_first_run_smoke.py:496, with prefix assertion `[:2] == ["fashion-radar","external-tool-readiness"]` (:499-503).
- **No forbidden product behavior:** changes are pure validator/test hardening; print-only contract enforcement unchanged (:476 `execution_mode == "print_only"`).

### Verification Reproduced

All three claimed commands pass exactly: `1 passed`, `52 passed`, `3 passed`. Full run of the three modules: `359 passed`.

### Minor (non-blocking) observations

- `check_first_run_smoke.py:512` `if not value` is effectively unreachable (`shlex.split` never yields empty tokens); harmless defensive code, no action required.
- `test_external_tool_adapters.py:91-92` adds value assertions for `--config-dir`/`--data-dir` against the instaloader fixture (`"configs"`/`"data"`); these are adapter-fixture constants, not user defaults, so they don't conflict with the no-hard-coded-defaults constraint.

**Verdict: Stage 70 changes are ready.**
