# Stage 328 ROW ONE Saved Signal Evidence Excerpts Design

## Goal

Add display-only evidence excerpts to the existing ROW ONE Saved Signal Index so
`articles/index.html` organizes saved fashion signals with short local text
snippets, not only internal links.

## Product Gap Closed

Stage 327 grouped saved local article references by signal, but each supporting
row still required opening another anchor before the reader could see the saved
article text behind the signal. Stage 328 closes the next report-layer gap in
the collect -> match -> report pipeline: the current saved local text should be
scan-readable directly inside the generated article library.

This supports the user's requirement that ROW ONE should整理信息 rather than
only providing links.

## Scope

- Generated ROW ONE HTML/CSS only.
- Extend the existing Saved Signal Index inside `articles/index.html`.
- Add one optional excerpt field to each render-only saved-signal support row.
- Build excerpts only from already saved `RowOneLocalArticle` data available
  during `render_row_one_site()`.
- Prefer a matching `RowOneLocalArticleContentItem.body`.
- Fall back to the first valid referenced saved paragraph.
- Preserve existing bilingual switching with `LocalizedText`.
- Add tests and documentation for generated-site-only behavior.

## Non-Goals

- Do not create a new generated page.
- Do not create `saved-signal-index.html`.
- Do not create `saved-signal-excerpt.html`.
- Do not create `data/saved-signal-index.json`.
- Do not create `data/saved-signal-excerpts.json`.
- Do not add `saved_signal_excerpt`, `signal_excerpt`, or related keys to
  `row-one-app/v7`, `row-one-manifest/v1`, or `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not change story IDs, detail routes, paragraph anchors, section anchors,
  or paragraph evidence anchors.
- Do not add source collection, fetching, extraction, matching, scoring,
  ranking, demand proof, coverage verification, LLM calls, translation calls,
  image generation, connectors, scheduling, deployment, market grouping, or
  compliance-review product behavior.
- Do not infer domestic/international grouping.
- Do not add dependencies.

## Data Model

Extend the render-only dataclass:

```python
@dataclass(frozen=True)
class RowOneSavedSignalIndexSupport:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    content_section_title: LocalizedText
    section_path: str
    paragraph_links: tuple[RowOneSavedSignalIndexParagraphLink, ...] = ()
    excerpt: LocalizedText | None = None
```

Append `excerpt` after `paragraph_links` to preserve compatibility with any
positional construction.

## Excerpt Selection

For each supporting row, compute one optional excerpt from the same winning
content-section items that already support the signal:

1. Use the first matching item body with nonblank English or Chinese text.
2. If no item body is usable, use the first valid referenced saved paragraph.
3. If neither source is usable, omit the excerpt.

When item body is used:

- Normalize whitespace.
- Cap each language to a fixed character limit.
- If English is blank and Chinese exists, use the Chinese text for both fields.
- If Chinese is blank and English exists, use the English text for both fields.

When paragraph fallback is used:

- Use only indices accepted by `_strict_valid_saved_signal_paragraph_indices()`.
- English comes from `article.paragraphs[index]`.
- Chinese comes from `article.paragraphs_zh[index]` when present and nonblank.
- If aligned Chinese text is missing, fall back to the English paragraph.
- Normalize and cap text.

The excerpt must be display-only. Hrefs, ids, classes, filenames, fragments, and
sort keys must never derive from excerpt text or other display strings.

## Rendering

Render the excerpt inside each saved signal support row, between the existing
support metadata and the existing action/paragraph links:

```html
<p class="saved-signal-index-support-excerpt">
  <span data-lang="en">...</span>
  <span data-lang="zh">...</span>
</p>
```

Omit the paragraph when `support.excerpt` is `None`.

Escape all excerpt text with the existing template escaping helper. Keep the
existing generated page, route placement, and metrics unchanged.

## Styling

Add compact editorial CSS for `.saved-signal-index-support-excerpt` using the
current ROW ONE visual language and existing CSS variables such as `--ink`,
`--muted`, and `--line`. The style should be readable in dense signal cards,
wrap long words safely, and avoid changing layout contracts outside the Saved
Signal Index.

## Tests

Add TDD coverage for:

- Builder uses a matching item body as the excerpt.
- Builder falls back to a valid saved paragraph when item body is absent.
- Builder ignores invalid, duplicate, bool, string, and out-of-range paragraph
  indices for excerpt fallback.
- Builder uses aligned `paragraphs_zh` when available and falls back to English
  when not.
- Builder caps long excerpts.
- Rendered `articles/index.html` displays escaped excerpts.
- Excerpts render after support metadata and before action/paragraph links.
- Hostile excerpt text is escaped and never used in hrefs, ids, classes, or
  fragments.
- Existing app/runtime/manifest JSON contracts do not include excerpt fields or
  rendered excerpt copy.
- Docs describe Stage 328 as generated-site-only and contract-safe.
