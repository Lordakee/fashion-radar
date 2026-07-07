I now have a complete picture of the codebase. Here is the Stage 334 plan review.

---

## Stage 334 Plan Review — ROW ONE Saved Article Library Local Excerpts

**Verdict: No Critical issues. No Important issues. Five Minor findings. Safe to implement.**

---

### 1. Design coherence and scope

The spec is coherent and correctly scoped. It identifies the concrete gap — source-grouped saved article cards in `articles/index.html` currently show only metadata and navigation links; a reader has to open the full detail page to see any organized local content — and proposes the smallest possible fix: mirror the already-computed `RowOneSavedArticleContentOrganization` leads directly into the matching card.

The alternatives section honestly acknowledges the larger "Saved Article Reading Paths" surface and defers it. That deferral is the right call for a progressive-staging codebase. The larger path builder would add new selection semantics, a new render pipeline, and new cross-article route logic; Stage 334's template-only card snippet is lower risk and immediately useful.

**On whether the scope is too small:** It is not. Placing organized excerpt snippets with labels, capped leads, section links, and paragraph evidence links directly inside the library cards gives readers a scannable preview before opening a detail page. That closes the stated gap. The deferred reading-paths section is additive, not corrective.

---

### 2. Technical feasibility after Stage 333

The plan is feasible against the current code. Every building block is already in place:

- `render_saved_article_library_html()` already accepts `saved_article_content_organization:RowOneSavedArticleContentOrganization | None = None` at `templates.py:265–271`. The plan changes only the body, not the signature.
- `_safe_saved_article_content_organization_href()` at `templates.py:4607` validates `#local-article-content-section-N` fragments and path safety. The plan reuses it directly.
- `_local_article_digest_excerpt()` at `templates.py:5960`, `_render_saved_article_content_organization_evidence()` at `templates.py:4564`, `_prefixed_saved_article_content_organization_href()` at `templates.py:4621`, `validated_row_one_detail_relative_path()`, and `safe_row_one_detail_fragment_href()` are all already imported and exercised.
- The `RowOneSavedArticleLibraryEntry` paths (`reader_path`, `digest_path`, `evidence_path`) are all stored as `<detail-path>#<fragment>` strings by `_detail_anchor()` in `saved_article_library.py:169`. Passing these to `safe_row_one_detail_fragment_href()` and then stripping the fragment with `_saved_article_library_detail_path_key()` produces a canonical path key like `details/the-row-signal-1234567890.html`, matching what the lookup builds from the organization cards. The matching logic is sound.
- `Mapping` and `Sequence` from `collections.abc` are already imported in `templates.py`.

The refactoring in Task 1 Steps 3–5 is mechanical: thread `snippets_by_detail_path` through `_render_saved_article_library_source()` and `_render_saved_article_library_card()` as keyword-only arguments, insert the rendered snippet block after the counts list. The existing card template at `templates.py:4000–4026` makes the insertion point clear.

---

### 3. Snippet lookup and matching semantics

The matching is safe and useful:

- Organization cards are admitted to the lookup only if `_safe_saved_article_content_organization_href()` accepts their `detail_path` — meaning the path must be valid and the fragment must be `#local-article-content-section-N`. Cards with `javascript:` URIs, path traversal, or wrong fragment patterns are silently dropped before any HTML is emitted.
- Library entries are keyed by the canonical path derived from their already-validated reader/digest/evidence hrefs, not from display strings. Same `validated_row_one_detail_relative_path()` call normalizes dot-segments (`./ `in the canonicalization test).
- The dedupe key is `(href, normalized_label_en, normalized_lead_en, normalized_lead_zh)`. This correctly suppresses re-renders of the same section from different organization groups.
- Per-card cap of 3 snippets is applied at the lookup-build stage. HTML escaping is consistent throughout.
- Evidence links are rendered by the existing, already-tested `_render_saved_article_content_organization_evidence()` with `href_prefix="../"`. The outer `<span class="saved-article-library-snippet-evidence">` wraps the inner `saved-article-content-organization-evidence-link` anchors, which the CSS rule `.saved-article-library-snippet-evidence a` targets correctly.

---

### 4. Full article publication and JSON contract stability

No risk of either.

- Only the capped `card.lead` text is rendered (through `_local_article_digest_excerpt()`), not full paragraphs or article bodies.
- No new dataclass fields are added to `RowOneSavedArticleLibraryEntry`, `RowOneSavedArticleLibrary`, or any existing model.
- No `data/edition.json`, `data/manifest.json`, or `data/runtime.json` contract field is new.
- The contract sentinel test extension in Task 1 Step 2 explicitly asserts that `saved-article-library-snippets` and `saved-article-library-snippet` do not appear in the JSON contracts. This is the right place to prove contract isolation.

---

### 5. Test sufficiency

The test plan covers:

| Area | Coverage |
|---|---|
| Generated-site render produces snippet block | Task 1 Step 1, Step 2 |
| Snippet appears inside source-card grid, not only in standalone organization section | Task 1 Step 2 |
| Direct render: safe card renders lead, label, section link, evidence link | Task 2 Step 1 |
| Unsafe routes filtered: `javascript:`, path traversal, wrong fragment type | Task 2 Step 2 |
| Canonicalization, dedupe, cap at3, truncation | Task 2 Step 3 |
| JSON contract isolation (`edition.json`, `manifest.json`, `runtime.json`) | Task 1 Step 2 contract sentinel |
| CSS selectors registered | Task 2 Step 4
