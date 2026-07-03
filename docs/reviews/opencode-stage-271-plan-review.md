**NOT APPROVED.**

### Critical (blockers)
- **C1 — Manifest schema not updated.** `schemas/row-one-manifest.schema.json:30` const-pins `app_contract.version` to `row-one-app/v1`. After the bump, the generated manifest carries `v2` and fails its own schema (`test_row_one_manifest_schema_validates_generated_payload`, `test_empty_row_one_manifest_payload_validates`). The plan's Files/Task 3/commit list omit this file, and spec lines 61-64 are self-contradictory ("manifest schema unchanged" vs. "version points to v2").
- **C2 — Incomplete v1→v2 test inventory.** `row-one-app/v1` is hard-pinned in 8 places the plan doesn't enumerate: the drift case at `tests/test_row_one_app_contract.py:502` (asserts v2 is *rejected* — will invert), `:557`, `tests/test_row_one_render.py:488,536`, `tests/test_row_one_cli.py:365,782`, `tests/test_first_run_smoke.py:4304`, and `tests/test_row_one_docs.py:147`. The latter two files aren't even in the modify list.

### Important
- **I1 — `editorial_takeaway` vs. `detail_sections`.** The 5-key `detail_sections` model omits `editorial_takeaway`, but Task 4 Step 1 asserts `"编辑整理"` in the HTML and Step 2 reorganizes the panel into those same 5 sections. Pick one: add it to `detail_sections`, keep a separate HTML takeaway block, or drop the assertion.

### Answers to the 5 questions
1. v2 bump over sidecar: reasonable, but manifest schema must move in lockstep (C1).
2. Fields are largely sufficient/coherent; gap is `editorial_takeaway` placement (I1).
3. Builder/schema steps are specific, but file scope is incomplete (C1, C2).
4. Missing: manifest schema update, full v1→v2 test sweep, editorial reconciliation.
5. Blockers exist: C1 and C2 fail the focused/full gates; resolve I1 to avoid rework.

Required fixes: C1, C2, I1. Optional follow-ups: M1–M4 (unused `edition` param, card `display` aliasing, intentional evidence duplication, `detailSection.body` schema sketch).
