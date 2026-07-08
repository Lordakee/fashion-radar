# Stage 343 ROW ONE Saved Article Content Organization Group Summary Design

## Objective

Stage 343 improves `articles/index.html` by adding a generated-site-only summary
strip at the top of each Saved Article Content Organization group. The strip
summarizes the existing cards in that group before readers scan individual cards:
distinct saved articles, source count, evidence paragraph count, and capped
first-seen reference chips.

## Product Gap

ROW ONE now offers local article pages, article-level information panels,
paragraph context cues, evidence boards, reading paths, theme digest, and
reference atlas. The remaining library-level gap is that each content organization
group currently jumps from title/dek straight into cards. Readers do not get a
quick sense of how broad or reference-heavy a group is before reading card by
card.

This stage closes that gap by turning existing group cards into a compact
group-level overview. It adds information, not another link module.

## Architecture

This is a generated-site-only rendering change in
`src/fashion_radar/row_one/templates.py`. It reuses only
`RowOneSavedArticleContentOrganizationGroup.cards`, existing card detail paths,
existing card references, existing paragraph indices, and existing safe href
validation helpers. It does not change models, schemas, app-facing JSON artifacts,
source collection, extraction, ranking, scheduling, deployment, or connector
behavior.

The implementation should add one private helper near
`_render_saved_article_content_organization_group()`:

- `_render_saved_article_content_organization_group_summary(group)`

The helper returns an empty string when the rendered group has no safe cards. The
group renderer inserts the summary between the group header and the card grid.

## Rendering Behavior

The group summary strip should show:

- saved card count
- distinct saved article count, deduped by validated detail page path
- distinct source count
- evidence paragraph count, deduped by `(validated detail page path, paragraph index)`
- first-seen reference chips, deduped by normalized `(name, type, label)` and capped

The summary should use bilingual labels and existing escape helpers. Reference
chips should be visible text only, not new outbound CTAs.

## Sanitization And Caps

Only cards with valid `_safe_saved_article_content_organization_href(card.detail_path)`
should contribute to the summary, matching the card renderer. Paragraph indices
must be strict integers; bools, strings, negative values, and duplicates must not
inflate evidence counts. Reference chips must be deduped, escaped, and capped to a
small fixed number in first-seen card order to avoid visual noise.

## Out Of Scope

This stage does not add cross-article recommendation rails, article downloading,
social-platform collection, external tool adapters, scraping, browser automation,
platform APIs, account/cookie/token behavior, ranking, demand proof, analytics,
personalization, recommendation, compliance review, new JSON artifacts, new route
families, or app contract changes. It only improves the generated ROW ONE saved
article library HTML from existing local organization data.

## Acceptance Criteria

- Each non-empty Saved Article Content Organization group renders a summary strip
  before its card grid.
- The summary counts only safe cards that would render in the group.
- Evidence paragraph counts are deduped by safe detail page path and strict
  paragraph index.
- Reference chips are escaped, deduped, and capped.
- Unsafe card paths do not contribute to summary counts or visible chips.
- Documentation states the generated-site-only boundary for Stage 343.
- Workflow tests confirm no new app-facing contract keys or JSON/HTML artifacts
  are created for the feature.
