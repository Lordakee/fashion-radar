## Stage 379 Plan Review — Saved Local Article Cross-Surface Organization Trail (opencode)

### Critical

**C1 — Task 4 render tests reference a fixture family that does not exist in `tests/test_row_one_render.py`**

Every test body proposed in Task 4 calls helpers that are defined in the *builder* test module (`tests/test_row_one_saved_article_local_reading_companion.py:33,52,81`) but are absent from the *render* test module the plan targets:

- `_story(story_id=...)` / `_story(story_id=..., source_name=...)` — no such function in `test_row_one_render.py` (only `_detail_story(story_id, headline, ...)` at `test_row_one_render.py:311` and the no-arg `_edition()` at `:240`).
- `_local_article(story.id)` / `_local_article(current.id, source_name=...)` — undefined; the render module uses `_signal_briefing_local_article()` (`:382`).
- `_edition(story)` and `_edition(current, peer)` — `_edition()` is declared with **no parameters** (`test_row_one_render.py:240`); passing args raises `TypeError`. The multi-story helper is `_edition_with_stories(*stories)` (`:338`), a different name.
- `_saved_article_library_entry(story_id)` (Task 4, Step 4) — no such fixture; `RowOneSavedArticleLibraryEntry` is only constructed inline at `:345` and `:11156`.

The established companion render test that the plan says to "add a test near" (`test_render_local_article_page_includes_saved_article_local_reading_companion`, `test_row_one_render.py:3387-3492`) uses `edition = _edition()`, `story = edition.stories[0]`, and `local_article=_signal_briefing_local_article()` — none of the fixtures the new tests assume. The Claude review's C1 caught only the `_companion_fixture` symbol in Step 3 and the rereview marked it resolved by inlining the companion, but the underlying root cause — a whole family of wrong-module fixtures across **all four** Task 4 steps — was missed. Result: Steps 1–4 will not produce a meaningful RED; they raise `NameError`/`TypeError` regardless of any implementation, breaking the TDD loop. The plan must either (a) rewrite the Task 4 tests against the render module's actual fixtures (`_edition()`, `edition.stories[0]`, `_signal_briefing_local_article()` / `_detail_story(...)`), or (b) explicitly add the missing `_story`/`_local_article`/`_edition_with_stories`/entry fixtures as a documented sub-step. As written the Step 4 hedge ("use the existing saved article library entry fixture") is also invalid because no such fixture exists.

### Important

**I1 — Card anchor and card href are derived from two independent, non-canonical paths**

The builder produces the library-card href from `story.id` (plan Task 3 Step 2: `_library_card_href(story.id)`; `story.id` is only screened by `safe_local_article_story_id` at `saved_article_local_reading_companion.py:94`). The library-card anchor, rendered from `entry` alone (`templates.py:9950`), must re-derive a story-id from the entry and cannot see `story.id`. These are two separate derivations that must agree byte-for-byte for the trail to resolve. Two concrete hazards:

1. The builder matches story↔entry on the **digest-path** detail path (`_library_entry_detail_path`, `saved_article_local_reading_companion.py:173-180`, digest_path only), but the plan tells the implementer to place the new `_saved_article_library_card_anchor_id(...)` "near `_saved_article_library_entry_detail_path`" (Task 5 Step 3), and that helper tries `reader_path` **first**, then digest, then evidence (`templates.py:10053-10067`). If `reader_path` and `digest_path` ever disagree on the embedded story-id, the anchor uses the reader-path id while the builder matched on the digest-path id — a silent, untestable anchor miss.
2. Nothing guarantees `story.id` equals the story-id parsed out of `story.detail_path`; they are independent fields on `RowOneStory`.

The plan already computes `current_detail_path` in the builder (`saved_article_local_reading_companion.py:97-99`). Recommend: derive the card href in the builder from `current_detail_path` (strip `details/` + `.html`, then `safe_local_article_story_id`) and derive the anchor from `entry.digest_path` by the **same** digest-only logic — never via the reader-path-first helper — so both sides share one canonical path. Add a unit test that proves the builder href and the anchor id agree for one fixture (Task 4 Step 4 only tests the anchor helper in isolation).

**I2 — Filing-trail renderer must not inherit the local-links `startswith("#")` acceptance guard**

The existing same-page link renderer drops every href that does not start with `#` (`templates.py:9217-9219`). Filing links are `index.html#...`, so they begin with `index.html`, not `#`. Task 5 Step 4 adds a separate `_render_saved_article_local_reading_companion_filing_trail(...)` but does not state its acceptance predicate. If the implementer mirrors the local-links block (call `_saved_article_local_reading_companion_href` then keep only `href.startswith("#")`), **every** filing link is silently filtered and the trail renders empty. The plan must specify that the trail renderer keeps any href that passes `_saved_article_local_reading_companion_href` and starts with `index.html#` (the new cross-surface pattern), distinct from local_links' `#`-only rule. Task 4 Step 1's RED will surface this, but the predicate should be explicit rather than inferred.

### Minor

**m1 — Dead CSS declaration carries forward from the prior review**

Task 5 Step 6 still sets `color: var(--ink)` on the combined `strong, a` rule and then overrides `a` with `color: var(--accent)` on the next rule. The `var(--ink)` value on `a` is unreachable. Set `var(--ink)` on `strong` only and `var(--accent)` on `a` only. (Carried from Claude m1, still unresolved.)

**m2 — Workflow sentinel deviates from the established templates-layer patch pattern**

Stage 373–377 generated-site-only tests patch a `fashion_radar.row_one.templates` (or `status_integrity`) function (`test_workflows.py:1595-1658`). Stage 379 patches `row_one_render.build_row_one_saved_article_local_reading_companion` instead. The target is valid (`render.py:73` imports it, `render.py:552` calls it directly), so this is not a defect, but it is a pattern break. If a later refactor moves the call behind a local alias the `raising=True` patch will start failing opaquely. Acceptable as-is; noted for consistency.

**m3 — Report-layer priority note**

Per `docs/REVIEW_PROTOCOL.md:56-62`, the v0.1.x track prioritizes source-coverage and matching-quality work, and report-layer refinements should stay "optional and contract-safe." Stage 379 is contract-safe (optional field with default, generated-site-only, no schema/route/JSON/manifest change) and is therefore within policy, but it is a navigation/wayfinding refinement rather than a coverage or matching gap. No change required; flagging so it is not mistaken for a coverage/matching deliverable.

**m4 — `aria-label="Saved article filing trail"` is English-only (intentional, but unstated)**

Consistent with other English-only `aria-label`s in the companion, so not a regression (Claude m2). The plan does not acknowledge this is deliberate; a one-line note would prevent a future "fix" that diverges from the existing companion convention.

---

No duplication with existing ROW ONE surfaces: the new `index.html#saved-article-organization-group-<key>` / `index.html#saved-article-library-card-<id>` links are the first article-page → library-anchor navigation; the existing organization jump index (`templates.py:737`) and `saved-article-library-entry-link` (`templates.py:8185`) are different surfaces/directions. Generated-site-only boundaries, href allow-listing, and AGENTS.md scope are otherwise respected. The blocking issue is C1 (un-runnable Task 4 tests); I1/I2 should be nailed down before implementation to avoid silent anchor misses.

END_OF_REVIEW
