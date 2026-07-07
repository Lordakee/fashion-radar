Now I have everything I need. Here is the complete rereview.

---

## Stage 334Plan Rereview — ROW ONE Saved Article Library Local Excerpts

**Verdict: No Critical issues. No Important issues. Five Minor findings. Safe to implement.**

---

### Critical findings

None.

---

### Important findings

None. The lookup/matching logic is sound: both the organization side and the entry side independently key on the path returned by `validated_row_one_detail_relative_path`, discarding the fragment. Unsafe routes, traversal, wrong fragment types, and `javascript:` URIs are all rejected before any HTML is emitted. Contract isolation (no new JSON fields, no new sidecar keys) is verified by the sentinel extensions in Task 1 Step 2.

---

### Minor findings

**M1 — `Mapping` not imported (`templates.py:3`)**
The existing import is `from collections.abc import Sequence`. The new helpers in Task 1 Steps 3–4 use `Mapping[str, Sequence[...]] | None` in four signatures. Add `Mapping` to line 3:
```python
from collections.abc import Mapping, Sequence
```
Without this, Ruff will emit `F821` and the type-check step fails immediately.

**M2 — "Read first" / "正文速览" assertion may not match the inline fixture (Task 1 Step 1)**
`test_render_row_one_site_writes_saved_article_library_page` builds its local article inline with `key="entities"` and item `label=LocalizedText(zh="The Row", en="The Row")`. The plan asserts `'<span data-lang="en">Read first</span>'` for `card.section_label.en`. That value comes from the content-organization builder, not the test plan. Before writing the assertion, verify what `section_label.en` the builder actually produces for a `key="entities"` section — it is likely `"People & Brands"`, not `"Read first"`. Use the actual value, or add a "read_first" content section to the inline fixture.

**M3 — Evidence-span double-wrap (`templates.py:4594`, Plan Task 1 Step 5)**
`_render_saved_article_content_organization_evidence()` already returns `<span class="saved-article-content-organization-evidence">…links…</span>`. The snippet renderer then wraps that in `<span class="saved-article-library-snippet-evidence">`. The plan's CSS targets `.saved-article-library-snippet-evidence a`, which works, but the inner `.saved-article-content-organization-evidence` class will also be present and pick up any CSS rules for that class from the content-org section. Before shipping, confirm there are no conflicting rules in `row_one_css()` for `.saved-article-content-organization-evidence a` that would bleed into the library card context.

**M4 — Redundant per-card cap in `_render_saved_article_library_snippets` (Plan Task 1 Step 5)**
The lookup builder in Task 1 Step 4 already emits `tuple(cards[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD])`. The renderer then slices `cards[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD]` again. Harmless and defensive, but the cap-at-3 test in Task 2 Step 3 verifies only the final rendered count, not which layer enforced it. No fix required; note it if debugging future cap changes.

**M5 — No explicit test for a library entry with no valid detail paths (Plan Task 2)**
`_saved_article_library_entry_detail_path` returns `None` when all three of `reader_path`, `digest_path`, and `evidence_path` are absent or unsafe, and the card silently emits no snippet block. The unsafe-filtering test in Task 2 Step 2 tests bad *organization* card paths, not a missing *library entry* path. Add a one-line assertion to an existing test (or the unsafe-filter test) confirming that a library entry with no valid paths produces no `.saved-article-library-snippets` element for that card.

---

### Safe to implement

Yes. M1 (missing import) must be fixed before the Ruff check passes; M2 (label assertion) must be verified before Task 1 Step 1 can go green. M3–M5 are low-risk and can be addressed inline during implementation without blocking the commit.
