# Stage 357 Daily Local Key Signals Digest Design

## Goal

Add a generated-site-only `Daily Local Key Signals Digest` to the ROW ONE
homepage (`index.html`) so the daily page opens with an aggregated editorial
view of the already-saved local article signals.

The feature should answer: across today's locally saved articles, what matters
most, which brands/products/people recur, and which themes help a reader decide
what to open first.

## Product Scope

- Add an optional homepage-only `Daily Local Key Signals Digest` section.
- Place it after existing homepage Saved Article Briefs and before Saved
  Article Content Organization.
- Reuse Stage 356 `Saved Article Key Signals` outputs for each current-edition
  local article.
- Organize the digest into compact groups:
  - `Why It Matters`;
  - `Brands`;
  - `Products`;
  - `People`;
  - `Themes`.
- Link only to generated local article pages and local article fragments, such
  as `articles/<story-id>.html#saved-article-key-signals-title`,
  `articles/<story-id>.html#local-article-paragraph-N`, and
  `articles/<story-id>.html#local-article-content-section-N`.

## Non-Goals

- No app contract, schema, runtime, manifest, or JSON artifact changes.
- No new article sidecars, generated data files, route families, or local
  storage behavior.
- No new scraping, source fetching, extraction, scoring, ranking, LLM calls,
  social connectors, scheduling, deployment, analytics, personalization,
  recommendation, or compliance-review behavior.
- No mutation of stored article text, paragraph indices, content sections,
  references, brief sections, or extracted source records.
- No external links or outbound article fetches.
- No rendering on `articles/index.html`, `details/*.html`, or
  `articles/<story-id>.html`; Stage 356 remains the article-page key signal
  surface.

## Data Sources

Reuse existing in-memory render inputs:

- `RowOneEdition`
- `RowOneStory`
- `RowOneLocalArticle`
- `build_row_one_saved_article_key_signals(...)`
- `RowOneSavedArticleKeySignals`
- `RowOneSavedArticleKeySignalGroup`
- `RowOneSavedArticleKeySignalReference`
- `RowOneSavedArticleKeySignalTheme`
- `RowOneSavedArticleKeySignalEvidence`

The builder must sanitize local article routes with:

- `safe_local_article_story_id(story.id)`
- `story.id == local_article.story_id`

## Aggregation Rules

- Iterate `edition.stories` in current homepage order.
- For each story with a matching local article, build Stage 356 key signals.
- Skip stories without valid key signals.
- `Why It Matters`:
  - collect the Stage 356 `why_it_matters` group statement;
  - render capped article-level statements with article title, source name, and
    local article link.
- `Brands`, `Products`, and `People`:
  - collect Stage 356 references from matching groups;
  - dedupe within each bucket by normalized displayed reference name;
  - preserve first-seen order while counting additional supporting articles;
  - attach the first readable support statement and first safe evidence/local
    article link.
- `Themes`:
  - collect Stage 356 theme labels;
  - dedupe by normalized displayed label;
  - preserve first-seen order while counting additional supporting articles;
  - attach the first safe content-section or article link.

## Rendering Rules

- Return `None` when no valid current-edition local article key signals can be
  built.
- Cap rendered Why It Matters entries, reference entries, theme entries, and
  support labels so the homepage remains compact.
- Compute total/support counts from the full eligible input before display caps.
- Escape all rendered text in `templates.py`.
- Revalidate every builder-provided href in the renderer.
- Renderer accepts only:
  - `articles/<safe-story-id>.html#saved-article-key-signals-title`;
  - `articles/<safe-story-id>.html#local-article-paragraph-N`;
  - `articles/<safe-story-id>.html#local-article-content-section-N`.

## Acceptance Criteria

- The homepage can render a readable daily digest of local key signals without
  changing app-facing contracts or generated data artifacts.
- The digest appears only on `index.html`.
- The digest appears after the Saved Article Briefs section and before the
  Saved Article Content Organization section when both exist.
- The digest includes readable statements, counts, references, themes, and safe
  links to locally generated article pages.
- Tests cover builder aggregation, dedupe/count separation, link safety,
  rendering escaping, homepage-only integration, docs references, and workflow
  guard coverage.
