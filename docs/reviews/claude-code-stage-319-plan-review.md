**All eight prior issues are resolved. No new Critical or Important issues found.**

---

**Prior issue status**

- **C1 (paragraph helper signature)** — Fixed. `_first_valid_local_article_paragraph_index` now takes `rendered_indices: set[int]` obtained from `_local_article_rendered_paragraph_indices(article)` and passes it correctly to `_valid_local_article_paragraph_indices`.

- **C2 (content-section paragraph-index traversal)** — Fixed. The helper iterates `section.items → item.paragraph_indices`, deduplicates with `seen_indices`, builds a flat list, then calls `_valid_local_article_paragraph_indices` and returns `valid_indices[0]`. Matches the design's "collect from all items, dedup first-seen, first valid only."

- **C3 (dedup fixture specificity)** — Fixed. The fixture has two identical `The Row` refs in `entity_refs` and two more in `content_sections[0].items[0].references`, plus `Alaia flats` in the second content-section. After dedup, unique refs are: The Row, Mary-Kate Olsen, Margaux, Signal `<script>Brand</script>`, Alaia flats = 5, matching the `count('class="detail-signal-briefing-ref"') == 5` assertion and `count(">The Row<") == 1`.

- **C4 (safe evidence count definition)** — Fixed. Implementation uses `sum(1 for link in story.evidence if _safe_external_url(link.url) is not None)`, exactly matching the design's "count only evidence links accepted by `_safe_external_url`."

- **I1 (CSS test order)** — Fixed. The CSS selector test is now written in Task 1 Step 4 (second) and the combined red-run verification is Step 5, so the CSS test exists before it is expected to fail.

- **I2 (nullable local_article typing)** — Fixed. All helpers declare `local_article: RowOneLocalArticle | None` and guard on `None` before delegating to the non-nullable inner function.

- **I3 (lower why-it-matters preservation)** — Fixed. The test explicitly slices the lower `id="why-it-matters"` section after the panel and asserts `"This signal belongs in Top Stories."` is still present there.

- **I4 (first-valid paragraph-index ambiguity)** — Fixed. The design's intent (collect all indices across items, dedup, validate, return first valid) is precisely what `_first_valid_local_article_paragraph_index` does. The fixture's `[0, 1]` deduped → `[0, 1]` valid → `0` → link `#local-article-paragraph-1`, matching the test assertion.

---

**New issues**

**Minor** — Task 1 has two steps numbered "Step 4": the first is "Verify render tests fail" and the second is "Add the CSS selector failing test." The duplicate label is confusing but has no functional impact on the implementation.

---

No Critical or Important issues remain.
