I'll review Stage 336 by inspecting the spec, plan, and existing source files in parallel.
Let me read the remaining key files to understand the patterns Stage 336 mirrors.
Let me verify the existing template helpers and docs sentinels referenced in the plan.
I have enough context to complete the review. Let me verify one more detail about the theme mapping semantics and the existing group titles.

The content organization groups (from `saved_article_content_organization.py:48-78`) are:
- `takeaways` → "Read First" / "优先阅读" (generic key takeaways)
- `entities` → "People & Brands" / "人物与品牌"
- `product_signals` → "Products" / "产品"
- `brand_signals` → "Source Structure" / "来源结构"

The plan maps these to themes:
- `takeaways` → `brand_momentum` ("Brand Momentum")
- `entities` → `people_designers` ("People / Designers")
- `product_signals` → `product_heat` ("Product Heat")
- `brand_signals` → `source_market_context` ("Source Structure / Market Context")

---

# Stage 336 Review

**Verdict: Needs revision** (one important semantic issue; otherwise safe to implement)

## Critical issues
None. The plan stays within scope: no app/runtime/manifest/schema/JSON contract changes, no crawling/extraction/ranking/LLM/connector/scheduling/deployment/social/compliance behavior, generated-site-only, mirrors the Stage 335 builder pattern closely.

## Important issues

1. **Theme titles mismatch source-group semantics.** The plan maps `takeaways` ("Read First" / generic key takeaways) → `brand_momentum` ("Brand Momentum"), and `entities` ("People & Brands") → `people_designers` ("People / Designers"). The "Read First" group is generic takeaways, not brand-specific; labeling it "Brand Momentum" with dek "Where saved local text concentrates today's brand signals" misleads readers. Likewise, "People & Brands" loses the "Brands" half when relabeled "People / Designers". The design's Chosen Approach says "Select capped cards ... by theme", implying card-level selection, but the plan implements a positional 1:1 group→theme mapping with no card-level theme filtering. Either (a) align theme titles to the source group titles (Read First, People & Brands, Products, Source Structure), or (b) actually filter cards by reference type before applying brand/people labels. Option (a) is the low-risk fix.

## Minor issues

1. **Design/plan divergence on reading-path inputs.** The design's Chosen Approach says "Select capped cards from already-safe content-organization cards and reading path steps", but the plan deliberately excludes `RowOneSavedArticleReadingPaths` from the builder. The plan's choice is reasonable and matches the design's Data Flow section, but the design's Chosen Approach sentence is stale and should be reconciled.

2. **Design lists themes in a different order than emitted.** Design lists "Brand Momentum, Product Heat, People / Designers, Source Structure"; plan emits in source-group order (brand_momentum, people_designers, product_heat, source_market_context). Not a blocker — plan is explicit — but the two docs disagree.

3. **`source_count` semantics are ambiguous.** Plan says "count unique normalized source names per theme and globally" but doesn't specify whether the global count is the union across themes or the sum. Union (deduplicated) is more meaningful; state it explicitly.

4. **Cross-theme repetition.** Dedupe key is `(theme_key, canonical_detail_path, lead.en, lead.zh)`, so the same story can appear in multiple themes (e.g., a story with both `takeaways` and `product_signals` sections surfaces in both `brand_momentum` and `product_heat`). For a "compact daily briefing" this may cause visible repetition. Consider noting this as accepted or adding a global per-story cap.

5. **Weak render assertion.** `assert "../details/" in html` will pass due to existing library cards/reading paths even if the digest renders no links. Prefer asserting the prefixed href appears inside the `saved-article-theme-digest` section.

6. **CSS coverage gap.** Plan adds 10 selectors but the test only asserts 3. The other 7 are untested. Consider asserting the header/metrics/card-meta/items/link/ref selectors too.

7. **Paragraph anchor offset not stated.** Plan says render `paragraph_indices` as `#local-article-paragraph-N` anchors. The codebase convention is 1-based (`local-article-paragraph-{index + 1}` at `templates.py:5094,5346,6653`). The plan should note the +1 offset or explicitly defer to the existing `_prefixed_saved_article_content_organization_href` helper, which already handles it.

## Specific plan changes required before implementation

1. Fix the theme-title/group-semantics mismatch (Important issue #1): either rename themes to match source groups, or add card-level reference filtering. The current mapping produces misleading labels.
2. Reconcile the design's "reading path steps" wording with the plan's exclusion of reading paths (Minor #1).
3. Clarify `source_count` global semantics as a union (Minor #3).

The referenced helpers (`_safe_saved_article_content_organization_href`, `_prefixed_saved_article_content_organization_href`, `validated_row_one_detail_relative_path`, `safe_row_one_detail_fragment_href`) all exist, and the Stage 335 docs sentinel the plan's docs test depends on is present in both `README.md:256` and `docs/row-one.md:471`.
