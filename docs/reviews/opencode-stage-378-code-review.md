## Stage 378 Saved Local Article Related Read Lanes Code Review (opencode)

**Critical**

None.

**Important**

None.

**Minor**

**M1. Per-lane cap is structurally unreachable through the renderer, and the `MAX_CARDS` / `MAX_CARDS_PER_LANE` invariant is undocumented.**
Both constants are 3. The Stage 377 builder hard-caps total cards at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS = 3`, so the per-lane cap can never fire in production. If the cap did fire through the renderer, the count-check fallback would reset `lanes_html` to empty and use the flat grid. A one-line comment near the constants would help future maintainers if `MAX_CARDS` is ever raised.

**M2. Redundant href validation and card HTML rendering in the lane path.**
The lane render path validates hrefs while pre-screening renderable cards and then re-validates through the shared card renderer. This is inconsequential at the current cap of three cards and matches the defensive shared-renderer plan, but adds some cognitive load when tracing the flow.

**M3. Lane header text duplicates card reason text for `same_section` and `same_source` in English.**
The lane title and the existing Stage 377 card reason both read "Same ROW ONE section" or "Same source desk" in English. This is cosmetic and not incorrect; changing Stage 377 card reasons is outside this stage.

**M4. Heading hierarchy uses lane `<h3>` and card `<h3>` at the same level.**
Inside the lane view the lane title and card titles both render as `<h3>`. Splitting card heading levels would require a separate lane card renderer, which would weaken the shared safe-renderer constraint. No action required unless the renderer is split later.

**Verification performed**

- Reviewed the git diff across all changed files.
- Verified `_related_read_lane_key` classification against each reason string produced by `_reason`.
- Confirmed `normalize_row_one_paragraph` only collapses whitespace, so the fullwidth colon in `共同信号：` is preserved.
- Confirmed safe href validation on lane paths via `_renderable_saved_article_local_related_read_cards`, `_render_saved_article_local_related_read_card`, and `_safe_saved_article_local_related_read_href`.
- Confirmed no-card-loss fallback behavior: when lane coverage does not match renderable safe-card count, the existing flat grid renders all renderable cards.
- Confirmed generated-site-only boundaries: no `lanes` field on `RowOneSavedArticleLocalRelatedReads`, no new JSON/HTML route family, schema field, app/runtime/manifest key, or contract payload entry.
- Confirmed no source acquisition, fetching, matching, extraction, scoring, ranking, recommendation, LLM, connector, scheduling, or compliance-review behavior was added.
- Focused tests, workflow contract/artifact test, ruff check, and ruff format check passed during review.

END_OF_REVIEW
