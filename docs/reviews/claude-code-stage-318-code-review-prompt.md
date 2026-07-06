# Stage 318 Code Review Prompt

Please review the Stage 318 implementation in `/home/ubuntu/fashion-radar`.

## Goal

Stage 318 adds a generated-site-only `Continue Reading / 继续阅读` rail to
ROW ONE detail pages. The rail appears after `Evidence Trail`, selects up to
three deterministic internal next reads from the same daily edition, and links
only to sibling generated detail-page filenames.

## Files to Review

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-06-stage-318-row-one-detail-continue-reading-rail-design.md`
- `docs/superpowers/plans/2026-07-06-stage-318-row-one-detail-continue-reading-rail-plan.md`

## Required Behavior

- Exclude the current story from the rail.
- Prefer stories from the same `section_key` in edition order.
- Fill from other sections in edition order.
- Skip unsafe or invalid `detail_path` values.
- Skip duplicate target detail-page filenames.
- Cap at three cards.
- Omit the rail when no related generated detail page exists.
- Use story summary excerpts, falling back to editorial takeaway.
- Escape rendered text.
- Render sibling links such as `same-section-1234567890.html`, not
  `details/same-section-1234567890.html`.

## Boundaries

This stage must not change:

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
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_prioritizes_same_section_and_fallbacks \
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_omits_without_related_stories \
  tests/test_row_one_render.py::test_render_row_one_detail_continue_reading_uses_editorial_takeaway_fallback \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_saved_paragraph_previews_boundary \
  tests/test_row_one_docs.py::test_row_one_docs_describe_detail_continue_reading_boundary -q
```

Result: `6 passed`.

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format src/fashion_radar/row_one/templates.py tests/test_row_one_render.py
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
git diff --check
```

Result: formatting applied to two files, then lint/format/diff whitespace checks
passed.

## Please Check

- Any Critical or Important correctness issues in the deterministic selection?
- Any route-safety or escaping gap?
- Any accidental contract/schema/runtime/manifest mutation?
- Any missing test coverage for the stated behavior?
- Any docs boundary mismatch?

Return findings ordered by severity:

- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional cleanup.

If there are no Critical or Important issues, state that clearly.
