# Stage 312 ROW ONE Saved Article Coverage Design

## Objective

Add a ROW ONE homepage saved article coverage surface that summarizes the
current edition's locally saved article corpus before readers open individual
detail pages. Stage 311 made one saved article easier to scan on its detail
page; Stage 312 should make the day's saved article set easier to understand
from the homepage.

## User Need

The user wants ROW ONE to be a professional daily fashion website that organizes
information, not a list of outbound links. A reader opening the homepage should
see whether today's edition has local saved text coverage, which sources are
represented, how many saved paragraphs are available, and which saved articles
are worth opening first.

## Current Context

ROW ONE already has:

- optional `RowOneLocalArticle` sidecars written under
  `data/articles/<story-id>.json`;
- `Daily Local Intelligence`, which groups strongest reads, brand watch,
  product watch, and heat movers from saved local article bodies;
- Stage 310 saved text reader on detail pages;
- Stage 311 saved text digest on detail pages.

What is missing is a compact homepage-level saved article coverage overview:
an edition reader can see the local saved article corpus as a set before
choosing a detail page.

## Recommended Approach

Implement a generated-site-only homepage section:

```text
Saved Article Coverage / 保存正文覆盖
```

The section should render after `Daily Local Intelligence` and before the lead
story block. It should be derived from the same `local_articles_by_story_id`
mapping already passed into `render_row_one_site()`.

The section should include:

- a metrics strip:
  - saved article count;
  - nonblank saved paragraph count;
  - organized section count;
  - source count;
- a source list with source names and saved article counts;
- a read queue of up to four saved article cards:
  - story headline;
  - source name;
  - section title;
  - saved paragraph count;
  - organized section count;
  - link to `details/<story>.html#local-article-digest` when the detail digest
    exists, otherwise `#local-article`;
- bilingual copy using the existing `data-lang` pattern.

The metrics are edition-level corpus totals. The read queue is intentionally
capped at four cards, so `article_count` may be larger than the number of
rendered cards.

## Architecture

Add a small internal builder module, for example
`src/fashion_radar/row_one/saved_article_coverage.py`, with dataclasses for the
homepage coverage view model. Keep this separate from the app-facing Pydantic
models to avoid implying a new JSON contract.

`render_row_one_site()` should:

1. build the app payload as it does today;
2. build `local_article_intelligence` as it does today;
3. build the new saved article coverage view model from `edition` and
   `local_articles_by_story_id`;
4. pass it to `render_index_html()`;
5. not write a new JSON artifact in this stage.

`render_index_html()` should accept an optional coverage model and render the
section only when it has publishable saved articles.

## Data Selection Rules

Only include local articles that:

- belong to a story in the current edition;
- have a safe local story id under existing story id rules;
- have at least one nonblank saved paragraph.

Counts:

- saved article count: number of included articles;
- saved paragraph count: sum of nonblank paragraphs;
- organized section count: sum of `content_sections`;
- source count: unique nonblank source names.

Read queue sorting:

1. edition story order;
2. story headline as a deterministic tie-breaker;
3. story id.

Source chips preserve first-seen source order from the edition story order.

Reference grouping is intentionally deferred. `Daily Local Intelligence` already
surfaces brand/person/product groupings; Stage 312 should stay focused on saved
article coverage and read-entry organization.

## Link Rules

Coverage cards should link to generated detail pages only. The primary link
should target `#local-article-digest` when the article has at least one nonblank
paragraph, because Stage 311 now renders that digest for saved articles. The
fallback target is `#local-article`.

Do not link to external source URLs from this homepage coverage surface.
External attribution remains in evidence and detail-page provenance.

## Boundaries

Stage 312 is generated-site presentation only.

It must not:

- change `row-one-app/v7`;
- change `data/edition.json`;
- change `row-one-manifest/v1`;
- change `row-one-runtime/v1`;
- change JSON schemas;
- change story IDs;
- change detail routes;
- change paragraph anchors;
- add source collection;
- add scraping, browser automation, platform APIs, login/cookie/proxy/CAPTCHA,
  or paywall behavior;
- add scoring, demand proof, platform coverage verification, social/community
  connectors, LLM calls, translation services, image generation, or scheduling;
- write a new JSON artifact in this stage.

## Testing Strategy

Use TDD.

Add focused tests for:

- builder output from mixed valid/invalid local article mappings;
- metrics counts for articles, saved paragraphs, organized sections, and
  sources;
- homepage rendering order after Daily Local Intelligence and before lead story;
- card links to `#local-article-digest`;
- no section when there are no saved articles;
- escaping of source names and headlines;
- app contract stability: no coverage data in `data/edition.json`, and contract
  versions remain unchanged;
- CSS selector presence;
- docs boundary text in README and `docs/row-one.md`.

## Verification

Implementation should pass:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py -q
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
