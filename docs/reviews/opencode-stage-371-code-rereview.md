# Stage 371 Final Opencode Rereview

Reviewer: opencode with model `zhipuai-coding-plan/glm-5.2`.

Scope: final staged Stage 371 diff after the label-only fallback fix.

Verification performed by reviewer:

- Focused Stage 371 suite: `497 passed`
- Targeted ruff check: clean

## Critical

None.

## Important

None. The label-only fallback fix is correctly in place:

- `_item_excerpt` now chains only `item.body`, valid `paragraph_indices`, and `section.body`, returning `None` otherwise.
- Builder item rendering skips cards when `excerpt is None`, so recognized items without article-backed body text are omitted.
- RED-to-GREEN coverage exists in `test_build_daily_local_saved_article_organizer_omits_label_only_items`.

## Focus-Area Cross-Checks

1. Recognized item omission is enforced; no label-only or anchorless content-section card is produced.
2. Href safety is defense-in-depth: builder validates article page hrefs, and render validates the full `articles/<safe-story-id>.html#local-article-content-section-N` or `#local-article-paragraph-N` form with one-based anchors.
3. Generated-site-only boundary holds: organizer output is rendered only into `index.html`, and links are same-site saved local article anchors.
4. App contract and artifact leak guards cover snake-case, kebab-case, title-case, and Chinese organizer names and artifact stems.
5. Homepage full-article publishing is prevented by the 180-character excerpt cap and tests that reject full paragraph publication.
6. Tests cover grouping, unsafe inputs, paragraph-index fallback, label-only omission, caps, truncation, render escaping/link filtering, docs boundary, and contract non-leak.

## Minor

1. `_truncate` may split a word at the excerpt cap. This is cosmetic and consistent with prior helpers.
2. Per-section href dedupe collapses same-lane items within one section to one card. This matches the documented "dedupe by lane and href" contract.

## Verdict

Approved. No critical or important findings remain after the label-only fallback fix.
