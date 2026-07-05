# Claude Code Stage 300 Code Review Prompt

Use maximum reasoning effort. Do not edit files.

Review the current uncommitted Stage 300 changes in `/home/ubuntu/fashion-radar`.

Base commit:

- `9107e3a` (`Stage 299: add row one local article brief sections`)

Plan and prior reviews:

- `docs/superpowers/plans/2026-07-05-stage-300-row-one-local-article-content-sections-plan.md`
- `docs/reviews/claude-code-stage-300-plan-review.md`
- `docs/reviews/opencode-stage-300-plan-review.md`

Changed implementation/test files:

- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/articles.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_articles.py`
- `tests/test_row_one_render.py`

Implementation summary:

- Adds additive local article `content_sections` sidecar data.
- Adds `RowOneLocalArticleContentItem` and
  `RowOneLocalArticleContentSection`, with localized label/body fields,
  optional `RowOneReference` references, and `paragraph_indices` pointing back
  into saved local body paragraphs.
- Keeps `brief_sections`, `paragraphs`, and `paragraphs_zh` semantics
  unchanged.
- Builds deterministic sections from existing data only:
  `takeaways`, `entities`, `product_signals`, `brand_signals`.
- Omits empty optional `entities` / `product_signals` sections.
- Keeps `brand_signals` always present because it always contains `Source`.
- Renders content sections inside the existing `#local-article` block after
  the Stage 299 brief and before saved body paragraphs.
- Keeps the single existing `#local-article` nav entry; no per-section anchors.
- Keeps current no-body gate: no saved body paragraphs means no local article
  section and no sidecar.
- Does not change `row-one-app/v7`, source extraction, social connectors,
  translation services, deployment, or compliance-review product behavior.

Verification already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_row_one_local_article_content_sections_default_empty \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_content_sections_work_on_fallback \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_omits_empty_optional_content_sections \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_content_sections_model_dump_json \
  -q
# 5 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py::test_render_row_one_detail_includes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_keeps_plain_local_article_without_zh_paragraphs \
  tests/test_row_one_render.py::test_render_row_one_detail_uses_plain_local_article_when_zh_paragraphs_mismatch \
  tests/test_row_one_render.py::test_render_row_one_detail_escapes_local_article_content \
  tests/test_row_one_render.py::test_render_row_one_detail_omits_local_article_content_sections_without_body_paragraphs \
  -q
# 5 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
# 78 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
# 5 files already formatted

UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
# 1969 passed

UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed

UV_NO_CONFIG=1 uv lock --check
# Resolved 85 packages
```

Generated-site verification:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-05T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
# Wrote ROW ONE site: reports/row-one/site/index.html
# Wrote 18 stories
```

Sidecar/detail proof after rebuild:

- `story_count`: 18
- `articles`: 18
- `details`: 18
- every sidecar has `content_sections`
- every sidecar has `takeaways`
- every sidecar has `brand_signals`
- every `takeaways` section has at least one item with `paragraph_indices`
- every `brand_signals` section has a `Source` item
- empty optional sections: 0
- detail pages with local articles missing
  `class="local-article-content-sections"`: 0
- `data/edition.json` contains no local article sidecar-only
  `paragraph_indices` and no `local-article-content-sections` class

Review questions:

1. Is the data model backward-compatible and correctly additive?
2. Are content sections built from existing local paragraphs and story metadata
   without changing paragraph extraction/alignment behavior?
3. Are optional sections omitted correctly, and is always-present
   `brand_signals` justified by the source item?
4. Does rendering stay inside the existing local article block and preserve
   nav/page/app contracts?
5. Are title/body/item/reference values escaped safely?
6. Are tests meaningful for model defaults, builder behavior, sidecar JSON,
   rendering order, escaping, mismatched zh behavior, and no-body gate?
7. Are there any Critical or Important issues blocking commit/push?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly.
