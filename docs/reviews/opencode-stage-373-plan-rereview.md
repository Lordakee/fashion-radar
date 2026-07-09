# Stage 373 Plan Re-Review Findings

opencode re-reviewed the Stage 373 plan after the Stage 366 filing-cue interaction fix.

## Critical

None remain.

## Important

None remain. The previous opencode I1 is resolved.

Verified against the codebase:

- `story` is in scope at `render_local_article_page_html`, and `include_body_filing_cues=True` is local-article-page-only, so marker building and threading are feasible and site-scoped.
- The Stage 366 body filing cue is rendered per paragraph index inside `_render_local_article_paragraphs`, so per-index suppression is mechanically sound.
- Both existing fragment regexes are available for render-time href validation.
- The suppression rule is encoded consistently across the design spec, the plan review-fixes section, render tests, and implementation steps.

## Minor

**M1: Empty-test sub-case needed rewording.**

The earlier plan said to test a section with no usable support, labels, or references. Because marker support falls back to the cited nonblank paragraph excerpt, that sub-case is not constructible when a valid insertion paragraph exists. The plan was updated to test empty output for mismatched ids, unsafe ids, all-blank paragraphs, and sections with no valid indices.

**M2: Filing-cue suppression is intentionally broad for marker paragraphs.**

Suppressing the inline Stage 366 filing cue on a marker paragraph also drops secondary filed-under links for other sections citing the same paragraph. This is acceptable because the marker paragraph now uses the block marker as its in-body signal and the pre-body content-section cards still preserve the broader section mapping.

**M3: Private strict-index helper non-int branch remains defensive.**

Model-level tests prove the user-visible filtering outcome. Direct helper-level coverage would be better if a future stage extracts the strict local article paragraph-index validator into a shared helper.
