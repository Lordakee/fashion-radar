Final review Stage 333 after addressing a read-only test coverage audit.

Read:

- `src/fashion_radar/row_one/saved_article_library.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_library.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/reviews/claude-code-stage-333-code-rereview.md`

Stage 333 goal:

Add a generated-site-only saved article library text-source map inside
`articles/index.html`. It reuses existing saved local article `body_source`
values to show included-library counts and per-card text source chips for
extracted article text, ROW ONE summary fallback, and skipped saved bodies.
It must not expose fallback reasons, and must not change app/runtime/manifest
contracts, schemas, JSON artifacts, collection/fetching/matching/extraction,
scoring/ranking/LLM/connectors/scheduling/deployment/classification, or
compliance-review behavior.

Post-rereview coverage feedback and fixes:

1. The skipped chip test did not validate skipped aggregate metrics.
   Fix: `test_render_saved_article_library_renders_skipped_text_source_chip()`
   now replaces the fixture aggregate counts with skipped=1, extracted=0,
   summary_fallback=0, and asserts both English/Chinese skipped metrics while
   rejecting fallback metric/label leakage.

2. Builder body-source counts were not pinned against existing cap semantics.
   Fix: the entry cap and source-group cap tests now assert article_count and
   all three body-source counters remain full included-library counts.

3. Generated contract no-leakage sentinel did not include Stage 333 vocabulary.
   Fix: the `edition.json`/`manifest.json`/`runtime.json` contract assertions
   now reject text-source map, text_source, body_source, aggregate count fields,
   and visible text-source labels.

Additional Minor coverage fixed:

- Added an end-to-end render test proving summary fallback reason text is not
  exposed in `articles/index.html`, and that the summary fallback chip is not
  a link.
- Added a Stage 333 docs slice guard rejecting contradictory scope phrases.

Verification run after these fixes:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_saved_article_library.py::test_saved_article_library_caps_entries_references_and_paragraph_links \
  tests/test_row_one_saved_article_library.py::test_saved_article_library_caps_source_groups \
  tests/test_row_one_render.py::test_render_row_one_site_writes_saved_article_library_page \
  tests/test_row_one_render.py::test_render_row_one_site_saved_article_library_hides_summary_fallback_reason \
  tests/test_row_one_render.py::test_render_saved_article_library_renders_skipped_text_source_chip \
  tests/test_row_one_docs.py::test_row_one_docs_describe_stage_333_saved_article_library_text_source_boundary \
  -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_library.py tests/test_row_one_render.py -q -k "saved_article_library or body_source"
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_row_one_docs.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check tests/test_row_one_saved_article_library.py tests/test_row_one_render.py tests/test_row_one_docs.py
```

Please review whether the coverage feedback is fully resolved and whether any
new Critical, Important, or Minor findings remain.
