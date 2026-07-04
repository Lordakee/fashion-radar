## Verdict

**Approve with required revisions.** The plan is correctly scoped as an additive, deterministic, local-observed report layer and properly bumps to `row-one-app/v6` (the root schema is `additionalProperties: false`, so a new required top-level field forces a major bump). However, it must not enter implementation until the critical and important findings below are fixed. The two blocking issues are: (1) the proposed `signal_synthesis` shape advertises `boundaries` and `top_movers` fields that never reach the schema/helper/tests, silently dropping the local-observed/review-required wording the prompt explicitly asks about; and (2) the entity-type grouping rule diverges from the already-shipped `briefing_topics` normalizer, which will make two top-level app surfaces disagree for the same edition.

---

## Critical Findings

### C1. `boundaries` (and `top_movers`) in illustrative shape but absent from schema/helper/tests

- **Where:** Plan lines 60-96 (shape) vs lines 269-278 (helper), lines 298-313 (schema def), Task 1 tests (lines 122-227).
- **Why it matters:** The shape example includes `"boundaries": {"zh": "本地观察，需人工复核。", "en": "Local observed signals; review required."}` and `"top_movers": [...]`. But `$defs.signalSynthesis.required` is `["title","dek","group_count","signal_count","groups"]`, the helper returns only those five keys, and no test asserts either field. Because the schema uses `additionalProperties: false`, even if a future implementer re-added them they'd be rejected. The review prompt specifically asks to verify the local-observed/review-required boundary wording reaches clients - under this plan it does not.
- **Smallest fix:** Add `boundaries` (a `localizedText`) to `$defs.signalSynthesis.required`, to the helper return, and to the Task 1 populated + empty tests. Either drop `top_movers` from the illustrative shape or add it to the schema too.

### C2. Entity-type grouping diverges from the shipping `briefing_topics` normalizer

- **Where:** Plan rule #1 (lines 101-102) vs `src/fashion_radar/row_one/briefing_topics.py:78-88`.
- **Why it matters:** The plan groups `entity_refs` only when `type` is exactly `brand` or `person`. `briefing_topics._topic_type_for_entity_reference` also maps `retailer`→`brand` and `actor/artist/celebrity/creator/influencer/model/person/stylist`→`person`. For an edition containing a `retailer` or `celebrity` entity_ref, `daily_digest.briefing_topics` will list a brand/person topic that `signal_synthesis` silently drops - two top-level app surfaces reporting contradictory signal sets and counts for the same edition. This is a data-correctness defect on a contract-versioned field.
- **Smallest fix:** Change rule #1 to "derive group type via the same mapping as `briefing_topics._topic_type_for_entity_reference`" (or call that helper directly), and add a RED test with a `retailer` and a `celebrity` entity_ref asserting both surfaces include the signal.

---

## Important Findings

### I1. No explicit step to update existing `row-one-app/v5` string literals

- **Where:** Files section (lines 17-56) and Task 4 (lines 388-431).
- **Why it matters:** Grep confirms 25+ hardcoded `row-one-app/v5` literals outside the files the plan calls out, including assertion sites that will fail immediately after the bump: `tests/test_row_one_render.py:984,1121`, `tests/test_first_run_smoke.py:3824,3874,3906,4542,4592`, `tests/test_row_one_app_contract.py:163,350,1306`, `tests/test_row_one_cli.py:557,780,1142`, `tests/test_row_one_docs.py:153,174,189,358,385`, `README.md:74,108`, `docs/row-one.md:84,118,125,129,185,220,252`, `scripts/check_first_run_smoke.py:1134,1188`. Task 4 says cli.py and check_first_run_smoke.py validators must "expect v6" but does not enumerate the test/docs string-literal updates, and the top-level Files list omits `tests/test_row_one_cli.py` and `tests/test_first_run_smoke.py` entirely (they appear only in the Task 4 sub-list).
- **Smallest fix:** Add a Task 4 step "Replace every remaining `row-one-app/v5` literal with `row-one-app/v6`" and list all 8 files; add the two missing test files to the top-level Files section.

### I2. `signal_synthesis` substantially duplicates `briefing_topics` without justification

- **Where:** "Product Gap Closed" (lines 13-15) and "Proposed shape" (lines 58-96) vs `src/fashion_radar/row_one/briefing_topics.py:1-170` and schema `$defs.briefingTopic` (lines 857-1021).
- **Why it matters:** `briefing_topics` already deterministically groups brand/product/designer/person from the same `entity_refs`/`product_refs`/`designer_refs`, already computes `story_count`, `evidence_count`, `positive_heat_delta_sum`, `max_heat_delta`, `lead_story_id`, `story_ids`, `cards`, `source_refs`, and is already rendered on the homepage as "Briefing Topics". The plan adds a parallel required top-level field (forcing a v6 bump and ~25 string-literal updates) without explaining why extending `briefing_topics` is insufficient. The plan's claim that ROW ONE "still mostly exposes them as story cards" is overstated, since the topics surface already exists.
- **Smallest fix:** Either (preferred) derive `signal_synthesis.groups` from `briefing_topics_payload(stories)` so the two surfaces cannot diverge, or add one paragraph in "Product Gap Closed" justifying the parallel surface (e.g. grouped-by-type with stable group ordering and bilingual summaries that `briefing_topics` doesn't expose).

### I3. Schema constraints for the new defs are underspecified

- **Where:** Plan lines 298-315.
- **Why it matters:** The plan names the fields on `signalSynthesisGroup` (`key`, `label`, `signal_count`, `signals`) and `signalSynthesisSignal` (`name`, `type`, `label`, `story_count`, `evidence_count`, `positive_heat_delta_sum`, `max_heat_delta`, `lead_story_id`, `lead_story_href`, `summary`, `story_ids`) but gives no constraints. Without them the drift tests can't lock the contract, and the four drift cases in Task 1 Step 3 are thinner than the `briefingTopic` precedent (test_row_one_app_contract.py:1056-1142 covers wrong type enum, zero story_count, null lead_story_id, empty story_ids, wrong id pattern, label/type mismatch).
- **Smallest fix:** Specify `group.key` and `signal.type` as `enum: ["brand","product","designer","person"]`; `signal.story_count` `minimum: 1`; `positive_heat_delta_sum`/`max_heat_delta` `minimum: 0`; `story_ids` `minItems: 1` with `$ref storyId` items; `lead_story_id` `$ref storyId`; `lead_story_href` `$ref detailHref`; `summary` `$ref localizedText`. Add drift cases for wrong type, zero story_count, null lead_story_id, empty story_ids, malformed lead_story_id.

### I4. Boundary/summary text generation is deferred and untested

- **Where:** Plan lines 281-283 (helpers left to "use the deterministic rules above") and Task 1 (no assertion on `summary` or `boundaries` wording).
- **Why it matters:** The prompt asks to verify local-observed/review-required wording and absence of market-demand/platform-coverage claims. The `_signal_summary` helper (which produces per-signal prose like "The Row appears in 2 stories, with max local mention delta +4...") is named but not shown, and no test asserts its output stays within boundaries. A future implementer could write "The Row is trending globally" or similar demand/coverage language and no test would catch it.
- **Smallest fix:** Show the `_signal_summary` template strings in the plan, assert the populated-test `summary` text verbatim (as the example already implies), and add a docs guard test asserting the phrases "local observed" / "review required" appear in `docs/row-one.md` and that "demand", "coverage", "platform" do not appear in the synthesis section.

---

## Minor Findings

### M1. `lead_story_id` selection rule is ambiguous
Rule #7 (line 114) says "first story for that signal after the sort above" but the sort in rule #4 orders signals, not stories within a signal. `briefing_topics` uses story encounter order (`story_ids[0]`). State explicitly: `story_ids` preserves first-encounter order and `lead_story_id = story_ids[0]`.

### M2. Renderer hostile-payload test is underspecified
Task 3 Step 1 (lines 331-347) describes the escape test in prose rather than the concrete code used for the contract tests. Provide concrete code: markup in `name`/`label`/`summary`, an unsafe `lead_story_href`, and assertions that `<`, `&`, and `../escape.html` do not appear in the rendered HTML.

### M3. Illustrative shape numbers disagree with the RED test
Shape example (lines 82-84) shows `positive_heat_delta_sum: 4, max_heat_delta: 4` for a 2-story brand; the Task 1 test (line 169) asserts `6` and `4`. Align the example with the test or label it "illustrative only".

### M4. Empty-edition `dek` text not in deterministic rules
Task 1 Step 2 asserts an empty-edition dek, but rule #8 (line 115) only mentions counts/groups, and `_signal_synthesis_dek` is not shown. Add the empty-case dek strings to rule #8 or inline the helper.

### M5. Homepage ordering test is partial
Task 3 Step 1 only asserts `edition_brief` precedes `signal_synthesis`. Since the plan inserts the section before `lead_story_block`/`briefing_topics`/`briefing_path`, also assert `signal_synthesis` precedes the lead story block to lock the intended placement.

### M6. Self-Review "no placeholders" claim is overstated
Six helper bodies (`_signal_synthesis_groups`, `_signal_synthesis_candidates`, `_signal_reference_payloads`, `_signal_summary`, `_positive_heat_delta`, `_localized_signal_group_label`) are deferred to "use the deterministic rules above" (lines 281-283). That is acceptable for a plan but is not "no TODO/TBD placeholders" (line 503). Soften the claim or inline the helper bodies.

---

## Recommended Plan Changes

1. **Add `boundaries` to the contract.** Put `boundaries` (`localizedText`) in `$defs.signalSynthesis.required`, in `_signal_synthesis_payload`, and in the Task 1 populated + empty test assertions. Drop `top_movers` from the illustrative shape or add it to the schema too. (Fixes C1, I4.)
2. **Reuse the `briefing_topics` entity-type mapping.** Replace rule #1's "type is brand or person" with "reuse `_topic_type_for_entity_reference`" and add a RED test with `retailer` and `celebrity` entity_refs asserting both surfaces include the signal. (Fixes C2; also addresses I2's divergence risk.)
3. **Add an explicit v5→v6 literal-update step.** In Task 4, add a step that enumerates and updates all 8 files containing `row-one-app/v5` (tests/test_row_one_render.py, tests/test_first_run_smoke.py, tests/test_row_one_app_contract.py, tests/test_row_one_cli.py, tests/test_row_one_docs.py, README.md, docs/row-one.md, scripts/check_first_run_smoke.py), and add `tests/test_row_one_cli.py` + `tests/test_first_run_smoke.py` to the top-level Files section. (Fixes I1.)
4. **Justify or unify with `briefing_topics`.** Either derive `signal_synthesis.groups` from `briefing_topics_payload(stories)` (preferred - guarantees agreement and avoids C2 entirely), or add a paragraph in "Product Gap Closed" explaining why a parallel grouped surface is needed beyond the existing flat topic list. (Fixes I2.)
5. **Specify full schema constraints and drift cases.** Mirror `briefingTopic` (schema lines 857-1021) for enums, minimums, patterns, and add the parallel drift cases. (Fixes I3.)
6. **Lock boundary wording in tests.** Assert `_signal_summary` output verbatim in the populated test and add a docs guard that "local observed"/"review required" appear and "demand"/"coverage"/"platform" do not appear in the synthesis section. (Fixes I4.)
7. **Clarify deterministic rules.** State `story_ids` encounter order and `lead_story_id = story_ids[0]`; inline `_signal_synthesis_dek` empty-case text; align illustrative numbers with the RED test. (Fixes M1, M3, M4.)

Once C1, C2, and I1 are addressed, the plan is safe to enter implementation under the staged review protocol; I2-I4 and the minor items can be refined during the code-review stage.
