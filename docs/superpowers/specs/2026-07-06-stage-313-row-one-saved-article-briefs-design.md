# Stage 313 ROW ONE Saved Article Briefs Design

## Objective

Add a ROW ONE homepage saved article briefs surface that shows what the
locally saved article bodies actually say, not only that saved article coverage
exists. Stage 312 summarizes the saved article corpus; Stage 313 should put
readable, source-backed article content on the homepage.

## User Need

The user wants ROW ONE to behave like a professional daily fashion website that
organizes information into useful reading surfaces. A reader should be able to
open the daily homepage and immediately scan saved local article takeaways,
relevant brands/people/designers, and relevant bags/shoes/products without
having to click into every detail page first.

## Current Context

ROW ONE already has:

- optional `data/articles/<story-id>.json` local sidecars with saved
  `paragraphs`, optional `paragraphs_zh`, and structured `content_sections`;
- detail-page saved text reader and saved text digest;
- homepage Daily Local Intelligence, which groups local signals;
- homepage Saved Article Coverage, which inventories the local article corpus.

The remaining gap is a homepage content-reading layer for the saved article
sidecars themselves: compact cards that surface the lead takeaway and local
references for each saved article.

## Recommended Approach

Implement a generated-site-only homepage section:

```text
Saved Article Briefs / 保存正文简报
```

The section should render after `Saved Article Coverage` and before the lead
story block. It should be derived only from the same `local_articles_by_story_id`
mapping already passed into `render_row_one_site()`.

Each card should represent one current-edition saved local article and include:

- story headline;
- ROW ONE section title;
- source name;
- a capped lead saved text excerpt:
  - prefer the first nonblank item body from the `takeaways` content section;
  - fallback to the first nonblank saved paragraph;
- up to four `People & Brands` chips from `entities` content sections;
- up to four `Products` chips from `product_signals` content sections;
- a link to `details/<story>.html#local-article-digest`;
- bilingual display using existing `data-lang` spans.

The section should be omitted when no publishable saved local articles exist.

## Architecture

Add a small shared detail-route helper module, for example
`src/fashion_radar/row_one/detail_routes.py`, so homepage builders and
templates validate `details/<story>.html#fragment` links through one internal
route contract instead of copy-pasting regexes.

Add a small internal dataclass builder module, for example
`src/fashion_radar/row_one/saved_article_briefs.py`.

The builder should:

1. iterate current edition stories in edition order;
2. select only local articles that belong to the current edition;
3. require `safe_local_article_story_id(story.id)`;
4. require a safe `details/<story>.html` detail path;
5. require at least one nonblank saved paragraph;
6. derive a lead brief from existing `content_sections` or paragraphs;
7. derive reference chips from existing `entities` and `product_signals`
   content sections;
8. cap homepage cards at four articles.

`render_row_one_site()` should build the saved article briefs view model and
pass it to `render_index_html()`.

`render_index_html()` should accept an optional saved article briefs model and
render the section after `saved_article_coverage_section`.

This is an HTML/CSS presentation surface only. It should not be written into
`data/edition.json`, `data/manifest.json`, `data/runtime.json`, or any new JSON
artifact.

## Data Selection Rules

Publishable saved article:

- current edition story only;
- safe story id under existing local article story id rules;
- safe detail path matching existing ROW ONE detail route shape;
- at least one nonblank saved paragraph.

Lead excerpt:

- prefer first nonblank `RowOneLocalArticleContentItem.body` in a `takeaways`
  section;
- otherwise use the first nonblank saved paragraph;
- when using a paragraph fallback and `paragraphs_zh` aligns one-to-one with
  `paragraphs`, use the aligned zh paragraph; otherwise use the English text as
  both language values;
- truncate rendered excerpts through existing template text helpers, not by
  mutating sidecar data.
- keep the homepage surface to a capped excerpt only. Full saved paragraphs
  remain on the generated detail page, with local source attribution visible in
  the brief card.

Reference chips:

- `People & Brands` reads references from `content_sections` with key
  `entities`;
- `Products` reads references from `content_sections` with key
  `product_signals`;
- dedupe by normalized name, type, and label while preserving first-seen order;
- cap each chip list at four;
- omit empty chip groups.

Ordering:

- cards preserve edition story order;
- cap to four cards;
- counts remain presentation-only and are not persisted.

## Link Rules

Cards link only to generated detail pages:

```text
details/<story>.html#local-article-digest
```

Template rendering should revalidate the href before emitting an anchor, using
the shared internal detail route constraints as other ROW ONE homepage links.
Do not link to external source URLs from this section.

## Boundaries

Stage 313 is generated-site presentation only.

It must not:

- change `row-one-app/v7`;
- change `data/edition.json`;
- change `row-one-manifest/v1`;
- change `row-one-runtime/v1`;
- change JSON schemas;
- change story IDs;
- change detail routes;
- change paragraph anchors;
- write a new JSON artifact;
- add source collection, scraping, browser automation, platform APIs, login,
  cookies, proxy, CAPTCHA, or paywall behavior;
- add scoring, demand proof, platform coverage verification, social/community
  connectors, LLM calls, translation services, image generation, or scheduling;
- add compliance-review product features.
- republish full external articles on the homepage. The homepage card shows a
  capped local excerpt, source name, and a link into the generated detail page.

## Testing Strategy

Use TDD.

Add focused unit tests for the builder:

- takeaway body is preferred over paragraph fallback;
- paragraph fallback is used when no takeaway body exists;
- invalid story ids, invalid detail paths, blank paragraphs, and non-edition
  articles are excluded;
- reference chips dedupe and preserve first-seen order;
- card cap is four in edition order.

Add rendering tests:

- homepage renders `Saved Article Briefs / 保存正文简报` after Saved Article
  Coverage and before the lead story;
- section is omitted without publishable saved articles;
- escaped headlines, sources, bodies, and reference chips render safely;
- invalid direct view-model hrefs are not emitted;
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` do not
  contain saved article briefs or contract version changes;
- CSS selectors exist with selector-aware checks.

Add docs tests:

- README and `docs/row-one.md` include Stage 313 boundary wording scoped to the
  Stage 313 paragraph.

## Verification

Implementation should pass:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_briefs.py tests/test_row_one_render.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Expected status contracts remain:

- `row-one-app/v7`
- `row-one-manifest/v1`
- `row-one-runtime/v1`
