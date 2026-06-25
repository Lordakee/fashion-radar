# Stage 199 Plan Review

## Verdict

**Approved with minor required changes.** The plan is a sound, fully-local
deterministic matching-quality node that correctly mirrors existing scoring
and representative-item semantics. No critical or important blockers. A few
minor gaps in test/fixture specification should be tightened before
implementation.

## Critical Findings

None.

## Important Findings

None.

## Minor Findings

1. **Task 4 Step 3 is too vague about the `report_payload()` fixture.**
   `tests/test_first_run_smoke.py:report_payload()` (line 524) builds the
   3-entity dict literal that `validate_report_outputs` consumes. Adding the
   `match_evidence` validation means each of the 3 entity dicts at lines
   620–666 must gain a `match_evidence` key, or the positive case at line 3624
   will fail. The plan says "include a minimal `match_evidence` object for
   sample entity fixtures" but does not name `report_payload()` or show the
   required shape. Any `match_evidence` fixture dict missing one of the 9
   keys would also need handling.

2. **Task 4 Step 2 `matched_items >= 1` check needs empirical confirmation.**
   The first-run smoke runs real `collect` + `match`. The 3 pinned entities
   (`The Row`, `The Row Margaux`, `Ballet Flats`) are each expected to match
   at least one community-signal row (lines 1131–1157 confirm match
   expectations), and the sample aliases are exact matches likely above
   `min_match_confidence=0.5`. This should hold, but the plan should either
   (a) run the smoke once to confirm, or (b) phrase the check as
   "`match_evidence` key present and `matched_items` is an int >= 0" with a
   separate softer assertion, to avoid a brittle pin on exact counts.

3. **No explicit test for the confidence tie-break rule.** Task 2's test
   fixture uses distinct confidences (0.8 vs 0.95), so it exercises
   highest-confidence selection but never the "confidence ties to
   lexicographically smallest reason" branch. A two-row fixture with equal
   confidence and reasons like `safe_alias` vs `parent_brand` would close
   this gap.

4. **No test for sub-threshold confidence filtering.** All Task 2 fixture
   confidences (0.8, 0.9, 0.95, 1.0) exceed `min_match_confidence=0.5`. A
   row with `confidence=0.3` should be excluded; this is currently only
   implied by the window-filter test.

5. **`docs/scoring.md` section placement is unspecified.**
   `tests/test_scoring_docs.py` parses the `## Limits` section via
   `text.split("## Limits")[1].split("\n## ")[0]`. The new `## Match Evidence`
   section must not be inserted *inside* `## Limits`. The plan should say
   "insert after `## Formula`, before `## Labels`" or similar.

6. **Markdown format for `min == max` is unspecified.** A single match
   renders as `confidence 1.00-1.00 avg 1.00`. Not wrong, but the plan
   should either document this or special-case it (e.g.,
   `confidence 1.00 avg 1.00`).

7. **Review output truncation.** `sed -n '1,260p'` in Tasks 0/5/6 may clip
   long GLM-5.2 reviews. Consider raising to 400 or using `wc -l` first.

## Answers To Review Questions

1. **Reasonable Stage 199 after Stage 198?** Yes. The Footwear News RSS
   option is blocked by SOCKS/socksio proxy noise in this sandbox and would
   produce advisory-only source-liveness evidence. Aggregate match evidence
   is fully local, offline-testable, advances deterministic matching
   quality, and reuses existing stored rows — the correct priority node.

2. **Aggregate-only, no raw leakage?** Yes. `EntityMatchEvidence` uses
   `ConfigDict(extra="forbid")` and exposes only counts + 3 confidence
   scalars. `EntityReport` is also `extra="forbid"`, so any accidental
   `alias`/`reason`/`context_terms`/`item_id`/`normalized_url` key would
   raise `ValidationError` at construction. The forbidden-string scan in
   `test_json_report_excludes_internal_database_and_matcher_fields` is
   correctly extended. The evidence SQL selects `reason` only to bucket it,
   never renders the raw string.

3. **Reason buckets aligned with matcher semantics?** Yes. The matcher
   (`extract/entities.py:10-14`) defines exactly 5 reasons:
   `accepted`, `context`, `missing_context`, `parent_brand`, `safe_alias`.
   `missing_context` is a *rejected* reason (returns `False` at lines 74,
   82) and is never stored, so only the 4 accepted reasons reach
   `item_entities`. The 4 known buckets + `other_supported_items` fallback
   is correct and defensive.

4. **Duplicate-row dedup sound?** Yes. Dedup by
   `(entity_name, entity_type, item_id)` with highest-confidence-wins and
   lexicographic reason tie-break is deterministic and mirrors scoring's
   per-entity/item dedup (`docs/scoring.md:24-25`). Since `entity_name` is
   fixed per query and `EntityReport` carries a single `entity_type`, the
   effective key is `item_id`, which matches how
   `_representative_items` dedups (`reports.py:453-458`). The schema has no
   unique constraint on `(item_id, entity_name, entity_type)`, so duplicate
   rows are possible and the dedup is necessary.

5. **Evidence window aligned?** Yes, exactly.
   `current_start < collected_at <= as_of` with
   `current_start = as_of - timedelta(days=scoring.current_window_days)`
   matches `_representative_items` (`reports.py:456`) and `docs/scoring.md`
   windows section (lines 27-48). `confidence >= min_match_confidence`
   matches the SQL filter at `reports.py:448`.

6. **Docs/smoke/CLI scoped enough?** Yes, with the fixture-placement caveat
   in Minor Finding 1. `test_scoring_docs.py` only pins the `## Limits`
   section, so a `## Match Evidence` section is safe if placed outside
   `Limits` (Minor Finding 5). The CLI smoke is a one-assertion extension
   to an existing test. No sprawl.

7. **Scope boundaries respected?** Yes. The plan explicitly excludes
   collection, source packs, configs, extract/scoring/discovery/trends/heat
   modules, social connectors, scraping/browser automation,
   login/cookie/session/token/proxy, ranking/hotness/demand proof, platform
   coverage, and compliance-review. It touches only report models,
   rendering, and tests. No schema changes.

8. **Impossible/brittle/missing-import steps?** No. Verified:
   - `ItemRepository.upsert_item` and `.replace_item_matches` signatures
     match the proposed `_store_item_with_matches` helper exactly
     (`repositories.py:29-36, 91-93`).
   - `_store_item` refactor to delegate to `_store_item_with_matches` is
     backward-compatible (same sentinel match dict).
   - `_count_label` exists at `reports.py:416-417`.
   - `EntityMatchEvidence` placement "before `EntityReport`" and field
     placement "after `representative_items`" are both valid.
   - The confidence rounding (`round(x, 4)` for JSON, `f"{x:.2f}"` for
     Markdown) is numerically sound: `0.925` formats to `"0.93"` because
     the float is slightly above 0.925 (verified).

## Required Plan Changes Before Implementation

1. **Task 4 Step 3:** Replace "include a minimal `match_evidence` object for
   sample entity fixtures" with an explicit instruction to update the
   `report_payload()` helper at `tests/test_first_run_smoke.py:524-670`,
   adding a full 9-key `match_evidence` dict to each of the 3 entity dicts
   (lines 620, 636, 651), and add one negative case where a missing
   `match_evidence` key raises `SmokeError`.

2. **Task 4 Step 2:** Either (a) run the smoke once to confirm all 3 pinned
   entities yield `matched_items >= 1`, or (b) soften the validator to
   require the `match_evidence` key presence + `matched_items` is a non-negative
   int, and assert `>= 1` only for `The Row`.

3. **Task 4 Step 4:** Specify that `## Match Evidence` is inserted after the
   `## Formula` section and before `## Labels` (or `## Limits`), so
   `test_scoring_docs.py`'s `## Limits` parser is unaffected.

4. **Task 2:** Add a tie-break test (two rows, equal confidence, reasons
   `safe_alias` and `parent_brand`, assert `parent_brand` wins) and a
   sub-threshold confidence exclusion test (one row at `confidence=0.3`,
   assert it is excluded).

5. **Task 3 Step 3:** Specify the Markdown rendering when
   `min_confidence == max_confidence` (either collapse to
   `confidence {v} avg {v}` or document the `X.XX-X.XX` form).

Optional: raise the `sed -n '1,260p'` truncation in Tasks 0/5/6 to 400 lines.
