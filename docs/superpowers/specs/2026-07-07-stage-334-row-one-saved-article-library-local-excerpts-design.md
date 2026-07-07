# Stage 334 ROW ONE Saved Article Library Local Excerpts Design

## Goal

Make `articles/index.html` more useful as a local reading surface by showing
organized local article excerpts inside the source-grouped saved article cards.
Readers should be able to scan what a downloaded/local article contains before
opening the detail page.

## Current Gap

Stages 326-333 turned the dedicated saved article library into a source-grouped,
signal-indexed, content-grouped page with body-source provenance. Stage 332 also
adds a standalone "Saved Article Content Organization" section that already
contains localized local-text leads.

The remaining gap is placement: source-grouped saved article cards still mostly
show metadata and links. A reader has to look at a separate organization section
or open the detail page to see the actual organized local excerpt for that
article.

## Chosen Approach

Reuse the existing `RowOneSavedArticleContentOrganization` view model and mirror
matching organized leads into the existing saved article library cards:

- Build a template-only lookup from `RowOneSavedArticleContentOrganizationCard`
  objects keyed by canonical generated detail page path.
- Match each `RowOneSavedArticleLibraryEntry` by its safe canonical
  `details/<story>.html` path, derived from existing reader/digest/evidence
  hrefs.
- Render up to three matching organized excerpts inside that saved article
  library card.
- Link each excerpt back to the existing detail-page
  `#local-article-content-section-N` anchor and reuse existing paragraph
  evidence links.

This keeps Stage 334 as a generated-site-only HTML enhancement. It does not add
new content generation, new dataclass fields, new schemas, new sidecars, or new
JSON artifacts.

## Alternatives Considered

A larger "Saved Article Reading Paths" section would add a new generated-site
builder that creates cross-article routes such as Read First, People & Brands,
Products, and Source Context. That is a good follow-up direction, but it is a
larger product surface with new selection semantics, render wiring, and tests.
Stage 334 deliberately takes the lower-risk step first: use the organized local
leads that already exist and place them directly where readers are scanning the
source-grouped article cards.

## UI Behavior

Each saved article library card can render a compact block:

- group/section label, such as `Read First`, `People & Brands`, or `Products`;
- a capped bilingual lead from existing saved local article organization;
- a safe internal link to the organized detail-page section;
- capped evidence paragraph links when available.

The card still retains the existing reader/digest/evidence actions. The in-card
excerpt block is a scan cue, not a replacement for the detail page reader.

If no matching organized content exists for an entry, the card omits the excerpt
block. If an organization card has an unsafe route or wrong fragment, that
snippet is omitted entirely.

## Architecture

Implementation stays in `templates.py`:

- `render_saved_article_library_html()` receives both the saved article library
  and the optional saved article content organization.
- A helper flattens the content organization into a per-detail-page snippet
  lookup using existing route validation.
- Source-group rendering passes that lookup into each card renderer.
- Card rendering emits a static HTML snippet block only for safe matching
  organization cards.
- Existing `_local_article_digest_excerpt()` handles text capping and
  normalization. Existing content-organization href helpers handle route and
  fragment safety.

No `RowOneLocalArticle` schema change is required. No
`RowOneSavedArticleLibrary` dataclass change is required. No app/runtime/manifest
contract change is required.

## Contract Boundaries

Do not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `row-one-runtime/v1`
- JSON schemas
- `data/articles/<story-id>.json` sidecar schema
- source collection
- fetching
- matching
- extraction
- scoring
- ranking
- LLM behavior
- connector behavior
- scheduling
- deployment behavior
- market grouping
- domestic/international classification
- compliance-review product behavior

Do not add:

- full article republication on `articles/index.html`
- outbound article URLs in the snippet block
- new extraction or crawling behavior
- new summary generation behavior
- new social/community platform behavior
- `data/saved-article-library-local-excerpts.json`
- any generated JSON contract for this section

## Tests

Add focused render and docs tests that prove:

- `articles/index.html` renders matching organized local excerpts inside saved
  article source cards, not only in the standalone content organization section;
- matching is based on safe canonical generated detail paths, not display
  strings;
- unsafe routes, traversal, and wrong fragments omit the entire snippet text;
- canonical detail paths render as `../details/<story>.html#...`;
- duplicate snippets are deduped and per-card snippets are capped;
- escaped local excerpt HTML cannot render raw tags;
- long local excerpts are truncated in the library card;
- `edition.json`, `manifest.json`, and `runtime.json` do not expose local excerpt
  view-model vocabulary or card text;
- `README.md` and `docs/row-one.md` document the Stage 334
  generated-site-only boundary.

## Out Of Scope

- No crawler, source, or social connector work.
- No article extraction dependency changes.
- No LLM-generated summaries.
- No full-article publication on the library index.
- No app contract change.
- No generated images.
- No broad visual redesign.
- No compliance-review functionality.
