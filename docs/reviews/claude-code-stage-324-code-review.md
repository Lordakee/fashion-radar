Here is the full code review for Stage 324.

---

## Critical Findings

None.

---

## Important Findings

None.

---

## Minor Suggestions

**1. Empty `<div>` when an evidence item has no references**

In `_render_local_article_paragraph_evidence_support`:

```python
refs = "".join(_render_local_article_paragraph_evidence_ref(ref) for ref in item.references)
return f"""...<div>{refs}</div></div>"""
```

When `item.references` is empty, this emits `<div></div>`. Not harmful, but slightly untidy. A simple guard would clean it up:

```python
refs_html = (
    f'<div>{refs}</div>\n'
    if refs else ""
)
```

**2. No zh fallback in evidence item body rendering**

In `_render_local_article_paragraph_evidence_support`, when `item.item_body.zh` is an empty string:

```python
body_zh = _esc(_local_article_paragraph_evidence_body(item.item_body.zh))
```

The zh span renders as `<span data-lang="zh"></span>` — an empty paragraph in zh mode. This is consistent with how other sections in the file render content without a zh value, so it's not a bug, but it's a cosmetic edge case worth being aware of. The existing pattern in the codebase (e.g., `_render_local_article_content_item`) is the same, so no change is strictly required.

**3. Map link presence not explicitly asserted**

`test_render_row_one_detail_includes_local_article_paragraph_evidence_index` verifies the ordering relationship:

```python
assert detail_html.index('class="local-article-map"') < detail_html.index(
    'id="local-article-paragraph-evidence"'
)
```

This confirms the map precedes the evidence block but does not directly assert that `href="#local-article-paragraph-evidence"` appears inside the map HTML. The `_render_local_article_map` change is exercised indirectly, but a direct assertion like:

```python
map_html = detail_html[
    detail_html.index('class="local-article-map"') : detail_html.index(
        'id="local-article-paragraph-evidence"'
    )
]
assert 'href="#local-article-paragraph-evidence"' in map_html
```

would make the map-link contract explicit. Minor, since the behavior is functionally covered.

---

## Review Notes by Focus Area

**Correctness of mapping, caps, dedupe, escaping, anchors**

All correct. The `_local_article_paragraph_evidence_entries` builder:
- Uses `_strict_valid_local_article_paragraph_indices` (bool/non-int rejection + rendered-index validation + dedupe) before fragment generation. The bool guard order — `not isinstance(index, int) or isinstance(index, bool)` — is correct because `bool` is a subclass of `int`.
- Builds a `mapped: dict[int, list[...]]` keyed by zero-based paragraph index, iterated in sorted order for stable output.
- Per-paragraph item deduplication via `seen_items[index]` using a comprehensive tuple key (section position, normalized titles, normalized labels, normalized body, normalized refs tuple).
- Row cap at8, items-per-row cap at 4, refs-per-item cap at 4, all applied in the right order.
- Paragraph anchors are1-based (`index + 1`), consistent with the rest of the codebase.
- Section anchors use the1-based `section_position` from `enumerate(..., start=1)`, consistent with how content sections are rendered and addressed throughout.
- Excerpt and body truncation go through `normalize_row_one_paragraph` → `_meta_description`. All output goes through `_esc()` at render time. No unescaped values reach the HTML.
- zh fallback in excerpts (when `aligned_zh[index]` is blank) falls back to `excerpt_en`, consistent with the reader and digest helpers.

The insert position in `_render_local_article` — after `article_map`, before `digest` — matches the declared spec and is verified by ordering assertions in the tests.

**Test adequacy**

Coverage is solid across the key behaviors: basic rendering, omission when no mapping exists, index filtering (negative, out-of-bounds, blank paragraphs, duplicates), bool rejection in the standalone helper, XSS escaping in all user-supplied fields (section title, item label, item body, ref name/type/label, paragraph text), all three caps (rows × items × refs), and the contract math (8 × 4 × 4 = 128 refs). The only omission is the explicit map-link assertion noted above, which is minor.

**Generated-site-only and JSON-contract boundaries**

Fully preserved. The paragraph evidence renderer is called exclusively from `_render_local_article` → `render_detail_html`. No JSON payload builders are touched. No new model fields, no new Pydantic validators, no new data files. `test_workflows.py` explicitly checks that `"local_article_paragraph_evidence"` and `"paragraph_evidence_index"` are absent from the generated contract payload. The `_render_local_article_map` change introduces `include_paragraph_evidence=False` as a defaulted parameter, so all existing call sites are unaffected.

**Docs and review artifacts**

The Stage 324 doc content is tested in `test_row_one_docs_describe_stage_324_paragraph_evidence_index_boundary`, which verifies the key boundary phrases (generated-site only, no JSON contract changes). The docs/reviews artifacts follow the same pattern as prior stages and are appropriate to commit.

**Regression risk**

Very low. The new code path activates only when `content_sections` contain items with valid `paragraph_indices` pointing to non-blank paragraphs. When that condition is not met, `paragraph_evidence` is an empty string and the template renders identically to before. The `include_paragraph_evidence=False` default in `_render_local_article_map` guarantees no change to existing paths that don't trigger the new builder. No shared state, no side effects on the index page, JSON payloads, signal briefing, or any other detail-page block.

---

## Final Verdict

**Approved to commit.**

The implementation is correct, complete, and well-bounded. All three scope constraints (no app/manifest/runtime contract changes, no new artifact fields, generated-site only) are maintained and tested. The three minor suggestions above are non-blocking and can be addressed in a future cleanup stage if desired.
