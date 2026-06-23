# Stage 170 Release Review

Objective:

Fix the singular `1 row` grammar in the human-readable `community-signal-lint-dir` per-file lines, so a one-row file renders `1 row` instead of `1 rows`.

## Summary

Stage 170 is a single, presentation-only renderer edit confined to `render_community_signal_directory_lint_table`. The per-file f-string `{file.row_count} rows` was replaced with `{format_count_label(file.row_count, 'row', 'rows')}`, reusing the existing helper from `lint_formatting.py` that `format_finding_counts` already depends on for the adjacent finding-count segment of the same line. The result is grammatically correct at 0, 1, and N rows and brings the community-signals directory renderer into line with the manual-signals renderer, which already emits `1 row`.

Scope is tightly respected and matches the stated boundaries:

- Exactly one renderer f-string changed in `src/fashion_radar/community_signals.py:325`, plus a one-symbol import addition (`format_count_label`) on the existing `lint_formatting` import line.
- `lint_community_signal_directory(...)`, `lint_community_signal_file(...)`, all structured models, JSON output, CLI command flow, field/source/platform counts, finding ordering, finding messages, and finding-count grammar are unchanged.
- The top-level summary line `Rows: {result.row_count} total, {result.valid_row_count} import-ready` (community_signals.py:312) and the `Files:` summary line are intentionally untouched, consistent with the "no changes to top-level summary lines" boundary.
- One doc example synced (`docs/community-signal-quality.md`: `1 rows` -> `1 row`), preserving the protected substring `0 import-ready, 1 error, 3 warnings, 2 info` asserted by the docs test.
- One existing renderer test tightened with a `startswith("- exports/signals.csv: 1 row, 0 import-ready, ")` assertion.
- No source-acquisition, connector, scraping, browser-automation, platform-API, login/cookie, monitoring, scheduling, demand-proof, ranking, coverage-verification, or compliance-review behavior was introduced.

The working tree contains exactly the declared 10 files in the release-review scope (3 modified tracked files and 7 new review/spec files) plus this generated release-review artifact, which is expected for the review step itself. There are no extra unrelated edits. The release-review output record is clean and self-contained.

Review history is clean: the plan review records no critical or important findings, and the code review records no critical or important findings. Both artifacts are single, coherent review bodies with clean Summary / Findings / Verdict sections and no stubs, tool-status lines, duplicated text, truncation, or empty output, consistent with `docs/REVIEW_PROTOCOL.md` capture hygiene.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Test-name fidelity (non-blocking, carried forward from the code review). `test_render_community_signal_directory_lint_table_singularizes_finding_counts` now also guards the per-file row-count singularization, so its name describes only part of its coverage. The test body is correct and the added assertion is appropriate. A future rename such as `..._singularizes_row_and_finding_counts` would improve fidelity; cosmetic only, not required for release.
2. Top-level summary grammar nit (non-blocking, already recorded in the plan review). When aggregates are 1, the summary still renders `Rows: 1 total` and `Files: 1`, the same class of nit. This is correctly out of scope for Stage 170 and is noted only so it is not lost for a possible future stage.

## Verification Assessment

I independently re-ran the declared focused and release-gate evidence fresh. Every claim in the release prompt reproduces.

Focused evidence (re-run, fresh):

- GREEN renderer test:
  `uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts -q`
  -> 1 passed.
- Full renderer module:
  `uv --no-config run --frozen pytest tests/test_community_signal_lint.py -q`
  -> 90 passed.
- Docs non-regression guard:
  `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q`
  -> 1 passed.
- Lint on changed files:
  `uv --no-config run --frozen ruff check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py`
  -> All checks passed.
- Format on changed files:
  `uv --no-config run --frozen ruff format --check src/fashion_radar/community_signals.py tests/test_community_signal_lint.py`
  -> 2 files already formatted.

RED validity is reasoned rather than re-executed, because the renderer fix is already in place: pre-change the f-string emitted `{file.row_count} rows`, which for the `row_count=1` fixture yields `1 rows,`; the new assertion requires `1 row,`, which fails against `1 rows,`. The RED state is therefore genuine and the cycle meaningful, matching the code review's reasoning. The renderer test constructs its `CommunitySignalDirectoryLintResult` (with a one-row `CommunitySignalLintResult`) directly in memory and calls `render_community_signal_directory_lint_table` with no file I/O and no lint execution, so it cleanly isolates the grammar.

Release-gate evidence (re-run, fresh):

- Full suite (proxy env stripped):
  `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
  -> 1367 passed in 36.47s.
- First-run sample smoke:
  `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
  -> First-run sample smoke passed.
- Release hygiene:
  `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  -> Release hygiene checks passed.
- Full lint:
  `uv --no-config run --frozen ruff check .`
  -> All checks passed.
- Full format:
  `uv --no-config run --frozen ruff format --check .`
  -> 144 files already formatted.
- Public lockfile integrity (user mirror config disabled):
  `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
  -> Resolved 84 packages in 2ms; no lockfile churn.
- Whitespace: `git diff --check` -> exit 0, no output.
- Secret scan: `rg -n 'ghp_[A-Za-z0-9]+' .` -> no matches (exit 1).
- Git credential surface: `git config --get-all http.https://github.com/.extraheader` -> no token-bearing header configured (exit 1).

Scope and tree hygiene confirmed against the working tree:

- `git status` shows exactly 3 modified tracked files (`src/fashion_radar/community_signals.py`, `tests/test_community_signal_lint.py`, `docs/community-signal-quality.md`) and the declared review/spec files, with no unrelated edits.
- `git diff` is confined to the per-file renderer f-string, its import line, one test assertion, and one doc example line. No `uv.lock` churn, no data/report/dashboard/handoff artifacts, no SQLite or sidecar files, no generated reports, no virtual-env or cache paths. Release-hygiene plus first-run smoke corroborate this.

The `format_count_label` reuse is cycle-free: `lint_formatting.py` imports nothing from `community_signals.py`, and the same row-count call pattern is already established in `importers/manual_signals.py`, so the edit is idiomatic and dependency-neutral.

## Verdict

Approve. Stage 170 is in scope, renderer-wording only, and ready to commit and push. RED/GREEN, full suite (1367 passed), lint, format, smoke, hygiene, lockfile integrity, whitespace, secret, and git-credential checks were all reproduced fresh and match the release evidence. The plan and code review artifacts are clean, complete, and consistent with `docs/REVIEW_PROTOCOL.md`. No out-of-scope behavior, generated artifact, lockfile mirror churn, secret, token, or local private data entered the working tree. There are no critical or important findings; the two minor notes are non-blocking and informational.
