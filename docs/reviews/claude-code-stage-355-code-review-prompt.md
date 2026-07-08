# Stage 355 Code Review Prompt

Review the Stage 355 implementation:

- `src/fashion_radar/row_one/saved_article_local_section_binder.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_local_section_binder.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`

Goal: add a generated-site-only `Saved Article Local Section Binder` to
`articles/<story-id>.html` pages. The binder should compactly index each saved
local article's existing `content_sections`, item labels, references, cited
paragraph anchors, and unfiled saved paragraphs without adding app-facing
payloads or generated JSON artifacts.

Please evaluate:

1. Builder correctness, including section-row caps, item/reference/paragraph
   caps, valid paragraph index filtering, cited paragraph tracking, unfiled
   paragraph detection, and excerpt truncation.
2. Render safety, including escaping, same-page fragment validation, and
   placement after the Stage 354 local reading companion and before
   `#local-article`.
3. Generated-site-only scope, including absence from homepage, library pages,
   detail pages, app contract payloads, manifest/runtime payloads, and sidecar
   artifacts.
4. Whether the compact binder remains distinct enough from Local Article
   Information.
5. Any concrete corrections needed before commit.
