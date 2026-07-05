# opencode Stage 303 Plan Review

## Verdict

APPROVE_WITH_NOTES.

One Important issue needs a plan clarification before implementation. No Critical issues.

## Critical Issues

None.

## Important Issues

### I1. Plain-fallback test updates are ambiguous

Task 2 Step 2 shows new assertions for `<p id="local-article-paragraph-N">...`, but it does not explicitly say to replace the existing exact assertions:

```python
assert "<p>One source paragraph.</p>" in detail_html
assert "<p>Second source paragraph.</p>" in detail_html
```

Those exact assertions will fail after adding `id="..."` to the `<p>` open tag. The plan should say the old assertions in both plain fallback tests are replaced, not augmented.

## Minor Notes

- Consider renaming `_render_local_article_paragraph_indices` to `_render_local_article_paragraph_links`, because it will emit anchor HTML rather than plain index text.
- Task 3 Step 4 should explicitly preserve the existing `len(article.paragraphs_zh) != len(article.paragraphs)` fallback guard and the per-paragraph zh-to-en fallback.
- Add opencode rereview artifacts to the commit list if they are created.

## Required Plan Changes

1. Clarify that the old exact `<p>...</p>` assertions in the plain fallback and zh-mismatch tests are replaced by the new id-bearing assertions.
2. Prefer the `_render_local_article_paragraph_links` helper name in the implementation plan.
3. Restate that the existing zh-length guard and zh fallback must be preserved.

## Boundary Review

The revised detail-page-only scope is sound. It avoids nested anchors on the homepage, avoids wrong-article aggregate links, keeps `data/edition.json`, `data/local-intelligence.json`, and `row-one-app/v7` unchanged, and does not add scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, image generation, or compliance-review product features.
