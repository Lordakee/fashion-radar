# Stage 270 Plan Rereview

**Verdict: APPROVED** (with one important test fix and a few minor cleanups to apply before/during coding)

The corrected plan is sound and addresses all nine review questions correctly: it builds on existing `refresh/schedule/local-ops/preview/serve` surfaces without duplicating them; keeps scheduling print-only; preserves the retention boundary (documents that `latest_only=True` only cleans known site children and explicitly does not delete dated reports); avoids OpenDesign, collectors, platform automation, account/cookie behavior, and compliance features; introduces `row-one-runtime/v1` as an additive, fixed-path, self-describing contract with its own schema and a manifest non-regression guard; scopes `row-one status` as validation/print-only; and the subprocess serve smoke uses an ephemeral port with clean terminate→kill teardown. Package archive, docs, first-run smoke, focused tests, and the full gate are covered.

## Critical findings
None.

## Important findings

1. **Serve-smoke CSS assertion will fail as written.** `tests/test_row_one_cli.py` Task 2 Step 5 asserts `assert "row-one" in fetched["/assets/row-one.css"]`. The CSS produced by `row_one_css()` (`src/fashion_radar/row_one/templates.py:173`) contains no `row-one` substring — only `RowOneSerif` (camelCase, no hyphen) and class names like `.edition-status`, `.site-header`. The JS assertion `assert "row-one:language" in fetched["/assets/row-one.js"]` is correct (the storage key `row-one:language` exists at `templates.py:625`), but the CSS one is not. Replace the CSS assertion with a substring that actually exists, e.g. `assert "RowOneSerif" in fetched["/assets/row-one.css"]` (or `":root"`, `"--paper"`, `".edition-status"`).

## Minor findings

2. **`validate_row_one_runtime` signature is inconsistent with its sibling.** Task 3 Step 3 specifies `validate_row_one_runtime(runtime_payload: str, *, expected_story_count: int)`, but the existing `validate_row_one_manifest(manifest_payload: Any, edition_payload: Any)` (`scripts/check_first_run_smoke.py:1106`) takes parsed dicts and is invoked via `validate_json_output(...)` wrappers. Make the new helper take a parsed dict (`runtime_payload: Any`) for consistency, and call it the same way manifest validation is called at `check_first_run_smoke.py:2913`.

3. **Render insertion point could be more explicit.** Task 1 Step 4 shows building/writing `runtime.json` before rebuilding `manifest_payload`, but `render.py:61-65` currently builds the manifest payload then writes `manifest.json`. State explicitly that the runtime block is inserted between the `edition.json` write (`render.py:57-60`) and the `manifest_payload = build_row_one_manifest_payload(...)` line (`render.py:61`), keeping `data/runtime.json` adjacent to the other data files.

4. **Docs drift test style.** Task 3 Step 1 asserts raw substrings (e.g. `"http://<LAN-IP>:8787"`) while every existing test in `tests/test_row_one_docs.py` uses `_normalized(text)` (whitespace-collapsed + casefolded). Either follow the `_normalized` convention or keep raw but be aware the LAN-IP assertion is case-sensitive; the existing doc already contains the exact `http://<LAN-IP>:8787` form so it will pass, but normalizing is more robust.

5. **Status JSON payload redundancy (optional).** The `row-one status --json` payload embeds the full `manifest` and `runtime` dicts plus a top-level `story_count`. Since `runtime.counts.story_count` already carries the count, the separate `story_count` key is redundant. Harmless; leave as-is or drop it.

## Suggested plan changes (exact references)
- `docs/superpowers/plans/2026-07-03-stage-270-row-one-runtime-readiness-plan.md` Task 2 Step 5: change `assert "row-one" in fetched["/assets/row-one.css"]` → `assert "RowOneSerif" in fetched["/assets/row-one.css"]`.
- Same plan, Task 3 Step 3: change `validate_row_one_runtime(runtime_payload: str, *, expected_story_count: int)` to accept a parsed dict and document that it is called via `validate_json_output("row-one runtime", row_one_runtime_path.read_text(...))`, mirroring the `validate_row_one_manifest(...)` call at `scripts/check_first_run_smoke.py:2913`.
- Same plan, Task 1 Step 4: make the insertion point explicit relative to `src/fashion_radar/row_one/render.py:57-65`.

The plan is approved for implementation after applying the important CSS-assertion fix; the minor items can be absorbed during the relevant tasks.
