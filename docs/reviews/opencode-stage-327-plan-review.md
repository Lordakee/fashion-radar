# Stage 327 opencode Plan Review

Reviewer: local opencode, `glm-5.2`

### Strengths

- Stage 327 is the right next step: Stage 326 organized saved articles by
  source, while Stage 327 cross-cuts them by existing reference name/type.
- Embedding the section inside `articles/index.html` is better scoped than
  adding another generated route for this stage because it avoids route,
  cleanup, and generated-child inventory expansion.
- The design explicitly stays current-edition and in-memory only, using
  `RowOneEdition` plus `local_articles_by_story_id`.
- The plan reuses the proven Stage 326 builder pattern and the existing template
  validation/escaping pattern.
- Caps, ordering, JSON contract boundaries, and paragraph index off-by-one
  behavior are called out.

### Issues

#### Critical (Must Fix)

1. `docs/superpowers/plans/2026-07-07-stage-327-row-one-saved-signal-index-plan.md`:
   homepage copy is inconsistent. The render test expects `signals or sources`,
   while the implementation step specifies `signal or source`. This will cause
   the TDD cycle to fail against the plan. Fix by choosing one string; prefer
   `Browse saved local articles by signals or sources.`.

#### Important (Should Fix)

1. `docs/superpowers/specs/2026-07-07-stage-327-row-one-saved-signal-index-design.md`
   and the plan: top-level `supporting_paragraph_count` semantics are ambiguous.
   Clarify that article/source counts are distinct across all entries, while
   supporting paragraph count is the sum of per-entry counts, so the same
   paragraph URL may count once per signal entry that references it.
2. Spec and plan: support-row grain is unspecified. Clarify whether one support
   equals a story, a story/content-section pair, or a story/content-section/item
   triple. Prefer one support per story per signal entry, with the first
   matching content section winning.
3. Plan: section href validator guidance references
   `safe_row_one_detail_fragment_href()` for `local-article-content-section-N`,
   but that helper requires an exact fragment. Use the existing
   `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE` pattern instead.
4. Plan/spec: homepage entry copy should be conditional on `saved_signal_index`
   existence. If the article library exists but there are no signal references,
   the homepage should not promise signal browsing.
5. Plan: the string-rejection test cannot be proven through Pydantic model
   construction because `paragraph_indices: list[int]` may coerce strings.
   Add a direct helper-level test for raw `object` paragraph indices.

#### Minor (Nice to Have)

- Pin metric label wording so tests do not fail on a copy coin flip.
- Explain why `saved_signal_index` is passed into `render_index_html()`.
- Add concrete negative docs-boundary assertions.
- Extend the omit render test to verify homepage copy fallback.

### Recommendation

Proceed with implementation? With fixes.

Fix the Critical and Important findings before implementation, then request a
focused plan rereview.
