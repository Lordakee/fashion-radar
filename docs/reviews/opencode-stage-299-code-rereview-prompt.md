# opencode Stage 299 Code Rereview Prompt

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`. Do not edit files.

Review the current uncommitted Stage 299 changes in `/home/ubuntu/fashion-radar`
after the first code review found I1:

- `what_happened` brief body saved raw feed summary HTML from `story.summary`,
  which displayed as visible escaped tag text in the local article brief.

The intended fix:

- `src/fashion_radar/row_one/articles.py` now cleans the summary-backed brief
  body with the existing ROW ONE text cleanup helpers before saving sidecars.
- `tests/test_row_one_articles.py` now has a regression test asserting raw
  summary HTML is stripped from `brief_sections[0].body` without mutating the
  source story summary.
- The plan and code-review prompts were updated to reflect this cleanup.

Verification after the fix:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_articles.py::test_build_row_one_local_articles_cleans_brief_summary_html_without_mutating_story \
  -q
# 1 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q
# 72 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/models.py src/fashion_radar/row_one/articles.py src/fashion_radar/row_one/templates.py tests/test_row_one_articles.py tests/test_row_one_render.py
# 5 files already formatted

UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
# 1963 passed

UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed

UV_NO_CONFIG=1 uv lock --check
# Resolved 85 packages

UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --as-of 2026-07-05T04:00:00Z \
  --output-dir reports/row-one/site \
  --latest-only
# Wrote 18 stories
```

Generated-site proof after fix:

- `story_count`: 18
- `articles`: 18
- `details`: 18
- every article sidecar has exactly four `brief_sections`
- keys are exactly `what_happened,why_it_matters,signal_context,watch_next`
- duplicate non-summary brief-body paragraphs in saved local body: 0
- raw HTML markup in summary-backed `what_happened` brief bodies: 0
- detail pages with local articles missing `class="local-article-brief"`: 0

Review questions:

1. Is I1 fully fixed?
2. Does the cleanup preserve readable summary prose and avoid mutating the
   source `RowOneStory.summary`?
3. Does the fix preserve the existing Stage 299 goals: structured brief
   sections, bilingual rendering, escaped output, legacy empty-brief behavior,
   and no duplicated `why_it_matters` / `signal_context` / `reader_path` body
   content? `what_happened` may mirror fallback/source summary body text when no
   fuller source article is available.
4. Are there any remaining Critical or Important issues blocking commit/push?

Return findings first, ordered by severity. If there are no Critical or
Important findings, say that explicitly. Start the completed review body with
`# opencode Stage 299 Code Rereview`.
