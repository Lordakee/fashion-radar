# Stage 373 Final Code Re-Review Findings

opencode re-reviewed the final Stage 373 implementation after the post-review Stage 366 test expectation fixes.

## Critical

None.

## Important

None. The final diff is correct across builder behavior, renderer interaction, updated Stage 366 filing-cue tests, escape and href filtering, and generated-site-only boundaries.

opencode verified these targeted tests:

```bash
UV_NO_CONFIG=1 uv run --frozen pytest tests/test_row_one_local_article_body_section_markers.py "tests/test_row_one_render.py::test_render_local_article_page_includes_body_section_markers_inside_body" "tests/test_row_one_render.py::test_render_local_article_body_section_markers_escape_text_and_filter_links" "tests/test_row_one_render.py::test_render_local_article_page_includes_body_filing_cues" "tests/test_row_one_render.py::test_render_local_article_page_body_filing_cues_filter_invalid_links" "tests/test_row_one_render.py::test_render_row_one_site_writes_body_filing_cues_only_on_local_article_pages" -q
# 11 passed
```

## Notes

- Builder story-id guard, rendered-index validation, duplicate paragraph marker suppression, sort-then-cap behavior, and fallback title are spec-compliant.
- Renderer markers are only threaded through the local article page path; the detail-page caller remains marker-free.
- Stage 366 cue suppression is correct in both aligned Chinese and single-language paragraph branches.
- The updated Stage 366 tests correctly document that marker paragraphs suppress inline cues while non-marker filed/unfiled paragraphs keep cues.
- Hostile marker hrefs are rejected and user text is escaped.
- The remaining TDD fallback dataclass in `tests/test_row_one_render.py` is harmless staged-test scaffolding.
