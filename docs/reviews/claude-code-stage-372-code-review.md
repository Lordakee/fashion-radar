## Stage 372 Code Review Findings

### Prior Issues — Confirmed Fixed

- **Nullable `RowOneLocalArticle.title`:** `_article_title()` handles `None` cleanly, falling back to story headline and then story id. `test_build_daily_local_reading_itinerary_falls_back_when_article_title_missing` covers the path.
- **Source context under skim-cap pressure:** `_add_source_context_card()` keeps a `Source context` card represented by displacing the last non-source card when the skim cap is full. The caps test asserts `Source context` remains present.
- **`selected_count` from safe rendered cards:** `_render_daily_local_reading_itinerary()` recomputes selected reads from href-safe rendered cards instead of trusting builder-provided counts. The render test passes `selected_count=99` and asserts `1 selected read` renders while `99 selected reads` does not.
- **`Paragraph 1` evidence fallback:** `_evidence_label()` follows the specified chain: reference name, item label, section title, article title, then `Paragraph 1`. The dedicated fallback test covers this.
- **CSS grid aligned with plan:** The itinerary grid uses `minmax(0, 1.2fr) minmax(0, 1fr)` and collapses to one column in the mobile media block.

### Critical

None.

### Important

None.

### Follow-up Fix After Review

The final Claude Code review noted a maintainability minor: dead `selected_story_ids` and `source_names` tracking sets in the builder after counts were changed to derive from rendered card lists. Those dead sets and related parameters were removed. Focused Stage 372 tests and lint passed after the cleanup.

### Verification

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py -q -k "daily_local_reading_itinerary or stage_372 or reading_itinerary"`: passed after final cleanup with `14 passed, 490 deselected`.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/daily_local_reading_itinerary.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py`: passed after final cleanup.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/daily_local_reading_itinerary.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_daily_local_reading_itinerary.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_workflows.py`: passed after final cleanup.
