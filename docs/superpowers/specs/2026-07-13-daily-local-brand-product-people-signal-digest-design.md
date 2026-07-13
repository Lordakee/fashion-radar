# Daily Local Brand, Product & People Signal Digest Design

## Context

ROW ONE already saves selected article bodies locally and exposes several useful
reading aids. The homepage still lacks one compact surface that answers a
reader's basic daily question: which brands, items, and people recur across the
saved reporting, and where in the local article text is each mention grounded?

## Decision

Add a generated-site-only homepage section named Daily Local Brand, Product &
People Signal Digest. It will aggregate existing RowOneReference values from
current-edition saved local article content sections into three fixed buckets:
Brands, Products, and People. Each merged entity retains a small, capped list
of same-site evidence links to the relevant saved local article content-section
anchor.

This deliberately uses existing structured references rather than adding a new
extractor, classifier, model call, trend score, or external source. Counts mean
only the number of currently saved articles and sources that mention an entity;
they are coverage facts, not a heat score or ranking.

## Reader Experience

The section appears on index.html immediately after Daily Saved Text Takeaways
and before the Daily Local Saved Article Organizer. It has:

- a bilingual title, deck, and compact article/source/entity coverage metrics;
- fixed bilingual buckets for brands, products, and people;
- a stable first-seen list of merged names in each bucket;
- per-name saved-article and source counts;
- up to three short, escaped evidence cards with a source, saved-content label,
  excerpt, and link to articles/<safe-story-id>.html#local-article-content-section-N.

It is omitted on sparse editions until at least two current-edition saved local
articles contribute usable, safe reference evidence. Links remain internal, and
the existing local article page is the place for full text.

## Data Flow

render_row_one_site() already has the current edition, safely loaded local
article sidecars, and generated local article page hrefs. A focused builder will:

1. accept only safe current-edition story IDs with a matching local article and
   a valid generated local page href;
2. inspect content_sections[*].items[*].references in current story, section,
   item, and reference order;
3. map existing reference type terms into Brands, Products, or People;
4. normalize a nonblank reference name for per-bucket deduplication while
   retaining its first display spelling;
5. record one evidence support per story/entity/section, use item body then
   section body as the short local excerpt, cap supports at three, and retain
   article/source sets for factual coverage counts;
6. return None when fewer than two articles contribute or no allowed bucket has
   evidence.

The renderer passes the optional payload only to render_index_html(). The
template escapes text and independently revalidates every href before writing
only the existing homepage.

## Boundaries

This node does not alter the app payload, manifest, runtime payload, schemas,
article sidecars, source collection, fetching, scraping, matching, extraction,
scoring, ranking, LLM behavior, connectors, scheduling, deployment, analytics,
personalization, recommendation, demand proof, coverage verification, or
compliance-review behavior. It creates no JSON artifact, route family,
standalone page, article page content, or persistence mechanism.

## Safety and Failure Behavior

Blank entities, unsupported reference types, mismatched articles, malformed
story IDs, unsafe page hrefs, invalid fragments, and blank evidence excerpts are
discarded. The whole section disappears when there is insufficient valid data.
The template performs its own same-site href validation so an invalid manually
constructed payload cannot introduce an outbound or traversal link.

## Validation

Focused builder tests cover aggregation, first-seen ordering, counts, support
deduplication/caps, sparse-data omission, unsupported types, local-anchor
safety, and localized excerpt fallback. Renderer tests cover bilingual output,
escaping, href rejection, section ordering, and omission. A workflow sentinel
proves that the section is emitted only into index.html; contract and artifact
denylist assertions prove that it does not leak into JSON or create a new page.
