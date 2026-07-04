# Stage 289 Plan Re-Review

## Critical

**None.** All four blocking issues from the prior review are resolved.

### Verification of prior blocking issues

| Prior issue | Status | Evidence |
|---|---|---|
| C1: `_contract_drift_signal_group()` must include valid `story_refs` | **Resolved** | Plan Task 1 Step 2 (lines 81-99) builds `story_ref` from `lead_story = payload["stories"][0]` — a full `_story_payload` (render.py:788-827) which has `id`, `headline`, `section_key`, `section.title`, `detail_href`, `source_name`, `published_date`, `evidence_count`, `heat_delta`. Adds `"story_refs": [story_ref]` before `signal_overrides`. |
| C2: `published_date` must allow `null` via `nullablePublishedDate` | **Resolved** | Plan line 190 uses `{"$ref": "#/$defs/nullablePublishedDate"}`. Line 112 adds a positive drift case for `published_date = None`. |
| I1: Schema should reuse existing `$defs` | **Resolved** | Plan lines 186-190 reuse `sectionKey`, `localizedText`, `detailHref`, `nullablePublishedDate`. |
| M1: Smoke tests should explicitly cover missing/mismatched `story_refs` | **Resolved** | Plan Task 3 Step 1 (lines 236-238) specifies both cases explicitly. |

## Important

### I1. Smoke fixture prerequisite not surfaced — both smoke fixtures have `groups: []`

`tests/test_first_run_smoke.py:3975` and `:4626` both define `"signal_synthesis": {... "groups": []}`. The planned unit cases ("Pop `story_refs` from a sample signal"; "Reorder `story_refs[].story_id`") require a **populated** signal in a fixture. The plan's Task 3 Step 1 says "from a sample signal" without telling the implementer where that signal comes from.

**Fix:** Add an explicit sub-step in Task 3 Step 1: "Extend the smoke fixture at `test_first_run_smoke.py:3963-3976` to include one `groups[0].signals[0]` with valid `story_refs` (or construct a minimal inline fixture in the new test), so the pop/reorder cases have a target."

## Minor

- **M1.** I2 from prior review (helper skips cards where `section` is not a dict) remains unaddressed. The skip at plan lines 141-145 could desync `story_refs` from `story_ids` if a card is ever malformed, breaking the assertion at plan line 78. Real cards always have `section` (sourced from `_story_payload` via `briefing_topics.py:52`), so non-blocking. Either drop the skip to mirror `_content_card_payload`'s direct access, or add a one-line invariant comment.

- **M2.** `signalStoryRef.story_id` inlines `{"type": "string", "minLength": 1}` (plan line 184) rather than reusing `storyId` `$def` (schema line 113-116). This is consistent with `contentCard.id` (line 810-813) and `story.id` (line 558-561), which also inline — so the schema has two patterns. Acceptable, but note the inconsistency: `signalSynthesisSignal.story_ids[]` enforces the strict `storyId` pattern while `story_refs[].story_id` would only enforce `minLength: 1`, even though the plan asserts they hold the same values.

- **M3.** Task 1 Step 1 hardcodes `"section_key": "top_stories"` and `"section_key": "brand_moves"` for the two expected story_refs (plan lines 53, 64). The implementer must verify these match the actual brand signal's card sections in the generated payload; the "Verify red/green" steps will catch mismatches.

## Answers to the re-review questions

1. **Resolves the 4 blocking issues?** Yes — C1, C2, I1, M1 are all addressed.
2. **Ready for implementation?** Yes, after applying I1 (smoke fixture prerequisite). The Minor items can be addressed during implementation.

**Recommendation: proceed with implementation after adding the smoke-fixture sub-step described in I1.**
