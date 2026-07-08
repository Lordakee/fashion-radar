# Stage 358 Daily Local Signal Momentum Design

## Goal

Add a generated-site-only `Daily Local Signal Momentum` section to the ROW ONE
homepage (`index.html`) so the daily page can show which brands, products, and
themes have the strongest support inside today's already-saved local articles.

The feature should answer: among today's local saved source set, which labels
are most concentrated enough to open first?

## Product Scope

- Add an optional homepage-only `Daily Local Signal Momentum` section.
- Place it after `Daily Local Key Signals Digest` and before `Saved Article
  Content Organization`.
- Reuse the existing Stage 350 `RowOneSavedArticleDailySignalLeaderboard`
  view model rather than creating a second aggregation algorithm.
- Render compact buckets for:
  - `Brands`;
  - `Products`;
  - `Themes`.
- For each label, show article count, source count, and capped supporting
  article links.
- Link support rows to generated first-class local article pages when possible,
  using `articles/<story-id>.html#local-article-digest`.
- Fall back to the existing detail digest route only when no safe first-class
  local article page href exists.

## Non-Goals

- No historical trend delta, time-series comparison, heat scoring, or ranking
  model.
- No new app contract, schema, runtime, manifest, or JSON artifact changes.
- No new sidecars, generated data files, route families, local storage behavior,
  SQLite writes, or retention behavior.
- No new scraping, source fetching, extraction, matching, scoring, ranking, LLM
  calls, social connectors, scheduling, deployment, analytics,
  personalization, recommendation, or compliance-review behavior.
- No rendering on `articles/index.html` under the new homepage class; Stage 350
  remains the article-library leaderboard surface.
- No mutation of Stage 350 dataclasses or builder behavior unless a test proves
  a compatibility bug.

## Data Sources

Reuse existing in-memory render inputs:

- `RowOneSavedArticleDailySignalLeaderboard`
- `RowOneSavedArticleDailySignalLeaderboardBucket`
- `RowOneSavedArticleDailySignalLeaderboardItem`
- `RowOneSavedArticleDailySignalLeaderboardSupport`
- existing `build_row_one_saved_article_daily_signal_leaderboard(...)`
- existing `build_row_one_saved_article_signal_facets(...)`
- existing saved article library and content organization builders

The homepage renderer must also receive a safe mapping from detail pages to
first-class local article page hrefs, derived from current-edition safe story
IDs and publishable local articles. This mapping is pure in-memory route
calculation; it must not write files.

## Rendering Rules

- Return an empty string when no leaderboard or no renderable buckets exist.
- Revalidate all support hrefs before rendering.
- Prefer `articles/<story-id>.html#local-article-digest` when a safe local
  article page href exists for the support's detail path.
- If falling back to a detail digest path, accept only
  `details/<safe-detail>.html#local-article-digest`.
- Escape all display text in `templates.py`.
- Use a distinct homepage class family:
  - `.daily-local-signal-momentum`
  - `.daily-local-signal-momentum-*`
- Do not reuse the Stage 350 `.saved-article-daily-signal-leaderboard` class on
  the homepage.

## Acceptance Criteria

- The homepage can render a compact current-day signal momentum panel from
  existing saved local article signal leaderboard data.
- The section appears only on `index.html`.
- The section appears after `.daily-local-key-signals-digest` and before
  `.saved-article-content-organization` when all three sections exist.
- The section displays brand, product, and theme labels with article/source
  counts and support links.
- Unsafe support links are filtered.
- App-facing contracts and generated JSON artifacts remain unchanged.
- Docs and workflow guards describe the generated-site-only boundary.
