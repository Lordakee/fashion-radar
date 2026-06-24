# Stage 184 Plan Review

## Critical

None.

## Important

None.

## Minor

1. **Identical-label case is exercised only at count 2.** `(2, "info", "info", "2 info")` proves the helper tolerates equal singular/plural labels, but because both branches yield the same string it does not strengthen the singular-only-for-one guard. Adding `(1, "info", "info", "1 info")` would also exercise the singular branch under identical labels. Cosmetic given the equality, and the case is a real caller (`format_finding_counts` at `lint_formatting.py:13`), so this is optional.

2. **The irregular plural is synthetic, not a current caller.** `analysis`/`analyses` is not used by any renderer (real callers are `error`, `warning`, `info`, `file`, `row`, `candidate`, `import-ready row`, `valid file`). This is intentional per the design (a derivation-resistance probe, not a caller guard), and count 2 is precisely the case that exposes mechanical `+"s"` derivation (`analysis`+`s` → `analysiss` would fail). Just flagging so the spec wording is not misread as claiming it is a current renderer label.

## Question Responses

1. **Objective coverage.** Satisfied. Non-error labels covered (`import-ready row`, `valid file`, `info`, `analysis`); current caller-shaped multi-word labels covered (`import-ready row` at `community_handoff_check.py:202`, `valid file` at `:209`); identical singular/plural covered (`info`/`info`); irregular plural covered (`analysis`/`analyses`).

2. **Meaningful guards.** Yes. The multi-word and irregular cases catch hardcoded-label regressions and mechanical plural derivation; the count 0 / count 1 / count 2 spread across multiple labels pins the singular-only-for-exactly-one threshold (`count 0 → plural`, `count 1 → singular`, `count 2 → plural`). The irregular plural at count 2 is the correct and sufficient derivation probe (count 1 would use the supplied singular directly and could not reveal a derivation bug).

3. **Test-only discipline.** Yes. All eight expected outputs match the current `format_count_label` exactly (`singular if count == 1 else plural`), so the new test will pass without a source change. The plan explicitly gates any helper edit on the test exposing a real defect, which it will not. Existing `format_finding_counts` tests are preserved.

4. **Focused verification.** Sufficient. Task 2 runs `pytest tests/test_lint_formatting.py -q`, `ruff check`, and `ruff format --check` against the touched test file; because the source is unchanged, file-scoped verification is adequate ahead of the full release gate in Task 3.

## Verdict

Approve implementation. The plan is accurate, in scope (test-only hardening), and consistent with the design and the shared-helper contract.
