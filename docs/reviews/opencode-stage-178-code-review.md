# Stage 178 Code Review

Objective:

Add focused regression guards for community handoff directory check renderer
count labels and unavailable candidate preview output.

## Summary

The Stage 178 implementation is a clean, test-only hardening stage that closes
all three minor coverage notes carried over from
`docs/reviews/opencode-stage-171-code-review.md`. The change set is confined to
`tests/test_community_handoff_check.py`: the existing singular renderer test is
renamed to `..._uses_singular_count_labels` (body unchanged), and two new
renderer-scoped exact-equality tests are appended. No runtime, model, CLI,
importer, candidate-scoring, JSON-shape, dependency, or lockfile behavior
changed; `git status` shows the only modified tracked file is the test module,
and `git diff --stat` reports `+100/-1` there, with the single deletion being
the old singular test name.

The three new/renamed assertions trace exactly against the renderer. For the
plural guard, the forced counts flow through
`render_community_handoff_directory_check_table(...)` at
`src/fashion_radar/community_handoff_check.py:169` and
`format_count_label(count, singular, plural)` at
`src/fashion_radar/lint_formatting.py:4` to produce
`Lint: 2 files, 2/2 import-ready rows, 2 errors`,
`Candidate preview: 2 candidates from 2 rows`, and
`Import dry-run: 2/2 valid files, 2 rows, 2 errors`. The slash-prefixed
numerators (`valid_row_count`, `valid_file_count`) stay raw and only the
denominators pass through `format_count_label(...)`, keyed off the denominator
count, which is the correct noun referent. For the unavailable guard, the
`candidate_preview is None` branch sets `candidate_preview_text = "unavailable"`
at `src/fashion_radar/community_handoff_check.py:175`, yielding
`Candidate preview: unavailable`, and the
`candidate_preview_unavailable` finding is appended at
`src/fashion_radar/community_handoff_check.py:106` and rendered through
`_table_cell(...)` at `src/fashion_radar/community_handoff_check.py:217`; since
the finding fields contain no `|`, `\r`, or `\n`, `_table_cell` is a no-op and
the rendered row matches the asserted string exactly.

The new tests reuse the existing deterministic fixture flow
(`_write_config`, `_write_csv_directory`, `_load_candidate_config`) and do not
overcouple to candidate scoring internals. The plural test builds a real
two-file result, asserts `result.candidate_preview is not None`, then uses
`model_copy` to force plural counts across all three sections — the same pattern
approved in Stage 171's singular test, and appropriate for a count-label guard
where the decoupling between forced counts and the empty `result.findings` list
is intentional. The unavailable test reuses the proven `bad.csv` scenario, asserts
`result.candidate_preview is None`, and scopes its assertions to the
candidate-preview summary line and the single stable finding row.

## Findings

### Critical

None.

### Important

None.

### Minor

1. The plural test's `model_copy` semantic decoupling is intentional and
   pre-approved (Stage 171 singular test, plan review minor note 1), so it needs
   no change. Because `result.findings` is not overridden while
   `community_signal_lint.error_count` and `import_dry_run.error_count` are
   forced to `2`, the renderer emits "No community handoff check findings." even
   though the Lint/Import dry-run lines report "2 errors". This is correct for a
   renderer-grammar guard and does not assert `result.ok` or finding consistency.
   Awareness note only.

2. The plural guard's RED value is complementary rather than standalone-strong.
   With counts forced to `2`, `format_count_label` always selects the plural
   branch, so a hypothetical regression that hard-coded singular forms would be
   caught, but a regression that merely dropped `format_count_label` for these
   nouns (reverting to literal plurals) would still pass the plural test. That
   gap is fully covered by the singular test, which would fail under such a
   revert. The two tests together pin both grammar branches; no action needed.

3. The unavailable test exercises the same `bad.csv` input already covered by
   `test_check_community_handoff_directory_preserves_lint_and_dry_run_on_candidate_failure`
   at `tests/test_community_handoff_check.py:114`. The duplication is deliberate
   and narrow: the existing test asserts structural state (`candidate_preview is
   None`, finding check names), while the new test pins the exact rendered
   summary line and finding row. This is appropriate renderer-output coverage and
   not a defect.

## Verification Assessment

I confirmed the implementation scope, the exact-line correctness, and the
focused verification evidence, and independently reproduced the GREEN results.

Scope. `git status --short` shows only `tests/test_community_handoff_check.py`
modified (plus the expected new untracked spec/plan/review artifacts).
`git diff tests/test_community_handoff_check.py` shows the singular test rename
(one function-name line changed, body byte-for-byte preserved) followed by two
verbatim additions from the approved plan. No source files, models, CLI, config,
dependency manifests, or `uv.lock` changed. The `community-handoff-check-dir`
scope boundary (local read-only, no source acquisition, no connectors, no
scraping, no browser automation, no platform APIs, no monitoring, no scheduling,
no ranking, no coverage verification, no compliance-review product feature) is
respected.

Exact-line correctness. I traced each asserted string through the renderer and
the `format_count_label` contract. All six plural assertions and both
unavailable assertions reproduce current renderer output exactly, including the
raw-integer slash numerators and the `_table_cell`-transparent finding row.

Existing-test integrity. The diff confirms no existing test was weakened or
deleted; the only removal is the stale singular test name. The module test count
rose from 7 (recorded in the Stage 171 review) to 9, consistent with two tests
added and none removed.

Independent reproduction. I ran the focused module and lint commands:

- `uv --no-config run --frozen pytest tests/test_community_handoff_check.py -q`
  — 9 passed.
- `uv --no-config run --frozen ruff check tests/test_community_handoff_check.py`
  — All checks passed.
- `uv --no-config run --frozen ruff format --check tests/test_community_handoff_check.py`
  — 1 file already formatted.

The prompt's RED/absence claims are consistent and inherent: neither new test
name existed before this stage, and the count-label and unavailable branches
were only indirectly exercised prior to Stage 178. The prompt's GREEN claims
(plural+singular pair -> 2 passed; unavailable -> 1 passed; module -> 9 passed;
ruff check and format clean) match my independent run. The focused verification
commands are sufficient for this stage's release gate; the full release gate
(proxy-stripped full pytest, smoke and hygiene scripts, `UV_NO_CONFIG=1 uv lock
--check`, `git diff --check`, token and extraheader absence checks) belongs to
the Stage 178 release step per `docs/REVIEW_PROTOCOL.md` and is not required for
this code review.

## Verdict

Approve. The implementation matches the approved Stage 178 plan exactly, all
three Stage 171 follow-up notes are addressed (singular rename, exact plural
guard, exact unavailable candidate-preview guard), the assertions are correct
and renderer-scoped without overcoupling to scoring internals, and no runtime,
source-acquisition, connector, scraping, platform-API, ranking,
coverage-verification, compliance-review, dependency, or lockfile behavior
changed. There are no critical or important findings; the three minor notes are
awareness items and do not block release verification.
