# Stage 347 ROW ONE Saved Article Source Brief Design

## Objective

Stage 347 adds a generated-site-only Saved Article Source Brief inside each
source group on `articles/index.html`. The brief explains what a saved source
contributes to the current local article set before readers scan the source's
article cards.

Stage 347 also tightens saved article coverage inclusion parity: homepage saved
article coverage should reject a local article whose `article.story_id` does not
match the current edition story, matching the saved article library and
first-class local article page gates.

## Product Gap

ROW ONE now provides daily saved article orientation, source cards, source-level
counts, content organization, body guides, evidence boards, theme digest,
reference atlas, coverage matrix, and first-class local article pages. The
remaining gap is source-level editorial context: a reader can see "Vogue
Business" or "WWD" as a group, but the page does not yet state what that source
adds today before listing cards.

The source brief closes that gap by turning existing saved article entries and
existing content-organization snippets into a compact source-level explanation.
It does not create a new page, route, JSON artifact, model, schema, or ranking
system.

## Architecture

This is a generated-site-only rendering change centered on
`src/fashion_radar/row_one/templates.py`:

- `_render_saved_article_library_source(...)` should render the source brief
  after the existing source header and before the source card grid.
- The brief should use `RowOneSavedArticleLibrarySourceGroup` counts, existing
  `RowOneSavedArticleLibraryEntry` values, and existing
  `RowOneSavedArticleContentOrganizationCard` body-guide data already grouped by
  detail path.
- The source brief should be omitted when there are no safe entries or no
  useful text.

The coverage parity guard is a small builder fix in
`src/fashion_radar/row_one/saved_article_coverage.py`: if a local article is
looked up by `story.id` but its `article.story_id` differs, it should be skipped.

## Rendering Behavior

For each non-empty saved article source group, render a brief with:

- a compact bilingual heading: "Source Brief" / "来源简报";
- source-level factual metrics derived from the source group, such as article
  count, saved paragraph count, and organized section count;
- up to two concise contribution bullets derived from safe entries in the group,
  preferring existing body-guide snippets when available and falling back to
  card titles / section labels when needed;
- safe internal links only to existing generated local article routes or detail
  anchors already allowed by the saved article library.

The brief should explain source contribution, not source quality. It must not
rank sources, score trust, verify coverage, add external article URLs as primary
navigation, or duplicate full article text.

## Sanitization And Caps

All source brief text must be escaped. The brief should cap bullets to two per
source group and cap excerpts with the existing local digest excerpt helper. It
must reuse existing safe href validation helpers instead of trusting raw paths.

Unsafe detail paths, unsafe article-page hrefs, traversal, `javascript:` hrefs,
and invalid local article anchors must not render. If a source group has only
unsafe or empty entries, the source brief shell should be omitted.

## Out Of Scope

Stage 347 does not add article downloading, social-platform collection, external
tool adapters, scraping, browser automation, platform APIs, account/cookie
credential behavior, new extraction, LLM summaries, ranking, recommendation,
analytics, personalization, scheduling, deployment, app contract changes, schema
changes, new route families, or compliance-review product behavior.

It also does not create `data/saved-article-source-brief.json`,
`data/source-brief.json`, or any new JSON/HTML artifact. The source brief is
rendered only inside the generated `articles/index.html` saved article library.

## Acceptance Criteria

- `articles/index.html` renders one `saved-article-source-brief` inside each
  saved article source group that has safe, useful local content.
- The brief appears after the source header and before the source card grid.
- Source brief bullets are escaped, capped, deduped, and linked only through safe
  local generated routes / anchors.
- Empty or unsafe source groups do not render an empty source brief shell.
- `build_row_one_saved_article_coverage()` rejects local articles whose
  `article.story_id` mismatches the current story id.
- No app-facing contract, schema, JSON artifact, route family, fetching,
  extraction, ranking, LLM, scheduling, deployment, or compliance-review product
  behavior changes.
- Documentation and workflow guards state the generated-site-only boundary for
  Stage 347.
