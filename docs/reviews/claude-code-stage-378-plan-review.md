**Critical**

**C1: `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` undefined in builder module.**
The plan's `_safe_related_read_card_href` helper (placed in `saved_article_local_related_reads.py`) calls `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE.fullmatch(fragment)`, but that regex is a module-private in `templates.py` (line 188) and is not imported or redefined in the builder. This is a `NameError` at runtime. Fix: inline `re.compile(r"local-article-paragraph-[1-9][0-9]*$")` in the builder, or restrict the new href guard to `templates.py` where the regex already lives.

---

**Important**

**I1: `Sequence` not imported in `saved_article_local_related_reads.py`.**
Current imports bring in `Collection` and `Mapping` from `collections.abc` but not `Sequence`. The proposed `build_row_one_saved_article_local_related_read_lanes(cards: Sequence[...])` signature needs `Sequence` added to that import.

**I2: `_related_read_lane(...)` body and lane `dek` copy never specified.**
The plan declares `RowOneSavedArticleLocalRelatedReadLane.dek: LocalizedText` and says "Add `_related_read_lane(...)` with localized lane copy," but no dek strings appear anywhere in the task steps. Implementer must invent copy, risking blank or placeholder text shipping.

**I3: Contract denylist misses bare `"lanes"` key.**
Task 5 denylist asserts compound names (`"saved_article_local_related_read_lanes"`, etc.) are absent from the generated contract payload. However, adding `lanes: tuple[..., ...] = ()` to `RowOneSavedArticleLocalRelatedReads` would serialize as the key `"lanes"` — a short key not covered by any denylist entry. If the model is ever serialized to the app/runtime contract, the guard gives false confidence.

---

**Minor**

**m1: `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_LANES = 3` is a no-op constant.**
`deduped_by_lane` is hardcoded to exactly three keys; the final `[:SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_LANES]` slice can never truncate. The constant adds maintenance surface without guarding anything real.

**m2: Test fixture may give `same_source` story an identical `section_key`.**
Task 2 Step 1 test builds `same_source` via `_story("same-source-3333333333", section_key="brand_moves")` but does not show the current story's section_key. If `_story()` defaults match `"brand_moves"`, the candidate scores `same_section=True` and emits a `"Same ROW ONE section"` reason, silently breaking the lane-order assertion.

**m3: Render test `html.index('id="local-article"')` may raise `ValueError`.**
Task 4 Step 1 asserts lane markup appears after `id="local-article"` using `str.index`. If the test helper renders only the related-reads section fragment rather than a full local-article page, `id="local-article"` is absent and `index()` throws instead of failing cleanly.

END_OF_REVIEW
