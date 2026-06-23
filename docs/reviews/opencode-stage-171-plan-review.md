# Stage 171 Plan Review

## Summary

The Stage 171 plan is a tightly scoped, presentation-only grammar fix for the
human-readable `community-handoff-check-dir` summary lines produced by
`render_community_handoff_directory_check_table(...)` in
`src/fashion_radar/community_handoff_check.py:169`. The structured result,
JSON output, check logic, CLI flow, strict mode, warnings, finding messages,
and exit codes are correctly left untouched. The design and plan are mutually
consistent, the field names in the planned `model_copy(...)` block match the
current Pydantic models (`valid_row_count`, `candidate_count`,
`valid_file_count`, `row_count`, `file_count`, `error_count` all verified
against `community_signals.py`, `community_candidates.py`, and
`manual_signals.py`), and the helper `format_count_label(count, singular,
plural)` already returns `f"{count} {label}"`, which is exactly what the
slash-prefixed phrases require. The plan correctly preserves the Stage 167
singular error-count behavior and follows the project review protocol.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Test name drift. The existing function
   `test_render_community_handoff_directory_check_table_uses_singular_error_label`
   at `tests/test_community_handoff_check.py:312` is named for the error label
   only. After Task 1 it will also assert file, import-ready row, candidate,
   row, and valid file singular labels. The name becomes slightly stale.
   Consider renaming it to something like
   `..._uses_singular_count_labels` or splitting the new grammar assertions
   into a separately named test so the name continues to describe intent. This
   is stylistic and does not block implementation.

2. No explicit plural-line assertion. After this stage there is no test that
   pins the rendered plural wording (for example `2 files`, `2/2
   import-ready rows`, `2 candidates from 2 rows`, `2/2 valid files`, `2
   rows`). The plural path is exercised indirectly through the integration
   test at `tests/test_community_handoff_check.py:65` and the CLI summary test
   at `tests/test_cli.py:4682`, but neither asserts the exact summary lines.
   Adding a complementary exact plural-line assertion would guard against a
   future plural regression. This is optional and slightly out of this stage's
   singular-grammar scope, so it is noted only as a candidate follow-up.

3. Internally inconsistent synthetic fixture. Forcing all counts to 1 via
   `model_copy(...)` on a result that actually contains two files and two
   rows produces a deliberately inconsistent renderer state. This matches the
   Stage 167 pattern and is acceptable for a renderer-only grammar test. The
   design doc already acknowledges this; no action needed.

## Plan Assessment

Question 1: Is this stage appropriately scoped and safe? Yes. Only one renderer
function is modified. No check logic, models, JSON output, CLI options, command
flow, strict-mode behavior, warnings, finding messages, or exit codes change.
The change is display-only and reversible.

Question 2: Does the plan satisfy the project boundary rules in `AGENTS.md`?
Yes. The `community-handoff-check-dir` command is an existing local-only
handoff readiness report. This stage adds no source acquisition, connectors,
scraping, browser automation, platform APIs, login, cookies, monitoring,
scheduling, demand proof, ranking, coverage verification, or compliance-review
features. It edits only local text rendering.

Question 3: Is extending the existing renderer test the right RED strategy?
Yes. The existing test already builds a valid real result and uses
`model_copy(...)` to force a synthetic one-error renderer state, which is the
cleanest way to reach the one-count grammar path without constructing a
contrived directory. Replacing the two `endswith(", 1 error")` checks with
exact-equality assertions on the Lint, Candidate preview, and Import dry-run
lines strictly increases coverage and fails clearly against the current
hard-coded plural labels before implementation.

Question 4: Are the planned `format_count_label(...)` calls correct for the
slash-prefixed phrases (`1/1 import-ready row`, `1/1 valid file`)? Yes. The
numerator (`valid_row_count` or `valid_file_count`) is left as a raw integer
and only the denominator passes through `format_count_label(...)`. Since the
helper returns `f"{count} {label}"`, composing
`f"{numerator}/{format_count_label(denominator, 'import-ready row',
'import-ready rows')}"` yields `1/1 import-ready row` when the denominator is
1 and `2/2 import-ready rows` when it is 2. The singular form is chosen on
`count == 1`, which is the correct grammar rule for the denominator of the
ratio. The standalone `candidate`, `row`, and `file` labels are also correct.

Question 5: Are there any critical or important planning findings before
implementation? No. The plan is correct as written and may proceed to
implementation after addressing the minor stylistic notes at the implementer's
discretion.

## Verdict

Approve. The Stage 171 plan is correctly scoped, technically accurate, and
consistent with the project boundary rules and review protocol. Proceed with
Task 1 (RED), Task 2 (GREEN), and Task 3 (review, release gate, commit, push).
