Now I have everything I need. Here is the re-review.

---

## Stage 337 Plan Re-Review — Saved Article Reference Atlas

### Five Specific Checks

---

**Check 1 — `_reference_atlas_local_article()` explicitly defined; no reliance on `_theme_digest_local_article()` ambiguity**

**Resolved.** Task 2, Step 1 explicitly adds a dedicated `_reference_atlas_local_article()` helper and states: "Add a dedicated `_reference_atlas_local_article()` helper rather than relying on `_theme_digest_local_article()`." The plan specifies it starts from `_theme_digest_local_article()` and produces a `model_copy()` whose `content_sections` explicitly enumerate the read-first section, `entities` (The Row brand), and `product_signals` (Alaia flats) — making Stage 337 render assertions independent of Stage 336 fixture drift. The prior I-1 finding is resolved.

Verified against the live fixture: `_signal_briefing_local_article()` at line 232 already carries both `entities` (The Row, type=brand) and `product_signals` (Alaia flats, type=shoe) — so the prior claude-code concern that the fixture lacked Alaia flats was incorrect for the base fixture, but the new dedicated helper removes all doubt regardless.

---

**Check 2 — CSS selector sentinel test present**

**Resolved.** Task 2, Step 1 includes `test_row_one_css_includes_saved_article_reference_atlas_styles` with all 19 selectors (`.saved-article-reference-atlas` through `.saved-article-reference-atlas-link`) using the same `re.search` regex pattern as the Stage 336 test. The test is wired into the focused verification command at Step 2 and Step 5. The prior Minor 1 (opencode) finding is resolved.

---

**Check 3 — `_library_with_safe_stories(*story_ids)` plural helper defined**

**Resolved.** Task 1, Step 1 names the helper explicitly, specifies its signature `_library_with_safe_stories(*story_ids: str)`, and states it generalizes the Stage 336 singular `_library_with_safe_story()` helper by emitting one `RowOneSavedArticleLibraryEntry` per story id with safe `digest_path`, `reader_path`, and `evidence_path` fragments. It appears in the dedupe test, cap test, and unsafe-path test, confirming the implementation expectation is fully covered. The prior Minor 2 (opencode) finding is resolved.

---

**Check 4 — Canonical bucket order and first-seen tie-break stated**

**Resolved.** The spec (§Reference Bucketing) states: "Render bucket groups in canonical order: Brands, People, Products, then Source Context; within each bucket, sort references by support count descending, then first-seen order." The plan builder description mirrors this exactly: "render buckets in canonical order: `brands`, `people`, `products`, `source_context`" and "sort references by `support_count` descending and first-seen order as tie-breaker." The positive builder test's assertion `[bucket.key for bucket in atlas.buckets] == ["brands", "people", "products"]` is consistent with definition order, not occurrence order. The prior Minor 3 (opencode) finding is resolved.

---

**Check 5 — All boundary protections intact**

**Pass.** No regressions found:

- **Generated-site-only**: builder writes only HTML in `articles/index.html`; homepage is explicitly excluded by the full-site test assertion `assert 'class="saved-article-reference-atlas"' not in homepage_html`.
- **JSON contract**: full-site test asserts `contract_version == "row-one-app/v7"`, `"row-one-manifest/v1"`, `"row-one-runtime/v1"` and iterates all three contract dumps checking absence of all atlas vocabulary (`saved_article_reference_atlas`, `reference_atlas`, `Alaia flats`, `保存文章引用图谱`, etc.).
- **No JSON artifact**: `assert not (tmp_path / "data" / "saved-article-reference-atlas.json").exists()`.
- **No collection/extraction/scoring/LLM/connector/scheduling/deployment**: builder inputs are `(library, organization)` — both already in scope in `render_row_one_site()`; nothing new is sourced.
- **Docs sentinel**: `test_row_one_docs_describe_stage_337_saved_article_reference_atlas_boundary` tests both `README.md` and `docs/row-one.md` for the exact boundary paragraph and explicitly asserts absence of `"row-one-app/v8"`, `"writes a new json artifact"`, `"adds source collection"`, `"adds fetching"`, `"adds extraction"`, `"adds trend scoring"`, `"adds heat ranking"`, `"adds connectors"`, `"adds scheduling"`, `"adds compliance review"`.

---

### New Findings

**Minor — `_reference_atlas_local_article()` fixture section numbering requires implementer attention**

The plan says the helper "starts from `_theme_digest_local_article()` and returns a `model_copy()` whose content sections explicitly include the existing read-first section plus `entities` and `product_signals`." If the fixture's `content_sections` list is `[takeaways, entities, product_signals]`, then `entities` is section 2 (`#local-article-content-section-2`) and the full-site test assertion:

```python
assert 'href="../details/the-row-signal-1234567890.html#local-article-content-section-1"' in section_html
```

is only satisfied if the content organization builder processes the `takeaways` section into a card (putting a The Row brand support at section 1). This is TDD-catchable — the test will fail at step 5 of Task 2 if the numbering is wrong, so it cannot silently pass. Recommended: add an explicit comment in `_reference_atlas_local_article()` noting which section index each key maps to, or design the fixture with `entities` as section 1 (skipping the leading `takeaways` section) if the content organization builder is confirmed to skip `takeaways`-key sections.

---

### Verdict

**Safe to implement.** All Critical and Important findings from both prior reviews are fully resolved. The one new finding is Minor and TDD-catchable. Proceed to Task 1.
