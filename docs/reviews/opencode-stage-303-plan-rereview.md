# opencode Stage 303 Plan Rereview

## Verdict

APPROVE.

## Critical Issues

None.

## Important Issues

None.

## Prior Important Issue Resolution

The prior Important issue is resolved. Task 2 Step 2 now explicitly says to replace the old exact `<p>One source paragraph.</p>` and `<p>Second source paragraph.</p>` assertions in both plain fallback tests with the new id-bearing assertions.

## Minor Notes

- `_render_local_article_paragraph_links` is a clearer helper name for the new anchor-rendering behavior.
- The plan now explicitly preserves the zh-length guard and per-paragraph zh-to-en fallback.
- The link-before-id assertion is achievable because content sections render before the local article body.

## Boundary Review

The plan remains detail-page-only, defers homepage paragraph links, avoids nested anchors, keeps `data/edition.json`, `data/local-intelligence.json`, and `row-one-app/v7` unchanged, and adds no scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product features.
