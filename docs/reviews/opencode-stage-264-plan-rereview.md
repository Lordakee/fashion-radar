# opencode Stage 264 Plan Rereview

## Critical

None. C1 from the first review is fully resolved. The revised plan introduces `fashion_radar/row_one/utils.py` (stdlib-only: `safe_external_url`, `isoformat_z`, `utc_datetime`), and `readiness.py` imports only from `utils` and `models` — there is no `readiness → templates` edge. The resulting graph is `templates → readiness → {models, utils}` and `templates → utils`, with no path back to `templates`, so no cycle can form regardless of import order. Verified against `render.py:10-17` (the existing `render → templates` edge stays safe because `templates` never imports `render`).

## Important

None. Both I1 and I2 are resolved and verified against the current codebase:

- **I1 resolved.** Task 3 Step 3 extends `RowOneRenderResult` with `edition: RowOneEdition` and sets it in `render_row_one_site`. I confirmed `RowOneRenderResult(` is constructed in exactly one place (`render.py:51`; the only other hit is a stage-260 plan doc, not code), so the change is fully contained. `write_row_one_site_files` (`workflows.py:140-141`) returns `render_row_one_site(...)` directly, so it propagates `edition` with no signature change — matching the plan's claim. `preview` then calls `build_row_one_readiness(result.edition)`. This is a private dataclass change; `data/edition.json` is still produced solely by `build_row_one_app_payload`, so the `row-one-app/v1` contract is provably untouched.
- **I2 resolved.** Task 3 Step 1 now uses `_write_minimal_config(config_dir)` (exists at `tests/test_row_one_cli.py:33`) and inline `CliRunner().invoke(app, ...)` (matches the existing `test_row_one_build_command_writes_empty_state_site` pattern at lines 77-101; `app` imported at line 13, `CliRunner` at line 11). No nonexistent helpers are referenced.

## Minor

**m1. `src/fashion_radar/row_one/utils.py` is missing from the Task 4 guardrail lists.** Task 1 Step 3 creates this shared module that `readiness.py` (and per the design, `templates.py`/`render.py`) imports from, but Task 4 Step 1/Step 3 enumerate `__init__.py`, `edition.py`, `models.py`, `readiness.py`, `render.py`, `server.py`, `templates.py` — not `utils.py`. setuptools will still ship it in the sdist, but the required-paths check won't guard the one module the new readiness layer hard-depends on. Add `"src/fashion_radar/row_one/utils.py"` to both `SDIST_REQUIRED_PATHS` (checker) and `SDIST_FILES` (test fixture) for symmetry with the other row_one modules.

**m2. `templates.py` dedup is stated but not instructed.** The design doc and the Task 1 Step 3 note say `templates.py`/`render.py` will import the shared helpers from `row_one.utils`, but Task 2 Step 3 only tells the implementer to `import build_row_one_readiness` into `templates.py`. Leaving the existing local `_safe_external_url` (`templates.py:533`) and `render.py`'s `_isoformat_z`/`_utc_datetime` (`render.py:181-188`) in place is harmless (no cycle either way), so this is not blocking — but the plan is internally soft on the M1 dedup it claims to fix. Either add an explicit "replace `templates._safe_external_url`/`render._isoformat_z`/`render._utc_datetime` with imports from `row_one.utils`" step, or drop the claim.

**m3. Carried M5 — weak render assertions unchanged.** `assert "1" in index_html` (twice) and `assert "0" in index_html` remain near-tautological and would pass against almost any page content. Prefer anchoring on the label+value pair (e.g. `"Stories</span>"` adjacency) so the status strip is actually guarded. Non-blocking.

**m4. Task 3 help test body is underspecified.** Step 2's RED command targets `test_row_one_preview_help_is_discoverable`, but Step 1 only says "Add a help test asserting `row-one preview --help` appears in CLI help output" with no body. The name is fixed by the RED command and the body is inferable from existing discoverability tests, but a one-line snippet would remove ambiguity.

## Positive checks

- Readiness derives solely from existing `RowOneEdition` fields; the test expectations in Task 1 match `_edition()` exactly: 1 story, 2 sections, 1 safe evidence link (the `javascript:` link is correctly excluded), `brand_moves` as the lone empty section, `2026-07-02T04:00:00Z` / `2026-07-02`, and the `ready`/`可阅读` labels. Empty-edition assertions also match (`RowOneEdition` is non-frozen, non-`validate_assignment`, so `edition.stories = []` mutates cleanly).
- `_render_status_metric` (Task 2 Step 3) is now fully specified with signature and HTML, escapes via `_esc`, and gives the Step 4 CSS a known `.edition-status`/`.edition-status-metric` structure to target.
- The `edition_date` representation divergence (date-only in readiness vs. ISO datetime in `row-one-app/v1`) is now documented in the design (lines 123-125), closing prior m4.
- `SDIST_FILES` extension is now explicit (prior m3 resolved, modulo m1 above).
- `format_row_one_site_access_message("127.0.0.1", …)` returns `Open: http://127.0.0.1:8787` (`server.py:25`), so the preview test's `assert "Open:" in result.output` holds under the default non-wildcard host — consistent with the design example.
- Schedule ordering check is genuine defense-in-depth; prior m6 acknowledged existing `test_row_one_schedule_prints_refresh_then_build` coverage, so no novelty overclaim.
- All six TDD task sequences are executable against the current codebase with the existing `_edition()`, `_write_minimal_config`, `CliRunner`, `row_one_app` command group, and `write_row_one_site_files` plumbing.
- Project boundaries preserved: no collection, scraping, platform APIs, scoring/ranking, scheduling-semantic, or `row-one-app/v1` contract changes; the readiness layer is display/visibility only.

## Verdict

**Approved to proceed to implementation.** All three prior blockers (C1, I1, I2) are fully resolved and verified against the codebase; no remaining Critical or Important issues. Address m1 (add `utils.py` to the package guardrail) within Task 4 before that task's verification, and ideally tighten m2/m3/m4 during their respective tasks. The plan is boundary-safe and its TDD steps are executable as written.
