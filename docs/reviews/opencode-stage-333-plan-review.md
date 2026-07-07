# opencode Stage 333 Plan Review

**Verdict:** None — proceed to implementation.

No Critical or Important issues remain. Claude Code's original Important
finding about transient dataclass fixture failures was closed by the plan
rereview.

## Findings

### Feasibility

The plan matches the current codebase: `RowOneLocalArticleBodySource` exists,
`RowOneLocalArticle.body_source` defaults to `extracted`, and the saved article
library builder/template path can carry body-source data without changing
sidecars or contracts.

### Count Semantics

Counts are scoped to included saved article library entries, not all sidecars.
This matches the existing `article_count` semantics, because the builder counts
entries after current-edition, safe-route, safe-id, and nonblank-paragraph
filters.

### Minor Revisions Applied

The original render-test plan set the main library-page local article to
`summary_fallback`, which conflicted with Claude Code's Minor suggestion to add
end-to-end coverage for the extracted text chip. Task 2 Step 2 now keeps the
main render test's local article at the default `body_source="extracted"` and
adds assertions for `Extracted article text` plus the homepage `1 extracted
text` metric.

The summary-fallback chip and metric assertions now belong to the fixture-based
`render_saved_article_library_html()` test, whose fixture entry is updated to
`body_source="summary_fallback"`.

### Boundary

The plan remains generated-site-only. It does not add fallback reason display,
new JSON artifacts, schema changes, app/runtime/manifest changes, collection,
fetching, matching, extraction, scoring, ranking, LLM, connector, scheduling,
market grouping, domestic/international classification, or compliance-review
behavior.
