# Stage 323 ROW ONE Local-First Reading Design

## Goal

Make ROW ONE feel like a local daily fashion-news site instead of a link directory by making saved local article reading the primary generated-site action when a story has usable saved paragraphs, and by adding direct evidence paragraph links to saved article content-organization cards.

## User Value

The user specifically wants articles downloaded locally and published into the ROW ONE webpage, with organized information rather than only links out to other websites. Earlier stages already save article sidecars, render local article readers on detail pages, and organize saved article content. Stage 323 should improve the reading path:

- From the homepage, readers should see and use a primary `Read saved article / 阅读本地正文` action for stories that have saved local text.
- From detail pages, readers should see the local saved article action before the external source action.
- From homepage saved article content-organization cards, readers should be able to jump directly to the supporting saved paragraphs, not only to a grouped content section.

## Scope

- Generated ROW ONE HTML/CSS only.
- Use existing data already available during site rendering:
  - `RowOneEdition`
  - `RowOneStory`
  - `RowOneLocalArticle`
  - existing `data/articles/<story-id>.json` sidecars
  - existing saved local paragraphs
  - existing detail routes
  - existing `#local-article`
  - existing `#local-article-reader`
  - existing `#local-article-paragraph-N`
  - existing `#local-article-content-section-N`
- Add a private optional `local_articles_by_story_id` argument to `render_index_html()` so homepage lead/story cards can decide whether a local-first action exists.
- Pass the existing `local_articles_by_story_id` map from `render_row_one_site()` into `render_index_html()`.
- Add local-first action UI for:
  - lead story CTA
  - regular story card CTA
  - detail page header/action area
- Keep ordinary heading/detail links pointing to the generated detail page.
- Keep external source links as secondary provenance.
- Add evidence paragraph chips to saved article content-organization cards from existing `card.paragraph_indices`.
- Convert saved article content-organization cards from wrapping anchors to `<article>` containers with standalone links so evidence paragraph chips do not create nested anchors.
- Escape all displayed text.
- Validate every local-first and evidence href at render time.

## Non-Goals

- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not add `local_first_read`, `local_read_path`, `saved_article_cta`, `evidence_paragraph_trail`, `paragraph_trail`, or any new app payload field.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not add source collection.
- Do not fetch article pages.
- Do not add article extraction behavior.
- Do not add scoring, matching, ranking, LLM calls, translation calls, image generation, connectors, deployment behavior, scheduling behavior, or compliance-review product features.
- Do not rename story IDs, detail routes, local article reader anchors, paragraph anchors, or content-section anchors.
- Do not add dependencies.

## Behavior

### Homepage Local-First Actions

When a story has a matching `RowOneLocalArticle` with at least one usable saved paragraph and a validated detail path:

- Lead story primary action should link to `details/<story>.html#local-article`.
- Lead story primary action label should be `Read saved article / 阅读本地正文`.
- Regular story card primary footer action should link to `details/<story>.html#local-article`.
- Regular story card primary footer action label should be `Read saved article / 阅读本地正文`.
- The card should include a compact `Saved locally / 本地已保存` cue with saved paragraph count.

When no usable local article exists:

- Existing lead/story card detail links and brief labels remain unchanged.
- No local-first badge or local-first href is rendered.

### Detail Local-First Action

When the detail page receives a usable `local_article`:

- Render a compact local-first action block near the story source area, before the external `Open Source Article / 打开原文` action.
- The local action should link to `#local-article`.
- The action label should be `Read saved article / 阅读本地正文`.
- Include a compact `Saved locally / 本地已保存` cue with saved paragraph count.
- Keep the external source action rendered after the local action as provenance.

When no usable local article exists:

- Do not render the local-first action block.
- Preserve existing detail behavior.

### Saved Article Content Organization Evidence Paragraph Links

For each saved article content-organization card:

- Keep the existing main content-section link to `details/<story>.html#local-article-content-section-N`.
- Render up to three direct evidence paragraph chips from existing `card.paragraph_indices`.
- Each evidence chip should link to `details/<story>.html#local-article-paragraph-{index + 1}`.
- Evidence chip labels should be `Evidence paragraph N / 证据段落 N`.
- Existing reference chips remain plain chips.
- Existing paragraph count may remain plain text if useful, but direct paragraph chips must be the click target for evidence.
- If the card's `detail_path` is unsafe, do not render unsafe links.
- If an index is invalid, not an integer, or negative, skip that paragraph chip.

## Link Safety

Local-first homepage links must only use validated generated detail routes plus `#local-article`.

Saved content-organization paragraph links must:

- Split the card detail path into path and fragment.
- Validate the path with `validated_row_one_detail_relative_path`.
- Require the existing content-section fragment to match `local-article-content-section-[1-9][0-9]*`.
- Require paragraph indices to be non-negative integers.
- Return only `details/<validated>.html#local-article-paragraph-[1-9][0-9]*`.

Rejected hrefs include:

- external URLs
- protocol-relative URLs
- `javascript:` URLs
- `data:` URLs
- path traversal
- percent-encoded traversal
- empty hrefs
- unknown fragments
- paragraph zero or negative paragraph fragments

## Styling

Add compact styles using the existing ROW ONE visual system:

- `.local-read-path`
- `.local-read-path-badge`
- `.local-read-action`
- `.saved-article-content-organization-card-link`
- `.saved-article-content-organization-evidence`
- `.saved-article-content-organization-evidence-link`

The styles should fit existing lead/story cards, detail pages, and saved article organization cards without changing homepage section order.

## Testing Requirements

- Render test: `render_row_one_site()` with a local article sidecar shows homepage lead/story local-first actions linking to `#local-article`.
- Omission test: no usable local article means no local-first homepage action.
- Detail test: local-first action appears before `Open Source Article / 打开原文` when a local article exists.
- Evidence paragraph test: saved article content-organization cards include safe paragraph chip links and still include the content-section main link.
- Nested-anchor test: saved article content-organization cards render as `<article>` containers, not wrapping `<a>` cards.
- Safety test: unsafe content organization paths and bad paragraph indices do not create paragraph links.
- Workflow boundary test: generated HTML includes the new generated-site markers, while `edition`, `manifest`, and `runtime` JSON do not include Stage 323 private keys.
- CSS test: new selectors exist.
- Docs test: README and `docs/row-one.md` describe Stage 323 as generated-site-only and explicitly state no contract/schema/artifact/source/fetching/scoring/LLM/connector/compliance changes.

## Risks

- Homepage CTA behavior: keep headline/detail links unchanged so readers can still open the detail page even when the CTA jumps to the local reader.
- Nested anchors: convert saved content-organization cards to `<article>` before adding evidence links.
- Link drift: validate all generated internal hrefs at render time.
- Scope creep: do not change collectors, extractors, JSON contracts, app payloads, schedules, or external connectors.

## Definition Of Done

- Stage 323 spec and plan are reviewed by Claude Code before implementation.
- Local saved article reading is the primary generated-site action when saved paragraphs exist.
- Saved content-organization cards provide direct safe jumps to evidence paragraphs.
- The feature is generated-site-only and keeps all JSON contracts stable.
- Focused tests, full tests, Ruff, lock check, and release hygiene pass.
- Claude Code code review has no unresolved Critical or Important findings.
- Changes are committed and pushed to `origin/main`.
