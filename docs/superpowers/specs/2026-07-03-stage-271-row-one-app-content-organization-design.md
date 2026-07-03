# Stage 271 ROW ONE App Content Organization Design

## Goal

Stage 271 makes ROW ONE more useful to the app by adding structured content
organization to the app-facing JSON payload. The app should be able to render
the latest edition, section rails, story cards, and story detail content from
JSON directly, without scraping HTML and without rebuilding grouping logic that
the backend already knows.

This stage directly addresses the product requirement that ROW ONE should
organize fashion information, not merely provide links.

## Current State

ROW ONE currently generates:

- `data/edition.json`: strict `row-one-app/v1` app payload with sections,
  stories, summaries, synthesis fields, links, display metadata, and counts.
- `data/manifest.json`: `row-one-manifest/v1` discovery payload pointing to the
  app contract.
- `data/runtime.json`: `row-one-runtime/v1` local runtime payload for status,
  refresh, and serving metadata.
- Static HTML homepage and detail pages.

The current app payload is already better than a link list, but app clients
still need to group stories by section, pick each section lead, build cards, and
translate story fields into detail sections themselves.

## Stage Boundary

Stage 271 is presentation and contract work only.

It will not:

- add new source collectors;
- scrape social platforms;
- call LLMs;
- call translation services;
- generate or fetch images;
- install cron/systemd timers;
- deploy or publish the local site;
- add compliance-review product features.

Local deploy readiness and schedule installation are deferred to later stages.

## Contract Strategy

Keep the file path `data/edition.json` and schema path
`schemas/row-one-app.schema.json`, but bump the app payload contract from
`row-one-app/v1` to `row-one-app/v2`.

Rationale:

- The current schema is strict and adding top-level fields is a contract change.
- App clients should be able to detect the richer organized payload by version.
- The manifest already points to contract version and schema path, so this is
  discoverable without adding another sidecar file.
- The filename stays stable for app integration.

`row-one-manifest/v1` remains unchanged as a manifest contract. Its
`app_contract.version` value will point to `row-one-app/v2`, so
`schemas/row-one-manifest.schema.json` must update the app contract version
const from `row-one-app/v1` to `row-one-app/v2`. The manifest `site` shape will
not gain a `runtime_path` or content arrays.

## New App Payload Fields

### `content_sections`

Add top-level `content_sections`, one entry per existing ROW ONE section, in the
same order as `sections`.

Each content section contains:

- `key`: section key.
- `title`: localized title.
- `dek`: localized deck text.
- `href`: homepage anchor.
- `story_count`: number of stories in the section.
- `lead_story_id`: first story id in the section, or `null` when empty.
- `story_ids`: ordered story ids for the section.
- `cards`: ordered lightweight story cards for the section.

Each card contains:

- `id`
- `headline`
- `summary`
- `editorial_takeaway`
- `reader_path`
- `detail_href`
- `display`
- `source_name`
- `published_date`
- `tags`
- `evidence_count`

Cards are derived from the canonical `stories` array. They do not introduce new
ranking or duplicate evidence arrays.

### Story `detail_sections`

Add `detail_sections` to every story. This gives app clients a direct detail
screen model.

Each story detail section contains:

- `key`: one of `summary`, `why_it_matters`, `editorial_takeaway`,
  `signal_context`, `reader_path`, `evidence`.
- `title`: localized title.
- `body`: localized body text for text sections, or `null` for evidence.
- `evidence`: array of evidence links for the evidence section, or an empty
  array for text sections.

This keeps detail content deterministic and based on retained local fields. It
does not claim to produce full article text or translations of source articles.

### Story `evidence_summary`

Add `evidence_summary` to every story:

- `safe_link_count`: safe clickable evidence link count.
- `total_count`: total evidence entries.
- `primary_source_name`: story source name.
- `sources`: ordered unique source names from evidence entries.

This gives the app a compact provenance summary without parsing each evidence
entry.

## HTML Alignment

The static detail page should use the same conceptual organization as
`detail_sections`:

- Summary
- Why It Matters
- Editorial Takeaway
- Signal Context
- Reader Path
- Evidence Trail

Stage 271 may improve labels and section rhythm in HTML, but it should not
overhaul the whole visual system or introduce screenshot testing. Deeper
professional UI polish can continue in a later stage.

## Schema Requirements

`schemas/row-one-app.schema.json` must be strict:

- top-level `content_sections` is required;
- story `detail_sections` and `evidence_summary` are required;
- no extra fields are allowed;
- section card ids must be non-empty strings;
- `lead_story_id` can be string or `null`;
- `detail_href` must use the existing safe detail href pattern;
- evidence entries must reuse the existing safe URL rules;
- display objects must reuse the existing display schema.

`schemas/row-one-manifest.schema.json` must continue to validate
`row-one-manifest/v1`, but its `app_contract.version` const must move to
`row-one-app/v2`.

## Tests

Add coverage for:

- generated `row-one-app/v2` payload validates against schema;
- manifest points to `row-one-app/v2`;
- `content_sections` groups stories exactly by `section_key`;
- `lead_story_id` is the first story id in a non-empty section and `null` for
  empty sections;
- cards mirror the canonical story fields that app clients need;
- every story has deterministic `detail_sections`;
- `detail_sections` includes the existing `editorial_takeaway` field as a first
  class detail block;
- `evidence_summary` counts safe links and preserves unique source names;
- schema rejects content-section drift, invalid detail section keys, and extra
  fields;
- docs describe the app content organization contract.

## Documentation

Update:

- `docs/row-one.md`: describe `row-one-app/v2`, `content_sections`,
  `detail_sections`, and `evidence_summary`.
- `docs/cli-reference.md` only if command descriptions mention app contract
  version.
- `README.md` if the top-level ROW ONE summary still says first-run smoke covers
  only manifest/serve and omits runtime/app organization.

## Risks

- Version bump may require test updates wherever the app contract version is
  pinned.
- Adding derived card/detail structures duplicates some fields. The canonical
  `stories` array remains the source of truth; tests must assert the derived
  fields mirror it.
- The payload can grow. Stage 271 keeps detail sections compact and avoids
  duplicating evidence in cards.
