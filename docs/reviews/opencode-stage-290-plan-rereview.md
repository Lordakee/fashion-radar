## Stage 290 Plan Re-Review — opencode (GLM 5.2, fallback reviewer)

Re-reviewed `docs/superpowers/plans/2026-07-04-stage-290-row-one-card-information-sections-plan.md` against the live tree (`render.py:29`, `render.py:794`, `cli.py:1618`/`1954`/`1964`, `schemas/row-one-app.schema.json:838`, `schemas/row-one-manifest.schema.json:30`, `scripts/check_first_run_smoke.py:1134`/`1188`, and all six cited test files).

### Answers

1. **I1 resolved?** Yes. `tests/test_row_one_render.py` is named in File Structure (plan:38) with an explicit "Migrate existing app contract assertions from `row-one-app/v7` to `row-one-app/v8`" instruction, enumerated in Task 3 Step 1 as "has 2" active refs (verified: lines 1144, 1281), and included in the Task 5 Step 1 focused pytest/ruff check/ruff format commands (plan:474-476).

2. **I2 resolved?** Yes. `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py` are migrated per File Structure (plan:40-41) and Task 4 Step 1. Task 4 Step 1 (plan:418) names the four specific docs tests to update (`test_row_one_docs_describe_versioned_app_json_contract`, `..._stage_271_app_content_organization`, `..._stage_277_homepage_briefing_topics`, `..._stage_272_editorial_web_experience`); I confirmed all four exist at `tests/test_row_one_docs.py:147,169,391,425`.

3. **Ready for implementation?** Yes.

### Findings

**Critical:** None.

**Important:** None. I1, I2, and M1 are all resolved.

**Minor:**

- M-1 (carry-forward, non-blocking): Task 1 Step 1's hedge — "assert the same keys exist on ... `content_sections[0]["cards"][0]` and ... `briefing_topics[0]["cards"][0]` **when those fixtures produce cards**" — is correct but implementers should confirm the default `_payload(tmp_path)` fixture actually yields cards in those slots (the daily-digest test shows `signals_to_watch` block has empty `story_ids` at `tests/test_row_one_app_contract.py:396`). The hedge covers it; just flagging so the implementer picks a non-empty fixture or skips gracefully.
- M-2: Task 1 Step 2's empty-edition assertions assume `content_sections[0]["cards"] == []` and `daily_digest["blocks"][0]["cards"] == []`. The plan's "or the nearest empty-payload test" fallback is sufficient, but the implementer should verify `test_row_one_app_payload_includes_empty_edition_brief_for_clients` (`tests/test_row_one_app_contract.py:479`) actually produces that exact shape before asserting.
- M-3: Task 3 Step 2 says to call the new validator "from the existing status payload validation path" without naming the function. It is discoverable (the `_require_row_one_value` cluster at `cli.py:1618-2005`), but naming the integration point would save a grep. Not blocking.
- M-4: Task 2 Step 4's `allOf` + `additionalProperties: false` caveat is technically accurate for JSON Schema 2020-12 (additionalProperties ignores `allOf`-merged siblings), and the five-fully-expanded-definitions fallback is the correct escape hatch. No change needed; recording so the implementer does not waste time on the `allOf` form.

M1 (enumerate active v7 refs): resolved. Task 3 Step 1 (plan:317) gives a per-file count that I verified exactly against the tree: `test_row_one_cli.py`=3, `test_row_one_render.py`=2, `test_row_one_app_contract.py`=3, `test_first_run_smoke.py`=5, `test_row_one_docs.py`=5, `cli.py`=2, `check_first_run_smoke.py`=2, app schema=1, manifest schema=1, README=2, `docs/row-one.md`=8 — all match `rg -n "row-one-app/v7"`.

**Verdict:** Plan is ready for implementation. No Critical or Important issues remain; the four Minor notes are implementer-facing clarifications, not plan defects.
