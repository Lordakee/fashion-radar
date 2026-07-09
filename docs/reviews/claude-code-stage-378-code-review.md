---

**Critical**

None.

---

**Important**

None.

---

**Minor**

**M1. Implicit coupling between `MAX_CARDS` and `MAX_CARDS_PER_LANE` is undocumented.**

Both constants are 3. Because the builder hard-caps total cards at `MAX_CARDS = 3`, the per-lane cap of 3 can never be hit today — even if all three renderable cards land in the same lane, none is dropped by the cap, so the count-guard fallback (`_saved_article_local_related_read_lane_card_count(lanes) != len(renderable_cards)`) is only reachable via an unclassified reason, exactly as the plan intends.

But the invariant that `MAX_CARDS_PER_LANE ≥ MAX_CARDS` must hold to prevent the per-lane cap from silently triggering the flat-grid fallback is not stated anywhere. If `MAX_CARDS` is later raised (e.g., to 5) without a matching raise of `MAX_CARDS_PER_LANE`, a two-card same-lane overflow would cause silent fallback to the flat grid with no test failure and no log signal. A short comment near the two constants (e.g., `# MAX_CARDS_PER_LANE must be >= MAX_CARDS to avoid cap-triggered fallback`) would close this.

`saved_article_local_related_reads.py:17-18`

---

**M2. Triple href validation per card in the lane-render path.**

`_render_saved_article_local_related_reads` subjects each card to `_safe_saved_article_local_related_read_href` three times:

1. The initial `cards` list comprehension via `_render_saved_article_local_related_read_card`.
2. `_renderable_saved_article_local_related_read_cards`.
3. `_render_saved_article_local_related_read_lane` → `_render_saved_article_local_related_read_card` (re-validates the already-screened lane cards).

Pass (3) is pure defence-in-depth; it cannot catch anything pass (2) did not already catch because both call the function with the same (`candidate_story_id`, `href`) pair. With `MAX_CARDS = 3` this is inconsequential for performance, but the extra pass adds cognitive load to anyone tracing the lane render flow. It is a deliberate defensive pattern (keeping the single-card renderer honest), so it does not need to be removed — a one-line comment at pass (3) noting "re-validates after pre-screening" would make the intent clear.

`templates.py` around line 9416–9418

---

**M3. ZH-only classification fixture for `same_section` is absent.**

`test_saved_article_local_related_read_lanes_preserve_order_and_cap_each_lane` exercises the ZH-only classification path for `same_source` by constructing a card with `reason=LocalizedText(en="", zh="同一来源")`. No equivalent direct-fixture test covers the `same_section` ZH branch (`zh="同一 ROW ONE 栏目"`, `en=""`). The `same_section` ZH path is exercised only indirectly through `test_saved_article_local_related_reads_groups_cards_into_lanes`, where the builder always emits the correct EN reason string alongside the ZH one.

This is a minor parity gap. Adding one card in the existing cap/order test (or a separate short test) with `en=""` and `zh="同一 ROW ONE 栏目"` would give symmetrical direct-fixture coverage for all three ZH branches.

`tests/test_row_one_saved_article_local_related_reads.py:540–579`

---

**M4. ZH-only fixture in the cap/order test is uncommented.**

The fixture at line 545 uses `reason=LocalizedText(en="", zh="同一来源")` — an empty EN reason — without a comment. Readers unfamiliar with the intent must inspect `_related_read_lane_key` to understand that the empty EN string is deliberately testing the ZH-fallback classification path rather than representing a realistic card. A brief comment (`# empty EN reason exercises the ZH-only classification path`) would make the fixture self-documenting.

`tests/test_row_one_saved_article_local_related_reads.py:545`

---

END_OF_REVIEW
