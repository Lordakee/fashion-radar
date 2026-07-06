# Stage 316 Code Review Prompt

Please review the uncommitted Stage 316 changes in `/home/ubuntu/fashion-radar`.

## Goal

Stage 316 adds a generated-site homepage section for ROW ONE that organizes
existing saved local article `content_sections` into scan-first groups. This
should make saved local article content visible on the homepage without changing
the app payload or generated JSON contracts.

## Scope to Review

- New builder: `src/fashion_radar/row_one/saved_article_content_organization.py`
- Rendering integration:
  - `src/fashion_radar/row_one/render.py`
  - `src/fashion_radar/row_one/templates.py`
- Tests:
  - `tests/test_row_one_saved_article_content_organization.py`
  - `tests/test_workflows.py`
  - `tests/test_row_one_docs.py`
  - `tests/test_row_one_render.py`
- Docs:
  - `README.md`
  - `docs/row-one.md`
- Stage docs/review artifacts under `docs/superpowers/` and `docs/reviews/`

## Required Behavior

- The builder must be pure and deterministic.
- It must only use current-edition stories.
- It must exclude mismatched `article.story_id`, invalid story IDs, unsafe detail
  paths, blank local article bodies, empty content sections, and unusable content
  sections.
- Group order must be:
  - `takeaways`
  - `entities`
  - `product_signals`
  - `brand_signals`
- Each group is capped at four cards.
- Content section fragment links must follow the existing rendered detail-page
  anchor behavior: `#local-article-content-section-N`, where `N` is one-based.
- Card paragraph indices remain zero-based internally and are aggregated from all
  usable items in the selected content section, filtered for nonblank paragraphs,
  and deduped in first-seen order.
- References are deduped by normalized `(name, type, label)` and capped.
- Homepage rendering should appear after saved article briefs and before normal
  story sections.
- Links must be sanitized to safe ROW ONE detail paths plus
  `local-article-content-section-[1-9][0-9]*` fragments.

## Boundary Requirements

Stage 316 must not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `data/manifest.json`
- `row-one-runtime/v1`
- `data/runtime.json`
- schemas
- source collection
- article fetching/extraction
- scoring
- connectors/social/community tools
- LLM calls
- compliance-review product behavior

It must not write a new JSON artifact.

## Verification Already Run

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_content_organization.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite tests/test_row_one_docs.py::test_row_one_docs_describe_local_article_content_organization_boundary -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_content_organization.py tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite tests/test_row_one_docs.py::test_row_one_docs_describe_article_readiness_boundary tests/test_row_one_docs.py::test_row_one_docs_describe_local_article_content_organization_boundary tests/test_row_one_render.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
```

Focused verification after formatting passed:

- `ruff check`: clean
- `ruff format --check`: clean
- focused pytest slice: `102 passed`

## Review Output

Please return findings ordered by severity:

- Critical: must fix before commit
- Important: should fix before commit
- Minor: optional cleanup

If there are no Critical or Important issues, state that clearly.
