# opencode Stage 264 Plan Review (fallback/independent — no Claude Code review exists yet)

## Critical

**C1. Circular import between `readiness.py` and `templates.py` will break the package import.**

The plan specifies (Task 1, Step 3):
```python
# readiness.py
from fashion_radar.row_one.templates import _safe_external_url
```
and (Task 2, Step 3): *"In `templates.py`, import `build_row_one_readiness`"* — a top-level `from fashion_radar.row_one.readiness import build_row_one_readiness`, called inside the new `_render_edition_status`.

This creates `templates → readiness → templates`. Whichever module loads first sees the other only partially initialized:
- If `readiness` loads first, its `from ...templates import _safe_external_url` triggers `templates`, which then does `from ...readiness import build_row_one_readiness` before `build_row_one_readiness` is defined → `ImportError`.
- If `templates` loads first, symmetric failure on `_safe_external_url` (defined near the end of `templates.py`, line 533).

`tests/test_row_one_readiness.py` and `tests/test_row_one_render.py` each force one of these orderings, so Task 1 Step 5 and Task 2 Step 5 verification will both fail. Note the existing `render.py → templates` edge is safe *only* because `templates` does not import `render`; adding the reverse edge through `readiness` is what introduces the cycle.

**Fix before implementation:** break the edge. Preferred: extract `_safe_external_url` (and the duplicated `_isoformat_z`/`_utc_datetime`) into a small shared module (e.g. `fashion_radar/row_one/urls.py` or `row_one/safe.py`) and have `templates.py`, `render.py`, and `readiness.py` all import from there. Alternative: inline/duplicate the ~6-line `_safe_external_url` into `readiness.py` so it has no `templates` dependency. Either way, the plan must not have `readiness` import from `templates` while `templates` imports from `readiness`.

## Important

**I1. `row_one preview` cannot compute readiness from what `write_row_one_site_files` returns.**

`write_row_one_site_files` (workflows.py:99) returns `RowOneRenderResult`, whose frozen dataclass (render.py:23-27) exposes only `output_dir`, `index_path`, `story_count` — **not** the `RowOneEdition`. But `build_row_one_readiness(edition: RowOneEdition)` requires the edition object (for `sections`, per-section stories, `generated_at`, `edition_date`).

Task 3, Step 3 is self-contradictory: it says *"load `data/edition.json` only for path existence checks and compute readiness from a new private helper if needed."* A path-existence check yields no data, and the readiness helper's signature takes a `RowOneEdition`, not a JSON dict.

**Fix:** pick one explicitly and document it in the plan:
1. Extend `RowOneRenderResult` (and `render_row_one_site`/`write_row_one_site_files`) to carry the built `edition: RowOneEdition`, then call `build_row_one_readiness(result.edition)` in `preview`. (Cleanest; also useful for future surfaces. Update `RowOneRenderResult` tests in `test_row_one_render.py`.) **This changes an internal dataclass, not the `row-one-app/v1` JSON contract, so it is boundary-safe.**
2. Or add a JSON-payload adapter `build_row_one_readiness_from_app_payload(dict)` that derives counts/empty-sections from `data/edition.json` (`story_count`, `evidence_count`, `sections[].story_count`, `generated_at`, `edition_date`). This keeps `write_row_one_site_files` unchanged but requires a second helper and a test for it.

Option 1 is recommended. The plan must state the chosen path and update Task 3's test/impl accordingly.

**I2. Task 3 CLI test references `_write_empty_cli_project(tmp_path)` and `runner`, neither of which exist.**

`tests/test_row_one_cli.py` currently uses `_write_minimal_config(config_dir)` (constructing `config_dir`/`data_dir`/`reports_dir` manually) and invokes via inline `CliRunner().invoke(app, ...)`. There is no module-level `runner` and no `_write_empty_cli_project` helper anywhere in `tests/` (verified). As written, the test snippet will raise `NameError` at collection.

**Fix:** either (a) reuse the existing `_write_minimal_config` pattern and `CliRunner().invoke(app, ...)`, or (b) explicitly add a Step 0 that defines `_write_empty_cli_project` (returning the 3-tuple) and a module-level `runner = CliRunner()`. The plan must specify which.

## Minor

**M1. `_isoformat_z`/`_utc_datetime` duplication.** `render.py` already defines these private helpers; Task 1 re-declares them in `readiness.py`. Combined with C1, move them to the shared module. If C1 is fixed via the shared-module route, this is free; otherwise at least import from `render` rather than re-declaring (note `render`'s copies are also private — promoting both to shared is the clean answer).

**M2. `_render_status_metric` is unspecified.** Task 2 Step 3 says "Add `_render_status_metric()` below it" with no signature or HTML. The render test's assertions imply a bilingual label + value cell, but the implementer must invent the exact markup/CSS. Add the helper's signature and a minimal HTML template (and confirm it escapes via `_esc`) so the `.edition-status` CSS rules in Step 4 have a known structure to target.

**M3. Package-archive test fixture edit is ambiguous.** Task 4 Step 1 lists ROW ONE paths under "add ROW ONE required sdist files" but the existing fixture is the module-level `SDIST_FILES` list that `write_sdist` consumes. State explicitly: *extend the existing `SDIST_FILES` list in `tests/test_package_archives.py`* (and `SDIST_REQUIRED_PATHS` in the checker) so the two stay in sync. The new `src/fashion_radar/row_one/readiness.py` entry is only valid after Task 1 creates the file — ordering is already correct (Task 1 → Task 4), just call it out.

**M4. `edition_date` representation differs across surfaces.** The `row-one-app/v1` JSON emits `edition_date` as a full ISO datetime (`2026-07-02T04:00:00Z`); the readiness helper emits date-only (`2026-07-02`). This is intentional and fine, but add a one-line note in the design doc so reviewers don't later flag it as contract drift.

**M5. Weak assertions in render/CLI tests.** `assert "1" in index_html` (twice) and `assert "0" in index_html` are near-tautological; prefer `assert "Stories</span>" in ...` style or substring the metric label+value pair to actually guard the status strip. Not blocking.

**M6. Schedule-ordering check already covered.** The "run before row-one build --latest-only" ordering already exists as `test_row_one_schedule_prints_refresh_then_build` (test_row_one_cli.py:294). Adding it to `check_first_run_smoke.py` is reasonable defense-in-depth, but note the existing coverage so the plan doesn't over-claim novelty.

## Plan revision recommendations

1. Resolve **C1** by specifying the shared-safe-url/util module (or inline duplication) and remove the `readiness → templates` edge.
2. Resolve **I1** by extending `RowOneRenderResult` to carry `edition` (preferred) OR by defining a JSON-payload readiness adapter; update Task 3 impl + test to match.
3. Resolve **I2** by either reusing `_write_minimal_config`/inline `CliRunner` or adding an explicit helper-definition step.
4. Specify `_render_status_metric`'s signature/HTML (M2).
5. Clarify the `SDIST_FILES` extension (M3) and add the `edition_date` representation note (M4).
6. Keep the boundary restatements — they are accurate. Confirm explicitly that `render_index_html` (the only templates.py function feeding `index.html`) is disjoint from `build_row_one_app_payload` (which feeds `data/edition.json`), so the `row-one-app/v1` contract is provably unchanged.

## Verdict

**Revise plan before implementation.** The scope, boundaries, and product intent are sound and within Stage 264's allowed surface; no out-of-scope work (no scraping, platform APIs, scoring/contract changes, etc.) is introduced. However, the plan as written contains one build-breaking defect (C1, circular import) and two correctness gaps that make Tasks 2–3 non-executable as specified (I1 edition not returned; I2 missing test helpers). Fix C1, I1, and I2, plus the minor clarifications, and the plan is approved to proceed to TDD implementation.
