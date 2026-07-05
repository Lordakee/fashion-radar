# opencode Stage 299 Code Review Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review the current uncommitted Stage 299 changes in `/home/ubuntu/fashion-radar`.

Base commit:

- `ab99230` (`Stage 298: add bilingual row one local article bodies`)

Plan and prior reviews:

- `docs/superpowers/plans/2026-07-05-stage-299-row-one-local-article-brief-sections-plan.md`
- `docs/reviews/claude-code-stage-299-plan-review.md`
- `docs/reviews/opencode-stage-299-plan-review.md`
- `docs/reviews/opencode-stage-299-plan-rereview.md`

Changed implementation/test files:

- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/articles.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_articles.py`
- `tests/test_row_one_render.py`

Implementation summary:

- Adds `RowOneLocalArticleBriefKey` and `RowOneLocalArticleBriefSection`.
- Adds `brief_sections: list[RowOneLocalArticleBriefSection]` to
  `RowOneLocalArticle` with a default empty list for backward compatibility.
- Builds four localized brief sections from existing `RowOneStory` fields:
  `what_happened`, `why_it_matters`, `signal_context`, and `watch_next`.
- Populates `brief_sections` for both extracted local articles and fallback
  summary local articles.
- Renders the brief above saved local article body paragraphs, using existing
  `data-lang="en"` / `data-lang="zh"` language-toggle spans.
- Cleans the summary-backed `what_happened` brief body before saving the
  sidecar, so raw RSS feed HTML does not appear as visible escaped tag text.
- Escapes brief titles and bodies in the HTML template.
- Preserves legacy rendering when `brief_sections` is empty.
- Avoids duplicating scan-layer content in the local article body: short
  extracted articles and fallback articles keep source/summary body plus
  `editorial_takeaway`; `summary`, `why_it_matters`, `signal_context`, and
  `reader_path` are exposed through `brief_sections`.
- Does not change `row-one-app/v7`, `data/edition.json`, collection, scraping,
  translation services, social connectors, deployment, app UI, or
  compliance-review product behavior.

Verification already run after the duplicate-content adjustment:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
# 72 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
# 5 files already formatted

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
- every article sidecar has exactly four `brief_sections`
- every sidecar has keys
  `what_happened,why_it_matters,signal_context,watch_next`
- duplicate non-summary brief-body paragraphs in saved local body: 0
- raw HTML markup in summary-backed `what_happened` brief bodies: 0
- detail pages with local articles missing `class="local-article-brief"`: 0

Review questions:

1. Does `brief_sections` remain backward-compatible with existing local article
   sidecars and model usage?
2. Are the four brief sections built from the correct localized `RowOneStory`
   fields?
3. Does the implementation avoid duplicating `why_it_matters`,
   `signal_context`, and `reader_path` in the local article body, while
   allowing `what_happened` to mirror fallback/source summary body text when no
   fuller source article is available?
4. Does the implementation clean raw feed HTML before saving the summary-backed
   `what_happened` body?
5. Does the template render bilingual brief sections correctly and escape all
   title/body content?
6. Is legacy local article rendering preserved when `brief_sections` is empty?
7. Are tests meaningful for builder behavior, serialization, rendering,
   backward compatibility, and escaping?
8. Are there any Critical or Important issues blocking commit/push?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly. Start the completed review body with
`# opencode Stage 299 Code Review`.
