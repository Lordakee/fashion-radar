# Stage 270 Plan Review — opencode (GLM 5.2 max, fallback reviewer)

**Repo:** `/home/ubuntu/fashion-radar`
**Artifacts reviewed:**
- `docs/superpowers/specs/2026-07-03-stage-270-row-one-runtime-readiness-design.md`
- `docs/superpowers/plans/2026-07-03-stage-270-row-one-runtime-readiness-plan.md`

Cross-checked against `src/fashion_radar/row_one/render.py`, `cli.py`, `server.py`, `ops.py`, `readiness.py`, `schemas/row-one-manifest.schema.json`, `tests/test_row_one_app_contract.py`, `tests/test_row_one_cli.py`, `tests/test_row_one_docs.py`, `tests/test_package_archives.py`, `scripts/check_first_run_smoke.py`, `docs/row-one.md`, `src/fashion_radar/__main__.py`.

## Verdict: NOT APPROVED

The approach (additive `row-one-runtime/v1`, validation-only `status`, real subprocess serve smoke, print-only scheduling, retention boundary, no OpenDesign/collectors/platform/compliance) is sound and well-scoped, and builds correctly on existing `refresh/schedule/local-ops/preview/serve`. However, there are **two blockers** that will make the plan fail as written, plus several issues to fix before coding.

## Critical findings (blockers)

**C1. Adding `runtime_path` to the manifest breaks the manifest schema and an existing test, and neither is in the plan.**
Plan Task 1 Step 5 modifies `build_row_one_manifest_payload` to add `"runtime_path": "data/runtime.json"` inside `site`. But:
- `schemas/row-one-manifest.schema.json:37` sets `site.additionalProperties: false` and `required: ["index_path", "data_path", "manifest_path", "assets_path", "details_path"]`. The added field is rejected → `tests/test_row_one_app_contract.py::test_row_one_manifest_schema_validates_generated_payload` (line 111) fails.
- `tests/test_row_one_app_contract.py::test_row_one_manifest_points_to_app_contract_and_site_paths` (lines 128–134) asserts `manifest["site"] == {...}` with exact equality; adding a key fails it.
- The plan's **Files** list does **not** include `schemas/row-one-manifest.schema.json`, and no step updates the existing exact-equality test.
- This also contradicts the design's own claim (`design.md:102–103`) that the runtime contract "does not change ... `row-one-manifest/v1`."

**Fix (pick one and make the design/plan consistent):**
- **(A, preferred for contract stability)** Drop Task 1 Step 2 and Step 5 entirely. Keep `row-one-runtime/v1` purely additive and self-describing at the fixed `data/runtime.json` path; do not touch the manifest. This matches the design's stated non-goal. Remove the `assert manifest["site"]["runtime_path"]` test (Step 2).
- **(B)** If the manifest must link to runtime, then add explicit steps: (1) update `schemas/row-one-manifest.schema.json` `site.properties` and `site.required` to include `runtime_path`; (2) update `test_row_one_manifest_points_to_app_contract_and_site_paths` to include the new key; (3) soften `design.md:102–103` to say the manifest gains one additive pointer. Also add `schemas/row-one-manifest.schema.json` to the plan's **Files** list and add a schema-drift test case for `site.runtime_path`.

**C2. The new docs test (Task 3 Step 1) asserts retention wording that the doc-update step (Task 3 Step 2) never adds.**
The new assertions require:
```python
assert "site output" in row_one_doc.lower()
assert "dated reports" in row_one_doc.lower()
```
Neither phrase exists in `docs/row-one.md` today, and Task 3 Step 2 only adds a "Runtime Status" section + a quickstart tweak. The design's "Retention Boundary" section explicitly requires documenting the site-output vs dated-reports distinction, but the plan never writes that wording. Result: the red→green test cannot go green.

**Fix:** Add an explicit Task 3 Step that inserts a "Retention Boundary" subsection into `docs/row-one.md` containing both "site output" and "dated reports" (e.g., "`latest_only=True` keeps only the latest ROW ONE **site output** children; **dated reports** (`fashion-radar-YYYY-MM-DD.*`) outside the site directory are not deleted."). Also add `data/runtime.json` to the "Generated Files" list (`docs/row-one.md:145–151`).

## Important findings (fix before coding)

**I1. `build_row_one_manifest_payload` signature/call mismatch.** Plan Step 4's render snippet calls `build_row_one_manifest_payload(edition, app_payload, runtime_payload)` (3 args), but the current signature (`render.py:124`) takes only `(edition, app_payload=None)`, and Step 5 only adds a constant string (no need for `runtime_payload`). Either drop the third argument (call with `(edition, app_payload)`) or, if following option B above, document the signature change explicitly. As written it will raise `TypeError`.

**I2. Subprocess serve smoke only fetches `/data/runtime.json`, not the asset set the design promises.** Design "Serve Smoke" says fetch `/`, `/data/manifest.json`, `/data/edition.json`, `/data/runtime.json`, `/assets/row-one.css`, `/assets/row-one.js`. The plan's Task 2 Step 5 test fetches only `/data/runtime.json`. Either expand the test to fetch (and assert 200 + minimal body for) the full set, or relax the design's claim. Also assert the loop actually succeeded (e.g., set a flag when status==200 and `assert succeeded`) so a silently-empty `body` doesn't masquerade as a pass.

**I3. First-run smoke insertion point is unspecified.** Task 3 Step 3 says "update ROW ONE smoke" generically. `scripts/check_first_run_smoke.py` has dedicated validators (`validate_row_one_manifest`, `validate_row_one_schedule_output`). Specify exactly: which function to add (`validate_row_one_runtime`), where it is called, and that `row-one status` is invoked via the existing `cli_command(...)` helper with `--host 127.0.0.1 --port 8787` and asserted via `assert_output_contains_text`.

**I4. `--json` diverges from the established CLI output convention.** Every other read command uses `--format {table,json}`. The design mandates `--json`, but note this is a precedent break; if acceptable, add a one-line note in `docs/cli-reference.md` that `row-one status` uses `--json` (not `--format json`) so users aren't surprised.

## Minor findings (optional)

- **M1.** Runtime `readiness.status` and `readiness.en` are always identical (`status = readiness.readiness.en`). Slightly redundant; acceptable, but consider dropping `status` or documenting why both exist.
- **M2.** Ephemeral-port smoke has a benign TOCTOU race between socket close and subprocess bind (standard pattern; same as existing `test_row_one_serve_dry_run_does_not_bind_requested_port`). Acceptable.
- **M3.** Task 4 Step 3 runs `tests/test_release_hygiene.py`, `tests/test_row_one_render.py`, `tests/test_row_one_edition.py`, `tests/test_row_one_readiness.py`, `tests/test_scheduling.py`, `tests/test_scheduling_docs.py` — confirm these paths exist before relying on the gate (they appear standard for this repo, but the plan should verify rather than assume).
- **M4.** Command ordering note: inserting `status` before `schedule` is fine functionally; just keep help text consistent.

## Suggested concrete plan changes

1. **Decide C1 now.** Recommended: adopt option (A) — remove manifest linkage entirely (delete Task 1 Step 2 and Step 5; remove `runtime_path` references). This keeps `row-one-manifest/v1` truly unchanged and removes three downstream breakages with no loss of runtime-readiness value (clients read `data/runtime.json` directly).
2. **Add a "Retention Boundary" doc step** to Task 3 with the exact "site output" / "dated reports" wording, and add `data/runtime.json` to the Generated Files list.
3. **Fix the `build_row_one_manifest_payload` call** in Step 4 to match the chosen option (under (A): `(edition, app_payload)`).
4. **Expand the serve smoke** (Task 2 Step 5) to fetch the full asset list and assert success explicitly.
5. **Specify the first-run smoke insertion point** and the new validator name in Task 3 Step 3.
6. If option (B) is chosen instead, add `schemas/row-one-manifest.schema.json` to **Files**, add schema-update + manifest-test-update + drift-test steps, and reconcile `design.md:102–103`.

This is a read-only review; no files were edited.
