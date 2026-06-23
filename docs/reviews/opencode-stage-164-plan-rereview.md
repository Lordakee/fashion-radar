# Stage 164 Plan Rereview

## Summary

The updated Stage 164 plan resolves the single important finding (I1) from the
prior plan review. The community-signal directory singular test now uses
`path="exports/signals.csv"` consistently with its
`startswith("- exports/signals.csv:")` search, yielding a clean RED -> GREEN
path. Scope, helper extraction, RED-test coverage, directory aggregate/per-file
handling, docs update, and the verification/review/release/commit/push chain
remain sound. No critical or important findings remain. The plan is approved
to proceed to implementation.

## Question Answers

### 1. Is Stage 164 still correctly scoped to human-readable lint finding-count labels only?

Yes. The design and plan restrict changes to the human table `Findings:`
summary line in each renderer and the per-file finding-count suffix in the
community-signal directory renderer. The out-of-scope list (design lines
42-49) explicitly preserves JSON output, lint model/severity/sorting/strict-
mode/CLI flow, and row-count grammar (`1 rows`), and forbids historical
rewrites and connector/scrape/platform-API work. Verified against current
code: the in-scope literals are exactly the inline `{n} errors/warnings/info`
expressions at `entity_packs.py:123-126`, `community_signals.py:285-288`
(single file), `community_signals.py:315-318` (directory aggregate), and
`community_signals.py:323-327` (per-file suffix). Source-pack's already-
singularized `_format_finding_count` helper at `source_packs.py:344-346` is
the only behavior to preserve while relocating.

### 2. Does the updated directory singular test now have a clean RED -> GREEN path?

Yes. I1 is fixed. Task 2 Step 4 builds `CommunitySignalLintResult` with
`path="exports/signals.csv"` (plan line 298), and the search at plan line 335
is `line.startswith("- exports/signals.csv:")`. The directory renderer emits
`f"- {file.path}: ..."` (`community_signals.py:323-327`), so the produced per-
file line is `- exports/signals.csv: ...`, which matches the prefix. The four
`path="..."` values in Task 2 are now uniformly `exports/signals.csv`
(verified: plan lines 207, 245, 298, 383), so the singular and plural
directory tests are internally consistent.

RED behavior before implementation: the aggregate `Findings:` line renders
`1 errors, 1 warnings, 1 info` and the per-file suffix renders
`... 1 errors, 1 warnings, 1 info`, so both assertions
(`"Findings: 1 error, 1 warning, 1 info" in lines` and
`"1 error, 1 warning, 1 info" in file_line`) fail as clean assertion failures,
not as `StopIteration`. GREEN behavior after implementation: both assertions
pass. The `next(...)` lookup resolves because the directory's `findings` list
defaults to empty but `file_result.findings` is non-empty, so the
"No community-signal directory findings." early-return guard at
`community_signals.py:328-330` is not triggered.

### 3. Is moving the Stage 162 source-pack helper into a shared internal `lint_formatting.py` module still appropriate?

Yes. The proposed `format_count_label(count, singular, plural)` is behaviorally
identical to the existing private `_format_finding_count` at
`source_packs.py:344-346`, preserving the `count == 1 -> singular, else plural`
rule and the invariant `('info', 'info')` pair. The new
`format_finding_counts(error_count, warning_count, info_count)` composes three
`format_count_label` calls and matches the existing inline tuple shape used by
all three renderers, so the extraction removes triplication without changing
output. `_format_finding_count` is used only inside
`render_source_pack_lint_table` (call sites at `source_packs.py:111-113`), so
removing it after the import swap is safe. The module is internal (no
re-export, no CLI surface), consistent with the existing
`normalize_source_name`/`normalize_source_target` helper convention.

### 4. Do the planned RED tests prove the entity/community singular-count gaps while preserving plural/non-one wording?

Yes. Each surface has a singular/plural pair:

- Entity-pack (Task 1): singular asserts `Findings: 1 error, 1 warning, 1 info`
  (fails today against `1 errors, 1 warnings, 1 info`); plural asserts
  `Findings: 2 errors, 2 warnings, 2 info` (passes today, guards regression).
- Community-signal file (Task 2 Steps 2-3): same singular/plural pattern against
  `render_community_signal_lint_table`.
- Community-signal directory (Task 2 Steps 4-5): singular asserts both the
  aggregate `Findings: 1 error, 1 warning, 1 info` and the per-file substring
  `1 error, 1 warning, 1 info`; plural asserts the count=2 forms for both.

Zero-count (`0 errors, 0 warnings, 0 info`) is already pinned by existing
tests that remain unchanged: `test_render_source_pack_lint_table_includes_-
tag_counts` at `tests/test_source_packs.py:298`,
`test_render_community_signal_directory_lint_table_clean_directory` at
`tests/test_community_signal_lint.py:660`, and the entity-pack renderer slice
checks. The count=1 branch and the count!=1 branch (including 0 and 2) are
therefore both covered for all three surfaces. The directory tests exercise
both stored-aggregate counts (`CommunitySignalDirectoryLintResult.error_count`
et al.) and computed file counts (`CommunitySignalLintResult.error_count`
property), matching the design's risk note (design lines 138-139).

Model-field compatibility is verified: the test constructors use only fields
declared on `EntityPackLintResult` (`entity_packs.py:34-63`),
`CommunitySignalLintResult` (`community_signals.py:58-84`),
`CommunitySignalDirectoryLintResult` (`community_signals.py:87-107`), and
their finding models, all of which are `extra="forbid"` BaseModel classes. The
new imports (`EntityPackFinding`, `EntityPackLintResult`,
`CommunitySignalFinding`, `CommunitySignalLintResult`,
`CommunitySignalDirectoryLintResult`) reference module-level public classes
and are valid.

### 5. Does the plan cover community-signal directory aggregate and per-file finding-count output without drifting into row-count grammar?

Yes. Task 3 Step 4 wires the directory aggregate `Findings:` line through
`format_finding_counts(result.error_count, result.warning_count,
result.info_count)` and rewrites the per-file suffix from
`f"{file.valid_row_count} import-ready, {file.error_count} errors, "
f"{file.warning_count} warnings, {file.info_count} info"`
to
`f"{file.valid_row_count} import-ready, "
f"{format_finding_counts(file.error_count, file.warning_count, file.info_count)}"`.
The `{file.row_count} rows` prefix at `community_signals.py:324` is untouched,
so `1 rows` row-count grammar is intentionally preserved, matching design line
132 and the prior plan-review Q4. The directory tests assert the per-file line
substring without asserting the `1 rows` portion, so they do not lock in or
reject the row-count wording.

### 6. Are verification, docs, code-review, release-review, release-hygiene, commit, and push steps complete enough?

Yes. The plan's verification chain is complete:

- Focused RED checks per task (Task 1 Step 4, Task 2 Step 6, Task 4 Step 3).
- Broader GREEN renderer checks after wiring (Task 3 Step 6): runs
  `tests/test_source_packs.py`, `tests/test_entity_pack_lint.py`,
  `tests/test_community_signal_lint.py`, and `tests/test_cli.py -k
  "source_pack_lint or entity_pack_lint or community_signal_lint"`, plus ruff
  check and ruff format --check on all touched source and test files. The
  source-pack regression risk flagged in design Risks (lines 136-137) is
  covered by including `tests/test_source_packs.py` here.
- Docs update (Task 4): `docs/community-signal-quality.md` lines 313 and 316
  change `1 errors` to `1 error`; the new
  `test_community_signal_quality_docs_use_singular_one_finding_count_examples`
  guards both the `Findings:` form and the `0 import-ready, 1 error(s)` form.
  The `0 errors` line for `exports/a.csv` (docs line 315) is correctly left
  unchanged and is not caught by the `not in text` assertions.
- Code review (Task 5 Step 1) with prompt, opencode run, jq-based cleaning,
  and critical/important fix loop.
- Full release gate (Task 5 Step 2): pytest, first-run smoke, release
  hygiene, ruff check, ruff format --check, `UV_NO_CONFIG=1 uv lock --check`,
  `git diff --check`, `ghp_` token scan, and GitHub extraheader scan. Commands
  use `uv --no-config run --frozen`, matching AGENTS.md guidance.
- Release review (Task 5 Step 3) with prompt and cleaning.
- Final hygiene re-check (Task 5 Step 4).
- Commit and push (Task 5 Step 5) with an explicit file list covering all
  created/modified source, test, docs, spec, plan, and review artifacts, and
  `x-access-token` extraheader auth.
- Post-push checks (Task 5 Step 6): `git status --short --branch`, local and
  `origin/main` `rev-parse`, and extraheader re-scan.

### 7. Are there any critical or important findings before implementation?

No. The only important finding from the prior review (I1) is resolved by the
`path="exports/signals.csv"` correction, which is now uniform across all four
`CommunitySignalLintResult` constructions in Task 2. Re-examination of the
updated plan surfaced no new critical or important issues.

## Findings

### Critical

None.

### Important

None. (Prior I1, the directory singular-test path/prefix mismatch, is fixed.)

### Minor

- M1 (carried, design only): The design's focused-verification block (design
  lines 156-157) still runs
  `pytest tests/test_source_pack_quality_docs.py tests/test_cli_docs.py -q -k
  "community_signal_quality"`. `tests/test_source_pack_quality_docs.py`
  contains no `community_signal_quality` tests, so pytest selects zero from
  that file. Harmless. The plan's own Task 3 Step 6 verification is cleaner
  and does not carry this mismatch. No plan change required; optionally tidy
  the design's focused block to drop `tests/test_source_pack_quality_docs.py`.

- M2 (carried): The release gate (Task 5 Step 2 and design lines 164-173)
  omits `uv build`, `check_package_archives.py`, and installed-wheel smoke.
  This is consistent with Stage 162's lightweight cosmetic-fix scope and with
  REVIEW_PROTOCOL.md step 3 treating package smoke as conditional, so it is
  non-blocking. Confirm package smoke is intentionally out of scope for this
  stage, as the prior review noted.

- M3 (carried): `format_count_label` has no leading underscore despite the
  design calling the helper "intentionally internal". This matches the
  existing public-helper convention (`normalize_source_name`,
  `normalize_source_target`) in `source_packs.py`, so it is a style note, not
  a defect. No change required.

- M4 (carried): No entity-pack docs regression test is added. The only finding
  example in `docs/entity-pack-quality.md:47` is
  `Findings: 0 errors, 16 warnings, 61 info`, which has no singular count, so
  there is no affected example to guard. Non-blocking; noted for completeness.

## Verdict

No critical or important findings. The updated plan resolves I1, the
directory singular test now follows a clean RED -> GREEN path, and the scope,
helper extraction, test coverage, directory aggregate/per-file handling, docs
update, and verification/review/release/commit/push chain are complete and
consistent with AGENTS.md and REVIEW_PROTOCOL.md. Approved to proceed with
implementation.
