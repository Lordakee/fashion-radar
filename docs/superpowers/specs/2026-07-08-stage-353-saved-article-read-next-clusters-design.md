# Stage 353 ROW ONE Saved Article Read Next Clusters Design

## Objective

Stage 353 adds a generated-site-only Saved Article Read Next Clusters section
inside `articles/index.html`. The section organizes existing saved local
articles into compact topical clusters so readers can understand what to read
next without leaving the ROW ONE site or opening a list of undifferentiated
links.

## Product Gap

Stage 352 added a short Saved Article Reading Queue, but that queue remains a
linear set of local article entry points. ROW ONE already has saved article
library cards, content organization, reading paths, theme digest, reference
atlas, signal facets, daily signal leaderboard, evidence board, and a jump
index. The missing layer is a small "read next by signal" organizer that
answers: which saved local articles belong together, what is the shared local
theme, and why should a reader open them?

Read Next Clusters close that gap as editorial organization. They are not a
ranking model, recommendation system, personalization layer, analytics layer,
market heat signal, or external popularity signal.

## Architecture

This is a generated-site-only presentation feature:

- `src/fashion_radar/row_one/saved_article_read_next_clusters.py` builds a
  capped in-memory view model from existing `RowOneSavedArticleLibrary` and
  `RowOneSavedArticleContentOrganization` data.
- Clusters reuse the existing content-organization groups (`Read First`,
  `People & Brands`, `Products`, `Source Structure`) as cluster themes.
- Cluster items reuse existing saved article titles, source names, section
  labels, local leads, references, paragraph evidence counts, body-source
  labels, safe local article page hrefs, and safe content-section anchors.
- `src/fashion_radar/row_one/templates.py` renders the clusters only inside
  `articles/index.html`, after the Stage 352 Reading Queue and before Signal
  Facets.
- `src/fashion_radar/row_one/render.py` should not gain new app-contract
  payloads. If wiring is required, it should pass only existing generated local
  article page href maps already used by the saved article library page.

The feature creates no schema, SQLite table, JSON artifact, route family,
collector, extraction path, ranking model, LLM call, scheduler, deployment,
app-facing contract field, analytics, personalization, recommendation, or
compliance-review product behavior.

## Rendering Behavior

When at least one safe cluster can be built, Stage 353 renders a
`saved-article-read-next-clusters` section in `articles/index.html`.

Each cluster should show:

- localized cluster title and dek from the existing content organization group;
- article count, source count, and evidence paragraph count;
- up to three local article cards;
- each card's title, source name, section label, body-source label, short local
  lead excerpt, reference chips, evidence count, and one safe local action link.

The section is omitted when no safe cluster item exists. It should not appear
on the homepage or detail article pages.

## Data Sources

Stage 353 should reuse only:

- `RowOneSavedArticleLibrary.groups`;
- `RowOneSavedArticleContentOrganization.groups`;
- existing generated local article page hrefs by safe detail path;
- safe detail digest and content-section anchors already represented by saved
  article library/content organization entries.

It should not inspect raw article text beyond the already-built organization
lead values, raw source URLs, imported signals, external search results, social
platform data, downloaded article HTML, or LLM output.

## Safety And Caps

All visible text must be escaped by the template layer. Links must be rechecked
at render time.

Allowed href forms:

- `<safe-story-id>.html#local-article-digest` for generated local article
  pages;
- `../details/<safe-detail-file>.html#local-article-content-section-N` for
  canonical same-site content-section fallback links;
- `../details/<safe-detail-file>.html#local-article-digest` only when no safe
  content-section link is available.

Rejected href forms:

- outbound URLs;
- protocol-relative URLs;
- JavaScript URLs;
- non-canonical traversal;
- whitespace-bearing hrefs;
- empty hrefs;
- wrong fragments.

Caps:

- up to three clusters;
- up to three items per cluster;
- up to four reference chips per item;
- no full article body text;
- no copied full article summaries;
- no outbound links.

## Out Of Scope

Stage 353 does not add article downloading, social-platform collection,
external tool adapters, scraping, browser automation, platform APIs,
account/session behavior, extraction changes, LLM summaries, ranking,
recommendation, analytics, personalization, scheduling, deployment, app
contract changes, schema changes, new route families, or compliance-review
product behavior.

It also does not create `data/saved-article-read-next-clusters.json`,
`data/article-read-next-clusters.json`, `saved-article-read-next-clusters.html`,
or any new JSON/HTML artifact.

## Acceptance Criteria

- `articles/index.html` renders a `saved-article-read-next-clusters` section
  after the Reading Queue and before Signal Facets when at least one safe
  cluster item exists.
- Clusters preserve existing content-organization group order instead of
  sorting by support counts, source counts, products, themes, or popularity.
- Items preserve saved article library order within each cluster.
- Items link only to safe local article page digest hrefs or safe same-site
  detail anchors.
- The template accepts canonical `../details/...#local-article-content-section-N`
  fallback links and rejects traversal, outbound, wrong-fragment, whitespace,
  and JavaScript href forms.
- Empty or unsafe inputs omit the whole section shell.
- Labels, titles, source names, section labels, body-source labels, references,
  leads, and counts are escaped.
- The feature does not appear on the homepage or detail article pages.
- No app-facing contract, schema, JSON artifact, route family, fetching,
  extraction, ranking, LLM, scheduling, deployment, analytics, personalization,
  recommendation, or compliance-review product behavior changes.
- Documentation and workflow guards state the generated-site-only boundary for
  Stage 353.
