# Stage 342 ROW ONE Saved Paragraph Context Cues Design

## Objective

Stage 342 improves ROW ONE generated local article reading pages by showing compact
context cues next to already-saved local article paragraphs. When a reader lands on
`articles/<story-id>.html#local-article-paragraph-N`, the page should show which
organized content section or item is using that paragraph, without sending the
reader to the original publisher page.

## Product Gap

ROW ONE now stores local article text, filters obvious extraction boilerplate, and
renders first-class local article pages. The remaining content-organization gap is
paragraph-level orientation: saved paragraphs can be cited by organized sections,
but the paragraph itself does not explain why it matters. This stage closes that
report-side gap by turning existing content-section paragraph references into
inline reading cues.

## Architecture

This is a generated-site-only rendering change in
`src/fashion_radar/row_one/templates.py`. It reuses
`RowOneLocalArticle.content_sections`, existing `paragraph_indices`, existing
saved local paragraphs, existing `#local-article-paragraph-N` anchors, and
existing `#local-article-content-section-N` anchors. It does not change models,
schemas, sidecar JSON, app-facing JSON artifacts, source collection,
extraction, ranking, scheduling, deployment, or connector behavior.

## Rendering Behavior

`_render_local_article_paragraphs(article)` will compute a mapping from each
rendered saved paragraph index to a small list of context labels. Each label
links to the page-local organized content section anchor that references the
paragraph. The information panel can also show saved-paragraph cue excerpts in
the already-existing local article information area, but the core reader cue
stays attached to the saved paragraph target.

The visible cue should be compact and bilingual:

- English prefix: `Used in`
- Chinese prefix: `用于`
- label text: section title plus item label when an item label exists, for example
  `Entities - The Row`
- href: `#local-article-content-section-N`

The cue should render immediately before the paragraph text while preserving the
current paragraph element and its `id="local-article-paragraph-N"` anchor. The
paragraph can contain the cue and the current English/Chinese text spans, so
existing anchor behavior and bilingual switching remain intact.

## Sanitization And Caps

Only strict integer paragraph indices are used. Boolean values, strings, negative
values, out-of-range values, duplicate indices in the same item, and indices for
blank paragraphs are ignored. Context labels are deduped per paragraph and capped
to a small fixed number to avoid clutter. Label text is escaped through the
existing HTML escaping helper before rendering. Paragraph snippets shown outside
the article body are normalized through existing paragraph-excerpt conventions.

## Style

Add a small `.local-article-paragraph-context` style family to the existing ROW ONE
CSS output. The cue should read as metadata, not as a new article body paragraph.
It should remain visually secondary to the article text and not create nested card
layouts.

## Out Of Scope

This stage does not add article downloading, social-platform collection, external
tool adapters, scraping, browser automation, platform APIs, account/cookie/token
behavior, ranking, demand proof, analytics, personalization, recommendation,
compliance review, new JSON artifacts, or app contract changes. It only improves
how the already-generated ROW ONE website explains saved local article paragraphs.

## Acceptance Criteria

- Local article pages still render existing saved paragraphs and existing
  paragraph anchors.
- Paragraphs referenced by content-section items show capped, escaped, deduped
  context cues with page-local content-section links.
- Invalid paragraph indices do not create cues or broken anchors.
- Bilingual paragraph rendering keeps the existing English and Chinese text spans.
- Documentation states the generated-site-only boundary for Stage 342.
- Workflow tests confirm no new app-facing contract keys or JSON/HTML artifacts are
  created for the feature.
