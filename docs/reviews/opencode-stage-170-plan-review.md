# Stage 170 Plan Review

Objective:

Fix singular `1 row` wording in human-readable `community-signal-lint-dir`
per-file lines.

Files reviewed:

- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`
- `docs/superpowers/specs/2026-06-23-stage-170-community-signal-directory-file-row-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-170-community-signal-directory-file-row-grammar-plan.md`
- `src/fashion_radar/community_signals.py`
- `tests/test_community_signal_lint.py`
- `docs/community-signal-quality.md`

## Summary

The stage is correctly scoped to a single presentation-only grammar defect: the
per-file directory lint line in
`render_community_signal_directory_lint_table(...)` hardcodes the plural `rows`
(`src/fashion_radar/community_signals.py:325`), so a one-row file renders
`- exports/b.csv: 1 rows, ...`. The plan fixes that one f-string, tightens the
right existing renderer test, and syncs the one matching doc example.

All factual claims in the plan check out against the current source:

- `format_count_label(count, singular, plural)` exists in
  `src/fashion_radar/lint_formatting.py:4` with the exact signature the plan
  uses; it returns `"1 row"` for count 1 and `"0 rows"` / `"2 rows"` otherwise.
- `format_finding_counts` (already imported in
  `community_signals.py:15`) is built on `format_count_label`, so
  `lint_formatting` is already a leaf dependency of this module. The added
  import introduces no cycle and no new dependency surface.
- The target test,
  `test_render_community_signal_directory_lint_table_singularizes_finding_counts`
  (`tests/test_community_signal_lint.py:719`), already constructs a synthetic
  `CommunitySignalLintResult` with `row_count=1` and already has a `file_line`
  lookup, so the added `startswith(...)` assertion drops in cleanly and will be
  RED before the renderer change.
- The planned import line
  `from fashion_radar.lint_formatting import format_count_label, format_finding_counts`
  is already alphabetically ordered for ruff/isort.
- The doc change at `docs/community-signal-quality.md:316` is the only `1 rows`
  occurrence, and the protected substring
  `0 import-ready, 1 error, 3 warnings, 2 info` asserted by
  `tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples`
  is preserved after the edit.

The boundary constraints in `AGENTS.md` are respected: no changes to
`lint_community_signal_directory(...)`, `lint_community_signal_file(...)`,
structured models, JSON output, CLI flow, finding ordering/messages,
finding-count grammar, or top-level summary lines.

## Findings

### Critical

None.

### Important

None.

### Minor

- The aggregate top-level summary line
  `Rows: {result.row_count} total, {result.valid_row_count} import-ready`
  (`src/fashion_radar/community_signals.py:312`) and the
  `Files: {result.file_count}` line (`community_signals.py:311`) are left
  intentionally untouched, consistent with the stated scope ("No changes to
  top-level summary lines such as `Rows: ... total, ... import-ready`"). Note
  for a possible future stage: when totals are 1 these still render
  `Rows: 1 total` and `Files: 1`, which is the same class of grammar nit. It is
  correctly out of scope here; recording it only so it is not lost.
- The plan lists
  `test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples`
  as a focused check. It passes both before and after the doc edit (it guards
  finding-count grammar, not row-count grammar), so it functions as a
  non-regression guard rather than a RED check. That is appropriate; no change
  needed.

## Plan Assessment

1. **Appropriately scoped and safe?** Yes. One renderer f-string, one existing
   test tightened via TDD (RED then GREEN), one doc example. No model, JSON,
   CLI, or summary-line changes. The fix is mechanical and the existing
   `format_count_label` helper is reused rather than reinlined.

2. **Satisfies `AGENTS.md` boundary rules?** Yes. The change is human-readable
   presentation grammar only. It adds no connectors, scraping, browser
   automation, platform APIs, login/cookies, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, or
   compliance-review behavior. It stays within the `community-signal-lint-dir`
   read-only lint surface.

3. **Right place for the `1 row` assertion?** Yes.
   `test_render_community_signal_directory_lint_table_singularizes_finding_counts`
   already builds a `row_count=1` fixture and already has the `file_line`
   lookup, so the added
   `startswith("- exports/signals.csv: 1 row, 0 import-ready, ")` assertion is
   the minimal, lowest-risk place to lock the grammar. A separate test would be
   redundant.

4. **Correct helper to reuse?** Yes.
   `format_count_label(file.row_count, 'row', 'rows')` is the same helper
   `format_finding_counts` already uses for count-noun singular/plural logic,
   so grammar stays centralized and behaves correctly at 0, 1, and N.

5. **Critical/important planning findings before implementation?** None. The
   RED check, import edit, renderer edit, doc edit, focused checks, and release
   gate are all internally consistent and verified against current source.

## Verdict

Approve. The plan is safe, correctly scoped, TDD-ordered, reuses the correct
existing helper, respects all `AGENTS.md` boundaries, and its concrete diffs
match the current source. Proceed to implementation with no required changes.
