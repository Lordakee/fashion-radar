# Stage 289 Plan Review

## Critical

### C1. Plan omits required update to `_contract_drift_signal_group` test helper — all existing drift cases will break

`tests/test_row_one_app_contract.py:138-173` defines `_contract_drift_signal_group`, which builds a drift signal **without** `story_refs`. It is used by ~13 parametrized drift cases (lines 1338-1501) that expect specific error patterns like `"is not one of"`, `"less than the minimum"`, `"does not match"`.

Adding `story_refs` to `signalSynthesisSignal.required` makes `jsonschema` fail the `required` keyword **first** (before `properties`), so the raised `ValidationError` message becomes `'story_refs' is a required property` and the `pytest.raises(match=...)` regex no longer matches.

**Fix:** Task 1 must update `_contract_drift_signal_group` to include a valid `story_refs` (one entry derived from `payload["stories"][0]`) so the helper still produces an otherwise-valid signal. The plan's Task 1 Step 1/Step 2 only extend the positive test and add new drift lambdas; they never touch this helper.

### C2. `signalStoryRef.published_date` schema rejects `null`, but stories can be undated

Plan schema (lines 169) hardcodes `"published_date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"}`. But `render.py:813` emits `"published_date": None` when `published_at` is `None`, and the existing `contentCard.published_date` correctly uses `nullablePublishedDate` (anyOf string|null, schema line 852-863). A signal grouping an undated story would produce `story_refs[i].published_date = null` and fail schema validation.

**Fix:** Use `{"$ref": "#/$defs/nullablePublishedDate"}` for `published_date`. The Task 1 test data hardcodes `"2026-07-02"`, so this regression would not be caught — add a drift case for `published_date: null` on a `story_ref` to lock it in (it should validate, not reject).

## Important

### I1. `section_key` and `detail_href` in `signalStoryRef` should reuse `$defs`, not inline

Plan lines 163-167 inline the section-key enum and the detail-href pattern. The schema already defines `sectionKey` (line 100) and `detailHref` (line 141). Inlining creates a third copy that can drift silently. Use `{"$ref": "#/$defs/sectionKey"}` and `{"$ref": "#/$defs/detailHref"}`. Same for `story_id` → reuse `storyId` `$def`.

### I2. Helper silently skips cards lacking `section`, which can desync `story_refs` from `story_ids`

`_signal_story_refs_from_topic` (plan lines 119-122) skips any card where `section` is not a dict. Real story payloads always have `section`, so this is fine in practice, but Task 1's assertion `story_refs story_id == story_ids` (plan line 77) would then fail mysteriously if a card is ever malformed. Either drop the skip (trust the contract, mirroring `_content_card_payload`) or document the invariant. Minor, but worth a one-line decision.

## Minor

- **M1.** Task 3 Step 1 ("Add unit coverage ... for missing or mismatched `story_refs`") is vague. Concretely specify the two smoke unit cases to mirror lines 4058-4066: (a) pop `story_refs`, expect `SmokeError` matching `"story_refs"`; (b) reorder `story_refs[].story_id`, expect `SmokeError` matching `"story_ids"`.
- **M2.** Docs phrase `"without joining back to stories[]"` (plan line 223) is awkward for prose; existing Stage 287 docs test (line 248) uses natural phrasing like `"derived from daily_digest.briefing_topics"`. Reword to something like `"embeds each signal's supporting story cards inline"` and `"derived from daily_digest.briefing_topics cards"`.
- **M3.** Task 4 Step 3 runs `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .` — good. Consider also noting that `render.py` will need `ruff format` after adding the helper (the plan's code block is already well-formed, so likely a no-op).

## Answers to the five questions

1. **Scope alignment:** Yes. Stage 289 directly serves the user's stated goal ("better information organization") by embedding compact story references into each signal. A runtime-manifest polish node would not address this need.
2. **Reasonableness/risk:** Approach is sound — it copies from `topic["cards"]` (which are raw `_story_payload` dicts via `briefing_topics.py:52`, so `section`, `section_key`, `detail_href`, `source_name`, `published_date`, `evidence_count`, `heat_delta` are all present). Low-risk **except** for C1 and C2, which must be fixed first.
3. **Tests/schema/smoke/docs sufficiency:** Insufficient as written. C1 (drift helper) and C2 (nullable date) are gaps; the rest of the coverage is adequate.
4. **Unnecessary/missing files:** No unnecessary files. Missing: the plan must list updating `_contract_drift_signal_group` in Task 1.
5. **Changes before implementation:** Yes — fix C1 and C2, apply I1 (reuse `$defs`). M1-M3 are nice-to-have.

**Recommendation: revise the plan before implementation.**
