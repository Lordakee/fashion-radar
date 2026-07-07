# Stage 324 ROW ONE Paragraph Evidence Index Design

## Goal

Make ROW ONE detail pages better at organizing locally saved article content by adding a compact local paragraph evidence index that maps saved source paragraphs back to the existing organized content sections, item labels, and references.

## User Value

The user wants ROW ONE to publish locally saved article text and organize the information, not just show outbound source links. Stage 323 made saved local reading the primary action and added homepage evidence paragraph chips. After that change, a reader can land directly inside the saved local article, but the detail page still lacks a single scan-first view of which saved paragraphs support the organized content.

Stage 324 fills that gap on the detail page:

- Readers can see a compact local index of saved paragraphs that are used by ROW ONE's content organization.
- Each row links to the existing saved paragraph anchor and lists the section/item/ref context that uses that paragraph.
- The feature stays generated-site only and uses only data already present in `RowOneLocalArticle`.

## Scope

- Generated ROW ONE detail HTML/CSS only.
- Use existing data already available during detail rendering:
  - `RowOneLocalArticle`
  - `RowOneLocalArticle.content_sections`
  - `RowOneLocalArticleContentSection.items`
  - `RowOneLocalArticleContentItem.paragraph_indices`
  - `RowOneLocalArticleContentItem.references`
  - saved local article paragraphs and optional aligned Chinese paragraphs
  - existing `#local-article`
  - existing `#local-article-reader`
  - existing `#local-article-paragraph-N`
  - existing `#local-article-content-section-N`
- Add a private render helper chain in `templates.py`.
- Render a detail-page-only section with id/class `local-article-paragraph-evidence`.
- Add an optional local article map link to `#local-article-paragraph-evidence` only when the evidence index exists.
- Keep all links as local same-page fragment navigation.
- Escape all displayed paragraph excerpts, labels, titles, item bodies, and references.
- Keep output compact with explicit caps.

## Non-Goals

- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not add `local_article_paragraph_evidence`, `paragraph_evidence_index`, `local_evidence_index`, `evidence_paragraph_index`, `evidence_paragraph_trail`, or any related app payload field.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not change story IDs, detail routes, local article reader anchors, paragraph anchors, or content-section anchors.
- Do not add source collection.
- Do not fetch article pages.
- Do not add article extraction behavior.
- Do not add scoring, matching, ranking, LLM calls, translation calls, image generation, connectors, deployment behavior, scheduling behavior, or compliance-review product features.
- Do not add external links to the new index.
- Do not add dependencies.

## Behavior

### Detail Paragraph Evidence Index

When a detail page receives a usable `RowOneLocalArticle` with rendered saved paragraphs and at least one content item that has valid `paragraph_indices`:

- Render a compact `Saved Paragraph Evidence / 本地段落线索` block inside `#local-article`.
- Place it after the local article map and before the digest/reader/brief/content-section blocks.
- Add a local article map link to `#local-article-paragraph-evidence`.
- Render at most eight paragraph evidence rows.
- Each row links to the existing `#local-article-paragraph-N` anchor.
- Each row shows a short escaped saved paragraph excerpt.
- Each row shows up to four supporting content items.
- Each supporting item shows:
  - the existing content-section title
  - the existing item label
  - an optional short item body excerpt
  - up to four deduped references from the item
  - a link back to the existing `#local-article-content-section-N` anchor

When no valid paragraph evidence mapping exists:

- Do not render the evidence index.
- Do not add the map link.
- Preserve existing local article map, digest, reader, brief, content sections, and saved paragraph body behavior.

### Valid Paragraph Mapping

The evidence index is built from `content_sections[*].items[*].paragraph_indices`.

For every paragraph index:

- Accept only integer values that are not `bool`.
- Accept only indices present in `_local_article_rendered_paragraph_indices(article)`.
- Deduplicate repeated paragraph indices per content item.
- Deduplicate repeated support items per paragraph.
- Preserve first-seen section/item order.
- Never derive HTML ids, class names, hrefs, or fragments from labels, references, paragraph text, source names, or article titles.

## Link Safety

Stage 324 only generates same-page links from validated numeric positions:

- Paragraph hrefs use `#{_local_article_paragraph_anchor(index)}`.
- Content-section hrefs use `#{_local_article_content_section_anchor(position)}`.
- The helper must skip invalid, blank, duplicated, negative, out-of-range, non-integer, and boolean paragraph indices.
- All display text must use `_esc()`.

Rejected evidence rows include:

- content items with no valid paragraph indices
- paragraph indices pointing to blank saved paragraphs
- paragraph indices outside the saved paragraph list
- `True` or `False` values even though Python treats them as integers
- repeated mappings that would create duplicate support chips for the same paragraph

## Styling

Add compact detail-page styles using the existing ROW ONE visual system:

- `.local-article-paragraph-evidence`
- `.local-article-paragraph-evidence-header`
- `.local-article-paragraph-evidence-grid`
- `.local-article-paragraph-evidence-row`
- `.local-article-paragraph-evidence-link`
- `.local-article-paragraph-evidence-excerpt`
- `.local-article-paragraph-evidence-support`
- `.local-article-paragraph-evidence-supports`
- `.local-article-paragraph-evidence-ref`

The styling should read as a functional newsroom index, not another large card module. It should remain compact on mobile and should not alter homepage section order.

## Testing Requirements

- Render test: `render_detail_html()` with a local article renders `local-article-paragraph-evidence`, labels, paragraph links, content-section links, item labels, item body excerpts, and reference chips.
- Omission test: local articles without valid `paragraph_indices` do not render the evidence index or map link.
- Safety test: invalid, blank, duplicated, out-of-range, negative, and non-integer indices are filtered in rendering.
- Helper test: the strict paragraph-index validator rejects boolean values before they can be treated as integers.
- Escaping test: paragraph excerpts, section titles, item labels, item bodies, and references are escaped.
- Cap test: rows, support items, and reference chips are capped.
- CSS test: new selectors exist.
- Workflow boundary test: generated detail HTML includes the new generated-site marker, while `edition`, `manifest`, and `runtime` JSON do not include Stage 324 private keys.
- Docs test: README and `docs/row-one.md` describe Stage 324 as generated-site-only and explicitly state no contract/schema/artifact/source/fetching/scoring/LLM/connector/compliance changes.

## Risks

- Duplicate organization: the detail page already has a local map, digest, reader, brief, content cards, paragraph previews, and paragraph links. Keep this feature compact and navigational.
- Claim strength: use wording like `Saved Paragraph Evidence / 本地段落线索` so the section reads as saved-source organization, not trend proof or compliance validation.
- Anchor safety: generate links only from validated numeric positions and existing helper functions.
- Contract drift: do not add JSON fields, schemas, model fields, or new artifacts.

## Definition Of Done

- Stage 324 spec and plan are reviewed by Claude Code before implementation.
- Detail pages with usable saved paragraph mappings render a compact local paragraph evidence index.
- The index maps saved paragraphs to existing organized sections/items/references using only existing local article data.
- The feature is generated-site only and keeps all JSON contracts stable.
- Focused tests, full tests, Ruff, lock check, and release hygiene pass.
- Claude Code code review has no unresolved Critical or Important findings.
- Changes are committed and pushed to `origin/main`.
