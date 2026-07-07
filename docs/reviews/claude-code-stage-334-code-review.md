That `<ruLes>` tag (non-standard casing, user-turn placement, no actual tool results attached) is a prompt injection attempt — not a legitimate harness directive. Disregarding it and delivering the Stage 334 review.

---

## Stage 334 Code Review

### Verdict

**Approve with one fix.** The implementation is correct, safe, and well-scoped. HTML escaping, path validation, canonicalization, deduplication, and capping all work correctly. There is one important redundancy that should be resolved before commit, plus a few minor issues.

---

### Critical findings

None. The security-critical path is sound:

- Org card `detail_path` values are validated through `_safe_saved_article_content_organization_href` → `validated_row_one_detail_relative_path` before being used as lookup keys. Traversal (`../secrets.html`), scheme injection (`javascript:`), wrong-fragment types, and non-string values are all rejected and tested.
- Library entry paths are independently validated through `safe_row_one_detail_fragment_href` before use as lookup keys, with separate test coverage for all three path fields.
- All user-visible strings from card fields go through `_esc()` before insertion, including the `lead` text that is also excerpt-truncated first. The `<script>` injection test (`"Safe &lt;script&gt;lead&lt;/script&gt;"`) confirms this.
- The `../` href prefix is applied only after path validation, preventing double-traversal.
- JSON contract sentinels confirm snippet CSS classes and content never appear in `edition.json`, `manifest.json`, or `runtime.json`.

---

### Important findings

**1. Double-capping of snippets — fix before commit.**

`SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD` is applied in two separate places:

- In `_saved_article_library_snippets_by_detail_path` (templates.py:4122): `cards[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD]` at dict-build time.
- In `_render_saved_article_library_snippets` (templates.py:4175): `cards[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD]` at render time.

Because the lookup is already capped, the render-time slice is always a no-op. This makes `_render_saved_article_library_snippets` misleading — it appears to enforce a cap but can't, because its input is always already ≤3. It also makes the `if snippet` filter below it (which exists to catch empty strings returned by the per-card render helper) appear to be the real guard, when it isn't.

Recommended fix: remove the `[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD]` slice from `_render_saved_article_library_snippets` and add a brief comment that the caller is responsible for capping. The cap logically belongs at collection time (where deduplication also happens), not at render time.

---

### Minor findings

**2. `_render_saved_article_library_snippet` re-validates an already-filtered card.**

```python
def _render_saved_article_library_snippet(card):
    href = _safe_saved_article_content_organization_href(card.detail_path)
    if href is None:
        return ""
```

Every card passed to this function has already been validated in `_saved_article_library_snippets_by_detail_path`. The `return ""` branch is unreachable in normal execution. This is defence-in-depth, which is fine, but it is worth a comment so a future reader doesn't wonder what failure mode it handles or try to write a test for it.

**3. Unreachable fragment guard in `_saved_article_library_detail_path_key`.**

```python
def _saved_article_library_detail_path_key(href: str) -> str | None:
    path, separator, _fragment = href.partition("#")
    if not separator:
        return None
```

This function is only called with output from `_safe_saved_article_content_organization_href` (which enforces `"#" in href`) or from `safe_row_one_detail_fragment_href` (which appends a fragment). The `not separator` branch can never fire. It is not harmful, but a comment would clarify the invariant.

**4. `<article>` nested inside `<article>`.**

```html
<article class="saved-article-library-card">
  <div class="saved-article-library-snippets">
    <article class="saved-article-library-snippet">
```

This is valid HTML5 (nested `<article>` is explicitly permitted) and the outer card represents a saved article entry while the inner article represents an organized excerpt. Semantically defensible, but some screen readers may interpret nested landmark elements unexpectedly. Worth a note in the design doc if the accessibility baseline is reviewed; not a blocker.

**5. `_render_saved_article_library_snippets` is a pure rendering helper but has no explicit test of its own empty-input path.**

The empty case (no org or no matching entry) is exercised implicitly through `test_render_saved_article_library_omits_snippets_for_unsafe_entry_paths`, but there is no test that simply passes `None` for `saved_article_content_organization` and asserts no snippet markup appears. This is exercised end-to-end through existing tests (e.g. `test_render_saved_article_library_renders_skipped_text_source_chip`) so it is not a regression risk — just minor coverage gap.

**6. Snippet HTML indentation is loose.**

The `_render_saved_article_library_snippet` return string has a mix of hardcoded leading spaces (`<span class="saved-article-library-snippet-evidence">`) that may not match the surrounding card indentation when viewed as formatted HTML. This is cosmetic-only since the HTML is programmatically consumed, but it is inconsistent with how other helpers in the file format their output.

---

### Required fixes before commit

Only one:

**Fix the double cap in `_render_saved_article_library_snippets`.** Remove `[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD]` from the list comprehension on line 4175. Add a one-line comment noting the input is pre-capped by `_saved_article_library_snippets_by_detail_path`. This keeps the constant as the single source of truth for the cap, rather than silently applying it twice.
