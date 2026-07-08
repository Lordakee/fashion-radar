# Stage 359 Daily Local Heat Signals Design

## Goal

Add a generated-site-only `Daily Local Heat Signals` section to the ROW ONE
homepage (`index.html`) so the daily page can surface which current-edition
brands and products are rising today and have saved local article text behind
them.

The feature should answer: among today's locally saved fashion stories, which
topics are getting heat now, and where can I open the local saved article
coverage?

## Product Scope

- Add an optional homepage-only `Daily Local Heat Signals` section.
- Place it after `Daily Local Signal Momentum` and before `Saved Article
  Content Organization`.
- Reuse the existing app payload `daily_digest.briefing_topics` topic
  aggregation, including `positive_heat_delta_sum` and `max_heat_delta`.
- Render only topics with positive current-edition heat and at least one story
  that has usable saved local article text.
- Show compact cards for current-day heated brands and products, including
  shoes and bags when the existing source references identify product subtypes.
- For each rendered topic, show topic type, story count, local article count,
  positive heat delta, max heat delta, evidence count, and capped local story
  links.
- Link story rows to generated first-class local article pages using
  `articles/<story-id>.html#local-article-digest`.

## Non-Goals

- No historical trend delta, multi-day comparison, persistence, retention,
  database write, or time-series analytics.
- No new app contract, schema, runtime, manifest, or JSON artifact changes.
- No new sidecars, generated data files, route families, local storage behavior,
  SQLite writes, or retention behavior.
- No new scraping, source fetching, extraction, matching, scoring, ranking,
  LLM calls, social connectors, scheduling, deployment, analytics,
  personalization, recommendation, or compliance-review behavior.
- No rendering on `articles/index.html`, detail pages, or `articles/<story-id>.html`
  local article pages under the new homepage class.
- No mutation of `briefing_topics_payload(...)`, app payload schema, Stage 350,
  Stage 356, Stage 357, or Stage 358 builders unless a test proves a
  compatibility bug.

## Data Sources

Reuse existing in-memory render inputs:

- `app_payload["daily_digest"]["briefing_topics"]`
- topic fields already produced by `briefing_topics_payload(...)`:
  - `topic_type`;
  - `title`;
  - `label`;
  - `story_count`;
  - `evidence_count`;
  - `positive_heat_delta_sum`;
  - `max_heat_delta`;
  - `story_ids`;
  - `cards`.
  - `source_refs`.
- existing `local_articles_by_story_id` passed into `render_index_html(...)`
- a safe `story_id -> local article page href` mapping derived from the same
  `_local_article_page_specs(...)` that writes `articles/<story-id>.html` pages;
- existing safe story-id and usable-local-article paragraph checks in
  `templates.py`.

The homepage renderer must derive local article links from the current in-memory
story ID, saved local article mapping, and generated-page href map. It must not
construct links from story IDs alone, and it must not read or write files.

## Rendering Rules

- Return an empty string when no usable heated local topics exist.
- Keep only topic types `brand` and `product`.
- Keep only topics with `positive_heat_delta_sum > 0` or `max_heat_delta > 0`.
- Keep only topic story IDs that:
  - are strings;
  - pass `safe_local_article_story_id(...)`;
  - have a matching current saved local article;
  - have at least one usable saved local paragraph;
  - exist in the safe generated local article page href map.
- Render topics sorted by `positive_heat_delta_sum` descending,
  `max_heat_delta` descending, local article count descending, evidence count
  descending, then topic title. Do not preserve the upstream briefing-topic sort
  because it prioritizes story count before heat.
- Prefer the topic `cards` payload for story headline/source/takeaway display,
  but render only cards whose IDs are in the safe local story allowlist.
- Render product subtype badges from existing `source_refs` when reference
  labels or types indicate bags, shoes, footwear, sneakers, boots, flats, heels,
  or sandals.
- Cap rendered topics to six and local story links to two per topic.
- Escape all display text in `templates.py`.
- Use a distinct homepage class family:
  - `.daily-local-heat-signals`
  - `.daily-local-heat-signals-*`
- Do not reuse `.daily-local-signal-momentum` or article-library class names.

## Acceptance Criteria

- The homepage can render a compact current-day heat signal panel from existing
  briefing topic heat fields and saved local article availability.
- The section appears only on `index.html`.
- The section appears after `.daily-local-signal-momentum` and before
  `.saved-article-content-organization` when all three sections exist.
- The section displays brand/product topic labels with heat, evidence, story,
  and local article counts.
- Product topics can show existing bag/shoe/footwear subtype badges from
  `source_refs`.
- Topic story rows link only to generated first-class local article pages.
- Topics without positive heat, topics without saved local text, unsafe story
  IDs, unsafe card values, traversal, and external schemes are filtered or
  escaped.
- App-facing contracts and generated JSON artifacts remain unchanged.
- Docs and workflow guards describe the generated-site-only boundary.
