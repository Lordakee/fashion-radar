# Claude Code Stage 312 Code Rereview Prompt

You are the primary local Claude Code reviewer for Fashion Radar Stage 312.
Use maximum reasoning. Review the current uncommitted working tree in
`/home/ubuntu/fashion-radar`, focusing on fixes made after your Stage 312 code
review.

## Original Findings To Recheck

1. Important: `build_row_one_saved_article_coverage()` included items whose
   `story.detail_path` would be rejected by the template href sanitizer, causing
   `coverage.items` and rendered cards to diverge.
2. Minor: saved article coverage card headline used English-only text instead
   of the bilingual `data-lang` span pattern.
3. Minor: `_render_saved_article_coverage()` had an unreachable
   `coverage.article_count == 0` guard.

## Fixes Made

- Added builder-level safe detail-path filtering in
  `src/fashion_radar/row_one/saved_article_coverage.py`.
- Added
  `tests/test_row_one_saved_article_coverage.py::test_saved_article_coverage_excludes_invalid_detail_paths`.
- Updated saved coverage card title rendering to use bilingual `data-lang`
  spans.
- Removed the unreachable `article_count == 0` guard.

## Required Boundaries Still Apply

- No changes to `row-one-app/v7`, `data/edition.json`,
  `row-one-manifest/v1`, `row-one-runtime/v1`, schemas, story IDs, detail
  routes, or paragraph anchors.
- No new JSON artifact.
- No source collection, scraping, scoring, LLM calls, scheduling,
  platform/social/community connectors, or compliance-review product features.

## Latest Verification

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_coverage.py tests/test_row_one_render.py::test_render_row_one_site_includes_saved_article_coverage tests/test_row_one_render.py::test_render_row_one_site_escapes_saved_article_coverage tests/test_row_one_render.py::test_render_row_one_site_rejects_invalid_saved_article_coverage_links tests/test_row_one_docs.py::test_row_one_docs_describe_saved_article_coverage_boundary -q`
  - `8 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`
  - passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`
  - passed

## Rereview Instructions

Return findings first, ordered by severity. Confirm whether the original
Important finding is fixed. If no Critical or Important findings remain, say so
clearly and mention any residual risk/test gaps.
