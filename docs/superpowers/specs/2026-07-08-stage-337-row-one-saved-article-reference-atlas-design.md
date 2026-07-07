# Stage 337 ROW ONE Saved Article Reference Atlas Design

## Goal

Make `articles/index.html` better at organizing the day's saved fashion information by adding a generated-site-only "Saved Article Reference Atlas". The atlas should aggregate existing structured references from already-saved local article content into compact brand, people, product, and source-context rows, so readers can quickly see which names and objects recur before opening detail-page sections.

## Current Gap

Stages 326-336 made the saved article library increasingly useful: source grouping, saved signal index, content organization, local excerpts, reading paths, and a theme digest. The page now explains what the saved article set is saying at a theme level, but it still does not provide a direct reference-level map for "which brands, designers, celebrities, bags, shoes, and other named signals appear across the saved local text today".

The existing `RowOneSavedArticleContentOrganizationCard.references` already carries deterministic, structured reference chips derived from saved local article sections. Stage 337 should aggregate those existing references into an index without adding source collection, extraction, scoring, LLM summarization, external enrichment, or JSON contract behavior.

## Chosen Approach

Add a small private generated-site builder for a saved article reference atlas:

- Build from existing `RowOneSavedArticleLibrary` and `RowOneSavedArticleContentOrganization` objects.
- Intersect content-organization cards against the existing saved article library to ensure atlas links point only to generated saved local detail pages.
- Aggregate existing `RowOneReference` values from content-organization cards into deterministic buckets: Brands, People, Products, and Source Context.
- Count supporting local leads and unique normalized source names per reference.
- Preserve canonical bucket order, then use first-seen order as the tie-breaker within each bucket so the atlas remains deterministic and does not imply external market ranking.
- Render the atlas only in `articles/index.html`, immediately after the Saved Article Theme Digest and before the Saved Signal Index.
- Link every support item only to validated internal `#local-article-content-section-N` anchors and optional paragraph evidence anchors.

This creates a direct reference-level organizing surface for daily fashion research while staying inside existing local saved article data.

## UI Behavior

When all sections exist, `articles/index.html` should render this order:

1. saved article library hero;
2. saved article theme digest;
3. saved article reference atlas;
4. saved signal index;
5. saved article reading paths;
6. saved article content organization;
7. source-grouped saved article library cards.

The reference atlas section should include:

- bilingual section title:
  - `Saved Article Reference Atlas`
  - `保存文章引用图谱`
- a compact bilingual dek that frames the atlas as names and product signals found in already-saved local article sections;
- up to four buckets:
  - Brands / 品牌
  - People / 人物
  - Products / 产品
  - Source Context / 来源语境
- up to six references per bucket;
- per-reference support count and source count;
- up to three support links per reference, each using local generated detail-page anchors;
- optional reference labels/types as chips;
- no outbound article URLs;
- no full article body republication.

The atlas should read like a professional fashion desk index: compact, evidence-linked, and clearly based on saved local text. It should not become a ranking product, trend score, social monitor, or market heat index.

## Reference Bucketing

Bucket references by normalized `RowOneReference.type` / `label` text. Evaluate the normalized type and label together in canonical bucket order: Brands first, then People, then Products, then Source Context. This means a reference with conflicting metadata lands in the first matching canonical bucket rather than duplicating across buckets.

- Brands: `brand`, `brands`, `label`, `house`, `designer_brand`, `fashion_house`, `maison`, `tracked` when the reference name is not empty. Here `label` means the literal normalized value `"label"`, not any non-empty `RowOneReference.label` field.
- People: `person`, `people`, `designer`, `celebrity`, `creative_director`, `creative`, `editor`, `founder`, `model`, `stylist`.
- Products: `product`, `products`, `bag`, `bags`, `shoe`, `shoes`, `sneaker`, `sneakers`, `accessory`, `accessories`, `apparel`, `dress`, `flat`, `flats`, `footwear`, `handbag`, `silhouette`, `skirt`, `watch`, `jewelry`.
- Source Context: every other non-empty reference with a non-empty type or label.

Dedupe references by bucket + normalized reference name. Preserve the first display casing and first non-empty type/label. Count unique sources case-insensitively. Render bucket groups in canonical order: Brands, People, Products, then Source Context; within each bucket, sort references by support count descending, then first-seen order.

## Data Flow

1. `render_row_one_site()` already builds `saved_article_library`, `saved_article_content_organization`, `saved_article_reading_paths`, and `saved_article_theme_digest`.
2. Stage 337 adds `build_row_one_saved_article_reference_atlas()` and calls it with the existing saved article library and content organization objects.
3. `_write_saved_article_library_page()` receives the atlas and passes it into `render_saved_article_library_html()`.
4. `render_saved_article_library_html()` renders the atlas immediately after the theme digest and before saved signal index.
5. The homepage and generated JSON contracts remain unchanged.

## Safety And Contract Boundaries

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
- outbound article URLs in the reference atlas
- new extraction or crawling behavior
- new summary generation behavior
- new social/community platform behavior
- `data/saved-article-reference-atlas.json`
- any generated JSON contract for this section

Primary atlas links must validate generated detail paths and `#local-article-content-section-N` anchors before prefixing `../`. Optional paragraph evidence links may be derived only from validated `paragraph_indices` and rendered as `#local-article-paragraph-N` anchors. Unsafe routes, traversal, wrong fragments, and `javascript:` routes must omit the unsafe support item or unsafe link from the atlas.

## Tests

Add tests that prove:

- the builder derives reference buckets from existing saved article library/content organization references and omits empty input;
- references dedupe by normalized bucket/name while preserving first display casing;
- support counts and source counts are deterministic;
- bucket and item caps are enforced;
- unsafe or non-library-matching detail paths do not contribute supports;
- `articles/index.html` renders `Saved Article Reference Atlas` / `保存文章引用图谱` after the theme digest and before saved signal index;
- rendered atlas rows show existing reference names, support/source counts, safe internal links, and evidence links when available;
- generated JSON artifacts do not expose reference-atlas vocabulary or local reference text;
- no `data/saved-article-reference-atlas.json` file is generated;
- `README.md` and `docs/row-one.md` document the Stage 337 generated-site-only boundary.

## Out Of Scope

- No social/community platform expansion.
- No crawler/source work.
- No new article extraction dependency.
- No LLM-generated summaries.
- No full-article publication on the library index.
- No app contract change.
- No generated images.
- No broad ROW ONE visual redesign.
- No compliance-review functionality.
- No ranking, trend score, heat score, or external popularity claim.
