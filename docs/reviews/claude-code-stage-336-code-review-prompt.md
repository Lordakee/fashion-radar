Review the Stage 336 implementation for Fashion Radar / ROW ONE.

Expected implementation:

- Adds generated-site-only Saved Article Theme Digest inside `articles/index.html`.
- Reuses already-saved local article sidecars, content organization, and safe
  local detail-page anchors.
- Keeps app/runtime/manifest/schema/JSON contracts unchanged.
- Does not add source collection, fetching, extraction, scoring, ranking, LLM,
  connector, scheduling, deployment, social/community, or compliance-review
  product behavior.

Files to inspect:

- `src/fashion_radar/row_one/saved_article_theme_digest.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_theme_digest.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-08-stage-336-row-one-saved-article-theme-digest-design.md`
- `docs/superpowers/plans/2026-07-08-stage-336-row-one-saved-article-theme-digest-plan.md`

Review checklist:

1. The implementation matches the Stage 336 spec and plan.
2. Unsafe/generated detail paths and fragments are filtered before rendering.
3. Theme digest content stays generated-site-only and does not leak into JSON.
4. Capping, dedupe, escaping, and truncation are deterministic.
5. Tests cover builder behavior, rendered HTML, CSS selectors, docs boundary, and
   contract non-exposure.
6. There are no Critical or Important maintainability/regression issues.

Classify findings as Critical, Important, Minor, or None. Include concrete file
and line references where possible. Focus on actual blockers.
