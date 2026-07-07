## Stage 328 Code Review

### Critical

None.

### Important

None.

### Medium

**1. `_support_excerpt` consumes `items` as a generator but passes a materialized tuple to `_item_body_excerpt` and also passes the original `paragraph_indices` to `_paragraph_excerpt` - iteration safety.**
`saved_signal_index.py:+358-365`

`items` is typed `Iterable[...]` at the call site. The fix materializes it into `item_list = tuple(items)` before passing to `_item_body_excerpt`, which is correct. However, `_paragraph_excerpt` independently re-runs `_strict_valid_saved_signal_paragraph_indices` on `paragraph_indices`, which is also an `Iterable`. Since `paragraph_indices` originates from `_referenced_paragraph_indices(items)` (a tuple), this is safe in practice today - but the function signature accepts `Iterable[object]`, so a caller passing a one-shot iterator would silently produce no results on the second traversal. Consider typing `paragraph_indices` as `Sequence[object]` or materializing it inside `_support_excerpt` like `items` was. Low likelihood of breaking now, but worth tightening.

### Minor

**1. `_saved_signal_excerpt_text` normalizes before checking length, but `_localized_excerpt` calls it twice with no shared result.**
`saved_signal_index.py:+318-333`
Both `en_text` and `zh_text` are computed independently, which is fine for correctness. No concern beyond the minor redundancy if both fields reference the same string (unlikely in practice).

**2. Excerpt position in DOM confirmed by test, but the CSS rule has no `max-width` / `clamp`.**
`templates.py:+1363-1368`
`overflow-wrap: anywhere` prevents hard layout breaks, but very long normalized excerpts (up to 220 chars of unbroken CJK) could still push the column wide on narrow viewports. Existing `padding: 36px min(7vw, 88px)` on `main` constrains the outer container, so this is unlikely to surface as a real issue. Worth noting if the index layout ever adds side-by-side columns.

**3. `_without_fenced_code` in `test_row_one_docs.py` splits naively on triple backticks.**
`test_row_one_docs.py:+80-81`
`"".join(text.split("```")[::2])` strips fenced blocks correctly for standard markdown, but a doc containing an inline `` `code span` `` with the word `row-one-app/v8` inside it would not be stripped. Given the boundary phrases checked are version strings unlikely to appear in inline code, this is fine for the current use case but not a general-purpose fence stripper.

**4. Workflow test assertion is conditional.**
`test_workflows.py:+475–477`
```python
if articles_html_path.exists():
    articles_html = articles_html_path.read_text(...)
    if "saved-signal-index-support-row" in articles_html:
        assert "saved-signal-index-support-excerpt" in articles_html
```
The assertion only fires when the generated file both exists and contains a support row. If the workflow test fixture produces no saved signals, the new assertion is never exercised. This is consistent with how the rest of the workflow test is structured (it tests the real workflow output), so it's acceptable - but it means excerpt regression would only be caught if the test data includes at least one saved signal with a qualifying article.

### Verdict

**Approved.** The change is tightly scoped, properly bounded (no new JSON artifacts, no contract changes, no runtime behavior), and well-covered by 11 new targeted tests. XSS escaping is correct and verified. The zh-only fallback fix is clean. The one medium-severity note (`Iterable` re-traversal in `_paragraph_excerpt`) is safe today given how callers materialize the value, but the type signature is worth tightening in a follow-up to prevent a silent bug if the signature is reused.
