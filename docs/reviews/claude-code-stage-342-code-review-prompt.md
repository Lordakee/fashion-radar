# Claude Code Stage 342 Code Review Prompt

You are reviewing completed Stage 342 code in `/home/ubuntu/fashion-radar`.
Use maximum reasoning. Operate read-only. Do not edit files.

## Objective

Review the Stage 342 implementation: generated-site-only saved paragraph context cues for ROW ONE local article pages.

## Scope Implemented

Changed files should include:

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`
- Stage 342 design/plan/review artifacts under `docs/superpowers/` and `docs/reviews/`

## Requirements

The implementation must:

1. Preserve existing `id="local-article-paragraph-N"` paragraph anchors.
2. Preserve existing `#local-article-content-section-N` section anchors and use 1-based section positions.
3. Reuse existing `RowOneLocalArticle.content_sections[*].items[*].paragraph_indices` only.
4. Strictly reject bool/string/negative/out-of-range/blank-paragraph indices.
5. Escape cue labels and excerpts.
6. Deduplicate and cap paragraph context cues.
7. Preserve bilingual paragraph rendering and existing plain fallback when `paragraphs_zh` is not aligned.
8. Keep the feature generated-site-only: no models, schemas, app-facing JSON contracts, new JSON/HTML artifact families, source collection, scraping, ranking, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

## Verification Already Run

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "paragraph_context or local_article_page or local_article_information"` -> `16 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q` -> `76 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q` -> `2328 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .` -> passed
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv --no-config lock --check` -> passed
- `git diff --check` -> passed

## Review Questions

1. Are there any correctness regressions in local article rendering, anchors, bilingual handling, or information panel rendering?
2. Are the new tests sufficient and aligned with the implementation?
3. Is the implementation contract-safe and generated-site-only?
4. Are there any critical or important issues that must be fixed before commit/push?

Return a concise severity-labeled review. If there are no critical or important issues, state that Stage 342 is approved for commit and push.
