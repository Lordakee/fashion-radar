# Stage 182 Plan Review

## Critical Findings

None.

## Important Findings

None.

The Stage 182 plan is approved for implementation. It is a minimal, correctly
scoped hardening of the existing default-artifact guard that satisfies the
Stage 51 release-review follow-up.

## Minor Findings

1. The new test is placed "immediately after
   `test_default_artifact_guard_detects_new_repo_data_and_report_files`"
   (`docs/superpowers/plans/2026-06-24-stage-182-first-run-config-artifact-guard-plan.md:50-51`),
   which splits the existing created/changed/deleted data-report guard block by
   inserting before the `changed` and `deleted` tests
   (`tests/test_first_run_smoke.py:3567`, `:3590`). This is purely cosmetic and
   does not affect correctness. Optional: place the new test after the
   `deleted` test to keep the data-report trio contiguous, or leave as-is since
   the new test is itself a "created" case and groups naturally with the
   existing created test.

2. Only the "created" case is tested for generated config files; "changed" and
   "deleted" config cases are not. This is acceptable because config files are
   folded into the same snapshot dict and reuse the identical diff logic already
   covered by the data/report changed/deleted tests
   (`tests/test_first_run_smoke.py:3567`, `:3590`), so a single created test is
   sufficient to prove inclusion. No change required.

## Review Focus Answers

### 1. Does the plan satisfy the objective?

Yes. The plan extends `snapshot_default_artifacts`
(`scripts/check_first_run_smoke.py:2302`) to include exactly
`configs/sources.yaml`, `configs/entities.yaml`, and `configs/scoring.yaml`
when present. This snapshot is taken before the smoke flow at line 2385
(`run_smoke`) and re-checked at line 2394, so an accidental repo-local write to
any of the three generated configs during the real smoke flow will now be
detected.

### 2. Does the plan avoid over-scanning and avoid treating tracked assets as generated?

Yes. The implementation checks exactly three named files via `path.is_file()`
and never walks the `configs/` tree. Tracked examples, source packs
(`configs/source-packs/`), entity packs (`configs/entity-packs/`), and
templates (`*.example.yaml`, `src/fashion_radar/templates/...`) are not in the
constant and are therefore never treated as generated artifacts. The three
targets are precisely the gitignored generated configs (`.gitignore:38-40`).

### 3. Is the proposed RED meaningful?

Yes. Before implementation, `snapshot_default_artifacts` only scans `data/` and
`reports/`, so creating the three config files after the snapshot produces no
diff and `assert_default_artifacts_unchanged` does not raise. The new test's
`pytest.raises(smoke.SmokeError)` therefore fails with "DID NOT RAISE", proving
the guard currently misses repo-local config writes. The RED is meaningful and
isolates the intended behavior.

### 4. Is the minimal implementation sufficient to catch created, changed, and deleted generated config files?

Yes. Each existing config file is added to the snapshot dict keyed by its
relative path (`relative_path` is equivalent to
`path.relative_to(repo_root)` here, so keying is consistent with the data/report
loop). The existing diff logic in `assert_default_artifacts_unchanged`
(`scripts/check_first_run_smoke.py:2314-2331`) computes created/changed/deleted
from path-set membership and digest comparison, so all three cases are covered
for config files exactly as they are for data/reports, with no additional diff
code needed.

### 5. Are focused verification commands sufficient before the full release gate?

Yes. Task 3 Step 1 runs the new test plus the three existing guard tests
(created/changed/deleted for data/reports), the real smoke script
(`python scripts/check_first_run_smoke.py --repo-root .`), and ruff
check/format on the two touched files. This proves the new behavior and guards
against regressions in the existing created/changed/deleted data-report
detection before the full release gate in Task 4. The full gate (Task 4) then
runs the complete pytest suite, release hygiene, repo-wide ruff, lock check,
and secret/extraheader scans.
