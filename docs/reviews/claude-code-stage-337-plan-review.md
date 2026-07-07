Having read all the listed files, here is the full review.

---

## Stage 337 Plan Review — Saved Article Reference Atlas

### Checklist Findings

---

####1. Generated-site-only boundary

**Pass.** The plan creates one new Python module (`saved_article_reference_atlas.py`) and writes only HTML into the existing `articles/index.html` write path. No new filesystem destinations are added. The full-site test explicitly asserts `not (tmp_path / "data" / "saved-article-reference-atlas.json").exists()`. The builder is called strictly after `saved_article_theme_digest` and before `_write_saved_article_library_page`. No homepage change.

---

#### 2. App/runtime/manifest/schema/JSON contract boundary

**Pass.** The full-site test directly checks:

```python
assert edition_payload["contract_version"] == "row-one-app/v7"
assert manifest_payload["contract_version"] == "row-one-manifest/v1"
assert runtime_payload["contract_version"] == "row-one-runtime/v1"
```

and iterates all three contract JSON dumps checking that none contain `saved_article_reference_atlas`, `reference_atlas`, `saved-article-reference-atlas`, `Saved Article Reference Atlas`, `保存文章引用图谱`, or `Alaia flats`. Consistent with the Stage 336 contract test pattern.

---

#### 3. No collection/extraction/scoring/LLM/connector behavior

**Pass.** The builder takes only `RowOneSavedArticleLibrary` and `RowOneSavedArticleContentOrganization` — both already built in `render_row_one_site()` before the new call. No new sources, fetching, extraction, LLM calls, scheduling, social connectors, or compliance behavior.

---

#### 4. Builder inputs — sufficient and not dead-coupled

**Pass.** Both inputs are live objects already in scope at the call site. The data flow in the spec (§Data Flow) matches exactly what `render.py` shows: `saved_article_library` is built at line 122, `saved_article_content_organization` at line 118, `saved_article_theme_digest` at line 134, and the new `saved_article_reference_atlas` call goes after those. The two-object signature mirrors `build_row_one_saved_article_theme_digest(library, organization)` exactly.

---

#### 5. Reference bucketing, dedupe, source counts, support counts, caps, safe-route filtering

**Mostly pass, one edge-case worth confirming.** The logic is coherent:

- **Bucketing** is by normalized `type`/`label` in definition order (Brands → People → Products → Source Context). The cap of 4 buckets matches the 4-group definition.
- **Dedupe** key `(bucket_key, normalized_name)` correctly preserves first display casing while counting duplicates — consistent with how `_references()` in `saved_article_content_organization.py` deduplicates within a single card.
- **Source counting** uses `normalized source name` case-insensitively across supports — consistent with `_source_key()` in `saved_article_theme_digest.py`.
- **Safe-route filtering** follows the exact same path-validation chain already established in `saved_article_theme_digest.py` (`_safe_content_section_href` → `validated_row_one_detail_relative_path` → library membership check). The unsafe-path rejection test covers traversal, `javascript:`, unmatched library paths, and non-content-section fragments — all four cases handled.
- **Caps**: 4 buckets / 6 refs / 3 supports. The cap test builds 8 unique brand cards and asserts `len(atlas.buckets[0].references) == 6`. Sound.
- **Sort**: support_count descending with first-seen as tie-breaker. Deterministic with no external ranking implied. The positive test result ordering (`["brands", "people", "products"]`) correctly reflects bucket-definition order, not occurrence order.

One minor coherence note: the spec says `tracked` belongs in Brands "when the reference name is not empty". The builder description restates "skip references whose `name.strip()` is empty" as a global pre-filter before bucketing. The test fixture uses `RowOneReference(name="The Row", type="brand", label="tracked")` which lands in Brands via `type="brand"`. This is consistent, but the implementer should confirm that `tracked` in the bucket-matching logic is applied on the **label** field when `type` alone doesn't match a named bucket (e.g., a reference with `type=""`, `label="tracked"` still goes to Brands). The spec text implies this; the plan description implies this; just worth a comment in the code.

---

#### 6. Render ordering and test patterns

**Pass.** The ordering assertion:

```python
library_html.index('class="saved-article-library-hero"')
< library_html.index('class="saved-article-theme-digest"')
< library_html.index('class="saved-article-reference-atlas"')
< library_html.index('class="saved-signal-index"')
< library_html.index('class="saved-article-reading-paths"')
< library_html.index('class="saved-article-content-organization"')
< library_html.index('class="saved-article-library-grid"')
```

matches the spec UI section order exactly and follows the same index-chain assertion style used in the Stage 336 theme digest test. The CSS selector list in Task 2 Step 4 follows the existing `.saved-article-theme-digest-*` naming convention.

The direct-render safety test constructs the atlas dataclass directly and injects unsafe paths into `supports`, confirming that the renderer must re-validate — a second line of defense consistent with the theme digest's `_safe_saved_article_content_organization_href` calls in `templates.py`.

---

#### 7. Test helper names and fixture assumptions

**One Important issue, three Minor notes.**

---

### Critical Findings

None.

---

### Important Findings

**I-1 — `_theme_digest_local_article()` does not contain an "Alaia flats" product reference.**

The full-site render test (`test_render_row_one_site_includes_saved_article_reference_atlas_in_article_library`) asserts:

```python
assert "Alaia flats" in section_html
assert "Products" in section_html
assert'href="../details/the-row-signal-1234567890.html#local-article-paragraph-1"' in section_html
```

`_theme_digest_local_article()` is defined as `_signal_briefing_local_article()` with a prepended `takeaways` section containing only `RowOneReference(name="The Row", type="brand", label="tracked")`. There is no `product_signals` section with "Alaia flats" in the fixture as visible in the source.

If `_signal_briefing_local_article()` does not already contain a product section with an Alaia flats reference, these three assertions will fail regardless of correct implementation. The plan does not specify that `_theme_digest_local_article()` should be extended, nor does it introduce a dedicated atlas fixture.

**Resolution required before implementation:** Either confirm that `_signal_briefing_local_article()` already contains a `product_signals` content section with `RowOneReference(name="Alaia flats", type="shoe", ...)` and at least one `paragraph_indices` entry — or replace `_theme_digest_local_article()` with a new `_reference_atlas_local_article()` fixture that explicitly adds the Alaia flats product section. The latter is safer: it avoids any risk of Stage 336 test behavior changing due to additional content sections in a shared fixture.

---

###
