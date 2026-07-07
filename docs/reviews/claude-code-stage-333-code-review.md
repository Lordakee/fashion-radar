Here is the Stage 333 code review.

---

## Stage 333 Code Review — ROW ONE Saved Article Library Text-Source Map

### 1. `body_source` Propagation into `RowOneSavedArticleLibraryEntry`

**Finding: None.**

`saved_article_library.py:12` correctly imports `RowOneLocalArticleBodySource` from models. `saved_article_library.py:41` adds `body_source: RowOneLocalArticleBodySource` as a required field on the frozen entry dataclass, placed between `organized_section_count` and `digest_path` — valid Python dataclass ordering because the two defaulted fields (`paragraph_links`, `references`) remain last. `saved_article_library.py:101` assigns `body_source=article.body_source` during entry construction. The propagation is exact, with no copying, coercion, or defaulting at the builder level.

---

### 2. Count Semantics

**Finding: None.**

`saved_article_library.py:135–139` computes the three counts as generator sums over `entries` — the flat list built after all four filters (safe route, safe story ID, mismatch check, nonblank-paragraph check) but before source-group capping at line 124. This is consistent with the existing `article_count=len(entries)` and `source_count=len(grouped_entries)` semantics. The test at `test_row_one_saved_article_library.py:239–275` explicitly verifies all four cases:

- `article_count == 3` (empty-skipped excluded)
- `extracted_article_count == 1`, `summary_fallback_article_count == 1`, `skipped_article_count == 1`
- The entry list over `library.groups[0].entries` carries the correct per-entry `body_source` strings in edition order

A subtle correctness point: if a single source has more than 8 entries, the group's displayed entries are capped at 8 (`line 124`), but the aggregate counts still reflect all entries. This is consistent with how `article_count` already works and matches the design specification.

---

### 3. Rendering of Nonzero Metrics and Per-Card Chips

**Finding: None.**

`templates.py:3921–3949` adds three conditional metric blocks, each gated on nonzero counts. Each calls `_render_saved_article_library_metric()` with the `_count_label()` helper, using the same singular/plural form (`"extracted text"/"extracted text"`, `"summary fallback"/"summary fallback"`, `"skipped"/"skipped"`) — intentional since these are descriptors, not countable nouns.

`templates.py:4029–4034` is `_saved_article_library_body_source_label()`: a simple three-way string switch with `"Extracted article text"` as the catch-all return. `templates.py:4037–4048` is `_render_saved_article_library_body_source_chip()`: a static `<li class="saved-article-library-text-source">` with a bilingual label span and a value span. `_esc()` is applied to the label, which is defensive and correct even though the label output is controlled. The chip is inserted at `templates.py:4021` inside the existing `<ul class="saved-article-library-card-counts">` list.

The `_count_label()` and `_render_saved_article_library_metric()` helpers are both pre-existing; no new template utility was needed. The helper placement (after `_render_saved_article_library_card()` and before `_render_saved_article_library_refs()`) is coherent.

---

### 4. No Fallback Reason Display, No Outbound Source-Link Additions

**Finding: None.**

No `reason` field appears anywhere in the new chip or metric rendering paths. The chip value is a static `<span>`, not an `<a>`. `test_row_one_render.py:4104` explicitly asserts `'href="ROW ONE summary fallback"' not in html`. No outbound article URLs are added; the existing `digest_path`, `reader_path`, `evidence_path`, and `paragraph_links` are unchanged, and the new chip adds no navigation surface.

---

### 5. JSON Contract and Generated-Artifact Boundaries

**Finding: None.**

`test_row_one_render.py:2808–2818` verifies against all three JSON contracts (`edition.json`, `manifest.json`, `runtime.json`) that none of `saved_article_library`, `daily_saved_article_library`, `article_library`, `saved-article-library`, or `Daily Saved Article Library` appear in the contract payloads, and that `data/saved-article-library.json` is not written. No new JSON file paths were introduced in any modified file. The new fields (`body_source`, `extracted_article_count`, `summary_fallback_article_count`, `skipped_article_count`) exist only on in-memory dataclass objects that are rendered to HTML; they never touch the JSON serialization path.

---

### 6. Test Adequacy and Brittleness

**Finding: Minor (one residual gap).**

Coverage provided by Stage 333:

| Assertion | Test |
|---|---|
| Builder propagates `body_source` per entry | `test_saved_article_library_tracks_body_source_counts_for_included_articles` |
| Aggregate extracted/fallback/skipped counts | Same |
| Zero-paragraph skipped excluded | Same (`article_count == 3`) |
| Extracted chip and metric in `articles/index.html` | `test_render_row_one_site_writes_saved_article_library_page` lines 2778–2782 |
| Extracted metric in `index.html` homepage widget | Same, line 2800 |
| Summary-fallback metric and chip | `test_render_saved_article_library_filters_content_organization_links_on_library_page` lines 4101–4103 |
| Chip is not a link | Same, line 4104 |
| JSON contracts unaffected | `test_render_row_one_site_writes_saved_article_library_page` lines 2808–2818 |
| Docs sentinel | `test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary` |

The two gaps flagged in the plan reviews were both partially closed:
- **Gap A (extracted chip):** Closed — `test_render_row_one_site_writes_saved_article_library_page` now asserts `"Extracted article text" in html` (line 2782).
- **Gap B (homepage metric):** Closed — same test asserts `"1 extracted text" in home_html` (line 2800).

**Remaining Minor gap:** The `"skipped"` chip label (`"Skipped"`) is not covered by any render-to-HTML test. If `_saved_article_library_body_source_label("skipped")` were misdirected (e.g., fell through to `"Extracted article text"` instead), no test would catch it. The builder test checks that `entry.body_source == "skipped"` propagates correctly, but does not drive HTML rendering. This is low risk — the label function is three lines with no logic that could silently misdirect — but it is a real gap.

The docs sentinel at `test_row_one_docs.py:1083–1099` uses `_normalized()` (whitespace-collapsed, casefold) with exact substring matching, consistent with every prior stage sentinel. Not brittle.

---

### 7. Documentation Accuracy

**Finding: None.**

`docs/row-one.md:471` and `README.md:256` both contain the exact Stage 333 boundary sentence, correctly placed before Stage 332. The sentence:

- States "generated-site only" ✓
- Names `body_source` and the three values ✓
- States "does not expose fallback reasons" ✓
- Lists all in-scope no-change contracts: `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, JSON artifacts, source collection, fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, market grouping, domestic/international classification, compliance-review✓

The docs sentinel test at `test_row_one_docs.py:1083–1099` matches both files against the normalized version of this exact sentence.

---

### 8. Scope Creep

**Finding: None.**

The diff touches exactly the seven files listed in the plan: `saved_article_library.py`, `templates.py`, `test_row_one_saved_article_library.py`, `test_row_one_render.py`, `test_row_one_docs.py`, `README.md`, `docs/row-one.md`. No changes to `models.py`, any schema file, `render.py`'s render entry point, `data/edition.json`, any collection/matching/scoring/ranking/LLM/connector/scheduler module, or any sidecar generation path. No new JSON file is created. No new generated page is created. The implementation is strictly a view-model extension and HTML renderer extension over already-existing data.

---

### Summary

| Category | Findings |
|---|---|
| Critical | None |
| Important | None |
| Minor | 1 — `"skipped"` chip label has no render-to-HTML test coverage |
| None | All other areas clean |

The implementation is correct and safe to commit. The single Minor gap (no HTML render test for the `"skipped"` chip label) is non-blocking; the label helper is trivially correct and the builder test confirms `body_source="skipped"` propagates, so the only unverified assertion is the static string `"Skipped"` appearing in rendered output. If you want to close it, adding `assert "Skipped" in html` to either render test (using a fixture entry with `body_source="skipped"`) would do it cleanly.
