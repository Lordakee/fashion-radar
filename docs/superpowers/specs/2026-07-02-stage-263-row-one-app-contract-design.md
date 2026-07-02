# Stage 263 ROW ONE App Contract Design

## Goal

Stage 263 formalizes ROW ONE `data/edition.json` into a stable app-facing JSON
contract so a separate ROW ONE app can render the daily edition without scraping
HTML or reimplementing template logic.

## Product Gap

Stage 260 created the local static site, Stage 261 added deterministic editorial
synthesis, and Stage 262 added reader orientation in HTML. The generated JSON is
still only a sanitized internal `RowOneEdition` dump. It has no explicit contract
version, no schema, and no client-ready section/story navigation fields. That is
weak for app integration because a client must infer counts, anchors, safe links,
and story orientation from internal model details.

Stage 263 closes the app-consumption gap in the `collect -> match -> report ->
ROW ONE` path by making the generated JSON a versioned public surface while
leaving source collection, matching, ranking, story IDs, HTML rendering, cleanup,
server behavior, and scheduling unchanged.

## Chosen Approach

Add a dedicated app payload builder for `data/edition.json`.

The builder derives a `row-one-app/v1` payload from existing local
`RowOneEdition`, `RowOneSection`, and `RowOneStory` objects. It keeps
`RowOneEdition` as the internal presentation model, but writes a client-ready
payload with stable top-level keys, section-level counts and hrefs, story-level
section metadata, detail hrefs, dates, safe evidence-link counts, sanitized URLs,
and bilingual text blocks.

The payload is deterministic and local-only. It does not add an API server,
authentication, deployment, live refresh, web sockets, scraping, platform APIs,
translation, LLM calls, image generation, demand proof, platform coverage
verification, or compliance-review product behavior.

## Contract Shape

Top-level payload:

```json
{
  "contract_version": "row-one-app/v1",
  "brand": "ROW ONE",
  "generated_at": "2026-07-02T04:00:00Z",
  "edition_date": "2026-07-02T04:00:00Z",
  "summary": {"zh": "...", "en": "..."},
  "sections": [],
  "stories": [],
  "story_count": 1,
  "evidence_count": 1
}
```

Section object:

```json
{
  "key": "top_stories",
  "title": {"zh": "今日重点", "en": "Top Stories"},
  "dek": {"zh": "...", "en": "..."},
  "href": "#top_stories",
  "story_count": 1
}
```

Story object:

```json
{
  "id": "the-row-signal-1234567890",
  "section_key": "top_stories",
  "section": {
    "key": "top_stories",
    "title": {"zh": "今日重点", "en": "Top Stories"},
    "href": "#top_stories"
  },
  "headline": "The Row signal",
  "summary": {"zh": "...", "en": "..."},
  "why_it_matters": {"zh": "...", "en": "..."},
  "editorial_takeaway": {"zh": "...", "en": "..."},
  "signal_context": {"zh": "...", "en": "..."},
  "reader_path": {"zh": "...", "en": "..."},
  "source_name": "Vogue Business",
  "source_url": "https://example.com/the-row",
  "published_at": "2026-07-02T04:00:00Z",
  "published_date": "2026-07-02",
  "detail_path": "details/the-row-signal-1234567890.html",
  "href": "details/the-row-signal-1234567890.html",
  "detail_href": "details/the-row-signal-1234567890.html",
  "tags": ["brand"],
  "evidence_count": 1,
  "evidence": []
}
```

Evidence object:

```json
{
  "title": "Safe evidence",
  "url": "https://example.com/evidence",
  "href": "https://example.com/evidence",
  "source_name": "Vogue Business"
}
```

Unsafe `source_url`, evidence `url`, and evidence `href` values are always
`null`. Story `detail_path`, `href`, and `detail_href` are the same validated
relative detail path. Evidence `url` and `href` are the same sanitized URL or
both `null`. Evidence count counts only safe clickable evidence URLs so it
matches the Stage 262 reader-facing orientation metadata.
Date-time fields use UTC `YYYY-MM-DDTHH:MM:SSZ` strings, while `published_date`
uses the UTC `YYYY-MM-DD` date derived from `published_at`.

## Schema

Add `schemas/row-one-app.schema.json` as the public schema for
`row-one-app/v1`. It validates required top-level keys, localized text objects,
section keys, story links, nullable URL fields, and integer counts.

The schema is a contract test target and a documentation artifact. It should not
require the app payload to include every future display field forever; the v1
schema can allow additional properties at the story/section level only if the
implementation deliberately chooses forward-compatible extension. For Stage 263,
use closed objects for top-level, sections, stories, evidence, and localized text
to keep the first contract strict and auditable.

## Generated Files

`row-one build` continues to generate the same site children:

- `index.html`
- `details/`
- `assets/row-one.css`
- `assets/row-one.js`
- `data/edition.json`
- `.row-one-site`

Stage 263 changes only the contents of `data/edition.json` from a sanitized
internal dump to the versioned app contract. It does not add `edition.raw.json`
in this stage; the project has no committed external consumer yet, and a single
versioned payload avoids two JSON surfaces drifting.

## Boundaries

Stage 263 does not:

- collect new sources;
- add scraping, browser automation, platform APIs, login cookies, proxy pools,
  CAPTCHA bypass, or paywall bypass;
- call LLMs, translation services, image services, or paid APIs;
- add deployment, publishing, auth, API serving, or remote hosting;
- change section caps, story ranking, story IDs, matching, scoring, or source
  attribution;
- change HTML rendering, detail-page output, latest-only cleanup, server dry-run
  behavior, or schedule command behavior;
- add demand proof, platform coverage verification, geographic market inference,
  or compliance-review product behavior.

## Acceptance Criteria

- `row-one build` writes `data/edition.json` with
  `contract_version == "row-one-app/v1"`.
- `data/edition.json` validates against `schemas/row-one-app.schema.json`.
- Sections include `href` and `story_count` derived from the current edition.
- Stories include section metadata, `detail_href`, `published_date`,
  `evidence_count`, and sanitized URL fields.
- Unsafe URLs are `null` everywhere in app-facing URL fields.
- Undated stories use `null` for both `published_at` and `published_date`.
- Existing ROW ONE HTML, detail pages, cleanup behavior, server validation, and
  schedule command behavior remain unchanged.
- Documentation describes the app contract and its presentation-only boundary.
- Focused ROW ONE render/edition/CLI/docs/schema tests and the full release gate
  pass.
