# Stage 363 Daily Local Coverage Map Design

## Context

Stages 357-362 added homepage sections that organize already-saved local article bodies by daily signals, momentum, heat, article capsules, reading lanes, and source provenance. Stage 362 answers which publications carried today's saved local articles, but readers still need a compact map of which sources contribute useful local text to each editorial organization bucket.

## Goal

Add a generated-site-only homepage section named **Daily Local Coverage Map**. It should sit after Daily Local Source Desk and before Saved Article Content Organization. It should cross-tab current saved local article sources against existing `RowOneSavedArticleContentOrganization` groups so ROW ONE can show where the day's saved local text has coverage across editorial buckets such as Read First, People & Brands, Products, and Source Structure.

The feature should make ROW ONE feel more like a professional editorial briefing desk: sources, organization buckets, local article pages, paragraph anchors, and reference chips become one compact navigational map built from already-downloaded local content.

## Non-Goals

- Do not add app-facing schema or payload fields.
- Do not create `data/daily-local-coverage-map.json`, `data/local-coverage-map.json`, or `data/coverage-map.json`.
- Do not create new route families or standalone HTML artifacts.
- Do not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages.
- Do not publish full articles on the homepage.
- Do not add outbound article URLs as primary navigation.
- Do not add fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

## Design

The homepage renderer derives a coverage map from:

- the current edition stories;
- existing `RowOneSavedArticleContentOrganization` groups and cards;
- existing saved local articles;
- generated local article page hrefs keyed by detail path;
- current story references and card references.

Eligibility for a coverage source row requires:

- a content-organization card with a nonblank source name;
- a safe detail path pointing to an existing current-edition story;
- a matching safe same-site local article page href;
- at least one local content-section anchor or paragraph anchor derived from existing card metadata;
- a matching saved local article with at least one usable paragraph.

Source grouping mirrors Stage 362:

- normalized source name: `normalize_row_one_paragraph(card.source_name)`;
- grouping key: `normalized_source_name.casefold()`;
- display name: the first normalized source name seen in content-organization order.

Each source row renders:

- source name;
- bucket count;
- saved article count;
- saved paragraph count;
- up to four bucket chips, each showing the organization group title and the number of local cards supporting it;
- up to five reference chips from existing card references, deduped by normalized name/type/label;
- up to two local coverage links pointing to same-site local article anchors.

Coverage links are labels only. The homepage does not republish article bodies or saved paragraph excerpts.

Rows are deterministic. Sort sources by:

1. bucket count descending;
2. saved article count descending;
3. saved paragraph count descending;
4. source display name case-insensitive ascending;
5. exact source display name ascending.

Cap the section at four sources. Cap bucket chips, reference chips, and links to keep the homepage compact.

## Rendering Boundary

The feature renders only inside homepage `index.html`. It must not write or mutate:

- `articles/index.html`;
- `articles/<story-id>.html`;
- story detail pages;
- `data/edition.json`;
- `data/manifest.json`;
- `data/runtime.json`;
- local article sidecar JSON.

## Placement

When present, the section renders after:

- `.daily-local-source-desk`

and before:

- `.saved-article-content-organization`

If Daily Local Source Desk is absent, Daily Local Coverage Map still uses the same relative homepage slot before Saved Article Content Organization.

## Link Safety

The renderer never derives local article hrefs from detail paths alone. It must use only the supplied generated href map and validate resulting links as same-site local article routes.

Rendered links must be same-site:

- `articles/<story-id>.html#local-article-content-section-N`; or
- `articles/<story-id>.html#local-article-paragraph-N` when a content-section anchor is unavailable and the card has a safe paragraph index.

Unsafe absolute paths, nested traversal, whitespace hrefs, mismatched story ids, missing local articles, and malformed anchors are filtered out.

## Testing Strategy

Tests should follow Stage 360-362 patterns:

- direct render test for source grouping, bucket counts, article counts, paragraph counts, ordering, caps, reference-chip dedupe, bilingual headings, same-site local links, and escaping;
- filtering test for unsafe detail paths, unsafe local article hrefs, missing local articles, blank source names, empty paragraphs, and mismatched story ids;
- placement test after Daily Local Source Desk and before Saved Article Content Organization;
- placement test when Daily Local Source Desk is absent, proving the Coverage Map still renders before Saved Article Content Organization;
- site-generation test proving homepage-only behavior and contract/artifact denylist;
- CSS selector test;
- docs boundary test in README and `docs/row-one.md`;
- workflow generated-site-only guard test.

## Review Notes

This is intentionally a presentation-layer organization map. It does not discover new content, fetch new articles, score source authority, build trends, or generate recommendations. It organizes already-downloaded local text by source and editorial bucket so the daily website has a clearer coverage map.
