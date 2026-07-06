Here is the full Stage 318 review.

---

## No Critical or Important issues found.

The implementation is correct on all stated requirements. Detailed findings below.

---

### Correctness — Selection Algorithm

`_detail_continue_reading_stories` (templates.py:3406–3430):

- Excludes current story by `candidate.id != story.id`. ✓
- Builds same-section candidates first, then other-section candidates, both iterating `edition.stories` in order → edition order within each group is preserved. ✓
- Deduplicates via `seen_paths` keyed on the resolved sibling filename, so stories pointing to the same `detail_path` are collapsed. ✓
- Caps at `DETAIL_CONTINUE_READING_MAX_ITEMS = 3`. ✓

### Route Safety

`_detail_continue_reading_href` (templates.py:3459–3463) delegates to `validated_row_one_detail_relative_path`, the same validator used across all other link sites in the codebase. Path-traversal inputs like `"../unsafe.html"` return `None`; the caller silently skips them. Sibling filenames are taken from `pure_path.name`, which strips the `details/` prefix correctly — links render as `same-section-1234567890.html`, not `details/same-section-1234567890.html`. ✓

### Escaping

All card fields — section title, headline, source name, excerpt — pass through `_esc()` at the point of interpolation (templates.py:3443–3455). Excerpts go through `_display_summary_text` first (strips RSS/feed HTML markup) before truncation, then through `_esc()`. No raw interpolation. ✓

### Excerpt Fallback

```python
excerpt_en = _detail_continue_reading_excerpt(story.summary.en or story.editorial_takeaway.en)
```

Empty-string `summary.en` correctly falls back to `editorial_takeaway.en` because `""` is falsy. One technically-reachable edge case: a whitespace-only summary like `"   "` is truthy, so it would not fall back, but `_display_summary_text("   ")` normalises to `""` making the excerpt visibly empty rather than incorrect. Negligible in practice.

### Placement

`{continue_reading}` is injected at templates.py:288, between the closing `</section>` of `#evidence-trail` and `</article>`. No `#continue-reading` link is added to `_render_article_contents` or `_render_local_article_map`. Correct per spec. ✓

### Contract / Schema Isolation

The workflow test (test_workflows.py:393–420) explicitly asserts:

```python
assert '"continue_reading"' not in generated_contract_payload
assert '"related_stories"' not in generated_contract_payload
```

and verifies `contract_version` pins for `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1` remain unchanged. The top-level `data/*.json` allowlist check is preserved. The second SQLite item (needed so the rail has a sibling to recommend) is verified immutable after the site write. ✓

No new JSON artifact is written. ✓

### Docs Boundary Sentinel

`test_row_one_docs_describe_detail_continue_reading_boundary` uses `"Stage 310 adds"` as the end sentinel (test_row_one_docs.py:449, 452). This works because the README and `docs/row-one.md` list stages in reverse-chronological order (newest first). Stage 310 therefore appears *after* Stage 318 in the file. The slice is non-empty and the assertions run correctly.

This is worth a comment: if Stage 319 is added in the same reverse-order style, the Stage 318 test will still work (Stage 310 remains a valid downstream sentinel). No action needed, but worth keeping in mind when the sentinel-chaining convention is documented.

---

### Minor Issues

**1— Card element type diverges from plan spec.**

The implementation renders:
```html
<article class="continue-reading-card">
  <a href="other-story.html">…</a>
</article>
```
The design spec and plan described `<a class="continue-reading-card" href="...">` (anchor as the card root). The CSS accounts for this with `.continue-reading-card a` rules for layout and colour. Tests pass. The `<article>` wrapper is semantically valid and arguably more correct for a self-contained content unit. This is a harmless deviation but worth noting if the spec is treated as the canonical structural reference.

**2 — No CSS selector test for the continue-reading component.**

Every prior stage that introduced CSS classes (saved-article-coverage, saved-article-briefs, content-organization, local-article reader/digest) added a `test_row_one_css_includes_*_styles` test that verifies the relevant selectors are present in the generated stylesheet. Stage 318 omits this. A regression that accidentally deletes `.continue-reading-grid { grid-template-columns: repeat(3, …) }` would go undetected. No functional impact today, but inconsistent with the established pattern.

**3 — Whitespace-only summary does not trigger editorial_takeaway fallback.**

Covered in the escaping section above. Not worth a test — the normaliser produces an empty visible excerpt rather than leaking whitespace. Noted for completeness.
