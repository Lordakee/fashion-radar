I'll review the Stage 69 spec and plan. Let me start by reading the artifacts and the current test file to understand what's being changed.
Now let me read the current test file to verify the plan's accuracy against actual code.
Let me find the specific test function and the assertions being changed.
Let me read the full test function to verify all the assertions and the duplicate handling.
I've verified the plan against the actual test code. Here are my findings.

---

## Stage 69 Plan Review

**No Critical issues.** All required safety constraints are satisfied: the ordered command-name assertion is preserved verbatim (plan lines 48-71 match test lines 1815-1836 exactly), runtime code is untouched, the first-run sequence is unchanged, `import-signals` duplicate handling via the loop (test lines 1848-1902) and ordered list is preserved, and the converted detail assertions retain identical semantics.

### Important

**1. Acceptance criterion is broader than the design/plan — `captured[0]` and `captured[1]` are left as numeric references.**

The spec's acceptance criterion (`docs/.../design.md:89-91`) states:

> `tests/test_first_run_smoke.py` **no longer uses numeric `captured[...]` references** for unique command detail assertions in the first-run command capture test.

But both `init` and `migrate-db` are unique commands with detail assertions that the plan does **not** convert:
- `tests/test_first_run_smoke.py:1838` — `assert captured[0] == ("init", "--config-dir", ...)`
- `tests/test_first_run_smoke.py:1847` — `assert captured[1] == ("migrate-db", "--data-dir", ...)`

The spec's Design section (`design.md:65-69`) and the plan's replacements (`plan.md:87-158`) only list 8 commands (the external-tool and community-handoff/dir commands). `init` and `migrate-db` are silently omitted, so after execution a `grep 'captured\[' tests/test_first_run_smoke.py` would still show two hits and the acceptance criterion would read as unmet.

Note `captured[0]` is **not** redundant: it verifies `--config-dir`/`--reports-dir` for `init`, which the flag-coverage loop (lines 1861-1878) does not check. So coverage would be preserved by converting it (not by dropping it).

Reconcile one of two ways before implementing:
- Convert both: add `single_command("init")` and `single_command("migrate-db")` to the plan; or
- Narrow the criterion, e.g. "no longer uses numeric `captured[...]` references for unique command detail assertions **after the deterministic head commands** (`init`, `migrate-db`)".

### Minor

None material. (The helper placement "immediately after the ordered assertion" is fine; nested closures over `captured` are well-formed; `single_command`'s `len == 1` guard is a strengthening, not a weakening; `uv --no-config run --frozen` matches project convention.)
