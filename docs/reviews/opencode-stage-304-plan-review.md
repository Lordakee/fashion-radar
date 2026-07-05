# opencode Stage 304 Plan Review

Verdict: APPROVE_WITH_NOTES

## Critical Issues

None.

## Important Issues

None.

## Assessment

The plan is technically reasonable and appropriately scoped. It keeps Stage 304 schema-neutral by reusing `RowOneLocalArticleContentItem.body`, preserves the existing `paragraph_indices` badge contract, and separates broad badge matching from name-only excerpt matching. This avoids misleading excerpt bodies from generic labels such as `bag`, `new`, or `tracked`, while still preserving paragraph badges that help users navigate supporting local paragraphs.

The plan stays within the requested report-layer improvement: it organizes already saved local article content inside ROW ONE detail content blocks. It does not add scraping, source acquisition, social connectors, platform APIs, browser automation, scheduling, monitoring, demand proof, platform coverage verification, app UI, image generation, dependency changes, or compliance-review product features.

The planned tests are strong enough to catch the key regression back to metadata-only bodies:

- generator assertions check matched entity, designer, and product bodies;
- a generic-label guard keeps `product / bag` fallback when only the label matches;
- JSON dump assertions confirm local sidecars carry the richer content;
- render assertions confirm detail pages publish the body through existing template paths;
- docs drift assertions update both README and ROW ONE documentation.

## Minor Notes

1. Task 2 HTML assertions are partially redundant because the same excerpt text can appear both as a content item body and as the first paragraph body. The JSON sidecar assertion is the stronger proof that the entity item body changed.

2. Task 3 should use the existing docs-test pattern: `row_one_docs = _normalized(_read(ROW_ONE_DOC))`. The plan's fallback wording around `Path("docs/row-one.md").read_text(...).lower()` is less consistent with current tests and could become whitespace-sensitive.
