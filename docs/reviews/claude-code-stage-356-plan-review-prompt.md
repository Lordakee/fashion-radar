# Stage 356 Plan Review Prompt

Review the Stage 356 design and plan:

- `docs/superpowers/specs/2026-07-08-stage-356-saved-article-key-signals-design.md`
- `docs/superpowers/plans/2026-07-08-stage-356-saved-article-key-signals-plan.md`

Goal: add a generated-site-only `Saved Article Key Signals` section to
`articles/<story-id>.html` pages. The section should organize existing
`RowOneStory` and `RowOneLocalArticle` content into compact Why It Matters,
Brands, Products, People, and Themes groups without adding app-facing payloads
or generated JSON artifacts.

Please evaluate:

1. Product fit with the user's request for content organization, not just links.
2. Whether the plan avoids app contracts, schemas, artifacts, fetching,
   extraction, scoring, ranking, LLM calls, connectors, scheduling, deployment,
   analytics, personalization, recommendation, and compliance-review behavior.
3. Whether the scope is non-duplicative with Stage 355's section binder.
4. Whether the explicit fallback mapping is technically sound:
   - Why It Matters: `local_article.brief_sections[key="why_it_matters"]`,
     falling back to `story.why_it_matters` only when the local article has at
     least one nonblank saved paragraph.
   - Brands, Products, People: existing
     `content_sections[*].items[*].references`, bucketed with
     `row_one_saved_article_reference_bucket(...)`, skipping blank names,
     deduping by normalized displayed reference name, and carrying readable
     support text from the first supporting content item body, item label, or
     section title when available.
   - Themes: existing content section titles and item labels only, with section
     keys used for stable support classification/anchors but not displayed as
     raw reader-facing labels.
5. Whether paragraph link handling, optional Why It Matters evidence, render
   ordering, docs stale-name guards, and tests are sufficient.
6. Any concrete corrections needed before implementation.
