## Stage 267 Plan Re-Review

### Prior blocking findings — status

- **C1 (strict command sequence) — FIXED.** Task 2 Step 4 (plan:244-265) now inserts the serve tuple "immediately after the existing `row-one preview` tuple and before the existing `row-one local-ops` tuple". Verified: preview tuple ends at `tests/test_first_run_smoke.py:1868`, local-ops starts at `:1869`; the smoke serve call is placed after the edition.json check (`check_first_run_smoke.py:2827`) and before the local-ops call (`:2828`), so recorded order matches expected order.
- **I1 (`row-one serve --dry-run` phrase in row-one.md) — ADDRESSED.** Plan:333-334 adds an explicit "preserve" instruction and the docs test pins the phrase (plan:299). The phrase currently lives only at `docs/row-one.md:115`; the TDD red→green cycle (Task 3 Step 2 fail → Step 4 pass) now catches any accidental drop.
- **M2 (inlined review-prompt block) — FIXED.** Plan ends cleanly at the commit/push step (plan:451); no `*** Add File:` block remains.

### Critical
None.

### Important
- **I1 (new) — first-run.md docs test will fail on capitalization.** The assertion is `assert "first-run smoke verifies the ROW ONE manifest" in first_run` (lowercase `f`, plan:300), but the docs edit writes a new paragraph starting `"First-run smoke verifies the ROW ONE manifest"` (capital `F`, plan:339). `docs/first-run.md` contains neither form today (`:130` has only the preview command sample), so Task 3 Step 4's "Expected: PASS" cannot hold — Python `in` is case-sensitive. Fix by aligning casing (capitalize the assertion string, or integrate the phrase mid-sentence).

### Minor
- **M1 — expected-tuple snippet references an undefined name.** Task 2 Step 4's tuple uses `str(reports_dir / "row-one" / "site")` (plan:255), but `expected_first_run_flow_commands(context, example_csv)` has no `reports_dir` local; every adjacent tuple uses `str(context.reports_dir / ...)`. The actual smoke call records `str(context.reports_dir / "row-one" / "site")`, so the snippet must be `str(context.reports_dir / "row-one" / "site")` or the strict-equality check NameErrors/fails. Intent is obvious from neighboring tuples, hence Minor.

### Verified correct
- Preview keeps `JSON:` (`cli.py:1460`) and adds `Manifest:` after it; no build/render behavior change. ✓
- Manifest validator fields match `render.py:122-156` (`contract_version`, `app_contract.path`, `site.index_path/manifest_path`, counts vs edition, readiness ready/empty). The fake's `edition.json` is correctly upgraded from `"{}"` (`test:4250`) to `{story_count:0, evidence_count:0}` so the count comparison holds. ✓
- `row-one serve --dry-run` emits exactly `Open: http://127.0.0.1:8787` (`cli.py:1505-1509`, `server.py:25`) and calls `validate_row_one_site_dir` without binding a socket; generated site has the `.row-one-site` marker + `index.html`. ✓
- Smoke helpers all exist (`assert_equal:518`, `validate_json_output:511`, `assert_non_empty_file:2522`, `run_cli:2483`, `assert_output_contains_text:1064`, `SmokeError:445`, `Mapping` imported). ✓
- Serve dry-run fake branch is scoped with `"--dry-run" in args`, so it won't swallow the `row-one serve --help` help call. ✓
- CLI test uses `output_dir` (`test_row_one_cli.py:115,143`), matching Task 1's new assertions. ✓
- Scope stays clear of `row-one-app/v1` schema, provenance, collectors, scoring, scheduling, cleanup, deployment, image/LLM, and compliance-review. ✓

### Verdict
**Approve with revisions.** The three blocking findings are resolved. Fix the new Important (first-run.md assertion/docs casing mismatch) and the Minor tuple name (`context.reports_dir`) before implementation; both are one-line edits. With those, the plan is feasible and the tests are executable as written.
