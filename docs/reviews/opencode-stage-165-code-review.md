# Stage 165 Code Review

## Summary

Stage 165 adds direct unit coverage for `fashion_radar.lint_formatting` via a
single focused module, `tests/test_lint_formatting.py`. The implementation
matches the design doc and plan exactly: one parametrized test for
`format_count_label(...)` covering zero/singular/plural, plus four direct
assertions for `format_finding_counts(...)` covering zero, singular, plural,
and mixed counts. No file under `src/` is modified, and `git status` shows
only the new test file plus review/spec/plan artifacts. The `info` invariant
(info stays `info` for every count) is pinned directly rather than only
indirectly through caller renderers. The Stage 165 objective is met.

## Findings

### Critical

None.

### Important

None.

### Minor

1. `format_count_label(...)` is currently only exercised with the
   `error`/`errors` pair (the parametrize block passes `"error", "errors"` for
   every row). In practice the helper is only ever called with three fixed
   pairs (`error/errors`, `warning/warnings`, `info/info`), all of which
   `format_finding_counts(...)` covers, so this is an observation rather than a
   gap. If the helper is ever generalized to new singular/plural pairs, adding
   a second parametrized pair would be worthwhile. Not blocking.

2. There is no explicit test asserting the comma-and-space separator contract
   independent of the full `format_finding_counts(...)` strings (e.g., that the
   join uses `", "`). The four `format_finding_counts(...)` assertions pin this
   implicitly, and the production helper is a 5-line function, so this is a
   style note only. Not blocking.

3. The plan review's minor finding about the long parametrized test name
   `test_format_count_label_uses_singular_only_for_one` carries over to the
   code. The name is accurate and matches the suite's descriptive style, so no
   change is requested.

## Verification Assessment

I independently re-ran each focused verification command against the working
tree.

- `uv --no-config run --frozen pytest tests/test_lint_formatting.py -q`:
  reproduced `7 passed`. This matches the claimed count (3 parametrized
  `format_count_label` rows + 4 `format_finding_counts` tests).
- `uv --no-config run --frozen pytest tests/test_source_packs.py
  tests/test_entity_pack_lint.py tests/test_community_signal_lint.py -q -k
  "render_"`: reproduced `14 passed, 114 deselected`, matching the evidence.
- `uv --no-config run --frozen ruff check tests/test_lint_formatting.py`:
  reproduced `All checks passed!`.
- `uv --no-config run --frozen ruff format --check tests/test_lint_formatting.py`:
  reproduced `1 file already formatted`.

Scope verification:

- `git status --short` shows only untracked additions: the new test module, the
  spec, the plan, and the two plan-review artifacts. No file under `src/` is
  modified, and no existing test module is modified.
- `git diff --stat HEAD` is empty for tracked files, confirming no production
  behavior change slipped in alongside the new tests.
- `grep` confirms the three callers (`source_packs.py`, `entity_packs.py`,
  `community_signals.py`) import only `format_finding_counts` and were not
  touched, so renderer output, CLI behavior, JSON output, docs output, lint
  semantics, strict-mode behavior, and row-count grammar are all unchanged.

Test-quality assessment:

- The tests are focused, readable, and limited to the helper contract. They do
  not reach into caller renderers, which keeps them resilient to renderer
  refactors.
- The `info` invariant is pinned directly and meaningfully:
  `format_finding_counts(1, 1, 1)` asserts `"1 info"` (not `"1 infos"`), and
  `format_finding_counts(2, 2, 2)` plus `format_finding_counts(1, 0, 2)`
  assert `"2 info"` at plural count. This pins the production code's
  `'info', 'info'` literal at both singular and plural counts, so the invariant
  would fail loudly if someone "fixed" it to `'info', 'infos'`.
- The tests do not overfit to caller renderers. They assert against the
  helper's own output strings, which is the correct contract boundary.

Plan and review artifacts:

- `docs/superpowers/specs/2026-06-23-stage-165-lint-formatting-helper-tests-design.md`
  and
  `docs/superpowers/plans/2026-06-23-stage-165-lint-formatting-helper-tests-plan.md`
  are clean, internally consistent, and match the implemented test module
  byte-for-byte (the plan's "exactly this content" block equals the shipped
  `tests/test_lint_formatting.py`).
- `docs/reviews/opencode-stage-165-plan-review-prompt.md` and
  `docs/reviews/opencode-stage-165-plan-review.md` are clean: no
  live-capture stubs, no tool-status chatter, no duplicated or truncated text.
  The plan review recorded two minor findings and no critical or important
  findings, which is appropriate.

Release-gate coverage (per the plan, Task 2 Step 3) remains the responsibility
of the subsequent release step; this code review only confirms the focused
gate, which is sufficient for the code-review node.

## Verdict

No critical or important findings. The Stage 165 implementation meets its
objective, respects every declared scope boundary, and ships clean focused
tests that pin the `info` invariant directly. Safe to proceed to release
verification.
