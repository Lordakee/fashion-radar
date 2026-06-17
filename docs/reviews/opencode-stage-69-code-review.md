I'll review the Stage 69 workspace. Let me start by examining the current state and the files in scope.
Let me see the full test function and the original version for comparison.
Let me verify the key claims: no remaining `captured[`, the exact-order assertion, runtime code unchanged, and check Python version compatibility.
Let me independently run the key verification commands to confirm the claimed results.
All verification claims independently confirmed. Here is my review.

---

## Stage 69 Code Review

**Scope confirmation:** Only `tests/test_first_run_smoke.py` is modified — no runtime code touched. All 10 numeric `captured[...]` references removed; the exact ordered command-name assertion at `tests/test_first_run_smoke.py:1814` is intact; `single_command("import-signals")` is correctly *not* called (duplicate preserved via the order list + the loop at `tests/test_first_run_smoke.py:1857-1911`).

### Findings

**No Critical issues.**
**No Important issues.**

1. **Minor — `tests/test_first_run_smoke.py:1839-1845`** — `commands_named` is a thin wrapper only ever invoked by `single_command`. Could be inlined, but keeping it documents intent and gives future tests a reusable lookup. No change required; purely stylistic.
2. **Minor — redundancy is intentional and beneficial.** `single_command`'s `assert len(commands) == 1` partially overlaps with the exact-order assertion at line 1814. This is desirable here: each detail assertion becomes positionally self-validating, so the test no longer silently rots if someone reorders the sequence list. Not a defect.

### Correctness checks performed

- All 10 `single_command` targets (`init`, `migrate-db`, `external-tool-adapters`, `external-tool-template`, `external-tool-workflow`, `external-tool-readiness`, `community-handoff-workflow`, `community-signal-lint-dir`, `community-candidates-dir`, `import-signals-dir`) are genuinely unique in the 22-command sequence — `len == 1` will hold.
- Each rewritten assertion compares against the identical tuple / element previously checked at the corresponding index (`captured[0/1/3/4/5/6/18/19/20/21]`), so no checks were dropped or altered.
- Distinct-name pairs (`community-signal-lint` vs `…-dir`, `community-candidates` vs `…-dir`, `imported-signals` vs `imported-signals-summary`, `import-signals` vs `import-signals-dir`) are not conflated by the `command[0] == command_name` filter.
- Type annotations (`list[tuple[str, ...]]`, `tuple[str, ...]`) are consistent with `requires-python = ">=3.11"` and with existing usage at `tests/test_first_run_smoke.py:1690,1734`.
- Helpers are defined *after* the order assertion but *before* every detail assertion that uses them — ordering is correct.
- Scope: pure test-maintenance; no connectors/scraping/platform APIs/scheduling/etc. introduced.

### Residual risk / test gaps

- The refactor preserves but does not strengthen coverage of the two `import-signals` invocations — their argument details are still validated only via the per-command loop (e.g. `--data-dir`, `SOURCE_NAME`, `AS_OF`), not by distinguishing the dry-run vs. real call. This is pre-existing behavior, not a regression introduced by Stage 69.
- `single_command` gives no positional information on failure beyond the name; a future non-unique addition would surface as `assert len(commands) == 1` rather than pointing at the conflicting positions — acceptable trade-off documented by the helper.

**Verdict: safe to proceed.** Critical/Important: none.
