# Stage 331 ROW ONE Local Article Provenance Design

## Goal

Make ROW ONE saved local article content explain how the saved body was produced:
page text extraction, summary fallback, or skipped/failed extraction. This
improves the daily website's information organization without turning the site
back into a link list.

## Current Gap

`build_row_one_local_articles()` already writes `data/articles/<story-id>.json`
sidecars, and detail pages render saved local paragraphs before the editorial
story content. However, `_build_story_local_article()` currently converts these
very different outcomes into indistinguishable sidecars:

- extractor succeeds and returns article text
- extractor raises an exception
- extractor returns `skipped=True` with a reason such as `robots_disallowed`
- extractor returns empty or unusable text
- article text cannot produce usable paragraphs and summary fallback is used

The fallback sidecars currently have `skipped=False` and `reason=None`, so
metrics, article readiness, and the rendered detail page cannot tell whether a
saved body is extracted source text or ROW ONE summary fallback.

## Proposed Surface

Add a generated-sidecar-only field on `RowOneLocalArticle`:

```python
body_source: Literal["extracted", "summary_fallback", "skipped"] = "extracted"
```

Meanings:

- `extracted`: paragraphs are derived from successfully extracted article page
  text.
- `summary_fallback`: article page extraction was unavailable, skipped, failed,
  empty, or unusable, and paragraphs were generated from the ROW ONE story
  summary/editorial context instead.
- `skipped`: reserved for valid sidecars with no publishable body. Stage 331
  does not need to render skipped sidecars on detail pages, but the model and
  metrics should handle it so future collection diagnostics can use the same
  vocabulary.

Keep existing `skipped` and `reason` fields:

- extracted sidecar: `body_source="extracted"`, `skipped=False`, `reason=None`
- summary fallback because extractor raised: `body_source="summary_fallback"`,
  `skipped=False`, `reason="extraction_failed"`
- summary fallback because extractor returned skipped: `body_source="summary_fallback"`,
  `skipped=False`, `reason=<extractor reason>`
- summary fallback because result text was empty: `body_source="summary_fallback"`,
  `skipped=False`, `reason="no_extractable_text"`
- summary fallback because prepared paragraphs were unusable:
  `body_source="summary_fallback"`, `skipped=False`,
  `reason="no_publishable_paragraphs"`

Existing sidecars without `body_source` remain valid and load as
`body_source="extracted"` by default.

## UI Behavior

The detail page local article provenance chips should add a bilingual text-source
chip:

- extracted: `Text source / 正文来源: Extracted article text`
- summary fallback: `Text source / 正文来源: ROW ONE summary fallback`
- skipped: `Text source / 正文来源: Skipped`

If `reason` is present, add a compact reason chip:

- `Fallback reason / 兜底原因: <reason>`

This keeps the professional site honest about what it is showing while still
displaying useful local text. It does not add compliance review functionality.

## Metrics And Readiness

Extend `RowOneLocalArticleSiteMetrics` with:

- `extracted_article_count`
- `summary_fallback_article_count`
- `skipped_article_count`

`build_row_one_local_article_metrics()` should count all valid sidecars and
classify them by `body_source`.

`row_one_local_article_site_metrics_payload()` should include the new counts.
`row-one article-readiness` should print them in text mode and include them in
JSON mode under the existing `local_articles` object. The existing keys stay
unchanged.

## Contract Boundaries

Do not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `row-one-runtime/v1`
- detail routes
- paragraph anchors
- manifest/runtime schemas
- source collection scheduling
- scoring
- LLM calls
- compliance-review product behavior

Adding fields to `data/articles/<story-id>.json` is acceptable because those
sidecars are already optional generated-site artifacts parsed by the local
`RowOneLocalArticle` model.

## Tests

Add focused tests that prove:

- extracted article text writes `body_source="extracted"` with no reason
- extractor skipped/failed/empty/unusable output writes
  `body_source="summary_fallback"` with the expected reason
- older sidecar payloads without `body_source` still load
- metrics payload includes extracted/fallback/skipped counts
- `row-one article-readiness --json` includes those counts
- detail page provenance renders the text-source chip and fallback reason
- docs mention local article body provenance and do not claim every saved local
  article is extracted source text

## Out Of Scope

- No new crawler or social connector work.
- No article extraction dependency changes.
- No new database schema.
- No generated image work.
- No UI redesign.
- No compliance review functionality.
