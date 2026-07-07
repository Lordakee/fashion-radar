## Stage 337 Review — Saved Article Reference Atlas

**Independent verification:** `ruff` clean on all touched files; targeted suite (252) and full suite (**2280 passed**) both green.

### Critical
None.

### Important
None. Boundaries are intact and well-tested:
- No contract changes — `edition.json` / `manifest.json` / `runtime.json` assert no `reference_atlas` / `saved-article-reference-atlas` / `Saved Article Reference Atlas` / `保存文章引用图谱` / local reference text leaks (`tests/test_row_one_render.py:3325`).
- No `data/saved-article-reference-atlas.json`; atlas is HTML-only, never serialized to any JSON writer.
- No outbound article URLs; supports point only at `details/<id>.html#local-article-content-section-N`, evidence at `#local-article-paragraph-N`.
- Link safety is **double-validated**: builder's `_safe_content_section_href` + library-stem intersection (`saved_article_reference_atlas.py:320`/`295`), then re-validated in template via `_safe_saved_article_content_organization_href` (`templates.py:5659`). `javascript:`, traversal, wrong-fragment, and non-library stems all rejected (covered by two dedicated tests).
- No new collection/fetch/extract/score/LLM/connector behavior — builder purely consumes existing `RowOneSavedArticleLibrary` + `RowOneSavedArticleContentOrganization`.
- Render order (theme digest → reference atlas → signal index → reading paths → content org → grid) matches spec and is asserted.

### Nice-to-have
1. **First-non-empty type/label wording vs. behavior** (`saved_article_reference_atlas.py:211`): the accumulator pins `reference_type`/`label` from the *first* occurrence and never back-fills if that first value is empty, whereas the spec says "preserve … first non-empty type/label." Real-world impact is negligible (a reference needs non-empty type-or-label to be included at all, and the chip falls back `label → type`), but no test exercises the "first occurrence empty, later non-empty" merge. Worth either a clarifying test or a one-line back-fill.
2. **Support dedup key omits `source_name`** (`:194`): dedup is `(detail_path, lead.en, lead.zh)`. Harmless in practice because `detail_path` encodes the story-id and each story has exactly one source, so two sources can't collide on the same path. Only worth noting if multi-source-per-article ever becomes possible.
3. **4-bucket cap is structurally unreachable** (`:267`): only four bucket keys exist, so `MAX_SAVED_ARTICLE_REFERENCE_ATLAS_BUCKETS` can never bind. Belt-and-suspenders; no action needed.
4. **Evidence link class reuse** (`templates.py:4990`): atlas evidence reconstructs a `RowOneSavedArticleContentOrganizationCard` to reuse the content-org evidence renderer, so inner links carry `saved-article-content-organization-evidence-link` inside an atlas-evidence wrapper. Intentional style reuse, not a defect.

Overall this is a clean, well-scoped stage that mirrors the established theme-digest / content-organization patterns.
