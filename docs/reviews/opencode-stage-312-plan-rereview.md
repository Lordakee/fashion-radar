## Stage 312 Plan Rereview (opencode fallback)

Acting as fallback reviewer per `AGENTS.md` after Claude Code returned 524.

### 1. Important Findings - Fix Confirmation

**Finding 1: Escaping test mutated `story.headline` directly - Fixed.**

The escaping test now constructs an immutable copy via
`edition.stories[0].model_copy(update={"headline": ...})` and reassigns
`edition.stories = [unsafe_story]` on a fresh local `_edition()` fixture. No
shared fixture object is mutated in place, and `model_copy` is the idiomatic
Pydantic v2 approach.

**Finding 2: Metrics-vs-capped-grid semantics - Fixed.**

- Design now states that metrics are edition-level corpus totals while the read
  queue is capped at four cards, so `article_count` may exceed rendered card
  count.
- Builder plan computes `article_count`, `saved_paragraph_count`, and
  `organized_section_count` over the full item list before the `items[:4]`
  slice, so totals reflect the corpus.
- Test plan asserts both `coverage.article_count == 6` and
  `len(coverage.items) == 4`.

**Finding 3: CSS selector test location - Fixed.**

Dedicated `test_row_one_css_includes_saved_article_coverage_styles` in
`tests/test_row_one_render.py` reads `assets/row-one.css` and asserts all six
selectors. Location is now explicit.

### 2. New Critical / Important Issues

None.

Minor non-blocking observations:

- `test_render_row_one_site_includes_saved_article_coverage` still uses direct
  assignment (`story.section_key = "top_stories"`). This is safe on a fresh
  local fixture and matches existing patterns, but a team may prefer
  `model_copy` for consistency.
- The builder always emits `#local-article-digest`; the design's
  `#local-article` fallback is effectively unreachable because the data
  selection filter already requires at least one nonblank paragraph, which is
  also the digest precondition. This is defensive and harmless.

### 3. Verdict

No Critical or Important findings remain. The revised design and plan are
approved to proceed to implementation.
