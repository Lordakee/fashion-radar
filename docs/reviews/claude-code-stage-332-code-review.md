I have all the diffs and context needed. Here is the Stage 332 code review.

---

## Stage 332 Code Review — ROW ONE Saved Article Library Content Groups

### 1. Correctness of `articles/index.html` Rendering and Placement

**None.**

`render.py` threads `saved_article_content_organization` cleanly through three call levels:

- `render_row_one_site()` → `_write_saved_article_library_page()` (`render.py:145-147`): single-line addition of the keyword argument.
- `_write_saved_article_library_page()` signature (`render.py:241-244`) and inner call (`render.py:251-254`): both updated consistently.
- `render_saved_article_library_html()` (`templates.py:267-276`): builds `content_organization` with `href_prefix="../"` before the template string, then inserts it between `{signal_index}` and `<div class="saved-article-library-grid">` (`templates.py:315-316`).

Placement matches the spec (hero → signal index → content organization → source grid). When the section renders empty — either because `organization` is `None` or all cards fail safety filtering — the empty string has no visible effect, consistent with how `signal_index` is handled.

The `RowOneSavedArticleContentOrganization` import (`render.py:30`) was correctly added, resolving the known gap flagged in both plan reviews.

---

### 2. Route and Fragment Safety, Including Validate-Then-Prefix and Canonical Output

**None.**

**Canonicalization improvement in `_safe_saved_article_content_organization_href()` (`templates.py:4555-4566`):** The function previously returned the raw `href` string. It now returns `f"{safe_path}#{fragment}"` using the canonical `safe_path` from `validated_row_one_detail_relative_path()`. A non-canonical input like `details/./story.html#local-article-content-section-1` exits the validator as `details/story.html#local-article-content-section-1`. This is strictly better and is tested in `test_render_saved_article_library_canonicalizes_content_organization_links`.

**Prefix order is correct.** In `_render_saved_article_content_organization_card()` (`templates.py:4447-4488`):

```python
href = _safe_saved_article_content_organization_href(card.detail_path)  # validate + canonicalize
if href is None:
    return ""
href = _prefixed_saved_article_content_organization_href(href, href_prefix)  # prefix after
```

In `_render_saved_article_content_organization_evidence()` (`templates.py:4519-4540`):

```python
href = _safe_saved_article_content_organization_evidence_href(card.detail_path, paragraph_index)
if href is None:
    continue
href = _prefixed_saved_article_content_organization_href(href, href_prefix)  # prefix after
```

`"../"` is never passed into the validators. Traversal (`../secrets.html`), `javascript:` URIs, wrong fragment types (`#local-article-paragraph-N` where a content-section fragment is required), negative indices, and boolean indices all continue to be filtered before any prefix is applied.

**`_prefixed_saved_article_content_organization_href()` (`templates.py:4569-4572`):** Simple, correct, no allocation when `href_prefix` is empty.

---

### 3. Homepage Behavior Remaining Unchanged

**None.**

`_render_saved_article_content_organization()` is called from the homepage render path (`render_index_html`) without the `href_prefix` argument, so it defaults to `""`. `_prefixed_saved_article_content_organization_href(href, "")` returns `href` unchanged.

The canonicalization change in `_safe_saved_article_content_organization_href()` does implicitly apply to the homepage as well: a non-canonical `detail_path` like `details/./story.html#...` would now be output as the canonical `details/story.html#...` on the homepage too. This is benign and strictly correct — the view model builder produces canonical paths, so real homepage cards are unaffected. The integration test (`test_render_row_one_site_includes_saved_article_content_organization_in_article_library`, `tests/test_row_one_render.py:2984`) asserts:

```python
assert (
    'href="details/the-row-signal-1234567890.html#local-article-content-section-1"'
) in homepage_html
```

confirming homepage links remain `details/...` (no `../` prefix). ✅

---

### 4. JSON Contract and Generated-Artifact Boundaries

**None.**

No data files are written. No new JSON contracts, sidecar schemas, or `data/` subdirectory entries are created. The integration test asserts all three contracts:

```python
for contract_json in (edition_payload, manifest_payload, runtime_payload):
    assert "saved_article_content_organization" not in contract_json
    assert "content_organization" not in contract_json
    assert "saved-article-content-organization" not in contract_json
    assert "Saved Article Content Organization" not in contract_json
assert not (tmp_path / "data" / "saved-article-content-organization.json").exists()
```

The diff introduces zero writes to `data/`. ✅

---

### 5. Test Adequacy and Brittleness

**None.**

Three new tests, one helper fix.

**`test_render_row_one_site_includes_saved_article_content_organization_in_article_library` (`tests/test_row_one_render.py:2933`):** Full end-to-end via `render_row_one_site()`. Covers: presence of the section on the library page, `../details/...` prefix for both content-section and evidence-paragraph links, ordering assertion (signal-index < content-org < source-grid by string position), homepage unprefixed links, all three JSON contracts free of the new section, and no new JSON artifact. Well-scoped and not brittle.

**`test_render_saved_article_library_filters_content_organization_links_on_library_page` (`tests/test_row_one_render.py:4037`):** Direct renderer call covering five distinct failure modes: `javascript:`, traversal, wrong-fragment type, negative index, boolean index. Negative assertions for each filtered path. Verifies valid prefixed links appear as `../details/...` at the section level and evidence level (`#local-article-paragraph-1`, `#local-article-paragraph-3` from `paragraph_indices=(0, 2)`). Verifies `Bad index card` title survives (card is shown, only bad evidence links are dropped).

**`test_render_saved_article_library_canonicalizes_content_organization_links` (`tests/test_row_one_render.py:4096`):** Exercises the new `f"{safe_path}#{fragment}"` return path with a `details/./story.html#...` input. Asserts the canonical `../details/story.html#...` form in output and `details/./` absent.

**`_saved_article_content_organization_section_html` helper update (`tests/test_row_one_render.py:3847`):** The original helper searched only for `\n<section class=` as a section boundary. On the library page, the content-organization section is followed by `<div class="saved-article-library-grid">` rather than a `<section>`, so the original would have returned an unbounded tail. The fix adds `library_grid = tail.find('<div class="saved-article-library-grid">')` and takes `min(boundary_offsets)`. Correct.

**One minor gap:** No test explicitly asserts that `render_saved_article_library_html(..., saved_article_content_organization=None)` produces no `saved-article-content-organization` section on the library page. This is implicitly covered by `_render_saved_article_content_organization(None, ...)` returning `""`, which is a pre-existing code path exercised by existing homepage tests. Not blocking, but a one-line negative assertion in the filter test would close the gap.

---

### 6. Documentation Accuracy

**None.**

The Stage 332 paragraph added to `README.md` and `docs/row-one.md` (`docs/row-one.md:471`, `README.md:256`) is accurate:

- Names `articles/index.html` as the only output changed✅
- States reuse of existing sidecars and `content_sections` ✅
- Lists all excluded systems: `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, JSON artifacts, collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international, compliance review ✅
- Inserted in reverse-chronological order (before Stage 331), consistent with surrounding entries ✅

The docs sentinel test (`test_row_one_docs.py:1064`) uses `_normalized()` and flat-contains matching — consistent with Stage 327/328 precedent and correct given no Stage 333 upper-bound marker exists yet.

---

### 7. Scope Creep

**None.**

The diff is contained to four files:

| File | Change |
|---|---|
| `render.py` | 3-line import + 3-line threading |
| `templates.py` | `href_prefix` parameter on 5 helpers + 1 new prefix helper + canonicalization fix in 1 validator |
| `tests/test_row_one_render.py` | 3 new tests + 1 helper fix |
| `tests/test_row_one_docs.py` | 1 new docs sentinel test |
| `README.md` / `docs/row-one.md` | 1 boundary paragraph each |

No crawler, connector, schema, scheduler, extraction, ranking, LLM, market grouping, domestic/international classification, or compliance-review code touched. No new sidecar. No new JSON artifact. No new data route.

---

## Summary

| Severity | Count | Items |
|---|---|---|
| Critical | 0 | — |
| Important | 0 | — |
| Minor | 1 | No explicit `None`-organization negative assertion on the library page (optional) |
| None | 6 | All other areas |

The implementation matches the plan and spec faithfully. The canonicalization improvement in `_safe_saved_article_content_organization_href()` is a clean incidental fix. Validate-then-prefix order is correct throughout. Homepage behavior is unchanged. All JSON contract and generated-artifact boundaries are respected. **Proceed to commit.**
