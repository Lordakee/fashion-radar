# Stage 345 ROW ONE Saved Article Daily Summary Design

## Objective

Stage 345 adds a generated-site-only Saved Article Daily Summary to
`articles/index.html`. The section gives readers a compact orientation layer for
today's saved local fashion articles: how many saved article entries are present,
which existing reading surfaces are available, and where to start reading the
locally saved article text.

## Product Gap

ROW ONE already renders saved article library cards, theme digest cards,
reference atlas buckets, saved signal index entries, reading paths, paragraph
evidence cards, content organization groups, group summaries, and an
organization coverage matrix. Those modules are valuable but dense. A reader
landing on the saved article library still needs a brief editorial orientation:
what has been saved today, which organizing surfaces are available, and which
safe internal links move them into the local saved text.

The daily summary closes that orientation gap without creating a new source of
analysis. It is a compact guide rail, not a new theme digest, evidence board,
reference atlas, ranking rail, or recommendation module.

## Architecture

This is a generated-site-only rendering change in
`src/fashion_radar/row_one/templates.py`. It derives all facts from existing
objects already passed to `render_saved_article_library_html()`:

- `RowOneSavedArticleLibrary`
- `RowOneSavedArticleThemeDigest`
- `RowOneSavedArticleReferenceAtlas`
- `RowOneSavedSignalIndex`
- `RowOneSavedArticleReadingPaths`
- `RowOneSavedArticleEvidenceBoard`
- `RowOneSavedArticleContentOrganization`

The implementation should add private render helpers near the saved article
library renderers:

- `_render_saved_article_daily_summary(...)`
- `_render_saved_article_daily_summary_link(...)`

The section should render immediately after the saved article library hero and
before the existing theme digest. If there is no safe saved article library
content and no available summary target, it returns an empty string.

## Rendering Behavior

The daily summary should show:

- one compact metric row for saved local articles, sources, and available
  organization surfaces;
- two or three short bilingual orientation statements derived from existing
  counts;
- safe quick links to existing sections on `articles/index.html`, such as Theme
  Digest, Reference Atlas, Saved Signal Index, Reading Paths, Evidence Board,
  Content Organization, and the source grid;
- one safe internal local-article reading link when a saved article entry has a
  validated local article page route or a safe detail-page local article digest
  target.

The section must not render article-body excerpts, theme item leads, paragraph
evidence excerpts, reference atlas buckets, coverage matrix rows, or content
organization cards. Those remain owned by their existing modules.

## Sanitization And Caps

All rendered text must be escaped. Links must be internal-only and deterministic.
Section-anchor links on `articles/index.html` should point to safe in-page
anchors owned by the generated page. Article reading links must reuse existing
safe detail-route or local article page validation patterns and must not trust
raw card paths.

The output should use fixed caps, stable source order, and no time, randomness,
ranking, scoring, heat logic, or recommendations.

## Out Of Scope

Stage 345 does not add article downloading, social-platform collection, external
tool adapters, scraping, browser automation, platform APIs, account/cookie/token
behavior, new content extraction, new summaries from LLMs, ranking, demand proof,
heat scoring, analytics, personalization, recommendation, compliance review, new
JSON artifacts, new route families, app contract changes, or outbound article
URLs as primary navigation. It only improves the generated ROW ONE saved article
library HTML from existing local article/library objects.

## Acceptance Criteria

- `articles/index.html` renders one Saved Article Daily Summary after the saved
  article library hero and before the saved article theme digest when saved
  local article context exists.
- The section contains compact factual orientation metrics and quick links to
  existing generated-page sections.
- The section does not duplicate theme lead lists, paragraph excerpts, reference
  buckets, coverage rows, or content organization cards.
- Unsafe or unavailable links do not render, and a fully empty summary shell is
  omitted.
- Documentation states the generated-site-only boundary for Stage 345.
- Workflow tests confirm no app-facing contract keys, schemas, route families,
  or JSON/HTML artifact files are created for the daily summary.
