I'll review the Stage 70 changes. Let me start by reading all the in-scope files in parallel.
Let me continue reading the test files and view the rest of test_first_run_smoke.py.
Let me check if there are any other relevant context files and verify the test claims.
Let me verify the key verification claims by running the focused tests, and check the diff to confirm what changed:
Let me run the key verification tests to confirm the claims:
Let me confirm the validator's behavior on the rejection cases that lack explicit negative tests:
Let me quickly confirm the review artifacts exist and run the broader test suite to confirm no regressions:
## Stage 70 Code Review

No **Critical** or **Important** issues found. The implementation matches the design and plan, runtime behavior is unchanged, and all claimed verification commands reproduce (`52 passed` in `test_first_run_smoke.py`, focused adapter/CLI tests pass, ruff clean).

### Findings

**1. Minor — `tests/test_first_run_smoke.py:1131` (test gap: non-table `--format` value)**
The Stage Goal lists "non-table readiness output format" as a required rejection. The validator rejects it correctly (`scripts/check_first_run_smoke.py:544-548` asserts exact `"table"`), but no negative test exercises `--format json` (or any non-table value). Existing negative tests cover only *missing* `--format` (`tests/test_first_run_smoke.py:1184-1196`). A future regression that loosens the `assert_equal` to a presence check would slip through silently.

**2. Minor — `tests/test_first_run_smoke.py:1131` (test gap: flag value replaced by next flag)**
The Stage Goal lists "flag values that are missing or replaced by the next flag" as a required rejection. The validator handles this via `value.startswith("--")` at `scripts/check_first_run_smoke.py:512`, and I confirmed by probe that `--source-name --format table` is rejected — but there is no negative test in the test file that asserts this path. Same residual risk as #1.

**3. Minor — `tests/test_first_run_smoke.py:1131` (test gap: trailing flag with no value)**
The validator handles end-of-list flags via `index + 1 >= len(readiness_parts)` at `scripts/check_first_run_smoke.py:509` (confirmed by probe: trailing `--as-of` is rejected), but again no explicit negative test exists. Closely related to #2; one combined negative test would cover both.

### Scope & Behavior

- No app/runtime/adapter-registry behavior changes; diff is test-only plus the smoke validator rewrite of the readiness-token checks.
- Validator semantics match the design: stable values use `assert_equal`, environment-dependent paths (`--config-dir`, `--data-dir`, `--as-of`) use presence-only checks. This is consistent with how the smoke invokes `external-tool-adapters` without pinning `--as-of` (`scripts/check_first_run_smoke.py:1081-1085`), so the `--as-of` presence-only check is correct, not a bug.
- `readiness_commands[0]` validates only the first matching readiness command in `recommended_commands`. Fine for the current single-readiness-command registry shape; mild robustness gap if the registry ever emits multiple.
- Stays within local-first/free-first boundaries: no connectors, scraping, browser automation, platform APIs, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review behavior added.

### Residual Risk

Low. The three Minor gaps above are pure test-coverage gaps on validator paths that already behave correctly — they affect future regression sensitivity, not current correctness. Adding three small negative cases (non-table `--format`, value-is-next-flag, trailing flag) to the existing parametric-style test would close the gap between the Stage Goal's stated rejection semantics and the explicit test contract.
