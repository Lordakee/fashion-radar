## Stage 372 Code Review Findings

### Prior Issues — Confirmed Fixed

- **C1 (`RowOneLocalArticle.title` None crash):** Fixed. `_article_title` guards with `article_title or ""`, and `test_build_daily_local_reading_itinerary_falls_back_when_article_title_missing` covers the nullable-title path. The previously failing full-suite regression `test_render_row_one_site_escapes_daily_local_intelligence` passes.
- **Render `selected_count` from safe cards:** Fixed. `_render_daily_local_reading_itinerary` computes `selected_count` from href-safe rendered cards, and `test_render_daily_local_reading_itinerary_escapes_and_filters_links` asserts `"1 selected read"` renders while stale `"99 selected reads"` does not.
- **Source context under skim-cap pressure:** Fixed. `_add_source_context_card` preserves a `Source context` card by replacing a non-source skim card when the skim cap is full, and the caps test asserts `"Source context"` remains present.
- **Evidence label final fallback:** Fixed. `_evidence_label` receives the raw nullable article title and falls back to `Paragraph 1` when reference, item label, section title, and article title are absent. `test_build_daily_local_reading_itinerary_evidence_label_falls_back_to_paragraph` covers the behavior.
- **Plan CSS and dead-code cleanup:** Fixed. The CSS grid now uses `minmax(0, 1.2fr) minmax(0, 1fr)`, and the redundant builder tracking sets / `article_emitted` guard were removed after review.

### Critical

None.

### Important

None.

### Verification

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest`: passed during rereview with `2623 passed`.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "daily_local_reading_itinerary or stage_372 or reading_itinerary"`: passed after final cleanup with `14 passed, 490 deselected`.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/daily_local_reading_itinerary.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py`: passed after final cleanup.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/daily_local_reading_itinerary.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py`: passed after final cleanup.
