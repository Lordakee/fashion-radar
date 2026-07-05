# opencode Stage 299 Code Rereview

Reviewer: opencode (`zhipuai-coding-plan/glm-5.2`, variant `max`)

Scope: Uncommitted Stage 299 changes in `/home/ubuntu/fashion-radar` after the
first code review found I1: raw feed summary HTML was saved into the
summary-backed `what_happened` brief body.

Mode: Read-only. No files were edited.

## Findings

### Critical

None.

### Important

None. I1 is fully resolved.

### Minor

The minor findings from the first review are unchanged and remain non-blocking:

- M1: brief body shares `LocalizedText` references with the story for the
  non-summary fields.
- M2: `aria-label="ROW ONE brief"` is English-only.
- M3: empty story fields would render an empty brief card.

## I1 Fix Assessment

`src/fashion_radar/row_one/articles.py` introduces
`_local_article_brief_text()` and applies it to the summary-backed
`what_happened` body before saving the article sidecar.

The helper composes the existing ROW ONE text cleanup pipeline:

- `protect_literal_angle_tokens` preserves literal angle-token text that is not
  a known HTML tag before HTML parsing.
- `clean_row_one_text` unescapes entities, strips HTML tags, removes
  `Original source summary:` / `来源摘要：` prefixes, and collapses blank lines.
- `clean_row_one_sentences` removes existing boilerplate and deduplicates long
  repeated sentences.
- `normalize_row_one_paragraph` and `restore_literal_angle_tokens` return
  readable one-paragraph prose.

The non-summary sections (`why_it_matters`, `signal_context`, `watch_next`) keep
their direct assignment from the existing story fields. `_local_article_context_text`
still only feeds `editorial_takeaway` into body enrichment, so
`why_it_matters`, `signal_context`, and `reader_path` are not re-injected into
the saved article body.

## Verification

opencode independently re-ran and inspected:

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py::test_build_row_one_local_articles_cleans_brief_summary_html_without_mutating_story -q`
  -> `1 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py -q`
  -> `72 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`
  -> `1963 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check ...`
  -> clean
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check ...`
  -> clean
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
  -> `Release hygiene checks passed`
- `UV_NO_CONFIG=1 uv lock --check`
  -> `Resolved 85 packages`

Generated-site proof after rebuild:

- story count: 18
- article sidecars: 18
- detail pages: 18
- every article sidecar has exactly four `brief_sections`
- brief keys are exactly
  `what_happened`, `why_it_matters`, `signal_context`, `watch_next`
- raw `<` / `>` markup in summary-backed `what_happened` bodies: 0
- duplicate non-summary brief bodies leaked into saved `paragraphs`: 0
- detail pages with a local article section missing
  `class="local-article-brief"`: 0

The regression test would have caught the old bug: simulating the pre-fix raw
assignment leaves `<` and `>` in the body and keeps the generated summary prefix,
both of which the new assertions reject.

## Review Questions

1. I1 is fully fixed.
2. The cleanup preserves readable summary prose and does not mutate
   `RowOneStory.summary`.
3. The fix preserves the Stage 299 goals: four structured brief sections,
   bilingual rendering, escaped output, legacy empty-brief behavior, and no
   duplicated `why_it_matters` / `signal_context` / `reader_path` body content.
4. There are no remaining Critical or Important issues blocking commit/push.
