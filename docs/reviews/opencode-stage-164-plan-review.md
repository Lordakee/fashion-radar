# Stage 164 Plan Review

## Summary

Stage 164 is correctly scoped to making human-readable lint finding-count
labels consistent across the source-pack, entity-pack, and community-signal
lint surfaces. The shared-helper approach is sound, the RED/GREEN structure
follows the project test-first workflow, and the verification, review,
release-gate, commit, and push steps are complete. There are no critical
(blocking) findings. There is one important finding (a broken RED test that
can never reach GREEN as written) and a few minor notes.

## Question Answers

1. Scope: correctly limited to human-readable lint finding-count labels?
Yes. The spec and plan restrict changes to the human table `Findings:`
summary and per-file finding-count suffixes. JSON output, lint
model/severity/sorting/strict-mode/CLI flow, and row-count grammar
(`1 rows`) are explicitly out of scope and are preserved. This closes the
gap flagged as M1 in the Stage 162 release review.

2. Moving the Stage 162 helper into a shared `lint_formatting.py`?
Appropriate. The local `_format_finding_count(...)` at
`source_packs.py:344` is behaviorally identical to the proposed
`format_count_label`, and entity/community renderers currently inline
`{n} errors` literals at `entity_packs.py:124` and
`community_signals.py:286,316,325-326`, so a shared helper removes
triplication. The `count == 1 -> singular, else plural` rule and the
invariant `info` label are preserved, matching Stage 162. The negative-
count branch noted as M3 in the Stage 162 release review is preserved and
remains unreachable (counts derive from `_count_findings` or stored
non-negative aggregates).

3. Do the planned RED tests prove the gaps while preserving plural wording?
Mostly; see Important finding I1. The entity-pack pair (Task 1) and the
community-signal file pair (Task 2 Steps 2-3) cleanly RED-then-GREEN and
guard the plural wording. The community-signal directory plural test
(Task 2 Step 5) is correct. The community-signal directory singular test
(Task 2 Step 4) cannot reach GREEN as written due to a path/prefix
mismatch (I1).

4. Directory aggregate + per-file finding-count output without drifting
into row-count grammar?
Yes. The aggregate `Findings:` line and each per-file suffix both route
through `format_finding_counts(...)`. The per-file replacement keeps
`{file.row_count} rows, {file.valid_row_count} import-ready` verbatim, so
`1 rows` row-count grammar is intentionally preserved, matching the
design's "left unchanged" note.

5. Verification, docs, code-review, release-review, release-hygiene,
commit, and push steps complete enough?
Yes, with minor notes. The plan includes focused RED checks, broader
GREEN renderer checks, a docs regression test, opencode code review, the
full release gate (pytest, first-run smoke, release hygiene, ruff
check/format, lock --check, git diff --check, token scan, extraheader
check), opencode release review, final hygiene re-check, commit, push,
and post-push verification. See minor M2 for one optional gap.

6. Critical or important findings before implementation?
No critical/blocking findings. One important finding (I1) must be fixed
before the RED/GREEN flow can complete.

## Important Findings

I1 - Community-signal directory singular test has a path/prefix mismatch
and can never reach GREEN.

In Task 2 Step 4, `test_render_community_signal_directory_lint_table_-
singularizes_finding_counts` builds `file_result` with
`path="signals.csv"` (plan line 298) but then searches
`file_line = next(line for line in lines if line.startswith("- exports/signals.csv:"))`
(plan line 335). The directory renderer emits `f"- {file.path}: ..."`
(community_signals.py:323-327), so the produced line is
`- signals.csv: ...`, which never starts with `- exports/signals.csv:`.
`next(...)` therefore raises `StopIteration` before the two assertions
are reached. The test ERRORs (not cleanly fails) both before and after
implementation; it would never go GREEN by changing only the renderer.

This is internally inconsistent with:
- The plural sibling test (Task 2 Step 5), which correctly uses
  `path="exports/signals.csv"` with the same
  `startswith("- exports/signals.csv:")` search.
- The design's expected output
  (`- signals.csv: 1 rows, 0 import-ready, 1 error, 1 warning, 1 info`,
  design line 129), which uses the bare `signals.csv` path.

Fix (pick one):
- Set `path="exports/signals.csv"` in the singular test to match the
  plural test and the `startswith` search; or
- Change the search to `line.startswith("- signals.csv:")` to match
  `path="signals.csv"` and the design's expected output.

Either fix yields a clean RED (assertion failure on `1 errors`/`1 warnings`)
before implementation and GREEN after.

## Minor Findings

M1 - Design focused-verification includes a file with no matching tests.
The design's focused block runs
`pytest tests/test_source_pack_quality_docs.py tests/test_cli_docs.py -q -k "community_signal_quality"`,
but `tests/test_source_pack_quality_docs.py` contains only
`test_source_pack_quality_docs_*` tests with no `community_signal_quality`
match. Harmless (pytest selects zero from that file), but the command could
be reduced to `tests/test_cli_docs.py`. Not blocking.

M2 - Release gate omits package-build/archive and installed-wheel smoke.
Task 5 Step 2 (and the design's release gate) include lockfile `--check`,
first-run smoke, release hygiene, ruff, token scan, and extraheader check,
but not `uv build` / `check_package_archives.py` / installed-wheel smoke
that `docs/REVIEW_PROTOCOL.md` step 3 documents for upload. This is
consistent with Stage 162's lightweight scope for a cosmetic text fix and
those checks are optional/conditional, so it is non-blocking; just confirm
the stage intentionally treats package smoke as out of scope.

M3 - `format_count_label` is exposed without an underscore prefix despite
being described as internal. The design says the helper is "intentionally
internal," yet `format_count_label` (used only by `format_finding_counts`)
has no leading underscore. This is consistent with the existing
`normalize_source_name` / `normalize_source_target` public-helper convention
in `source_packs.py`, so it is not a defect; noted only in case the author
wants a leading underscore for the genuinely-internal sub-helper.

M4 - No entity-pack docs regression test added.
`docs/entity-pack-quality.md:47` shows
`Findings: 0 errors, 16 warnings, 61 info` (no singular count), so there is
no affected example to guard and no doc change is required there. The plan's
docs test covers only `community-signal-quality.md`, which is the only
user-facing doc with a singular finding-count example. Non-blocking; noted
for completeness.

## Verdict

No critical findings. Fix I1 before implementation so the directory singular
test follows a clean RED -> GREEN path. With I1 addressed, the plan is
approved to proceed.
