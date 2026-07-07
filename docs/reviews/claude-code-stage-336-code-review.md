## Stage 336Code Review — ROW ONE Saved Article Theme Digest

All tests passed. All files inspected. Findings are below.

---

### Checklist 1 — Implementation matches the spec and plan

**Result: NONE**

The builder, render wiring, and template all match the spec and plan precisely:

- `saved_article_theme_digest.py`: correct four-group mapping (`takeaways→read_first`, `entities→people_brands`, `product_signals→products`, `brand_signals→source_structure`), caps, and dedupe key.
- `render.py:134-137`: builder called after both dependencies are ready; passed through `_write_saved_article_library_page()` at line 160.
- `templates.py:341-344`: display order in `render_saved_article_library_html()` is hero → `{theme_digest}` → `{signal_index}` → `{reading_paths}` → `{content_organization}` → library grid. Matches spec §UI Behavior exactly.
- No changes to `ROW_ONE_APP_CONTRACT_VERSION`, `ROW_ONE_MANIFEST_CONTRACT_VERSION`, `ROW_ONE_RUNTIME_CONTRACT_VERSION`, JSON payloads, or schemas.

---

### Checklist 2 — Unsafe/generated detail paths filtered before rendering

**Result: NONE**

Defense is layered correctly at two independent checkpoints.

**Builder (`saved_article_theme_digest.py`):**
- `_safe_content_section_href()` (line 205) validates: must be a string, must contain `#`, fragment must start with `local-article-content-section-`, number must be decimal and≥ 1, path must pass `validated_row_one_detail_relative_path()`.
- `_detail_path_key()` (line 220) strips the fragment and re-validates the path through the same route helper before adding it to the allowed set or checking against it.
- Intersection check at line 191: card detail path must match a path already present in the saved article library.

**Renderer (`templates.py`):**
- `_render_saved_article_theme_digest_item()` (line 4609) calls `_safe_saved_article_content_organization_href(item.detail_path)` again and returns early if it is `None`. The `../` prefix is applied only after this second validation (line 4612).
- Evidence links are derived via `_render_saved_article_theme_digest_evidence()` (line 4653), which delegates to the existing `_render_saved_article_content_organization_evidence()`. Paragraph anchors are derived only from `paragraph_indices` (zero-based integers rendered as `index + 1`), never from raw URL input.

Test `test_saved_article_theme_digest_rejects_unsafe_or_unmatched_detail_paths()` covers traversal (`../secret.html`), library-unmatched, and wrong-fragment cases, verifying only the safe card survives.

---

### Checklist 3 — Theme digest stays generated-site-only, does not leak into JSON

**Result: NONE**

- `render_row_one_site()` in `render.py` passes the digest only to `_write_saved_article_library_page()`. It is never serialized into any `data/` file.
- `test_render_row_one_site_includes_saved_article_theme_digest_in_article_library()` (render test line 3224-3235) checks all three contracts and the file system:
  - `data/edition.json`, `data/manifest.json`, `data/runtime.json` do not contain `"saved_article_theme_digest"`, `"theme_digest"`, `"saved-article-theme-digest"`, `"Saved Article Theme Digest"`, `"保存文章主题简报"`, or any local lead text.
  - `data/saved-article-theme-digest.json` does not exist.
- Contract versions remain `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`.

---

### Checklist 4 — Capping, dedupe, escaping, and truncation are deterministic

**Result: NONE**

| Property | Mechanism | Test |
|---|---|---|
| Theme cap | `MAX_SAVED_ARTICLE_THEME_DIGEST_THEMES = 4`, checked at line 145 | `test_saved_article_theme_digest_maps_source_groups_and_counts_source_union` (4 groups → 4 themes) |
| Item cap | `MAX_SAVED_ARTICLE_THEME_DIGEST_ITEMS = 3`, checked at line 130 | Same test;4 cards per group → 3 items |
| Dedupe | Key `(theme_key, canonical_path, normalized_lead.en, normalized_lead.zh)` at lines 117-124 | `test_saved_article_theme_digest_caps_and_dedupes_theme_items` (8 identical cards → 1 item) |
| Source union | `global_source_keys` is the union across all themes (not sum); case-folded | `test_…maps_source_groups_and_counts_source_union` asserts `digest.source_count == 2` |
| Escaping | All text fields through `_esc()` (wraps `html.escape`) in renderer | `test_render_saved_article_library_html_escapes_and_truncates_theme_digest` asserts `<script>` absent, `&lt;` entities present |
| Lead truncation | `_local_article_digest_excerpt()` at `LOCAL_ARTICLE_DIGEST_EXCERPT_CHARS = 160` | Same test: `section_html.count("Long lead")< 80` |

---

### Checklist 5 — Test coverage

**Result: Minor gap (see below)**

**Covered:**

| Area | Test |
|---|---|
| Builder derives from existing inputs | `test_saved_article_theme_digest_builds_theme_cards_from_existing_saved_inputs` |
| Builder omits empty input | `test_saved_article_theme_digest_omits_empty_inputs` |
| Unsafe paths rejected | `test_saved_article_theme_digest_rejects_unsafe_or_unmatched_detail_paths` |
| Caps and dedupe | `test_saved_article_theme_digest_caps_and_dedupes_theme_items` |
| Source union counting, group-key ordering | `test_saved_article_theme_digest_maps_source_groups_and_counts_source_union` |
| Full site render, section ordering, safe anchor links | `test_render_row_one_site_includes_saved_article_theme_digest_in_article_library` |
| Digest absent from homepage | Same test, `assert'class="saved-article-theme-digest"' not in homepage_html` |
| Outbound URLs excluded | Same test, `assert "https://example.com/the-row" not in section_html` |
| Contract non-exposure (3 JSON files + no digest.json) | Same test, lines 3224-3235 |
| Escape and lead truncation | `test_render_saved_article_library_html_escapes_and_truncates_theme_digest` |
| Docs boundary | `test_row_one_docs_describe_stage_336_saved_article_theme_digest_boundary` |

**Gap — Minor:**

The plan (Task 3 Step 2) specifies extending the existing `row_one_css()` tests with explicit CSS selector assertions for all nine Stage 336 selectors (`.saved-article-theme-digest`, `.saved-article-theme-digest-header`, etc.). No such dedicated test function exists — `test_row_one_css_includes_saved_article_theme_digest_styles` is absent, unlike the analogous `test_row_one_css_includes_saved_article_reading_path_styles` at line 6735 and `test_row_one_css_includes_saved_signal_index_styles` at line 6713.

The CSS selectors themselves are present (confirmed at `templates.py:1446-1569`) and are exercised implicitly via the HTML render tests, so this is not a functional gap. But it is inconsistent with the test pattern every prior stage established and makes CSS regressions harder to catch at selector granularity.

---

### Checklist 6 — Critical or Important maintainability/regression issues

**Result: None (Critical), None (Important)**

Two Minor observations:

**Minor A — Duplicate container class within a single item (`templates.py:4626-4649`)**

`_render_saved_article_theme_digest_item()` unconditionally emits a `<div class="saved-article-theme-digest-actions">` for the main "Open theme section" link, then conditionally emits a second `<div class="saved-article-theme-digest-actions">` for paragraph evidence. Both siblings in the same `<li>` share the same class, so any CSS rule targeting `.saved-article-theme-digest-actions` will apply to both. This is not a bug — the layout appears intentional — but it does mean the CSS cannot independently style the two action groups without a structural selector like`:first-of-type` or an added modifier class. Worth noting if these ever need to diverge visually.

**Minor B — Direct attribute mutation on Pydantic model in test fixture (`test_row_one_render.py:334`)**

`_theme_digest_local_article()` does:
```python
article = _signal_briefing_local_article()
article.content_sections = [...]
```

All other fixture mutations in the same file use `model_copy(deep=True, update={...})` (e.g. line 393). If `RowOneLocalArticle` ever gains a frozen config or a validator triggered on `content_sections` assignment, this fixture will fail at test time without warning. The tests currently pass — this is a style and fragility concern, not a bug.

---

### Summary

| Checklist item | Classification |
|---|---|
| 1. Matches spec and plan | **None** |
| 2. Unsafe paths filtered | **None** |
| 3. No JSON leakage | **None** |
| 4. Deterministic capping/dedupe/escaping/truncation | **None** |
| 5. Test coverage | **Minor** (missing dedicated CSS selector assertions) |
| 6. Maintainability/regression issues | **Minor** × 2 (duplicate action div class; direct model mutation in test fixture) |

No Critical or Important issues. The three Minor findings are non-blocking. The implementation is clean, follows established patterns, and all6 builder tests + 14 render/CSS tests pass.
