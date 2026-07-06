Here is the plan review.

---

## Stage 317 Plan Review

### Critical findings

None.

---

### Important findings

None.

---

### Minor findings

**M1 — Incomplete function body for `_render_local_article_content_item` update (Task 1, Step 3)**

The plan shows the new helper and the updated signature for `_render_local_article_content_item`, but the insertion block uses `...` and references `parts` instead of showing the complete updated function body:

```python
previews = _render_local_article_content_paragraph_previews(...)
...
if previews:
    parts.append(previews)
```

The existing code uses `item_parts`, not `parts`, and the `...` leaves the exact insertion point implicit. An engineer following the plan must infer that the preview block goes after the optional body and before the existing `paragraphs = _render_local_article_paragraph_links(...)` call. The tests will catch a wrong insertion order, but showing the complete function body would remove the ambiguity and be consistent with the plan's own no-placeholders rule.

---

**M2 — Stage 316 slice update placement is ambiguous (Task 2, Step 2)**

Step 2 is titled "Add failing docs guard" and contains the new Stage 317 test, but it also shows the Stage 316 slice boundary change inline in the same code block. The Stage 316 slice (`readme_stage_316 = readme[... : readme.index("Stage 317 adds")]`) belongs in the existing `test_row_one_docs_describe_local_article_content_organization_boundary()` function, not in the new Stage 317 test. The way it is presented, an engineer could put both slices inside the new test function. Splitting the step — first edit the existing Stage 316 test, then add the new Stage 317 test — would prevent the confusion.

---

**M3 — `rendered_indices` semantics not narrated for Stage 317 workers (Task 1, Step 3)**

The plan reuses `rendered_indices` as passed to `_render_local_article_content_paragraph_previews`, but does not note that this set is the pre-computed allowlist of non-blank in-range indices (from `_local_article_rendered_paragraph_indices`), not an accumulating set of already-emitted indices. The `seen` set inside `_valid_local_article_paragraph_indices` handles intra-call dedup locally; `rendered_indices` is never mutated. An engineer unfamiliar with Stage 316 could misread the name and attempt to add mutation logic. A one-line comment in the helper would remove the confusion.

---

### Final recommendation

**Ready to implement.** No Critical or Important findings. The plan is well-sequenced after Stage 316, touches only the correct files, and its tests cover all specified behaviors: rendering, bilingual alignment and mismatch, escaping, cap at two, intra-item dedup, negative and out-of-range filtering, blank-paragraph suppression, anchor correctness, generated-contract exclusion, and doc boundary guards. The three minor findings are all small clarity gaps that the test suite would catch if an engineer guesses wrong; none blocks implementation.
