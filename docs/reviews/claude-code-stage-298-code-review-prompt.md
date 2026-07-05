# Claude Code Stage 298 Code Review Prompt

Use maximum reasoning effort. Do not edit files.

Review the current uncommitted Stage 298 changes in `/home/ubuntu/fashion-radar`.

Base commit:

- `f2c5343` (`Stage 297: enrich short row one local articles`)

Plan and prior reviews:

- `docs/superpowers/plans/2026-07-05-stage-298-row-one-bilingual-local-article-body-plan.md`
- `docs/reviews/claude-code-stage-298-plan-review.md`
- `docs/reviews/opencode-stage-298-plan-review.md`

Changed implementation/test files:

- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/articles.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_articles.py`
- `tests/test_row_one_render.py`

Implementation summary:

- Adds `paragraphs_zh: list[str] = Field(default_factory=list)` to
  `RowOneLocalArticle`.
- Replaces Stage 297 `_story_local_article_paragraphs(...)` with
  `_story_local_article_paragraph_sets(...)` returning aligned English/Chinese
  paragraph lists.
- Extracted source paragraphs duplicate into `paragraphs_zh` when no translation
  exists; ROW ONE fallback/context paragraphs use existing Chinese
  `RowOneStory` fields.
- Renders local article paragraphs with `data-lang="en"` and `data-lang="zh"`
  spans only when `len(paragraphs_zh) == len(paragraphs)`.
- Keeps Stage 297 plain paragraph rendering for missing or mismatched
  `paragraphs_zh`, preserving legacy behavior.
- Does not change `row-one-app/v7`, `edition.json`, scraping, source matching,
  platform APIs, translation services, deployment, app UI, or compliance-review
  product behavior.

Verification already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
# 71 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
# 5 files already formatted

rg -n "def _story_local_article_paragraphs" src/fashion_radar/row_one/articles.py
# no matches, exit code 1

UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
# 1962 passed

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
- every article sidecar has `paragraphs`
- every article sidecar has `paragraphs_zh`
- `len(paragraphs_zh) == len(paragraphs)` for all 18 sidecars
- every generated detail page with `id="local-article"` includes
  `data-lang="zh"` spans

Read-only subagent audit:

- No Critical or Important findings.
- Confirmed compatibility, escaping, app-contract non-impact, and old helper
  removal.

Review questions:

1. Does `paragraphs_zh` remain backward-compatible with existing local article
   sidecars and model usage?
2. Is paragraph alignment correct for extracted source text, fallback summaries,
   short context enrichment, and substantial non-enriched articles?
3. Does the template preserve legacy plain rendering when Chinese paragraphs are
   missing or mismatched?
4. Are English and Chinese local article paragraphs escaped safely?
5. Is `row-one-app/v7`/`edition.json` contract preserved?
6. Are there any Critical or Important issues blocking commit/push?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly.
