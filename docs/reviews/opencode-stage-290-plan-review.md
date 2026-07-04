## opencode Stage 290 Plan Review

I read the plan (`docs/superpowers/plans/2026-07-04-stage-290-row-one-card-information-sections-plan.md`) and cross-checked it against `render.py`, both schemas, `cli.py`, `check_first_run_smoke.py`, and every test file it touches, plus a repo-wide `row-one-app/v7` sweep.

### Critical
None. The core design is sound: `contentCard.information_sections` is a deterministic, additive presentation-organization layer that reuses existing localized card fields, mirrors the proven `stories[].detail_sections` concept without duplicating its evidence section, and stays inside all stated scope boundaries (no collection/matching/ranking/scoring/story-ID/compliance/LLM/dependency work). The `allOf` + `prefixItems`/`items:false` schema pattern is already used in this schema (`editionBriefStoriesMetric`, `briefingTopic`), so the approach is consistent and proven, with a sensible fallback note.

### Important

**I1. `tests/test_row_one_render.py` v7 assertions are not migrated.**
The contract bump breaks two existing assertions the plan never lists:
- `tests/test_row_one_render.py:1144` — `assert payload["contract_version"] == "row-one-app/v7"`
- `tests/test_row_one_render.py:1281` — same.

The plan's File Structure mentions this file only conditionally ("only if homepage rendering touches `information_sections` directly"), and `Task 5 Step 1`'s focused pytest run *excludes* `test_row_one_render.py`, so the breakage would surface only at the full `pytest -q` release gate in `Task 5 Step 2`.
**Fix:** Add an explicit step to update both lines to `row-one-app/v8`, and add `tests/test_row_one_render.py` to the `Task 5 Step 1` focused verification command so the regression is caught early.

**I2. The docs `v7` -> `v8` migration is unspecified.**
`README.md` (2 refs: `:74`, `:109`) and `docs/row-one.md` (8 refs: `:84`, `:119`, `:126`, `:131`, `:134`, `:210`, `:245`, `:277`) describe the *active* app contract as `row-one-app/v7`. `Task 4 Step 1` only *adds* Stage 290 wording; it never migrates these. This forces one of two bad outcomes:
- docs stay `v7` while the payload is `v8` -> inaccurate "active version" documentation; or
- docs move to `v8` -> five existing assertions in `tests/test_row_one_docs.py` break: `:153`, `:174`, `:189`, `:409`, `:436`.

**Fix:** Make `Task 4` explicitly migrate the `v7` -> `v8` references in both `README.md` and `docs/row-one.md`, and in the same step update the five existing `tests/test_row_one_docs.py` assertions (including `test_row_one_docs_describe_versioned_app_json_contract` and `test_row_one_docs_describe_stage_271_app_content_organization`) to `v8`. The new Stage 290 docs test (`Task 4 Step 2`) is additive and fine.

### Minor

**M1. "Update affected tests that assert the contract string" is too loose.** The sweep shows ~11 test-file `v7` references across `test_row_one_cli.py` (`:611`, `:838`, `:1250`), `test_row_one_app_contract.py` (`:231`, `:418`, `:1961`), and `test_first_run_smoke.py` (`:3824`, `:3888`, `:3920`, `:4699`, `:4763`). Also `cli.py` has *two* (`:1954`, `:1964`) and `check_first_run_smoke.py` has *two* (`:1134`, `:1188`), but the plan says "the app contract expectation" (singular). Enumerate the per-file counts so none are missed.

**M2. Information-section key/title tuple is triplicated** across `render.py` (`CONTENT_CARD_INFORMATION_SECTIONS`), `cli.py` (`_EXPECTED_ROW_ONE_CARD_INFORMATION_SECTIONS`), and mirrored in `check_first_run_smoke.py`. This matches the established Stage 289 `story_refs` pattern (smoke must stay standalone), so it's acceptable, but you could share one module between `render.py` and `cli.py` to prevent future label drift.

**M3. Drift-test `match` strings are under-specified** (`Task 1 Step 3`). The `__setitem__("key","bad")` case yields a `const` violation on the positional `prefixItems[0]` def; ensure the regex is loose enough (e.g. match `"summary"`) and that the append-extra case matches `maxItems`/`too long`. Not blocking — just needs care at implementation time.

### Answers to the five review questions
1. **Right layer?** Yes. `contentCard.information_sections` is the correct low-risk next information-organization surface — additive, display-ready, and non-overlapping with evidence-bearing `detail_sections`.
2. **`v7` -> `v8` appropriate?** Yes, and required. `contentCard` uses `additionalProperties:false` + `required`, and is shared by `content_sections`, `daily_digest.blocks`, and `daily_digest.briefing_topics`, so adding a required field is a real contract change.
3. **Scope correct?** Yes for schema/renderer/status/smoke, with the exceptions in I1 and I2. Constraint adherence is correctly maintained.
4. **Missing/unnecessary files?** Missing: explicit `test_row_one_render.py` migration (I1) and docs `v7` -> `v8` migration (I2). Nothing unnecessary.
5. **Blocking flaws?** None. Fix I1 and I2 before implementation; the rest are minor.

**Verdict: no critical flaws; implement after addressing I1 and I2.**
