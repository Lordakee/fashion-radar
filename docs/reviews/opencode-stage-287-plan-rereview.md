## Verdict

**Approve with one Important revision.** The corrected plan resolves all five original blockers and all three prior-rereview Critical test-construction defects. Verified against `briefing_topics.py`, `render.py`, `templates.py`, the schema `$defs` (`storyId`, `detailHref`, `localizedText`), the test fixtures (`_edition`, `_payload`, `_schema_validator`, `_contract_drift_topic`), the drift parametrization at `tests/test_row_one_app_contract.py:1244`, the escape-test pattern at `tests/test_row_one_render.py:544`, and the `render_index_html` signature at `templates.py:22`. The `v5`→`v6` sweep covers all 12 source/test/doc files returned by `rg "row-one-app/v5"` (the two `docs/superpowers/plans/*` hits are historical plan artifacts and are correctly excluded). One Important wording-determinism gap and two minor items remain; none block starting implementation.

## Critical Findings

None. The plan is correctly scoped, additive, contract-safe, and its test code matches existing scaffolding. `boundaries` is present in the shape (line 73), helper (lines 429-432), schema `$defs.signalSynthesis.required` (line 456) + `properties.boundaries` (line 463), the populated test (lines 177-180), the empty test (lines 214-217), the hostile render test (line 575), and the docs guard (lines 686-691). `signal_synthesis.groups` derives from `briefing_topics_payload(stories)` (Rule 1, line 104; helper spec, line 439) and the mapping-parity test (lines 354-379) pins `retailer`→`brand` and `celebrity`→`person` against the same normalizer at `briefing_topics.py:78-88`.

## Important Findings

**I1. No-signal dek trigger is ambiguous for editions that have stories but no refs.**
- **Where:** Deterministic Rules 12 and 14 (plan lines 127-133), helper `_signal_synthesis_dek` (line 426), empty test (Task 1 Step 2, lines 207-225).
- **Why it matters:** Rule 12 ("populated dek") keys off `story_count`, Rule 14 ("empty editions") is demonstrated only with `edition.stories = []`. But the condition that yields `signal_count: 0 / groups: []` also occurs for a non-empty edition whose stories carry no `entity_refs`/`product_refs`/`designer_refs` — a case the suite already exercises (`test_row_one_app_daily_digest_topics_do_not_infer_people_from_section_or_tags`). A literal implementer keying off `len(stories) == 0` would emit `"ROW ONE organized 0 readable signals from 1 stories today."`, which is broken wording on a contract-versioned app surface and is not pinned by any test.
- **Smallest fix:** State in Rule 14 that the empty/no-signal dek applies whenever `signal_count == 0` regardless of story count (Rule 12 applies only when `signal_count > 0`), and add a RED test rendering an edition with one ref-less story asserting the `"No ROW ONE signals are ready to organize yet."` dek plus `group_count: 0`.

## Minor Findings

- **M1.** Rule 12 en dek is grammatically broken for single-story editions: `"organized {signal_count} readable signals from {story_count} stories today"` yields "1 readable signals from 1 stories". The codebase already has `_plural_word` (`render.py:451`); branch on `signal_count == 1` and `story_count == 1`, or reuse that helper. (zh is unaffected.)
- **M2.** No test exercises intra-group multi-signal ordering (Rule 5, lines 114-118). Every populated case has ≤1 signal per group, so the (positive_heat_delta_sum, evidence_count, story_count, name) tiebreak is unverified. Carried over from the prior rereview M1; non-blocking.

## Recommended Plan Changes

1. **Fix I1:** clarify that the Rule 14 dek fires on `signal_count == 0` (not on `len(stories) == 0`), and add a no-refs-nonempty-edition dek test.
2. **Fix M1 (optional):** handle en singular/plural for `signal`/`story` in Rule 12 via the existing `_plural_word` helper.
3. **Fix M2 (optional):** add a two-brand-signal case to lock the Rule 5 tiebreak.

With I1 addressed, the plan is safe to enter implementation under the staged review protocol.
