# Stage 317 Code Review Prompt

Please review the uncommitted Stage 317 changes in `/home/ubuntu/fashion-radar`.

## Goal

Stage 317 adds generated-site detail-page saved paragraph previews inside
organized local article content items. The intent is to make the
`#local-article-content-section-N` landing point more useful after Stage 316
homepage cards send readers into detail pages.

## Scope to Review

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 317 plan/review artifacts under `docs/superpowers/` and `docs/reviews/`

## Required Behavior

- Render compact saved paragraph previews inside local article content items.
- Use only existing `RowOneLocalArticle.paragraphs`,
  `RowOneLocalArticle.paragraphs_zh`, and `content_sections`.
- Cap previews at two valid paragraph indices per item.
- Preserve first-seen order while skipping duplicate, negative, out-of-range, and
  blank paragraph indices.
- Link previews to the existing one-based `#local-article-paragraph-N` anchors.
- Keep internal paragraph indices zero-based.
- Render bilingual preview text only when `paragraphs_zh` aligns with
  `paragraphs`.
- Escape all visible text.

## Boundary Requirements

Stage 317 must not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `data/manifest.json`
- `row-one-runtime/v1`
- `data/runtime.json`
- schemas
- detail routes
- paragraph anchors
- source collection
- article fetching/extraction
- scoring
- connectors/social/community tools
- LLM calls
- compliance-review product behavior

It must not write a new JSON artifact.

## Verification Already Run

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_content_items_show_saved_paragraph_previews \
  tests/test_row_one_render.py::test_render_row_one_detail_content_previews_filter_invalid_indices_and_escape -q

UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_content_items_show_saved_paragraph_previews \
  tests/test_row_one_render.py::test_render_row_one_detail_content_previews_filter_invalid_indices_and_escape \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_local_article_content_organization_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_saved_paragraph_previews_boundary -q

UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_local_article_content_organization_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_saved_paragraph_previews_boundary -q

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
git diff --check
```

Latest focused verification after formatting:

- focused pytest slice: `101 passed`
- Ruff check: clean
- Ruff format check: clean
- diff whitespace check: clean

## Review Output

Please return findings ordered by severity:

- Critical: must fix before commit
- Important: should fix before commit
- Minor: optional cleanup

If there are no Critical or Important issues, state that clearly.
