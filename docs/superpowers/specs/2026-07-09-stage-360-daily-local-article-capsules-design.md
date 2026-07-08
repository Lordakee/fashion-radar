# Stage 360 Daily Local Article Capsules Design

## Goal

Add a generated-site-only `Daily Local Article Capsules` section to the ROW ONE
homepage (`index.html`) so the daily page includes compact readable article
summaries built from already-saved local article text, not only topic links,
signal panels, or external source links.

The feature should answer: which saved local fashion articles should I read
first today, what does each one say in its own saved text, and where can I open
the exact local article digest/paragraphs inside ROW ONE?

## Product Scope

- Add an optional homepage-only `Daily Local Article Capsules` section.
- Place it after `Daily Local Heat Signals` and before `Saved Article Content
  Organization`.
- Use current in-memory `RowOneEdition.stories` plus
  `local_articles_by_story_id` and the generated local article page href map.
- Render compact article cards with:
  - story headline;
  - source name;
  - saved article body-source/provenance label when available from existing
    local article metadata;
  - up to three saved paragraph excerpts;
  - one compact "why it matters" line from the existing story field;
  - key references from existing story references and saved local content
    references;
  - same-site links into `articles/<story-id>.html#local-article-digest` and
    paragraph anchors when generated local article pages exist.
- Cap the section so the homepage stays editorial and scan-first.

## Non-Goals

- No new app contract, schema, runtime, manifest, sidecar, route family, or JSON
  artifact.
- No source fetching, scraping, crawling, connector, platform API, account,
  cookie, token, browser automation, scheduling, deployment, analytics,
  personalization, recommendation, LLM, translation, extraction, matching,
  scoring, ranking, database, retention, or compliance-review behavior.
- No full-article publishing on the homepage.
- No mutation of local article body text, paragraph anchors, detail routes, or
  first-class local article page routes.
- No rendering on `articles/index.html`, detail pages, or
  `articles/<story-id>.html` pages under the new homepage class.
- No changes to Stage 357 Daily Local Key Signals Digest, Stage 358 Daily Local
  Signal Momentum, Stage 359 Daily Local Heat Signals, or Saved Article Content
  Organization behavior except homepage ordering around the new section.

## Data Sources

Reuse existing in-memory render inputs:

- `RowOneEdition.stories`
- `RowOneStory` fields already rendered elsewhere:
  - `id`
  - `headline`
  - `source_name`
  - `why_it_matters`
  - `detail_path`
  - `entity_refs`
  - `product_refs`
  - `designer_refs`
- existing `local_articles_by_story_id`
- existing `RowOneLocalArticle` fields:
  - `title`
  - `source_name`
  - `body_source`
  - `paragraphs`
  - `paragraphs_zh`
  - `content_sections`
- generated safe story-id-to-local-article page href map derived from
  `_local_article_page_specs(...)`, not from story IDs alone.

## Rendering Rules

- Return an empty string when there are no usable saved local article capsules.
- A story can render only when:
  - the story ID is safe;
  - `local_articles_by_story_id[story.id]` exists;
  - the article has at least one usable saved paragraph;
  - the generated local article page href map contains the story ID;
  - the mapped page filename is safe and matches the story ID.
- Sort capsules by the current edition story order; this section is a read path,
  not a heat or score ranking.
- Cap capsules to four.
- Cap paragraph excerpts to three per capsule.
- Cap reference chips to six per capsule, deduped by normalized
  name/type/label.
- Prefer aligned `paragraphs_zh` only when it has the same length as
  `paragraphs`; otherwise show English/source excerpts in both language spans.
- Link the primary card action to
  `articles/<story-id>.html#local-article-digest`.
- Link paragraph excerpts to
  `articles/<story-id>.html#local-article-paragraph-N`.
- Escape all display text in `templates.py`.
- Use a distinct homepage class family:
  - `.daily-local-article-capsules`
  - `.daily-local-article-capsules-*`
- Do not reuse `.daily-local-heat-signals`, `.daily-local-signal-momentum`, or
  saved article library class names.

## Acceptance Criteria

- The homepage can render compact local article capsules from already-saved
  local text.
- The section appears only on `index.html`.
- The section appears after `.daily-local-heat-signals` and before
  `.saved-article-content-organization` when all three sections exist.
- Each card includes article/source identity, why-it-matters context, local
  paragraph excerpts, reference chips, and same-site local article links.
- Unsafe story IDs, missing local articles, empty local paragraphs, unsafe page
  hrefs, mismatched page hrefs, traversal, external schemes, and raw HTML are
  filtered or escaped.
- App-facing contracts and generated JSON artifacts remain unchanged.
- Docs and workflow guards describe the generated-site-only boundary.
