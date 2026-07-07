# Stage 326 opencode Code Review

Reviewer: local opencode, `glm-5.2`

### Strengths

- Clean separation: pure builder (`saved_article_library.py`) produces frozen
  dataclasses; templates render. No I/O or schema coupling.
- Defensive validation matches existing modules: `safe_local_article_story_id`,
  `is_safe_row_one_detail_path`, and strict bool/non-int/out-of-range/
  blank-paragraph filtering close the paragraph-link escape hatches.
- Link safety is consistent: page hrefs are re-validated before `../` prefixes
  are emitted from `articles/index.html`.
- Scope discipline is verifiable: workflow and render tests assert no
  `saved_article_library`, `saved-article-library`, or daily library headings
  leak into edition/manifest/runtime JSON, and no
  `data/saved-article-library.json` is written.
- Cleanup integration is correct: `GENERATED_CHILDREN` adds `articles` and the
  existing marker guard still refuses unmarked directories.
- Optional behavior chain is intact: no saved articles means no `articles/`
  directory, no homepage entry, and no library page.
- Escaping audit is clean: titles, source names, section titles, paragraph
  labels, reference names, and reference labels/types are escaped in templates.
- Focused Stage 326 tests passed.

### Issues

#### Critical (Must Fix)

None.

#### Important (Should Fix)

None.

#### Minor (Nice to Have)

- `src/fashion_radar/row_one/saved_article_library.py`: source group
  `article_count` reports the total article count for a source, while rendered
  `.entries` are capped at eight per source. This is internally consistent, but
  scanners may not realize only the first eight cards are displayed. A future
  polish pass could render a `+N more` hint when `len(entries) < article_count`.

### Assessment

Stage 326 is a tight, well-scoped generated-site-only addition. The builder is
pure and defensive, templates escape user-facing text, link validation is
layered, scope boundaries are enforced by implementation and workflow tests,
and latest-only cleanup is extended without weakening the marker guard.

Ready to merge? Yes.
